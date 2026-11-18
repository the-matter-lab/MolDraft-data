# MolDraft v18 website

Static leaderboard and interactive cost, token, and total-atom charts for MolDraft v18. All scores and chart aggregates are computed from the public v18 data release and checked against its manuscript analysis outputs.

## Build in this workspace

```bash
python structure_2d_to_3d/moldraft/build.py --data-repo /path/to/MolDraft-data --check
```

This updates `site/`. `--check-only` verifies the existing output. `--site-dir` selects another output directory.

## Build in the public data repository

The website source is in `website/`, and GitHub Pages serves `docs/`:

```bash
python website/build.py --check
python tools/update_checksums.py
python tools/check_integrity.py
```

The builder reads `release.json`, the dataset index, model configuration, per-model v18 verification records, summaries, resource-use tables, and `analysis/results_metrics.json`. It checks all model totals, the three source categories, costs, tokens, and the five total-atom bins against the manuscript analysis. The verifier description covers identity, stereochemical configuration, and coarse coordination geometry.

Scores are exported as aggregate statistics. The introduction also pairs one original input drawing with a rotating view of a verified model-generated answer. All remaining drawings and per-molecule records are accessed through the data repository link. The site requires no backend and uses relative asset paths suitable for a GitHub Pages project URL.

## Rebuild the molecule demonstration

The checked-in GIF and still frame need no rendering dependencies to serve or build the website. To regenerate them, install NumPy and Pillow in a separate environment and run:

```bash
python website/render_demo.py
```

`website/demo/source.json` records the exact input drawing, generated answer, verification record, and their hashes. `website/demo/structure.npz` contains the corresponding verifier-owned single-point arrays. The renderer confirms that the coordinates match the deposited generated answer and that it passes all three v18 checks before producing a rigid rotation. The original coordinates are never optimized or replaced. GIF playback can be paused and defaults to a still frame when reduced motion is requested.
