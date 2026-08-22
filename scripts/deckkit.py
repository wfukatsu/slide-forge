#!/usr/bin/env python3
"""A kit for declaratively writing diagram-centric decks.

A deck is written as "1 module = 1 deck". A module registers slides via
`slide()` / `plain()`, which accumulate in `SLIDES`. `render_deck.py` generates
the deck, and `validate_layout.py` checks coordinates without calling the API.

    # mydeck.py
    from deckkit import *

    plain(layout="COVER", title="タイトル", subtitle="サブタイトル")

    @slide("結論を述べるアクションタイトル", note="スピーカーノート")
    def s_overview(d):
        layers(d, X0, DY0, W, [
            ("アプリ",  "業務アプリケーション",   d.P.primary),
            ("基盤",    "ミドルウェア",           d.P.primaryDark),
        ])
        foot(d, ["・要点を1行で"], "提供: ... ｜ 状況: GA")

All coordinates are in inches. The origin is the top-left of the slide. `d` is a diagrams.Canvas.

The layout safe area (LAYOUT) is computed from the template's page size.
The defaults are values measured on a 10 x 5.625 inch (16:9) template.
"""
from __future__ import annotations

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _text import em, fit_em  # noqa: E402,F401
from diagrams import Canvas, Palette, darken, lighten, mix, readable_on  # noqa: E402,F401

__all__ = [
    # Registration
    "SLIDES", "slide", "plain", "reset",
    # Layout constants
    "X0", "W", "XE", "DY0", "DY1", "NY", "EY", "PAGE_W", "PAGE_H",
    "TITLE_EM_MAX", "BODY_FONT_SIZE", "BODY_LINE_SPACING", "BODY_MAX_LINES",
    "configure_layout",
    # Bottom fixed elements
    "foot", "FOOT_MODE",
    # Composite parts (basic)
    "caption", "grouphead", "zone", "db", "grid", "layers", "steps_v",
    "pill", "pills", "xmark", "checkmark", "banner", "kv_rows",
    # Composite parts (layout patterns)
    "tone_colors", "tone_solid",
    "compare_panels", "swimlane", "timeline", "tree", "decision",
    "quadrant", "matrix_map", "roadmap", "pyramid", "cycle", "funnel",
    "callouts", "stats", "checklist", "pipeline", "legend",
    # Measurement
    "em", "fit_em", "fits_one_line",
    # Re-exports
    "Canvas", "Palette", "lighten", "darken", "mix", "readable_on",
]

# ---------------------------------------------------------------------------
# Layout constants
#
# Values measured on a 16:9 (10 x 5.625in) template.
#   - The title placeholder is y=0.126, h=0.351 -> a single line ends at y=0.48
#   - The master's logo/copyright footer starts around y=5.197
#   - So diagrams should stay within y=0.84-4.30, with the key-points and
#     edition lines below that
# For templates of a different size, override with configure_layout().
# ---------------------------------------------------------------------------
PAGE_W, PAGE_H = 10.0, 5.625
X0, W, XE = 0.5, 9.0, 9.5
DY0, DY1 = 0.84, 4.30           # top/bottom bounds where diagrams may be drawn
NY = 4.38                       # key-points line (up to 2 lines)
EY = 4.86                       # edition/availability line (1 line)

# Upper bound (in full-width-equivalent chars) for a title to fit on one line.
# At 20pt bold, em=31.0 fit on 1 line while em=33.0 wrapped to 2 lines, so the
# cap is set to 30.5. If it wraps to 2 lines, the title encroaches on DY0 and
# overlaps the diagram.
TITLE_EM_MAX = 30.5

# Recommended values when flowing text into the body placeholder.
# Google's lineSpacing is a percentage of the font's native line height
# (about 1.45em for Noto Sans JP), so 12pt / 120% gives roughly 0.29in per
# line. h=4.068in fits about 14 lines.
BODY_FONT_SIZE = 12
BODY_LINE_SPACING = 120
BODY_MAX_LINES = 14


def configure_layout(*, page_w=None, page_h=None, margin=None,
                     diagram_top=None, diagram_bottom=None,
                     note_y=None, edition_y=None, title_em_max=None):
    """Override the page size or safe area. Use this when the template is not 16:9.

    Passing just `margin` recomputes X0 / W / XE.
    """
    global PAGE_W, PAGE_H, X0, W, XE, DY0, DY1, NY, EY, TITLE_EM_MAX
    if page_w is not None:
        PAGE_W = page_w
    if page_h is not None:
        PAGE_H = page_h
    if margin is not None:
        X0 = margin
    XE = PAGE_W - X0
    W = XE - X0
    if diagram_top is not None:
        DY0 = diagram_top
    if diagram_bottom is not None:
        DY1 = diagram_bottom
    if note_y is not None:
        NY = note_y
    if edition_y is not None:
        EY = edition_y
    if title_em_max is not None:
        TITLE_EM_MAX = title_em_max


# ---------------------------------------------------------------------------
# Measurement
# ---------------------------------------------------------------------------
# `em` lives in _text.py and is re-exported here: the auditor in diagrams.py
# measures with the same function, so a title this says fits is a title the
# audit agrees fits.


def fits_one_line(title: str) -> bool:
    return em(title) <= TITLE_EM_MAX


# ---------------------------------------------------------------------------
# Slide registration
# ---------------------------------------------------------------------------

SLIDES: list[dict] = []


def reset() -> None:
    """Clear registered slides (for tests / reloading)."""
    SLIDES.clear()


def slide(title=None, *, layout="TITLE_ONLY", note=None, **kw):
    """Decorator that registers a slide which draws a diagram.

    The decorated function is called as draw(d), where d is a diagrams.Canvas.
    layout is the template's role name or layout key. Since the diagram is
    drawn manually, the default is a TITLE_ONLY-style layout with no body
    placeholder.
    """
    def deco(fn):
        SLIDES.append(dict(layout=layout, title=title, notes=note, draw=fn, **kw))
        return fn
    return deco


