"""The four tools exposed to the MolDraft model."""
from __future__ import annotations

import base64
from dataclasses import dataclass
from io import BytesIO
import json
from pathlib import Path
import shutil
import tempfile
from typing import Literal

from PIL import Image, ImageDraw, ImageFont
from pydantic import BaseModel, ConfigDict, Field

from .sandbox import Sandbox


class Arguments(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)


class Bash(Arguments):
    command: str = Field(description="Shell command executed in work dir directory")


class Png(Arguments):
    png_file_relative_path: str = Field(description="The relative path to the PNG file the agent wants to view.")


class View(Arguments):
    xyz_file_relative_path: str = Field(description="Path to XYZ file")
    left_right_deg: float = Field(description="Degrees to rotate Left/Right (Azimuth). Positive is Right.")
    up_down_deg: float = Field(description="Degrees to rotate Up/Down (Elevation). Positive is Down")
    reset_view: bool = Field(False, description="Set True to reset camera to default.")


class Constraint(Arguments):
    atoms: list[int] = Field(description="Atom indices (0-based).")
    value: float = Field(description="Target distance in Angstroms or angle in degrees.")


class Xtb(Arguments):
    input_xyz: str = Field(description="Relative path to the source XYZ structure file.")
    output_xyz: str = Field(description="Relative path where the optimized XYZ file will be saved.")
    gfn_method: Literal["gfn0", "gfn1", "gfn2", "gfnff"] = "gfn2"
    ncores: int = Field(4, ge=1)
    charge: int | None = Field(None, description="Total molecular charge (default: neutral).")
    uhf: int | None = Field(None, ge=0, description="Number of unpaired electrons (default: singlet).")
    force_constant: float | None = Field(None, gt=0, description="Global constraint force constant; start with 0.5 to 1.")
    distance_constraints: list[Constraint] | None = None
    angle_constraints: list[Constraint] | None = None
    dihedral_constraints: list[Constraint] | None = None


SCHEMAS = {
    "view_molecule": (View, "Rotates the molecule relative to the current view. Always shows the full molecule, resetting any previous zoom. The rotation is relative to the last view unless reset_view is true."),
    "constraint_xtb": (Xtb, "Run an xTB geometry optimisation with specified geometric constraints. Returns the execution status and output paths. Set the force constant when applying constraints."),
    "view_png_file": (Png, "Return the specified PNG image in a model-friendly format. Call this tool whenever you want to look at a PNG."),
    "bash_kernel": (Bash, "Run a shell command in the work dir. (pre cd workdir already)"),
}
PROFILES = {
    "four-tools": tuple(SCHEMAS),
    "png-bash": ("view_png_file", "bash_kernel"),
}


@dataclass
class ToolResult:
    text: str
    png: bytes | None = None

    @property
    def base64(self):
        return base64.b64encode(self.png).decode("ascii")


def image_result(path: Path, camera=None):
    with Image.open(path, formats=["PNG"]) as source:
        source.load()
        image = source.copy()
    if max(image.size) > 2000:
        image.thumbnail((2000, 2000), Image.Resampling.LANCZOS)
    if camera:
        image = camera_overlay(image, camera)
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return ToolResult("Image returned.", buffer.getvalue())


def camera_overlay(image, matrix):
    image = image.convert("RGBA")
    layer = Image.new("RGBA", image.size)
    draw = ImageDraw.Draw(layer)
    x, y = 65, image.height - 65
    draw.ellipse((x - 50, y - 50, x + 50, y + 50), fill=(0, 0, 0, 140))
    axes = zip("XYZ", ("#ff5050", "#50ff50", "#6464ff"), (matrix[:3], matrix[3:6], matrix[6:9]))
    for label, color, (dx, dy, _) in sorted(axes, key=lambda axis: axis[2][2]):
        end_x, end_y = x + dx * 35, y - dy * 35
        draw.line((x, y, end_x, end_y), fill=color, width=4)
        draw.ellipse((end_x - 7, end_y - 7, end_x + 7, end_y + 7), fill=color, outline="white")
        draw.text((end_x - 3, end_y - 4), label, font=ImageFont.load_default(), fill="black")
    return Image.alpha_composite(image, layer).convert("RGB")


def case_path(root: Path, relative: str, *, existing=False):
    path = Path(relative)
    if path.is_absolute():
        raise ValueError("Provide a relative path inside the working directory.")
    resolved = (root / path).resolve()
    if resolved == root or not resolved.is_relative_to(root):
        raise ValueError("Path is outside the working directory.")
    if existing and not resolved.is_file():
        raise ValueError(f"File not found or not a regular file: {relative}")
    return resolved


