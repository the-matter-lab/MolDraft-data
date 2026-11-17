# MolDraft v18 verifier

`structure_verifier.py` is the implementation used for the v18 2700 main and
300 ablation records. Install `requirements-current.txt` in Python 3.12, with
xTB 6.7.1 available separately for GFN2 single points. MAPPA is unmodified.

Compute GT and prediction WBO matrices at the reference charge/spin without
optimizing either submitted geometry. Supply each `(elements, coordinates, wbo)`
triple to `structure_verifier.verify_arrays`; the matrix interface uses Angstrom
coordinates. The campaign enforces a 300-second whole-case process watchdog;
the library caller must supply this outer guard when reproducing that policy.

The unchanged native MAPPA search uses 3 seeds, branch cap 10000, iso tolerance
1, graph/cut floor 0.15, ordinary/metal WBO-change thresholds 0.5/0.3 and no cut
sweep. One native zero-event correspondence is used for all coordinate checks.
R/S-related configuration, E/Z, supported axes and configuration loss are
checked without enumerating alternative molecular mappings.

Coordination reference contacts require WBO>=0.15, without a bond-length cutoff.
Adjacent non-H, nonmetal donors connected in a separate WBO-only covalent
subgraph (floor 0.4) with mutual WBO>=1.1 form one haptic site. Metal bridges
and ordinary single donor--donor bonds do not merge separate positions.
Prediction retention requires WBO>=0.10 for at least one donor of each reference
site. Equivalent terminal donors attached to the same nonmetal atom can retain
one occupied position; selection uses WBO and keeps the mapped reference donor
on an exact tie. Distance and angle fitting do not select a replacement donor.
No absolute, radius-based or reference-relative distance cutoff enters the
coordination check. Coordinates supply site directions and angles; the existing
noncoordination stereo graph remains unchanged.
Angles are compared within chemical site-pair classes, with chelate and
interligand angles separated. RMS>20 degrees OR maximum deviation>60 degrees
fails, including values just over the cutoffs. These are coarse operational
tolerances; general metal Delta/Lambda chirality is not claimed.

Scores have only pass and fail. Timeouts, no required MAPPA correspondence and
xTB failures are fail, with raw diagnostic flags retained as failure reasons.
Every main-model or ablation rate has denominator 300. Exact settings are in
`verification_policy.json` and each verification record. Reference and answer
hashes are included in the answer indices and verdict records.
