<p align="center">
  <img src="docs/assets/moldraft-logo.png" alt="MolDraft logo" width="128">
</p>

<h1 align="center">MolDraft</h1>

<p align="center"><strong>Can Language Models Build Molecules in Three Dimensions?</strong></p>

<p align="center">
  <a href="https://arxiv.org/abs/2611.25041">Paper (arXiv)</a> ·
  <a href="https://the-matter-lab.github.io/MolDraft-data/">Leaderboard</a> ·
  <a href="https://the-matter-lab.github.io/MolDraft-data/blog/">Research blog</a> ·
  <a href="https://the-matter-lab.github.io/MolDraft-data/data_300_new.html">2D Data Gallery</a> ·
  <a href="https://github.com/the-matter-lab/MolDraft-data/releases/latest">Download release</a> ·
  <a href="#citation">Citation</a>
</p>

MolDraft benchmarks how well multimodal language models build 3D molecular structures from 2D chemical drawings. Given one drawing and a short instruction, an agent must produce an `answer.xyz` file with coordinates for every atom, including hydrogens. The verifier checks molecular identity, stereochemical configuration, and coarse coordination geometry against a reference structure.

## Dataset and results

The benchmark contains **300 drawing–structure pairs** across 59 VSEPR-curated structures, 70 natural products, and 171 literature structures. The current leaderboard covers ten models and **1,649 of 3,000 attempts passed**. GPT-6.2 Astra leads with **230/300 (76.7%)**. The manuscript evaluation covers nine models and 1,419 passes in 2,700 attempts. In the paired GPT-6.1 Sol ablation, the two-tool setup resolves **201/300** molecules and the four-tool setup resolves **214/300**.

| What you need | Where to find it |
| --- | --- |
| Dataset index | [data/index.csv](data/index.csv), with category, atom counts, and paths for each pair |
| Benchmark inputs and references | [2D drawings](data/png) and [reference XYZ structures](data/xyz) |
| Model scores | [Main results summary](results/final_results/summary.csv) and [model and ablation comparison](results/final_results/accuracy_all_models_and_ablations.csv) |
| GPT-6.2 Astra leaderboard run | [Per-molecule scores and usage](website/supplemental_runs/gpt-6.2-astra.json) |
| Main answers, sessions, and verdicts | [Answer index](results/final_results/answer_index.csv), [per-model records](results/final_results), and [combined verdicts](results/final_results/verification_2700.json) |
| Paired tool ablation | [Two-tool records](results/two_tool_ablation), [four-tool GPT-6.1 Sol baseline](results/final_results/gpt-6.1-sol), and [per-molecule comparison](results/two_tool_ablation/eval/comparison.csv) |
| Prompts and model settings | [Main run settings](configuration) and [ablation run configuration](results/two_tool_ablation/eval/run_config.json) |
| Manuscript analysis | [analysis/](analysis) |

The release includes 2,605 main answers, 300 ablation answers, and all 3,000 session transcripts. Attempts without an answer count as failures.

## Quick start

The repository includes the data, a standalone four-tool agent, and the published verifier. Use the current `main` branch to run new evaluations.

```bash
git clone https://github.com/the-matter-lab/MolDraft-data.git
cd MolDraft-data
python tools/check_integrity.py
python tools/summarize_results.py
```

