#!/usr/bin/env python3
"""図解主体のデッキを宣言的に書くためのキット。

デッキは「1 モジュール = 1 デッキ」で書く。モジュールは `slide()` / `plain()` で
スライドを登録し、`SLIDES` に溜める。`render_deck.py` が生成し、
`validate_layout.py` が API を呼ばずに座標を検査する。

    # mydeck.py
    from deckkit import *

    plain(layout="COVER", title="タイトル", subtitle="サブタイトル")

    @slide("結論を述べるアクションタイトル", note="スピーカーノート")
    def s_overview(d):
        layers(d, X0, DY0, W, [
            ("アプリ",  "業務アプリケーション",   d.P.primary),
            ("基盤",    "ミドルウェア",           d.P.primaryDark),
        ])
        foot(d, ["・要点を1行で"], "提供: ... ｜ 状況: GA")

座標はすべてインチ。原点はスライド左上。`d` は diagrams.Canvas。

レイアウトの安全域（LAYOUT）はテンプレートのページサイズから算出する。
既定値は 10 x 5.625 インチ（16:9）のテンプレートで実測した値。
"""
from __future__ import annotations

import math
import os
import sys
import unicodedata

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from diagrams import Canvas, Palette, darken, lighten, mix, readable_on  # noqa: E402,F401

__all__ = [
    # 登録
    "SLIDES", "slide", "plain", "reset",
    # レイアウト定数
    "X0", "W", "XE", "DY0", "DY1", "NY", "EY", "PAGE_W", "PAGE_H",
    "TITLE_EM_MAX", "BODY_FONT_SIZE", "BODY_LINE_SPACING", "BODY_MAX_LINES",
    "configure_layout",
    # 下部固定要素
    "foot", "FOOT_MODE",
    # 複合パーツ（基本）
    "caption", "grouphead", "zone", "db", "grid", "layers", "steps_v",
    "pill", "pills", "xmark", "checkmark", "banner", "kv_rows",
    # 複合パーツ（レイアウトパターン）
    "tone_colors", "tone_solid",
    "compare_panels", "swimlane", "timeline", "tree", "decision",
    "quadrant", "matrix_map", "roadmap", "pyramid", "cycle", "funnel",
    "callouts", "stats", "checklist", "pipeline", "legend",
    # 計測
    "em", "fits_one_line",
    # 再エクスポート
    "Canvas", "Palette", "lighten", "darken", "mix", "readable_on",
]

# ---------------------------------------------------------------------------
# レイアウト定数
#
# 16:9（10 x 5.625in）テンプレートでの実測値。
#   - タイトルのプレースホルダは y=0.126, h=0.351 → 1 行なら y=0.48 で終わる
#   - マスターのロゴ・著作権フッターは y=5.197 付近から始まる
#   - よって図は y=0.84〜4.30 に収め、その下を要点行とエディション行に充てる
# 別サイズのテンプレートを使う場合は configure_layout() で上書きする。
# ---------------------------------------------------------------------------
PAGE_W, PAGE_H = 10.0, 5.625
X0, W, XE = 0.5, 9.0, 9.5
DY0, DY1 = 0.84, 4.30           # 図を描いてよい上端・下端
NY = 4.38                       # 要点行（最大2行）
EY = 4.86                       # 提供エディション行（1行）

# タイトルが 1 行に収まる全角換算幅の上限。
# 20pt bold で em=31.0 は 1 行、em=33.0 は 2 行になったため 30.5 を上限とする。
# 2 行になるとタイトルが DY0 を侵食して図と重なる。
TITLE_EM_MAX = 30.5

# 本文プレースホルダに流し込む場合の推奨値。
# Google の lineSpacing はフォント本来の行高（Noto Sans JP で約 1.45em）に対する
# 百分率なので、12pt / 120% で 1 行あたり約 0.29in。h=4.068in に約 14 行入る。
BODY_FONT_SIZE = 12
BODY_LINE_SPACING = 120
BODY_MAX_LINES = 14


def configure_layout(*, page_w=None, page_h=None, margin=None,
                     diagram_top=None, diagram_bottom=None,
                     note_y=None, edition_y=None, title_em_max=None):
    """ページサイズや安全域を上書きする。テンプレートが 16:9 でない場合に使う。

    margin だけ渡せば X0 / W / XE を再計算する。
    """
    global PAGE_W, PAGE_H, X0, W, XE, DY0, DY1, NY, EY, TITLE_EM_MAX
    if page_w is not None:
        PAGE_W = page_w
    if page_h is not None:
        PAGE_H = page_h
    if margin is not None:
        X0 = margin
    XE = PAGE_W - X0
    W = XE - X0
    if diagram_top is not None:
        DY0 = diagram_top
    if diagram_bottom is not None:
        DY1 = diagram_bottom
    if note_y is not None:
        NY = note_y
    if edition_y is not None:
        EY = edition_y
    if title_em_max is not None:
        TITLE_EM_MAX = title_em_max


# ---------------------------------------------------------------------------
# 計測
# ---------------------------------------------------------------------------

def em(s: str) -> float:
    """文字列の全角換算幅。全角=1.0、半角=0.5 で数える。"""
    return sum(1.0 if unicodedata.east_asian_width(c) in "WFA" else 0.5 for c in s)


def fits_one_line(title: str) -> bool:
    return em(title) <= TITLE_EM_MAX


# ---------------------------------------------------------------------------
# スライドの登録
# ---------------------------------------------------------------------------

SLIDES: list[dict] = []


def reset() -> None:
    """登録済みスライドを消す（テストや再読み込み用）。"""
    SLIDES.clear()


def slide(title=None, *, layout="TITLE_ONLY", note=None, **kw):
    """図を描くスライドを登録するデコレータ。

    デコレートした関数は draw(d) として呼ばれる。d は diagrams.Canvas。
    layout はテンプレートのロール名またはレイアウトキー。図を自分で描くので
    本文プレースホルダを持たない TITLE_ONLY 系が既定。
    """
    def deco(fn):
        SLIDES.append(dict(layout=layout, title=title, notes=note, draw=fn, **kw))
        return fn
    return deco