def plain(*, layout, **kw):
    """Register a slide that consists only of placeholders (cover, section divider, back cover, etc.).

    title / subtitle / body / bodies / notes are passed through as-is.
    Passing an array for body joins it with newlines.
    """
    SLIDES.append(dict(layout=layout, draw=None, **kw))


# ---------------------------------------------------------------------------
# Bottom fixed elements
#
# Shapes drawn while FOOT_MODE is True are excluded from validate_layout's
# boundary checks, since it is correct for the key-points and edition lines
# to sit below DY1.
# ---------------------------------------------------------------------------

FOOT_MODE = [False]


def foot(d, points=None, edition=None):
    """Place the key-points line (up to 2 lines) and an availability line at the bottom of the slide.

    points is the slide's takeaway message. edition is supplementary text you
    want to show consistently on feature pages, such as "Provided: ... | Status: GA".
    Both are optional.
    """
    FOOT_MODE[0] = True
    try:
        if points:
            d.label(X0, NY, W, 0.46, "\n".join(points), size=10.5,
                    align="START", valign="TOP", color=d.P.text, line_spacing=115)
        if edition:
            d.label(X0, EY, W, 0.22, edition, size=9,
                    align="START", valign="TOP", color=d.P.muted)
    finally:
        FOOT_MODE[0] = False


# ---------------------------------------------------------------------------
# Composite parts
# ---------------------------------------------------------------------------

def caption(d, x, y, w, text, *, size=9, color=None, align="CENTER", h=0.22):
    """Small caption placed under a diagram."""
    return d.label(x, y, w, h, text, size=size, align=align, valign="TOP",
                   color=color or d.P.muted, line_spacing=115)


def grouphead(d, x, y, w, text, *, fill=None, size=10, h=0.28):
    """Banner-style heading."""
    return d.shape(x, y, w, h, kind="RECTANGLE",
                   fill=fill or lighten(d.P.primary, 0.86), stroke=None,
                   text=text, size=size, bold=True, color=d.P.primaryDark)


def zone(d, x, y, w, h, label=None, *, fill=None, stroke=None, size=9):
    """A region that groups elements together. Can have a small heading in the top-left.

    Draw the region's contents at y + 0.34 or below so they don't overlap the heading.
    """
    d.shape(x, y, w, h, kind="ROUND_RECTANGLE", fill=fill or "#FBFCFE",
            stroke=stroke or lighten(d.P.primary, 0.72), stroke_weight=1.0)
    if label:
        d.label(x + 0.1, y + 0.06, w - 0.2, 0.24, label, size=size, bold=True,
                align="START", valign="TOP", color=d.P.primaryDark)


def banner(d, y, text, *, tone="info", size=9, h=0.34, x=None, w=None):
    """Full-width notice/summary bar. tone is info / good / warn / bad."""
    tones = {
        "info": (lighten(d.P.primary, 0.90), lighten(d.P.primary, 0.62), d.P.text),
        "good": (lighten(d.P.success, 0.86), None, darken(d.P.success, 0.45)),
        "warn": (lighten(d.P.warning, 0.74), None, darken(d.P.warning, 0.55)),
        "bad": (lighten(d.P.danger, 0.88), lighten(d.P.danger, 0.55), darken(d.P.danger, 0.25)),
    }
    fill, stroke, col = tones.get(tone, tones["info"])
    return d.shape(x if x is not None else X0, y, w if w is not None else W, h,
                   kind="ROUND_RECTANGLE", fill=fill, stroke=stroke,
                   text=text, size=size, bold=True, color=col)


def db(d, x, y, w, h, name, *, sub=None, fill="#FFFFFF", stroke=None):
    """Database cylinder icon plus a label below it.

    The label extends about 0.22in below h (0.42in if sub is given), so
    choose y with that margin at the bottom in mind.
    """
    d.shape(x, y, w, h, kind="CAN", fill=fill, stroke=stroke or d.P.muted,
            stroke_weight=1.0)
    d.label(x - 0.2, y + h + 0.03, w + 0.4, 0.22, name, size=8.5,
            align="CENTER", valign="TOP", color=d.P.text)
    if sub:
        d.label(x - 0.2, y + h + 0.24, w + 0.4, 0.2, sub, size=7.5,
                align="CENTER", valign="TOP", color=d.P.muted)


def grid(d, x, y, w, cols, rows, *, col_w=None, head_h=0.32, row_h=0.30,
         size=9, head_size=9, first_align="START", head_fill=None,
         cell_colors=None):
    """Table. cols is an array of headers, rows is an array of rows (each row an array of cells).

    cell_colors(i, j, cell) -> (fill, color) | None lets you color individual
    cells. Use it to show OK/NG (○/×) or yes/no via color. Returns the table's bottom y.
    """
    n = len(cols)
    if col_w is None:
        col_w = [w * 0.34] + [(w - w * 0.34) / (n - 1)] * (n - 1)
    hf = head_fill or lighten(d.P.primary, 0.80)
    cx = x
    for j, c in enumerate(cols):
        d.shape(cx, y, col_w[j], head_h, kind="RECTANGLE", fill=hf, stroke="#FFFFFF",
                stroke_weight=0.75, text=c, size=head_size, bold=True,
                color=d.P.primaryDark, align=(first_align if j == 0 else "CENTER"))
        cx += col_w[j]
    for i, row in enumerate(rows):
        ry = y + head_h + i * row_h
        bg = "#FFFFFF" if i % 2 == 0 else "#F7F9FC"
        cx = x
        for j, cell in enumerate(row):
            col, f = d.P.text, bg
            if cell_colors:
                cc = cell_colors(i, j, cell)
                if cc:
                    f, col = cc
            d.shape(cx, ry, col_w[j], row_h, kind="RECTANGLE", fill=f, stroke="#FFFFFF",
                    stroke_weight=0.75, text=cell, size=size, color=col,
                    bold=(j == 0), align=(first_align if j == 0 else "CENTER"))
            cx += col_w[j]
    return y + head_h + len(rows) * row_h


