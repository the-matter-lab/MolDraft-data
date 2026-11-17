#!/usr/bin/env python3
"""Pre-rendered SVG scatter charts for the MolDraft site (stdlib only, pure functions).

Two variants, both "success rate vs x" with a log10 x axis:
    cost    x = cost_usd.per_task_mean   (USD per molecule attempted)
    tokens  x = tokens.total     (input incl. cached reads + output, whole run)

The look follows tbench.ai's PARETO view: a 960x580 canvas, squares for points
(frontier members larger and in the brand green), a step line through the Pareto
frontier with the dominated region lightly shaded, 14px labels "Model (effort)",
hairline grid.  Inline SVGs use CSS custom properties so one SVG serves both
themes; `literal=True` substitutes light-theme hex values for standalone files.
"""
from __future__ import annotations

import math
from html import escape

W, H = 960, 580
ML, MT, MR, MB = 84, 20, 28, 52
PX0, PX1 = ML, W - MR          # plot x range
PY0, PY1 = MT, H - MB          # plot y range (PY0 = top)

# Theme tokens used inside the SVG; the literal map is the light theme.
TOKENS = {
    "bg": "var(--background)", "fg": "var(--foreground)", "muted": "var(--muted-foreground)",
    "grid": "var(--border)", "brand": "var(--brand)", "brand_strong": "var(--brand-strong)",
}
LITERAL = {
    "bg": "#ffffff", "fg": "#09090b", "muted": "#71717b", "grid": "#e4e4e7",
    "brand": "#009652", "brand_strong": "#016846",
}
FONT = "'Google Sans Code', ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
CHAR_W = 0.6                    # Google Sans Code advance per glyph, in em

VARIANTS = {
    "cost": dict(
        title="Success rate vs cost/molecule",
        x_label="COST/MOLECULE (USD, LOG SCALE)",
        footer="Success rate on 300 molecules against the mean cost per molecule (USD at list prices; "
               "total run cost divided by all 300 molecules attempted). "
               "The step line is the Pareto frontier: no model above it costs less.",
        getter=lambda e: (e.get("cost_usd") or {}).get("per_task_mean"),
        fmt=lambda v: fmt_cost(v),
    ),
    "tokens": dict(
        title="Success rate vs tokens",
        x_label="TOTAL TOKENS OF THE RUN (INPUT + OUTPUT, LOG SCALE)",
        footer="Success rate on 300 molecules against the total tokens of each run (input incl. cached reads, "
               "plus output). The step line is the Pareto frontier: no model above it uses fewer tokens.",
        getter=lambda e: (e.get("tokens") or {}).get("total"),
        fmt=lambda v: fmt_tokens(v),
    ),
}


# ----------------------------------------------------------------------------- scales
def _nice_floor(v: float) -> float:
    """Largest 1/2/5 x 10^n that is <= v."""
    e = math.floor(math.log10(v))
    for m in (5, 2, 1):
        c = m * 10 ** e
        if c <= v * (1 + 1e-12):
            return c
    return 10 ** e


def _nice_ceil(v: float) -> float:
    e = math.floor(math.log10(v))
    for m in (1, 2, 5, 10):
        c = m * 10 ** e
        if c >= v * (1 - 1e-12):
            return c
    return 10 ** (e + 1)


def log_domain(values: list[float]) -> tuple[float, float]:
    vals = [v for v in values if v is not None and v > 0]
    lo, hi = min(vals) / 1.1, max(vals) * 1.1
    return _nice_floor(lo), _nice_ceil(hi)


def log_ticks(lo: float, hi: float) -> list[float]:
    """1-2-5 ticks inside [lo, hi] when there are at most 10, otherwise decades only."""
    ticks = []
    e = math.floor(math.log10(lo))
    while 10 ** e <= hi * (1 + 1e-9):
        for m in (1, 2, 5):
            t = m * 10 ** e
            if lo * (1 - 1e-9) <= t <= hi * (1 + 1e-9):
                ticks.append(t)
        e += 1
    if len(ticks) > 10:
        ticks = [t for t in ticks if abs(math.log10(t) - round(math.log10(t))) < 1e-9]
    return ticks