def plain(*, layout, **kw):
    """プレースホルダだけで完結するスライド（表紙・中扉・裏表紙など）を登録する。

    title / subtitle / body / bodies / notes をそのまま渡せる。
    body に配列を渡すと改行で連結される。
    """
    SLIDES.append(dict(layout=layout, draw=None, **kw))


# ---------------------------------------------------------------------------
# 下部の固定要素
#
# FOOT_MODE が True の間に描かれた図形は validate_layout の境界検査から外れる。
# 要点行とエディション行は DY1 より下に置くのが正しいため。
# ---------------------------------------------------------------------------

FOOT_MODE = [False]


def foot(d, points=None, edition=None):
    """スライド下部に要点（最大2行）と提供状況の行を置く。

    points はスライドの持ち帰りメッセージ。edition は「提供: ... ｜ 状況: GA」など、
    機能ページで一貫して示したい補足。どちらも省略できる。
    """
    FOOT_MODE[0] = True
    try:
        if points:
            d.label(X0, NY, W, 0.46, "\n".join(points), size=10.5,
                    align="START", valign="TOP", color=d.P.text, line_spacing=115)
        if edition:
            d.label(X0, EY, W, 0.22, edition, size=9,
                    align="START", valign="TOP", color=d.P.muted)
    finally:
        FOOT_MODE[0] = False


# ---------------------------------------------------------------------------
# 複合パーツ
# ---------------------------------------------------------------------------

def caption(d, x, y, w, text, *, size=9, color=None, align="CENTER", h=0.22):
    """図の下に添える小さな説明。"""
    return d.label(x, y, w, h, text, size=size, align=align, valign="TOP",
                   color=color or d.P.muted, line_spacing=115)


def grouphead(d, x, y, w, text, *, fill=None, size=10, h=0.28):
    """帯状の見出し。"""
    return d.shape(x, y, w, h, kind="RECTANGLE",
                   fill=fill or lighten(d.P.primary, 0.86), stroke=None,
                   text=text, size=size, bold=True, color=d.P.primaryDark)


def zone(d, x, y, w, h, label=None, *, fill=None, stroke=None, size=9):
    """要素をまとめる領域。左上に小見出しを置ける。

    領域の中身は y + 0.34 以降に描くと見出しと重ならない。
    """
    d.shape(x, y, w, h, kind="ROUND_RECTANGLE", fill=fill or "#FBFCFE",
            stroke=stroke or lighten(d.P.primary, 0.72), stroke_weight=1.0)
    if label:
        d.label(x + 0.1, y + 0.06, w - 0.2, 0.24, label, size=size, bold=True,
                align="START", valign="TOP", color=d.P.primaryDark)


def banner(d, y, text, *, tone="info", size=9, h=0.34, x=None, w=None):
    """全幅の注意書き・要約バー。tone は info / good / warn / bad。"""
    tones = {
        "info": (lighten(d.P.primary, 0.90), lighten(d.P.primary, 0.62), d.P.text),
        "good": (lighten(d.P.success, 0.86), None, darken(d.P.success, 0.45)),
        "warn": (lighten(d.P.warning, 0.74), None, darken(d.P.warning, 0.55)),
        "bad": (lighten(d.P.danger, 0.88), lighten(d.P.danger, 0.55), darken(d.P.danger, 0.25)),
    }
    fill, stroke, col = tones.get(tone, tones["info"])
    return d.shape(x if x is not None else X0, y, w if w is not None else W, h,
                   kind="ROUND_RECTANGLE", fill=fill, stroke=stroke,
                   text=text, size=size, bold=True, color=col)


def db(d, x, y, w, h, name, *, sub=None, fill="#FFFFFF", stroke=None):
    """データベースの円柱アイコン＋下部ラベル。

    ラベルは h の下に約 0.22in（sub があれば 0.42in）はみ出すので、
    下端の余裕を見て y を決めること。
    """
    d.shape(x, y, w, h, kind="CAN", fill=fill, stroke=stroke or d.P.muted,
            stroke_weight=1.0)
    d.label(x - 0.2, y + h + 0.03, w + 0.4, 0.22, name, size=8.5,
            align="CENTER", valign="TOP", color=d.P.text)
    if sub:
        d.label(x - 0.2, y + h + 0.24, w + 0.4, 0.2, sub, size=7.5,
                align="CENTER", valign="TOP", color=d.P.muted)


def grid(d, x, y, w, cols, rows, *, col_w=None, head_h=0.32, row_h=0.30,
         size=9, head_size=9, first_align="START", head_fill=None,
         cell_colors=None):
    """表。cols は見出しの配列、rows は行の配列（各行はセルの配列）。

    cell_colors(i, j, cell) -> (fill, color) | None で、セルごとに配色できる。
    ○×や可否を色で示すときに使う。戻り値は表の下端 y。
    """
    n = len(cols)
    if col_w is None:
        col_w = [w * 0.34] + [(w - w * 0.34) / (n - 1)] * (n - 1)
    hf = head_fill or lighten(d.P.primary, 0.80)
    cx = x
    for j, c in enumerate(cols):
        d.shape(cx, y, col_w[j], head_h, kind="RECTANGLE", fill=hf, stroke="#FFFFFF",
                stroke_weight=0.75, text=c, size=head_size, bold=True,
                color=d.P.primaryDark, align=(first_align if j == 0 else "CENTER"))
        cx += col_w[j]
    for i, row in enumerate(rows):
        ry = y + head_h + i * row_h
        bg = "#FFFFFF" if i % 2 == 0 else "#F7F9FC"
        cx = x
        for j, cell in enumerate(row):
            col, f = d.P.text, bg
            if cell_colors:
                cc = cell_colors(i, j, cell)
                if cc:
                    f, col = cc
            d.shape(cx, ry, col_w[j], row_h, kind="RECTANGLE", fill=f, stroke="#FFFFFF",
                    stroke_weight=0.75, text=cell, size=size, color=col,
                    bold=(j == 0), align=(first_align if j == 0 else "CENTER"))
            cx += col_w[j]
    return y + head_h + len(rows) * row_h


