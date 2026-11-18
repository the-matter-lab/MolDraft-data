#!/usr/bin/env python3
"""Render the verified homepage example without changing its atomic coordinates.

Optional asset rebuild: python -m pip install numpy Pillow
                       python website/render_demo.py
The cached single-point Wiberg bond orders are used only to draw sticks.
"""
from pathlib import Path
import csv
import hashlib
import json
import shutil

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "website/demo/source.json"
OUT = ROOT / "docs/assets/demo"
COLORS = {
    "C": "#90a4ad", "H": "#e9eded", "N": "#497fe0",
    "P": "#df9c3e", "Cl": "#44b861", "Ru": "#1eaa8c",
}
RADII = {"C": .30, "H": .18, "N": .32, "P": .40, "Cl": .40, "Ru": .52}
WIDTH, HEIGHT, SS, FRAMES = 640, 480, 2, 72


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inputs():
    source = json.loads(SOURCE.read_text())
    for kind, expected in source["sha256"].items():
        assert sha(ROOT / source[kind]) == expected, kind
    verdicts = json.loads((ROOT / source["verification"]).read_text())
    row = next(row for row in verdicts["rows"] if row["name"] == source["molecule"])
    assert row["verifier_version"] == "moldraft.stereochemistry/v18"
    assert row["overall_pass"] and not row["verifier_error"]
    assert all(row[key] for key in ("aam_pass", "stereo_pass", "geometry_pass"))
    assert row["answer_sha256"] == source["sha256"]["answer"]
    assert row["reference_sha256"] == source["sha256"]["reference"]
    with (ROOT / "data/index.csv").open() as handle:
        entry = next(entry for entry in csv.DictReader(handle) if entry["id"] == source["molecule"])
    assert source["image"] == "data/" + entry["image"]
    assert int(entry["total_atoms"]) == 102
    with np.load(ROOT / source["arrays"]) as arrays:
        elements = arrays["elements"].tolist()
        coords, orders = arrays["coordinates"].copy(), arrays["wbo"].copy()
    lines = (ROOT / source["answer"]).read_text().splitlines()
    atoms = [line.split() for line in lines[2:] if line.strip()]
    assert elements == [atom[0] for atom in atoms]
    assert np.allclose(coords, [[float(v) for v in atom[1:4]] for atom in atoms], atol=1e-10, rtol=0)
    assert elements.count("Ru") == 2 and len(elements) == 102
    bonds = [(i, j) for i in range(len(elements)) for j in range(i) if orders[i, j] >= .4]
    assert all(symbol in COLORS for symbol in elements)
    return source, elements, coords, bonds


def rotation(angle):
    c, s = np.cos(angle), np.sin(angle)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])


