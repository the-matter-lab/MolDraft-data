# MolDraft v18 results

Release: `v18`. Result set: `moldraft.formal/v18`. Verifier: `moldraft.stereochemistry/v18`.

The nine models have **1,419 passes in 2,700 attempts**. Every model uses a denominator of 300. The two-tool ablation has **201/300** passes; its paired four-tool baseline has **214/300**. All verdicts use v18.

`verification_2700.json`, per-model `verification.json`, `per_case.csv`, `summary.json`, `summary.csv`, and `accuracy_all_models_and_ablations.csv` report these scores. The answer indices link each attempt to its reference, available answer, hashes, and verdict. Session transcripts, input drawings, reference coordinates, submitted structures, tokens, and generation costs are provided.

All outcomes are pass or fail. Timeouts, searches without the required MAPPA correspondence, and failed xTB calculations are failures in the full denominator. Diagnostic flags record failure reasons.