def layers(d, x, y, w, items, *, row_h=0.62, gap=0.1, label_w=1.55):
    """水平レイヤー図。items は (レイヤー名, 説明, 色) の配列で上から下へ並ぶ。

    アーキテクチャの階層を示すのに使う。戻り値は下端 y。
    """
    for i, (name, body, col) in enumerate(items):
        ry = y + i * (row_h + gap)
        d.shape(x, ry, label_w, row_h, kind="ROUND_RECTANGLE", fill=col, stroke=None,
                text=name, size=10, bold=True, color="#FFFFFF", line_spacing=105)
        d.shape(x + label_w + 0.08, ry, w - label_w - 0.08, row_h,
                kind="ROUND_RECTANGLE", fill=lighten(col, 0.9),
                stroke=lighten(col, 0.6), text=body, size=9.5, color=d.P.text,
                line_spacing=115)
    return y + len(items) * (row_h + gap) - gap


def steps_v(d, x, y, w, items, *, row_h=0.52, gap=0.16, num_w=0.34):
    """番号付きの縦フロー。items は (見出し, 説明) の配列。戻り値は下端 y。"""
    for i, (head, body) in enumerate(items):
        ry = y + i * (row_h + gap)
        d.shape(x, ry + (row_h - num_w) / 2, num_w, num_w, kind="ELLIPSE",
                fill=d.P.primary, stroke=None, text=str(i + 1), size=10,
                bold=True, color="#FFFFFF")
        d.shape(x + num_w + 0.12, ry, w - num_w - 0.12, row_h,
                kind="ROUND_RECTANGLE", fill=lighten(d.P.primary, 0.93),
                stroke=lighten(d.P.primary, 0.7))
        d.label(x + num_w + 0.26, ry + 0.05, w - num_w - 0.4, 0.24, head, size=9.5,
                bold=True, align="START", valign="TOP", color=d.P.primaryDark)
        d.label(x + num_w + 0.26, ry + 0.28, w - num_w - 0.4, row_h - 0.3, body,
                size=8.5, align="START", valign="TOP", color=d.P.text,
                line_spacing=110)
        if i < len(items) - 1:
            d.arrow(x + num_w / 2, ry + row_h + 0.01, x + num_w / 2,
                    ry + row_h + gap - 0.01, color=d.P.primary, weight=1.5)
    return y + len(items) * (row_h + gap) - gap


def kv_rows(d, x, y, w, items, *, key_w=1.85, row_h=0.32, gap=0.06,
            key_fill=None, key_color=None, size=8):
    """「項目 → 補足」の2列リスト。表よりも軽く見せたいときに使う。"""
    for i, (k, v) in enumerate(items):
        ry = y + i * (row_h + gap)
        d.shape(x, ry, key_w, row_h, kind="ROUND_RECTANGLE",
                fill=key_fill or lighten(d.P.info, 0.84), stroke=None,
                text=k, size=size, color=key_color or darken(d.P.info, 0.35))
        d.label(x + key_w + 0.16, ry + 0.05, w - key_w - 0.16, row_h - 0.06, v,
                size=size - 0.5, align="START", color=d.P.text)
    return y + len(items) * (row_h + gap) - gap


def pill(d, x, y, w, h, text, *, fill=None, color=None, size=8.5):
    """角丸のチップ1個。"""
    return d.shape(x, y, w, h, kind="ROUND_RECTANGLE",
                   fill=fill or lighten(d.P.primary, 0.85), stroke=None,
                   text=text, size=size, color=color or d.P.primaryDark, bold=True)


def pills(d, x, y, w, items, *, per_row=5, h=0.26, gap=0.08, fill=None,
          color=None, size=8.5):
    """チップの格子。対応製品や権限の一覧など、順序が重要でない列挙に使う。

    戻り値は下端 y。
    """
    rows = (len(items) + per_row - 1) // per_row
    pw = (w - gap * (per_row - 1)) / per_row
    for i, t in enumerate(items):
        r, c = divmod(i, per_row)
        pill(d, x + c * (pw + gap), y + r * (h + gap), pw, h, t,
             fill=fill, color=color, size=size)
    return y + rows * (h + gap) - gap


def xmark(d, cx, cy, *, r=0.14, color=None):
    """不可・失敗を示す丸バツ。中心座標で置く。"""
    c = color or d.P.danger
    d.shape(cx - r, cy - r, r * 2, r * 2, kind="ELLIPSE", fill=c, stroke=None,
            text="×", size=11, bold=True, color="#FFFFFF")


def checkmark(d, cx, cy, *, r=0.14, color=None):
    """可・成功を示す丸チェック。中心座標で置く。"""
    c = color or d.P.success
    d.shape(cx - r, cy - r, r * 2, r * 2, kind="ELLIPSE", fill=c, stroke=None,
            text="✓", size=10, bold=True, color="#FFFFFF")


# ---------------------------------------------------------------------------
# レイアウトパターン
#
# 共通の約束:
#   - 座標はインチ。x, y は左上。
#   - **戻り値は必ず描画領域の下端 y**。次のブロックはその値を起点に置く。
#     これを守れば「前のブロックがはみ出して次に重なる」事故が起きない。
#   - tone は "primary" / "info" / "good" / "warn" / "bad" / "muted" / "accent"。
# ---------------------------------------------------------------------------

def tone_colors(d, tone="info"):
    """tone 名から (塗り, 枠, 文字色) を返す。淡い面＋濃い文字の組。"""
    P = d.P
    m = {
        "primary": (P.primary, None, "#FFFFFF"),
        "accent": (P.info, None, "#FFFFFF"),
        "info": (lighten(P.primary, 0.90), lighten(P.primary, 0.62), P.text),
        "good": (lighten(P.success, 0.86), lighten(P.success, 0.50), darken(P.success, 0.45)),
        "warn": (lighten(P.warning, 0.72), lighten(P.warning, 0.42), darken(P.warning, 0.55)),
        "bad": (lighten(P.danger, 0.88), lighten(P.danger, 0.52), darken(P.danger, 0.25)),
        "muted": ("#F4F6F9", lighten(P.muted, 0.55), P.text),
    }
    return m.get(tone, m["info"])


