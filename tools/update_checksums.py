"""Refresh the checksum manifest after rebuilding the MolDraft v18 website."""
from pathlib import Path
import hashlib

root = Path(__file__).resolve().parent.parent
files = sorted(path for path in root.rglob("*")
               if path.is_file() and path.name != "checksums.sha256"
               and not {".git", "__pycache__", ".pytest_cache", ".venv", "work"}.intersection(path.relative_to(root).parts)
               and path.name != ".env" and not path.name.startswith(".env."))
(root / "checksums.sha256").write_text("".join(
    hashlib.sha256(path.read_bytes()).hexdigest() + "  " + path.relative_to(root).as_posix() + "\n"
    for path in files))
print(f"Updated checksums for {len(files)} files.")