class Tools:
    def __init__(self, work: Path, profile: str, xtb_threads: int):
        self.sandbox = Sandbox(work)
        self.work = self.sandbox.work
        self.profile = PROFILES[profile]
        self.xtb_threads = xtb_threads
        self.views = {}

    def definitions(self):
        for name in self.profile:
            model, description = SCHEMAS[name]
            yield {"name": name, "description": description, "parameters": model.model_json_schema()}

    def call(self, name, values):
        try:
            if name not in self.profile:
                raise ValueError(f"Tool is not enabled: {name}")
            arguments = SCHEMAS[name][0].model_validate(values)
            return getattr(self, name)(arguments)
        except (ValueError, OSError, RuntimeError, Image.DecompressionBombError) as exc:
            return ToolResult(f"Error in {name}: {exc}")

    def bash_kernel(self, arguments):
        status, output = self.sandbox.run(["/bin/bash", "-c", arguments.command])
        if status and not output:
            output = f"Command exited with status {status}."
        if len(output) > 100_000:
            import tiktoken

            encoder = tiktoken.get_encoding("cl100k_base")
            tokens = encoder.encode_ordinary(output)
            if len(tokens) > 50_000:
                output = (encoder.decode(tokens[:25_000])
                          + f"\n\n[... OMITTED ~{len(tokens) - 50_000} TOKENS ...]\n\n"
                          + encoder.decode(tokens[-25_000:]))
        return ToolResult(output)

    def view_png_file(self, arguments):
        path = case_path(self.work, arguments.png_file_relative_path, existing=True)
        return image_result(path)

    def view_molecule(self, arguments):
        path = case_path(self.work, arguments.xyz_file_relative_path, existing=True)
        path_in_sandbox = Path("/work") / path.relative_to(self.work)
        previous = None if arguments.reset_view else self.views.get(path)
        with tempfile.TemporaryDirectory(prefix=".view-", dir=self.work) as temp:
            output = Path(temp)
            params = [str(path_in_sandbox), f"/work/{output.name}", arguments.left_right_deg,
                      arguments.up_down_deg, previous]
            render_code = Path(__file__).with_name("render.py").read_text()
            status, log = self.sandbox.run(
                [str(self.sandbox.python), "-I", "-c", render_code, json.dumps(params)]
            )
            if status:
                raise RuntimeError(log[-2000:])
            camera = json.loads((output / "camera.json").read_text())
            self.views[path] = camera
            return image_result(output / "view.png", camera)

    def constraint_xtb(self, arguments):
        source = case_path(self.work, arguments.input_xyz, existing=True)
        output = case_path(self.work, arguments.output_xyz)
        if source.suffix.lower() != ".xyz" or output.suffix.lower() != ".xyz":
            raise ValueError("Use .xyz for both structure paths.")
        log_path = case_path(self.work, str(output.relative_to(self.work).with_suffix(".log")))
        if output == log_path:
            raise ValueError("Output and log must be separate files.")
        with tempfile.TemporaryDirectory(prefix=".xtb-", dir=self.work) as folder:
            calc = Path(folder)
            shutil.copyfile(source, calc / "input.xyz")
            method = ["--gfnff"] if arguments.gfn_method == "gfnff" else ["--gfn", arguments.gfn_method[-1]]
            command = ["xtb", "input.xyz", "--opt", *method, "-P", str(min(arguments.ncores, self.xtb_threads))]
            if arguments.charge is not None:
                command += ["--chrg", str(arguments.charge)]
            if arguments.uhf is not None:
                command += ["--uhf", str(arguments.uhf)]
            lines = []
            if arguments.force_constant is not None:
                lines.append(f"   force constant={arguments.force_constant:g}")
            with (calc / "input.xyz").open() as xyz:
                atom_count = int(xyz.readline())
            if atom_count <= 0:
                raise ValueError("An XYZ file must contain at least one atom.")
            for kind, count in (("distance", 2), ("angle", 3), ("dihedral", 4)):
                for item in getattr(arguments, f"{kind}_constraints") or []:
                    if len(item.atoms) != count or any(i < 0 or i >= atom_count for i in item.atoms):
                        raise ValueError(f"{kind} requires {count} valid zero-based atom indices.")
                    indices = ", ".join(str(i + 1) for i in item.atoms)
                    lines.append(f"   {kind}: {indices}, {item.value:.10g}")
            if lines:
                (calc / "constraints.inp").write_text("\n".join(["$constrain", *lines, "$end", ""]))
                command += ["--input", "constraints.inp"]
            status, log = self.sandbox.run(command, cwd=calc, timeout=600)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            log_path.write_text(log)
            optimized = calc / "xtbopt.xyz"
            has_output = optimized.is_file()
            if has_output:
                output.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(optimized, output)
            elif not status:
                status = 1
        return ToolResult(json.dumps({
            "return_code": status,
            "output_xyz": arguments.output_xyz if has_output else None,
            "log_path": log_path.relative_to(self.work).as_posix(),
            "error_msg": log[-2000:] if status else None,
        }))