def tone_solid(d, tone="info"):
    """tone 名から、点や帯に使う濃い単色を返す。"""
    P = d.P
    return {
        "primary": P.primary,
        "accent": P.info,
        # info は淡い面と対になる中間色にする。primary と同じ色にすると
        # 凡例やマーカーで両者を見分けられない
        "info": lighten(P.primary, 0.35),
        "good": P.success,
        # warning をそのまま暗くすると茶色になり「注意」に見えない。
        # danger 側へ少し寄せて琥珀色にする
        "warn": darken(mix(P.warning, P.danger, 0.25), 0.12),
        "bad": P.danger,
        "muted": lighten(P.muted, 0.20),
    }.get(tone, P.primary)


def _fit(d, x, y, w, h, text, *, size, bold=False, color=None, align="CENTER",
         valign="MIDDLE", ls=110):
    """箱の中にテキストを置く。パターン内部で使う薄いラッパー。"""
    return d.label(x, y, w, h, text, size=size, bold=bold,
                   color=color or d.P.text, align=align, valign=valign,
                   line_spacing=ls)


# ---- 1. 対比パネル（Before / After・A / B） ----

def compare_panels(d, x, y, w, h, left, right, *, gap=0.50, arrow=True):
    """2 枚のパネルを左右に並べて対比する。

    left / right は dict:
        {"title": 見出し, "tone": "bad"/"good"/…, "head": 中央の強調行,
         "items": [項目, …], "note": 下部の注記}
    左右で同じ構造・同じ位置に要素を置くと、差分だけが目に入る。
    """
    pw = (w - gap) / 2
    for i, spec in enumerate((left, right)):
        px = x + i * (pw + gap)
        tone = spec.get("tone", "info")
        fill, stroke, col = tone_colors(d, tone)
        zone(d, px, y, pw, h, spec.get("title"),
             fill=lighten(fill, 0.55), stroke=stroke)
        iy = y + 0.36
        if spec.get("head"):
            d.shape(px + 0.20, iy, pw - 0.40, 0.40, kind="ROUND_RECTANGLE",
                    fill=tone_solid(d, tone), stroke=None, text=spec["head"],
                    size=9.5, bold=True, color="#FFFFFF")
            iy += 0.52
        items = spec.get("items", [])
        if items:
            avail = (y + h - 0.10) - iy - (0.46 if spec.get("note") else 0.0)
            ih = min(0.52, max(0.30, (avail - 0.08 * (len(items) - 1)) / max(1, len(items))))
            for it in items:
                d.shape(px + 0.20, iy, pw - 0.40, ih, kind="ROUND_RECTANGLE",
                        fill=fill, stroke=stroke, text=it, size=8.5, color=col,
                        line_spacing=110)
                iy += ih + 0.08
        if spec.get("note"):
            d.label(px + 0.20, y + h - 0.46, pw - 0.40, 0.40, spec["note"],
                    size=8, align="START", valign="TOP", color=col, line_spacing=115)
    if arrow:
        d.arrow_shape(x + pw + 0.02, y + h / 2 - 0.23, gap - 0.04, 0.46,
                      fill=lighten(d.P.primary, 0.70))
    return y + h


# ---- 2. スイムレーン ----

def swimlane(d, x, y, w, lanes, steps, *, lane_h=1.02, lane_gap=0.30,
             label_w=1.30, box_gap=0.20):
    """レーン（担当）× ステップの図。

    lanes = [(レーン名, 色), …]（上から順）
    steps = [(見出し, 本文, レーンindex, tone), …]（左から順）

    ステップ間の矢印は**実際の座標を結ぶ**。レーンをまたぐ場合に水平線を引くと
    経路が嘘になるため、始点と終点をそのまま繋いでいる。
    """
    cx = x + label_w + 0.10
    cw = w - label_w - 0.10
    lane_y = []
    for i, (nm, col) in enumerate(lanes):
        ly = y + i * (lane_h + lane_gap)
        lane_y.append(ly)
        d.shape(x, ly, label_w, lane_h, kind="ROUND_RECTANGLE", fill=col,
                stroke=None, text=nm, size=9, bold=True, color="#FFFFFF",
                line_spacing=105)
        d.shape(cx, ly, cw, lane_h, kind="ROUND_RECTANGLE",
                fill=lighten(col, 0.94), stroke=lighten(col, 0.78),
                stroke_weight=0.75)

    n = len(steps)
    bw = (cw - 0.24 - box_gap * (n - 1)) / n
    centers = []
    for i, step in enumerate(steps):
        head, body, lane, tone = (list(step) + ["info"])[:4]
        fill, stroke, col = tone_colors(d, tone)
        bx = cx + 0.12 + i * (bw + box_gap)
        by = lane_y[lane]
        d.shape(bx, by + 0.12, bw, lane_h - 0.24, kind="ROUND_RECTANGLE",
                fill=fill, stroke=stroke)
        d.label(bx + 0.06, by + 0.20, bw - 0.12, 0.24, head, size=9, bold=True,
                align="CENTER", color=col)
        if body:
            d.label(bx + 0.06, by + 0.45, bw - 0.12, lane_h - 0.60, body,
                    size=8, align="CENTER", color=col, line_spacing=110)
        centers.append((bx, bx + bw, by + lane_h / 2))
    for i in range(n - 1):
        _, x_end, y1 = centers[i]
        x_start, _, y2 = centers[i + 1]
        d.arrow(x_end + 0.03, y1, x_start - 0.03, y2, color=d.P.primary, weight=1.6)
    return y + len(lanes) * (lane_h + lane_gap) - lane_gap


# ---- 3. タイムライン ----

