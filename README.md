<p align="center">
  <img src="docs/assets/moldraft-logo.png" alt="MolDraft logo" width="128">
</p>

<h1 align="center">MolDraft</h1>

<p align="center"><strong>Can Language Models Build Molecules in Three Dimensions?</strong></p>

<p align="center">
  <a href="#dataset-and-results">Dataset and results</a> ·
  <a href="website/README.md#preview-the-website">Preview the website</a> ·
  <a href="https://github.com/the-matter-lab/MolDraft-data/releases/latest">Download release</a> ·
  <a href="#citation">Citation</a>
</p>

MolDraft benchmarks how well multimodal language models build 3D molecular structures from 2D chemical drawings. Given one drawing and a short instruction, an agent must produce an `answer.xyz` file with coordinates for every atom, including hydrogens. The verifier checks molecular identity, stereochemical configuration, and coarse coordination geometry against a reference structure.

## Dataset and results

The benchmark contains **300 drawing–structure pairs** across 59 VSEPR-curated structures, 70 natural products, and 171 literature structures. Across nine models, **1,419 of 2,700 attempts passed**. Resolve rates range from **25.0% to 76.0%**. In the paired GPT-6.1 Sol ablation, the two-tool setup resolves **201/300** molecules and the four-tool setup resolves **214/300**.

| What you need | Where to find it |
| --- | --- |
| Dataset index | [data/index.csv](data/index.csv), with category, atom counts, and paths for each pair |
| Benchmark inputs and references | [2D drawings](data/png) and [reference XYZ structures](data/xyz) |
| Model scores | [Main results summary](results/final_results/summary.csv) and [model and ablation comparison](results/final_results/accuracy_all_models_and_ablations.csv) |
| Main answers, sessions, and verdicts | [Answer index](results/final_results/answer_index.csv), [per-model records](results/final_results), and [combined verdicts](results/final_results/verification_2700.json) |
| Paired tool ablation | [Ablation records](results/two_tool_ablation) and [per-molecule comparison](results/two_tool_ablation/eval/comparison.csv) |
| Prompts and model settings | [Main run settings](configuration) and [ablation run configuration](results/two_tool_ablation/eval/run_config.json) |
| Manuscript analysis | [analysis/](analysis) |

The release includes 2,605 main answers, 300 ablation answers, and all 3,000 session transcripts. Attempts without an answer count as failures.

## Quick start

Download the source archive from [GitHub Releases](https://github.com/the-matter-lab/MolDraft-data/releases/latest), or clone the repository to browse the data and reproduce the score summaries.

```bash
git clone https://github.com/the-matter-lab/MolDraft-data.git
cd MolDraft-data
python tools/check_integrity.py
python tools/summarize_results.py
```

The [integrity check](VALIDATION.md) verifies file hashes, dataset completeness, and agreement across the result tables. For a new evaluation, see the [verifier guide](benchmark/VERIFICATION.md) and [recorded verification policy](benchmark/verification_policy.json). The guide documents the Python dependencies, xTB version, and MAPPA pin.

## Evaluation setup

The benchmark uses Estructural, built on [El Agente (AgentNet)](https://github.com/the-matter-lab/ElAgente). Each molecule gets one attempt of at most 100 model calls. The agent runs without network access or access to the reference structures. The [local website preview](website/README.md#preview-the-website) links to the four tool implementations. The [Estructural case studies](https://github.com/the-matter-lab/ElAgenteEstructuralCaseStudies) are public.

## Sources and rights

The 2D Data Gallery in the [local website preview](website/README.md#preview-the-website) shows sources for each drawing and reference structure. The same records are in the [dataset bibliography](data/REFERENCES.md) and [per-molecule provenance table](data/references.tsv). See [source notices](SOURCE_NOTICES.md) for attribution and licence terms.

## Citation

If you use MolDraft, please cite the benchmark and its accompanying manuscript. GitHub also provides citation exports from [CITATION.cff](CITATION.cff).

```bibtex
@misc{xu2026moldraft,
  title        = {Can Language Models Build Molecules in Three Dimensions?},
  author       = {Xu, Hanyong and Zou, Yunheng and Nieto Faza, Olalla and
                  Perez Sanchez, Juan Bernardo and Yin, Aiwei and
                  Aspuru-Guzik, Al{\'a}n and Bernales, Varinia},
  year         = {2026},
  howpublished = {MolDraft benchmark dataset and evaluation records},
  url          = {https://github.com/the-matter-lab/MolDraft-data/releases/latest}
}
```

Website maintenance and asset build instructions are in the [website guide](website/README.md).
