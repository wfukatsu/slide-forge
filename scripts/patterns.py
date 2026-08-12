#!/usr/bin/env python3
"""Business framework diagrams (a mixin meant to be mixed into `diagrams.Canvas`).

Turns the standard "shapes" seen in new-business proposal and internal
approval decks into reusable parts. Where `illustrations` handles generic
metaphorical diagrams (pyramids, icebergs, ...), this module draws the
shapes of business frameworks themselves.

    d = Canvas(deck, slide_id, template)
    d.posmap(0.6, 1.2, 6.0, 3.6, [("A社", 0.8, 0.2), ("自社", 0.8, 0.9)],
             x_axis=("サポートがそこそこ", "サポートが充実"),
             y_axis=("導入までが遅い", "導入までが速い"), highlight="自社")
    d.gantt(0.6, 1.2, 9.0, 3.0, ["4月", "5月", "6月", "7月"],
            [("キックオフ", 0.5, 0.5), ("フェーズ1", 0.5, 2.2, "○○実施")])
    d.orgchart(0.6, 1.2, 6.0, 3.2,
               ("PJ責任者\n山田", [("営業担当\n佐藤", []), ("開発担当\n鈴木", [])]))
    d.lean_canvas(0.5, 1.1, 9.0, 4.0, {"problem": ["○○ができない"], ...})
    d.nested_circles(0.6, 1.2, 8.6, 3.4, [("市場全体", "1.2兆円"),
                     ("当社ターゲット", "800億円"), ("獲得目標", "12億円")])
    d.testimonial(0.6, 1.2, 8.6, 2.4, "コスト削減につながりそう", "田中 一郎",
                  role="株式会社○○ 情報システム部長")

Every diagram follows the same stacking convention as the other parts:
**it returns the y-coordinate of the bottom edge of the drawn area.**
Coordinates are in inches. After drawing, always run the `audit_*` self-checks.
"""
from __future__ import annotations

from colors import darken, lighten, readable_on
from _i18n import t, register

register({
    "influence_graph needs at least 1 person": "influence_graph には最低 1 名必要です",
    "links join people on different levels ({a} / {b}); a link line can only "
    "run along one level. Use reportsTo for a reporting line, or note the "
    "relationship in the kicker":
        "links が段の違う 2 人（{a} / {b}）を結んでいます。関係線は同じ段の中でしか"
        "引けません。上下関係なら reportsTo を、それ以外は示唆に書いてください",
    "{a} and {b} sit side by side, leaving no room for a link line. Put the "
    "relationship in the kicker, or keep it only in the draw.io version":
        "{a} と {b} は隣り合っており、関係線を引く幅がありません。"
        "関係は示唆に書くか、draw.io 版だけに残してください",
    "outcome_tree needs at least 1 node": "outcome_tree には最低 1 ノード必要です",
    "{n} people leave only {cell:.2f}in per column. Thin the graph with "
    "account_graph.extract() and put the rest in draw.io":
        "{n} 名では 1 列 {cell:.2f}in しか取れません。account_graph.extract() で"
        "間引き、残りは draw.io に出してください",
    "{n} nodes on one row leave only {cell:.2f}in each. Thin the graph with "
    "account_graph.extract() and put the rest in draw.io":
        "1 段に {n} ノードでは 1 つ {cell:.2f}in しか取れません。"
        "account_graph.extract() で間引き、残りは draw.io に出してください",
    "w={w} h={h} leaves no room for the plot area":
        "w={w} h={h} ではプロット領域が確保できません",
    "point '{name}' has coordinates ({px}, {py}); both must be within 0-1":
        "点「{name}」の座標 ({px}, {py}) は 0〜1 で指定します",
    "Unknown blocks {unknown}. Available: {available}":
        "未知のブロック {unknown}。利用可能: {available}",
    "nested_circles needs at least 2 rings": "nested_circles はリングが 2 個以上必要です",
    "{leaves} leaves leave only {cell:.2f}in per column. Widen w or split "
    "the tree":
        "葉が {leaves} 個で 1 列 {cell:.2f}in しか取れません。"
        "w を広げるか木を分割してください",
    "Row '{name}': the span ({start}-{end}) must be within 0-{ncols}":
        "行「{name}」の期間 ({start}〜{end}) は 0〜{ncols} で指定します",
    "w={w} leaves no room for the labels": "w={w} ではラベル領域が確保できません",
    "fishbone takes 2 to 6 categories, got {n}":
        "fishbone のカテゴリは 2〜6 個です（{n} 個が渡されました）",
    "fishbone: category '{name}' has {n} causes; 4 or fewer fit. "
    "Merge or move the rest to an appendix":
        "fishbone: カテゴリ「{name}」の原因が {n} 個あります。載るのは 4 個まで"
        "です。統合するか、残りは補足資料に回してください",
    "fishbone: category '{name}' needs at least 1 cause":
        "fishbone: カテゴリ「{name}」には原因が最低 1 個必要です",
})

