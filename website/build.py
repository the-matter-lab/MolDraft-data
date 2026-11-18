#!/usr/bin/env python3
"""Build the MolDraft v18 website from the public data release.

All displayed rates, costs, tokens, source categories, and atom-count bins are
computed from v18 records and checked against the manuscript analysis outputs.
Scores are exported as aggregates. A verified example is shown in the homepage demo.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import decimal
import hashlib
import html
import json
import math
import re
import statistics
import sys
from html.parser import HTMLParser
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import charts  # noqa: E402  (sibling module, stdlib only)

HERE = Path(__file__).resolve().parent
DATA_REPO = HERE.parent if (HERE.parent / "release.json").exists() else None
SITE = HERE.parent / "docs" if DATA_REPO else HERE / "site"
TEMPLATES = HERE / "templates"
META = HERE / "models_meta.json"

Z95 = 1.959963984540054
SOURCE_ORDER = ["vsepr", "np", "literature"]

# Text that must never appear in the shipped site: molecule names and question ids.
LEAK_PATTERNS = [
    re.compile(r"\bnp_[a-z0-9]"), re.compile(r"\bshot_[a-z0-9]"), re.compile(r"\bvsepr_tier"),
    re.compile(r"\bpaper_(?:pr|paper)\d"), re.compile(r"\bmol_\d{4}\b"),
]


def wilson(k: int, n: int, z: float = Z95) -> tuple[float, float]:
    """95% Wilson score interval for k successes in n trials, in percent."""
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (100 * (centre - half), 100 * (centre + half))


def display_date(iso: str) -> str:
    d = dt.date.fromisoformat(iso)
    return f"{d.strftime('%b')} {d.day}, {d.year}"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def as_bool(s: str) -> bool:
    return s.strip().lower() == "true"


def load_inputs():
    if DATA_REPO is None:
        raise SystemExit("Pass --data-repo pointing to the public MolDraft v18 data checkout.")
    release = json.loads((DATA_REPO / "release.json").read_text())
    if release.get("version") != "v18" or release.get("current_verifier_version") != "moldraft.stereochemistry/v18":
        raise SystemExit("The website requires the v18 data release and verifier.")
    with (DATA_REPO / "data/index.csv").open(newline="") as handle:
        index = list(csv.DictReader(handle))
    assert len(index) == 300 and len({row["id"] for row in index}) == 300
    settings = json.loads((DATA_REPO / "configuration/models.json").read_text())
    metrics = json.loads((DATA_REPO / "analysis/results_metrics.json").read_text())
    meta = json.loads(META.read_text())
    return release, index, settings, metrics, meta


def is_pass(row):
    return bool(row["overall_pass"]) and not row["verifier_error"]


def build_doc() -> dict:
    release, index, settings, metrics, meta = load_inputs()
    categories = {row["id"]: row["category"] for row in index}
    source_categories = {"vsepr": "VSEPR-curated", "np": "natural-product", "literature": "literature"}
    efforts = {row["id"]: row["reasoning_effort"] for row in settings["models"]}
    source_paths = ["release.json", "data/index.csv", "configuration/models.json", "configuration/user_prompt.txt", "analysis/results_metrics.json"]
    meta["benchmark"]["prompt"] = (DATA_REPO / "configuration/user_prompt.txt").read_text().strip()
    cases = {}
    entries = []
    for model, counts in release["models"].items():
        mm = meta["models"][model]
        folder = DATA_REPO / "results/final_results" / model
        verification = json.loads((folder / "verification.json").read_text())
        summary = json.loads((folder / "summary.json").read_text())
        with (folder / "per_case.csv").open(newline="") as handle:
            usage = list(csv.DictReader(handle))
        rows = verification["rows"]
        assert len(rows) == len(usage) == 300
        assert {row["name"] for row in rows} == set(categories)
        assert {row["verifier_version"] for row in rows} == {"moldraft.stereochemistry/v18"}
        assert verification["verifier"]["schema"] == "moldraft.stereochemistry/v18"
        passed = sum(is_pass(row) for row in rows)
        assert passed == counts["passes"] == verification["n_pass"] == summary["overall"]["passed"]
        assert passed == metrics["resources"][model]["passed"]
        cases[model] = rows
        source_paths.extend(str((folder / name).relative_to(DATA_REPO))
                            for name in ["verification.json", "summary.json", "per_case.csv"])
        errors = sum(bool(row["verifier_error"]) for row in rows)
        flags = Counter(row["flag"] for row in rows)
        lo, hi = wilson(passed, 300)
        token_rows = [int(row["input_tokens"]) + int(row["output_tokens"]) for row in usage]
        cost_rows = [float(row["cost_usd"]) for row in usage]
        tokens = summary["tokens"]
        inp, out, cached = (int(tokens[key]) for key in ["input_tokens", "output_tokens", "cached_tokens"])
        cost = float(summary["cost_usd"])
        assert math.isclose(cost / 300, metrics["resources"][model]["cost"], abs_tol=1e-10)
        assert math.isclose((inp + out) / 300, metrics["resources"][model]["tokens"], abs_tol=1e-8)
        by_source = {}
        for key in SOURCE_ORDER:
            group = [row for row in rows if categories[row["name"]] == source_categories[key]]
            bp = sum(is_pass(row) for row in group)
            blo, bhi = wilson(bp, len(group))
            metric_key = {"vsepr": "VSEPR", "np": "natural_product", "literature": "literature"}[key]
            assert bp == metrics["sources"][metric_key]["passes"][model]
            by_source[key] = dict(label=meta["sources"][key]["label"], n=len(group), passed=bp,
                                  success_rate=round(100 * bp / len(group), 2),
                                  ci95=dict(low=round(blo, 2), high=round(bhi, 2)))
        org = mm["organization"]
        entries.append(dict(
            model_id=model, display_name=mm["display_name"], organization=org,
            org_url=meta["organizations"].get(org, {}).get("url"),
            org_logo=meta["organizations"].get(org, {}).get("logo"),
            effort=efforts[model], date=None, display_date=None,
            release_date=mm.get("release_date"),
            display_release_date=display_date(mm["release_date"]) if mm.get("release_date") else None,
            n=300, passed=passed, verifier_error=errors, judgeable=300-errors,
            verifier_version="moldraft.stereochemistry/v18",
            success_rate=round(100 * passed / 300, 2), display_success_rate=f"{100 * passed / 300:.1f}%",
            ci95=dict(method="wilson", level=0.95, low=round(lo, 2), high=round(hi, 2),
                      half_width=round((hi-lo)/2, 2),
                      display_half_width=str(decimal.Decimal((hi-lo)/2).quantize(
                          decimal.Decimal("0.1"), rounding=decimal.ROUND_HALF_UP))),
            failures=dict(wrong_mol=flags["wrong_mol"], wrong_stereo=flags["wrong_stereo"],
                          wrong_geometry=flags["wrong_geometry"], no_answer=flags["no_answer"],
                          verifier_error=errors,
                          other=max(0, 300-passed-errors-flags["wrong_mol"]-flags["wrong_stereo"]
                                    -flags["wrong_geometry"]-flags["no_answer"])),
            aam_pass=sum(bool(row.get("aam_pass")) for row in rows),
            tokens=dict(input=inp, output=out, cached_input=cached, total=inp+out,
                        cache_hit_pct=100*cached/inp if inp else None,
                        per_task_mean=round((inp+out)/300),
                        per_task_median=round(statistics.median(token_rows))),
            cost_usd=dict(total=cost, per_task_mean=cost/300,
                          per_task_median=round(statistics.median(cost_rows), 4),
                          basis=summary["cost_basis"],
                          per_case_rows_match_total=abs(round(sum(cost_rows),2)-cost)<0.011),
            sessions_without_usage=sum(int(row["input_tokens"]) == 0 for row in usage),
            by_source=by_source, notes=[],
        ))
    entries.sort(key=lambda row: (-row["passed"], row["display_name"]))
    previous, rank = None, 0
    for i, entry in enumerate(entries, 1):
        if entry["passed"] != previous:
            rank, previous = i, entry["passed"]
        entry["rank"] = rank
    assert sum(entry["passed"] for entry in entries) == 1419
    sources = {key: dict(label=meta["sources"][key]["label"], short=meta["sources"][key]["short"],
                        n=sum(row["category"] == source_categories[key] for row in index))
               for key in SOURCE_ORDER}
    return dict(schema_version=1, release_version="v18", result_set="moldraft.formal/v18",
                generated_at=dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
                site=meta["site"], benchmark=dict(meta["benchmark"], runs=len(entries)),
                sources=sources,
                source_files={name: sha256(DATA_REPO/name) for name in source_paths},
                entries=entries, atom_bins=atom_size_bins(cases, index, metrics),
                organizations=meta["organizations"])


def atom_size_bins(cases, index, metrics):
    """Aggregate total-atom bins and verify every count against manuscript analysis."""
    atoms = {row["id"]: int(row["total_atoms"]) for row in index}
    bins = []
    for label, expected in metrics["total_atoms"].items():
        low, high = map(int, label.split("--"))
        members = {name for name, count in atoms.items() if low <= count <= high}
        assert len(members) == expected["n"]
        per_model, passed_all, total_all = {}, 0, 0
        for model, rows in cases.items():
            group = [row for row in rows if row["name"] in members]
            passed = sum(is_pass(row) for row in group)
            assert passed == expected["passes"][model]
            per_model[model] = dict(passed=passed, n=len(group), rate=round(100*passed/len(group),1))
            passed_all += passed
            total_all += len(group)
        bins.append(dict(label=f"{low}\u2013{high}", lo=low, hi=high, n=len(members),
                         pooled=dict(passed=passed_all,total=total_all,rate=round(100*passed_all/total_all,1)),
                         models=per_model))
    assert sum(row["n"] for row in bins) == 300
    return dict(unit="total atoms, including hydrogen", n_bins=len(bins), bins=bins,
                note="Total-atom quintile bins used in the paper; pooled rates include all nine models.")


def logo_sprite() -> str:
    """Inline <symbol> sprite from site/assets/logos/*.svg (monochrome, fill=currentColor)."""
    parts = []
    for f in sorted((SITE / "assets" / "logos").glob("*.svg")):
        svg = f.read_text()
        vb = re.search(r'viewBox="([^"]+)"', svg)
        body = re.sub(r"<title>.*?</title>", "", re.search(r"<svg[^>]*>(.*)</svg>", svg, re.S).group(1), flags=re.S).strip()
        parts.append(f'<symbol id="logo-{f.stem}" viewBox="{vb.group(1) if vb else "0 0 24 24"}" '
                     f'fill="currentColor" fill-rule="evenodd">{body}</symbol>')
    if not parts:
        return ""
    return ('<svg class="svg-sprite" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" focusable="false">'
            + "".join(parts) + "</svg>")


def render_page(doc: dict, template: Path | None = None, out: Path | None = None) -> Path | None:
    tpl = template or TEMPLATES / "index.html"
    if not tpl.exists():
        print(f"  (no {tpl.relative_to(HERE.parent.parent)}; page not rendered)")
        return None
    text = tpl.read_text()
    if "__LEADERBOARD_JSON__" not in text:
        sys.exit("templates/index.html has no __LEADERBOARD_JSON__ placeholder")
    charts_markup = doc.pop("_charts_markup", None)
    if charts_markup is None:
        charts_markup, doc["charts"] = charts.charts_html(doc)
    payload = json.dumps(doc, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    site = doc["site"]
    subs = {
        "__LEADERBOARD_JSON__": payload,
        "__LOGO_SPRITE__": logo_sprite(),
        "__CHARTS_HTML__": charts_markup,
        "__GENERATED_AT__": doc["generated_at"],
        "__GENERATED_DATE__": display_date(doc["generated_at"][:10]),
        "__SITE_TITLE__": site["title"],
        "__STYLE_HASH__": sha256(SITE / "assets/style.css")[:12],
        "__CHARTS_HASH__": sha256(SITE / "assets/charts.js")[:12],
        "__HERO_TITLE__": site["hero_title"],
        "__TAGLINE__": site["tagline"],
        "__GITHUB_URL__": site["github_url"],
        "__CARD_FOOTER__": site["card_footer"],
        "__CANARY__": site["canary"],
        "__CANARY_GUID__": site["canary_guid"],
        "__N_MOLECULES__": str(doc["benchmark"]["n_molecules"]),
        "__N_MODELS__": str(doc["benchmark"]["runs"]),
    }
    for k, v in subs.items():
        # Text placeholders are HTML-escaped; the JSON payload is inserted verbatim.
        text = text.replace(k, v if k in ("__LEADERBOARD_JSON__", "__LOGO_SPRITE__", "__CHARTS_HTML__") else html.escape(v, quote=True))
    left = re.findall(r"__[A-Z_]{3,}__", text)
    if left:
        sys.exit(f"unreplaced placeholders in template: {sorted(set(left))}")
    out = out or SITE / "index.html"
    out.write_text(text)
    return out


class _Refs(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs, self.scripts_json, self.title = [], 0, None
        self._in_title = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        for key in ("src", "href", "data-animation", "data-poster"):
            v = a.get(key)
            if v and not v.startswith(("http://", "https://", "#", "mailto:", "data:")):
                self.refs.append(v.split("#")[0].split("?")[0])
        if tag == "script" and a.get("type") == "application/json":
            self.scripts_json += 1
        if tag == "title":
            self._in_title = True

    def handle_data(self, data):
        if self._in_title:
            self.title = (self.title or "") + data

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False


def check_site() -> int:
    problems = []
    index = SITE / "index.html"
    if not index.exists():
        problems.append("site/index.html missing")
    else:
        p = _Refs()
        p.feed(index.read_text())
        for ref in sorted(set(p.refs)):
            if ref and not (SITE / ref).exists():
                problems.append(f"index.html references missing file: {ref}")
        if not p.title:
            problems.append("index.html has no <title>")
        if p.scripts_json == 0:
            problems.append("index.html has no inline application/json data block")
        left = sorted(set(re.findall(r"__[A-Z_]{3,}__", index.read_text())))
        if left:
            problems.append(f"index.html still contains placeholders: {left}")
        for m in re.finditer(r"url\(([^)]+)\)", (SITE / "fonts" / "google-sans-code.css").read_text()
                             if (SITE / "fonts" / "google-sans-code.css").exists() else ""):
            ref = m.group(1).strip("'\"")
            if not ref.startswith(("http", "data:")) and not (SITE / "fonts" / ref).exists():
                problems.append(f"fonts/google-sans-code.css references missing file: {ref}")
    data = SITE / "data" / "leaderboard.json"
    if data.exists():
        doc = json.loads(data.read_text())
        if len(doc["entries"]) < 1:
            problems.append("leaderboard.json has no entries")
        for e in doc["entries"]:
            if not (0 <= e["ci95"]["low"] <= e["success_rate"] <= e["ci95"]["high"] <= 100):
                problems.append(f"{e['model_id']}: CI does not bracket the rate")
        if doc.get("release_version") != "v18" or doc.get("benchmark", {}).get("version") != "v18":
            problems.append("website release metadata must be v18")
        if any(e.get("verifier_version") != "moldraft.stereochemistry/v18" or e["n"] != 300 for e in doc["entries"]):
            problems.append("all model results must use the v18 verifier and denominator 300")
        if len(doc["entries"]) != 9 or sum(e["passed"] for e in doc["entries"]) != 1419:
            problems.append("website scores do not match the nine-model v18 release")
        if {key: value["n"] for key, value in doc["sources"].items()} != {"vsepr": 59, "np": 70, "literature": 171}:
            problems.append("website source categories do not match v18")
        if len(doc["benchmark"]["verifier"]["gates"]) != 3 or doc["benchmark"]["verifier"].get("geometry_blind"):
            problems.append("website must describe all three v18 checks")
        if DATA_REPO:
            for name, digest in doc["source_files"].items():
                if sha256(DATA_REPO / name) != digest:
                    problems.append(f"stale data source: {name}")
        if "charts" in doc and index.exists():
            problems += charts.check_charts(index.read_text(), doc["charts"])
            for variant in doc["charts"]:
                f = SITE / "charts" / f"{variant}.svg"
                if not f.exists():
                    problems.append(f"standalone chart missing: charts/{variant}.svg")
                elif "var(" in f.read_text():
                    problems.append(f"charts/{variant}.svg still contains CSS variables")
    else:
        problems.append("site/data/leaderboard.json missing")
    # Leak scan over every text file shipped.
    for f in SITE.rglob("*"):
        if f.is_file() and f.suffix.lower() in {".html", ".css", ".js", ".json", ".svg", ".txt", ".md"}:
            txt = f.read_text(errors="replace")
            for pat in LEAK_PATTERNS:
                m = pat.search(txt)
                if m:
                    problems.append(f"{f.relative_to(SITE)}: leak pattern {pat.pattern!r} matched {m.group(0)!r}")
    # Nothing but the expected file types.
    for f in SITE.rglob("*"):
        if f.is_file() and f.name != ".nojekyll" and f.suffix.lower() not in {".html", ".css", ".js", ".json", ".svg", ".woff2", ".png", ".gif", ".ico", ".txt", ".md", ".webmanifest"}:
            problems.append(f"unexpected file type shipped: {f.relative_to(SITE)}")
    if problems:
        print("CHECK FAILED:")
        for p in problems:
            print("  -", p)
        return 1
    print("check ok: assets resolve, CIs bracket rates, no molecule names or case ids in site/")
    return 0


def main() -> int:
    global DATA_REPO, SITE
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="run structural and leak checks after building")
    ap.add_argument("--check-only", action="store_true", help="only run the checks")
    ap.add_argument("--template", type=Path, help="render this template instead of templates/index.html")
    ap.add_argument("--out-html", type=Path, help="write the rendered page here instead of site/index.html")
    ap.add_argument("--data-repo", type=Path, help="MolDraft v18 data checkout")
    ap.add_argument("--site-dir", type=Path, help="static output directory")
    args = ap.parse_args()
    if args.data_repo:
        DATA_REPO = args.data_repo.resolve()
    if args.site_dir:
        SITE = args.site_dir.resolve()
    if not args.check_only:
        doc = build_doc()
        (SITE / ".nojekyll").write_text("")
        # Charts are laid out before the JSON is written so leaderboard.json carries their metadata.
        charts_markup, doc["charts"] = charts.charts_html(doc)
        (SITE / "charts").mkdir(parents=True, exist_ok=True)
        for variant in doc["charts"]:
            if variant in charts.VARIANTS:
                svg = charts.render_svg(charts.layout(doc["entries"], variant), literal=True)
            else:
                svg = charts.render_bins_svg(doc["atom_bins"], literal=True,
                                             series=charts.bin_series(doc["atom_bins"], doc["entries"], "all", {}))
            (SITE / "charts" / f"{variant}.svg").write_text(svg + "\n")
        (SITE / "data").mkdir(parents=True, exist_ok=True)
        out = SITE / "data" / "leaderboard.json"
        out.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n")
        print(f"  wrote {out}  ({len(doc['entries'])} entries)")
        doc["_charts_markup"] = charts_markup
        page = render_page(doc, args.template, args.out_html)
        if page:
            try:
                print(f"  wrote {page.relative_to(HERE.parent.parent)}")
            except ValueError:
                print(f"  wrote {page}")
        w = max(len(e["display_name"]) for e in doc["entries"])
        for e in doc["entries"]:
            print(f"  {e['rank']:>2}  {e['display_name']:<{w}}  {e['success_rate']:5.1f}%  "
                  f"[{e['ci95']['low']:.1f}, {e['ci95']['high']:.1f}]  {e['passed']}/{e['n']}")
    if args.check or args.check_only:
        return check_site()
    return 0


if __name__ == "__main__":
    sys.exit(main())