def layers(d, x, y, w, items, *, row_h=0.62, gap=0.1, label_w=1.55):
    """Horizontal layer diagram. items is an array of (layer name, description, color), stacked top to bottom.

    Use this to show an architecture's layers. Returns the bottom y.
    """
    for i, (name, body, col) in enumerate(items):
        ry = y + i * (row_h + gap)
        d.shape(x, ry, label_w, row_h, kind="ROUND_RECTANGLE", fill=col, stroke=None,
                text=name, size=10, bold=True, color="#FFFFFF", line_spacing=105)
        d.shape(x + label_w + 0.08, ry, w - label_w - 0.08, row_h,
                kind="ROUND_RECTANGLE", fill=lighten(col, 0.9),
                stroke=lighten(col, 0.6), text=body, size=9.5, color=d.P.text,
                line_spacing=115)
    return y + len(items) * (row_h + gap) - gap


def steps_v(d, x, y, w, items, *, row_h=0.52, gap=0.16, num_w=0.34):
    """Numbered vertical flow. items is an array of (heading, description). Returns the bottom y."""
    for i, (head, body) in enumerate(items):
        ry = y + i * (row_h + gap)
        d.shape(x, ry + (row_h - num_w) / 2, num_w, num_w, kind="ELLIPSE",
                fill=d.P.primary, stroke=None, text=str(i + 1), size=10,
                bold=True, color="#FFFFFF")
        d.shape(x + num_w + 0.12, ry, w - num_w - 0.12, row_h,
                kind="ROUND_RECTANGLE", fill=lighten(d.P.primary, 0.93),
                stroke=lighten(d.P.primary, 0.7))
        d.label(x + num_w + 0.26, ry + 0.05, w - num_w - 0.4, 0.24, head, size=9.5,
                bold=True, align="START", valign="TOP", color=d.P.primaryDark)
        d.label(x + num_w + 0.26, ry + 0.28, w - num_w - 0.4, row_h - 0.3, body,
                size=8.5, align="START", valign="TOP", color=d.P.text,
                line_spacing=110)
        if i < len(items) - 1:
            d.arrow(x + num_w / 2, ry + row_h + 0.01, x + num_w / 2,
                    ry + row_h + gap - 0.01, color=d.P.primary, weight=1.5)
    return y + len(items) * (row_h + gap) - gap


def kv_rows(d, x, y, w, items, *, key_w=1.85, row_h=0.32, gap=0.06,
            key_fill=None, key_color=None, size=8):
    """A two-column "item -> note" list. Use this when a table would feel too heavy."""
    for i, (k, v) in enumerate(items):
        ry = y + i * (row_h + gap)
        d.shape(x, ry, key_w, row_h, kind="ROUND_RECTANGLE",
                fill=key_fill or lighten(d.P.info, 0.84), stroke=None,
                text=k, size=size, color=key_color or darken(d.P.info, 0.35))
        d.label(x + key_w + 0.16, ry + 0.05, w - key_w - 0.16, row_h - 0.06, v,
                size=size - 0.5, align="START", color=d.P.text)
    return y + len(items) * (row_h + gap) - gap


def pill(d, x, y, w, h, text, *, fill=None, color=None, size=8.5,
         text_margin=0.04):
    """A single rounded chip.

    A chip's padding is its own geometry — the 0.10in a text frame carries by
    default would take most of the width of a chip a few tenths of an inch
    wide, and wrap a word like TIMESTAMP that was meant to sit on one line.
    """
    return d.shape(x, y, w, h, kind="ROUND_RECTANGLE",
                   fill=fill or lighten(d.P.primary, 0.85), stroke=None,
                   text=text, size=size, color=color or d.P.primaryDark, bold=True,
                   text_margin=text_margin)


def pills(d, x, y, w, items, *, per_row=5, h=0.26, gap=0.08, fill=None,
          color=None, size=8.5):
    """Grid of chips. Use this for enumerations where order doesn't matter, like supported products or permissions.

    Returns the bottom y.
    """
    rows = (len(items) + per_row - 1) // per_row
    pw = (w - gap * (per_row - 1)) / per_row
    for i, t in enumerate(items):
        r, c = divmod(i, per_row)
        pill(d, x + c * (pw + gap), y + r * (h + gap), pw, h, t,
             fill=fill, color=color, size=size)
    return y + rows * (h + gap) - gap


def xmark(d, cx, cy, *, r=0.14, color=None):
    """Circled X mark indicating no/failure. Positioned by center coordinates."""
    c = color or d.P.danger
    # A badge this small is all glyph: the margin Slides bakes into a text
    # frame is wider than the badge itself, and a full-width mark like × has
    # nowhere to sit. Pull it back out
    d.shape(cx - r, cy - r, r * 2, r * 2, kind="ELLIPSE", fill=c, stroke=None,
            text="×", size=11, bold=True, color="#FFFFFF", text_margin=0.0)


def checkmark(d, cx, cy, *, r=0.14, color=None):
    """Circled check mark indicating yes/success. Positioned by center coordinates."""
    c = color or d.P.success
    d.shape(cx - r, cy - r, r * 2, r * 2, kind="ELLIPSE", fill=c, stroke=None,
            text="✓", size=10, bold=True, color="#FFFFFF", text_margin=0.0)


# ---------------------------------------------------------------------------
# Layout patterns
#
# Common conventions:
#   - Coordinates are in inches. x, y is the top-left corner.
#   - **The return value is always the bottom y of the drawn area.** The next
#     block should be positioned starting from that value. Following this
#     convention prevents the "previous block overflows and overlaps the next"
#     accident.
#   - tone is one of "primary" / "info" / "good" / "warn" / "bad" / "muted" / "accent".
# ---------------------------------------------------------------------------