# Block definitions for lean_canvas. Holds (key, heading) pairs in the standard Lean Canvas order
LEAN_CANVAS_KEYS = {
    "problem": "課題",
    "solution": "解決策",
    "key_metrics": "主要指標",
    "uvp": "独自の価値提案",
    "advantage": "圧倒的な優位性",
    "channels": "チャネル",
    "segments": "顧客セグメント",
    "cost": "コスト構造",
    "revenue": "収益の流れ",
}


def _card_band_h(h: float) -> float:
    """Height of the top/bottom band in a 3-tier card. Used by both the card body and the connector line."""
    return min(0.15, h * 0.26)


def _node(tree):
    """Normalize an orgchart node to (label, [children...]). Also accepts lists that come from JSON."""
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


class PatternMixin:
    """Mixin that adds business framework diagrams to `Canvas`."""

    # ---- Positioning map ----

    def posmap(self, x, y, w, h, points, *, x_axis=("低", "高"),
               y_axis=("低", "高"), highlight=None, highlight_color=None,
               size=10, bubble=0.72) -> float:
        """Positioning map (position relative to two axes). Returns the y-coordinate
        of the bottom edge.

        points are (label, px, py). px / py are relative coordinates in 0-1,
        with 0 at left/bottom and 1 at right/top. x_axis / y_axis are the labels
        for the two ends of each axis (low side, high side).
        Only the label(s) listed in highlight (e.g. "自社") get filled with the accent color.

        Where `matrix()` shows "classification into 4 quadrants", this shows the
        "positional relationship" against competitors. If you just want to name
        the quadrants, use matrix() instead.
        """
        cap_h = 0.30                       # Height of the top/bottom axis-end labels
        # Left/right axis-end labels are placed in boxes. The width reserved is
        # whatever fits the longer label on one line (a fixed width tends to wrap
        # awkwardly, e.g. "8 chars + 1 char")
        need = max(self._em(str(t)) for t in x_axis) \
            * (size - 1) / 72.0 * 1.1 + 0.34
        side_w = min(max(1.0, need), w * 0.30)
        gx, gy = x + side_w, y + cap_h
        gw, gh = w - side_w * 2, h - cap_h * 2
        if gw < 1.0 or gh < 1.0:
            raise ValueError(t("w={w} h={h} leaves no room for the plot area",
                               w=w, h=h))
        self.shape(gx, gy, gw, gh, kind="RECTANGLE", fill=self.P.surfaceAlt,
                   stroke=None)
        cx, cy = gx + gw / 2, gy + gh / 2
        ax = lighten(self.P.text, 0.35)
        self.line(cx, gy + gh, cx, gy, color=ax, weight=1.5,
                  end_arrow="FILL_ARROW", start_arrow="FILL_ARROW", free=True)
        self.line(gx, cy, gx + gw, cy, color=ax, weight=1.5,
                  end_arrow="FILL_ARROW", start_arrow="FILL_ARROW", free=True)
        # Axis-end labels. Top/bottom sit outside the plot area; left/right sit
        # as white boxes on the extension of the axis line
        self.label(gx, y, gw, cap_h - 0.04, y_axis[1], size=size, bold=True,
                   align="CENTER", valign="BOTTOM", color=self.P.text)
        self.label(gx, gy + gh + 0.04, gw, cap_h - 0.04, y_axis[0], size=size,
                   bold=True, align="CENTER", valign="TOP", color=self.P.text)
        lab_h = 0.52
        self.shape(x, cy - lab_h / 2, side_w - 0.08, lab_h, kind="RECTANGLE",
                   fill=self.P.white, stroke=self.P.border, text=x_axis[0],
                   size=size - 1, color=self.P.text, line_spacing=105)
        self.shape(gx + gw + 0.08, cy - lab_h / 2, side_w - 0.08, lab_h,
                   kind="RECTANGLE", fill=self.P.white, stroke=self.P.border,
                   text=x_axis[1], size=size - 1, color=self.P.text,
                   line_spacing=105)

        hi = {highlight} if isinstance(highlight, str) else set(highlight or ())
        r = bubble / 2
        for name, px, py in points:
            if not (0 <= px <= 1 and 0 <= py <= 1):
                raise ValueError(t("point '{name}' has coordinates ({px}, {py}); "
                                   "both must be within 0-1",
                                   name=name, px=px, py=py))
            bx = gx + (gw - bubble) * px
            by = gy + (gh - bubble) * (1 - py)
            fill = ((highlight_color or self.P.success) if name in hi
                    else self.P.primary)
            self.shape(bx, by, bubble, bubble, kind="ELLIPSE",
                       fill=fill, stroke=self.P.white, stroke_weight=1.5,
                       text=name, size=size, bold=True, color=readable_on(fill),
                       line_spacing=100)
        return y + h

    # ---- Gantt chart ----

    def gantt(self, x, y, w, h, columns, rows, *, label_w=None, size=10,
              colors=None, zebra=True) -> float:
        """Gantt chart (schedule bar chart). Returns the y-coordinate of the bottom edge.

        columns are the period headings (e.g. ["4月", "5月", "6月"]). rows are
        (row label, start, end) or (row label, start, end, bar label).
        start/end are fractional column units, where 0 is the left edge of the
        first column and len(columns) is the right edge.
        **A row where start == end is drawn as a milestone (◆).**

        Bar overlaps and dependency arrows are not represented. If you need to
        show fine-grained dependencies, a table is easier to draw and edit.
        """
        ncols = len(columns)
        lw = label_w if label_w is not None else min(1.8, w * 0.20)
        head_h = 0.34
        track_x, track_w = x + lw, w - lw
        cu = track_w / ncols               # width of one column
        row_h = (h - head_h) / len(rows)
        body_y = y + head_h

        self.shape(track_x, y, track_w, head_h, kind="RECTANGLE",
                   fill=self.P.primary, stroke=None)
        for c, name in enumerate(columns):
            self.label(track_x + c * cu, y, cu, head_h, str(name), size=size,
                       bold=True, align="CENTER", valign="MIDDLE",
                       color=readable_on(self.P.primary))
        if zebra:
            for i in range(len(rows)):
                if i % 2:
                    self.shape(x, body_y + i * row_h, w, row_h, kind="RECTANGLE",
                               fill=self.P.surfaceAlt, stroke=None)
        for c in range(ncols + 1):
            self.line(track_x + c * cu, y, track_x + c * cu, y + h,
                      color=self.P.border, weight=0.75, dashed=(0 < c < ncols),
                      free=True)
        self.line(x, y + h, x + w, y + h, color=self.P.border, weight=1.0,
                  free=True)

        bar_h = min(0.34, row_h * 0.52)
        for i, row in enumerate(rows):
            name, start, end = row[0], row[1], row[2]
            caption = row[3] if len(row) > 3 else None
            if not (0 <= start <= end <= ncols):
                raise ValueError(t(
                    "Row '{name}': the span ({start}-{end}) must be within "
                    "0-{ncols}", name=name, start=start, end=end, ncols=ncols))
            ry = body_y + i * row_h
            cyy = ry + row_h / 2
            self.label(x + 0.06, ry, lw - 0.16, row_h, str(name), size=size,
                       align="START", valign="MIDDLE", color=self.P.text)
            c = (colors[i] if isinstance(colors, (list, tuple)) else colors) \
                or self.P.primary
            if end - start < 1e-9:         # milestone
                ms = 0.20
                self.shape(track_x + start * cu - ms / 2, cyy - ms / 2, ms, ms,
                           kind="DIAMOND", fill=darken(c, 0.15), stroke=None)
                if caption:
                    # A milestone at the right edge would overflow both the frame
                    # and the last column's line if written to the right. Flip it
                    # to the left when it doesn't fit. Either placement can overlap
                    # a column line, so paint the row's background color underneath
                    # to hide the line
                    cs = size - 1
                    mx = track_x + start * cu
                    # Without adding the box's left/right inset (0.10 x 2), the box
                    # would be exactly the text's raw width and wrap. The 1.1x
                    # bold-text margin matches the in-bar label
                    need = self._em(caption) * cs / 72.0 * 1.1 + 0.24
                    room = (track_x + track_w) - (mx + ms / 2 + 0.06)
                    bg = self.P.surfaceAlt if (zebra and i % 2) else self.P.page
                    if room >= need:
                        gx, align = mx + ms / 2 + 0.06, "START"
                    else:
                        gx, align = mx - ms / 2 - 0.06 - need, "END"
                    self.shape(gx, cyy - 0.13, need, 0.26, kind="RECTANGLE",
                               fill=bg, stroke=None)
                    self.label(gx, cyy - 0.13, need, 0.26, caption, size=cs,
                               bold=True, align=align, valign="MIDDLE",
                               color=self.P.text)
                continue
            bx, bw = track_x + start * cu, (end - start) * cu
            self.shape(bx, cyy - bar_h / 2, bw, bar_h, kind="ROUND_RECTANGLE",
                       fill=c, stroke=None)
            if caption:
                need = self._em(caption) * (size - 1) / 72.0 * 1.1 + 0.16
                if need <= bw:             # fits inside the bar if possible, otherwise place to the right
                    self.label(bx, cyy - 0.13, bw, 0.26, caption, size=size - 1,
                               align="CENTER", valign="MIDDLE",
                               color=readable_on(c))
                else:
                    self.label(bx + bw + 0.06, cyy - 0.13,
                               max(0.6, x + w - bx - bw - 0.08), 0.26, caption,
                               size=size - 1, align="START", valign="MIDDLE",
                               color=self.P.muted)
        return y + h

    # ---- Org chart ----

    def orgchart(self, x, y, w, h, tree, *, size=10, node_h=None,
                 root_fill=None) -> float:
        """Org chart (top-down tree). Returns the y-coordinate of the bottom edge.

        tree is (label, [children...]). Children may be the same nested form,
        a string, or {"label": ..., "children": [...]}. Making the label two
        lines like "role\\nname" gives the typical org-chart look.

        Column width is auto-allocated by leaf count. Trees with depth >= 4 or
        more than 8 leaves will have crushed text, so split them by placing
        multiple orgchart calls side by side per department.
        """
        label, _ = _node(tree)
        depth = _depth(tree)
        leaves = _leaves(tree)
        gap_y = 0.30
        nh = node_h or min(0.62, (h - gap_y * (depth - 1)) / depth)
        cell = w / leaves
        if cell < 0.85:
            raise ValueError(t(
                "{leaves} leaves leave only {cell:.2f}in per column. Widen w "
                "or split the tree", leaves=leaves, cell=cell))
        level_h = (h - nh) / max(depth - 1, 1)

        def place(node, left, top, is_root):
            text, children = _node(node)
            span = _leaves(node) * cell
            ncx = left + span / 2
            nw = min(cell * _leaves(node) - 0.12, 2.2)
            fill = (root_fill or self.P.primary) if is_root else self.P.surface
            self.shape(ncx - nw / 2, top, nw, nh, kind="RECTANGLE", fill=fill,
                       stroke=None if is_root else self.P.border,
                       text=text, size=size, bold=is_root,
                       color=readable_on(fill) if is_root else self.P.text,
                       line_spacing=105)
            if not children:
                return
            child_top = top + level_h
            bus_y = top + nh + (level_h - nh) / 2
            self.line(ncx, top + nh, ncx, bus_y, color=self.P.border,
                      weight=1.25, free=True)
            cl = left
            centers = []
            for c in children:
                cspan = _leaves(c) * cell
                centers.append(cl + cspan / 2)
                place(c, cl, child_top, False)
                cl += cspan
            if len(centers) > 1:
                self.line(centers[0], bus_y, centers[-1], bus_y,
                          color=self.P.border, weight=1.25, free=True)
            for ccx in centers:
                self.line(ccx, bus_y, ccx, child_top, color=self.P.border,
                          weight=1.25, free=True)

        place(tree, x, y, True)
        return y + h

    # ---- Lean Canvas ----

    def lean_canvas(self, x, y, w, h, blocks, *, size=9, title_size=9.5) -> float:
        """Lean Canvas (9 blocks). Returns the y-coordinate of the bottom edge.

        blocks is a dict of key -> content (a string or list of strings). Keys are
        problem / solution / key_metrics / uvp / advantage / channels /
        segments / cost / revenue (see `LEAN_CANVAS_KEYS`).
        Blocks whose key is missing are drawn as an empty frame only.

        Putting long text in all 9 blocks will always overflow. Summarize each
        block to 2-3 items, each around 15 characters or fewer, before passing it in.
        """
        unknown = set(blocks) - set(LEAN_CANVAS_KEYS)
        if unknown:
            raise ValueError(t("Unknown blocks {unknown}. Available: {available}",
                               unknown=sorted(unknown),
                               available=list(LEAN_CANVAS_KEYS)))
        g = 0.06
        top_h = (h - g) * 0.66
        bot_h = h - g - top_h
        cw = (w - g * 4) / 5
        half = (top_h - g) / 2
        bot_y = y + top_h + g
        col = [x + i * (cw + g) for i in range(5)]
        cells = {                          # key -> (x, y, w, h)
            "problem":     (col[0], y, cw, top_h),
            "solution":    (col[1], y, cw, half),
            "key_metrics": (col[1], y + half + g, cw, half),
            "uvp":         (col[2], y, cw, top_h),
            "advantage":   (col[3], y, cw, half),
            "channels":    (col[3], y + half + g, cw, half),
            "segments":    (col[4], y, cw, top_h),
            "cost":        (x, bot_y, (w - g) / 2, bot_h),
            "revenue":     (x + (w + g) / 2, bot_y, (w - g) / 2, bot_h),
        }
        for key, title in LEAN_CANVAS_KEYS.items():
            bx, by, bw, bh = cells[key]
            self.shape(bx, by, bw, bh, kind="RECTANGLE", fill=self.P.white,
                       stroke=self.P.border)
            self.shape(bx, by, bw, 0.26, kind="RECTANGLE",
                       fill=self.P.surface, stroke=None)
            self.label(bx + 0.07, by + 0.015, bw - 0.14, 0.23, title,
                       size=title_size, bold=True, align="START",
                       valign="MIDDLE", color=self.P.primaryDark)
            content = blocks.get(key)
            if not content:
                continue
            items = [content] if isinstance(content, str) else list(content)
            self.label(bx + 0.08, by + 0.30, bw - 0.16, bh - 0.36,
                       "\n".join(f"・{t}" for t in items), size=size,
                       align="START", valign="TOP", color=self.P.text,
                       line_spacing=118)
        return y + h

    # ---- Nested circles (TAM / SAM / SOM) ----

    def nested_circles(self, x, y, w, h, rings, *, size=10, colors=None) -> float:
        """Nested circles that show whole-vs-part scale (TAM / SAM / SOM, etc.).
        Returns the y-coordinate of the bottom edge.

        rings are, **from the outside in**, (label, value display) or a string.
        Circles are stacked with aligned bottom edges, with labels drawn out to
        the right. Only use values that have a cited source.
        """
        n = len(rings)
        if n < 2:
            raise ValueError(t("nested_circles needs at least 2 rings"))
        d0 = min(h, w * 0.52)
        ccx = x + d0 / 2
        base = y + (h + d0) / 2            # bottom edge of the circle (vertically centered)
        cols = colors or [lighten(self.P.primary, 0.82 - 0.62 * i / (n - 1))
                          for i in range(n)]
        lab_x = ccx + d0 / 2 + 0.35
        lab_w = x + w - lab_x
        if lab_w < 1.2:
            raise ValueError(t("w={w} leaves no room for the labels", w=w))
        # Give the labels generous line spacing. Cramming them together makes
        # the "value" and the next ring's "name" look like one block, causing
        # the value's owning circle to be misread
        lab_h = 0.52
        row_gap = max(0.24, (h - lab_h * n) / max(n - 1, 1) - lab_h * 0.4)
        row_gap = min(row_gap, 0.55)
        for i, ring in enumerate(rings):
            name, value = (ring if isinstance(ring, (tuple, list))
                           else (ring, None))
            d = d0 * (n - i) / n
            self.shape(ccx - d / 2, base - d, d, d, kind="ELLIPSE",
                       fill=cols[i], stroke=self.P.white, stroke_weight=1.5)
            # The leader line starts at the center of the top band that's
            # visible only for that ring
            d_in = d0 * (n - i - 1) / n
            ay = base - d + (d - d_in) / 4
            ly = y + (h - lab_h * n - row_gap * (n - 1)) / 2 \
                + i * (lab_h + row_gap)
            self.line(ccx, ay, lab_x - 0.08, ly + lab_h / 2,
                      color=self.P.border, weight=1.0, free=True)
            self.label(lab_x, ly, lab_w, 0.24, name, size=size, bold=True,
                       align="START", valign="BOTTOM", color=self.P.text)
            if value:
                self.label(lab_x, ly + 0.25, lab_w, lab_h - 0.25, value,
                           size=size + 2, bold=True, align="START",
                           valign="TOP", color=darken(cols[i], 0.35))
        return y + h

    # ---- Customer / key-person testimonial ----

    def testimonial(self, x, y, w, h, quote, name, *, role=None, points=None,
                    icon="person", size=10, quote_size=13) -> float:
        """Quote card (verbatim customer voice / internal key-person comment).
        Returns the y-coordinate of the bottom edge.

        A person pictogram plus name/title on the left, the quote on the right.
        Passing points adds bullet-point supplementary notes below the quote.
        **Only use quotes from real, actual statements**
        (being a design component is not a license to fabricate a quote).
        """
        self.shape(x, y, w, h, kind="RECTANGLE", fill=self.P.surfaceAlt,
                   stroke=self.P.border)
        pw = min(1.7, w * 0.24)
        pad = 0.18
        ic = min(0.85, pw - 0.5)
        icx = x + pw / 2
        self.icon(icon, icx - ic / 2, y + pad, ic)
        name_y = y + pad + ic + 0.10
        self.label(x + 0.08, name_y, pw - 0.16, 0.26, name, size=size, bold=True,
                   align="CENTER", valign="TOP", color=self.P.text)
        if role:
            self.label(x + 0.08, name_y + 0.27, pw - 0.16,
                       max(0.22, y + h - name_y - 0.31), role, size=size - 1.5,
                       align="CENTER", valign="TOP", color=self.P.muted,
                       line_spacing=112)
        qx = x + pw + 0.12
        qw = x + w - qx - pad
        quote_h = (h - pad * 2) * (0.52 if points else 1.0)
        self.label(qx, y + pad, qw, quote_h, f"“{quote}”", size=quote_size,
                   bold=True, align="START", valign="MIDDLE",
                   color=self.P.primaryDark, line_spacing=125)
        if points:
            self.line(qx, y + pad + quote_h + 0.04, x + w - pad,
                      y + pad + quote_h + 0.04, color=self.P.border, weight=1.0,
                      free=True)
            self.label(qx, y + pad + quote_h + 0.12, qw,
                       h - pad * 2 - quote_h - 0.12,
                       "\n".join(f"・{t}" for t in points), size=size,
                       align="START", valign="TOP", color=self.P.text,
                       line_spacing=122)
        return y + h

    # ---- Account graph (influence / discovery) ----

    def _account_card(self, x, y, w, h, *, band_text, body_text, foot_text,
                      body_fill, band_fill, foot_fill, band_color, foot_color,
                      size, dashed=False, band_right=False):
        """Band-body-band 3-tier card. Reproduces the same look as the draw.io version on a slide."""
        bh = _card_band_h(h)
        stroke = lighten(self.P.text, 0.55 if not dashed else 0.72)
        dash = "DASH" if dashed else "SOLID"
        fw = min(w * 0.55, 0.85)
        self.shape(x, y, w, bh, kind="RECTANGLE", fill=band_fill, stroke=stroke,
                   dash=dash, text=band_text, size=size - 1, bold=True,
                   color=band_color)
        self.shape(x, y + bh, w, h - bh * 2, kind="RECTANGLE", fill=body_fill,
                   stroke=stroke, dash=dash, text=body_text, size=size,
                   color=self.P.text, line_spacing=100)
        if foot_text:
            fx = x + w - fw if band_right else x
            self.shape(fx, y + h - bh, fw, bh, kind="RECTANGLE", fill=foot_fill,
                       stroke=stroke, dash=dash, text=foot_text, size=size - 1.5,
                       bold=True, color=foot_color)

    def influence_graph(self, x, y, w, h, people, *, links=None, size=9,
                        more=None) -> float:
        """Influence map that arranges buying-committee members in an org structure.
        Returns the y-coordinate of the bottom edge.

        `people` is a list of dicts with `(id, roles, org, name, influence, stance,
        met, reportsTo)` (same shape as `scripts/account_graph.py`). Role goes in
        the top band, influence in the bottom band, stance is shown as the body
        fill color, and not-yet-met is shown with a dashed border.

        Fills use the semantic palette rather than brand colors: close is success,
        opposed is danger, neutral is surfaceAlt. This automatically fits the
        template's color scheme.

        When there are many people, thin them with `account_graph.extract()` and
        pass "N more: see the draw.io version" to `more`. Don't cram everyone
        onto one slide.
        """
        if not people:
            raise ValueError(t("influence_graph needs at least 1 person"))
        by_id = {p["id"]: p for p in people}
        kids: dict[str, list[str]] = {p["id"]: [] for p in people}
        roots = []
        for p in people:
            parent = p.get("reportsTo")
            if parent and parent in by_id:
                kids[parent].append(p["id"])
            else:
                roots.append(p["id"])

        def leaves(nid):
            return sum(leaves(c) for c in kids[nid]) or 1

        def depth(nid):
            return 1 + max((depth(c) for c in kids[nid]), default=0)

        total_leaves = sum(leaves(r) for r in roots)
        levels = max(depth(r) for r in roots)
        cell = w / total_leaves
        if cell < 0.95:
            raise ValueError(t(
                "{n} people leave only {cell:.2f}in per column. Thin the graph "
                "with account_graph.extract() and put the rest in draw.io",
                n=total_leaves, cell=cell))
        note_h = 0.24 if more else 0.0
        gap_y = 0.26
        ch = min(0.80, (h - note_h - gap_y * (levels - 1)) / levels)
        level_h = (h - note_h - ch) / max(levels - 1, 1)
        centers: dict[str, float] = {}

        def place(nid, left, top):
            p = by_id[nid]
            span = leaves(nid) * cell
            cx = left + span / 2
            cw = min(span - 0.10, 1.85)
            centers[nid] = (cx, top, cw)
            stance = p.get("stance", "neutral")
            fill = {"close": lighten(self.P.success, 0.82),
                    "opposed": lighten(self.P.danger, 0.86)}.get(
                        stance, self.P.surfaceAlt)
            body = "\n".join(s for s in (p.get("org", ""), p["name"]) if s)
            self._account_card(
                cx - cw / 2, top, cw, ch,
                band_text="/".join(p.get("roles", [])), body_text=body,
                foot_text=p.get("influence", "").capitalize(),
                body_fill=fill, band_fill=lighten(self.P.text, 0.88),
                foot_fill=lighten(self.P.text, 0.88),
                band_color=darken(self.P.danger, 0.15),
                foot_color=darken(self.P.primary, 0.2),
                size=size, dashed=not p.get("met", True))
            if not kids[nid]:
                return
            # The bottom band is partial width. Drawing the line from the outer
            # frame's bottom edge would make it sprout from the band's side
            # padding, so attach it to the bottom edge of the body box, which is
            # drawn full width
            body_bottom = top + ch - _card_band_h(ch)
            bus = top + ch + (level_h - ch) / 2
            self.line(cx, body_bottom, cx, bus, color=self.P.border, weight=1.2,
                      free=True)
            cl, cxs = left, []
            for c in kids[nid]:
                cspan = leaves(c) * cell
                cxs.append(cl + cspan / 2)
                place(c, cl, top + level_h)
                cl += cspan
            if len(cxs) > 1:
                self.line(cxs[0], bus, cxs[-1], bus, color=self.P.border,
                          weight=1.2, free=True)
            for ccx in cxs:
                self.line(ccx, bus, ccx, top + level_h, color=self.P.border,
                          weight=1.2, free=True)

        left = x
        for r in roots:
            place(r, left, y)
            left += leaves(r) * cell
        for lk in links or []:
            a, b = lk.get("from"), lk.get("to")
            if a not in centers or b not in centers:
                continue
            (ax, ay, aw), (bx, by, bw) = centers[a], centers[b]
            if abs(ay - by) > 0.01:
                # A line crossing levels would run across the top of other cards.
                # Rather than silently distorting it, stop and require it to be
                # expressed via reportsTo, or restrict it to two people at the
                # same level.
                raise ValueError(t(
                    "links join people on different levels ({a} / {b}); a link "
                    "line can only run along one level. Use reportsTo for a "
                    "reporting line, or note the relationship in the kicker",
                    a=a, b=b))
            # Derive the margin from the card width. A fixed value would make
            # the line length negative for adjacent cards, causing the line to
            # silently disappear without an error
            (lx, lw), (rx, rw) = ((ax, aw), (bx, bw)) if ax < bx else ((bx, bw), (ax, aw))
            x1, x2 = lx + lw / 2 + 0.04, rx - rw / 2 - 0.04
            if x2 - x1 <= 0.06:
                # There's no width to draw a line between adjacent cards.
                # Silently dropping it would make the relationship look like it
                # never existed, so stop and prompt the caller to move it into
                # the kicker instead.
                raise ValueError(t(
                    "{a} and {b} sit side by side, leaving no room for a link "
                    "line. Put the relationship in the kicker, or keep it only "
                    "in the draw.io version", a=a, b=b))
            self.line(x1, ay + ch / 2, x2, ay + ch / 2,
                      color=self.P.border, weight=1.2, dashed=True, free=True)
        if more:
            self.label(x, y + h - note_h, w, note_h, more, size=size - 1,
                       color=self.P.muted, align="START", valign="MIDDLE")
        return y + h

    def outcome_tree(self, x, y, w, h, nodes, *, edges=None, size=9,
                     more=None) -> float:
        """A diagram connecting Goal / Strategy / Tactics by support relationships.
        Returns the y-coordinate of the bottom edge.

        `nodes` are dicts of `(id, tier, text, owner)`, `edges` are
        `{"from": the supporting side, "to": the supported side}`. A multi-parent
        structure is allowed, where one Tactics item supports multiple Strategy
        items.

        **The row is determined by graph depth, not tier.** A sub-goal that
        supports a higher-level goal still has tier "goal", but its row is one
        level lower. tier only determines the badge color.
        """
        if not nodes:
            raise ValueError(t("outcome_tree needs at least 1 node"))
        edges = edges or []
        supports: dict[str, list[str]] = {n["id"]: [] for n in nodes}
        for e in edges:
            if e["from"] in supports and e["to"] in supports:
                supports[e["from"]].append(e["to"])
        depth: dict[str, int] = {}

        def d(nid):
            if nid in depth:
                return depth[nid]
            depth[nid] = 0
            depth[nid] = 1 + max((d(t) for t in supports[nid]), default=-1)
            return depth[nid]

        for n in nodes:
            d(n["id"])
        rows = sorted({depth[n["id"]] for n in nodes})
        widest = max(sum(1 for n in nodes if depth[n["id"]] == r) for r in rows)
        cell = w / widest
        if cell < 1.15:
            raise ValueError(t(
                "{n} nodes on one row leave only {cell:.2f}in each. Thin the "
                "graph with account_graph.extract() and put the rest in draw.io",
                n=widest, cell=cell))
        note_h = 0.24 if more else 0.0
        gap_y = 0.30
        ch = min(0.72, (h - note_h - gap_y * (len(rows) - 1)) / len(rows))
        level_h = (h - note_h - ch) / max(len(rows) - 1, 1)
        # The three tiers need to be visually distinguishable at a glance. Since
        # primary and info are both blue-ish in many templates, they'd be hard
        # to tell apart side by side, so they aren't used together here.
        tier_fill = {"goal": lighten(self.P.primary, 0.68),
                     "strategy": lighten(self.P.warning, 0.42),
                     "tactics": lighten(self.P.text, 0.86)}
        pos: dict[str, tuple[float, float]] = {}
        order: dict[str, float] = {}
        for ri, r in enumerate(rows):
            row = [n for n in nodes if depth[n["id"]] == r]
            row.sort(key=lambda n: (
                sum(order.get(t, 0) for t in supports[n["id"]])
                / max(1, len(supports[n["id"]])), n["id"]))
            span = w / len(row)
            for i, n in enumerate(row):
                order[n["id"]] = i
                cx = x + span * (i + 0.5)
                top = y + ri * level_h
                pos[n["id"]] = (cx, top)
                cw = min(span - 0.14, 2.3)
                self._account_card(
                    cx - cw / 2, top, cw, ch,
                    band_text=n["tier"].capitalize(), body_text=n["text"],
                    foot_text=n.get("owner", ""),
                    body_fill=self.P.white,
                    band_fill=tier_fill.get(n["tier"], self.P.surfaceAlt),
                    foot_fill=lighten(self.P.text, 0.88),
                    band_color=self.P.text,
                    foot_color=darken(self.P.primary, 0.2),
                    size=size, band_right=True)
        for e in edges:
            if e["from"] not in pos or e["to"] not in pos:
                continue
            fx, fy = pos[e["from"]]
            tx, ty = pos[e["to"]]
            # The endpoint is the bottom edge of the body box. The outer frame's
            # bottom edge only spans the owner-band width, so dropping the
            # arrow at the center would land it in the band's side padding
            end = ty + ch - _card_band_h(ch)
            # A diagonal line would cross over the owner band on its way to the
            # endpoint. Use orthogonal routing that bends between rows, entering
            # and exiting vertically instead
            bus = (fy + end) / 2
            self.line(fx, fy, fx, bus, color=self.P.border, weight=1.2, free=True)
            if abs(tx - fx) > 0.02:
                self.line(fx, bus, tx, bus, color=self.P.border, weight=1.2,
                          free=True)
            self.line(tx, bus, tx, end, color=self.P.border, weight=1.2,
                      end_arrow="FILL_ARROW", free=True)
        if more:
            self.label(x, y + h - note_h, w, note_h, more, size=size - 1,
                       color=self.P.muted, align="START", valign="MIDDLE")
        return y + h

    # ---- Cause-and-effect diagram (fishbone) ----

    def fishbone(self, x, y, w, h, problem, categories, *, size=9,
                 head_w=None) -> float:
        """Cause-and-effect diagram (fishbone). Returns the y-coordinate of the bottom edge.

        `problem` is the head at the right end (the effect), `categories` is a
        list of `(category name, [causes...])`. Main bones alternate top and
        bottom (0, 2, 4... on top, 1, 3, 5... on bottom).
        Categories must be 2-6, and causes at most 4 per category. Merge
        anything that overflows before passing it in (a fishbone diagram isn't
        meant to prove exhaustive coverage — it's meant to narrow in on likely
        causes).

        Since Slides can't place text at an angle, this doesn't use textbook-style
        diagonal sub-bones. Only the main bone's diagonal line is kept, and causes
        are laid out as horizontal bullet points running alongside the main bone
        (a simplified form that favors readability).
        """
        n = len(categories)
        if not 2 <= n <= 6:
            raise ValueError(t("fishbone takes 2 to 6 categories, got {n}", n=n))
        norm = []
        for c in categories:
            name, causes = (c["label"], c["causes"]) if isinstance(c, dict) \
                else (c[0], c[1])
            causes = list(causes)
            if not causes:
                raise ValueError(t(
                    "fishbone: category '{name}' needs at least 1 cause",
                    name=name))
            if len(causes) > 4:
                raise ValueError(t(
                    "fishbone: category '{name}' has {n} causes; 4 or fewer "
                    "fit. Merge or move the rest to an appendix",
                    name=name, n=len(causes)))
            norm.append((str(name), causes))

        cy = y + h / 2
        hw = head_w if head_w is not None else min(1.6, w * 0.18)
        hh = min(0.86, h * 0.30)
        # Spine. Drawn up to the point where it meets the head box
        self.line(x, cy, x + w - hw, cy, color=self.P.primary, weight=2.5,
                  free=True)
        self.shape(x + w - hw, cy - hh / 2, hw, hh, kind="RECTANGLE",
                   fill=self.P.primary, stroke=None, text=problem,
                   size=size + 1.5, bold=True, color=readable_on(self.P.primary),
                   line_spacing=110)

        top = [c for i, c in enumerate(norm) if i % 2 == 0]
        bottom = [c for i, c in enumerate(norm) if i % 2 == 1]
        usable_w = w - hw - 0.3
        cat_h = 0.34
        for row, cats in (("top", top), ("bottom", bottom)):
            if not cats:
                continue
            sw = usable_w / len(cats)
            for i, (name, causes) in enumerate(cats):
                bx = x + i * sw + 0.08
                bw = sw - 0.3
                if row == "top":
                    by = y
                    txt_y = y + cat_h + 0.06
                    txt_h = cy - y - cat_h - 0.24
                    txt_valign = "TOP"
                else:
                    by = y + h - cat_h
                    txt_h = (y + h - cat_h) - cy - 0.24
                    txt_y = by - 0.06 - txt_h
                    txt_valign = "BOTTOM"
                self.shape(bx, by, bw, cat_h, kind="RECTANGLE",
                           fill=self.P.surface, stroke=self.P.border,
                           text=name, size=size, bold=True, color=self.P.text)
                # Main bone. Runs from the box's right edge to the spine, angled
                # toward the head. The cause bullet list leaves 0.5in of space on
                # the right (so the bone's path doesn't cross the text)
                sx = bx + bw - 0.15
                ex = min(bx + bw + 0.35, x + w - hw - 0.1)
                sy = by + cat_h if row == "top" else by
                self.line(sx, sy, ex, cy, color=lighten(self.P.primary, 0.45),
                          weight=1.6, free=True)
                if txt_h > 0.2:
                    self.label(bx, txt_y, max(0.8, bw - 0.5), txt_h,
                               "\n".join(f"・{c}" for c in causes),
                               size=size - 0.5, align="START",
                               valign=txt_valign, color=self.P.muted,
                               line_spacing=125)
        return y + h
