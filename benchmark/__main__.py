"""Generate and score 3D structures with the standalone MolDraft agent."""
from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import csv
from dataclasses import asdict
import json
from pathlib import Path
import random
import shutil
import subprocess
import sys
import tempfile

from PIL import Image

from .agent import CONFIG, Conversation, Model, run_agent
from .agent_tools import PROFILES, Tools, case_path
from .sandbox import check_sandbox
from .score import digest, verify_case
from .structure_verifier import provenance


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
BUDGET = json.loads((ROOT / "benchmark/verification_policy.json").read_text())["case_budget_seconds"]


def positive(value):
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError("Expected a positive integer.")
    return number


def write_json(path, value):
    staging = path.with_suffix(path.suffix + ".tmp")
    staging.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    staging.replace(path)


def inputs(data):
    with (data / "index.csv").open(newline="", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))
    if not rows or len({row["id"] for row in rows}) != len(rows):
        raise ValueError("The dataset index is empty or has duplicate molecule IDs.")
    rows.sort(key=lambda row: row["id"])
    random.Random(42).shuffle(rows)
    cases = []
    for index, row in enumerate(rows, 1):
        image = case_path(data, row["image"], existing=True)
        reference = case_path(data, row["reference"], existing=True)
        cases.append({"case_id": f"mol_{index:04d}", "name": row["id"],
                      "image": str(image), "reference": str(reference),
                      "reference_sha256": digest(reference)})
    return cases


def anonymize(image, target):
    with Image.open(image, formats=["PNG"]) as source:
        # Retain pixels and transparency, and drop metadata that can identify
        # the molecule. The benchmark task sees only the anonymous filename.
        clean = source.convert("RGBA" if "transparency" in source.info or "A" in source.mode else "RGB")
        clean.info.clear()
        clean.save(target)


def run_one(out, model, profile, threads, prompt, case):
    case_id = case["case_id"]
    work = out / "work" / case_id
    session = out / "sessions" / case_id
    work.mkdir()
    session.mkdir()
    png = f"{case_id}.png"
    anonymize(case["image"], work / png)
    tools = Tools(work, profile, threads)
    report = run_agent(model, prompt.format(anonymous_png=png), tools, session / "transcript.jsonl")
    answer = work / "answer.xyz"
    valid = not answer.is_symlink() and answer.is_file() and answer.stat().st_size <= 1_000_000
    # A session whose budget is exhausted or interrupted has no submission.
    if report["status"] == "completed" and valid:
        shutil.copyfile(answer, session / "answer.xyz")
    report.update(case_id=case_id, submitted=(session / "answer.xyz").is_file())
    write_json(session / "session.json", report)
    return report


def run(args):
    model = Model.configured(args.model, args.api_model, args.provider, args.effort)
    cases = inputs(args.data.resolve())
    selected = cases[:args.limit]
    check_sandbox()
    prompt = (CONFIG / "user_prompt.txt").read_text().strip()
    with tempfile.TemporaryDirectory() as temporary:
        Conversation(model, "", Tools(Path(temporary), args.profile, args.xtb_threads))
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    (out / "work").mkdir()
    (out / "sessions").mkdir()
    write_json(out / "run.json", {
        "model": asdict(model), "profile": args.profile, "xtb_threads": args.xtb_threads,
        "dataset_size": len(cases), "cases": selected,
        "system_prompt_sha256": digest(CONFIG / "system_prompt.txt"),
        "user_prompt_sha256": digest(CONFIG / "user_prompt.txt"),
    })

    def attempt(case):
        return run_one(out, model, args.profile, args.xtb_threads, prompt, case)

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        for i, row in enumerate(pool.map(attempt, selected), 1):
            print(f"[{i}/{len(selected)}] {row['case_id']} {row['status']} "
                  f"submitted={row['submitted']}", flush=True)