def tone_colors(d, tone="info"):
    """Return (fill, stroke, text color) for a tone name. A pale fill paired with a dark text color."""
    P = d.P
    m = {
        "primary": (P.primary, None, "#FFFFFF"),
        "accent": (P.info, None, "#FFFFFF"),
        "info": (lighten(P.primary, 0.90), lighten(P.primary, 0.62), P.text),
        "good": (lighten(P.success, 0.86), lighten(P.success, 0.50), darken(P.success, 0.45)),
        "warn": (lighten(P.warning, 0.72), lighten(P.warning, 0.42), darken(P.warning, 0.55)),
        "bad": (lighten(P.danger, 0.88), lighten(P.danger, 0.52), darken(P.danger, 0.25)),
        "muted": ("#F4F6F9", lighten(P.muted, 0.55), P.text),
    }
    return m.get(tone, m["info"])


def tone_solid(d, tone="info"):
    """Return a solid, saturated color for a tone name, for use in dots or bars."""
    P = d.P
    return {
        "primary": P.primary,
        "accent": P.info,
        # Make info a mid-tone that pairs with the pale fill. Using the same
        # color as primary would make the two indistinguishable in legends/markers
        "info": lighten(P.primary, 0.35),
        "good": P.success,
        # Darkening warning as-is turns it brown, which doesn't read as
        # "caution". Shift it slightly toward danger to get an amber tone
        "warn": darken(mix(P.warning, P.danger, 0.25), 0.12),
        "bad": P.danger,
        "muted": lighten(P.muted, 0.20),
    }.get(tone, P.primary)


def _fit(d, x, y, w, h, text, *, size, bold=False, color=None, align="CENTER",
         valign="MIDDLE", ls=110):
    """Place text inside a box. A thin wrapper used internally by patterns."""
    return d.label(x, y, w, h, text, size=size, bold=bold,
                   color=color or d.P.text, align=align, valign=valign,
                   line_spacing=ls)


# ---- 1. Compare panels (Before / After, A / B) ----

def compare_panels(d, x, y, w, h, left, right, *, gap=0.50, arrow=True):
    """Place two panels side by side for comparison.

    left / right is a dict:
        {"title": heading, "tone": "bad"/"good"/…, "head": center emphasis line,
         "items": [item, …], "note": bottom note}
    Placing elements in the same structure and position on both sides makes
    only the differences catch the eye.
    """
    pw = (w - gap) / 2
    for i, spec in enumerate((left, right)):
        px = x + i * (pw + gap)
        tone = spec.get("tone", "info")
        fill, stroke, col = tone_colors(d, tone)
        zone(d, px, y, pw, h, spec.get("title"),
             fill=lighten(fill, 0.55), stroke=stroke)
        iy = y + 0.36
        if spec.get("head"):
            d.shape(px + 0.20, iy, pw - 0.40, 0.40, kind="ROUND_RECTANGLE",
                    fill=tone_solid(d, tone), stroke=None, text=spec["head"],
                    size=9.5, bold=True, color="#FFFFFF")
            iy += 0.52
        items = spec.get("items", [])
        if items:
            avail = (y + h - 0.10) - iy - (0.46 if spec.get("note") else 0.0)
            ih = min(0.52, max(0.30, (avail - 0.08 * (len(items) - 1)) / max(1, len(items))))
            for it in items:
                d.shape(px + 0.20, iy, pw - 0.40, ih, kind="ROUND_RECTANGLE",
                        fill=fill, stroke=stroke, text=it, size=8.5, color=col,
                        line_spacing=110)
                iy += ih + 0.08
        if spec.get("note"):
            d.label(px + 0.20, y + h - 0.46, pw - 0.40, 0.40, spec["note"],
                    size=8, align="START", valign="TOP", color=col, line_spacing=115)
    if arrow:
        d.arrow_shape(x + pw + 0.02, y + h / 2 - 0.23, gap - 0.04, 0.46,
                      fill=lighten(d.P.primary, 0.70))
    return y + h


# ---- 2. Swimlane ----

def swimlane(d, x, y, w, lanes, steps, *, lane_h=1.02, lane_gap=0.30,
             label_w=1.30, box_gap=0.20):
    """Lane (owner) x step diagram.

    lanes = [(lane name, color), …] (top to bottom)
    steps = [(heading, body, lane index, tone), …] (left to right)

    Arrows between steps **connect the actual coordinates**. Drawing a
    horizontal line when crossing lanes would misrepresent the path, so the
    start and end points are connected directly instead.
    """
    cx = x + label_w + 0.10
    cw = w - label_w - 0.10
    lane_y = []
    for i, (nm, col) in enumerate(lanes):
        ly = y + i * (lane_h + lane_gap)
        lane_y.append(ly)
        d.shape(x, ly, label_w, lane_h, kind="ROUND_RECTANGLE", fill=col,
                stroke=None, text=nm, size=9, bold=True, color="#FFFFFF",
                line_spacing=105)
        d.shape(cx, ly, cw, lane_h, kind="ROUND_RECTANGLE",
                fill=lighten(col, 0.94), stroke=lighten(col, 0.78),
                stroke_weight=0.75)

    n = len(steps)
    bw = (cw - 0.24 - box_gap * (n - 1)) / n
    centers = []
    for i, step in enumerate(steps):
        head, body, lane, tone = (list(step) + ["info"])[:4]
        fill, stroke, col = tone_colors(d, tone)
        bx = cx + 0.12 + i * (bw + box_gap)
        by = lane_y[lane]
        d.shape(bx, by + 0.12, bw, lane_h - 0.24, kind="ROUND_RECTANGLE",
                fill=fill, stroke=stroke)
        d.label(bx + 0.06, by + 0.20, bw - 0.12, 0.24, head, size=9, bold=True,
                align="CENTER", color=col)
        if body:
            d.label(bx + 0.06, by + 0.45, bw - 0.12, lane_h - 0.60, body,
                    size=8, align="CENTER", color=col, line_spacing=110)
        centers.append((bx, bx + bw, by + lane_h / 2))
    for i in range(n - 1):
        _, x_end, y1 = centers[i]
        x_start, _, y2 = centers[i + 1]
        d.arrow(x_end + 0.03, y1, x_start - 0.03, y2, color=d.P.primary, weight=1.6)
    return y + len(lanes) * (lane_h + lane_gap) - lane_gap


# ---- 3. Timeline ----

