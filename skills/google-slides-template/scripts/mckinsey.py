#!/usr/bin/env python3
"""印刷物用（read-alone）デッキの型（`diagrams.Canvas` に混ぜて使うミックスイン）。

マッキンゼー流のコンサルティング資料の作法を部品にしたもの。**読者が独りで
読み切る前提**の資料——配布用・提出用・稟議用——で使う。登壇用の「1 枚 1 メッセージ・
文字は少なく」とは設計が逆で、1 枚に結論・根拠・出典が閉じているのが正しい。

    d = Canvas(deck, slide_id, template)
    b = d.governing_message(0.5, 0.55, 9.0, "受注処理の内製化で年 1,800 万円を削減できる")
    b = d.lead_in(0.5, b + 0.06, 9.0, "現行 3 工程のうち、2 工程は既存システムで代替できる。")
    inner = d.exhibit_frame(0.5, b + 0.18, 5.9, 2.7, 1, "工程別の年間コスト")
    d.vbars(inner[0] + 0.2, inner[1] + 0.15, inner[2] - 0.4, inner[3] - 0.3, [...])
    d.so_what(6.6, b + 0.18, 2.9, 2.7, "上位 2 工程だけで削減額の 8 割を占める")
    d.source_note(0.5, 4.85, 9.0, "2026 年 3 月の業務量調査（n=42）",
                  notes=["※1 人件費は部門平均単価で換算"])

設計の根拠（2026-08 調査）:

- アクションタイトルは **15 語以内・2 行まで・能動態**。「何を見せるか」ではなく
  「何が言えるか」を書く。タイトルだけを順に読むと論旨になる（横の論理）。
- 定量スライドには**必ず出典行**を置く。数値の主張に出典が無いものは載せない。
- 示唆ボックス（kicker）は**使いすぎない**。目安は全体の 2 割以下。タイトルの
  焼き直しを入れない（それはタイトルの仕事）。図に無い新情報も入れない。
- 図表には通し番号を振る。本文・付録から参照できるようにするため。

すべての部品は他と同じ積み上げ規約に従い、**描画領域の下端 y を返す**。
例外は `exhibit_frame` だけで、中身を描くための内側領域 `(x, y, w, h)` を返す。
座標はインチ。描いたら `audit_*` の自己点検を必ず通すこと。
"""
from __future__ import annotations

from colors import lighten, readable_on

# ゴーストデッキのデータ状態。印刷前に「未取得」が残っていないかを見るための区分
GHOST_STATUS = {
    "confirmed": ("確定", "success"),
    "wip": ("作成中", "warning"),
    "missing": ("未取得", "danger"),
}


def _node(tree):
    """ロジックツリーのノードを (ラベル, [子…]) に正規化する。JSON 由来の list も受ける。"""
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


