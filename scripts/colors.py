#!/usr/bin/env python3
"""Color utilities.

Shared by all five of `diagrams` / `charts` / `illustrations` / `patterns` /
`images`. Since those modules import each other, the common color math lives
here to avoid circular imports.

For backward compatibility, the same names are also re-exported from
`diagrams` (`from diagrams import lighten` continues to work as before).
"""
from __future__ import annotations


def _clamp(v: float) -> int:
    return max(0, min(255, int(round(v))))


def mix(hex_a: str, hex_b: str, t: float) -> str:
    """Mix hex_a and hex_b by t (0→a, 1→b)."""
    a = [int(hex_a.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)]
    b = [int(hex_b.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)]
    return "#%02X%02X%02X" % tuple(_clamp(a[i] + (b[i] - a[i]) * t) for i in range(3))


def lighten(hex_color: str, t: float) -> str:
    """Blend toward white. t=0 gives the original color, t=1 gives white."""
    return mix(hex_color, "#FFFFFF", t)


def darken(hex_color: str, t: float) -> str:
    return mix(hex_color, "#000000", t)


def relative_luminance(hex_color: str) -> float:
    ch = []
    for i in (0, 2, 4):
        c = int(hex_color.lstrip("#")[i:i + 2], 16) / 255
        ch.append(c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4)
    return 0.2126 * ch[0] + 0.7152 * ch[1] + 0.0722 * ch[2]


def contrast_ratio(a: str, b: str) -> float:
    l1, l2 = relative_luminance(a), relative_luminance(b)
    return (max(l1, l2) + 0.05) / (min(l1, l2) + 0.05)


def readable_on(bg: str, dark: str = "#0F172A", light: str = "#FFFFFF") -> str:
    """Return whichever text color has higher contrast against the background."""
    return dark if contrast_ratio(bg, dark) >= contrast_ratio(bg, light) else light


class Palette:
    """Build the diagram color set from the template's colorScheme."""

    def __init__(self, colors: dict):
        c = colors
        self.primary = c.get("accent5", "#2673BB")
        self.primaryDark = darken(self.primary, 0.35)
        self.success = c.get("accent1", "#63C045")
        self.danger = c.get("accent2", "#EE2155")
        self.info = c.get("accent3", "#0985FD")
        self.warning = c.get("accent4", "#FFEF24")
        self.text = c.get("dark1", "#0F172A")
        self.muted = c.get("dark2", "#6B7280")
        self.surface = lighten(self.primary, 0.92)
        self.surfaceAlt = c.get("light2", "#F9FAFB")
        self.border = lighten(self.primary, 0.65)
        self.white = "#FFFFFF"
        # Slide background color. Using this color for panels placed behind text
        # blends naturally with both light and dark templates
        self.page = c.get("light1", "#FFFFFF")

    def series(self, n: int) -> list[str]:
        """Return n series colors. Cycles through theme-derived colors in order,
        extending with lightness variants once they run out.

        The order is **fixed** (chart series are always painted in this order;
        never cycled or reordered). This order passed color-vision-deficiency
        validation: a back-to-back primary → info blue pair is indistinguishable
        (ΔE 10.5 < 15), and warning's yellow nearly disappears against white, so
        the sequence is blue → green → cyan → red → dark yellow, with yellow
        darkened specifically for charts (every adjacent pair reaches CVD
        ΔE ≥ 9.2 / normal vision ΔE ≥ 27). Green and dark yellow fall below a
        3:1 contrast ratio against a white background, so charts using them
        must always add a legend and direct labels.
        """
        chart_yellow = "#C7A500"
        base = [self.primary, self.success, self.info, self.danger, chart_yellow]
        out = []
        for i in range(n):
            c = base[i % len(base)]
            round_ = i // len(base)
            out.append(c if round_ == 0 else lighten(c, min(0.55, 0.22 * round_)))
        return out