def timeline(d, x, y, w, marks, *, bands=None, h=1.60, label_w=1.90):
    """Time series along a horizontal axis.

    marks = [(position 0.0-1.0, label, tone), …]
    bands = [(start position, end position, label, tone), …] (period bands laid over the line)

    Put supplementary text in the marker's own label. A separate label plus a
    vertical arrow would overlap other markers' descriptions or the block below.
    """
    line_y = y + h * 0.46

    def px(p):
        return x + 0.30 + (w - 0.60) * p

    d.line(x + 0.30, line_y, x + w - 0.30, line_y,
           color=lighten(d.P.muted, 0.30), weight=1.5, free=True)   # axis
    for a, b, label, tone in (bands or []):
        fill, _, col = tone_colors(d, tone)
        d.shape(px(a), line_y - 0.38, px(b) - px(a), 0.24, kind="ROUND_RECTANGLE",
                fill=fill, stroke=None, text=label, size=7.5, bold=True, color=col)
    for p, label, tone in marks:
        mx, col = px(p), tone_solid(d, tone)
        d.shape(mx - 0.09, line_y - 0.09, 0.18, 0.18, kind="ELLIPSE",
                fill=col, stroke=None)
        d.label(mx - label_w / 2, line_y + 0.15, label_w,
                (y + h) - (line_y + 0.15), label, size=7.5, bold=True,
                align="CENTER", valign="TOP", color=darken(col, 0.20),
                line_spacing=105)
    return y + h


# ---- 4. Hierarchical tree ----

def tree(d, x, y, w, nodes, *, row_h=0.46, gap=0.10, indent=0.24,
         box_w=1.45, size=8.5):
    """Tree with depth. nodes = [(depth, name, description), …], placed top to bottom.

    The connector line from a parent is drawn from "the nearest node one
    level shallower", not from the previous node at the same depth.
    """
    last_y = {}
    for i, (depth, name, desc) in enumerate(nodes):
        iy = y + i * (row_h + gap)
        ix = x + depth * indent
        shade = min(0.72, 0.0 + depth * 0.22)
        col = lighten(d.P.primaryDark, shade)
        d.shape(ix + 0.16, iy, box_w, row_h - 0.12, kind="ROUND_RECTANGLE",
                fill=col, stroke=None, text=name, size=size, bold=True,
                color="#FFFFFF" if shade < 0.55 else d.P.text)
        if desc:
            d.label(ix + box_w + 0.30, iy + 0.03, w - (ix - x) - box_w - 0.46,
                    row_h - 0.14, desc, size=size - 1, align="START",
                    valign="MIDDLE", color=d.P.text, line_spacing=110)
        if depth > 0 and (depth - 1) in last_y:
            py = last_y[depth - 1]
            ex = x + (depth - 1) * indent + 0.30
            d.line(ex, py + row_h - 0.12, ex, iy + (row_h - 0.12) / 2,
                   color=lighten(d.P.muted, 0.25), weight=1.0, free=True)
            d.line(ex, iy + (row_h - 0.12) / 2, ix + 0.14,
                   iy + (row_h - 0.12) / 2, color=lighten(d.P.muted, 0.25),
                   weight=1.0, free=True)
        last_y[depth] = iy
    return y + len(nodes) * (row_h + gap) - gap


# ---- 5. Decision branch ----

def decision(d, x, y, w, question, branches, *, dia_w=3.70, dia_h=0.78,
             box_h=0.60, drop=0.42):
    """A diamond decision with 2-3 outcomes fanning out below it.

    branches = [(branch label, outcome text, tone), …]
    The diamond's text is not placed directly on the shape but overlaid as a
    separate label (otherwise the edges get clipped).
    """
    cx = x + w / 2
    d.shape(cx - dia_w / 2, y, dia_w, dia_h, kind="DIAMOND",
            fill=lighten(d.P.warning, 0.68), stroke=None)
    _fit(d, cx - dia_w / 2 + 0.30, y + 0.14, dia_w - 0.60, dia_h - 0.28,
         question, size=8.5, bold=True, color=darken(d.P.warning, 0.55), ls=105)

    n = len(branches)
    by = y + dia_h + drop
    bw = (w - 0.30 * (n - 1)) / n
    # Every arrow first, then the labels on top of them. The outer branches'
    # arrows cross the whole width of their own box on the way down, so no
    # side of the box is clear of the path — the label has to ride over it
    for i, (_, _, tone) in enumerate(branches):
        bx = x + i * (bw + 0.30)
        # Land slightly right of the box's center so the arrowhead and the
        # left-aligned label don't stack up on the same point
        d.arrow(cx + (i - (n - 1) / 2) * 0.55, y + dia_h + 0.02,
                bx + bw * 0.62, by - 0.02, color=tone_solid(d, tone), weight=1.5)
    for i, (label, text, tone) in enumerate(branches):
        fill, stroke, col = tone_colors(d, tone)
        bx = x + i * (bw + 0.30)
        # Backed by the page color, not drawn bare: the arrow passing under it
        # would otherwise run straight through the wording
        d.shape(bx, by - 0.26, bw * 0.46, 0.22, kind="RECTANGLE",
                fill=d.P.page, stroke=None, text=label, size=7.5,
                align="START", valign="MIDDLE", color=d.P.muted)
        d.shape(bx, by, bw, box_h, kind="ROUND_RECTANGLE", fill=fill,
                stroke=stroke, text=text, size=9, color=col, line_spacing=110)
    return by + box_h


# ---- 6. 2x2 matrix ----

