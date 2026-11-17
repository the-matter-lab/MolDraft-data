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

Only aggregate statistics are exported into the website. Input drawings, molecule identifiers, and per-molecule answers are accessed through the separate data repository link. The site requires no backend and uses relative asset paths suitable for a GitHub Pages project URL.
