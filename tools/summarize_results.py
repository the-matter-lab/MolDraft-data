"""Print reported resolve rates for the complete set and three source categories."""
from pathlib import Path
import csv
import json

ROOT = Path(__file__).resolve().parent.parent
index = list(csv.DictReader((ROOT / "data/index.csv").open()))
category = {r["id"]: r["category"] for r in index}
result = {}
for model in sorted((ROOT / "results/final_results").iterdir()):
    if not model.is_dir():
        continue
    rows = json.loads((model / "verification.json").read_text())["rows"]
    assert len(rows) == len(index) == 300
    groups = {"all": rows}
    for cat in sorted(set(category.values())):
        groups[cat] = [r for r in rows if category[r["name"]] == cat]
    result[model.name] = {}
    for name, group in groups.items():
        count = sum(bool(r["overall_pass"]) and not r["verifier_error"] for r in group)
        result[model.name][name] = {"passed": count, "molecules": len(group),
                                  "resolve_rate_percent": 100 * count / len(group)}
print(json.dumps(result, indent=2))
