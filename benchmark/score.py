"""Whole-case watchdog and GFN2-xTB inputs for the published v18 verifier."""
from __future__ import annotations

from collections import Counter
import hashlib
import json
import math
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import tempfile

from .structure_verifier import (
    ReferenceConstraintError, VerificationUnresolved, provenance, verify_arrays,
)


def parse_xyz(text: str):
    lines = text.splitlines()
    try:
        n = int(lines[0])
        if n < 1 or len(lines) < n + 2 or any(line.strip() for line in lines[n + 2:]):
            raise ValueError("Incorrect atom count.")
        atoms = []
        for line in lines[2:n + 2]:
            element, x, y, z, *_ = line.split()
            if not re.fullmatch(r"[A-Z][a-z]?", element):
                raise ValueError(f"Invalid element: {element}")
            coords = tuple(float(value) for value in (x, y, z))
            if not all(math.isfinite(value) for value in coords):
                raise ValueError("Non-finite coordinate.")
            atoms.append((element, *coords))
    except (IndexError, ValueError) as exc:
        raise ValueError(f"Invalid XYZ: {exc}") from exc
    return atoms


def charge_spin(reference_text):
    comment = reference_text.splitlines()[1]
    charge = re.search(r"\bq\s*=\s*(-?\d+)", comment)
    multiplicity = re.search(r"\bmultiplicity\s*=\s*(\d+)", comment)
    spin = re.search(r"\bS\s*=\s*(\d+(?:\.\d+)?)", comment)
    uhf = max(0, int(multiplicity[1]) - 1) if multiplicity else round(2 * float(spin[1])) if spin else 0
    return int(charge[1]) if charge else 0, uhf


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verdict(flag, *, error=None, verifier_error=False):
    return {
        "flag": flag, "overall_pass": False, "verifier_error": verifier_error,
        "aam_pass": False, "stereo_pass": None, "geometry_pass": None, "error": error,
    }


def verify_child(reference, prediction, work, threads, timeout):
    from mappa.chemistry_computations.xtb import run_xtb

    try:
        reference_text = reference.read_text()
        ref_atoms = parse_xyz(reference_text)
    except (ValueError, OSError) as exc:
        return verdict("no_gt_xyz", error=str(exc), verifier_error=True)
    try:
        pred_atoms = parse_xyz(prediction.read_text())
    except (ValueError, OSError) as exc:
        return verdict("parse_fail", error=str(exc))
    if Counter(a[0] for a in ref_atoms) != Counter(a[0] for a in pred_atoms):
        return verdict("wrong_mol", error="Element composition differs.")
    charge, uhf = charge_spin(reference_text)
    args = {"charge": charge, "uhf": uhf, "omp_threads": threads}
    try:
        ref_data = run_xtb(reference, work / "reference", **args)
    except Exception as exc:
        return verdict("gt_xtb_failed", error=str(exc), verifier_error=True)
    try:
        pred_data = run_xtb(prediction, work / "prediction", **args)
    except Exception as exc:
        return verdict("pred_xtb_failed", error=str(exc), verifier_error=True)
    try:
        result = verify_arrays(*ref_data, *pred_data, wall_time_seconds=timeout)
    except VerificationUnresolved as exc:
        result = verdict("verification_unresolved", error=str(exc), verifier_error=True)
        result.update(getattr(exc, "verification_record", {}))
    except ReferenceConstraintError as exc:
        result = verdict("reference_constraint_error", error=str(exc), verifier_error=True)
    except Exception as exc:
        result = verdict("aam_failed", error=str(exc), verifier_error=True)
    result.update(charge=charge, uhf=uhf)
    result["gt_copy_suspected"] = (
        sorted((a[0], *(round(v, 4) for v in a[1:])) for a in ref_atoms)
        == sorted((a[0], *(round(v, 4) for v in a[1:])) for a in pred_atoms)
    )
    return result


def verify_case(reference: Path, answer: Path, work: Path, *, threads=1, timeout=300):
    if not answer.is_file():
        return verdict("no_answer")
    with tempfile.TemporaryDirectory(prefix="moldraft-verification-", dir=work) as temp:
        scratch = Path(temp).resolve()
        command = [sys.executable, "-m", "benchmark.score", str(reference.resolve()),
                   str(answer.resolve()), str(scratch), str(threads), str(timeout)]
        with (scratch / "worker.log").open("wb") as log:
            process = subprocess.Popen(command, stdout=log, stderr=log, start_new_session=True)
            try:
                process.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                process.wait()
                return verdict("timeout", error=f"Whole-case budget of {timeout}s exceeded.",
                               verifier_error=True)
        output = scratch / "verdict.json"
        if process.returncode or not output.is_file():
            log_tail = (scratch / "worker.log").read_text(errors="replace")[-1500:]
            return verdict("verifier_crashed", error=log_tail, verifier_error=True)
        return json.loads(output.read_text())


if __name__ == "__main__":
    reference, answer, work = map(Path, sys.argv[1:4])
    provenance()
    row = verify_child(reference, answer, work, int(sys.argv[4]), int(sys.argv[5]))
    (work / "verdict.json").write_text(json.dumps(row))
