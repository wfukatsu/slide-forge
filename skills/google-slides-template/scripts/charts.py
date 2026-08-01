#!/usr/bin/env python3
"""表とグラフを描くミックスイン（`diagrams.Canvas` に混ぜて使う）。

    d = Canvas(deck, slide_id, template)
    d.table(0.5, 1.2, 9.0, ["項目", "従来", "提案"],
            [["構築期間", "6ヶ月", "2ヶ月"], ["運用工数", "3人月", "0.5人月"]])
    d.vbars(0.5, 1.2, 6.0, 3.2, [("2023", 120), ("2024", 210), ("2025", 380)])
    d.vbars_grouped(0.5, 1.2, 9.0, 3.4, ["Q1", "Q2"],
                    [("従来", [40, 42]), ("提案", [18, 12])])
    d.linechart(0.5, 1.2, 9.0, 3.2, ["1月", "2月", "3月"],
                [("応答時間", [320, 180, 90])], unit="ms")
    d.pie(0.7, 1.3, 2.8, [("移行済み", 62), ("移行中", 23), ("未着手", 15)])

設計の約束（データ可視化の一般則に合わせている）:

- **棒グラフの基線は必ずゼロ。** 負値・途中からの軸は受け付けない
  （変化を誇張するため）。折れ線だけ `y_min` を動かせる。
- **系列色は `Palette.series()` の固定順**（primary → info → success →
  warning → danger）。並べ替えたり循環させたりしない。色は系列＝実体に
  ついて回り、順位や大小では塗らない。単一系列の棒は primary 一色。
- **文字は本文色（text / muted）で描く。** 系列の識別は隣の色見本が担う。
- **軸・グリッドは控えめに**（border 色・破線）。数値は選択的に直接ラベル。
- 表は Slides ネイティブのテーブル（後から編集できる）。グラフは図形で
  描くので、`audit_*` の自己点検と `--dry-run` がそのまま効く。
  円グラフだけ SVG → PNG で貼る（Slides API に扇形が無いため）。

座標はインチ。戻り値は他の部品と同じく描画領域の下端 y。
"""
from __future__ import annotations

import hashlib
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _auth  # noqa: E402
from colors import lighten, readable_on  # noqa: E402
from icons import _try_cairosvg, _try_cli  # noqa: E402

CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "..", "cache", "charts")


def _fmt(v) -> str:
    """数値の既定表示。整数は桁区切り、小数は 1 桁。"""
    if isinstance(v, float) and not v.is_integer():
        return f"{v:,.1f}"
    return f"{int(v):,}"


def _nice_ceil(v: float) -> float:
    """軸の上限に使う「きりのよい数」への切り上げ（1 / 2 / 2.5 / 5 × 10^k）。"""
    if v <= 0:
        return 1.0
    exp = math.floor(math.log10(v))
    for m in (1, 2, 2.5, 5, 10):
        n = m * (10 ** exp)
        if v <= n * (1 + 1e-9):
            return n
    return 10.0 ** (exp + 1)


def _series_pairs(series) -> list[tuple[str, list]]:
    """[(名前, [値…]), …] に正規化する。JSON 由来のリストも受ける。"""
    out = []
    for s in series:
        if isinstance(s, dict):
            out.append((s["name"], list(s["values"])))
        else:
            name, values = s
            out.append((str(name), list(values)))
    return out


