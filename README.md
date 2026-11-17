# MolDraft v18

Data, submitted structures, evaluation records, and verifier for **Can Language Models Build Molecules in Three Dimensions?**

**[Explore the public MolDraft leaderboard](https://the-matter-lab.github.io/MolDraft-data/)** — interactive scores, costs, tokens, and total-atom charts.

The release version and Git tag are **v18**. The result set is `moldraft.formal/v18`; every main-experiment and two-tool ablation verdict uses `moldraft.stereochemistry/v18`.

## Dataset

MolDraft contains **300 molecular drawing/reference pairs**: 59 VSEPR-curated structures, 70 natural products, and 171 literature structures. Each task requires an XYZ structure containing all atoms, including hydrogens.

`data/index.csv` links each molecule ID to its category, input image, reference coordinates, atom counts, and source identifier. The 300 images in `data/png/` and 300 structures in `data/xyz/` have matching filename stems. Source information is recorded in `data/references.tsv` and `data/REFERENCES.md`; geometric annotations are in `data/geometry.tsv` and `data/descriptors.tsv`. The `paper` and `screenshot` source labels both map to the literature category. Organic nSPS analyses use the 84 metal-free natural-product and literature entries.

## v18 results

The nine models have **1,419 passes in 2,700 attempts**. Per-model resolve rates range from **25.0% to 76.0%**, using all 300 attempts in each denominator.

| Model | Passes / 300 | Resolve rate |
|---|---:|---:|
| gpt-6-astra | 228 | 76.00% |
| gpt-6.1-sol | 214 | 71.33% |
| claude-opus-5 | 173 | 57.67% |
| claude-fable-5-1 | 162 | 54.00% |
| claude-opus-5-5 | 162 | 54.00% |
| qwen3.8-max | 140 | 46.67% |
| gpt-6-sol | 137 | 45.67% |
| kimi-k3 | 128 | 42.67% |
| gpt-6-luna | 75 | 25.00% |

The GPT-6.1-sol two-tool ablation resolves **201/300** molecules, with **214/300** for its paired four-tool baseline. Both configurations use the v18 verifier.

- `results/final_results/verification_2700.json`: all main-experiment verdicts and diagnostics.
- `results/final_results/summary.csv`: model totals, tokens, and costs.
- `results/final_results/accuracy_all_models_and_ablations.csv`: v18 scores for all nine models and the two-tool ablation.
- `results/final_results/answer_index.csv`: every main attempt, linked to its reference, answer where present, hashes, and verdict.
- `results/final_results/<model>/`: per-molecule verdicts, resource-use tables, summaries, and session records.
- `results/two_tool_ablation/`: ablation answers, transcripts, verdicts, paired comparison, and answer index.
- `configuration/`: model settings, tools, budgets, and recorded prompts.
- `analysis/`: manuscript analysis outputs.

All **2,605 available main answers**, **300 ablation answers**, **2,700 main transcripts**, and **300 ablation transcripts** are included. The 95 main attempts without an answer remain explicit failures. Images in transcript tool messages are represented by `[image]`; input drawings are provided in `data/png/`.

All outcomes are pass or fail. Timeouts, searches without the required MAPPA correspondence, and xTB failures count as failures in the full denominator. Diagnostic flags record failure reasons. Rates for a chemical subset use that subset's complete molecule count.

## v18 verifier

`benchmark/structure_verifier.py` implements the v18 checks, with documentation in `benchmark/VERIFICATION.md` and settings in `benchmark/verification_policy.json`. MAPPA is pinned to commit `2f9762e1e09801e619cfd537abf3798ae8b0f3de`. The verification checks molecular identity, stereochemical configuration, and coarse coordination-site geometry. No coordination bond-length cutoff is applied.

```bash
python -m pip install -r benchmark/requirements-current.txt
```

Use Python 3.12 and xTB 6.7.1 for GFN2 WBO calculations. The documented `structure_verifier.verify_arrays` interface accepts reference and prediction element/coordinate/WBO arrays. Whole-case timeout handling belongs to the caller, as specified in the verification documentation. Model-provider credentials are not needed for verification.

## Validation

```bash
python tools/check_integrity.py
python tools/summarize_results.py
```

`release.json` records v18, dataset and model counts, and the verifier version. `checksums.sha256` covers every deposited file except the checksum file itself. `tools/check_integrity.py` checks hashes, all 300 drawing/reference pairs, v18 version consistency, answer indices, per-model and combined verdicts, summaries, and paired ablation scores. See `VALIDATION.md` and `audit/v18.json` for the validation results.

## Sources and rights

Source-specific conditions apply to third-party drawings and coordinates. See `data/references.tsv`, `data/REFERENCES.md`, and `SOURCE_NOTICES.md`. This repository does not assign a blanket licence to third-party material.

## Website

GitHub Pages publishes the static website from `docs/`. The source is in `website/` and reads these v18 result records directly. To rebuild and refresh file checksums:

```bash
python website/build.py --check
python tools/update_checksums.py
python tools/check_integrity.py
```
