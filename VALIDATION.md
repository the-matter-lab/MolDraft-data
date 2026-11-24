# MolDraft v18 validation

Release: **v18**. Result set: `moldraft.formal/v18`. Verifier: `moldraft.stereochemistry/v18`.

- 300 input drawings, 300 reference XYZ structures, and one index record per molecule.
- 2,700 main verdicts for nine models, with 1,419 passes and 300 attempts per model.
- 300 two-tool ablation verdicts with 201 passes. The paired [four-tool baseline](results/final_results/gpt-6.1-sol) has 214 passes across the same 300 cases.
- 2,605 available main answers and 300 ablation answers, with answer/reference hashes in the indices.
- 2,700 main session transcripts and 300 ablation transcripts.
- All released verdicts use the v18 verifier and the recorded policy.
- Drawing images, reference coordinates, submitted answers, and session transcripts preserve their recorded bytes.
- Per-molecule verdicts, combined records, CSV tables, answer indices, and summary counts are checked for agreement.
- The checksum manifest covers every deposited file except itself.

Run `python tools/check_integrity.py` and `python tools/summarize_results.py` from the repository root. The machine-readable report is `audit/v18.json`. These checks establish completeness and consistency; they do not independently reassess the chemistry of each molecule.
