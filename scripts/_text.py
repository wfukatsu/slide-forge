#!/usr/bin/env python3
"""Text measurement shared by the drawing engine, the deck DSL, and the ledgers.

One definition, because three of them disagreeing would mean the auditor, the
author-time helpers, and the slot builders each drawing a different conclusion
about whether a string fits its box.
"""
from __future__ import annotations

import math
import unicodedata
from dataclasses import dataclass
from functools import lru_cache
from typing import Callable

# Slides lays Japanese text out on a full-width grid: a CJK character occupies
# a whole cell and a Latin one about half. Widths are therefore counted in
# full-width equivalents ("em"), never in characters — len() is off by 2x on
# ASCII and says nothing useful about how much of a box a string takes.
_WIDE = "WFA"      # East_Asian_Width: Wide, Fullwidth, Ambiguous


@lru_cache(maxsize=8192)
def em(s: str) -> float:
    """Width of *s* in full-width equivalents.

    Memoised: the overlap audit measures the same labels many times over, and
    this is a per-character Unicode lookup.
    """
    return sum(1.0 if unicodedata.east_asian_width(c) in _WIDE else 0.5 for c in s)


def fit_em(text: str, budget: float, *, ellipsis: str = "…") -> str:
    """Truncate *text* to *budget* full-width equivalents, marking the cut.

    Room for the ellipsis is taken out of the budget, so the result is never
    wider than asked for.
    """
    if em(text) <= budget:
        return text
    mark = em(ellipsis)
    kept: list[str] = []
    used = 0.0
    for ch in text:
        if used + em(ch) > budget - mark:
            break
        kept.append(ch)
        used += em(ch)
    return "".join(kept).rstrip() + ellipsis


# ---------------------------------------------------------------------------
# Fitting text to its box
# ---------------------------------------------------------------------------
#
# The Slides API cannot switch a shape's "text fitting" option: `autofitType`
# accepts only NONE on write ("Autofit types other than NONE are not
# supported"), and inserting text resets it to NONE anyway. Text that runs
# past its box is therefore drawn outside it — spilling above and below a
# MIDDLE-anchored box, or upward from a BOTTOM-anchored one — which reads as
# the text being out of place. The fitting done in the editor has to be
# reproduced here, before the requests are sent.

# Slides' built-in left/right inner margin of a text frame (api-notes §14)
TEXT_INSET_X = 0.10
# Noto Sans JP line height, as a multiple of the font size
LINE_EM = 1.45

FIT_MODES = ("shrink", "grow", "none")
DEFAULT_FIT = "shrink"
# How far fitting may go before it gives up and leaves the audit to report it
MIN_FIT_INSET = 0.03        # in, per side
MIN_FONT_RATIO = 0.7        # of the requested size
MIN_FONT_PT = 8.0
# A deck built for print (spec "density": "print" — a read-alone handout or
# a proposal read on paper) is read at arm's length, where 8, 9 and 10pt stay
# legible. Fitting there may go all the way down to this floor regardless of
# MIN_FONT_RATIO; a projected deck keeps the ratio.
PRINT_MIN_FONT_PT = 8.0
DENSITIES = ("print", "presentation")
FIT_STEP_PT = 0.5
FIT_STEP_INSET = 0.01
# Share of the column fitting counts as usable. Slides wraps a line that
# exactly fills its column: measured in a 2.6in box at 12pt (15.0 full-width
# characters by the formula), 14 fit and the 15th wraps — the same in a
# TEXT_BOX, RECTANGLE and ROUND_RECTANGLE, in Noto Sans JP and Arial. The
# audits keep the plain formula; fitting plans against this narrower column
# so what it declares fitted really does.
FIT_WIDTH = 0.95


def wrapped_lines(text: str, width_in: float, size: float) -> int:
    """Lines *text* takes in a column *width_in* wide at *size* pt, for fitting.

    Counts against FIT_WIDTH of the column, so a line that would exactly fill
    it counts as wrapping, as it does in Slides.
    """
    per = max(width_in, 0.01) * FIT_WIDTH * 72.0 / size
    n = 0
    for ln in text.split("\n"):
        e = em(ln)
        n += max(1, int(e / per) + (1 if e % per else 0))
    return n


def text_height(text: str, w: float, size: float, *, line_spacing: float = 100,
                inset: float = TEXT_INSET_X, line_em: float = LINE_EM) -> float:
    """Height in inches *text* needs in a box *w* wide with *inset* per side."""
    return (wrapped_lines(text, w - inset * 2, size) * size * line_em
            * (line_spacing / 100.0) / 72.0)


def min_font_size(size: float, floor: float | None = None) -> float:
    """The smallest size shrinking may reach from *size*.

    An explicit *floor* wins; otherwise 70% of the size, but never below 8pt,
    rounded up onto the 0.5pt grid shrinking steps along. A size already
    under the floor is left alone rather than grown.
    """
    if floor is None:
        floor = math.ceil(max(size * MIN_FONT_RATIO, MIN_FONT_PT) / FIT_STEP_PT) * FIT_STEP_PT
    return min(size, floor)


@dataclass(frozen=True)
class Fit:
    size: float
    inset: float
    fits: bool


def fit_box(need: Callable[[float, float], float], h: float, size: float,
            inset: float = TEXT_INSET_X, *, min_size: float | None = None,
            min_inset: float = MIN_FIT_INSET, slack: float = 0.0) -> Fit:
    """Pick the font size and inner margin that make text fit a box *h* tall.

    *need(size, inset)* returns the height in inches the text takes. Text that
    already fits comes back unchanged. Otherwise the margin is tightened
    first — it costs nothing visible — and the font shrinks in 0.5pt steps
    only once the margin alone is not enough. At each size the widest margin
    that fits is kept. When even the smallest size and margin do not fit,
    those are returned with ``fits=False``: the best that can be done, and
    the caller's audit still reports it.
    """
    if need(size, inset) <= h + slack:
        return Fit(size, inset, True)
    floor_inset = min(min_inset, inset)
    insets = []
    i = inset
    while i > floor_inset + 1e-9:
        insets.append(round(i, 4))
        i -= FIT_STEP_INSET
    insets.append(floor_inset)

    lo = min_font_size(size, min_size)
    sizes = [size]
    s = math.floor(size / FIT_STEP_PT - 1e-6) * FIT_STEP_PT
    while s > lo + 1e-9:
        sizes.append(s)
        s -= FIT_STEP_PT
    if lo < size:
        sizes.append(lo)

    for s in sizes:
        for i in insets:
            if need(s, i) <= h + slack:
                return Fit(s, i, True)
    return Fit(sizes[-1], floor_inset, False)


def grow_box(y: float, h: float, need: float, valign: str) -> tuple[float, float]:
    """Grow a box to *need* tall, keeping the edge its text is anchored to.

    Reproduces "resize shape to fit text": a TOP-anchored box grows down, a
    BOTTOM-anchored one up, a MIDDLE one both ways. A box is never shrunk.
    """
    if need <= h:
        return y, h
    extra = need - h
    if valign == "MIDDLE":
        y -= extra / 2
    elif valign in ("BOTTOM", "END"):
        y -= extra
    return y, need


def describe_fit(size: float, inset: float, fit: Fit) -> str:
    """What fitting changed, e.g. "14→11.5pt, inset 0.10→0.04in" ("" if nothing)."""
    parts = []
    if fit.size != size:
        parts.append(f"{size:g}→{fit.size:g}pt")
    if abs(fit.inset - inset) > 1e-9:
        parts.append(f"inset {inset:.2f}→{fit.inset:.2f}in")
    return ", ".join(parts)