def is_decade(v: float) -> bool:
    return abs(math.log10(v) - round(math.log10(v))) < 1e-9


def fmt_cost(v: float) -> str:
    if v >= 1000:
        s = f"{v / 1000:.1f}".rstrip("0").rstrip(".")
        return f"${s}k"
    if v >= 1:
        return f"${v:.0f}" if abs(v - round(v)) < 1e-9 else f"${v:.2f}".rstrip("0").rstrip(".")
    return "$" + f"{v:.4f}".rstrip("0").rstrip(".")


def fmt_tokens(v: float) -> str:
    for unit, div in (("B", 1e9), ("M", 1e6), ("k", 1e3)):
        if v >= div:
            s = f"{v / div:.2f}".rstrip("0").rstrip(".")
            return f"{s}{unit}"
    return f"{v:.0f}"


def px(x: float, lo: float, hi: float) -> float:
    return PX0 + (PX1 - PX0) * (math.log10(x) - math.log10(lo)) / (math.log10(hi) - math.log10(lo))


def py(y: float) -> float:
    return PY1 - (PY1 - PY0) * y / 100.0


# ----------------------------------------------------------------------------- frontier
def frontier(points: list[dict]) -> list[dict]:
    """Pareto frontier for 'higher y at lower x is better'.

    Finite points only; for equal x keep the higher y; sort by x ascending; always keep
    the cheapest point, then keep a point iff its y is strictly above the running best.
    """
    best_at_x: dict[float, dict] = {}
    for p in points:
        if p["x"] is None or p["y"] is None or not (p["x"] > 0):
            continue
        if p["x"] not in best_at_x or p["y"] > best_at_x[p["x"]]["y"]:
            best_at_x[p["x"]] = p
    out, best = [], -math.inf
    for p in sorted(best_at_x.values(), key=lambda q: q["x"]):
        if p["y"] > best:
            out.append(p)
            best = p["y"]
    return out


# ----------------------------------------------------------------------------- labels
def _label_text(e: dict) -> tuple[str, str]:
    name = e.get("display_name") or e.get("model_id") or "—"
    effort = e.get("effort")
    return name, (f" ({effort})" if effort else "")


def frontier_segments(points: list[dict]) -> list[tuple[float, float, float, float]]:
    """Axis-aligned boxes (2px half-width) covering the step line, used as label obstacles."""
    front = sorted((p for p in points if p.get("frontier")), key=lambda p: p["x"])
    if not front:
        return []
    segs = []
    def box(x1, y1, x2, y2):
        return (min(x1, x2) - 2, min(y1, y2) - 2, max(x1, x2) + 2, max(y1, y2) + 2)
    segs.append(box(front[0]["px"], PY1, front[0]["px"], front[0]["py"]))
    for a, b in zip(front, front[1:]):
        segs.append(box(a["px"], a["py"], b["px"], a["py"]))
        segs.append(box(b["px"], a["py"], b["px"], b["py"]))
    segs.append(box(front[-1]["px"], front[-1]["py"], PX1, front[-1]["py"]))
    return segs