def verify(args):
    out = args.run.resolve()
    manifest = json.loads((out / "run.json").read_text())
    cases = manifest["cases"]
    evidence = provenance()
    scoring = out / "eval"
    scoring.mkdir(exist_ok=True)

    def one(case):
        case_id = case["case_id"]
        reference = Path(case["reference"])
        if digest(reference) != case["reference_sha256"]:
            raise ValueError(f"Reference changed since generation: {case['name']}")
        answer = out / "sessions" / case_id / "answer.xyz"
        row = verify_case(reference, answer, scoring, threads=args.xtb_threads, timeout=args.timeout)
        row.update(case_id=case_id, name=case["name"], reference_sha256=case["reference_sha256"],
                   answer_sha256=digest(answer) if answer.is_file() else None,
                   verdict="pass" if row["overall_pass"] else "fail")
        return row

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        rows = list(pool.map(one, cases))
    passes = sum(row["overall_pass"] for row in rows)
    full = len(rows) == manifest["dataset_size"] == 300
    write_json(scoring / "verification.json", {
        "model": manifest["model"]["id"], "profile": manifest["profile"],
        "verifier": evidence, "case_budget_seconds": args.timeout, "full_300": full,
        "n_cases": len(rows), "n_pass": passes, "n_fail": len(rows) - passes,
        "success_rate": passes / len(rows) if full else None,
        "flags": Counter(row["flag"] for row in rows), "rows": rows,
    })
    with (scoring / "per_case.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["case_id", "name", "verdict", "flag",
                                                  "aam_pass", "stereo_pass", "geometry_pass"])
        writer.writeheader()
        writer.writerows({key: row.get(key) for key in writer.fieldnames} for row in rows)
    label = "Full benchmark" if full else "Subset check"
    print(f"{label}: {passes}/{len(rows)} passed. Results: {scoring}")


def verify_xyz(args):
    provenance()
    args.work_dir.mkdir(parents=True, exist_ok=True)
    result = verify_case(args.reference, args.prediction, args.work_dir,
                         threads=args.xtb_threads, timeout=args.timeout)
    write_json(args.work_dir / "verification.json", result)
    print(json.dumps(result, indent=2))


def check(_args):
    check_sandbox(scientific_tools=True)
    version = subprocess.run(["xtb", "--version"], check=True, capture_output=True, text=True)
    if "6.7.1" not in version.stdout + version.stderr:
        raise RuntimeError("Use xTB 6.7.1 from environment.yml to reproduce the published scoring.")
    details = provenance()
    print(f"Sandbox, scientific tools, xTB 6.7.1 and MAPPA {details['mappa_version']} "
          f"({details['mappa_commit'][:7]}) are available.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(required=True)
    preflight = sub.add_parser("check", help="check the Linux sandbox and verifier installation")
    preflight.set_defaults(action=check)

    new = sub.add_parser("run", help="generate model answers")
    new.set_defaults(action=run)
    new.add_argument("--data", type=Path, default=DATA)
    new.add_argument("--out", type=Path, required=True, help="new run directory")
    new.add_argument("--model", required=True, help="model name, matching configuration/models.json for paper settings")
    new.add_argument("--api-model", help="provider model alias if it differs from --model")
    new.add_argument("--provider", choices=("auto", "openai", "anthropic", "chat"), default="auto")
    new.add_argument("--effort", choices=("none", "low", "medium", "high", "xhigh", "max"))
    new.add_argument("--profile", choices=tuple(PROFILES), default="four-tools")
    new.add_argument("--workers", type=positive, default=1)
    new.add_argument("--xtb-threads", type=positive, default=4)
    new.add_argument("--limit", type=positive, help="generate a small subset to check the installation")

    score = sub.add_parser("verify", help="score a run with the published v18 verifier")
    score.set_defaults(action=verify)
    score.add_argument("--run", type=Path, required=True)
    score.add_argument("--workers", type=positive, default=1)
    score.add_argument("--xtb-threads", type=positive, default=1)
    score.add_argument("--timeout", type=positive, default=BUDGET)

    pair = sub.add_parser("verify-xyz", help="score a single reference/prediction pair")
    pair.set_defaults(action=verify_xyz)
    pair.add_argument("--reference", type=Path, required=True)
    pair.add_argument("--prediction", type=Path, required=True)
    pair.add_argument("--work-dir", type=Path, required=True)
    pair.add_argument("--xtb-threads", type=positive, default=1)
    pair.add_argument("--timeout", type=positive, default=BUDGET)

    args = parser.parse_args()
    try:
        args.action(args)
    except (OSError, ValueError, RuntimeError) as exc:
        parser.exit(1, f"MolDraft: {exc}\n")


if __name__ == "__main__":
    main()
