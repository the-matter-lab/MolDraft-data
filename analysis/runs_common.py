"""Shared loading for the results scripts (results_tables.py, make_results_figs.py, dataset_stats.py).

The scored rows are each LLM's 300 merged rows on data_300_new, as collected in final_results
(structure_2d_to_3d/final_results/<model>/verification.json in the ElAgente repository): the entries
unchanged since data300 keep their re-verified rows, the rest were rerun and verified with the alignment
timeout at 400 s and one retry at 900 s. Overall rates use all 300 attempts. Subset rates use every molecule in the selected subset;
verifier errors remain in the denominator and do not count as resolved.

Size and complexity are binned by quantiles of this dataset rather than at fixed widths, so that every
bin holds about the same number of molecules: heavy atoms in quintiles over all 300, nSPS in quartiles
over the natural products. Heavy atoms are counted from the reference xyz files, which are authoritative
where descriptors.tsv lags behind a corrected reference.
"""
import csv, json
from pathlib import Path

MODELS = ("gpt-6.1-sol", "gpt-6-astra", "claude-opus-5", "claude-opus-5-5", "claude-fable-5-1",
          "qwen3.8-max", "gpt-6-sol", "kimi-k3", "gpt-6-luna")
SOURCES = ["VSEPR", "natural_product", "literature"]
SOURCE_NAME = {"VSEPR": "VSEPR-curated", "natural_product": "Natural products",
               "literature": "Literature"}
# Legacy dataset labels describe depiction provenance; both belong to one literature source.
SOURCE_GROUP = {"paper": "literature", "screenshot": "literature"}
SIZE_BINS, NSPS_BINS = 5, 4


def read_dataset(data_dir):
    """(manifest, geometry, descriptors), keyed by name; descriptors' atom counts taken from the xyz files."""
    data_dir = Path(data_dir).expanduser()
    read = lambda f: {r["name"]: r for r in csv.DictReader(open(data_dir / f), delimiter="\t")}
    man, geo, des = read("manifest.tsv"), read("geometry.tsv"), read("descriptors.tsv")
    for table in (man, geo, des):
        for row in table.values():
            row["original_source"] = row["source"]
            row["source"] = SOURCE_GROUP.get(row["source"], row["source"])
    for name, r in des.items():
        lines = (data_dir / "xyz" / f"{name}.xyz").read_text().split("\n")
        n = int(lines[0].split()[0])
        els = [l.split()[0] for l in lines[2:2 + n]]
        r["heavy_atoms"] = str(sum(e != "H" for e in els))
        r["total_atoms"] = str(n)
    return man, geo, des


def load(final_dir, data_dir):
    """(rows by model, manifest, geometry, descriptors), each table keyed by molecule name."""
    final_dir = Path(final_dir).expanduser()
    man, geo, des = read_dataset(data_dir)
    rows = {}
    for model in MODELS:
        rows[model] = json.loads((final_dir / model / "verification.json").read_text())["rows"]
        if len(rows[model]) != 300:
            raise SystemExit(f"{model}: {len(rows[model])} rows, expected 300")
        unknown = [r["name"] for r in rows[model] if r["name"] not in man]
        if unknown:
            raise SystemExit(f"{model}: {len(unknown)} rows not in the dataset, e.g. {unknown[0]}")
    return rows, man, geo, des


def rate(model_rows, sel=lambda name: True):
    """Passes / all selected molecules; verifier errors stay in the denominator."""
    selected = [r for r in model_rows if sel(r["name"])]
    if not selected:
        return float("nan")
    return 100 * sum(bool(r["overall_pass"]) and not r["verifier_error"] for r in selected) / len(selected)


def quantile_cuts(values, k):
    """k-1 cut points, each a value of the data, that split it into k bins as equal as ties allow."""
    v = sorted(values)
    cands = sorted(set(v))
    return [min(cands, key=lambda c: (abs(sum(x < c for x in v) - i * len(v) / k), c)) for i in range(1, k)]


def quantile_bins(names, value, k, fmt="{:g}"):
    """[(label, selector)] for k quantile bins of value(name) over `names`; a bin holds lo <= x < next cut."""
    vals = [value(n) for n in names]
    cuts = quantile_cuts(vals, k)
    edges = [None] + cuts + [None]                 # the outer bins are open, so other sources fit too
    out = []
    for lo, hi in zip(edges, edges[1:]):
        inside = [x for x in vals if (lo is None or x >= lo) and (hi is None or x < hi)]
        label = f"{fmt.format(min(inside))}--{fmt.format(max(inside))}"
        out.append((label, lambda n, lo=lo, hi=hi: (lo is None or value(n) >= lo) and (hi is None or value(n) < hi)))
    return out


def size_bins(man, des):
    """Heavy-atom quintiles over all molecules."""
    return quantile_bins(list(man), lambda n: int(des[n]["heavy_atoms"]), SIZE_BINS)


def nsps_bins(man, des):
    """nSPS quartiles over the natural products; the selectors also apply to other sources."""
    nps = [n for n in man if man[n]["source"] == "natural_product"]
    # One decimal: rounded to integers, adjacent bins can print the same edge (42.57 and 43.39 -> 43).
    return quantile_bins(nps, lambda n: float(des[n]["nsps"]), NSPS_BINS, fmt="{:.2f}")


def organic_names(man, des):
    """Metal-free natural products and literature molecules used in the organic nSPS analysis."""
    return [n for n in man if man[n]["source"] in {"natural_product", "literature"}
            and des[n]["has_metal"] == "no"]


def organic_nsps_bins(man, des):
    names = organic_names(man, des)
    return quantile_bins(names, lambda n: float(des[n]["nsps"]), NSPS_BINS, fmt="{:.2f}")