def place_labels(points: list[dict], font_px: int = 14, gap: float = 9.0) -> None:
    """Deterministic label placement: right, left, above, below; least-overlap fallback.

    Each point gets label_x/label_y/anchor plus a text box used for collision checks.
    Widths are exact because the site font is monospace (0.6 em per glyph).
    Obstacles: other points, already placed labels, the frontier step line, the plot edge.
    """
    occupied: list[tuple[float, float, float, float]] = []
    discs = [(p["px"] - 7, p["py"] - 7, p["px"] + 7, p["py"] + 7) for p in points]
    lines = frontier_segments(points)

    def box(p, cand):
        w = (len(p["label"]) + len(p["label2"])) * CHAR_W * font_px
        h = font_px
        x, y = p["px"], p["py"]
        if cand == "right":
            return (x + gap, y - h / 2, x + gap + w, y + h / 2), x + gap, y, "start"
        if cand == "left":
            return (x - gap - w, y - h / 2, x - gap, y + h / 2), x - gap, y, "end"
        if cand == "above":
            return (x - w / 2, y - gap - h, x + w / 2, y - gap), x, y - gap - h / 2, "middle"
        return (x - w / 2, y + gap, x + w / 2, y + gap + h), x, y + gap + h / 2, "middle"

    def overlap(a, b):
        return not (a[2] < b[0] or b[2] < a[0] or a[3] < b[1] or b[3] < a[1])

    def cost(b, own):
        c = 0
        c += sum(1 for o in occupied if overlap(b, o)) * 10
        c += sum(1 for i, d in enumerate(discs) if i != own and overlap(b, d)) * 5
        c += sum(1 for l in lines if overlap(b, l)) * 3
        if b[0] < PX0 or b[2] > PX1 + MR - 4 or b[1] < PY0 or b[3] > PY1:
            c += 20
        return c

    # most constrained first: points with the most neighbours within 60px
    order = sorted(range(len(points)), key=lambda i: -sum(
        1 for j in range(len(points)) if j != i and abs(points[j]["px"] - points[i]["px"]) < 60
        and abs(points[j]["py"] - points[i]["py"]) < 60))
    for i in order:
        p = points[i]
        best = None
        for cand in ("right", "left", "above", "below"):
            b, lx, ly, anchor = box(p, cand)
            c = cost(b, i)
            if best is None or c < best[0]:
                best = (c, b, lx, ly, anchor)
            if c == 0:
                break
        _, b, lx, ly, anchor = best
        p.update(label_x=round(lx, 1), label_y=round(ly, 1), anchor=anchor, box=b)
        occupied.append(b)


# ----------------------------------------------------------------------------- rendering
def chart_points(entries: list[dict], variant: str) -> list[dict]:
    g = VARIANTS[variant]["getter"]
    pts = []
    for e in entries:
        x = g(e)
        y = e.get("success_rate")
        if x is None or y is None or not (x > 0):
            continue
        name, eff = _label_text(e)
        pts.append(dict(id=e["model_id"], x=float(x), y=float(y), label=name, label2=eff,
                        org=e.get("organization"), effort=e.get("effort")))
    return pts


def layout(entries: list[dict], variant: str) -> dict:
    pts = chart_points(entries, variant)
    lo, hi = log_domain([p["x"] for p in pts])
    for p in pts:
        p["px"] = round(px(p["x"], lo, hi), 1)
        p["py"] = round(py(p["y"]), 1)
    front = frontier(pts)
    front_ids = {p["id"] for p in front}
    for p in pts:
        p["frontier"] = p["id"] in front_ids
    place_labels(pts)
    return dict(variant=variant, lo=lo, hi=hi, ticks=log_ticks(lo, hi), points=pts,
                frontier=[p["id"] for p in front])


