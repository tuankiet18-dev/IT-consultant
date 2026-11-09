"""Builds the page-1 system context SVG and writes it into context.html (between the two svg tags of page 1).
Hand-placed layout: edit the coordinates below and run `python make_context_svg.py`, then build_pdfs.js.
"""
import math
import re
from pathlib import Path

W, H = 1100, 600
CX, CY, R = 550, 292, 108
INK, BODY, BLUE, AMBER, GREY = "#0f172a", "#334155", "#1e3a8a", "#b45309", "#64748b"


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;")


def circle_point(deg):
    """Point on the circle; 0 deg = right, 90 deg = down."""
    a = math.radians(deg)
    return CX + R * math.cos(a), CY + R * math.sin(a)


out = [f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="System context diagram">']
out.append(
    "<defs>"
    + "".join(
        f'<marker id="{i}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0L10 5L0 10z" fill="{c}"/></marker>'
        for i, c in (("mb", BLUE), ("ma", AMBER), ("mg", GREY))
    )
    + "</defs>"
)


def box(x, y, w, h, title, sub, fill, stroke, dashed=False, extra=None):
    dash = ' stroke-dasharray="7 5"' if dashed else ""
    out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{fill}" stroke="{stroke}" stroke-width="2.2"{dash}/>')
    out.append(f'<text x="{x + w / 2}" y="{y + 31}" text-anchor="middle" font-size="17" font-weight="700" fill="{INK}">{esc(title)}</text>')
    out.append(f'<text x="{x + w / 2}" y="{y + 52}" text-anchor="middle" font-size="13" fill="#475569">{esc(sub)}</text>')
    if extra:
        out.append(extra)


def flow(points, color, marker, dashed=False):
    d = "M" + " L".join(f"{x:.0f} {y:.0f}" for x, y in points)
    dash = ' stroke-dasharray="8 6"' if dashed else ""
    out.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="2.6"{dash} marker-end="url(#{marker})"/>')


def badge(x, y, n, color):
    out.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="12" fill="{color}"/>')
    out.append(f'<text x="{x:.0f}" y="{y + 4.5:.0f}" text-anchor="middle" font-size="13" font-weight="700" fill="#fff">{n}</text>')


def label(x, y, lines, anchor="start", color=BODY, bold_first=False):
    for i, t in enumerate(lines):
        w = ' font-weight="600"' if bold_first and i == 0 else ""
        out.append(
            f'<text x="{x}" y="{y + i * 17}" text-anchor="{anchor}" font-size="14.5" fill="{color}"{w} '
            f'paint-order="stroke" stroke="#fff" stroke-width="5" stroke-linejoin="round">{esc(t)}</text>'
        )


# ---- entities ----------------------------------------------------------------
box(440, 14, 220, 76, "Planner", "single local user", "#e0e7ff", "#3730a3")
box(40, 170, 240, 84, "Input data files", "CSV files or one ZIP", "#fde8e8", "#9f1239")
box(40, 322, 240, 92, "Company A systems", "ERP · WMS · TMS", "#f1f5f9", GREY, dashed=True,
    extra=f'<rect x="92" y="384" width="136" height="22" rx="11" fill="#cbd5e1"/>'
          f'<text x="160" y="400" text-anchor="middle" font-size="12" font-weight="700" fill="#334155">NOT CONNECTED</text>')
box(40, 500, 240, 84, "Approved plan export", "ZIP of CSV and JSON files", "#fde8e8", "#9f1239")
box(830, 236, 230, 100, "Groq API", "external LLM service", "#fffbeb", AMBER,
    extra=f'<text x="945" y="312" text-anchor="middle" font-size="13" font-weight="700" fill="{AMBER}">optional, opt-in per request</text>')

# ---- flows (7 numbers match the register on page 2) ---------------------------
# 3: planner <-> system
flow([(512, 92), (512, 205)], BLUE, "mb")
flow([(588, 205), (588, 92)], BLUE, "mb")
badge(512, 148, 3, BLUE)
badge(588, 148, 3, BLUE)
label(496, 112, ["load, calculate, adjust,", "approve or reject"], "end")
label(604, 112, ["results, route ranking,", "explanation, audit trail"])
# 1: Company A -> input files (manual)
flow([(160, 320), (160, 258)], GREY, "mg", dashed=True)
badge(160, 289, 1, GREY)
label(180, 283, ["orders, rates, supply,", "capacities, exported by hand"])
# 2: input files -> system
p = circle_point(190)
flow([(282, 212), p], BLUE, "mb")
badge((282 + p[0]) / 2, (212 + p[1]) / 2, 2, BLUE)
label(296, 150, ["8 required CSV files", "or one ZIP, plus up to", "3 optional lane files"])
# 6: system -> approved export
p = circle_point(155)
flow([p, (282, 530)], BLUE, "mb")
badge((282 + p[0]) / 2, (530 + p[1]) / 2, 6, BLUE)
label(330, 505, ["approved plan ZIP", "(only after approval)"])
# 7: export -> Company A (manual)
flow([(160, 498), (160, 418)], GREY, "mg", dashed=True)
badge(160, 458, 7, GREY)
label(180, 452, ["imported by hand;", "nothing written back"])
# 4 / 5: system <-> Groq (optional)
flow([circle_point(-14), (828, 266)], AMBER, "ma")
badge(742, 266, 4, AMBER)
label(660, 214, ["fact pack:", "calculated numbers", "and names only"], color="#92400e")
flow([(828, 312), circle_point(14)], AMBER, "ma")
badge(742, 312, 5, AMBER)
label(656, 346, ["draft explanation text", "figures checked,", "stays a draft"], color="#92400e")

# ---- the system ---------------------------------------------------------------
out.append(f'<circle cx="{CX}" cy="{CY}" r="{R}" fill="#1d4ed8"/>')
out.append(f'<text x="{CX}" y="{CY - 18}" text-anchor="middle" font-size="30" font-weight="800" fill="#fff">Nordic Flow</text>')
out.append(f'<text x="{CX}" y="{CY + 16}" text-anchor="middle" font-size="30" font-weight="800" fill="#fff">MVP</text>')
out.append(f'<text x="{CX}" y="{CY + 46}" text-anchor="middle" font-size="13" fill="#dbeafe">web UI · API · optimiser</text>')
out.append(f'<text x="{CX}" y="{CY + 64}" text-anchor="middle" font-size="13" fill="#dbeafe">SQLite store · audit trail</text>')

# ---- legend -------------------------------------------------------------------
lx, ly = 760, 400
out.append(f'<rect x="{lx}" y="{ly}" width="316" height="184" rx="8" fill="#fff" stroke="#cbd5e1" stroke-width="1.6"/>')
out.append(f'<text x="{lx + 16}" y="{ly + 26}" font-size="12" font-weight="700" fill="#64748b" letter-spacing="1.2">HOW TO READ THIS DIAGRAM</text>')
rows = [
    ("circle", "the system: Nordic Flow MVP"),
    ("rect", "external person or service"),
    ("files", "files that enter or leave the system"),
    ("blue", "data flow, implemented"),
    ("amber", "optional call to an external service"),
    ("grey", "manual step, not integrated"),
]
for i, (kind, text) in enumerate(rows):
    y = ly + 50 + i * 21
    x = lx + 18
    if kind == "circle":
        out.append(f'<circle cx="{x + 12}" cy="{y - 4}" r="8" fill="#1d4ed8"/>')
    elif kind == "rect":
        out.append(f'<rect x="{x}" y="{y - 12}" width="24" height="16" rx="2" fill="#e0e7ff" stroke="#3730a3" stroke-width="1.6"/>')
    elif kind == "files":
        out.append(f'<rect x="{x}" y="{y - 12}" width="24" height="16" rx="2" fill="#fde8e8" stroke="#9f1239" stroke-width="1.6"/>')
    else:
        c, m, d = {"blue": (BLUE, "mb", ""), "amber": (AMBER, "ma", ""), "grey": (GREY, "mg", ' stroke-dasharray="5 4"')}[kind]
        out.append(f'<path d="M{x} {y - 4} L{x + 24} {y - 4}" stroke="{c}" stroke-width="2.4"{d} marker-end="url(#{m})"/>')
    out.append(f'<text x="{x + 38}" y="{y}" font-size="13.5" fill="{BODY}">{esc(text)}</text>')
out.append("</svg>")

svg = "\n    ".join(out)
here = Path(__file__).parent
html = (here / "context.html").read_text(encoding="utf-8")
new = re.sub(r'<svg viewBox="0 0 1100 \d+" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="System context diagram">.*?</svg>',
             lambda m: svg, html, count=1, flags=re.S)
assert new != html, "svg block not found"
(here / "context.html").write_text(new, encoding="utf-8", newline="")
print("context.html page-1 diagram rewritten")
