#!/usr/bin/env python3
"""Page components and analysis figures (a mixin used together with `diagrams.Canvas`).

While `illustrations` / `patterns` / `charts` draw "the figure itself," this
module holds **components that build the page's skeleton** (title bar, lead-in
text, kicker, source-note line, exhibit frame), the **analysis figures** used
alongside them (logic tree, waterfall, rating matrix), and **deck-design
tools** (summary, storyline, ghost deck).

Usable regardless of the deck's purpose. That said, **how much of it you use
depends on the purpose**:

- Talks / study sessions -- just `governing_message` (the action title) and
  `source_note`. One message per slide; lead-in text and kickers can be said
  aloud instead
- Handouts / submissions / approval documents (read-alone) -- use all of it.
  Since the reader goes through it alone, each slide must contain its
  conclusion, evidence, and source in a self-contained way

    d = Canvas(deck, slide_id, template)
    b = d.governing_message(0.5, 0.55, 9.0, "In-housing order processing can cut costs by $180K/year")
    b = d.lead_in(0.5, b + 0.06, 9.0, "Of the current 3 processes, 2 can be replaced by the existing system.")
    inner = d.exhibit_frame(0.5, b + 0.18, 5.9, 2.7, 1, "Annual cost by process")
    d.vbars(inner[0] + 0.2, inner[1] + 0.15, inner[2] - 0.4, inner[3] - 0.3, [...])
    d.so_what(6.6, b + 0.18, 2.9, 2.7, "The top 2 processes alone account for 80% of the savings")
    d.source_note(0.5, 4.85, 9.0, "March 2026 workload survey (n=42)",
                  notes=["*1 Labor cost converted using the department average rate"])

Design rationale (researched 2026-08, based on consulting-firm slide conventions):

- The action title must be **15 words or fewer, at most 2 lines, active
  voice**. Write "what can be concluded," not "what is being shown." Reading
  just the titles in sequence should form the argument (horizontal logic).
- **Always place a source-note line** on a quantitative slide. Never show a
  numeric claim without a source.
- **Don't overuse** the kicker (so-what) box. A rule of thumb is at most 20%
  of slides overall. Don't restate the title (that's the title's job), and
  don't introduce new information that isn't in the figure.
- Number exhibits sequentially so they can be referenced from the body text
  or an appendix.

All components follow the same stacking convention as the rest of the
codebase and **return the y-coordinate of the bottom edge of the area they
drew**. The one exception is `exhibit_frame`, which returns the inner area
`(x, y, w, h)` for drawing its contents. Coordinates are in inches. Always
run the `audit_*` self-checks after drawing.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _i18n import t, register  # noqa: E402
from colors import lighten, readable_on  # noqa: E402

register({
    "  warn: the action title will wrap to {lines} lines. "
    "Trim it to 2 lines or fewer (\"{head}…\")":
        "  warn: アクションタイトルが {lines} 行になります。"
        "2 行までに削ってください（「{head}…」）",
    "governing_message: text is empty": "governing_message: text が空です",
    "lead_in: text is empty": "lead_in: text が空です",
    "so_what: text is empty": "so_what: text が空です",
    "source_note: source is empty (never show numbers without a source)":
        "source_note: source が空です（出典の無い数値は載せない）",
    "exhibit_frame: the frame is too small (w={w}, h={h})":
        "exhibit_frame: 枠が小さすぎます（w={w}, h={h}）",
    "mece_tree: depth {depth} is unreadable. Split into at most 3 levels":
        "mece_tree: 深さ {depth} は読めません。3 階層までに分割してください",
    "mece_tree: a column of {w:.2f}in is too narrow. Widen w or reduce the depth":
        "mece_tree: 1 列 {w:.2f}in は狭すぎます。w を広げるか階層を減らしてください",
    "mece_tree: {leaves} leaves at {h:.2f}in per row is too tight":
        "mece_tree: 葉が {leaves} 個で 1 行 {h:.2f}in は狭すぎます",
    "waterfall: good must be 'up' or 'down' (got {good!r})":
        "waterfall: good は 'up' か 'down'（指定: {good!r}）",
    "waterfall: fewer than 3 items does not make a bridge":
        "waterfall: 3 項目未満では橋渡しになりません",
    "waterfall: unknown kind '{kind}' (use total or delta)":
        "waterfall: 未知の種別 '{kind}'（total か delta）",
    "waterfall: the first item must be a total (the starting sum)":
        "waterfall: 先頭は total（起点の合計）である必要があります",
    "waterfall: total '{label}' does not match the running sum "
    "(given {value:g} / accumulated {cum:g})":
        "waterfall: 合計 '{label}' が積算と一致しません "
        "(指定 {value:g} / 積算 {cum:g})",
    "waterfall: the axis maximum is 0 or less": "waterfall: 上限が 0 以下です",
    "waterfall: series that go negative cannot be drawn (the baseline is fixed at zero)":
        "waterfall: 負の領域に入る系列は表現できません（基線はゼロ固定）",
    "waterfall: h={h} is too short (values and labels take {used}in)":
        "waterfall: h={h} では低すぎます（数値とラベルで {used}in 使う）",
    "rating_matrix: rows is empty": "rating_matrix: rows が空です",
    "rating_matrix: {levels} dots do not fit in a {w:.2f}in column":
        "rating_matrix: 1 列 {w:.2f}in にドット {levels} 個は入りません",
    "rating_matrix: row '{label}' has {nvals} values but there are {ncols} columns":
        "rating_matrix: 行 '{label}' の値が {nvals} 個、列は {ncols} 個",
    "rating_matrix: value {v!r} must be an integer from 0 to {levels}":
        "rating_matrix: 値 {v!r} は 0〜{levels} の整数にしてください",
    "exec_summary: {n} supporting points. Bundle them into at most 5":
        "exec_summary: 論点が {n} 個。5 個までに束ねてください",
    "exec_summary: h={h} cannot fit 3 blocks":
        "exec_summary: h={h} では 3 ブロックが入りません",
    "storyline: titles is empty": "storyline: titles が空です",
    "ghost: slides is empty": "ghost: slides が空です",
    "ghost: {w:.2f}×{h:.2f}in per card is too small":
        "ghost: 1 枚 {w:.2f}×{h:.2f}in は小さすぎます",
    "ghost: unknown status '{status}' ({allowed})":
        "ghost: 未知の状態 '{status}'（{allowed}）",
})

# Data status categories for a ghost deck. Used to check that no "未取得" (missing) items remain before finalizing
GHOST_STATUS = {
    "confirmed": ("確定", "success"),
    "wip": ("作成中", "warning"),
    "missing": ("未取得", "danger"),
}


def _node(tree):
    """Normalize a logic-tree node to (label, [children...]). Also accepts a list, as read from JSON."""
    if isinstance(tree, str):
        return tree, []
    if isinstance(tree, dict):
        return tree["label"], list(tree.get("children") or [])
    label, children = tree
    return label, list(children or [])


def _leaves(tree) -> int:
    _, children = _node(tree)
    return sum(_leaves(c) for c in children) if children else 1


def _depth(tree) -> int:
    _, children = _node(tree)
    return 1 + (max(_depth(c) for c in children) if children else 0)


class PageMixin:
    """Mixin that adds page components and analysis figures to `Canvas`."""

    # Effective line-height factor for body text. Matches the line spacing used by label()
    _LINE = 1.45

    # ---- 1. Governing message (action title) ----

    def governing_message(self, x, y, w, text, *, size=17, bar=0.055,
                          color=None, max_words=15) -> float:
        """Draw the action title with an accent bar. Returns the bottom y.

        Prefer the template's TITLE placeholder when it's usable. This
        component is for composing with a BLANK layout, or when you need a
        2-line title to land exactly where you intend.

        Warns when `max_words` is exceeded (the convention caps titles at 15
        words / 2 lines). Japanese can't be counted in words, so full-width
        characters are counted at 40 per line as a rule of thumb.
        """
        if not text or not text.strip():
            raise ValueError(t("governing_message: text is empty"))
        c = color or self.P.primary
        # Estimate the line count: count full-width chars as 1, half-width as 0.5, and divide by the per-line capacity
        width = sum(1.0 if ord(ch) > 0x2E80 else 0.5 for ch in text)
        per_line = max(1.0, (w - 0.3) * 72 / size)
        lines = max(1, int(width / per_line + 0.999))
        if lines > 2:
            print(t("  warn: the action title will wrap to {lines} lines. "
                    "Trim it to 2 lines or fewer (\"{head}…\")",
                    lines=lines, head=text[:20]))
        h = max(0.42, lines * size * self._LINE * 1.05 / 72 + 0.14)
        self.shape(x, y, bar, h, kind="RECTANGLE", fill=c, stroke=None)
        self.label(x + bar + 0.14, y, w - bar - 0.14, h, text,
                   size=size, bold=True, color=self.P.text,
                   valign="MIDDLE", line_spacing=105)
        return y + h

    # ---- 2. Lead-in ----

    def lead_in(self, x, y, w, text, *, size=10.5, rule=True) -> float:
        """1-2 lines right below the title, stating why to look at this figure. Returns the bottom y.

        In handouts/submissions the reader goes through it alone, so hand
        them the reading guidance before the figure. In a talk deck this can
        usually be omitted since it can be said aloud.
        """
        if not text or not text.strip():
            raise ValueError(t("lead_in: text is empty"))
        top = y
        if rule:
            self.shape(x, y, w, 0.012, kind="RECTANGLE",
                       fill=self.P.border, stroke=None)
            top = y + 0.012 + 0.06
        width = sum(1.0 if ord(ch) > 0x2E80 else 0.5 for ch in text)
        # Estimate under the same assumptions as audit_text_fit: 0.1in padding on each side,
        # line height = _LINE x line_spacing. Skimp here and you'll trip the check yourself
        per_line = max(1.0, (w - 0.2) * 72 / size)
        lines = max(1, int(width / per_line + 0.999))
        h = lines * size * self._LINE * 1.25 / 72 + 0.06
        self.label(x, top, w, h, text, size=size, color=self.P.muted,
                   line_spacing=125)
        return top + h

    # ---- 3. So-what box (kicker) ----

    def so_what(self, x, y, w, h, text, *, label="示唆", size=10.5,
                accent=None, points=None) -> float:
        """Put into words what can be read from the figure. Returns the bottom y.

        **Don't overuse it.** A rule of thumb is at most 20% of slides
        overall. Never write either of these:

        - A restatement of the title (the slide's claim is the title's job)
        - New information that isn't in the figure (that becomes an unsupported claim)

        Aligned with the left accent bar; corners are not rounded (a shared
        convention across this skill).
        """
        if not text or not text.strip():
            raise ValueError(t("so_what: text is empty"))
        c = accent or self.P.primary
        self.shape(x, y, w, h, kind="RECTANGLE",
                   fill=lighten(c, 0.93), stroke=lighten(c, 0.6))
        self.shape(x, y, 0.055, h, kind="RECTANGLE", fill=c, stroke=None)
        pad_l = 0.055 + 0.16
        head_h = 0.28
        self.label(x + pad_l, y + 0.12, w - pad_l - 0.16, head_h, label,
                   size=9, bold=True, color=c)
        body_y = y + 0.12 + head_h
        body_h = h - (body_y - y) - 0.14
        if points:
            lines = "\n".join(f"・{p}" for p in points)
            text = f"{text}\n\n{lines}"
        self.label(x + pad_l, body_y, w - pad_l - 0.16, body_h, text,
                   size=size, color=self.P.text, line_spacing=130)
        return y + h

    # ---- 4. Source-note line ----

    def source_note(self, x, y, w, source, *, notes=None, size=7.5,
                    rule=True, prefix="出典") -> float:
        """The source-note line and footnotes at the bottom of the page. Returns the bottom y.

        **Always place this on a slide that shows numbers.** Never show a
        figure you can't source. `notes` is a list of footnotes corresponding
        to a "*1" marker in the body text, shown above the source line.
        """
        if not source or not str(source).strip():
            raise ValueError(
                t("source_note: source is empty (never show numbers without a source)"))
        top = y
        if rule:
            self.shape(x, y, w, 0.01, kind="RECTANGLE",
                       fill=self.P.border, stroke=None)
            top = y + 0.01 + 0.04
        line_h = size * self._LINE * 1.2 / 72
        rows = list(notes or []) + [f"{prefix}: {source}"]
        h = len(rows) * line_h + 0.06
        self.label(x, top, w, h, "\n".join(rows), size=size,
                   color=self.P.muted, line_spacing=120)
        return top + h

    # ---- 5. Exhibit frame ----

    def exhibit_frame(self, x, y, w, h, number, title, *, size=9.5,
                      pad=0.14, label_prefix="図表"):
        """Draw a numbered exhibit frame, and **return the inner area (x, y, w, h) for drawing its contents**.

        This is the one component whose return value differs from the
        stacking convention (since another figure is drawn inside the
        frame). The number is assigned so it can be referenced from the body
        text or an appendix; the caller is responsible for managing the
        sequential numbering.
        """
        if h <= 0.6 or w <= 1.0:
            raise ValueError(t("exhibit_frame: the frame is too small (w={w}, h={h})",
                               w=w, h=h))
        self.shape(x, y, w, h, kind="RECTANGLE", fill=None, stroke=self.P.border)
        head_h = 0.3
        self.shape(x, y, w, head_h, kind="RECTANGLE",
                   fill=self.P.surfaceAlt, stroke=None)
        tag = f"{label_prefix} {number}"
        tag_w = 0.28 + len(tag) * size / 72 * 0.62
        self.shape(x + pad, y + 0.05, tag_w, head_h - 0.1, kind="RECTANGLE",
                   fill=self.P.primary, stroke=None, text=tag,
                   size=size - 1.5, bold=True, color=self.P.white)
        self.label(x + pad + tag_w + 0.12, y + 0.05, w - pad * 2 - tag_w - 0.12,
                   head_h - 0.1, title, size=size, bold=True,
                   color=self.P.text, valign="MIDDLE")
        return (x + pad, y + head_h + 0.08, w - pad * 2, h - head_h - 0.08 - pad)

    # ---- 6. Logic tree (MECE) ----

    def mece_tree(self, x, y, w, h, tree, *, size=10, gap=0.34,
                  root_fill=None, node_h=None) -> float:
        """A logic tree that expands from left to right. Returns the bottom y.

        Whereas `orgchart` (patterns) is a vertical org chart, this expands
        the breakdown of an issue horizontally. Whether the breakdown is
        MECE (no gaps, no overlaps) is the drawer's responsibility; this
        component only guarantees the shape.

        `tree` is `(label, [children...])`. A child can be the same nested
        shape, a plain string, or `{"label": ..., "children": [...]}`.
        """
        depth, leaves = _depth(tree), _leaves(tree)
        if depth > 4:
            raise ValueError(t("mece_tree: depth {depth} is unreadable. "
                               "Split into at most 3 levels", depth=depth))
        col_w = (w - gap * (depth - 1)) / depth
        if col_w < 1.1:
            raise ValueError(t("mece_tree: a column of {w:.2f}in is too narrow. "
                               "Widen w or reduce the depth", w=col_w))
        row_h = h / leaves
        nh = node_h or min(row_h - 0.12, 0.78)
        if nh < 0.3:
            raise ValueError(t("mece_tree: {leaves} leaves at {h:.2f}in per row is too tight",
                               leaves=leaves, h=row_h))

        def draw(node, level: int, top: float) -> tuple[float, float]:
            """Returns (center y, height occupied)."""
            label, children = _node(node)
            span = _leaves(node) * row_h
            cx = x + level * (col_w + gap)
            is_root = level == 0
            fill = (root_fill or self.P.primary) if is_root else (
                self.P.surface if children else self.P.white)
            stroke = None if is_root else self.P.border
            cy = top + span / 2
            self.shape(cx, cy - nh / 2, col_w, nh, kind="RECTANGLE",
                       fill=fill, stroke=stroke, text=label, size=size,
                       bold=is_root, color=readable_on(fill) if is_root else self.P.text,
                       line_spacing=110)
            child_top = top
            for ch in children:
                ccy, cspan = draw(ch, level + 1, child_top)
                # Parent's right edge -> midpoint -> child's left edge. Bend points are free (not touching is the correct line)
                midx = cx + col_w + gap / 2
                self.line(cx + col_w, cy, midx, cy, color=self.P.border, free=True)
                self.line(midx, cy, midx, ccy, color=self.P.border, free=True)
                self.line(midx, ccy, cx + col_w + gap, ccy,
                          color=self.P.border, free=True)
                child_top += cspan
            return cy, span

        draw(tree, 0, y)
        return y + h

    # ---- 7. Waterfall ----

    def waterfall(self, x, y, w, h, items, *, unit="", size=9.5,
                  bar_ratio=0.62, max_value=None, good="up") -> float:
        """A bridge of increases and decreases (waterfall). Returns the bottom y.

        `items` is `(label, value)` or `(label, value, kind)`. `kind` is
        `"total"` (a sum stacked from 0) or `"delta"` (a change floating from
        the previous total; the default). Totals are colored primary. The
        color of a delta is decided by `good`:

        - `good="up"` (default) -- an increase is success green (a
          revenue/profit bridge)
        - `good="down"` -- a decrease is success green (a cost/lead-time
          reduction bridge)

        Coloring purely by sign would flip the meaning in a cost-reduction
        context, where "a reduction" would end up red.

        **The last total must match the running sum.** A mismatch raises
        `ValueError` (catching a data mix-up right here).
        """
        if good not in ("up", "down"):
            raise ValueError(t("waterfall: good must be 'up' or 'down' (got {good!r})",
                               good=good))
        if len(items) < 3:
            raise ValueError(t("waterfall: fewer than 3 items does not make a bridge"))
        rows = []
        for it in items:
            if len(it) == 3:
                label, value, kind = it
            else:
                (label, value), kind = it, "delta"
            if kind not in ("total", "delta"):
                raise ValueError(t("waterfall: unknown kind '{kind}' (use total or delta)",
                                   kind=kind))
            rows.append((label, float(value), kind))
        if rows[0][2] != "total":
            raise ValueError(t("waterfall: the first item must be a total (the starting sum)"))

        # Determine the running sum and each bar's top/bottom edges
        cum, bars = 0.0, []
        for label, value, kind in rows:
            if kind == "total":
                if bars and abs(value - cum) > 1e-6:
                    raise ValueError(
                        t("waterfall: total '{label}' does not match the running sum "
                          "(given {value:g} / accumulated {cum:g})",
                          label=label, value=value, cum=cum))
                lo, hi = 0.0, value
                cum = value
            else:
                lo, hi = (cum, cum + value) if value >= 0 else (cum + value, cum)
                cum += value
            bars.append((label, value, kind, lo, hi))

        top = max_value if max_value is not None else max(hi for *_, hi in bars)
        if top <= 0:
            raise ValueError(t("waterfall: the axis maximum is 0 or less"))
        if min(lo for *_, lo, _ in bars) < 0:
            raise ValueError(t("waterfall: series that go negative cannot be drawn "
                               "(the baseline is fixed at zero)"))

        val_h, cat_h = 0.24, 0.30
        plot_h = h - val_h - cat_h
        if plot_h < 0.5:
            raise ValueError(t("waterfall: h={h} is too short (values and labels take {used}in)",
                               h=h, used=val_h + cat_h))
        cell = w / len(bars)
        bw = cell * bar_ratio
        base_y = y + val_h + plot_h

        prev_right = None
        for i, (label, value, kind, lo, hi) in enumerate(bars):
            cx = x + i * cell + cell / 2
            bx = cx - bw / 2
            y_hi = base_y - hi / top * plot_h
            y_lo = base_y - lo / top * plot_h
            if kind == "total":
                fill = self.P.primary
            else:
                is_good = (value >= 0) if good == "up" else (value < 0)
                fill = self.P.success if is_good else self.P.danger
            self.shape(bx, y_hi, bw, max(0.02, y_lo - y_hi), kind="RECTANGLE",
                       fill=fill, stroke=None)
            shown = f"{value:+,.0f}{unit}" if kind == "delta" else f"{value:,.0f}{unit}"
            self.label(cx - cell / 2, y_hi - val_h, cell, val_h, shown,
                       size=size, bold=True, align="CENTER", valign="BOTTOM",
                       color=self.P.text)
            self.label(cx - cell / 2, base_y + 0.04, cell, cat_h, label,
                       size=size - 0.5, align="CENTER", valign="TOP",
                       color=self.P.muted, line_spacing=105)
            # Bridging dashed line. Connects the previous bar's top (or bottom) edge to the next one
            connect_y = base_y - (hi if value >= 0 or kind == "total" else lo) / top * plot_h
            if prev_right is not None:
                self.line(prev_right[0], prev_right[1], bx, prev_right[1],
                          color=self.P.border, dashed=True, free=True)
            prev_right = (bx + bw, connect_y if kind == "total" else
                          base_y - (hi if value >= 0 else lo) / top * plot_h)
        return y + h

    # ---- 8. Rating matrix (dot rating) ----

    def rating_matrix(self, x, y, w, columns, rows, *, levels=4, size=10,
                      label_w=None, row_h=0.42, dot=0.13) -> float:
        """Show a row x column rating as a number of dots. Returns the bottom y.

        `rows` is `(label, [value, ...])`, where each value is an integer
        from 0 to `levels`. The number of columns must match the number of
        values.

        The Slides API has no pie-slice shape with an adjustable angle, so a
        Harvey ball's "fill exactly a quarter" can't be drawn; this
        represents it with a count of filled-in dots instead. **Filled vs.
        outlined is distinguishable even in black-and-white printing**,
        which actually makes this easier to handle in handout materials.
        """
        if not rows:
            raise ValueError(t("rating_matrix: rows is empty"))
        lw = label_w if label_w is not None else min(2.6, w * 0.34)
        col_w = (w - lw) / len(columns)
        if col_w < levels * (dot + 0.05):
            raise ValueError(t("rating_matrix: {levels} dots do not fit in a {w:.2f}in column",
                               levels=levels, w=col_w))
        head_h = 0.36
        self.label(x, y, lw, head_h, "", size=size)
        for j, col in enumerate(columns):
            self.label(x + lw + j * col_w, y, col_w, head_h, col, size=size - 0.5,
                       bold=True, align="CENTER", valign="MIDDLE", color=self.P.text)
        self.shape(x, y + head_h, w, 0.012, kind="RECTANGLE",
                   fill=self.P.border, stroke=None)
        top = y + head_h + 0.012
        for i, (label, values) in enumerate(rows):
            if len(values) != len(columns):
                raise ValueError(
                    t("rating_matrix: row '{label}' has {nvals} values but there are "
                      "{ncols} columns", label=label, nvals=len(values), ncols=len(columns)))
            ry = top + i * row_h
            if i % 2 == 1:
                self.shape(x, ry, w, row_h, kind="RECTANGLE",
                           fill=self.P.surfaceAlt, stroke=None)
            self.label(x + 0.06, ry, lw - 0.12, row_h, label, size=size,
                       valign="MIDDLE", color=self.P.text)
            for j, v in enumerate(values):
                if not isinstance(v, int) or not 0 <= v <= levels:
                    raise ValueError(
                        t("rating_matrix: value {v!r} must be an integer from 0 to {levels}",
                          v=v, levels=levels))
                span = levels * dot + (levels - 1) * 0.05
                sx = x + lw + j * col_w + (col_w - span) / 2
                for k in range(levels):
                    filled = k < v
                    self.shape(sx + k * (dot + 0.05), ry + (row_h - dot) / 2, dot, dot,
                               kind="ELLIPSE",
                               fill=self.P.primary if filled else self.P.white,
                               stroke=None if filled else self.P.muted,
                               stroke_weight=0.75)
        return top + len(rows) * row_h

    # ---- 9. Executive summary (SCR) ----

    def exec_summary(self, x, y, w, h, situation, complication, resolution, *,
                     points=None, size=10.5, labels=("状況", "課題", "答え")) -> float:
        """Lead with the conclusion in 3 tiers: Situation -> Complication -> Resolution. Returns the bottom y.

        The entry point to the Pyramid Principle. The condition is that
        **this one slide alone must let the reader make a decision**; the
        body that follows is just the supporting evidence for it. `points`
        are the supporting points behind the answer (3-5; if you need more,
        reconsider the body's chapter breakdown).
        """
        blocks = [(labels[0], situation), (labels[1], complication), (labels[2], resolution)]
        if points and len(points) > 5:
            raise ValueError(t("exec_summary: {n} supporting points. "
                               "Bundle them into at most 5", n=len(points)))
        pts_h = 0.0
        if points:
            pts_h = 0.34 + len(points) * 0.3
        block_h = (h - pts_h - 0.16 * 2) / 3
        if block_h < 0.5:
            raise ValueError(t("exec_summary: h={h} cannot fit 3 blocks", h=h))
        badge_w = 0.72
        for i, (name, text) in enumerate(blocks):
            by = y + i * (block_h + 0.16)
            last = i == len(blocks) - 1
            c = self.P.primary if last else self.P.muted
            self.shape(x, by, badge_w, block_h, kind="RECTANGLE",
                       fill=c if last else lighten(c, 0.85), stroke=None,
                       text=name, size=size - 0.5, bold=True,
                       color=self.P.white if last else self.P.text)
            self.shape(x + badge_w, by, w - badge_w, block_h, kind="RECTANGLE",
                       fill=lighten(self.P.primary, 0.95) if last else self.P.white,
                       stroke=self.P.border)
            self.label(x + badge_w + 0.16, by + 0.08, w - badge_w - 0.32, block_h - 0.16,
                       text, size=size, valign="MIDDLE", color=self.P.text,
                       bold=last, line_spacing=125)
        if points:
            py = y + 3 * (block_h + 0.16)
            self.label(x, py, w, 0.28, "答えを支える論点", size=9, bold=True,
                       color=self.P.muted)
            for i, p in enumerate(points):
                ly = py + 0.3 + i * 0.3
                self.shape(x + 0.04, ly + 0.09, 0.11, 0.11, kind="ELLIPSE",
                           fill=self.P.primary, stroke=None)
                self.label(x + 0.28, ly, w - 0.28, 0.3, p, size=size - 0.5,
                           color=self.P.text, valign="MIDDLE")
        return y + h

    # ---- 10. Horizontal logic (storyline) ----

    def storyline(self, x, y, w, titles, *, size=10, row_h=0.44,
                  highlight=None) -> float:
        """Lines up the action titles in order, to confirm that reading them forms the argument. Returns the bottom y.

        `titles` is a string or `(page number, title)`, connected by a
        vertical rule on the left. **Also a design tool**: if the argument
        doesn't hold together here, fix the structure before building the
        slides (order: ghost deck -> this figure -> generation).
        """
        if not titles:
            raise ValueError(t("storyline: titles is empty"))
        rows = [(t if isinstance(t, (tuple, list)) else (i + 1, t))
                for i, t in enumerate(titles)]
        rail_x = x + 0.22
        self.shape(rail_x, y + row_h / 2, 0.014, (len(rows) - 1) * row_h,
                   kind="RECTANGLE", fill=self.P.border, stroke=None)
        hl = set(highlight or [])
        for i, (num, text) in enumerate(rows):
            ry = y + i * row_h
            on = num in hl
            c = self.P.primary if on else self.P.muted
            self.shape(rail_x - 0.105, ry + row_h / 2 - 0.11, 0.23, 0.23,
                       kind="ELLIPSE", fill=c if on else self.P.white,
                       stroke=None if on else c, stroke_weight=1.0)
            # Make the number label's box wider than the circle. audit_text_fit
            # assumes 0.1in of padding on each side, so at the circle's exact
            # size it would mechanically be flagged as "overflow"
            self.label(rail_x - 0.2, ry + row_h / 2 - 0.11, 0.42, 0.23, str(num),
                       size=7, bold=True, align="CENTER", valign="MIDDLE",
                       color=self.P.white if on else c)
            self.label(x + 0.56, ry, w - 0.56, row_h, text, size=size,
                       bold=on, valign="MIDDLE", color=self.P.text)
        return y + len(rows) * row_h

    # ---- 11. Ghost deck ----

    def ghost(self, x, y, w, h, slides, *, cols=4, size=8, gap=0.16) -> float:
        """A ghost deck of skeleton-only slides laid out in a grid. Returns the bottom y.

        `slides` is `(number, action title, exhibit description, status)`.
        Status is `confirmed` / `wip` / `missing`. This is a figure **for
        confirming the argument and the data lineup before finalizing**; it
        is a design tool, not a deliverable.
        """
        if not slides:
            raise ValueError(t("ghost: slides is empty"))
        rows = (len(slides) + cols - 1) // cols
        cw = (w - gap * (cols - 1)) / cols
        ch = (h - gap * (rows - 1)) / rows
        if cw < 1.2 or ch < 0.9:
            raise ValueError(t("ghost: {w:.2f}×{h:.2f}in per card is too small",
                               w=cw, h=ch))
        for i, item in enumerate(slides):
            num, title, exhibit, status = (list(item) + ["confirmed"])[:4]
            if status not in GHOST_STATUS:
                raise ValueError(t("ghost: unknown status '{status}' ({allowed})",
                                   status=status, allowed=sorted(GHOST_STATUS)))
            name, tone = GHOST_STATUS[status]
            c = getattr(self.P, tone)
            gx = x + (i % cols) * (cw + gap)
            gy = y + (i // cols) * (ch + gap)
            self.shape(gx, gy, cw, ch, kind="RECTANGLE",
                       fill=self.P.white, stroke=self.P.border)
            self.shape(gx, gy, cw, 0.05, kind="RECTANGLE", fill=c, stroke=None)
            self.label(gx + 0.08, gy + 0.1, 0.3, 0.2, str(num), size=size - 1,
                       bold=True, color=self.P.muted)
            self.label(gx + 0.34, gy + 0.1, cw - 0.42, ch * 0.42, title,
                       size=size, bold=True, color=self.P.text, line_spacing=110)
            self.label(gx + 0.08, gy + ch * 0.52, cw - 0.16, ch * 0.28, exhibit,
                       size=size - 1, color=self.P.muted, line_spacing=110)
            self.label(gx + 0.08, gy + ch - 0.26, cw - 0.16, 0.2, name,
                       size=size - 1.5, bold=True, color=c)
        return y + h