class ChartMixin:
    """`Canvas` に表とグラフを足すミックスイン。"""

    # ---- 表（Slides ネイティブのテーブル） ----

    def table(self, x, y, w, headers, rows, *, col_widths=None, row_h=0.34,
              header_h=0.38, size=10, header_size=None, aligns=None,
              header_fill=None, zebra=True, border=None) -> float:
        """表を描き、下端 y を返す。headers は列見出し、rows は行のリスト。

        - `col_widths` は列幅の比率（例 `[2, 1, 1]`）。省略すると等分
        - `aligns` は列ごとの寄せ（"START" / "CENTER" / "END"）。省略すると
          1 列目 START・残り CENTER
        - `zebra` で偶数行に薄い縞を敷く（行数が多いときの読み違え防止）
        - セルは Slides のテーブルなので、生成後にユーザーが編集できる

        `row_h` は**最小**行高。文字が折り返すと行は勝手に伸びるので、
        戻り値はあくまで見積もり。セルに入り切らない文字は `audit_text_fit()`
        が生成前に拾う。
        """
        ncols = len(headers)
        for i, r in enumerate(rows):
            if len(r) != ncols:
                raise ValueError(f"rows[{i}] の列数 {len(r)} が見出しの {ncols} と合いません")
        weights = list(col_widths) if col_widths else [1.0] * ncols
        if len(weights) != ncols:
            raise ValueError("col_widths の要素数が headers と合いません")
        total_w = sum(weights)
        widths = [w * wt / total_w for wt in weights]
        aligns = list(aligns) if aligns else ["START"] + ["CENTER"] * (ncols - 1)
        head_c = header_fill or self.P.primary
        head_fg = readable_on(head_c)
        border_c = border or self.P.border
        h_total = header_h + row_h * len(rows)

        oid = self._oid("t")
        nrows = len(rows) + 1
        reqs = [{"createTable": {
            "objectId": oid, "rows": nrows, "columns": ncols,
            "elementProperties": self._elem_props(x, y, w, h_total)}}]

        # 列幅・行高（minRowHeight なので文字が多いと伸びる）
        for c, cw in enumerate(widths):
            reqs.append({"updateTableColumnProperties": {
                "objectId": oid, "columnIndices": [c],
                "tableColumnProperties": {
                    "columnWidth": {"magnitude": _auth.inches(cw), "unit": "EMU"}},
                "fields": "columnWidth"}})
        reqs.append({"updateTableRowProperties": {
            "objectId": oid, "rowIndices": [0],
            "tableRowProperties": {
                "minRowHeight": {"magnitude": _auth.inches(header_h), "unit": "EMU"}},
            "fields": "minRowHeight"}})
        if rows:
            reqs.append({"updateTableRowProperties": {
                "objectId": oid, "rowIndices": list(range(1, nrows)),
                "tableRowProperties": {
                    "minRowHeight": {"magnitude": _auth.inches(row_h), "unit": "EMU"}},
                "fields": "minRowHeight"}})

        # 罫線は控えめに 1 本の色で
        reqs.append({"updateTableBorderProperties": {
            "objectId": oid, "borderPosition": "ALL",
            "tableBorderProperties": {
                "tableBorderFill": {"solidFill": {
                    "color": {"rgbColor": _auth.hex_to_rgb(border_c)}}},
                "weight": {"magnitude": 12700, "unit": "EMU"},
                "dashStyle": "SOLID"},
            "fields": "tableBorderFill,weight,dashStyle"}})

        def cell_fill(r0, c0, rspan, cspan, color):
            reqs.append({"updateTableCellProperties": {
                "objectId": oid,
                "tableRange": {"location": {"rowIndex": r0, "columnIndex": c0},
                               "rowSpan": rspan, "columnSpan": cspan},
                "tableCellProperties": {
                    "tableCellBackgroundFill": {"solidFill": {
                        "color": {"rgbColor": _auth.hex_to_rgb(color)}}},
                    "contentAlignment": "MIDDLE"},
                "fields": "tableCellBackgroundFill.solidFill,contentAlignment"}})

        # 全セルの縦位置を中央へ（塗りは行単位で上書き）
        reqs.append({"updateTableCellProperties": {
            "objectId": oid,
            "tableRange": {"location": {"rowIndex": 0, "columnIndex": 0},
                           "rowSpan": nrows, "columnSpan": ncols},
            "tableCellProperties": {"contentAlignment": "MIDDLE"},
            "fields": "contentAlignment"}})
        cell_fill(0, 0, 1, ncols, head_c)
        if zebra:
            for r in range(2, nrows, 2):
                cell_fill(r, 0, 1, ncols, self.P.surfaceAlt)

        def put_text(r, c, text, *, color, bold, fsize, align):
            if text is None or str(text) == "":
                return
            loc = {"rowIndex": r, "columnIndex": c}
            reqs.append({"insertText": {
                "objectId": oid, "cellLocation": loc, "text": str(text)}})
            reqs.append({"updateTextStyle": {
                "objectId": oid, "cellLocation": loc,
                "style": {
                    "fontFamily": "Noto Sans JP",
                    "fontSize": {"magnitude": fsize, "unit": "PT"},
                    "bold": bold,
                    "foregroundColor": {"opaqueColor": {
                        "rgbColor": _auth.hex_to_rgb(color)}}},
                "textRange": {"type": "ALL"},
                "fields": "fontFamily,fontSize,bold,foregroundColor"}})
            reqs.append({"updateParagraphStyle": {
                "objectId": oid, "cellLocation": loc,
                "style": {"alignment": align},
                "textRange": {"type": "ALL"}, "fields": "alignment"}})

        hs = header_size or size
        for c, head in enumerate(headers):
            put_text(0, c, head, color=head_fg, bold=True, fsize=hs,
                     align=aligns[c])
        for r, row in enumerate(rows, start=1):
            for c, val in enumerate(row):
                put_text(r, c, val, color=self.P.text, bold=False, fsize=size,
                         align=aligns[c])

        self.deck.requests += reqs
        self._seq += 1
        self.rects[oid] = (x, y, w, h_total, "TABLE")
        self.solids.append({"rect": (x, y, w, h_total), "seq": self._seq,
                            "name": f"表 {str(headers[0])[:12]}"})
        # セルごとの文字を audit_text_fit / audit_overlaps の対象に登録する。
        # セルの内側余白は左右 0.05in（図形の 0.1in より狭い）だが、検査側の
        # 見積もり（TEXT_INSET_X）に合わせて保守的に評価される
        cx0 = x
        for c, cw in enumerate(widths):
            cy0 = y
            for r in range(nrows):
                rh = header_h if r == 0 else row_h
                text = headers[c] if r == 0 else rows[r - 1][c]
                if text is not None and str(text) != "":
                    self.texts[f"{oid}_r{r}c{c}"] = {
                        "rect": (cx0, cy0, cw, rh), "kind": "TABLE_CELL",
                        "text": str(text), "size": hs if r == 0 else size,
                        "ls": 100, "fill": True, "align": aligns[c],
                        "valign": "MIDDLE", "seq": self._seq}
                cy0 += rh
            cx0 += cw
        return y + h_total

    # ---- 縦棒グラフ ----

    VBAR_VAL_H = 0.24   # 棒の上の数値ラベルの高さ
    VBAR_LAB_H = 0.30   # 基線の下のカテゴリラベルの高さ

    def vbars(self, x, y, w, h, items, *, max_value=None, colors=None, unit="",
              size=10, value_size=10, bar_ratio=0.62) -> float:
        """縦棒グラフ。items は (ラベル, 数値) か (ラベル, 数値, 表示文字列)。

        基線はゼロ固定（負値は不可）。棒は primary 一色が既定で、`colors` に
        リストを渡したときだけ塗り分ける（強調は 1 本だけ等、意図があるとき）。
        数値は各棒の上に直接ラベルする。出典のある数値にだけ使うこと。
        戻り値は下端 y（= y + h）。
        """
        plot_h = h - self.VBAR_VAL_H - self.VBAR_LAB_H
        if plot_h < 0.4:
            raise ValueError(f"h={h} ではプロット領域が確保できません（0.94in 以上に）")
        vals = [it[1] for it in items]
        if any(v < 0 for v in vals):
            raise ValueError("vbars は負値を扱えません（基線ゼロ固定）")
        mx = max_value or _nice_ceil(max(vals))
        n = len(items)
        cell = w / n
        bw = cell * bar_ratio
        base_y = y + self.VBAR_VAL_H + plot_h

        self.line(x, base_y, x + w, base_y, color=self.P.border, weight=1.0,
                  free=True)
        for i, item in enumerate(items):
            name, value = item[0], item[1]
            caption = item[2] if len(item) > 2 else _fmt(value) + unit
            c = (colors[i] if isinstance(colors, (list, tuple))
                 else colors) or self.P.primary
            bx = x + i * cell + (cell - bw) / 2
            bh = plot_h * value / mx
            if bh > 0.005:
                self.shape(bx, base_y - bh, bw, bh, kind="RECTANGLE",
                           fill=c, stroke=None)
            self.label(bx - 0.25, base_y - bh - self.VBAR_VAL_H, bw + 0.5,
                       self.VBAR_VAL_H - 0.02, caption, size=value_size,
                       bold=True, align="CENTER", valign="BOTTOM",
                       color=self.P.text)
            self.label(x + i * cell, base_y + 0.04, cell, self.VBAR_LAB_H - 0.04,
                       name, size=size, align="CENTER", valign="TOP",
                       color=self.P.text)
        return y + h

    def vbars_grouped(self, x, y, w, h, categories, series, *, max_value=None,
                      colors=None, unit="", size=10, value_size=8.5,
                      legend=True, values=True) -> float:
        """グループ化した縦棒。categories は横軸、series は [(系列名, [値…]), …]。

        系列色は `Palette.series()` の固定順。凡例は上に 1 行。
        戻り値は下端 y（= y + h）。
        """
        pairs = _series_pairs(series)
        ns, ncat = len(pairs), len(categories)
        for name, vs in pairs:
            if len(vs) != ncat:
                raise ValueError(f"系列「{name}」の値が {len(vs)} 個で、"
                                 f"categories の {ncat} と合いません")
            if any(v < 0 for v in vs):
                raise ValueError("vbars_grouped は負値を扱えません（基線ゼロ固定）")
        cols = list(colors) if colors else self.P.series(ns)
        leg_h = 0.28 if (legend and ns >= 2) else 0.0
        if leg_h:
            self._legend_row(x, y, w, [(name, cols[i])
                                       for i, (name, _) in enumerate(pairs)],
                             size=size)
        plot_top = y + leg_h + self.VBAR_VAL_H
        plot_h = h - leg_h - self.VBAR_VAL_H - self.VBAR_LAB_H
        if plot_h < 0.4:
            raise ValueError(f"h={h} ではプロット領域が確保できません")
        mx = max_value or _nice_ceil(max(v for _, vs in pairs for v in vs))
        base_y = plot_top + plot_h
        cell = w / ncat
        group_w = cell * 0.72
        gap = 0.03
        bw = (group_w - gap * (ns - 1)) / ns

        self.line(x, base_y, x + w, base_y, color=self.P.border, weight=1.0,
                  free=True)
        for ci, cat in enumerate(categories):
            gx = x + ci * cell + (cell - group_w) / 2
            for si, (_, vs) in enumerate(pairs):
                v = vs[ci]
                bx = gx + si * (bw + gap)
                bh = plot_h * v / mx
                if bh > 0.005:
                    self.shape(bx, base_y - bh, bw, bh, kind="RECTANGLE",
                               fill=cols[si], stroke=None)
                if values:
                    self.label(bx - 0.18, base_y - bh - 0.20, bw + 0.36, 0.18,
                               _fmt(v) + unit, size=value_size, align="CENTER",
                               valign="BOTTOM", color=self.P.text)
            self.label(x + ci * cell, base_y + 0.04, cell, self.VBAR_LAB_H - 0.04,
                       cat, size=size, align="CENTER", valign="TOP",
                       color=self.P.text)
        return y + h

    def _legend_row(self, x, y, w, entries, *, size=10) -> float:
        """色見本＋名前を 1 行に左詰めで並べる凡例。entries は [(名前, 色), …]。"""
        ex = x
        for name, c in entries:
            # ラベル枠は文字幅＋テキストインセット（左右 0.1in）＋ゆとり。
            # ぴったりに切ると Slides 側の実描画で折り返す
            tw = self._em(str(name)) * size / 72.0 * 1.1 + 0.30
            self.shape(ex, y + 0.075, 0.16, 0.11, kind="RECTANGLE",
                       fill=c, stroke=None)
            self.label(ex + 0.20, y, tw, 0.26, str(name), size=size,
                       align="START", valign="MIDDLE", color=self.P.text)
            ex += 0.20 + tw + 0.18
        if ex - 0.30 > x + w:
            print(f"  warn: 凡例が幅 {w:.1f}in に収まっていません"
                  f"（必要 {ex - 0.30 - x:.1f}in）。系列名を短くしてください",
                  file=sys.stderr)
        return y + 0.26

    # ---- 折れ線グラフ ----

    def linechart(self, x, y, w, h, labels, series, *, y_min=0, y_max=None,
                  grid=4, unit="", markers=True, size=9.5, legend=True,
                  axis_w=0.6, end_values=False) -> float:
        """折れ線グラフ。labels は横軸の目盛り、series は [(系列名, [値…]), …]。

        軸は 1 本だけ（二重軸は作れない仕様）。スケールの違う 2 系列は
        グラフを分けること。`grid` は横グリッドの分割数で、目盛りの数値は
        左の `axis_w` 幅に出す（単位は最上段の目盛りにだけ付く）。
        `y_max` を省略すると目盛りが丸い数字になるよう上限を選ぶ。
        `end_values=True` で各系列の最後の点にだけ数値を添える
        （全点ラベルはしない）。戻り値は下端 y（= y + h）。
        """
        pairs = _series_pairs(series)
        ns, npt = len(pairs), len(labels)
        for name, vs in pairs:
            if len(vs) != npt:
                raise ValueError(f"系列「{name}」の値が {len(vs)} 個で、"
                                 f"labels の {npt} と合いません")
        cols = self.P.series(ns)
        leg_h = 0.28 if (legend and ns >= 2) else 0.0
        lab_h = 0.28
        allv = [v for _, vs in pairs for v in vs]
        mn = y_min
        if y_max is not None:
            mx = y_max
        else:
            # 目盛りが 100 / 200 / … のような丸い数字になるよう、
            # 「きりのよい刻み × 分割数」を上限にする
            raw = max(allv)
            step = _nice_ceil((raw - mn) / grid) if raw > mn else 1.0
            mx = mn + step * grid
        if mx <= mn:
            raise ValueError(f"y_max({mx}) は y_min({mn}) より大きい必要があります")

        # 目盛り文字列を先に決め、最長のものが折り返さない軸幅を確保する
        # （Slides の実描画は見積もりより広く食うので係数は甘めに取る）
        ticks = [_fmt(mn + g / grid * (mx - mn)) + (unit if g == grid else "")
                 for g in range(grid + 1)]
        need_w = max(self._em(t) for t in ticks) * 8.5 / 72.0 * 1.2 + 0.34
        axis_w = max(axis_w, need_w)

        if leg_h:
            self._legend_row(x + axis_w, y,  w - axis_w,
                             [(name, cols[i]) for i, (name, _) in enumerate(pairs)],
                             size=size)
        px0, pw = x + axis_w, w - axis_w
        py0 = y + leg_h + 0.08
        ph = h - leg_h - lab_h - 0.08
        if ph < 0.6 or pw < 1.0:
            raise ValueError(f"w={w} h={h} ではプロット領域が確保できません")

        def ypos(v):
            return py0 + ph - (v - mn) / (mx - mn) * ph

        # グリッドと目盛り。基線だけ実線、上は破線で控えめに
        for g in range(grid + 1):
            frac = g / grid
            gy = py0 + ph - frac * ph
            self.line(px0, gy, px0 + pw, gy,
                      color=self.P.border if g == 0 else lighten(self.P.border, 0.5),
                      weight=1.0 if g == 0 else 0.75, dashed=g > 0, free=True)
            self.label(x, gy - 0.10, axis_w - 0.08, 0.2, ticks[g], size=8.5,
                       align="END", valign="MIDDLE", color=self.P.muted)

        step = pw / npt
        xs = [px0 + (i + 0.5) * step for i in range(npt)]
        for i, lab in enumerate(labels):
            self.label(xs[i] - step / 2, py0 + ph + 0.05, step, lab_h - 0.05,
                       str(lab), size=size, align="CENTER", valign="TOP",
                       color=self.P.text)
        for si, (name, vs) in enumerate(pairs):
            c = cols[si]
            for i in range(npt - 1):
                self.line(xs[i], ypos(vs[i]), xs[i + 1], ypos(vs[i + 1]),
                          color=c, weight=2.0, free=True)
            if markers:
                mr = 0.05
                for i in range(npt):
                    self.shape(xs[i] - mr, ypos(vs[i]) - mr, mr * 2, mr * 2,
                               kind="ELLIPSE", fill=c, stroke=self.P.white,
                               stroke_weight=1.0)
            if end_values:
                self.label(xs[-1] - 0.5, ypos(vs[-1]) - 0.30, 1.0, 0.2,
                           _fmt(vs[-1]) + unit, size=9, bold=True,
                           align="CENTER", valign="BOTTOM", color=self.P.text)
        return y + h

    # ---- 円 / ドーナツグラフ ----

    def pie(self, x, y, size, items, *, donut=True, colors=None,
            legend_w=None, label_size=10, unit="", bg="#FFFFFF") -> float:
        """円グラフ（既定はドーナツ）。items は [(ラベル, 数値), …]。

        Slides API には角度を指定できる扇形が無いため、円だけ SVG を PNG に
        焼いて画像として貼る（cairosvg か rsvg-convert が要る）。凡例は右側に
        図形で描くので、文字の検査は通常どおり効く。`--dry-run` では円の
        代わりに同じ大きさの円形プレースホルダを置いて座標だけ検査する。

        - 構成比を見せる用途にだけ使う。系列が 7 つ以上なら「その他」に
          まとめるか、棒グラフ（vbars / hbars）に変えること
        - 12 時から時計回り、渡した順に描く（勝手に並べ替えない）
        - ドーナツの穴と切れ目は `bg` 色で塗る（既定は白）。白背景以外の
          スライドでは `bg` を背景色に合わせること

        戻り値は下端 y（= y + size）。
        """
        vals = [float(v) for _, v in items]
        if any(v < 0 for v in vals) or sum(vals) <= 0:
            raise ValueError("pie の値は正の数の合計が必要です")
        if len(items) > 6:
            print(f"  warn: 円グラフに {len(items)} 系列は多すぎます。"
                  "「その他」に畳むか棒グラフを検討してください", file=sys.stderr)
        cols = list(colors) if colors else self.P.series(len(items))
        total = sum(vals)

        if getattr(self.deck, "dry", False):
            self.shape(x, y, size, size, kind="ELLIPSE",
                       fill=self.P.surface, stroke=self.P.border)
        else:
            png = self._pie_png(vals, cols, donut, bg)
            self.image(x, y, size, size, png, fit="contain",
                       alt="円グラフ: " + ", ".join(str(n) for n, _ in items))

        lx = x + size + 0.25
        lw = legend_w or 2.4
        row_h = 0.30
        ly = y + max(0.0, (size - row_h * len(items)) / 2)
        for i, (name, v) in enumerate(items):
            ry = ly + i * row_h
            self.shape(lx, ry + 0.085, 0.16, 0.13, kind="RECTANGLE",
                       fill=cols[i], stroke=None)
            pct = v / total * 100
            cap = (f"{name}  {_fmt(v)}{unit}（{pct:.0f}%）" if unit
                   else f"{name}  {pct:.0f}%")
            self.label(lx + 0.26, ry, lw - 0.26, row_h, cap, size=label_size,
                       align="START", valign="MIDDLE", color=self.P.text)
        return y + size

    def _pie_png(self, vals, cols, donut, bg) -> str:
        """円グラフの SVG を組み立てて PNG に焼き、パスを返す。"""
        px = 1024
        cx = cy = px / 2
        r = px / 2 - 8
        key = hashlib.sha256(
            f"{vals}|{cols}|{donut}|{bg}".encode()).hexdigest()[:16]
        os.makedirs(CACHE_DIR, exist_ok=True)
        path = os.path.join(CACHE_DIR, f"pie-{key}.png")
        if os.path.exists(path):
            return path

        total = sum(vals)
        parts = []
        a0 = -90.0
        for v, c in zip(vals, cols):
            if v <= 0:
                continue
            sweep = v / total * 360.0
            if sweep >= 360.0 - 1e-6:
                parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{c}"/>')
            else:
                a1 = a0 + sweep
                x1 = cx + r * math.cos(math.radians(a0))
                y1 = cy + r * math.sin(math.radians(a0))
                x2 = cx + r * math.cos(math.radians(a1))
                y2 = cy + r * math.sin(math.radians(a1))
                large = 1 if sweep > 180 else 0
                # 切れ目は 2px 相当の縁取りで作る（データの隙間ではなく見た目の分離）
                parts.append(
                    f'<path d="M{cx:.2f},{cy:.2f} L{x1:.2f},{y1:.2f} '
                    f'A{r:.2f},{r:.2f} 0 {large} 1 {x2:.2f},{y2:.2f} Z" '
                    f'fill="{c}" stroke="{bg}" stroke-width="5"/>')
            a0 += sweep
        if donut:
            parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r * 0.56:.2f}" '
                         f'fill="{bg}"/>')
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" '
               f'viewBox="0 0 {px} {px}">' + "".join(parts) + "</svg>")

        tmp = path + f".{os.getpid()}.part"
        try:
            if not (_try_cairosvg(svg, tmp, px) or _try_cli(svg, tmp, px)):
                raise RuntimeError(
                    "円グラフのラスタライズに失敗しました。"
                    "pip install cairosvg（または brew install librsvg）を実行してください")
            os.replace(tmp, path)
        finally:
            if os.path.exists(tmp):
                os.unlink(tmp)
        return path