def timeline(d, x, y, w, marks, *, bands=None, h=1.60, label_w=1.90):
    """横軸の時系列。

    marks = [(位置0.0〜1.0, ラベル, tone), …]
    bands = [(開始位置, 終了位置, ラベル, tone), …]（線の上に敷く期間の帯）

    補足はマーカーのラベルに持たせること。別ラベル＋縦矢印にすると
    他のマーカーの説明文や下のブロックに重なる。
    """
    line_y = y + h * 0.46

    def px(p):
        return x + 0.30 + (w - 0.60) * p

    d.line(x + 0.30, line_y, x + w - 0.30, line_y,
           color=lighten(d.P.muted, 0.30), weight=1.5, free=True)   # 軸
    for a, b, label, tone in (bands or []):
        fill, _, col = tone_colors(d, tone)
        d.shape(px(a), line_y - 0.38, px(b) - px(a), 0.24, kind="ROUND_RECTANGLE",
                fill=fill, stroke=None, text=label, size=7.5, bold=True, color=col)
    for p, label, tone in marks:
        mx, col = px(p), tone_solid(d, tone)
        d.shape(mx - 0.09, line_y - 0.09, 0.18, 0.18, kind="ELLIPSE",
                fill=col, stroke=None)
        d.label(mx - label_w / 2, line_y + 0.15, label_w,
                (y + h) - (line_y + 0.15), label, size=7.5, bold=True,
                align="CENTER", valign="TOP", color=darken(col, 0.20),
                line_spacing=105)
    return y + h


# ---- 4. 階層ツリー ----

def tree(d, x, y, w, nodes, *, row_h=0.46, gap=0.10, indent=0.24,
         box_w=1.45, size=8.5):
    """深さ付きのツリー。nodes = [(深さ, 名前, 説明), …] を上から順に置く。

    親からのかぎ線は、同じ深さの直前のノードではなく「1 つ浅い直近のノード」
    から引く。
    """
    last_y = {}
    for i, (depth, name, desc) in enumerate(nodes):
        iy = y + i * (row_h + gap)
        ix = x + depth * indent
        shade = min(0.72, 0.0 + depth * 0.22)
        col = lighten(d.P.primaryDark, shade)
        d.shape(ix + 0.16, iy, box_w, row_h - 0.12, kind="ROUND_RECTANGLE",
                fill=col, stroke=None, text=name, size=size, bold=True,
                color="#FFFFFF" if shade < 0.55 else d.P.text)
        if desc:
            d.label(ix + box_w + 0.30, iy + 0.03, w - (ix - x) - box_w - 0.46,
                    row_h - 0.14, desc, size=size - 1, align="START",
                    valign="MIDDLE", color=d.P.text, line_spacing=110)
        if depth > 0 and (depth - 1) in last_y:
            py = last_y[depth - 1]
            ex = x + (depth - 1) * indent + 0.30
            d.line(ex, py + row_h - 0.12, ex, iy + (row_h - 0.12) / 2,
                   color=lighten(d.P.muted, 0.25), weight=1.0, free=True)
            d.line(ex, iy + (row_h - 0.12) / 2, ix + 0.14,
                   iy + (row_h - 0.12) / 2, color=lighten(d.P.muted, 0.25),
                   weight=1.0, free=True)
        last_y[depth] = iy
    return y + len(nodes) * (row_h + gap) - gap


# ---- 5. 条件分岐 ----

def decision(d, x, y, w, question, branches, *, dia_w=3.70, dia_h=0.78,
             box_h=0.60, drop=0.42):
    """菱形の判定と、その下に扇状に広がる 2〜3 の帰結。

    branches = [(分岐ラベル, 帰結テキスト, tone), …]
    菱形の文字は図形に直接入れず、別ラベルを重ねる（端が切れるため）。
    """
    cx = x + w / 2
    d.shape(cx - dia_w / 2, y, dia_w, dia_h, kind="DIAMOND",
            fill=lighten(d.P.warning, 0.68), stroke=None)
    _fit(d, cx - dia_w / 2 + 0.30, y + 0.14, dia_w - 0.60, dia_h - 0.28,
         question, size=8.5, bold=True, color=darken(d.P.warning, 0.55), ls=105)

    n = len(branches)
    by = y + dia_h + drop
    bw = (w - 0.30 * (n - 1)) / n
    for i, (label, text, tone) in enumerate(branches):
        fill, stroke, col = tone_colors(d, tone)
        bx = x + i * (bw + 0.30)
        # 矢印は箱の中央よりやや右に落とし、ラベルは左寄せにして経路を避ける
        d.arrow(cx + (i - (n - 1) / 2) * 0.55, y + dia_h + 0.02,
                bx + bw * 0.62, by - 0.02, color=tone_solid(d, tone), weight=1.5)
        d.label(bx, by - 0.26, bw * 0.46, 0.22, label, size=7.5,
                align="START", color=d.P.muted)
        d.shape(bx, by, bw, box_h, kind="ROUND_RECTANGLE", fill=fill,
                stroke=stroke, text=text, size=9, color=col, line_spacing=110)
    return by + box_h


# ---- 6. 2×2 マトリクス ----

