#!/usr/bin/env python3
"""Text measurement shared by the drawing engine, the deck DSL, and the ledgers.

One definition, because three of them disagreeing would mean the auditor, the
author-time helpers, and the slot builders each drawing a different conclusion
about whether a string fits its box.
"""
from __future__ import annotations

import unicodedata
from functools import lru_cache

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