def render_svg(lay: dict, literal: bool = False, title_id: str | None = None) -> str:
    t = LITERAL if literal else TOKENS
    v = VARIANTS[lay["variant"]]
    fmt = v["fmt"]
    tid = title_id or f"chart-{lay['variant']}-title"
    o = []
    o.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
             f'role="img" aria-labelledby="{tid}" class="chart-svg" data-variant="{lay["variant"]}" '
             f'font-family="{escape(FONT)}">')
    o.append(f'<title id="{tid}">{escape(v["title"])}</title>')
    o.append(f'<desc>{escape(v["x_label"].capitalize())}; y axis success rate in percent; '
             f'{len(lay["points"])} models; Pareto frontier: '
             f'{", ".join(lay["frontier"])}.</desc>')
    if literal:
        o.append(f'<rect x="0" y="0" width="{W}" height="{H}" fill="{t["bg"]}"/>')

    # grid: y ticks every 20 and x decades, hairline solid
    o.append('<g class="grid" stroke-width="1">')
    for yv in range(0, 101, 20):
        yy = py(yv)
        o.append(f'<line x1="{PX0}" x2="{PX1}" y1="{yy:.1f}" y2="{yy:.1f}" stroke="{t["grid"]}"/>')
    for tk in lay["ticks"]:
        if is_decade(tk):
            xx = px(tk, lay["lo"], lay["hi"])
            o.append(f'<line x1="{xx:.1f}" x2="{xx:.1f}" y1="{PY0}" y2="{PY1}" stroke="{t["grid"]}"/>')
    o.append('</g>')

    # dominated-region shade + frontier step line
    front = [p for p in lay["points"] if p["frontier"]]
    front.sort(key=lambda p: p["x"])
    if len(front) >= 1:
        path = [f'M{front[0]["px"]:.1f},{PY1}', f'L{front[0]["px"]:.1f},{front[0]["py"]:.1f}']
        for a, b in zip(front, front[1:]):
            path.append(f'L{b["px"]:.1f},{a["py"]:.1f}')
            path.append(f'L{b["px"]:.1f},{b["py"]:.1f}')
        path.append(f'L{PX1},{front[-1]["py"]:.1f}')
        shade = " ".join(path) + f' L{PX1},{PY1} Z'
        o.append(f'<path class="shade" d="{shade}" fill="{t["fg"]}" fill-opacity="0.05" stroke="none"/>')
        o.append(f'<path class="frontier" d="{" ".join(path)}" fill="none" stroke="{t["brand"]}" '
                 f'stroke-width="1.5" stroke-opacity="0.9" stroke-linejoin="round"/>')

    # axes
    o.append(f'<g class="axes" stroke="{t["muted"]}" stroke-opacity="0.4" stroke-width="1">')
    o.append(f'<line x1="{PX0}" x2="{PX1}" y1="{PY1}" y2="{PY1}"/>')
    o.append(f'<line x1="{PX0}" x2="{PX0}" y1="{PY0}" y2="{PY1}"/>')
    o.append('</g>')
    # tick labels
    o.append(f'<g class="ticks" fill="{t["muted"]}" font-size="12">')
    for yv in range(0, 101, 20):
        o.append(f'<text x="{PX0 - 10}" y="{py(yv):.1f}" text-anchor="end" dominant-baseline="middle">{yv}%</text>')
    for tk in lay["ticks"]:
        xx = px(tk, lay["lo"], lay["hi"])
        o.append(f'<text x="{xx:.1f}" y="{PY1 + 18}" text-anchor="middle">{escape(fmt(tk))}</text>')
    o.append('</g>')
    # axis titles
    o.append(f'<g class="axis-titles" fill="{t["fg"]}" font-size="12" letter-spacing="1.5">')
    o.append(f'<text x="{(PX0 + PX1) / 2:.1f}" y="{H - 10}" text-anchor="middle">{escape(v["x_label"])}</text>')
    o.append(f'<text transform="translate(18,{(PY0 + PY1) / 2:.1f}) rotate(-90)" text-anchor="middle">SUCCESS RATE (%)</text>')
    o.append('</g>')

    # points (squares; frontier members larger and in brand green) with a surface ring
    o.append('<g class="points">')
    for i, p in enumerate(lay["points"]):
        s = 10 if p["frontier"] else 8
        fill = t["brand_strong"] if p["frontier"] else t["muted"]
        o.append(f'<rect class="pt{" pt-frontier" if p["frontier"] else ""}" data-i="{i}" data-id="{escape(p["id"])}" '
                 f'x="{p["px"] - s / 2 - 1:.1f}" y="{p["py"] - s / 2 - 1:.1f}" width="{s + 2}" height="{s + 2}" '
                 f'fill="{fill}" stroke="{t["bg"]}" stroke-width="2" tabindex="0">'
                 f'<title>{escape(p["label"] + p["label2"])}: {p["y"]:.1f}%, {escape(fmt(p["x"]))}</title></rect>')
    o.append('</g>')
    # labels: model in foreground, effort muted
    o.append(f'<g class="labels" font-size="14" pointer-events="none">')
    for p in lay["points"]:
        pos = f'x="{p["label_x"]}" y="{p["label_y"]}" text-anchor="{p["anchor"]}" dominant-baseline="middle"'
        text = f'{escape(p["label"])}{escape(p["label2"])}'
        # halo first (stroke only), then the coloured text on top
        o.append(f'<text {pos} fill="none" stroke="{t["bg"]}" stroke-width="3" stroke-linejoin="round" '
                 f'stroke-opacity="0.9">{text}</text>')
        o.append(f'<text {pos} fill="{t["fg"]}">{escape(p["label"])}'
                 f'<tspan fill="{t["muted"]}">{escape(p["label2"])}</tspan></text>')
    o.append('</g>')
    o.append('</svg>')
    return "\n".join(o)


