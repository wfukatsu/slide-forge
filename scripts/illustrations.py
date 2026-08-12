#!/usr/bin/env python3
"""Diagram-style "image diagrams" drawn with shapes only.

A mixin added to `diagrams.Canvas`. Needs no API key or network access, and
pulls its colors from the template's palette, so unlike AI-generated images
it produces **the exact same picture every time**.

There are two layers.

1. **Pictograms** ... parts that represent a single meaning as one picture:
   person, server, DB, cloud, key, etc. Used via `icon()` / `icon_row()` /
   `icon_flow()`.
2. **Metaphor diagrams** ... diagrams that show the shape of a relationship
   itself, such as a pyramid, funnel, iceberg, or balance scale. See
   `pyramid()` / `funnel()` / `iceberg()` / `balance()`, etc.

        d = Canvas(deck, slide_id, template)
        d.icon_flow(0.7, 1.2, 8.6, [("person", "利用者"), ("browser", "アプリ"),
                                    ("server", "API"), ("database", "台帳")])
        b = d.pyramid(1.6, 2.4, 6.8, 2.4, ["経営指標", "業務指標", "システム指標"])

All diagrams follow the same stacking convention as `diagrams` and
**return the bottom y of the drawn area**. Place the next block starting
from that return value.

After drawing a diagram, always call `audit_overlaps()` / `audit_text_fit()`.
Pictogram captions can collide with each other when labels are long, and
this can be caught at the coordinate stage.
"""
from __future__ import annotations

import math

from colors import darken, lighten, readable_on
from _i18n import t, register

register({
    "icon_flow: pictograms are too large to leave arrow gaps (w={w}, {n} items, "
    "size={size} -> gap {gap:.3f}in). Reduce size to {max_size:.2f} or less, "
    "widen w, or use icon_row (no arrows)":
        "icon_flow: 絵が大きすぎて矢印の隙間がありません（w={w}, {n} 個, "
        "size={size} → 隙間 {gap:.3f}in）。size を {max_size:.2f} 以下にするか、"
        "w を広げるか、矢印の要らない icon_row を使うこと",
    "Unknown pictogram '{name}'. Available: {available}":
        "未知のピクトグラム '{name}'。利用可能: {available}",
    "venn supports exactly 2 or 3 labels": "venn は 2 個か 3 個のラベルにのみ対応します",
    "quadrants takes exactly 4 items (top-left, top-right, bottom-left, bottom-right)":
        "quadrants は 4 個（左上・右上・左下・右下）",
    "comparison needs at least 2 columns, got {n}":
        "comparison は 2 列以上必要です（{n} 列）",
    "w={w} leaves {pw:.2f}in per column for {n} columns; "
    "use fewer columns or a table":
        "w={w} では {n} 列で 1 列 {pw:.2f}in しか取れません。"
        "列を減らすか表に切り替えてください",
})

# List of pictograms. Values that can be passed to icon()'s name.
ICONS = (
    "person", "people", "server", "database", "cloud", "document", "documents",
    "gear", "lock", "shield", "browser", "mobile", "bot", "chart", "clock",
    "check", "cross", "warning", "mail", "key", "network", "code", "stack",
    "folder", "bulb", "search", "sync", "flag", "coin", "chip",
    "calendar", "pin",
)