The [integrity check](VALIDATION.md) verifies file hashes, dataset completeness, and agreement across the result tables. The [Zenodo snapshot](https://doi.org/10.5281/zenodo.24511623) archives the paper data.

## Run the benchmark

Use Linux with unprivileged user, mount, PID, and network namespaces enabled. The launcher uses `unshare`, `mount`, `setpriv`, and `chroot` from the system. On Debian or Ubuntu install `util-linux` and `coreutils` if needed. Install the scientific tools in a dedicated environment outside the data and run directories.

```bash
mamba env create -f environment.yml
mamba activate moldraft
python -m pip install -r benchmark/requirements-runner.txt
python -m benchmark check
```

The check verifies the namespace sandbox, xTB and MAPPA installation before you use a model API. Each session starts with one anonymous PNG. The shell and programs it launches can write to that session only. They see a cleared environment, a read-only tool installation, and an isolated network. Model requests are made by the runner outside the tool sandbox. If the host blocks the namespaces, use a Linux VM or compute node that permits them.

Set the API key for your model in your shell. The published model IDs and reasoning levels are listed in [configuration/models.json](configuration/models.json).

| Interface | Provider selection | Credentials and endpoint |
| --- | --- | --- |
| OpenAI Responses | `--provider openai` or automatic for `gpt-*` | `OPENAI_API_KEY`, optional `OPENAI_BASE_URL` ending in `/v1` |
| Anthropic Messages | `--provider anthropic` or automatic for `claude-*` | `ANTHROPIC_API_KEY`, optional `ANTHROPIC_BASE_URL` |
| OpenAI-compatible Chat Completions | `--provider chat` or automatic for Kimi and Qwen | `MOONSHOT_API_KEY` with optional `MOONSHOT_BASE_URL`, or `QWEN_API_KEY` with `QWEN_BASE_URL` |

Use `MOLDRAFT_API_KEY` and `MOLDRAFT_BASE_URL` to override those settings for a compatible endpoint. If your provider uses a different ID for the same model, set `--api-model` and keep the paper ID in `--model` to load its settings.

Run two cases to check your endpoint and tools. The example assumes you have access to `gpt-6.1-sol`.

```bash
python -m benchmark run --model gpt-6.1-sol --limit 2 --out work/smoke
python -m benchmark verify --run work/smoke
```

Run the complete 300-molecule benchmark in a separate directory:

```bash
python -m benchmark run --model gpt-6.1-sol --workers 4 --out work/gpt-6.1-sol
python -m benchmark verify --run work/gpt-6.1-sol --workers 4
```

The default agent exposes `view_png_file`, `view_molecule`, `constraint_xtb`, and `bash_kernel`. Add `--profile png-bash` to the generation command to run the two-tool ablation in a fresh output directory. The runner uses the deposited prompts, reasoning levels, one attempt per molecule and at most 100 model calls per attempt. Endpoint behavior and sampling can affect newly generated answers. The deposited results remain the record of the published runs.

Scoring uses v18 with a 300-second whole-case watchdog. Every attempt is in the denominator, including missing answers and verifier failures. A limited run is a subset check. See the [verification method](benchmark/VERIFICATION.md) and [recorded policy](benchmark/verification_policy.json).

You can also score your own reference/answer pair without calling a model:

```bash
python -m benchmark verify-xyz --reference reference.xyz --prediction answer.xyz --work-dir work/pair
```

### Follow a session locally

The runner writes one JSON object per line to `transcript.jsonl` as the session runs. The log includes prompts, model replies, token usage, tool calls, and text outputs. Image outputs appear as `[image]` markers. Once the first session starts, open its transcript in an editor or follow it from another terminal at the repository root:

```bash
tail -f work/smoke/sessions/mol_0001/transcript.jsonl
```

The published drawings and reference coordinates are in [`data/`](data), and the paper's archived answers, transcripts, and verdicts are in [`results/`](results). New runs write to the directory passed to `--out`. For the example `--out work/smoke`, paths inside that directory are:

| File or directory | Contents |
| --- | --- |
| `run.json` | Run settings and the mapping from anonymous case IDs to dataset molecule IDs |
| `sessions/mol_0001/transcript.jsonl` | Live transcript for that case |
| `sessions/mol_0001/session.json` | Final session status and call and token counts |
| `sessions/mol_0001/answer.xyz` | Submitted coordinates, if the case produced a submission |
| `work/mol_0001/` | Anonymous input image and working files created by the tools |
| `eval/verification.json` and `eval/per_case.csv` | Scores and failure reasons written by `verify` |

These local files are available without a tracing service. You can use the JSONL records with your own tracing or analysis tools. The top-level `work/` directory used in the examples is ignored by Git.

## Sources and rights

The [2D Data Gallery](https://the-matter-lab.github.io/MolDraft-data/data_300_new.html) shows sources for each drawing and reference structure. The same records are in the [dataset bibliography](data/REFERENCES.md) and [per-molecule provenance table](data/references.tsv). See [source notices](SOURCE_NOTICES.md) for attribution and licence terms.

The original MolDraft software and its documentation are released under the [MIT License](LICENSE). Dataset drawings and coordinates retain their source-specific terms. External dependencies retain their own licences.

## Citation

If you use MolDraft, please cite the [archived benchmark dataset](https://doi.org/10.5281/zenodo.24511623) and the [accompanying preprint](https://arxiv.org/abs/2611.25041). GitHub provides dataset citation exports from [CITATION.cff](CITATION.cff).

```bibtex
@misc{xu2026moldraft,
  title         = {Can Language Models Build Molecules in Three Dimensions?},
  author        = {Xu, Hanyong and Zou, Yunheng and Nieto Faza, Olalla and
                   P{\'e}rez S{\'a}nchez, Juan Bernardo and Yin, Aiwei and
                   Aspuru-Guzik, Al{\'a}n and Bernales, Varinia},
  year          = {2026},
  eprint        = {2611.25041},
  archivePrefix = {arXiv},
  primaryClass  = {physics.chem-ph},
  url           = {https://arxiv.org/abs/2611.25041}
}
```

Website maintenance and asset build instructions are in the [website guide](website/README.md). The launch thread and video assets are in [website/promotion](website/promotion).