def bin_series(ab: dict, entries: list[dict], mode: str, orgs: dict) -> list[dict]:
    """Series to draw for a mode: pooled, one model, or the top-5 models by overall success rate."""
    bins = ab["bins"]
    if mode == "all":
        return [dict(key="all", label="All models", color="brand",
                     rates=[b["pooled"]["rate"] for b in bins],
                     counts=[(b["pooled"]["passed"], b["pooled"]["total"]) for b in bins])]
    by_id = {e["model_id"]: e for e in entries}
    if mode == "top5":
        ranked = sorted((e for e in entries if e.get("success_rate") is not None),
                        key=lambda e: (-e["success_rate"], e.get("rank", 99)))[:5]
        used: dict[str, int] = {}
        out = []
        for e in ranked:
            org = e.get("organization") or "Other"
            pal = (orgs.get(org) or {}).get("palette") or ["#71717b", "#9f9fa9"]
            i = used.get(org, 0)
            used[org] = i + 1
            m = e["model_id"]
            out.append(dict(key=m, label=e["display_name"], color=pal[i % len(pal)],
                            rates=[b["models"].get(m, {}).get("rate") for b in bins],
                            counts=[(b["models"].get(m, {}).get("passed", 0), b["models"].get(m, {}).get("n", 0)) for b in bins]))
        return out
    e = by_id.get(mode)
    if not e:
        return []
    return [dict(key=mode, label=e["display_name"], color="brand",
                 rates=[b["models"].get(mode, {}).get("rate") for b in bins],
                 counts=[(b["models"].get(mode, {}).get("passed", 0), b["models"].get(mode, {}).get("n", 0)) for b in bins])]


