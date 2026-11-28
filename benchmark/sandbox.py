"""Run each tool command in a separate Linux filesystem and network namespace."""
from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


_ENTER = r"""
root=$1 prefix=$2 work=$3 inside=$4
shift 4
mount -t tmpfs -o nosuid,nodev tmpfs "$root"
for path in /usr /bin /lib /lib64 /etc/ld.so.cache /etc/fonts "$prefix"; do
    [ -e "$path" ] || continue
    [ ! -e "$root$path" ] || continue
    if [ -d "$path" ]; then
        mkdir -p "$root$path"
    else
        mkdir -p "$(dirname "$root$path")"
        touch "$root$path"
    fi
    mount --bind "$path" "$root$path"
    mount -o remount,bind,ro,nosuid,nodev "$root$path"
done
mkdir -p "$root"/{dev,proc,tmp,work}
for node in null zero random urandom; do
    touch "$root/dev/$node"
    mount --bind "/dev/$node" "$root/dev/$node"
done
mount -t proc -o nosuid,nodev,noexec proc "$root/proc"
mount --bind "$work" "$root/work"
mount -o remount,bind,nosuid,nodev "$root/work"
exec /usr/sbin/chroot "$root" /usr/bin/setpriv \
    --bounding-set=-all --inh-caps=-all --ambient-caps=-all --no-new-privs \
    /usr/bin/env -i HOME=/work LANG=C.UTF-8 PATH="$prefix/bin:/usr/bin:/bin" \
    OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 LIBGL_ALWAYS_SOFTWARE=1 \
    /bin/bash -eu -c 'cd -- "$1"; shift; exec "$@"' bash "$inside" "$@"
"""


class Sandbox:
    def __init__(self, work: Path):
        self.work = work.resolve()
        self.prefix = Path(sys.prefix).resolve()
        self.python = self.prefix / "bin/python"
        self.binary = shutil.which("unshare")
        if not self.binary:
            raise RuntimeError("Install Linux util-linux and enable unprivileged user namespaces.")
        if self.prefix in self.work.parents or self.prefix == self.work:
            raise ValueError("Keep run data outside the Python environment.")

    def run(self, argv: list[str], *, cwd: Path | None = None, timeout=60, output_limit=1_000_000):
        inside = Path("/work") / (cwd or self.work).resolve().relative_to(self.work)
        # Use a file for subprocess output so a verbose tool cannot exhaust
        # the runner's RAM. Keep only the beginning and end of large outputs.
        with tempfile.TemporaryDirectory(prefix="moldraft-root-") as root, tempfile.TemporaryFile() as output:
            command = [
                self.binary, "--user", "--map-root-user", "--mount", "--propagation", "private",
                "--net", "--pid", "--ipc", "--uts", "--fork", "--kill-child",
                "/bin/bash", "-eu", "-c", _ENTER, "sandbox", root, str(self.prefix),
                str(self.work), str(inside), *argv,
            ]
            try:
                process = subprocess.run(
                    command, stdin=subprocess.DEVNULL, stdout=output,
                    stderr=subprocess.STDOUT, timeout=timeout, check=False,
                    start_new_session=True,
                )
            except subprocess.TimeoutExpired:
                return 124, "[TIMEOUT]"
            size = output.tell()
            output.seek(0)
            if size > output_limit:
                head = output.read(output_limit // 2)
                output.seek(-output_limit // 2, os.SEEK_END)
                data = head + b"\n[... output truncated ...]\n" + output.read()
            else:
                data = output.read()
        return process.returncode, data.decode("utf-8", errors="replace")


def check_sandbox(*, scientific_tools=False):
    with tempfile.TemporaryDirectory(prefix="moldraft-check-") as folder:
        root = Path(folder)
        work = root / "case"
        work.mkdir()
        secret = root / "host-only"
        secret.write_text("host only")
        sandbox = Sandbox(work)
        code = """
import os, pathlib, socket, sys
assert not pathlib.Path(sys.argv[1]).exists(), "host filesystem visible"
assert os.getcwd() == "/work"
assert not any(k.endswith("_API_KEY") for k in os.environ)
assert {name for _, name in socket.if_nameindex()} == {"lo"}, "host network visible"
assert os.getpid() == 1, "no private PID namespace"
pathlib.Path("probe").write_text("ok")
"""
        status, output = sandbox.run([str(sandbox.python), "-I", "-c", code, str(secret)])
        if status or not (work / "probe").is_file():
            raise RuntimeError(f"Sandbox check failed: {output.strip()}")
        if scientific_tools:
            code = (
                "from rdkit import Chem\n"
                "from pymol import cmd\n"
                "import ase, shutil\n"
                "assert all(shutil.which(name) for name in ('xtb', 'obabel'))"
            )
            status, output = sandbox.run([str(sandbox.python), "-I", "-c", code])
            if status:
                raise RuntimeError(f"Scientific tools are unavailable in the sandbox: {output.strip()}")
