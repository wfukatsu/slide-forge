#!/usr/bin/env python3
"""図形だけで描く「イメージ図」。

`diagrams.Canvas` に生えるミックスイン。API キーもネットワークも要らず、色は
テンプレートの配色から取るので、AI 生成画像と違って**毎回まったく同じ絵**になる。

2 層ある。

1. **ピクトグラム** … 人・サーバ・DB・雲・鍵など、意味を 1 個の絵で表す部品。
   `icon()` / `icon_row()` / `icon_flow()` から使う。
2. **比喩図** … ピラミッド・ファネル・氷山・天秤など、関係の形そのものを見せる図。
   `pyramid()` / `funnel()` / `iceberg()` / `balance()` など。

        d = Canvas(deck, slide_id, template)
        d.icon_flow(0.7, 1.2, 8.6, [("person", "利用者"), ("browser", "アプリ"),
                                    ("server", "API"), ("database", "台帳")])
        b = d.pyramid(1.6, 2.4, 6.8, 2.4, ["経営指標", "業務指標", "システム指標"])

すべての図は `diagrams` と同じ積み上げ規約に従い、**描画領域の下端 y を返す**。
次のブロックはその戻り値を起点に置くこと。

図を描いたら `audit_overlaps()` / `audit_text_fit()` を必ず呼ぶ。ラベルが長いと
ピクトグラムのキャプションどうしがぶつかるが、これは座標の段階で拾える。
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
})

# ピクトグラムの一覧。icon() の name に渡せる値。
ICONS = (
    "person", "people", "server", "database", "cloud", "document", "documents",
    "gear", "lock", "shield", "browser", "mobile", "bot", "chart", "clock",
    "check", "cross", "warning", "mail", "key", "network", "code", "stack",
    "folder", "bulb", "search", "sync", "flag", "coin", "chip",
)


class IllustrationMixin:
    """`Canvas` にピクトグラムと比喩図を足すミックスイン。"""

    # ---------------- ピクトグラム ----------------

    def icon(self, name: str, x: float, y: float, size: float = 0.8, *,
             color: str | None = None, label: str | None = None,
             label_size: float = 9, label_w: float | None = None,
             label_gap: float = 0.05, bold_label: bool = False) -> float:
        """size×size の正方形にピクトグラムを描く。戻り値は下端 y。

        label を渡すと絵の下に中央揃えのキャプションを置く。キャプションの幅は
        既定で size の 2 倍（絵より広い）。横に並べるときは label_w で明示すること。
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
        """ピクトグラムを横一列に等間隔で並べる。items は名前か (名前, ラベル)。"""
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
        """ピクトグラムを矢印でつないだ流れ図。「利用者 → アプリ → DB」の類。

        矢印は絵と絵の間の隙間にだけ引く（絵に食い込まない）。

        **絵が大きすぎると隙間が無くなる。** そのまま描くと矢印の終点が始点より
        左に来て、右向きのはずの矢印が逆向きに描かれる。API も audit も
        （`_anchored` な線なので）これを拾わないため、ここで止める。
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
        """ピクトグラムを格子状に並べる。items は名前か (名前, ラベル)。"""
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

    # ---- 個々のピクトグラム。すべて (x, y, s, c) の正方形に収める ----

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
        # 掛け金はドーナツ（円環）。下半分は本体で隠れるので、きれいな U 字に見える。
        # 角丸矩形で代用すると半径が足りず「四角い掛け金」になる
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

    # ---------------- 比喩図 ----------------

    # 継ぎ目に背景色の筋が出ないように部品どうしを重ねる量（インチ）
    _SEAM = 0.01

    def _taper(self, cx, y, h, w_top, w_bot, fill, *, alpha=1.0) -> None:
        """上底 w_top・下底 w_bot の等脚台形を、指定どおりの傾きで描く。

        **Slides の `TRAPEZOID` は使えない。** 上底の食い込みが「表示高さ × 0.25」に
        固定されていて、幅でも scaleY でも変えられないため（実測）、上底と下底を
        自分で決める図（ピラミッド・ファネル）には向かない。TRAPEZOID をそのまま
        積むと、段ごとに傾きが変わって輪郭がギザギザになる。

        そこで「中央の矩形＋左右の直角三角形」の 3 部品に分けて描く。
        RIGHT_TRIANGLE は既定で直角が左下にあるので、flip_x / flip_y で
        必要な向きの角を作る。
        """
        inner = min(w_top, w_bot)
        wedge = abs(w_bot - w_top) / 2
        s = self._SEAM
        if inner > 0:
            self.shape(cx - inner / 2 - s, y, inner + s * 2, h, kind="RECTANGLE",
                       fill=fill, stroke=None, alpha=alpha)
        if wedge < 0.01:
            return
        down = w_bot > w_top          # 下が広い＝ピラミッド。実体は下側
        # 左のくさび: 実体は中央寄り（右）。下広なら右下、上広なら右上に直角が来る
        self.shape(cx - max(w_top, w_bot) / 2, y, wedge + s, h,
                   kind="RIGHT_TRIANGLE", fill=fill, stroke=None, alpha=alpha,
                   flip_x=True, flip_y=not down)
        # 右のくさび: 実体は中央寄り（左）
        self.shape(cx + inner / 2 - s, y, wedge + s, h,
                   kind="RIGHT_TRIANGLE", fill=fill, stroke=None, alpha=alpha,
                   flip_y=not down)

    def pyramid(self, x, y, w, h, levels, *, colors=None, size=12,
                gap=0.04, captions=None) -> float:
        """階層（上ほど少数・上位）。levels は上から順のラベル。戻り値は下端 y。

        captions を渡すと各段の右側に補足を置く。x + w の外側を使うので、
        captions を使うときは w を狭めに取ること。

        台形は 180 度回して上底を狭くしている。**文字は図形に入れず別に重ねる**
        （回すと文字も一緒に逆さまになるため）。
        """
        n = len(levels)
        cols = colors or [lighten(self.P.primary, 0.55 * i / max(n - 1, 1))
                          for i in range(n)]
        lh = (h - gap * (n - 1)) / n
        cx = x + w / 2
        for i, text in enumerate(levels):
            top = y + i * (lh + gap)
            # 頂点を幅 0 として線形に広げる。上底＝ひとつ上の段の下底なので、
            # 段ごとの傾きが揃い、輪郭が一直線になる
            top_w = w * i / n
            bot_w = w * (i + 1) / n
            fill = cols[i] if not isinstance(cols, str) else cols
            if i == 0:
                self.shape(cx - bot_w / 2, top, bot_w, lh, kind="TRIANGLE",
                           fill=fill, stroke=None)
            else:
                self._taper(cx, top, lh, top_w, bot_w, fill)
            # 頂点の段は塗りが細いので、文字は下寄りに置く
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
        """絞り込み（上が広く下が狭い）。stages は (ラベル, 値の表示) か文字列。

        値を表示する場合、その領域は x + w の右外側を使う。
        """
        n = len(stages)
        lh = (h - gap * (n - 1)) / n
        cx = x + w / 2
        narrow = 0.62               # 最下段までに何割すぼめるか
        for i, st in enumerate(stages):
            label, value = st if isinstance(st, (tuple, list)) else (st, None)
            top = y + i * (lh + gap)
            # 各段の上底＝ひとつ上の段の下底。輪郭が一直線につながる
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
        """重なり。sets は 2 個または 3 個のラベル。center は共通部分のラベル。"""
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
        # ラベルは円の外側へ。円の上に重ねるとアルファ越しに読みにくい。
        # 外へ出した結果が枠からはみ出さないよう、最後に [x, x+w] に収める
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
            # 重なりは淡いので白抜きだと沈む。濃い文字色にする
            self.label(mx - 0.75, my - 0.15, 1.5, 0.3, center, size=size - 1,
                       align="CENTER", valign="MIDDLE", bold=True,
                       color=darken(self.P.primary, 0.45))
        return y + h

    def iceberg(self, x, y, w, h, above, below, *, above_title="見えている部分",
                below_title="見えていない部分", size=10, art_ratio=0.44) -> float:
        """氷山（表に出ている一部と、水面下の大半）。above/below は文字列のリスト。

        左 art_ratio の幅に絵、右に説明を置く。海面は絵の領域だけを塗るので、
        右の文字が水色の上に載って読みにくくなることはない。
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
        # 水面下は上底が広く下へすぼまる＝台形を 180 度回したもの
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
        """天秤（2 つの選択肢の比較）。left/right は (見出し, [項目…])。

        tilt が正なら右が重い、負なら左が重い見た目になる。0 なら水平。
        """
        beam_y = y + h * 0.22
        drop = h * 0.055 * (1 if tilt > 0 else -1 if tilt < 0 else 0)
        cx = x + w / 2
        hang = 0.30          # 吊り紐の長さ。短いと皿が竿にめり込んで見える
        # 支柱と支点（竿より先に描く＝竿が上に来る）
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
        """階段（段階を踏んで上がっていく）。items は下段から上段へのラベル。

        段どうしは隙間なく隣接させる。離すと棒グラフに見えてしまい、
        「量の比較」という別の意味に読まれる。
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
        """積層（技術スタック等）。items は上から順の (ラベル, 補足) か文字列。"""
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
        """中心と放射（ハブ＆スポーク）。spokes は周囲に置くラベルのリスト。"""
        cx, cy = x + w / 2, y + h / 2
        cw, ch = min(w * 0.30, 2.1), min(h * 0.30, 0.86)
        nw, nh = min(w * 0.26, 1.8), min(h * 0.24, 0.62)
        # 周回半径は「枠の半分 − ノードの半分」。固定係数だと枠を余らせるか、
        # ノードの分だけはみ出すかのどちらかになる
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
        """2×2 のマトリクス。quadrants は左上・右上・左下・右下の順。"""
        if len(quadrants) != 4:
            raise ValueError(t("quadrants takes exactly 4 items "
                               "(top-left, top-right, bottom-left, bottom-right)"))
        pad = 0.44          # 軸ラベルの領域
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
            # 回転（rotation=270）だと日本語が横倒しになって読みにくい。
            # 1 文字ずつ改行して縦に積む＝擬似的な縦書きにする
            ls = size - 1
            lh = len(y_label) * ls * self.LINE_EM / 72.0
            self.label(x - 0.02, gy + gh / 2 - lh / 2, pad - 0.10, lh + 0.06,
                       "\n".join(y_label), size=ls, align="CENTER", valign="MIDDLE",
                       bold=True, color=self.P.text, line_spacing=100)
        return y + h

    def before_after(self, x, y, w, h, before, after, *, size=11,
                     before_title="Before", after_title="After") -> float:
        """左右の対比。before/after は文字列のリスト。中央に矢印を置く。"""
        arrow_w = 0.58
        pw = (w - arrow_w) / 2
        for i, (title, items, col) in enumerate((
                (before_title, before, self.P.muted),
                (after_title, after, self.P.primary))):
            px = x + i * (pw + arrow_w)
            self.shape(px, y, pw, 0.42, kind="ROUND_RECTANGLE", fill=col,
                       stroke=None, text=title, size=size, bold=True,
                       color=readable_on(col))
            self.shape(px, y + 0.46, pw, h - 0.46, kind="ROUND_RECTANGLE",
                       fill=lighten(col, 0.88), stroke=lighten(col, 0.6))
            # 左右の余白は詰める。広く取ると 1 行に入る文字数が減り、
            # 箇条書きが 1 文字だけ次行へこぼれる
            self.label(px + 0.10, y + 0.60, pw - 0.20, h - 0.74,
                       "\n".join(f"・{t}" for t in items), size=size,
                       align="START", valign="TOP", color=self.P.text,
                       line_spacing=130)
        self.shape(x + pw + 0.06, y + h / 2 - 0.22, arrow_w - 0.12, 0.44,
                   kind="RIGHT_ARROW", fill=lighten(self.P.primary, 0.45),
                   stroke=None)
        return y + h

    def journey(self, x, y, w, h, milestones, *, size=10, size_title=11) -> float:
        """道のり。マイルストーンを一本道の上下に交互に配置する。

        milestones は (見出し, 補足) か文字列。項目が増えても縦に潰れない。
        """
        road_y = y + h / 2
        self.shape(x, road_y - 0.07, w, 0.14, kind="ROUND_RECTANGLE",
                   fill=lighten(self.P.primary, 0.80), stroke=None)
        n = len(milestones)
        cell = w / n
        stem = 0.26         # 道から見出しの箱までの距離
        head_h = 0.34
        for i, ms in enumerate(milestones):
            head, sub = ms if isinstance(ms, (tuple, list)) else (ms, None)
            cx = x + i * cell + cell / 2
            up = (i % 2 == 0)
            bw = cell - 0.18
            # 見出しの箱は道の近くに、補足はその外側に。上下で鏡像になる
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
        """横方向の時系列。items は (時点, 見出し) か文字列。"""
        line_y = y + 0.30
        self.line(x, line_y, x + w, line_y, color=lighten(self.P.primary, 0.5),
                  weight=2.0, free=True)
        n = len(items)
        cell = w / n
        for i, it in enumerate(items):
            when, head = it if isinstance(it, (tuple, list)) else ("", it)
            cx = x + i * cell + cell / 2
            self.label(cx - cell / 2, y, cell, 0.24, when, size=size,
                       align="CENTER", valign="TOP", color=self.P.muted, bold=True)
            self.shape(cx - 0.08, line_y - 0.08, 0.16, 0.16, kind="ELLIPSE",
                       fill=self.P.primary, stroke=None)
            self.label(cx - cell / 2 + 0.06, line_y + 0.16, cell - 0.12,
                       row_h - 0.46, head, size=size_title, align="CENTER",
                       valign="TOP", color=self.P.text, line_spacing=115)
        return y + row_h
