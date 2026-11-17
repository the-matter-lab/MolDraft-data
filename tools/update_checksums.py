"""Refresh the checksum manifest after rebuilding the MolDraft v18 website."""
from pathlib import Path
import hashlib

root = Path(__file__).resolve().parent.parent
files = sorted(path for path in root.rglob("*")
               if path.is_file() and path.name != "checksums.sha256"
               and ".git" not in path.relative_to(root).parts
               and "__pycache__" not in path.relative_to(root).parts)
(root / "checksums.sha256").write_text("".join(
    hashlib.sha256(path.read_bytes()).hexdigest() + "  " + path.relative_to(root).as_posix() + "\n"
    for path in files))
print(f"Updated checksums for {len(files)} files.")
