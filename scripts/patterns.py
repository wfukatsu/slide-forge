#!/usr/bin/env python3
"""ビジネスフレームワーク図（`diagrams.Canvas` に混ぜて使うミックスイン）。

新規事業提案・企画稟議のデッキで定番の「型」を部品にしたもの。
`illustrations` が一般的な比喩図（ピラミッド・氷山…）を担うのに対し、
こちらはビジネスフレームワークそのものの形を描く。

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

すべての図は他の部品と同じ積み上げ規約に従い、**描画領域の下端 y を返す**。
座標はインチ。描いたら `audit_*` の自己点検を必ず通すこと。
"""
from __future__ import annotations

from colors import darken, lighten, readable_on
from _i18n import t, register

register({
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
})

# lean_canvas のブロック定義。(キー, 見出し) を標準のリーンキャンバスの並びで持つ
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


def _node(tree):
    """orgchart のノードを (ラベル, [子…]) に正規化する。JSON 由来のリストも受ける。"""
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
    """`Canvas` にビジネスフレームワーク図を足すミックスイン。"""

    # ---- ポジショニングマップ ----

    def posmap(self, x, y, w, h, points, *, x_axis=("低", "高"),
               y_axis=("低", "高"), highlight=None, highlight_color=None,
               size=10, bubble=0.72) -> float:
        """ポジショニングマップ（2 軸上の位置関係）。戻り値は下端 y。

        points は (ラベル, px, py)。px / py は 0〜1 の相対座標で、
        0 が左・下、1 が右・上。x_axis / y_axis は軸の両端ラベル (低い側, 高い側)。
        highlight に挙げたラベル（例「自社」）だけ強調色で塗る。

        `matrix()` が「4 象限への分類」を見せるのに対し、こちらは競合との
        「位置関係」を見せる。象限に名前を付けたいだけなら matrix() を使うこと。
        """
        cap_h = 0.30                       # 上下の軸端ラベルの高さ
        # 左右の軸端ラベルは箱に入れる。幅は長いほうのラベルが 1 行で入る分を
        # 確保する（固定幅だと「8 字＋1 字」のような折り返しになりやすい）
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
        # 軸端ラベル。上下はプロットの外、左右は軸の延長線上に白い箱で置く
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

    # ---- ガントチャート ----

    def gantt(self, x, y, w, h, columns, rows, *, label_w=None, size=10,
              colors=None, zebra=True) -> float:
        """ガントチャート（線表）。戻り値は下端 y。

        columns は期間の見出し（例 ["4月", "5月", "6月"]）。rows は
        (行ラベル, 開始, 終了) か (行ラベル, 開始, 終了, バーのラベル)。
        開始・終了は列単位の小数で、0 が最初の列の左端、len(columns) が右端。
        **開始 == 終了 の行はマイルストーン（◆）**として描く。

        バーの重なりや依存関係の矢印は表現しない。細かい依存を見せたい図は
        表（table）で書くほうが編集もしやすい。
        """
        ncols = len(columns)
        lw = label_w if label_w is not None else min(1.8, w * 0.20)
        head_h = 0.34
        track_x, track_w = x + lw, w - lw
        cu = track_w / ncols               # 1 列ぶんの幅
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
            if end - start < 1e-9:         # マイルストーン
                ms = 0.20
                self.shape(track_x + start * cu - ms / 2, cyy - ms / 2, ms, ms,
                           kind="DIAMOND", fill=darken(c, 0.15), stroke=None)
                if caption:
                    self.label(track_x + start * cu + ms / 2 + 0.06, cyy - 0.13,
                               max(0.8, track_w - start * cu - ms), 0.26, caption,
                               size=size - 1, bold=True, align="START",
                               valign="MIDDLE", color=self.P.text)
                continue
            bx, bw = track_x + start * cu, (end - start) * cu
            self.shape(bx, cyy - bar_h / 2, bw, bar_h, kind="ROUND_RECTANGLE",
                       fill=c, stroke=None)
            if caption:
                need = self._em(caption) * (size - 1) / 72.0 * 1.1 + 0.16
                if need <= bw:             # 入るならバーの中、無理なら右隣
                    self.label(bx, cyy - 0.13, bw, 0.26, caption, size=size - 1,
                               align="CENTER", valign="MIDDLE",
                               color=readable_on(c))
                else:
                    self.label(bx + bw + 0.06, cyy - 0.13,
                               max(0.6, x + w - bx - bw - 0.08), 0.26, caption,
                               size=size - 1, align="START", valign="MIDDLE",
                               color=self.P.muted)
        return y + h

    # ---- 体制図・組織図 ----

    def orgchart(self, x, y, w, h, tree, *, size=10, node_h=None,
                 root_fill=None) -> float:
        """体制図（トップダウンの木）。戻り値は下端 y。

        tree は (ラベル, [子…])。子は同じ形の入れ子・文字列・
        {"label": …, "children": […]} のいずれでもよい。ラベルを
        「役割\\n氏名」のように 2 行にすると典型的な体制図の見た目になる。

        列の幅は葉の数で自動配分する。深さ 4 以上や葉が 8 を超える木は
        文字が潰れるので、部門ごとに orgchart を並べて分割すること。
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

    # ---- リーンキャンバス ----

    def lean_canvas(self, x, y, w, h, blocks, *, size=9, title_size=9.5) -> float:
        """リーンキャンバス（9 ブロック）。戻り値は下端 y。

        blocks はキー → 内容（文字列か文字列のリスト）の辞書。キーは
        problem / solution / key_metrics / uvp / advantage / channels /
        segments / cost / revenue（`LEAN_CANVAS_KEYS` 参照）。
        無いキーのブロックは枠だけ描く。

        9 ブロックすべてに長文を入れると必ず溢れる。各ブロック 2〜3 項目・
        1 項目 15 文字程度までに要約してから渡すこと。
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
        cells = {                          # キー → (x, y, w, h)
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

    # ---- 入れ子の円（TAM / SAM / SOM） ----

    def nested_circles(self, x, y, w, h, rings, *, size=10, colors=None) -> float:
        """入れ子の円で全体と部分の規模感を見せる（TAM / SAM / SOM など）。
        戻り値は下端 y。

        rings は**外側から**順に (ラベル, 値の表示) か文字列。円は下端を
        揃えて重ね、右側にラベルを引き出す。値は出典のある数値にだけ使うこと。
        """
        n = len(rings)
        if n < 2:
            raise ValueError(t("nested_circles needs at least 2 rings"))
        d0 = min(h, w * 0.52)
        ccx = x + d0 / 2
        base = y + (h + d0) / 2            # 円の下端（縦中央に配置）
        cols = colors or [lighten(self.P.primary, 0.82 - 0.62 * i / (n - 1))
                          for i in range(n)]
        lab_x = ccx + d0 / 2 + 0.35
        lab_w = x + w - lab_x
        if lab_w < 1.2:
            raise ValueError(t("w={w} leaves no room for the labels", w=w))
        # ラベルは行間を広めに取る。詰めると「値」と次のリングの「名前」が
        # ひとかたまりに見え、どの円の値か読み違える
        lab_h = 0.52
        row_gap = max(0.24, (h - lab_h * n) / max(n - 1, 1) - lab_h * 0.4)
        row_gap = min(row_gap, 0.55)
        for i, ring in enumerate(rings):
            name, value = (ring if isinstance(ring, (tuple, list))
                           else (ring, None))
            d = d0 * (n - i) / n
            self.shape(ccx - d / 2, base - d, d, d, kind="ELLIPSE",
                       fill=cols[i], stroke=self.P.white, stroke_weight=1.5)
            # 引き出し線の起点は、そのリングだけが見えている頂部の帯の中心
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

    # ---- 顧客・キーマンの声 ----

    def testimonial(self, x, y, w, h, quote, name, *, role=None, points=None,
                    icon="person", size=10, quote_size=13) -> float:
        """引用カード（顧客の生の声・社内キーマンのコメント）。戻り値は下端 y。

        左に人物ピクトグラムと氏名・肩書、右に引用文。points を渡すと
        引用の下に箇条書きの補足を置く。**引用は実在の発言にだけ使うこと**
        （デザイン部品が発言をでっち上げてよい理由にはならない）。
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