def quadrant(d, x, y, w, h, quads, *, x_label="", y_label="",
             x_axis=("低", "高"), y_axis=("低", "高")):
    """2×2 のマトリクス。quads は [左上, 右上, 左下, 右下] の順で
    (見出し, [項目, …], tone)。優先度づけや配置戦略に使う。
    """
    pad = 0.42                       # 軸ラベルの余白
    gx, gy = x + pad, y
    gw, gh = w - pad, h - pad
    cw, ch = gw / 2, gh / 2
    for i, (head, items, tone) in enumerate(quads):
        fill, stroke, col = tone_colors(d, tone)
        qx = gx + (i % 2) * cw
        qy = gy + (i // 2) * ch
        d.shape(qx + 0.03, qy + 0.03, cw - 0.06, ch - 0.06,
                kind="ROUND_RECTANGLE", fill=fill, stroke=stroke)
        d.label(qx + 0.16, qy + 0.10, cw - 0.32, 0.24, head, size=9, bold=True,
                align="START", valign="TOP", color=col)
        if items:
            d.label(qx + 0.16, qy + 0.36, cw - 0.32, ch - 0.46,
                    "\n".join("・" + s for s in items), size=8, align="START",
                    valign="TOP", color=d.P.text, line_spacing=125)
    # 軸
    d.label(x, gy, pad - 0.06, gh, y_label, size=8, bold=True, align="CENTER",
            valign="MIDDLE", color=d.P.muted)
    d.label(gx, y + h - pad + 0.06, gw, pad - 0.10, x_label, size=8, bold=True,
            align="CENTER", valign="TOP", color=d.P.muted)
    d.label(gx, y + h - pad + 0.06, 1.4, 0.20, x_axis[0], size=7.5,
            align="START", valign="TOP", color=d.P.muted)
    d.label(gx + gw - 1.4, y + h - pad + 0.06, 1.4, 0.20, x_axis[1], size=7.5,
            align="END", valign="TOP", color=d.P.muted)
    return y + h


# ---- 7. ポジショニングマップ（2 軸散布） ----

def matrix_map(d, x, y, w, h, items, *, x_label="", y_label="",
               x_axis=("低", "高"), y_axis=("低", "高"), dot=0.13):
    """2 軸上に項目を配置する。items = [(名前, x0〜1, y0〜1, tone), …]

    y は上が 1.0。競合比較や機能の位置づけに使う。
    """
    pad_l, pad_b = 0.46, 0.40
    gx, gy = x + pad_l, y
    gw, gh = w - pad_l, h - pad_b
    d.shape(gx, gy, gw, gh, kind="RECTANGLE", fill="#FBFCFE",
            stroke=lighten(d.P.primary, 0.75), stroke_weight=1.0)
    d.line(gx, gy + gh / 2, gx + gw, gy + gh / 2, color=lighten(d.P.muted, 0.55),
           weight=0.9, dashed=True, free=True)                      # 目盛り
    d.line(gx + gw / 2, gy, gx + gw / 2, gy + gh, color=lighten(d.P.muted, 0.55),
           weight=0.9, dashed=True, free=True)
    for name, px_, py_, tone in items:
        cx = gx + gw * px_
        cy = gy + gh * (1.0 - py_)
        col = tone_solid(d, tone)
        d.shape(cx - dot, cy - dot, dot * 2, dot * 2, kind="ELLIPSE",
                fill=col, stroke=None)
        d.label(cx - 1.05, cy + dot + 0.02, 2.10, 0.22, name, size=7.5,
                bold=True, align="CENTER", valign="TOP", color=darken(col, 0.25))
    d.label(x, gy, pad_l - 0.08, gh, y_label, size=8, bold=True, align="CENTER",
            valign="MIDDLE", color=d.P.muted)
    d.label(gx, gy + gh + 0.04, gw, 0.22, x_label, size=8, bold=True,
            align="CENTER", valign="TOP", color=d.P.muted)
    d.label(gx, gy + gh + 0.04, 1.4, 0.20, x_axis[0], size=7.5, align="START",
            valign="TOP", color=d.P.muted)
    d.label(gx + gw - 1.4, gy + gh + 0.04, 1.4, 0.20, x_axis[1], size=7.5,
            align="END", valign="TOP", color=d.P.muted)
    return y + h


# ---- 8. ロードマップ（フェーズ × レーン） ----

def roadmap(d, x, y, w, phases, lanes, *, head_h=0.32, lane_h=0.44, gap=0.10,
            label_w=1.90):
    """フェーズを列、レーンを行にしたロードマップ。

    phases = [列見出し, …]
    lanes  = [(レーン名, [(開始列index, 列数, ラベル, tone), …]), …]
    """
    n = len(phases)
    cw = (w - label_w) / n
    for j, ph in enumerate(phases):
        d.shape(x + label_w + j * cw, y, cw, head_h, kind="RECTANGLE",
                fill=lighten(d.P.primary, 0.82), stroke="#FFFFFF",
                stroke_weight=0.75, text=ph, size=8.5, bold=True,
                color=d.P.primaryDark)
    for i, (nm, bars) in enumerate(lanes):
        ry = y + head_h + 0.06 + i * (lane_h + gap)
        d.label(x, ry, label_w - 0.12, lane_h, nm, size=8.5, align="START",
                valign="MIDDLE", color=d.P.text)
        d.shape(x + label_w, ry, cw * n, lane_h, kind="RECTANGLE",
                fill="#F7F9FC" if i % 2 else "#FFFFFF", stroke=None)
        for start, span, label, tone in bars:
            fill, stroke, col = tone_colors(d, tone)
            d.shape(x + label_w + start * cw + 0.05, ry + 0.05,
                    span * cw - 0.10, lane_h - 0.10, kind="ROUND_RECTANGLE",
                    fill=fill, stroke=stroke, text=label, size=8, color=col)
    return y + head_h + 0.06 + len(lanes) * (lane_h + gap) - gap


# ---- 9. ピラミッド（成熟度・階層） ----

def pyramid(d, x, y, w, h, levels, *, gap=0.08, min_ratio=0.40):
    """上ほど狭い段組み。levels は上から [(名前, 説明, tone), …]。

    成熟度モデルや「土台 → 応用」の関係を示すのに使う。
    """
    n = len(levels)
    lh = (h - gap * (n - 1)) / n
    for i, (name, desc, tone) in enumerate(levels):
        ratio = min_ratio + (1.0 - min_ratio) * (i / max(1, n - 1))
        lw = w * ratio
        lx = x + (w - lw) / 2
        ly = y + i * (lh + gap)
        col = tone_solid(d, tone)
        inside = desc and ((w - lw) / 2 - 0.12) < 1.2
        d.shape(lx, ly, lw, lh, kind="ROUND_RECTANGLE", fill=col, stroke=None,
                text=name, size=9.5, bold=True, color="#FFFFFF",
                valign="TOP" if inside else "MIDDLE")
        if desc:
            side = (w - lw) / 2 - 0.12
            if side >= 1.2:                       # 横に置ける
                d.label(x + w - side, ly, side, lh, desc, size=8,
                        align="START", valign="MIDDLE", color=d.P.text,
                        line_spacing=110)
            else:                                 # 置けなければ段の中に入れる
                d.label(lx + 0.10, ly + lh * 0.52, lw - 0.20, lh * 0.42, desc,
                        size=7.5, align="CENTER", valign="TOP",
                        color=lighten("#FFFFFF", 0.0) if False else "#E8F1FA")
    return y + h


# ---- 10. サイクル（循環プロセス） ----

def cycle(d, x, y, w, h, steps, *, box_w=1.95, box_h=0.62, size=8.5,
          tone="info"):
    """矩形 (x, y, w, h) に内接する循環プロセス。steps = [ラベル, …]（4〜6 個が適切）

    半径は箱がこの矩形からはみ出さないよう自動で決まる。中心と半径を直接
    指定する形にすると、上端が安全域を突き抜ける事故が起きやすいため。
    矢印はステップ間の中間角に接線方向で置く。
    """
    cx, cy = x + w / 2, y + h / 2
    n = len(steps)
    # 矢印は箱の外側の環に置くので、その分だけ箱の半径を内側に取る
    ring = box_h * 0.55 + 0.10
    r = max(0.30, min((h - box_h) / 2 - ring, (w - box_w) / 2))
    # 半径が小さいと向かい合う箱どうしがぶつかる。箱の幅を半径に合わせて詰め、
    # 細くなったぶん半径を取り直す
    box_w = min(box_w, max(0.85, 2 * r - 0.16))
    r = max(0.30, min((h - box_h) / 2 - ring, (w - box_w) / 2))
    fill, stroke, col = tone_colors(d, tone)
    pos = []
    for i, s in enumerate(steps):
        th = -math.pi / 2 + 2 * math.pi * i / n
        px = cx + r * math.cos(th)
        py = cy + r * math.sin(th)
        pos.append((px, py))
        d.shape(px - box_w / 2, py - box_h / 2, box_w, box_h,
                kind="ROUND_RECTANGLE", fill=fill, stroke=stroke,
                text=s, size=size, color=col, line_spacing=105)
    ra = r + ring                                  # 矢印を置く環の半径
    for i in range(n):
        th = -math.pi / 2 + 2 * math.pi * (i + 0.5) / n
        ax = cx + ra * math.cos(th)
        ay = cy + ra * math.sin(th)
        tx, ty = -math.sin(th), math.cos(th)      # 接線（時計回り）
        d.arrow(ax - tx * 0.22, ay - ty * 0.22, ax + tx * 0.22, ay + ty * 0.22,
                color=d.P.primary, weight=1.6, free=True)   # 箱の間を回る矢印
    return y + h


# ---- 11. ファネル ----

def funnel(d, x, y, w, h, stages, *, gap=0.08, min_ratio=0.42):
    """上ほど広い漏斗。stages = [(ラベル, 補足, tone), …] を上から順に。"""
    n = len(stages)
    sh = (h - gap * (n - 1)) / n
    for i, (label, sub, tone) in enumerate(stages):
        ratio = 1.0 - (1.0 - min_ratio) * (i / max(1, n - 1))
        sw = w * ratio
        sx = x + (w - sw) / 2
        sy = y + i * (sh + gap)
        col = tone_solid(d, tone)
        inside = sub and ((w - sw) / 2 - 0.12) < 1.2
        d.shape(sx, sy, sw, sh, kind="ROUND_RECTANGLE", fill=col, stroke=None,
                text=label, size=9.5, bold=True, color="#FFFFFF",
                valign="TOP" if inside else "MIDDLE")
        if sub:
            side = (w - sw) / 2 - 0.12
            if side >= 1.2:                       # 横に置ける
                d.label(x + w - side, sy, side, sh, sub, size=8, align="START",
                        valign="MIDDLE", color=d.P.text, line_spacing=110)
            else:                                 # 置けなければ段の中に入れる
                d.label(sx + 0.10, sy + sh * 0.52, sw - 0.20, sh * 0.42, sub,
                        size=7.5, align="CENTER", valign="TOP", color="#E8F1FA")
    return y + h


# ---- 12. 注釈つき図（中央＋番号つきコールアウト） ----

def callouts(d, x, y, w, h, center, notes, *, note_w=2.40, tone="primary"):
    """中央の対象に番号つきの注釈を左右から付ける。

    center = (見出し, 本文)
    notes  = [(注釈テキスト, "left" | "right"), …]（付けた順に 1, 2, 3…）
    """
    fill, stroke, col = tone_colors(d, tone)
    ccx = x + w / 2
    cw = w - 2 * (note_w + 0.34)
    # 中央の箱は内容に合わせた高さにして上下中央へ。h いっぱいに広げると
    # 文字が上に寄って下half が空洞に見える。
    ch = min(h - 0.20, 1.50)
    cyy = y + (h - ch) / 2
    d.shape(ccx - cw / 2, cyy, cw, ch, kind="ROUND_RECTANGLE",
            fill=fill, stroke=stroke)
    d.label(ccx - cw / 2 + 0.12, cyy + 0.20, cw - 0.24, 0.30, center[0],
            size=10, bold=True, align="CENTER", color=col)
    if center[1]:
        d.label(ccx - cw / 2 + 0.12, cyy + 0.54, cw - 0.24, ch - 0.70, center[1],
                size=8.5, align="CENTER", valign="TOP", color=col,
                line_spacing=120)

    sides = {"left": [], "right": []}
    for i, (text, side) in enumerate(notes):
        sides.setdefault(side, []).append((i + 1, text))
    for side, lst in sides.items():
        if not lst:
            continue
        nh = min(0.72, (h - 0.20 - 0.14 * (len(lst) - 1)) / len(lst))
        nx = x if side == "left" else x + w - note_w
        for k, (num, text) in enumerate(lst):
            ny = y + 0.10 + k * (nh + 0.14)
            d.shape(nx if side == "left" else nx + note_w - 0.30,
                    ny + (nh - 0.30) / 2, 0.30, 0.30, kind="ELLIPSE",
                    fill=d.P.primary, stroke=None, text=str(num), size=9,
                    bold=True, color="#FFFFFF")
            tx = nx + 0.38 if side == "left" else nx
            d.label(tx, ny, note_w - 0.38, nh, text, size=8,
                    align="START" if side == "left" else "END",
                    valign="MIDDLE", color=d.P.text, line_spacing=115)
            edge = ccx - cw / 2 if side == "left" else ccx + cw / 2
            anchor = nx + note_w if side == "left" else nx
            # 接続線の終点は箱の高さに丸める。箱の外に伸ばすと何も指さない線になる
            ly = min(max(ny + nh / 2, cyy + 0.12), cyy + ch - 0.12)
            d.line(anchor + (0.06 if side == "left" else -0.06),
                   ny + nh / 2, edge, ly, free=True,   # 注釈側は文字なので接点なし
                   color=lighten(d.P.primary, 0.60), weight=0.9, dashed=True)
    return y + h


# ---- 13. 指標の行（KPI） ----

def stats(d, x, y, w, items, *, h=0.92, gap=0.20, value_size=22):
    """大きな数値を横並びにする。items = [(値, 説明, tone), …]

    出典のある数値にだけ使うこと。推測値を大きく見せてはいけない。
    """
    n = len(items)
    cw = (w - gap * (n - 1)) / n
    # 枠が低いときは数値のフォントを縮める。固定サイズだと枠から溢れて切れる
    vh = h * 0.54
    vs = min(value_size, vh * 72.0 / Canvas.LINE_EM)
    for i, (value, cap, tone) in enumerate(items):
        col = tone_solid(d, tone)
        cx = x + i * (cw + gap)
        d.shape(cx, y, cw, h, kind="ROUND_RECTANGLE", fill=lighten(col, 0.90),
                stroke=lighten(col, 0.55))
        d.label(cx + 0.10, y + 0.06, cw - 0.20, vh, value,
                size=vs, bold=True, align="CENTER", valign="MIDDLE", color=col)
        d.label(cx + 0.10, y + h * 0.62, cw - 0.20, h * 0.34, cap, size=8,
                align="CENTER", valign="TOP", color=d.P.muted, line_spacing=115)
    return y + h


# ---- 14. チェックリスト ----

def checklist(d, x, y, w, items, *, row_h=0.34, gap=0.08, size=9):
    """状態つきの項目リスト。items = [(テキスト, "done"|"todo"|"warn"), …]"""
    marks = {"done": ("✓", "good"), "todo": ("□", "muted"), "warn": ("!", "warn")}
    for i, (text, state) in enumerate(items):
        glyph, tone = marks.get(state, marks["todo"])
        fill, stroke, col = tone_colors(d, tone)
        ry = y + i * (row_h + gap)
        d.shape(x, ry, row_h, row_h, kind="ROUND_RECTANGLE",
                fill=tone_solid(d, tone) if state != "todo" else "#FFFFFF",
                stroke=None if state != "todo" else lighten(d.P.muted, 0.45),
                text=glyph, size=size, bold=True,
                color="#FFFFFF" if state != "todo" else d.P.muted)
        d.shape(x + row_h + 0.10, ry, w - row_h - 0.10, row_h,
                kind="ROUND_RECTANGLE", fill=fill, stroke=stroke, text=text,
                size=size, color=col, align="START")
    return y + len(items) * (row_h + gap) - gap


# ---- 15. パイプライン（範囲強調つき） ----

def pipeline(d, x, y, w, steps, *, h=0.80, gap=0.30, highlight=None,
             highlight_note=None, size=8.5):
    """左から右への工程。highlight=(開始index, 終了index) の範囲だけ強調する。

    「全体の流れのうち、自分たちが担うのはここ」を示すのに使う。
    """
    n = len(steps)
    bw = (w - gap * (n - 1)) / n
    lo, hi = highlight if highlight else (-1, -2)
    for i, s in enumerate(steps):
        own = lo <= i <= hi
        sx = x + i * (bw + gap)
        d.shape(sx, y, bw, h, kind="ROUND_RECTANGLE",
                fill=d.P.primary if own else lighten(d.P.muted, 0.88),
                stroke=None if own else lighten(d.P.muted, 0.50),
                text=s, size=size, bold=own,
                color="#FFFFFF" if own else d.P.text, line_spacing=110)
        if i < n - 1:
            d.arrow(sx + bw + 0.03, y + h / 2, sx + bw + gap - 0.03, y + h / 2,
                    color=d.P.primary, weight=1.5)
    bottom = y + h
    if highlight and highlight_note:
        hx = x + lo * (bw + gap)
        hw = (hi - lo + 1) * bw + (hi - lo) * gap
        d.label(hx, bottom + 0.04, hw, 0.22, highlight_note, size=8, bold=True,
                align="CENTER", valign="TOP", color=d.P.primaryDark)
        bottom += 0.26
    return bottom


# ---- 16. 凡例 ----

def legend(d, x, y, w, items, *, size=8, h=0.24, gap=0.28, swatch=0.16):
    """色の凡例。items = [(色または tone 名, ラベル), …] を横に並べる。"""
    cx = x
    for col, label in items:
        if isinstance(col, str) and col.startswith("#"):
            fill, stroke = col, None
        else:
            fill, stroke, _ = tone_colors(d, col)   # 図形と同じ塗りを見せる
        d.shape(cx, y + (h - swatch) / 2, swatch, swatch, kind="ROUND_RECTANGLE",
                fill=fill, stroke=stroke)
        # テキストボックスの内側余白があるため、実測幅に 1.1 倍と 0.22in を足す
        tw = em(label) * size / 72 * 1.10 + 0.22
        d.label(cx + swatch + 0.08, y, tw, h, label, size=size, align="START",
                valign="MIDDLE", color=d.P.muted)
        cx += swatch + 0.08 + tw + gap
    return y + h