def render_bins_svg(ab: dict, literal: bool = False, title_id: str = "chart-atoms-title",
                    series: list[dict] | None = None, mode: str = "all") -> str:
    """Bar chart of success rate per atom-count bin: one series (pooled or one model) or grouped bars (top 5)."""
    t = LITERAL if literal else TOKENS
    bins = ab["bins"]
    if series is None:
        series = bin_series(ab, [], "all", {})
    o = []
    o.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
             f'role="img" aria-labelledby="{title_id}" class="chart-svg" data-variant="atoms" data-mode="{escape(mode)}" '
             f'font-family="{escape(FONT)}">')
    who = ", ".join(s["label"] for s in series)
    o.append(f'<title id="{title_id}">Success rate vs molecule size: {escape(who)}</title>')
    o.append(f'<desc>Success rate per atom-count bin for {escape(who)}.</desc>')
    if literal:
        o.append(f'<rect x="0" y="0" width="{W}" height="{H}" fill="{t["bg"]}"/>')
    o.append('<g class="grid" stroke-width="1">')
    for yv in range(0, 101, 20):
        yy = py(yv)
        o.append(f'<line x1="{PX0}" x2="{PX1}" y1="{yy:.1f}" y2="{yy:.1f}" stroke="{t["grid"]}"/>')
    o.append('</g>')
    o.append(f'<g class="axes" stroke="{t["muted"]}" stroke-opacity="0.4" stroke-width="1">')
    o.append(f'<line x1="{PX0}" x2="{PX1}" y1="{PY1}" y2="{PY1}"/>')
    o.append(f'<line x1="{PX0}" x2="{PX0}" y1="{PY0}" y2="{PY1}"/>')
    o.append('</g>')
    o.append(f'<g class="ticks" fill="{t["muted"]}" font-size="12">')
    for yv in range(0, 101, 20):
        o.append(f'<text x="{PX0 - 10}" y="{py(yv):.1f}" text-anchor="end" dominant-baseline="middle">{yv}%</text>')
    band = (PX1 - PX0) / len(bins)
    for i, bn in enumerate(bins):
        cx = PX0 + band * (i + 0.5)
        o.append(f'<text x="{cx:.1f}" y="{PY1 + 18}" text-anchor="middle">{escape(bn["label"])} atoms</text>')
        o.append(f'<text x="{cx:.1f}" y="{PY1 + 34}" text-anchor="middle" font-size="11">n = {bn["n"]}</text>')
    o.append('</g>')
    o.append(f'<g class="axis-titles" fill="{t["fg"]}" font-size="12" letter-spacing="1.5">')
    o.append(f'<text x="{(PX0 + PX1) / 2:.1f}" y="{H - 1}" text-anchor="middle">MOLECULE SIZE (ATOMS, QUANTILE BINS)</text>')
    o.append(f'<text transform="translate(18,{(PY0 + PY1) / 2:.1f}) rotate(-90)" text-anchor="middle">SUCCESS RATE (%)</text>')
    o.append('</g>')
    k = len(series)
    bar_w, gap = (24, 0) if k == 1 else (22, 3)
    group_w = k * bar_w + (k - 1) * gap
    o.append('<g class="bars">')
    for i, bn in enumerate(bins):
        cx = PX0 + band * (i + 0.5)
        x0 = cx - group_w / 2
        for j, s in enumerate(series):
            rate = s["rates"][i]
            if rate is None:
                continue
            fill = t["brand"] if s["color"] == "brand" else s["color"]
            top = py(rate)
            x = x0 + j * (bar_w + gap)
            passed, total = s["counts"][i]
            o.append(f'<rect class="bin-bar" data-bin="{i}" data-series="{escape(s["key"])}" x="{x:.1f}" y="{top:.1f}" '
                     f'width="{bar_w}" height="{PY1 - top:.1f}" fill="{fill}" tabindex="0">'
                     f'<title>{escape(s["label"])}, {escape(bn["label"])} atoms: {rate:.1f}% ({passed}/{total})</title></rect>')
            if k == 1:
                o.append(f'<text x="{cx:.1f}" y="{top - 8:.1f}" text-anchor="middle" font-size="13" fill="{t["fg"]}">{rate:.1f}%</text>')
    o.append('</g>')
    if k > 1:  # legend inside the plot, top-left
        o.append(f'<g class="legend" font-size="12" fill="{t["fg"]}">')
        for j, s in enumerate(series):
            yy = PY0 + 14 + j * 18
            o.append(f'<rect x="{PX0 + 12}" y="{yy - 6}" width="12" height="12" fill="{s["color"]}"/>')
            o.append(f'<text x="{PX0 + 30}" y="{yy}" dominant-baseline="middle">{escape(s["label"])}</text>')
        o.append('</g>')
    o.append('</svg>')
    return "\n".join(o)


def footnotes(entries: list[dict]) -> list[str]:
    notes = ["Costs use the recorded provider usage and price schedule, including applicable cache and long-context rates. "
             "Mean cost is the recorded total divided by all 300 attempts."]
    for e in entries:
        c = e.get("cost_usd") or {}
        name = e.get("display_name") or e["model_id"]
        if (e.get("sessions_without_usage") or 0) > 0:
            notes.append(f"{name}: {e['sessions_without_usage']} of {e.get('n', 300)} sessions returned no usage record; "
                         f"its tokens and cost are lower bounds.")
        if (e.get("tokens") or {}).get("cache_hit_pct") == 0:
            notes.append(f"{name}: no cached reads were reported, so its cost assumes uncached input.")
    efforts = {e.get("effort") for e in entries if e.get("effort")}
    if len(efforts) > 1:
        odd = [f"{e.get('display_name') or e['model_id']} ({e['effort']})" for e in entries
               if e.get("effort") != max(efforts, key=lambda x: sum(1 for q in entries if q.get("effort") == x))]
        if odd:
            notes.append("Reasoning effort differs: " + ", ".join(odd) + "; all others ran at high.")
    return notes


