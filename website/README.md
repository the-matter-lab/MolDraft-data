# MolDraft website

The MolDraft website contains the leaderboard, interactive charts, and 2D Data Gallery. The checked-in site is in [`docs/`](../docs), and its builder and templates are in this directory.

## Preview the website

From the repository root, serve the checked-in site:

```bash
python -m http.server 8000 --bind 127.0.0.1 --directory docs
```

Open the [leaderboard](http://127.0.0.1:8000/) or the [2D Data Gallery](http://127.0.0.1:8000/data_300_new.html) in your browser.

## Rebuild from the dataset

From the repository root:

```bash
python website/build.py --check
python tools/update_checksums.py
python tools/check_integrity.py
```

The builder reads the release metadata, dataset index, model settings, and evaluation records. It checks manuscript runs against the published analysis and reads newer runs from [supplemental_runs/](supplemental_runs). Supplemental runs use the same dataset and verifier. Their files record per-molecule verdicts, token usage, and the pricing used to estimate cost. Use `python website/build.py --check-only` to validate the existing site. GitHub Pages serves `docs/`.

Scores are exported as aggregate statistics. Below the leaderboard, a demonstration pairs one original input drawing with a rotating view of a verified model-generated answer, followed by the explanatory text. The 2D Data Gallery copies the 300 original PNGs from the release and links each entry to its sources using the dataset index, provenance table, and bibliography. Per-molecule evaluation records are accessed through the data repository link. The site requires no backend and uses relative asset paths suitable for a GitHub Pages project URL.

The Table view includes the demonstration, explanatory text, and footer. Cost/Molecule, Tokens, and Atoms show their chart panels and hide those lower sections. Atoms initially shows Top 5. Returning to Table or following an About link restores the full page. Direct `?view=` links use the same behavior.

## Rebuild the molecule demonstration

The checked-in GIF and still frame need no rendering dependencies to serve or build the website. To regenerate them, install NumPy and Pillow in a separate environment and run:

```bash
python website/render_demo.py
```

`website/demo/source.json` records the exact input drawing, generated answer, verification record, and their hashes. `website/demo/structure.npz` contains the corresponding verifier-owned single-point arrays. The renderer confirms that the coordinates match the deposited generated answer and that it passes all three verifier checks before producing a rigid rotation. The original coordinates are never optimized or replaced. GIF playback can be paused and defaults to a still frame when reduced motion is requested.
