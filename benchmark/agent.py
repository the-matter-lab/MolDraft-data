"""Minimal provider loop for the four-tool benchmark."""
from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import os
from pathlib import Path

import requests

from .agent_tools import ToolResult, Tools


CONFIG = Path(__file__).resolve().parents[1] / "configuration"
SEQUENTIAL_TOOLS = (
    "\n\n[IMPORTANT CONSTRAINT] You must NOT call multiple tools in parallel. "
    "Execute tools ONE AT A TIME, sequentially. Wait for each tool's result before "
    "calling the next tool. Never batch multiple tool calls in a single response."
)


@dataclass(frozen=True)
class Model:
    id: str
    api_model: str
    provider: str
    effort: str | None
    max_calls: int
    max_tokens: int | None

    @classmethod
    def configured(cls, name, api_model, provider, effort):
        config = json.loads((CONFIG / "models.json").read_text())
        settings = {entry["id"]: entry for entry in config["models"]}
        lower = name.lower()
        if provider == "auto":
            provider = "anthropic" if lower.startswith("claude") else (
                "openai" if lower.startswith("gpt") else "chat")
        if effort is None:
            effort = settings.get(name, {}).get("reasoning_effort", "high")
        return cls(name, api_model or name, provider, None if effort == "none" else effort,
                   config["max_model_calls"], config["max_total_tokens"].get(name))


@dataclass
class Call:
    id: str
    name: str
    arguments: dict


def call_arguments(raw):
    try:
        return json.loads(raw) if isinstance(raw, str) else raw
    except json.JSONDecodeError:
        return None


class Conversation:
    def __init__(self, model: Model, question: str, tools: Tools):
        self.model = model
        self.definitions = list(tools.definitions())
        self.system = (CONFIG / "system_prompt.txt").read_text().rstrip("\n")
        self.family = model.id.lower()
        self.sequential_prompt = self.family.startswith(("kimi", "moonshot", "qwen"))
        if self.sequential_prompt:
            self.system += SEQUENTIAL_TOOLS
        self.history = [{"role": "user", "content": question}]
        if model.provider == "chat":
            self.history.insert(0, {"role": "system", "content": self.system})
        self.base_url, self.key = self.credentials(model.provider)

    def credentials(self, provider):
        if provider == "anthropic":
            key = os.getenv("ANTHROPIC_API_KEY")
            endpoint = os.getenv("ANTHROPIC_BASE_URL", "https://api.anthropic.com")
        elif self.family.startswith(("kimi", "moonshot")) and provider == "chat":
            key = os.getenv("MOONSHOT_API_KEY")
            endpoint = os.getenv("MOONSHOT_BASE_URL", "https://api.moonshot.ai/v1")
        elif self.family.startswith("qwen") and provider == "chat":
            key = os.getenv("QWEN_API_KEY")
            endpoint = os.getenv("QWEN_BASE_URL") or os.getenv("OPENAI_BASE_URL")
        else:
            key = os.getenv("OPENAI_API_KEY")
            endpoint = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        key = os.getenv("MOLDRAFT_API_KEY") or key
        endpoint = os.getenv("MOLDRAFT_BASE_URL") or endpoint
        if not key or not endpoint:
            raise ValueError("Set the model API key and base URL (see README).")
        endpoint = endpoint.rstrip("/")
        if provider == "anthropic" and not endpoint.endswith("/v1"):
            endpoint += "/v1"
        return endpoint, key

    def turn(self, client):
        model = self.model
        body = {"model": model.api_model}
        if model.provider == "openai":
            path = "responses"
            headers = {"Authorization": f"Bearer {self.key}"}
            body.update(instructions=self.system, input=self.history, store=False,
                        include=["reasoning.encrypted_content"], parallel_tool_calls=False,
                        tools=[{"type": "function", **tool, "strict": False}
                               for tool in self.definitions])
            if model.effort:
                body["reasoning"] = {"effort": model.effort}
        elif model.provider == "anthropic":
            path = "messages"
            headers = {"x-api-key": self.key, "anthropic-version": "2023-06-01"}
            body.update(system=self.system, messages=self.history, max_tokens=64000,
                        tool_choice={"type": "auto", "disable_parallel_tool_use": True},
                        tools=[{"name": t["name"], "description": t["description"],
                                "input_schema": t["parameters"]} for t in self.definitions])
            if model.effort:
                body.update(thinking={"type": "adaptive"}, output_config={"effort": model.effort})
        else:
            path = "chat/completions"
            headers = {"Authorization": f"Bearer {self.key}"}
            body.update(messages=self.history,
                        tools=[{"type": "function", "function": t} for t in self.definitions])
            if not self.family.startswith("qwen"):
                body.update(parallel_tool_calls=False, tool_choice="auto")
            else:
                body["temperature"] = 0.6
            if model.effort:
                body["reasoning_effort"] = model.effort
        response = client.post(f"{self.base_url}/{path}", json=body, headers=headers, timeout=900,
                               allow_redirects=False)
        if not 200 <= response.status_code < 300:
            message = response.text.replace(self.key, "[redacted]")[:1500]
            raise RuntimeError(f"Provider HTTP {response.status_code}: {message}")
        return self.receive(response.json())

    def receive(self, data):
        text = []
        calls = []
        usage = data.get("usage") or {}
        provider = self.model.provider
        if provider == "openai":
            if data.get("status") in ("failed", "incomplete", "cancelled"):
                raise RuntimeError(f"Provider ended the turn: {data.get('status')}")
            blocks = data["output"]
            self.history.extend(blocks)
            for item in blocks:
                if item["type"] == "function_call":
                    calls.append(Call(item["call_id"], item["name"], call_arguments(item["arguments"])))
                elif item["type"] == "message":
                    text += [b.get("text", b.get("refusal", "")) for b in item.get("content", [])]
        elif provider == "anthropic":
            if data.get("stop_reason") in ("max_tokens", "model_context_window_exceeded"):
                raise RuntimeError(f"Provider ended the turn: {data['stop_reason']}")
            blocks = data["content"]
            self.history.append({"role": "assistant", "content": blocks})
            for item in blocks:
                if item["type"] == "tool_use":
                    calls.append(Call(item["id"], item["name"], item["input"]))
                elif item["type"] == "text":
                    text.append(item["text"])
        else:
            choice = data["choices"][0]
            if choice.get("finish_reason") in ("length", "content_filter"):
                raise RuntimeError(f"Provider ended the turn: {choice['finish_reason']}")
            message = choice["message"]
            self.history.append(message)
            text.append(message.get("content") or "")
            for item in message.get("tool_calls") or []:
                fn = item["function"]
                calls.append(Call(item["id"], fn["name"], call_arguments(fn["arguments"])))
        if not calls and not any(text):
            raise RuntimeError("Provider returned an empty reply.")
        return "\n".join(text), calls, usage

    def add_results(self, results: list[tuple[Call, ToolResult]]):
        provider = self.model.provider
        if provider == "anthropic":
            blocks = []
            for call, result in results:
                content = [{"type": "text", "text": result.text or "(no output)"}]
                if result.png:
                    content.append({"type": "image", "source": {
                        "type": "base64", "media_type": "image/png", "data": result.base64}})
                blocks.append({"type": "tool_result", "tool_use_id": call.id, "content": content})
            self.history.append({"role": "user", "content": blocks})
        elif provider == "openai":
            for call, result in results:
                output = result.text
                if result.png:
                    output = [{"type": "input_image", "detail": "auto",
                               "image_url": f"data:image/png;base64,{result.base64}"}]
                self.history.append({"type": "function_call_output", "call_id": call.id, "output": output})
        else:
            images = []
            for call, result in results:
                self.history.append({"role": "tool", "tool_call_id": call.id,
                                     "content": result.text})
                if result.png:
                    images.extend([{"type": "text", "text": f"Image from {call.name}:"},
                                   {"type": "image_url", "image_url": {
                                       "url": f"data:image/png;base64,{result.base64}"}}])
            if images:
                self.history.append({"role": "user", "content": images})