def charts_html(doc: dict) -> tuple[str, dict]:
    """Return (HTML for the two hidden chart views, metadata for leaderboard.json)."""
    entries = doc["entries"]
    html_parts, meta = [], {}
    for variant in ("cost", "tokens"):
        lay = layout(entries, variant)
        v = VARIANTS[variant]
        svg = render_svg(lay)
        notes = footnotes(entries)
        meta[variant] = dict(
            x_label=v["x_label"], domain=[lay["lo"], lay["hi"]], ticks=lay["ticks"],
            frontier=lay["frontier"],
            points={p["id"]: dict(x=p["x"], y=p["y"], px=p["px"], py=p["py"], frontier=p["frontier"],
                                  label_x=p["label_x"], label_y=p["label_y"], anchor=p["anchor"])
                    for p in lay["points"]},
        )
        html_parts.append(
            f'<div class="view" data-view="{variant}" hidden>\n'
            f'  <div class="card chart-card">\n'
            f'    <div class="chart-head"><span>{escape(v["title"])}</span></div>\n'
            f'    <div class="chart-body">\n{svg}\n    </div>\n'
            f'    <footer class="card-footer">{escape(v["footer"])}</footer>\n'
            f'    <ol class="chart-notes">' + "".join(f"<li>{escape(n)}</li>" for n in notes) + '</ol>\n'
            f'  </div>\n</div>')
    ab = doc.get("atom_bins")
    if ab and ab.get("bins"):
        orgs = doc.get("organizations") or {}
        modes = [("all", "All models"), ("top5", "Top 5")] + [(e["model_id"], e["display_name"]) for e in entries]
        svgs, chips = [], []
        for mode, label in modes:
            series = bin_series(ab, entries, mode, orgs)
            if not series:
                continue
            svgs.append(f'<div class="atoms-mode" data-mode="{escape(mode)}"{"" if mode == "all" else " hidden"}>\n'
                        + render_bins_svg(ab, series=series, mode=mode, title_id=f"chart-atoms-{mode}-title") + '\n</div>')
            chips.append(f'<button type="button" class="chip" data-mode="{escape(mode)}" '
                         f'aria-pressed="{"true" if mode == "all" else "false"}">{escape(label)}</button>')
        html_parts.append(
            '<div class="view" data-view="atoms" hidden>\n'
            '  <div class="card chart-card">\n'
            '    <div class="chart-head"><span>Success rate vs molecule size</span></div>\n'
            '    <div class="chart-body">\n' + "\n".join(svgs) + '\n    </div>\n'
            '    <div class="chip-row" role="group" aria-label="Model">' + "".join(chips) + '</div>\n'
            '    <footer class="card-footer">Success rate per atom-count bin (bins are quantiles of the 300 molecules). '
            'ALL MODELS pools every attempt in the bin; TOP 5 compares the five best models by overall success rate.</footer>\n'
            '  </div>\n</div>')
        meta["atoms"] = dict(n_bins=ab["n_bins"], labels=[b["label"] for b in ab["bins"]], modes=[m for m, _ in modes])
    return "\n".join(html_parts), meta


def check_charts(index_html: str, meta: dict) -> list[str]:
    """Structural checks used by build.py --check."""
    problems = []
    for variant, m in meta.items():
        if f'data-variant="{variant}"' not in index_html:
            problems.append(f"chart {variant}: inline SVG missing from index.html")
        if "frontier" not in m:
            continue
        if len(m["frontier"]) < 2:
            problems.append(f"chart {variant}: frontier has fewer than 2 points ({m['frontier']})")
        pts = m["points"]
        for pid, p in pts.items():
            if not (PX0 <= p["px"] <= PX1 and PY0 <= p["py"] <= PY1):
                problems.append(f"chart {variant}: {pid} plotted outside the plot rect")
    return problems
