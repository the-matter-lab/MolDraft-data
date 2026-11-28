"""PyMOL renderer executed in the tool sandbox."""
import json
from pathlib import Path
import sys

from pymol import cmd


def render(xyz, output, azimuth, elevation, previous):
    cmd.reinitialize()
    cmd.set("auto_zoom", 0)
    cmd.load(xyz, "molecule", format="xyz")
    cmd.hide("all")
    cmd.show("sticks")
    cmd.show("spheres")
    cmd.set("sphere_scale", 0.25)
    cmd.set("stick_radius", 0.15)
    cmd.util.cbao()
    cmd.set("label_color", "cyan")
    cmd.set("label_size", 14)
    cmd.label("all", "'%s:%d' % (elem, ID-1)")
    if previous:
        cmd.set_view(previous)
    else:
        cmd.orient()
    cmd.turn("x", elevation)
    cmd.turn("y", azimuth)
    cmd.zoom()
    cmd.ray(1000, 1000)
    cmd.png(str(Path(output) / "view.png"))
    (Path(output) / "camera.json").write_text(json.dumps(cmd.get_view()))


if __name__ == "__main__":
    render(*json.loads(sys.argv[1]))
