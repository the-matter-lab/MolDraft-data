"""Validate the deposited MolDraft data, scores, versions, and file hashes."""
from pathlib import Path
from collections import Counter
import csv
import hashlib
import json

ROOT = Path(__file__).resolve().parent.parent
VERSION = "v18"
VERIFIER = "moldraft.stereochemistry/v18"
RESULT_SET = "moldraft.formal/v18"


def is_payload(path):
    relative = path.relative_to(ROOT)
    return (path.is_file() and path.name != "checksums.sha256"
            and not {".git", "__pycache__", ".pytest_cache", ".venv", "work"}.intersection(relative.parts)
            and path.name != ".env" and not path.name.startswith(".env."))


def load(path):
    return json.loads((ROOT / path).read_text())


def table(path):
    with (ROOT / path).open(newline="") as handle:
        return list(csv.DictReader(handle))


def passed(row):
    return bool(row["overall_pass"]) and not row["verifier_error"]


checksums = {}
for line in (ROOT / "checksums.sha256").read_text().splitlines():
    expected, name = line.split("  ", 1)
    assert name not in checksums, name
    path = ROOT / name
    assert path.resolve().is_relative_to(ROOT.resolve()), name
    assert path.is_file(), name
    assert hashlib.sha256(path.read_bytes()).hexdigest() == expected, name
    checksums[name] = expected
payload = {path.relative_to(ROOT).as_posix() for path in ROOT.rglob("*") if is_payload(path)}
assert set(checksums) == payload, "Checksum coverage does not match the deposited files"

release = load("release.json")
assert release["version"] == VERSION
assert release["release_tag"] == "verifier"
assert release["result_set"] == RESULT_SET
assert release["current_verifier_version"] == VERIFIER
assert release["main_verifier_versions"] == {VERIFIER: 2700}
assert load("benchmark/verification_policy.json")["verifier"]["schema"] == VERIFIER

index = table("data/index.csv")
names = {row["id"] for row in index}
assert len(names) == len(index) == release["molecules"] == 300
assert Counter(row["category"] for row in index) == {
    "VSEPR-curated": 59, "natural-product": 70, "literature": 171}
assert len(list((ROOT / "data/png").glob("*.png"))) == 300
assert len(list((ROOT / "data/xyz").glob("*.xyz"))) == 300
for row in index:
    assert (ROOT / "data" / row["image"]).is_file()
    lines = (ROOT / "data" / row["reference"]).read_text().splitlines()
    assert int(lines[0]) == int(row["total_atoms"])
    assert len(lines[2:2 + int(lines[0])]) == int(lines[0])

combined = load("results/final_results/verification_2700.json")
assert combined["result_set"] == RESULT_SET
assert combined["verifier"]["schema"] == VERIFIER
assert len(combined["rows"]) == 2700
by_pair = {(row["model"], row["name"]): row for row in combined["rows"]}
assert len(by_pair) == 2700
for model, counts in release["models"].items():
    folder = f"results/final_results/{model}"
    data = load(folder + "/verification.json")
    rows = data["rows"]
    assert data["result_set"] == RESULT_SET
    assert data["verifier"]["schema"] == VERIFIER
    assert len(rows) == 300 and {row["name"] for row in rows} == names
    assert {row["verifier_version"] for row in rows} == {VERIFIER}
    assert all("previous_pass" not in row and "previous_flag" not in row for row in rows)
    assert all(by_pair[(model, row["name"])] == row for row in rows), model
    records = {row["name"]: row for row in rows}
    total = sum(passed(row) for row in rows)
    assert total == counts["passes"] == data["n_pass"]
    summary = load(folder + "/summary.json")
    assert summary["result_set"] == RESULT_SET
    assert total == summary["overall"]["passed"]
    assert summary["overall"]["denominator"] == 300
    per_case = table(folder + "/per_case.csv")
    assert len(per_case) == 300 and {row["name"] for row in per_case} == names
    for row in per_case:
        current = records[row["name"]]
        assert bool(int(row["passed"])) == passed(current), (model, row["name"], "passed")
        assert row["flag"] == current["flag"], (model, row["name"], "flag")
    sessions = ROOT / folder / "sessions"
    assert len(list(sessions.glob("*/transcript.json"))) == counts["transcripts"] == 300
    assert len(list(sessions.glob("*/answer.xyz"))) == counts["answers"]

assert sum(passed(row) for row in combined["rows"]) == release["total_main_passes"] == 1419
assert combined["n_pass"] == 1419
summary_rows = table("results/final_results/summary.csv")
assert {row["model"] for row in summary_rows} == set(release["models"])
for row in summary_rows:
    assert int(row["pass"]) == release["models"][row["model"]]["passes"]
    assert int(row["accuracy_denominator"]) == 300

ablation = load("results/two_tool_ablation/eval/verification.json")
assert ablation["result_set"] == RESULT_SET
assert ablation["verifier"]["schema"] == VERIFIER
assert len(ablation["rows"]) == 300 and {row["name"] for row in ablation["rows"]} == names
assert {row["verifier_version"] for row in ablation["rows"]} == {VERIFIER}
assert sum(passed(row) for row in ablation["rows"]) == ablation["n_pass"] == 201
ablation_records = {row["name"]: row for row in ablation["rows"]}
assert release["models"]["gpt-6.1-sol"]["passes"] == 214
comparison = table("results/two_tool_ablation/eval/comparison.csv")
assert len(comparison) == 300 and {row["name"] for row in comparison} == names
for row in comparison:
    name = row["name"]
    assert (row["ablation_pass"].lower() in {"true", "1"}) == passed(ablation_records[name])
    assert (row["baseline_pass"].lower() in {"true", "1"}) == passed(by_pair[("gpt-6.1-sol", name)])

for path, expected_count, lookup in [
    ("results/final_results/answer_index.csv", 2700, by_pair),
    ("results/two_tool_ablation/answer_index.csv", 300,
     {("gpt-6.1-sol", name): row for name, row in ablation_records.items()}),
]:
    rows = table(path)
    assert len(rows) == expected_count
    assert len({(row["model"], row["molecule_id"]) for row in rows}) == expected_count
    for row in rows:
        record = lookup[(row["model"], row["molecule_id"])]
        assert bool(int(row["passed"])) == passed(record)
        assert row["verdict"] == ("pass" if passed(record) else "fail")
        for kind in ["reference", "answer"]:
            if row[kind + "_path"]:
                digest = hashlib.sha256((ROOT / row[kind + "_path"]).read_bytes()).hexdigest()
                assert digest == row[kind + "_sha256"] == record[kind + "_sha256"]
            else:
                assert not row[kind + "_sha256"]

flat = table("results/final_results/accuracy_all_models_and_ablations.csv")
assert len(flat) == 10 and {row["version"] for row in flat} == {VERSION}
for row in flat:
    expected = 201 if row["tool_profile"] == "png-bash" else release["models"][row["model"]]["passes"]
    assert int(row["passed"]) == expected and int(row["denominator"]) == 300
    assert abs(float(row["rate_pct"]) - 100 * expected / 300) < 1e-10

for name, digest in load("analysis/ablation_metrics.json")["inputs_sha256"].items():
    assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest

print("MolDraft integrity passed: file hashes; 300 drawing/reference pairs; 2,700 main and 300 ablation verdicts; "
      "all summaries and answer indices; consistent verifier and result-set identifiers.")