def render(elements, coords, bonds, scale):
    width, height = WIDTH * SS, HEIGHT * SS
    points = coords * scale + np.array([width / 2, height / 2, 0])
    points[:, 1] = height - points[:, 1]
    depth = np.full((height, width), -np.inf, dtype=np.float32)
    rgb = np.ones((height, width, 3), dtype=np.float32)
    light = np.array([-.45, -.55, 1.]); light /= np.linalg.norm(light)
    halfway = light + [0, 0, 1]; halfway /= np.linalg.norm(halfway)
    palette = {key: np.array([int(value[i:i + 2], 16) / 255 for i in (1, 3, 5)])
               for key, value in COLORS.items()}

    def paint(box, z, normals, inside, color):
        x0, y0, x1, y1 = box
        update = inside & (z > depth[y0:y1, x0:x1])
        diffuse = np.clip(normals @ light, 0, 1)
        gloss = np.clip(normals @ halfway, 0, 1) ** 50
        shaded = np.clip(color * (.32 + .68 * diffuse[..., None]) + .30 * gloss[..., None], 0, 1)
        depth[y0:y1, x0:x1][update] = z[update]
        rgb[y0:y1, x0:x1][update] = shaded[update]

    def box_for(x0, y0, x1, y1):
        return max(int(x0) - 1, 0), max(int(y0) - 1, 0), min(int(x1) + 2, width), min(int(y1) + 2, height)

    def sphere(point, radius, color):
        x, y, z = point
        box = x0, y0, x1, y1 = box_for(x - radius, y - radius, x + radius, y + radius)
        if x1 <= x0 or y1 <= y0: return
        ys, xs = np.mgrid[y0:y1, x0:x1]
        dx, dy = xs + .5 - x, ys + .5 - y
        squared = dx * dx + dy * dy
        dz = np.sqrt(np.clip(radius * radius - squared, 0, None))
        normals = np.stack([dx, dy, dz], -1) / radius
        paint(box, z + dz, normals, squared < radius * radius, color)

    def cylinder(start, end, radius, color):
        axis = end - start
        length = np.linalg.norm(axis)
        if length < 1e-8: return
        axis /= length
        qa = 1 - axis[2] ** 2
        if qa < 1e-8: return
        box = x0, y0, x1, y1 = box_for(min(start[0], end[0]) - radius,
                                     min(start[1], end[1]) - radius,
                                     max(start[0], end[0]) + radius,
                                     max(start[1], end[1]) + radius)
        if x1 <= x0 or y1 <= y0: return
        ys, xs = np.mgrid[y0:y1, x0:x1]
        dx, dy = xs + .5 - start[0], ys + .5 - start[1]
        projection = dx * axis[0] + dy * axis[1]
        qb = -2 * projection * axis[2]
        qc = dx * dx + dy * dy - projection * projection - radius * radius
        discriminant = qb * qb - 4 * qa * qc
        dz = (-qb + np.sqrt(np.clip(discriminant, 0, None))) / (2 * qa)
        t = projection + dz * axis[2]
        normals = (np.stack([dx, dy, dz], -1) - t[..., None] * axis) / radius
        inside = (discriminant > 0) & (t >= 0) & (t <= length)
        paint(box, start[2] + dz, normals, inside, color)

    for i, j in bonds:
        middle = (points[i] + points[j]) / 2
        cylinder(points[i], middle, .10 * scale, palette[elements[i]])
        cylinder(middle, points[j], .10 * scale, palette[elements[j]])
    for point, symbol in zip(points, elements):
        sphere(point, RADII[symbol] * scale, palette[symbol])
    return Image.fromarray((rgb * 255).astype(np.uint8)).resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)


def main():
    source, elements, coords, bonds = inputs()
    OUT.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT / source["image"], OUT / "coordination-input.png")
    heavy = np.array([symbol != "H" for symbol in elements])
    coords -= coords[heavy].mean(axis=0)
    _, _, axes = np.linalg.svd(coords[heavy], full_matrices=False)
    if np.linalg.det(axes) < 0: axes[-1] *= -1
    coords = coords @ axes.T
    tilt = .28
    elevation = np.array([[1, 0, 0], [0, np.cos(tilt), -np.sin(tilt)], [0, np.sin(tilt), np.cos(tilt)]])
    poses = [coords @ rotation(2 * np.pi * frame / FRAMES).T @ elevation.T for frame in range(FRAMES)]
    extent = np.max(np.abs(np.stack(poses)), axis=(0, 1)) + .85
    scale = min(WIDTH * SS / (2 * extent[0]), HEIGHT * SS / (2 * extent[1]))
    images = []
    for frame, pose in enumerate(poses):
        images.append(render(elements, pose, bonds, scale))
        if frame % 18 == 0: print(f"Rendered {frame + 1}/{FRAMES} frames", flush=True)
    images[0].save(OUT / "coordination-poster.png", optimize=True)
    sheet = Image.new("RGB", (WIDTH, HEIGHT * 8), "white")
    for i, frame in enumerate(images[::9]): sheet.paste(frame, (0, i * HEIGHT))
    palette = sheet.quantize(colors=256)
    frames = [frame.quantize(palette=palette, dither=Image.Dither.NONE) for frame in images]
    target = OUT / "coordination-rotation.gif"
    frames[0].save(target, save_all=True, append_images=frames[1:], duration=80,
                   loop=0, optimize=False, disposal=2)
    print(f"Wrote verified 102-atom demo, {len(bonds)} bonds, {target.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