def total_tokens(usage):
    if "total_tokens" in usage:
        return usage["total_tokens"]
    return sum(usage.get(key, 0) or 0 for key in (
        "input_tokens", "output_tokens", "cache_creation_input_tokens", "cache_read_input_tokens",
    ))


def run_agent(model, question, tools, transcript: Path):
    conversation = Conversation(model, question, tools)
    turns = tokens = tool_calls = 0
    reason = "max_model_calls"
    with requests.Session() as client, transcript.open("w", encoding="utf-8") as log:
        def record(message):
            log.write(json.dumps(message, ensure_ascii=False) + "\n")
            log.flush()

        record({"role": "system", "content": conversation.system})
        record({"role": "user", "content": question})
        for turns in range(1, model.max_calls + 1):
            try:
                text, calls, usage = conversation.turn(client)
            except (requests.RequestException, ValueError, RuntimeError, KeyError, IndexError, TypeError) as exc:
                reason = "provider_error"
                record({"role": "error", "content": str(exc)})
                break
            tokens += total_tokens(usage)
            record({"role": "assistant", "content": text, "usage": usage,
                    "tool_calls": [asdict(call) for call in calls]})
            if model.max_tokens is not None and tokens > model.max_tokens:
                reason = "max_total_tokens"
                break
            if not calls:
                reason = "completed"
                break
            results = [(call, tools.call(call.name, call.arguments)) for call in calls]
            for call, result in results:
                record({"role": "tool", "name": call.name, "tool_call_id": call.id,
                        "content": result.text, "image": "[image]" if result.png else None})
            tool_calls += len(results)
            conversation.add_results(results)
    return {"status": reason, "model_calls": turns, "tool_calls": tool_calls, "total_tokens": tokens}