def quadrant(d, x, y, w, h, quads, *, x_label="", y_label="",
             x_axis=("低", "高"), y_axis=("低", "高")):
    """2x2 matrix. quads is a list in [top-left, top-right, bottom-left, bottom-right] order,
    each (heading, [item, …], tone). Use this for prioritization or positioning strategy.
    """
    pad = 0.42                       # margin for axis labels
    gx, gy = x + pad, y
    gw, gh = w - pad, h - pad
    cw, ch = gw / 2, gh / 2
    for i, (head, items, tone) in enumerate(quads):
        fill, stroke, col = tone_colors(d, tone)
        qx = gx + (i % 2) * cw
        qy = gy + (i // 2) * ch
        d.shape(qx + 0.03, qy + 0.03, cw - 0.06, ch - 0.06,
                kind="ROUND_RECTANGLE", fill=fill, stroke=stroke)
        d.label(qx + 0.16, qy + 0.10, cw - 0.32, 0.24, head, size=9, bold=True,
                align="START", valign="TOP", color=col)
        if items:
            d.label(qx + 0.16, qy + 0.36, cw - 0.32, ch - 0.46,
                    "\n".join("・" + s for s in items), size=8, align="START",
                    valign="TOP", color=d.P.text, line_spacing=125)
    # axes
    d.label(x, gy, pad - 0.06, gh, y_label, size=8, bold=True, align="CENTER",
            valign="MIDDLE", color=d.P.muted)
    d.label(gx, y + h - pad + 0.06, gw, pad - 0.10, x_label, size=8, bold=True,
            align="CENTER", valign="TOP", color=d.P.muted)
    d.label(gx, y + h - pad + 0.06, 1.4, 0.20, x_axis[0], size=7.5,
            align="START", valign="TOP", color=d.P.muted)
    d.label(gx + gw - 1.4, y + h - pad + 0.06, 1.4, 0.20, x_axis[1], size=7.5,
            align="END", valign="TOP", color=d.P.muted)
    return y + h


# ---- 7. Positioning map (2-axis scatter) ----

def matrix_map(d, x, y, w, h, items, *, x_label="", y_label="",
               x_axis=("低", "高"), y_axis=("低", "高"), dot=0.13):
    """Place items on two axes. items = [(name, x0-1, y0-1, tone), …]

    y=1.0 is the top. Use this for competitive comparisons or feature positioning.
    """
    pad_l, pad_b = 0.46, 0.40
    gx, gy = x + pad_l, y
    gw, gh = w - pad_l, h - pad_b
    d.shape(gx, gy, gw, gh, kind="RECTANGLE", fill="#FBFCFE",
            stroke=lighten(d.P.primary, 0.75), stroke_weight=1.0)
    d.line(gx, gy + gh / 2, gx + gw, gy + gh / 2, color=lighten(d.P.muted, 0.55),
           weight=0.9, dashed=True, free=True)                      # gridline
    d.line(gx + gw / 2, gy, gx + gw / 2, gy + gh, color=lighten(d.P.muted, 0.55),
           weight=0.9, dashed=True, free=True)
    for name, px_, py_, tone in items:
        cx = gx + gw * px_
        cy = gy + gh * (1.0 - py_)
        col = tone_solid(d, tone)
        d.shape(cx - dot, cy - dot, dot * 2, dot * 2, kind="ELLIPSE",
                fill=col, stroke=None)
        d.label(cx - 1.05, cy + dot + 0.02, 2.10, 0.22, name, size=7.5,
                bold=True, align="CENTER", valign="TOP", color=darken(col, 0.25))
    d.label(x, gy, pad_l - 0.08, gh, y_label, size=8, bold=True, align="CENTER",
            valign="MIDDLE", color=d.P.muted)
    d.label(gx, gy + gh + 0.04, gw, 0.22, x_label, size=8, bold=True,
            align="CENTER", valign="TOP", color=d.P.muted)
    d.label(gx, gy + gh + 0.04, 1.4, 0.20, x_axis[0], size=7.5, align="START",
            valign="TOP", color=d.P.muted)
    d.label(gx + gw - 1.4, gy + gh + 0.04, 1.4, 0.20, x_axis[1], size=7.5,
            align="END", valign="TOP", color=d.P.muted)
    return y + h


# ---- 8. Roadmap (phases x lanes) ----

def roadmap(d, x, y, w, phases, lanes, *, head_h=0.32, lane_h=0.44, gap=0.10,
            label_w=1.90):
    """Roadmap with phases as columns and lanes as rows.

    phases = [column heading, …]
    lanes  = [(lane name, [(start column index, column span, label, tone), …]), …]
    """
    n = len(phases)
    cw = (w - label_w) / n
    for j, ph in enumerate(phases):
        d.shape(x + label_w + j * cw, y, cw, head_h, kind="RECTANGLE",
                fill=lighten(d.P.primary, 0.82), stroke="#FFFFFF",
                stroke_weight=0.75, text=ph, size=8.5, bold=True,
                color=d.P.primaryDark)
    for i, (nm, bars) in enumerate(lanes):
        ry = y + head_h + 0.06 + i * (lane_h + gap)
        d.label(x, ry, label_w - 0.12, lane_h, nm, size=8.5, align="START",
                valign="MIDDLE", color=d.P.text)
        d.shape(x + label_w, ry, cw * n, lane_h, kind="RECTANGLE",
                fill="#F7F9FC" if i % 2 else "#FFFFFF", stroke=None)
        for start, span, label, tone in bars:
            fill, stroke, col = tone_colors(d, tone)
            d.shape(x + label_w + start * cw + 0.05, ry + 0.05,
                    span * cw - 0.10, lane_h - 0.10, kind="ROUND_RECTANGLE",
                    fill=fill, stroke=stroke, text=label, size=8, color=col)
    return y + head_h + 0.06 + len(lanes) * (lane_h + gap) - gap


# ---- 9. Pyramid (maturity / hierarchy) ----

def pyramid(d, x, y, w, h, levels, *, gap=0.08, min_ratio=0.40):
    """Tiers that narrow toward the top. levels, top to bottom, is [(name, description, tone), …].

    Use this to show a maturity model or a "foundation -> application" relationship.
    """
    n = len(levels)
    lh = (h - gap * (n - 1)) / n
    for i, (name, desc, tone) in enumerate(levels):
        ratio = min_ratio + (1.0 - min_ratio) * (i / max(1, n - 1))
        lw = w * ratio
        lx = x + (w - lw) / 2
        ly = y + i * (lh + gap)
        col = tone_solid(d, tone)
        inside = desc and ((w - lw) / 2 - 0.12) < 1.2
        d.shape(lx, ly, lw, lh, kind="ROUND_RECTANGLE", fill=col, stroke=None,
                text=name, size=9.5, bold=True, color="#FFFFFF",
                valign="TOP" if inside else "MIDDLE")
        if desc:
            side = (w - lw) / 2 - 0.12
            if side >= 1.2:                       # fits alongside
                d.label(x + w - side, ly, side, lh, desc, size=8,
                        align="START", valign="MIDDLE", color=d.P.text,
                        line_spacing=110)
            else:                                 # otherwise, put it inside the tier
                d.label(lx + 0.10, ly + lh * 0.52, lw - 0.20, lh * 0.42, desc,
                        size=7.5, align="CENTER", valign="TOP",
                        color=lighten("#FFFFFF", 0.0) if False else "#E8F1FA")
    return y + h


# ---- 10. Cycle (circular process) ----

def cycle(d, x, y, w, h, steps, *, box_w=1.95, box_h=0.62, size=8.5,
          tone="info"):
    """A circular process inscribed in the rectangle (x, y, w, h). steps = [label, …] (4-6 is a good count)

    The radius is chosen automatically so the boxes don't overflow this
    rectangle. Directly specifying the center and radius makes it easy for
    the top edge to poke through the safe area, so this is avoided.
    Arrows are placed tangentially at the midpoint angle between steps.
    """
    cx, cy = x + w / 2, y + h / 2
    n = len(steps)
    # Arrows sit on a ring outside the boxes, so shrink the box radius
    # inward by that amount
    ring = box_h * 0.55 + 0.10
    r = max(0.30, min((h - box_h) / 2 - ring, (w - box_w) / 2))
    # If the radius gets too small, opposing boxes collide. Shrink the box
    # width to fit the radius, then recompute the radius for the narrower box
    box_w = min(box_w, max(0.85, 2 * r - 0.16))
    r = max(0.30, min((h - box_h) / 2 - ring, (w - box_w) / 2))
    fill, stroke, col = tone_colors(d, tone)
    pos = []
    for i, s in enumerate(steps):
        th = -math.pi / 2 + 2 * math.pi * i / n
        px = cx + r * math.cos(th)
        py = cy + r * math.sin(th)
        pos.append((px, py))
        d.shape(px - box_w / 2, py - box_h / 2, box_w, box_h,
                kind="ROUND_RECTANGLE", fill=fill, stroke=stroke,
                text=s, size=size, color=col, line_spacing=105)
    ra = r + ring                                  # radius of the ring where arrows sit
    for i in range(n):
        th = -math.pi / 2 + 2 * math.pi * (i + 0.5) / n
        ax = cx + ra * math.cos(th)
        ay = cy + ra * math.sin(th)
        tx, ty = -math.sin(th), math.cos(th)      # tangent (clockwise)
        d.arrow(ax - tx * 0.22, ay - ty * 0.22, ax + tx * 0.22, ay + ty * 0.22,
                color=d.P.primary, weight=1.6, free=True)   # arrow circling between the boxes
    return y + h


# ---- 11. Funnel ----

def funnel(d, x, y, w, h, stages, *, gap=0.08, min_ratio=0.42):
    """A funnel that widens toward the top. stages = [(label, note, tone), …], top to bottom."""
    n = len(stages)
    sh = (h - gap * (n - 1)) / n
    for i, (label, sub, tone) in enumerate(stages):
        ratio = 1.0 - (1.0 - min_ratio) * (i / max(1, n - 1))
        sw = w * ratio
        sx = x + (w - sw) / 2
        sy = y + i * (sh + gap)
        col = tone_solid(d, tone)
        inside = sub and ((w - sw) / 2 - 0.12) < 1.2
        d.shape(sx, sy, sw, sh, kind="ROUND_RECTANGLE", fill=col, stroke=None,
                text=label, size=9.5, bold=True, color="#FFFFFF",
                valign="TOP" if inside else "MIDDLE")
        if sub:
            side = (w - sw) / 2 - 0.12
            if side >= 1.2:                       # fits alongside
                d.label(x + w - side, sy, side, sh, sub, size=8, align="START",
                        valign="MIDDLE", color=d.P.text, line_spacing=110)
            else:                                 # otherwise, put it inside the tier
                d.label(sx + 0.10, sy + sh * 0.52, sw - 0.20, sh * 0.42, sub,
                        size=7.5, align="CENTER", valign="TOP", color="#E8F1FA")
    return y + h


# ---- 12. Annotated diagram (center + numbered callouts) ----

def callouts(d, x, y, w, h, center, notes, *, note_w=2.40, tone="primary"):
    """Attach numbered annotations from the left and right to a central subject.

    center = (heading, body)
    notes  = [(annotation text, "left" | "right"), …] (numbered 1, 2, 3… in the order given)
    """
    fill, stroke, col = tone_colors(d, tone)
    ccx = x + w / 2
    cw = w - 2 * (note_w + 0.34)
    # Size the center box to its content and center it vertically. Stretching
    # it to fill h pushes the text upward, leaving the bottom half looking empty.
    ch = min(h - 0.20, 1.50)
    cyy = y + (h - ch) / 2
    d.shape(ccx - cw / 2, cyy, cw, ch, kind="ROUND_RECTANGLE",
            fill=fill, stroke=stroke)
    d.label(ccx - cw / 2 + 0.12, cyy + 0.20, cw - 0.24, 0.30, center[0],
            size=10, bold=True, align="CENTER", color=col)
    if center[1]:
        d.label(ccx - cw / 2 + 0.12, cyy + 0.54, cw - 0.24, ch - 0.70, center[1],
                size=8.5, align="CENTER", valign="TOP", color=col,
                line_spacing=120)

    sides = {"left": [], "right": []}
    for i, (text, side) in enumerate(notes):
        sides.setdefault(side, []).append((i + 1, text))
    for side, lst in sides.items():
        if not lst:
            continue
        nh = min(0.72, (h - 0.20 - 0.14 * (len(lst) - 1)) / len(lst))
        nx = x if side == "left" else x + w - note_w
        for k, (num, text) in enumerate(lst):
            ny = y + 0.10 + k * (nh + 0.14)
            d.shape(nx if side == "left" else nx + note_w - 0.30,
                    ny + (nh - 0.30) / 2, 0.30, 0.30, kind="ELLIPSE",
                    fill=d.P.primary, stroke=None, text=str(num), size=9,
                    bold=True, color="#FFFFFF")
            tx = nx + 0.38 if side == "left" else nx
            d.label(tx, ny, note_w - 0.38, nh, text, size=8,
                    align="START" if side == "left" else "END",
                    valign="MIDDLE", color=d.P.text, line_spacing=115)
            edge = ccx - cw / 2 if side == "left" else ccx + cw / 2
            anchor = nx + note_w if side == "left" else nx
            # Clamp the connector line's endpoint to the box's height. Letting
            # it extend outside the box would make it point at nothing
            ly = min(max(ny + nh / 2, cyy + 0.12), cyy + ch - 0.12)
            d.line(anchor + (0.06 if side == "left" else -0.06),
                   ny + nh / 2, edge, ly, free=True,   # no dot on the annotation side, since it's just text
                   color=lighten(d.P.primary, 0.60), weight=0.9, dashed=True)
    return y + h


# ---- 13. Metrics row (KPI) ----

def stats(d, x, y, w, items, *, h=0.92, gap=0.20, value_size=22):
    """Lay out large numbers side by side. items = [(value, description, tone), …]

    Use this only for figures with a real source. Don't display estimates prominently.
    """
    n = len(items)
    cw = (w - gap * (n - 1)) / n
    # Shrink the value's font when the box is short. A fixed size would overflow and get clipped
    vh = h * 0.54
    vs = min(value_size, vh * 72.0 / Canvas.LINE_EM)
    for i, (value, cap, tone) in enumerate(items):
        col = tone_solid(d, tone)
        cx = x + i * (cw + gap)
        d.shape(cx, y, cw, h, kind="ROUND_RECTANGLE", fill=lighten(col, 0.90),
                stroke=lighten(col, 0.55))
        d.label(cx + 0.10, y + 0.06, cw - 0.20, vh, value,
                size=vs, bold=True, align="CENTER", valign="MIDDLE", color=col)
        d.label(cx + 0.10, y + h * 0.62, cw - 0.20, h * 0.34, cap, size=8,
                align="CENTER", valign="TOP", color=d.P.muted, line_spacing=115)
    return y + h


# ---- 14. Checklist ----

def checklist(d, x, y, w, items, *, row_h=0.34, gap=0.08, size=9):
    """List of items with state. items = [(text, "done"|"todo"|"warn"), …]"""
    marks = {"done": ("✓", "good"), "todo": ("□", "muted"), "warn": ("!", "warn")}
    for i, (text, state) in enumerate(items):
        glyph, tone = marks.get(state, marks["todo"])
        fill, stroke, col = tone_colors(d, tone)
        ry = y + i * (row_h + gap)
        d.shape(x, ry, row_h, row_h, kind="ROUND_RECTANGLE",
                fill=tone_solid(d, tone) if state != "todo" else "#FFFFFF",
                stroke=None if state != "todo" else lighten(d.P.muted, 0.45),
                text=glyph, size=size, bold=True,
                color="#FFFFFF" if state != "todo" else d.P.muted)
        d.shape(x + row_h + 0.10, ry, w - row_h - 0.10, row_h,
                kind="ROUND_RECTANGLE", fill=fill, stroke=stroke, text=text,
                size=size, color=col, align="START")
    return y + len(items) * (row_h + gap) - gap


# ---- 15. Pipeline (with range highlight) ----

def pipeline(d, x, y, w, steps, *, h=0.80, gap=0.30, highlight=None,
             highlight_note=None, size=8.5):
    """A process flowing left to right. Only the highlight=(start index, end index) range is emphasized.

    Use this to show "which part of the overall flow is ours" within a larger process.
    """
    n = len(steps)
    bw = (w - gap * (n - 1)) / n
    lo, hi = highlight if highlight else (-1, -2)
    for i, s in enumerate(steps):
        own = lo <= i <= hi
        sx = x + i * (bw + gap)
        d.shape(sx, y, bw, h, kind="ROUND_RECTANGLE",
                fill=d.P.primary if own else lighten(d.P.muted, 0.88),
                stroke=None if own else lighten(d.P.muted, 0.50),
                text=s, size=size, bold=own,
                color="#FFFFFF" if own else d.P.text, line_spacing=110)
        if i < n - 1:
            d.arrow(sx + bw + 0.03, y + h / 2, sx + bw + gap - 0.03, y + h / 2,
                    color=d.P.primary, weight=1.5)
    bottom = y + h
    if highlight and highlight_note:
        hx = x + lo * (bw + gap)
        hw = (hi - lo + 1) * bw + (hi - lo) * gap
        d.label(hx, bottom + 0.04, hw, 0.22, highlight_note, size=8, bold=True,
                align="CENTER", valign="TOP", color=d.P.primaryDark)
        bottom += 0.26
    return bottom


# ---- 16. Legend ----

def legend(d, x, y, w, items, *, size=8, h=0.24, gap=0.28, swatch=0.16):
    """Color legend. items = [(color or tone name, label), …], laid out horizontally."""
    cx = x
    for col, label in items:
        if isinstance(col, str) and col.startswith("#"):
            fill, stroke = col, None
        else:
            fill, stroke, _ = tone_colors(d, col)   # show the same fill as the shape
        d.shape(cx, y + (h - swatch) / 2, swatch, swatch, kind="ROUND_RECTANGLE",
                fill=fill, stroke=stroke)
        # Text boxes have inner padding, so add a 1.1x factor and 0.22in to the measured width
        tw = em(label) * size / 72 * 1.10 + 0.22
        d.label(cx + swatch + 0.08, y, tw, h, label, size=size, align="START",
                valign="MIDDLE", color=d.P.muted)
        cx += swatch + 0.08 + tw + gap
    return y + h