class McKinseyMixin:
    """`Canvas` に印刷物用デッキの型を足すミックスイン。"""

    # 本文の実効行高の係数。label() の行送りと合わせてある
    _LINE = 1.45

    # ---- 1. ガバニングメッセージ（アクションタイトル） ----

    def governing_message(self, x, y, w, text, *, size=17, bar=0.055,
                          color=None, max_words=15) -> float:
        """アクションタイトルを帯つきで描く。戻り値は下端 y。

        テンプレートの TITLE プレースホルダが使えるならそちらを優先する。
        この部品は BLANK レイアウトで組むときと、2 行のタイトルを確実に
        意図した位置に出したいときに使う。

        `max_words` を超えると警告を出す（15 語・2 行が上限という作法）。
        日本語は語で数えられないので、全角 40 字を 1 行の目安として数える。
        """
        if not text or not text.strip():
            raise ValueError("governing_message: text が空です")
        c = color or self.P.primary
        # 行数の見積もり。全角 1・半角 0.5 で数え、1 行の収容字数で割る
        width = sum(1.0 if ord(ch) > 0x2E80 else 0.5 for ch in text)
        per_line = max(1.0, (w - 0.3) * 72 / size)
        lines = max(1, int(width / per_line + 0.999))
        if lines > 2:
            print(f"  warn: アクションタイトルが {lines} 行になります。"
                  f"2 行までに削ってください（「{text[:20]}…」）")
        h = max(0.42, lines * size * self._LINE * 1.05 / 72 + 0.14)
        self.shape(x, y, bar, h, kind="RECTANGLE", fill=c, stroke=None)
        self.label(x + bar + 0.14, y, w - bar - 0.14, h, text,
                   size=size, bold=True, color=self.P.text,
                   valign="MIDDLE", line_spacing=105)
        return y + h

    # ---- 2. リードイン（導入文） ----

    def lead_in(self, x, y, w, text, *, size=10.5, rule=True) -> float:
        """タイトル直下の 1〜2 行。「この図を何のために見るか」を書く。戻り値は下端 y。

        印刷物では読者が独りで読むので、図の前に読み方を渡す。
        登壇用デッキでは口頭で言えばよいので、通常は不要。
        """
        if not text or not text.strip():
            raise ValueError("lead_in: text が空です")
        top = y
        if rule:
            self.shape(x, y, w, 0.012, kind="RECTANGLE",
                       fill=self.P.border, stroke=None)
            top = y + 0.012 + 0.06
        width = sum(1.0 if ord(ch) > 0x2E80 else 0.5 for ch in text)
        # audit_text_fit と同じ前提で見積もる: 左右パディング 0.1in ずつ、
        # 行高は _LINE × line_spacing。ここをけちると検査に自分で引っかかる
        per_line = max(1.0, (w - 0.2) * 72 / size)
        lines = max(1, int(width / per_line + 0.999))
        h = lines * size * self._LINE * 1.25 / 72 + 0.06
        self.label(x, top, w, h, text, size=size, color=self.P.muted,
                   line_spacing=125)
        return top + h

    # ---- 3. 示唆ボックス（So what / kicker） ----

    def so_what(self, x, y, w, h, text, *, label="示唆", size=10.5,
                accent=None, points=None) -> float:
        """図から読み取れることを言葉で置く。戻り値は下端 y。

        **使いすぎない。** 目安は全体の 2 割以下。次の 2 つは書いてはならない:

        - タイトルの焼き直し（スライドの主張はタイトルの仕事）
        - 図に無い新情報（根拠のない主張になる）

        左端のアクセントバーに合わせ、角は丸めない（スキル共通の規約）。
        """
        if not text or not text.strip():
            raise ValueError("so_what: text が空です")
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

    # ---- 4. 出典・注記行 ----

    def source_note(self, x, y, w, source, *, notes=None, size=7.5,
                    rule=True, prefix="出典") -> float:
        """ページ下端の出典行と注記。戻り値は下端 y。

        **数値を載せたスライドには必ず置く。** 出典を書けない数字は載せない。
        `notes` は本文中の「※1」に対応する注記のリストで、出典より上に出る。
        """
        if not source or not str(source).strip():
            raise ValueError("source_note: source が空です（出典の無い数値は載せない）")
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

    # ---- 5. 図表枠（Exhibit） ----

    def exhibit_frame(self, x, y, w, h, number, title, *, size=9.5,
                      pad=0.14, label_prefix="図表"):
        """図表番号つきの枠を描き、**中身を描くための内側領域 (x, y, w, h) を返す**。

        この部品だけ戻り値が積み上げ規約と違う（枠の中に別の図を描くため）。
        番号は本文や付録から参照するために振る。呼び出し側で通し番号を管理すること。
        """
        if h <= 0.6 or w <= 1.0:
            raise ValueError(f"exhibit_frame: 枠が小さすぎます（w={w}, h={h}）")
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

    # ---- 6. ロジックツリー（MECE） ----

    def mece_tree(self, x, y, w, h, tree, *, size=10, gap=0.34,
                  root_fill=None, node_h=None) -> float:
        """左から右へ広がるロジックツリー。戻り値は下端 y。

        `orgchart`（patterns）が縦の体制図なのに対し、こちらは論点の分解を
        横に展開する。分解が MECE か（漏れなく・重複なく）は描く側の責任で、
        この部品は形しか保証しない。

        `tree` は `(ラベル, [子…])`。子は同じ形の入れ子・文字列・
        `{"label": …, "children": […]}` のいずれでもよい。
        """
        depth, leaves = _depth(tree), _leaves(tree)
        if depth > 4:
            raise ValueError(f"mece_tree: 深さ {depth} は読めません。3 階層までに分割してください")
        col_w = (w - gap * (depth - 1)) / depth
        if col_w < 1.1:
            raise ValueError(f"mece_tree: 1 列 {col_w:.2f}in は狭すぎます。w を広げるか階層を減らしてください")
        row_h = h / leaves
        nh = node_h or min(row_h - 0.12, 0.78)
        if nh < 0.3:
            raise ValueError(f"mece_tree: 葉が {leaves} 個で 1 行 {row_h:.2f}in は狭すぎます")

        def draw(node, level: int, top: float) -> tuple[float, float]:
            """(中心 y, 占有した高さ) を返す。"""
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
                # 親の右辺 → 中間 → 子の左辺。折れ点は free（接しないのが正しい線）
                midx = cx + col_w + gap / 2
                self.line(cx + col_w, cy, midx, cy, color=self.P.border, free=True)
                self.line(midx, cy, midx, ccy, color=self.P.border, free=True)
                self.line(midx, ccy, cx + col_w + gap, ccy,
                          color=self.P.border, free=True)
                child_top += cspan
            return cy, span

        draw(tree, 0, y)
        return y + h

    # ---- 7. ウォーターフォール ----

    def waterfall(self, x, y, w, h, items, *, unit="", size=9.5,
                  bar_ratio=0.62, max_value=None, good="up") -> float:
        """増減の橋渡し（ウォーターフォール）。戻り値は下端 y。

        `items` は `(ラベル, 値)` か `(ラベル, 値, 種別)`。種別は
        `"total"`（0 から積む合計）か `"delta"`（前の合計から浮かせる増減。既定）。
        合計は primary。増減の色は `good` で決める:

        - `good="up"`（既定）… 増加が success 緑（売上・利益の橋）
        - `good="down"` … 減少が success 緑（コスト・リードタイム削減の橋）

        符号だけで塗ると、コスト削減の文脈で「削減＝赤」になり意味が逆転する。

        **最後の total は積算と一致していなければならない。** ずれていたら
        `ValueError`（データの取り違えをここで止める）。
        """
        if good not in ("up", "down"):
            raise ValueError(f"waterfall: good は 'up' か 'down'（指定: {good!r}）")
        if len(items) < 3:
            raise ValueError("waterfall: 3 項目未満では橋渡しになりません")
        rows = []
        for it in items:
            if len(it) == 3:
                label, value, kind = it
            else:
                (label, value), kind = it, "delta"
            if kind not in ("total", "delta"):
                raise ValueError(f"waterfall: 未知の種別 '{kind}'（total か delta）")
            rows.append((label, float(value), kind))
        if rows[0][2] != "total":
            raise ValueError("waterfall: 先頭は total（起点の合計）である必要があります")

        # 積算とバーの上下端を決める
        cum, bars = 0.0, []
        for label, value, kind in rows:
            if kind == "total":
                if bars and abs(value - cum) > 1e-6:
                    raise ValueError(
                        f"waterfall: 合計 '{label}' が積算と一致しません "
                        f"(指定 {value:g} / 積算 {cum:g})")
                lo, hi = 0.0, value
                cum = value
            else:
                lo, hi = (cum, cum + value) if value >= 0 else (cum + value, cum)
                cum += value
            bars.append((label, value, kind, lo, hi))

        top = max_value if max_value is not None else max(hi for *_, hi in bars)
        if top <= 0:
            raise ValueError("waterfall: 上限が 0 以下です")
        if min(lo for *_, lo, _ in bars) < 0:
            raise ValueError("waterfall: 負の領域に入る系列は表現できません（基線はゼロ固定）")

        val_h, cat_h = 0.24, 0.30
        plot_h = h - val_h - cat_h
        if plot_h < 0.5:
            raise ValueError(f"waterfall: h={h} では低すぎます（数値とラベルで {val_h + cat_h}in 使う）")
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
            # 橋渡しの点線。前の棒の上端（または下端）と次をつなぐ
            connect_y = base_y - (hi if value >= 0 or kind == "total" else lo) / top * plot_h
            if prev_right is not None:
                self.line(prev_right[0], prev_right[1], bx, prev_right[1],
                          color=self.P.border, dashed=True, free=True)
            prev_right = (bx + bw, connect_y if kind == "total" else
                          base_y - (hi if value >= 0 else lo) / top * plot_h)
        return y + h

    # ---- 8. 評価マトリクス（ドット評価） ----

    def rating_matrix(self, x, y, w, columns, rows, *, levels=4, size=10,
                      label_w=None, row_h=0.42, dot=0.13) -> float:
        """行 × 列の評価をドットの数で示す。戻り値は下端 y。

        `rows` は `(ラベル, [値, …])` で、値は 0〜`levels` の整数。
        列の数と値の数は一致していなければならない。

        Slides API には角度を指定できる扇形が無く、ハーヴェイボールの
        「4 分の 1 だけ塗る」が描けないため、塗り分けたドットの数で表す。
        **白黒印刷でも塗り／抜きが判別できる**ので、印刷物ではむしろ扱いやすい。
        """
        if not rows:
            raise ValueError("rating_matrix: rows が空です")
        lw = label_w if label_w is not None else min(2.6, w * 0.34)
        col_w = (w - lw) / len(columns)
        if col_w < levels * (dot + 0.05):
            raise ValueError(f"rating_matrix: 1 列 {col_w:.2f}in にドット {levels} 個は入りません")
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
                    f"rating_matrix: 行 '{label}' の値が {len(values)} 個、列は {len(columns)} 個")
            ry = top + i * row_h
            if i % 2 == 1:
                self.shape(x, ry, w, row_h, kind="RECTANGLE",
                           fill=self.P.surfaceAlt, stroke=None)
            self.label(x + 0.06, ry, lw - 0.12, row_h, label, size=size,
                       valign="MIDDLE", color=self.P.text)
            for j, v in enumerate(values):
                if not isinstance(v, int) or not 0 <= v <= levels:
                    raise ValueError(f"rating_matrix: 値 {v!r} は 0〜{levels} の整数にしてください")
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

    # ---- 9. エグゼクティブサマリー（SCR） ----

    def exec_summary(self, x, y, w, h, situation, complication, resolution, *,
                     points=None, size=10.5, labels=("状況", "課題", "答え")) -> float:
        """状況 → 課題 → 答え の 3 段で結論を先に置く。戻り値は下端 y。

        ピラミッド原則の入口。**この 1 枚だけ読めば意思決定できる**ことが条件で、
        続く本編はここの根拠を並べたものになる。`points` は答えを支える論点
        （3〜5 個。それ以上に分けるなら本編の章立てを見直す）。
        """
        blocks = [(labels[0], situation), (labels[1], complication), (labels[2], resolution)]
        if points and len(points) > 5:
            raise ValueError(f"exec_summary: 論点が {len(points)} 個。5 個までに束ねてください")
        pts_h = 0.0
        if points:
            pts_h = 0.34 + len(points) * 0.3
        block_h = (h - pts_h - 0.16 * 2) / 3
        if block_h < 0.5:
            raise ValueError(f"exec_summary: h={h} では 3 ブロックが入りません")
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

    # ---- 10. 横の論理（ストーリーライン） ----

    def storyline(self, x, y, w, titles, *, size=10, row_h=0.44,
                  highlight=None) -> float:
        """アクションタイトルを順に並べ、読むと論旨になることを確かめる図。戻り値は下端 y。

        `titles` は文字列か `(ページ番号, タイトル)`。左の縦罫で連結する。
        **設計に使う図**でもある: ここで論旨が通らないなら、スライドを作る前に
        構成を直す（ゴーストデッキ → この図 → 生成、の順）。
        """
        if not titles:
            raise ValueError("storyline: titles が空です")
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
            # 番号ラベルの枠は円より広めに取る。audit_text_fit は左右 0.1in の
            # パディングを見込むため、円と同寸だと機械的に「溢れ」と判定される
            self.label(rail_x - 0.2, ry + row_h / 2 - 0.11, 0.42, 0.23, str(num),
                       size=7, bold=True, align="CENTER", valign="MIDDLE",
                       color=self.P.white if on else c)
            self.label(x + 0.56, ry, w - 0.56, row_h, text, size=size,
                       bold=on, valign="MIDDLE", color=self.P.text)
        return y + len(rows) * row_h

    # ---- 11. ゴーストデッキ ----

    def ghost(self, x, y, w, h, slides, *, cols=4, size=8, gap=0.16) -> float:
        """骨子だけのスライドを並べたゴーストデッキ。戻り値は下端 y。

        `slides` は `(番号, アクションタイトル, 図表の説明, 状態)`。状態は
        `confirmed` / `wip` / `missing`。**清書の前にここで論旨とデータの
        当てを確かめる**ための図で、成果物ではなく設計の道具。
        """
        if not slides:
            raise ValueError("ghost: slides が空です")
        rows = (len(slides) + cols - 1) // cols
        cw = (w - gap * (cols - 1)) / cols
        ch = (h - gap * (rows - 1)) / rows
        if cw < 1.2 or ch < 0.9:
            raise ValueError(f"ghost: 1 枚 {cw:.2f}×{ch:.2f}in は小さすぎます")
        for i, item in enumerate(slides):
            num, title, exhibit, status = (list(item) + ["confirmed"])[:4]
            if status not in GHOST_STATUS:
                raise ValueError(f"ghost: 未知の状態 '{status}'（{sorted(GHOST_STATUS)}）")
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