class IllustrationMixin:
    """Mixin that adds pictograms and metaphor diagrams to `Canvas`."""

    # ---------------- Pictograms ----------------

    def icon(self, name: str, x: float, y: float, size: float = 0.8, *,
             color: str | None = None, label: str | None = None,
             label_size: float = 9, label_w: float | None = None,
             label_gap: float = 0.05, bold_label: bool = False) -> float:
        """Draws a pictogram in a size×size square. Returns the bottom y.

        If label is passed, a center-aligned caption is placed below the
        picture. By default the caption width is 2x size (wider than the
        picture). Specify label_w explicitly when placing icons side by side.
        """
        if name not in ICONS:
            raise ValueError(t("Unknown pictogram '{name}'. Available: {available}",
                               name=name, available=list(ICONS)))
        c = color or self.P.primary
        getattr(self, f"_icon_{name}")(x, y, size, c)
        bottom = y + size
        if label:
            lw = label_w or size * 2
            lines = label.count("\n") + 1
            lh = max(0.24, lines * label_size * 1.45 / 72 + 0.06)
            self.label(x + size / 2 - lw / 2, bottom + label_gap, lw, lh, label,
                       size=label_size, align="CENTER", valign="TOP",
                       color=self.P.text, bold=bold_label, line_spacing=110)
            bottom += label_gap + lh
        return bottom

    def icon_row(self, x: float, y: float, w: float, items, *, size: float = 0.82,
                 color=None, label_size: float = 9.5, gap: float | None = None) -> float:
        """Lays pictograms out in an evenly spaced row. items is a name or a (name, label) tuple."""
        n = len(items)
        cell = w / n
        bottom = y
        for i, item in enumerate(items):
            name, label = item if isinstance(item, (tuple, list)) else (item, None)
            c = color[i] if isinstance(color, (list, tuple)) else color
            cx = x + i * cell + cell / 2
            bottom = max(bottom, self.icon(
                name, cx - size / 2, y, size, color=c, label=label,
                label_size=label_size, label_w=cell - (gap if gap else 0.16)))
        return bottom

    def icon_flow(self, x: float, y: float, w: float, items, *, size: float = 0.82,
                  color=None, label_size: float = 9.5, arrow_color=None) -> float:
        """Flow diagram connecting pictograms with arrows, e.g. "User → App → DB".

        Arrows are only drawn in the gap between pictures (never overlapping
        a picture).

        **If the pictures are too large, the gap disappears.** Drawing it
        anyway would put the arrow's end point to the left of its start
        point, drawing what should be a right-pointing arrow backwards.
        Neither the API nor the audit catches this (since it's an
        `_anchored` line), so we stop it here instead.
        """
        n = len(items)
        cell = w / n
        if n > 1 and cell - size - 0.20 < 0.06:
            raise ValueError(t(
                "icon_flow: pictograms are too large to leave arrow gaps "
                "(w={w}, {n} items, size={size} -> gap {gap:.3f}in). Reduce "
                "size to {max_size:.2f} or less, widen w, or use icon_row "
                "(no arrows)",
                w=w, n=n, size=size, gap=cell - size - 0.20,
                max_size=cell - 0.26))
        bottom = y
        for i, item in enumerate(items):
            name, label = item if isinstance(item, (tuple, list)) else (item, None)
            c = color[i] if isinstance(color, (list, tuple)) else color
            cx = x + i * cell + cell / 2
            bottom = max(bottom, self.icon(
                name, cx - size / 2, y, size, color=c, label=label,
                label_size=label_size, label_w=cell - 0.5))
            if i < n - 1:
                ay = y + size / 2
                self.arrow(cx + size / 2 + 0.10, ay, cx + cell - size / 2 - 0.10, ay,
                           color=arrow_color or self.P.primary, weight=1.5,
                           _anchored=True)
        return bottom

    def icon_grid(self, x: float, y: float, w: float, items, *, cols: int = 4,
                  size: float = 0.72, row_gap: float = 0.30, color=None,
                  label_size: float = 9) -> float:
        """Lays pictograms out in a grid. items is a name or a (name, label) tuple."""
        cell = w / cols
        bottom = y
        row_top = y
        for i, item in enumerate(items):
            if i and i % cols == 0:
                row_top = bottom + row_gap
            name, label = item if isinstance(item, (tuple, list)) else (item, None)
            c = color[i] if isinstance(color, (list, tuple)) else color
            cx = x + (i % cols) * cell + cell / 2
            bottom = max(bottom if i % cols else row_top, self.icon(
                name, cx - size / 2, row_top, size, color=c, label=label,
                label_size=label_size, label_w=cell - 0.14))
        return bottom

    # ---- Individual pictograms. All fit inside an (x, y, s, c) square ----

    def _icon_person(self, x, y, s, c):
        self.shape(x + 0.34 * s, y + 0.04 * s, 0.32 * s, 0.32 * s,
                   kind="ELLIPSE", fill=c, stroke=None)
        self.shape(x + 0.14 * s, y + 0.44 * s, 0.72 * s, 0.46 * s,
                   kind="ROUND_2_SAME_RECTANGLE", fill=c, stroke=None)

    def _icon_people(self, x, y, s, c):
        soft = lighten(c, 0.55)
        self._icon_person(x + 0.26 * s, y, 0.74 * s, soft)
        self._icon_person(x, y + 0.10 * s, 0.74 * s, c)

    def _icon_server(self, x, y, s, c):
        soft = lighten(c, 0.84)
        for i in range(3):
            top = y + 0.08 * s + i * 0.30 * s
            self.shape(x + 0.06 * s, top, 0.88 * s, 0.22 * s,
                       kind="ROUND_RECTANGLE", fill=soft, stroke=c, stroke_weight=1.1)
            self.shape(x + 0.14 * s, top + 0.07 * s, 0.08 * s, 0.08 * s,
                       kind="ELLIPSE", fill=c, stroke=None)

    def _icon_database(self, x, y, s, c):
        self.shape(x + 0.12 * s, y + 0.06 * s, 0.76 * s, 0.88 * s,
                   kind="FLOW_CHART_MAGNETIC_DISK", fill=lighten(c, 0.82),
                   stroke=c, stroke_weight=1.2)

    def _icon_cloud(self, x, y, s, c):
        self.shape(x, y + 0.16 * s, s, 0.66 * s, kind="CLOUD",
                   fill=lighten(c, 0.84), stroke=c, stroke_weight=1.2)

    def _icon_document(self, x, y, s, c):
        self.shape(x + 0.18 * s, y + 0.04 * s, 0.64 * s, 0.88 * s,
                   kind="FLOW_CHART_DOCUMENT", fill="#FFFFFF", stroke=c,
                   stroke_weight=1.2)
        for i in range(3):
            ly = y + 0.28 * s + i * 0.16 * s
            self.line(x + 0.30 * s, ly, x + 0.70 * s, ly,
                      color=lighten(c, 0.4), weight=1.0, free=True)

    def _icon_documents(self, x, y, s, c):
        self.shape(x + 0.10 * s, y + 0.04 * s, 0.80 * s, 0.88 * s,
                   kind="FLOW_CHART_MULTIDOCUMENT", fill="#FFFFFF", stroke=c,
                   stroke_weight=1.2)

    def _icon_gear(self, x, y, s, c):
        self.shape(x + 0.02 * s, y + 0.02 * s, 0.96 * s, 0.96 * s,
                   kind="STAR_12", fill=c, stroke=None)
        self.shape(x + 0.34 * s, y + 0.34 * s, 0.32 * s, 0.32 * s,
                   kind="ELLIPSE", fill="#FFFFFF", stroke=None)

    def _icon_lock(self, x, y, s, c):
        # The shackle is a donut (ring). The bottom half is hidden behind
        # the body, so it reads as a clean U shape.
        # Substituting a round rectangle doesn't have enough radius and
        # produces a "square shackle"
        self.shape(x + 0.27 * s, y + 0.04 * s, 0.46 * s, 0.52 * s,
                   kind="DONUT", fill=c, stroke=None)
        self.shape(x + 0.12 * s, y + 0.38 * s, 0.76 * s, 0.54 * s,
                   kind="ROUND_RECTANGLE", fill=c, stroke=None)

    def _icon_shield(self, x, y, s, c):
        self.shape(x + 0.10 * s, y + 0.05 * s, 0.80 * s, 0.90 * s,
                   kind="PENTAGON", fill=lighten(c, 0.55), stroke=c,
                   stroke_weight=1.5, rotation=180)

    def _icon_browser(self, x, y, s, c):
        self.shape(x + 0.02 * s, y + 0.14 * s, 0.96 * s, 0.72 * s,
                   kind="RECTANGLE", fill="#FFFFFF", stroke=c, stroke_weight=1.2)
        self.shape(x + 0.02 * s, y + 0.14 * s, 0.96 * s, 0.16 * s,
                   kind="RECTANGLE", fill=c, stroke=None)
        for i in range(3):
            self.shape(x + 0.08 * s + i * 0.10 * s, y + 0.19 * s,
                       0.06 * s, 0.06 * s, kind="ELLIPSE", fill="#FFFFFF", stroke=None)

    def _icon_mobile(self, x, y, s, c):
        self.shape(x + 0.28 * s, y + 0.02 * s, 0.44 * s, 0.96 * s,
                   kind="ROUND_RECTANGLE", fill="#FFFFFF", stroke=c, stroke_weight=1.4)
        self.shape(x + 0.33 * s, y + 0.11 * s, 0.34 * s, 0.68 * s,
                   kind="RECTANGLE", fill=lighten(c, 0.82), stroke=None)

    def _icon_bot(self, x, y, s, c):
        self.line(x + 0.5 * s, y + 0.04 * s, x + 0.5 * s, y + 0.20 * s,
                  color=c, weight=1.4, free=True)
        self.shape(x + 0.43 * s, y, 0.14 * s, 0.14 * s, kind="ELLIPSE",
                   fill=c, stroke=None)
        self.shape(x + 0.10 * s, y + 0.20 * s, 0.80 * s, 0.62 * s,
                   kind="ROUND_RECTANGLE", fill=lighten(c, 0.82), stroke=c,
                   stroke_weight=1.2)
        for dx in (0.28, 0.58):
            self.shape(x + dx * s, y + 0.40 * s, 0.14 * s, 0.14 * s,
                       kind="ELLIPSE", fill=c, stroke=None)

    def _icon_chart(self, x, y, s, c):
        for i, hr in enumerate((0.38, 0.62, 0.88)):
            bw = 0.22 * s
            bx = x + 0.12 * s + i * 0.28 * s
            self.shape(bx, y + (0.92 - hr * 0.84) * s, bw, hr * 0.84 * s,
                       kind="RECTANGLE",
                       fill=c if i == 2 else lighten(c, 0.45), stroke=None)
        self.line(x + 0.06 * s, y + 0.93 * s, x + 0.94 * s, y + 0.93 * s,
                  color=lighten(c, 0.3), weight=1.2, free=True)

    def _icon_clock(self, x, y, s, c):
        self.shape(x + 0.04 * s, y + 0.04 * s, 0.92 * s, 0.92 * s,
                   kind="ELLIPSE", fill="#FFFFFF", stroke=c, stroke_weight=1.8)
        self.line(x + 0.5 * s, y + 0.5 * s, x + 0.5 * s, y + 0.22 * s,
                  color=c, weight=1.6, free=True)
        self.line(x + 0.5 * s, y + 0.5 * s, x + 0.72 * s, y + 0.58 * s,
                  color=c, weight=1.6, free=True)

    def _icon_check(self, x, y, s, c):
        col = c if c != self.P.primary else self.P.success
        self.shape(x + 0.04 * s, y + 0.04 * s, 0.92 * s, 0.92 * s, kind="ELLIPSE",
                   fill=col, stroke=None, text="✓", color="#FFFFFF",
                   size=max(8, s * 46), bold=True)

    def _icon_cross(self, x, y, s, c):
        col = c if c != self.P.primary else self.P.danger
        self.shape(x + 0.04 * s, y + 0.04 * s, 0.92 * s, 0.92 * s, kind="ELLIPSE",
                   fill=col, stroke=None, text="✕", color="#FFFFFF",
                   size=max(8, s * 40), bold=True)

    def _icon_warning(self, x, y, s, c):
        col = c if c != self.P.primary else self.P.warning
        self.shape(x, y + 0.06 * s, s, 0.88 * s, kind="TRIANGLE", fill=col,
                   stroke=darken(col, 0.25), stroke_weight=1.2, text="!",
                   color=readable_on(col), size=max(8, s * 30), bold=True,
                   valign="BOTTOM")

    def _icon_mail(self, x, y, s, c):
        self.shape(x + 0.04 * s, y + 0.20 * s, 0.92 * s, 0.60 * s,
                   kind="RECTANGLE", fill="#FFFFFF", stroke=c, stroke_weight=1.3)
        self.line(x + 0.04 * s, y + 0.20 * s, x + 0.50 * s, y + 0.56 * s,
                  color=c, weight=1.3, free=True)
        self.line(x + 0.50 * s, y + 0.56 * s, x + 0.96 * s, y + 0.20 * s,
                  color=c, weight=1.3, free=True)

    def _icon_key(self, x, y, s, c):
        self.shape(x + 0.02 * s, y + 0.28 * s, 0.44 * s, 0.44 * s,
                   kind="DONUT", fill=c, stroke=None)
        self.shape(x + 0.42 * s, y + 0.44 * s, 0.54 * s, 0.12 * s,
                   kind="RECTANGLE", fill=c, stroke=None)
        for dx in (0.66, 0.84):
            self.shape(x + dx * s, y + 0.56 * s, 0.09 * s, 0.16 * s,
                       kind="RECTANGLE", fill=c, stroke=None)

    def _icon_network(self, x, y, s, c):
        cx, cy = x + 0.5 * s, y + 0.5 * s
        pts = [(cx, y + 0.08 * s), (x + 0.10 * s, y + 0.84 * s),
               (x + 0.90 * s, y + 0.84 * s)]
        for px, py in pts:
            self.line(cx, cy, px, py, color=lighten(c, 0.35), weight=1.2, free=True)
        for px, py in pts:
            self.shape(px - 0.10 * s, py - 0.10 * s, 0.20 * s, 0.20 * s,
                       kind="ELLIPSE", fill=lighten(c, 0.35), stroke=None)
        self.shape(cx - 0.15 * s, cy - 0.15 * s, 0.30 * s, 0.30 * s,
                   kind="ELLIPSE", fill=c, stroke=None)

    def _icon_code(self, x, y, s, c):
        self.shape(x + 0.02 * s, y + 0.14 * s, 0.96 * s, 0.72 * s,
                   kind="ROUND_RECTANGLE", fill=c, stroke=None, text="</>",
                   color="#FFFFFF", size=max(7, s * 20), bold=True)

    def _icon_stack(self, x, y, s, c):
        for i in range(3):
            self.shape(x + 0.04 * s, y + 0.14 * s + i * 0.26 * s, 0.92 * s, 0.22 * s,
                       kind="PARALLELOGRAM",
                       fill=lighten(c, 0.15 + 0.28 * i), stroke=None)

    def _icon_folder(self, x, y, s, c):
        self.shape(x + 0.06 * s, y + 0.16 * s, 0.36 * s, 0.12 * s,
                   kind="RECTANGLE", fill=c, stroke=None)
        self.shape(x + 0.04 * s, y + 0.24 * s, 0.92 * s, 0.60 * s,
                   kind="ROUND_RECTANGLE", fill=lighten(c, 0.72), stroke=c,
                   stroke_weight=1.2)

    def _icon_bulb(self, x, y, s, c):
        glow = lighten(self.P.warning, 0.25)
        self.shape(x + 0.22 * s, y + 0.04 * s, 0.56 * s, 0.56 * s,
                   kind="ELLIPSE", fill=glow, stroke=c, stroke_weight=1.2)
        self.shape(x + 0.36 * s, y + 0.58 * s, 0.28 * s, 0.14 * s,
                   kind="RECTANGLE", fill=c, stroke=None)
        self.shape(x + 0.39 * s, y + 0.74 * s, 0.22 * s, 0.10 * s,
                   kind="RECTANGLE", fill=c, stroke=None)

    def _icon_search(self, x, y, s, c):
        self.line(x + 0.62 * s, y + 0.62 * s, x + 0.94 * s, y + 0.94 * s,
                  color=c, weight=3.0, free=True)
        self.shape(x + 0.04 * s, y + 0.04 * s, 0.66 * s, 0.66 * s,
                   kind="DONUT", fill=c, stroke=None)

    def _icon_sync(self, x, y, s, c):
        self.shape(x + 0.06 * s, y + 0.06 * s, 0.88 * s, 0.88 * s,
                   kind="DONUT", fill=lighten(c, 0.25), stroke=None)
        self.shape(x + 0.72 * s, y - 0.02 * s, 0.26 * s, 0.24 * s,
                   kind="TRIANGLE", fill=c, stroke=None, rotation=90)
        self.shape(x + 0.02 * s, y + 0.78 * s, 0.26 * s, 0.24 * s,
                   kind="TRIANGLE", fill=c, stroke=None, rotation=270)

    def _icon_calendar(self, x, y, s, c):
        # 2 binder rings + body + header band + date dots
        for rx in (0.24, 0.70):
            self.shape(x + rx * s, y + 0.02 * s, 0.06 * s, 0.16 * s,
                       kind="RECTANGLE", fill=darken(c, 0.2), stroke=None)
        self.shape(x + 0.06 * s, y + 0.10 * s, 0.88 * s, 0.84 * s,
                   kind="ROUND_RECTANGLE", fill="#FFFFFF", stroke=c,
                   stroke_weight=1.8)
        self.shape(x + 0.06 * s, y + 0.10 * s, 0.88 * s, 0.24 * s,
                   kind="RECTANGLE", fill=c, stroke=None)
        for row in range(2):
            for col in range(3):
                self.shape(x + (0.20 + 0.24 * col) * s,
                           y + (0.46 + 0.22 * row) * s, 0.10 * s, 0.10 * s,
                           kind="RECTANGLE", fill=lighten(c, 0.55), stroke=None)

    def _icon_pin(self, x, y, s, c):
        # Map pin: round head + downward-pointing leg + white center
        self.shape(x + 0.30 * s, y + 0.50 * s, 0.40 * s, 0.44 * s,
                   kind="TRIANGLE", fill=c, stroke=None, rotation=180)
        self.shape(x + 0.18 * s, y + 0.04 * s, 0.64 * s, 0.64 * s,
                   kind="ELLIPSE", fill=c, stroke=None)
        self.shape(x + 0.40 * s, y + 0.24 * s, 0.20 * s, 0.20 * s,
                   kind="ELLIPSE", fill="#FFFFFF", stroke=None)

    def _icon_flag(self, x, y, s, c):
        self.shape(x + 0.16 * s, y + 0.04 * s, 0.07 * s, 0.92 * s,
                   kind="RECTANGLE", fill=darken(c, 0.2), stroke=None)
        self.shape(x + 0.23 * s, y + 0.08 * s, 0.60 * s, 0.40 * s,
                   kind="RIGHT_TRIANGLE", fill=c, stroke=None, rotation=180)

    def _icon_coin(self, x, y, s, c):
        self.shape(x + 0.06 * s, y + 0.06 * s, 0.88 * s, 0.88 * s, kind="ELLIPSE",
                   fill=lighten(self.P.warning, 0.2), stroke=darken(self.P.warning, 0.3),
                   stroke_weight=1.4, text="¥", color=darken(self.P.warning, 0.5),
                   size=max(8, s * 32), bold=True)

    def _icon_chip(self, x, y, s, c):
        for i in range(4):
            ly = y + 0.28 * s + i * 0.16 * s
            self.line(x + 0.02 * s, ly, x + 0.20 * s, ly, color=c, weight=1.4, free=True)
            self.line(x + 0.80 * s, ly, x + 0.98 * s, ly, color=c, weight=1.4, free=True)
        self.shape(x + 0.18 * s, y + 0.18 * s, 0.64 * s, 0.64 * s,
                   kind="ROUND_RECTANGLE", fill=lighten(c, 0.72), stroke=c,
                   stroke_weight=1.3)
        self.shape(x + 0.34 * s, y + 0.34 * s, 0.32 * s, 0.32 * s,
                   kind="RECTANGLE", fill=c, stroke=None)

    # ---------------- Metaphor diagrams ----------------

    # Amount (in inches) parts overlap by, so seams don't show background-color streaks
    _SEAM = 0.01

    def _taper(self, cx, y, h, w_top, w_bot, fill, *, alpha=1.0) -> None:
        """Draws an isosceles trapezoid with top width w_top and bottom
        width w_bot, at exactly the specified slope.

        **Slides' `TRAPEZOID` shape can't be used.** Its top-edge inset is
        fixed at "display height × 0.25" and can't be changed via width or
        scaleY (verified empirically), which makes it unsuitable for
        diagrams where the top and bottom widths must be chosen explicitly
        (pyramid, funnel). Stacking TRAPEZOID shapes directly also makes the
        slope change from step to step, producing a jagged outline.

        So instead this draws 3 parts: a center rectangle plus a right
        triangle on each side. RIGHT_TRIANGLE has its right angle at the
        bottom-left by default, so flip_x / flip_y are used to produce the
        corner orientation needed.
        """
        inner = min(w_top, w_bot)
        wedge = abs(w_bot - w_top) / 2
        s = self._SEAM
        if inner > 0:
            self.shape(cx - inner / 2 - s, y, inner + s * 2, h, kind="RECTANGLE",
                       fill=fill, stroke=None, alpha=alpha)
        if wedge < 0.01:
            return
        down = w_bot > w_top          # bottom wider = pyramid; the solid part is at the bottom
        # Left wedge: the solid part faces the center (right). If wider at
        # the bottom, the right angle sits bottom-right; if wider at the
        # top, top-right
        self.shape(cx - max(w_top, w_bot) / 2, y, wedge + s, h,
                   kind="RIGHT_TRIANGLE", fill=fill, stroke=None, alpha=alpha,
                   flip_x=True, flip_y=not down)
        # Right wedge: the solid part faces the center (left)
        self.shape(cx + inner / 2 - s, y, wedge + s, h,
                   kind="RIGHT_TRIANGLE", fill=fill, stroke=None, alpha=alpha,
                   flip_y=not down)

    def pyramid(self, x, y, w, h, levels, *, colors=None, size=12,
                gap=0.04, captions=None) -> float:
        """Hierarchy (fewer / higher-ranked toward the top). levels are
        labels ordered from top to bottom. Returns the bottom y.

        If captions is passed, supplementary text is placed to the right of
        each level. This uses space outside x + w, so keep w narrower when
        using captions.

        The trapezoid is rotated 180 degrees to narrow the top edge.
        **Text is not embedded in the shape but overlaid separately** (since
        rotating would flip the text upside down too).
        """
        n = len(levels)
        cols = colors or [lighten(self.P.primary, 0.55 * i / max(n - 1, 1))
                          for i in range(n)]
        lh = (h - gap * (n - 1)) / n
        cx = x + w / 2
        for i, text in enumerate(levels):
            top = y + i * (lh + gap)
            # Widens linearly from a 0-width apex. Since each level's top
            # width equals the level above's bottom width, the slope stays
            # consistent across levels and the outline forms a straight line
            top_w = w * i / n
            bot_w = w * (i + 1) / n
            fill = cols[i] if not isinstance(cols, str) else cols
            if i == 0:
                self.shape(cx - bot_w / 2, top, bot_w, lh, kind="TRIANGLE",
                           fill=fill, stroke=None)
            else:
                self._taper(cx, top, lh, top_w, bot_w, fill)
            # The apex level's fill is narrow, so the text is placed toward the bottom
            if i == 0:
                self.label(cx - w / 2, top + lh - 0.30, w, 0.30, text, size=size,
                           align="CENTER", valign="MIDDLE", bold=True,
                           color=readable_on(fill))
            else:
                self.label(cx - top_w / 2, top, top_w, lh, text, size=size,
                           align="CENTER", valign="MIDDLE", bold=True,
                           color=readable_on(fill))
            if captions and i < len(captions) and captions[i]:
                self.label(x + w + 0.16, top, max(1.2, w * 0.42), lh, captions[i],
                           size=max(8, size - 2), align="START", valign="MIDDLE",
                           color=self.P.muted, line_spacing=110)
        return y + h

    def funnel(self, x, y, w, h, stages, *, size=12, gap=0.06,
               value_w=1.5) -> float:
        """Narrowing funnel (wide at the top, narrow at the bottom). stages
        is (label, displayed value) or a plain string.

        When displaying a value, that area uses the space to the right of
        x + w.
        """
        n = len(stages)
        lh = (h - gap * (n - 1)) / n
        cx = x + w / 2
        narrow = 0.62               # what fraction to taper by, down to the bottom level
        for i, st in enumerate(stages):
            label, value = st if isinstance(st, (tuple, list)) else (st, None)
            top = y + i * (lh + gap)
            # Each level's top width equals the level above's bottom width,
            # so the outline connects in a straight line
            top_w = w * (1 - narrow * i / n)
            bot_w = w * (1 - narrow * (i + 1) / n)
            fill = lighten(self.P.primary, 0.62 * i / max(n - 1, 1))
            self._taper(cx, top, lh, top_w, bot_w, fill)
            self.label(cx - bot_w / 2, top, bot_w, lh, label, size=size,
                       align="CENTER", valign="MIDDLE", bold=True,
                       color=readable_on(fill))
            if value:
                self.label(x + w + 0.14, top, value_w, lh, value, size=size,
                           align="START", valign="MIDDLE", color=self.P.primary,
                           bold=True)
        return y + h

    def venn(self, x, y, w, h, sets, *, center=None, size=11, alpha=0.55) -> float:
        """Overlap diagram. sets is 2 or 3 labels. center is the label for the shared intersection."""
        n = len(sets)
        if n not in (2, 3):
            raise ValueError(t("venn supports exactly 2 or 3 labels"))
        cols = [self.P.primary, self.P.info, self.P.success][:n]
        if n == 2:
            r = min(h, w * 0.62) / 2
            centers = [(x + w / 2 - r * 0.62, y + h / 2), (x + w / 2 + r * 0.62, y + h / 2)]
        else:
            r = min(h * 0.58, w * 0.42) / 2 * 1.35
            cx, cy = x + w / 2, y + h / 2 + r * 0.16
            centers = [(cx, cy - r * 0.62),
                       (cx - r * 0.60, cy + r * 0.46),
                       (cx + r * 0.60, cy + r * 0.46)]
        for (ccx, ccy), col in zip(centers, cols):
            self.shape(ccx - r, ccy - r, r * 2, r * 2, kind="ELLIPSE",
                       fill=col, stroke=None, alpha=alpha)
        # Labels go outside the circles. Overlaying them on the circle
        # makes them hard to read through the alpha blending.
        # Clamp the final position to [x, x+w] so pushing them outward
        # doesn't overflow the frame
        lw = min(1.7, w * 0.46)
        for (ccx, ccy), label, col in zip(centers, sets, cols):
            out_x, out_y = ccx - x - w / 2, ccy - y - h / 2
            lx = ccx + (r * 0.98 if out_x > 0 else -r * 0.98 if out_x < 0 else 0)
            ly = ccy + (r * 0.98 if out_y >= 0 else -r * 1.28)
            lx = min(max(lx - lw / 2, x), x + w - lw)
            ly = min(max(ly - 0.17, y), y + h - 0.34)
            self.label(lx, ly, lw, 0.34, label, size=size, bold=True,
                       align="CENTER", valign="MIDDLE", color=darken(col, 0.25))
        if center:
            mx = sum(c[0] for c in centers) / n
            my = sum(c[1] for c in centers) / n
            # The overlap is pale, so white text would get lost; use a dark text color instead
            self.label(mx - 0.75, my - 0.15, 1.5, 0.3, center, size=size - 1,
                       align="CENTER", valign="MIDDLE", bold=True,
                       color=darken(self.P.primary, 0.45))
        return y + h

    def iceberg(self, x, y, w, h, above, below, *, above_title="見えている部分",
                below_title="見えていない部分", size=10, art_ratio=0.44) -> float:
        """Iceberg (the visible sliver above vs. the bulk hidden below the
        waterline). above/below are lists of strings.

        The picture occupies the left art_ratio of the width, with
        explanatory text on the right. The sea is only painted within the
        picture's area, so the text on the right never sits on top of the
        blue and become hard to read.
        """
        art_w = w * art_ratio
        water = y + h * 0.30
        sea = lighten(self.P.info, 0.82)
        self.shape(x, water, art_w, (y + h) - water, kind="RECTANGLE",
                   fill=sea, stroke=None)
        cx = x + art_w / 2
        peak_w = art_w * 0.52
        self.shape(cx - peak_w / 2, y, peak_w, water - y, kind="TRIANGLE",
                   fill=lighten(self.P.primary, 0.30), stroke=None)
        # Below the waterline: wide at top, narrowing downward = a trapezoid rotated 180 degrees
        self.shape(cx - art_w * 0.44, water, art_w * 0.88, (y + h) - water - 0.06,
                   kind="TRAPEZOID", fill=lighten(self.P.primary, 0.60),
                   stroke=None, rotation=180)
        self.line(x, water, x + art_w, water, color=self.P.info, weight=1.8,
                  free=True)

        tx = x + art_w + 0.30
        tw = w - art_w - 0.30
        self.label(tx, y, tw, 0.28, above_title, size=size + 1, bold=True,
                   align="START", color=self.P.primary)
        self.label(tx, y + 0.32, tw, max(0.3, water - y - 0.34),
                   "\n".join(f"・{t}" for t in above), size=size, align="START",
                   color=self.P.text, line_spacing=125)
        self.label(tx, water + 0.06, tw, 0.28, below_title, size=size + 1, bold=True,
                   align="START", color=self.P.primaryDark)
        self.label(tx, water + 0.38, tw, max(0.3, (y + h) - water - 0.40),
                   "\n".join(f"・{t}" for t in below), size=size, align="START",
                   color=self.P.text, line_spacing=125)
        return y + h

    def balance(self, x, y, w, h, left, right, *, size=11, tilt=0) -> float:
        """Balance scale (comparing two options). left/right are
        (heading, [items...]).

        If tilt is positive, the right side looks heavier; if negative, the
        left side does. 0 is level.
        """
        beam_y = y + h * 0.22
        drop = h * 0.055 * (1 if tilt > 0 else -1 if tilt < 0 else 0)
        cx = x + w / 2
        hang = 0.30          # length of the hanging string; too short and the pan looks like it's sunk into the beam
        # Post and pivot (drawn before the beam, so the beam ends up on top)
        self.shape(cx - 0.05, beam_y, 0.10, h * 0.56, kind="RECTANGLE",
                   fill=self.P.muted, stroke=None)
        self.shape(cx - w * 0.055, y + h * 0.78, w * 0.11, h * 0.16,
                   kind="TRIANGLE", fill=self.P.muted, stroke=None)
        self.line(x + w * 0.16, beam_y - drop, x + w * 0.84, beam_y + drop,
                  color=self.P.text, weight=3.0, free=True)
        self.shape(cx - 0.09, beam_y - 0.09, 0.18, 0.18, kind="ELLIPSE",
                   fill=self.P.text, stroke=None)

        pw = min(w * 0.40, (w - 0.4) / 2)
        for i, (side, dy) in enumerate(((left, -drop), (right, drop))):
            head, items = side if isinstance(side, (tuple, list)) else (side, [])
            pan_cx = x + w * (0.25 if i == 0 else 0.75)
            pan_y = beam_y + dy + hang
            col = self.P.primary if i == 0 else self.P.info
            self.line(pan_cx, beam_y + dy, pan_cx, pan_y, color=self.P.muted,
                      weight=1.4, free=True)
            self.shape(pan_cx - pw / 2, pan_y, pw, 0.38, kind="ROUND_RECTANGLE",
                       fill=col, stroke=None, text=head, size=size, bold=True,
                       color=readable_on(col))
            if items:
                self.label(pan_cx - pw / 2 + 0.10, pan_y + 0.44, pw - 0.20,
                           max(0.3, (y + h) - (pan_y + 0.46)),
                           "\n".join(f"・{t}" for t in items), size=size - 1,
                           align="START", valign="TOP", color=self.P.text,
                           line_spacing=125)
        return y + h

    def steps(self, x, y, w, h, items, *, size=11, captions=None) -> float:
        """Staircase (climbing step by step). items are labels ordered from
        the bottom step to the top.

        Steps are placed flush against each other with no gap. Spacing them
        out would make it read as a bar chart instead, implying the
        unrelated meaning of "comparing quantities."
        """
        n = len(items)
        bw = w / n
        for i, text in enumerate(items):
            bh = h * (i + 1) / n
            bx = x + i * bw
            by = y + h - bh
            fill = lighten(self.P.primary, 0.60 - 0.60 * i / max(n - 1, 1))
            self.shape(bx, by, bw, bh, kind="RECTANGLE", fill=fill, stroke=None)
            self.label(bx + 0.06, by + 0.06, bw - 0.18, 0.52, text, size=size,
                       bold=True, align="START", valign="TOP",
                       color=readable_on(fill), line_spacing=110)
            if captions and i < len(captions) and captions[i]:
                self.label(bx + 0.06, by + 0.60, bw - 0.18, max(0.3, bh - 0.66),
                           captions[i], size=size - 2, align="START", valign="TOP",
                           color=readable_on(fill), line_spacing=115)
        return y + h

    def layers(self, x, y, w, h, items, *, size=11, gap=0.06) -> float:
        """Stacked layers (e.g. a tech stack). items is (label, note) or a plain string, ordered from top to bottom."""
        n = len(items)
        lh = (h - gap * (n - 1)) / n
        for i, item in enumerate(items):
            label, sub = item if isinstance(item, (tuple, list)) else (item, None)
            top = y + i * (lh + gap)
            fill = lighten(self.P.primary, 0.20 + 0.62 * i / max(n - 1, 1))
            fg = readable_on(fill)
            self.shape(x, top, w, lh, kind="ROUND_RECTANGLE", fill=fill, stroke=None)
            self.label(x + 0.18, top, w * 0.42, lh, label, size=size, bold=True,
                       align="START", valign="MIDDLE", color=fg)
            if sub:
                self.label(x + w * 0.44, top, w * 0.54 - 0.18, lh, sub,
                           size=size - 1, align="START", valign="MIDDLE", color=fg)
        return y + h

    def hub(self, x, y, w, h, center, spokes, *, size=10, center_size=11,
            radius=None) -> float:
        """Hub and spoke. spokes is a list of labels placed around the center."""
        cx, cy = x + w / 2, y + h / 2
        cw, ch = min(w * 0.30, 2.1), min(h * 0.30, 0.86)
        nw, nh = min(w * 0.26, 1.8), min(h * 0.24, 0.62)
        # The orbit radius is "half the frame minus half the node." A fixed
        # coefficient would either leave slack in the frame or overflow it
        # by the node's size
        rx = max(0.2, w / 2 - nw / 2 - 0.04) if radius is None else radius
        ry = max(0.2, h / 2 - nh / 2 - 0.04) if radius is None else radius
        n = len(spokes)
        pts = []
        for i in range(n):
            a = -math.pi / 2 + 2 * math.pi * i / n
            pts.append((cx + rx * math.cos(a), cy + ry * math.sin(a)))
        for px, py in pts:
            self.line(cx, cy, px, py, color=lighten(self.P.primary, 0.55),
                      weight=1.3, free=True)
        for (px, py), label in zip(pts, spokes):
            self.shape(px - nw / 2, py - nh / 2, nw, nh, kind="ROUND_RECTANGLE",
                       fill=self.P.surface, stroke=self.P.border, text=label,
                       size=size, color=self.P.text, line_spacing=110)
        self.shape(cx - cw / 2, cy - ch / 2, cw, ch, kind="ELLIPSE",
                   fill=self.P.primary, stroke=None, text=center, size=center_size,
                   bold=True, color="#FFFFFF", line_spacing=110)
        return y + h

    def matrix(self, x, y, w, h, quadrants, *, x_axis=("低", "高"),
               y_axis=("低", "高"), x_label=None, y_label=None, size=11) -> float:
        """2×2 matrix. quadrants are in top-left, top-right, bottom-left, bottom-right order."""
        if len(quadrants) != 4:
            raise ValueError(t("quadrants takes exactly 4 items "
                               "(top-left, top-right, bottom-left, bottom-right)"))
        pad = 0.44          # area reserved for axis labels
        gx, gy = x + pad, y
        gw, gh = w - pad, h - pad
        cw, ch = gw / 2, gh / 2
        cols = [lighten(self.P.primary, 0.86), lighten(self.P.success, 0.78),
                lighten(self.P.muted, 0.86), lighten(self.P.info, 0.82)]
        for i, text in enumerate(quadrants):
            col, row = i % 2, i // 2
            fill = cols[i]
            self.shape(gx + col * cw + 0.03, gy + row * ch + 0.03,
                       cw - 0.06, ch - 0.06, kind="ROUND_RECTANGLE",
                       fill=fill, stroke=None, text=text, size=size,
                       color=self.P.text, line_spacing=115)
        self.line(gx, gy + gh, gx + gw, gy + gh, color=self.P.muted, weight=1.4,
                  free=True)
        self.line(gx, gy, gx, gy + gh, color=self.P.muted, weight=1.4, free=True)
        self.label(gx, gy + gh + 0.04, gw / 2, 0.26, x_axis[0], size=size - 2,
                   align="START", color=self.P.muted)
        self.label(gx + gw / 2, gy + gh + 0.04, gw / 2, 0.26, x_axis[1],
                   size=size - 2, align="END", color=self.P.muted)
        self.label(x - 0.06, gy + gh - 0.28, pad, 0.26, y_axis[0], size=size - 2,
                   align="END", color=self.P.muted)
        self.label(x - 0.06, gy + 0.02, pad, 0.26, y_axis[1], size=size - 2,
                   align="END", color=self.P.muted)
        if x_label:
            self.label(gx, gy + gh + 0.26, gw, 0.26, x_label, size=size - 1,
                       align="CENTER", bold=True, color=self.P.text)
        if y_label:
            # Rotating (rotation=270) turns Japanese text sideways and makes
            # it hard to read. Instead, break each character onto its own
            # line and stack them vertically, simulating vertical writing
            ls = size - 1
            lh = len(y_label) * ls * self.LINE_EM / 72.0
            self.label(x - 0.02, gy + gh / 2 - lh / 2, pad - 0.10, lh + 0.06,
                       "\n".join(y_label), size=ls, align="CENTER", valign="MIDDLE",
                       bold=True, color=self.P.text, line_spacing=100)
        return y + h

    def comparison(self, x, y, w, h, columns, *, size=11, arrows=False,
                   highlight=None, colors=None, gap=0.22) -> float:
        """Lays options out side by side for comparison. columns is a list
        of (heading, [items...]).

        For 2 options showing "current state → proposal", `before_after()`
        provides a specialized form. Use this one when there are 3 or more
        options, when it's a parallel comparison rather than a transition,
        or when you want to highlight one recommended option.

        - `arrows=True` places right-pointing arrows between columns. Use
          this **only for transitions** (current → proposal, As-Is →
          To-Be). Adding arrows to a parallel comparison implies the
          unintended meaning of "progressing left to right."
        - Passing a column index to `highlight` makes only that column
          primary-colored, with the rest muted. Use this to indicate one
          recommended option. The default is all columns the same color
          (a parallel comparison with no implied ranking).
        - `colors` lets you set each column's color explicitly (takes
          priority over `highlight`).

        Corners use `RECTANGLE`. ROUND_RECTANGLE's corner radius scales
        with the shorter side (measured at roughly radius ≒ 0.155 × short
        side), so a short heading band and a tall body box end up with
        mismatched roundness even with identical settings. Since the
        Slides API doesn't let you specify a corner radius directly, this
        keeps corners square instead, matching `so_what` / `steps`.
        """
        n = len(columns)
        if n < 2:
            raise ValueError(t("comparison needs at least 2 columns, got {n}", n=n))
        gap_w = 0.58 if arrows else gap
        pw = (w - gap_w * (n - 1)) / n
        if pw < 0.8:
            raise ValueError(t(
                "w={w} leaves {pw:.2f}in per column for {n} columns; "
                "use fewer columns or a table", w=w, pw=pw, n=n))
        if colors is not None:
            cols = [colors[i % len(colors)] for i in range(n)]
        elif highlight is not None:
            cols = [self.P.primary if i == highlight else self.P.muted
                    for i in range(n)]
        else:
            cols = [self.P.primary] * n
        for i, entry in enumerate(columns):
            title, items = entry[0], entry[1]
            col = cols[i]
            px = x + i * (pw + gap_w)
            self.shape(px, y, pw, 0.42, kind="RECTANGLE", fill=col,
                       stroke=None, text=title, size=size, bold=True,
                       color=readable_on(col))
            self.shape(px, y + 0.46, pw, h - 0.46, kind="RECTANGLE",
                       fill=lighten(col, 0.88), stroke=lighten(col, 0.6))
            # Keep the left/right margins tight. Widening them reduces the
            # characters that fit per line, causing bullet items to spill a
            # single character onto the next line
            self.label(px + 0.10, y + 0.60, pw - 0.20, h - 0.74,
                       "\n".join(f"・{s}" for s in items), size=size,
                       align="START", valign="TOP", color=self.P.text,
                       line_spacing=130)
            if arrows and i < n - 1:
                self.shape(px + pw + 0.06, y + h / 2 - 0.22, gap_w - 0.12, 0.44,
                           kind="RIGHT_ARROW", fill=lighten(self.P.primary, 0.45),
                           stroke=None)
        return y + h

    def before_after(self, x, y, w, h, before, after, *, size=11,
                     before_title="Before", after_title="After") -> float:
        """Side-by-side contrast. before/after are lists of strings, with
        an arrow placed in the center.

        A specialized form of `comparison()`: 2 columns, with an arrow,
        highlighting the right side. For 3+ options or a parallel
        comparison with no implied ranking, use `comparison()` directly.
        """
        return self.comparison(x, y, w, h,
                               [(before_title, before), (after_title, after)],
                               size=size, arrows=True, highlight=1)

    def journey(self, x, y, w, h, milestones, *, size=10, size_title=11) -> float:
        """Journey. Places milestones alternately above and below a single
        road/line.

        milestones is (heading, note) or a plain string. Doesn't get
        vertically squeezed as items increase.
        """
        road_y = y + h / 2
        self.shape(x, road_y - 0.07, w, 0.14, kind="ROUND_RECTANGLE",
                   fill=lighten(self.P.primary, 0.80), stroke=None)
        n = len(milestones)
        cell = w / n
        stem = 0.26         # distance from the road to the heading box
        head_h = 0.34
        for i, ms in enumerate(milestones):
            head, sub = ms if isinstance(ms, (tuple, list)) else (ms, None)
            cx = x + i * cell + cell / 2
            up = (i % 2 == 0)
            bw = cell - 0.18
            # The heading box sits near the road, with the note further out. Mirrors above/below
            if up:
                by = road_y - stem - head_h
                sub_y, sub_h = y, by - y - 0.04
            else:
                by = road_y + stem
                sub_y, sub_h = by + head_h + 0.04, (y + h) - (by + head_h + 0.04)
            self.line(cx, road_y, cx, road_y + (-stem if up else stem),
                      color=self.P.primary, weight=1.4, free=True)
            self.shape(cx - bw / 2, by, bw, head_h, kind="ROUND_RECTANGLE",
                       fill=self.P.primary, stroke=None, text=head,
                       size=size_title, bold=True, color="#FFFFFF")
            if sub and sub_h > 0.16:
                self.label(cx - bw / 2, sub_y, bw, sub_h, sub, size=size,
                           align="CENTER", valign="BOTTOM" if up else "TOP",
                           color=self.P.muted, line_spacing=115)
            self.shape(cx - 0.09, road_y - 0.09, 0.18, 0.18, kind="ELLIPSE",
                       fill=self.P.primaryDark, stroke=None)
        return y + h

    def timeline(self, x, y, w, items, *, size=10, size_title=11, row_h=0.9) -> float:
        """Horizontal timeline. items is (point in time, heading) or a plain string."""
        line_y = y + 0.30
        self.line(x, line_y, x + w, line_y, color=lighten(self.P.primary, 0.5),
                  weight=2.0, free=True)
        n = len(items)
        cell = w / n
        for i, it in enumerate(items):
            when, head = it if isinstance(it, (tuple, list)) else ("", it)
            cx = x + i * cell + cell / 2
            # With TOP alignment, text crowds toward the bottom of its box
            # (right above the ●) and looks cramped.
            # MIDDLE alignment gives the right amount of spacing from the ●
            self.label(cx - cell / 2, y, cell, 0.24, when, size=size,
                       align="CENTER", valign="MIDDLE", color=self.P.muted,
                       bold=True)
            self.shape(cx - 0.08, line_y - 0.08, 0.16, 0.16, kind="ELLIPSE",
                       fill=self.P.primary, stroke=None)
            self.label(cx - cell / 2 + 0.06, line_y + 0.16, cell - 0.12,
                       row_h - 0.46, head, size=size_title, align="CENTER",
                       valign="TOP", color=self.P.text, line_spacing=115)
        return y + row_h
