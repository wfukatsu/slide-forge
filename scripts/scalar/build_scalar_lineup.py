#!/usr/bin/env python3
"""Scalar product lineup / product features / use cases / case studies deck (11 content pages).

Researched 2026-08-24 from scalar-labs.com, scalardb.scalar-labs.com,
PR TIMES press releases, and the official Scalar boilerplate deck.

  Run:    .venv/bin/python scripts/scalar/build_scalar_lineup.py [--folder <URL>]
  Check:  .venv/bin/python scripts/scalar/build_scalar_lineup.py --dry-run
"""
from __future__ import annotations

import os
import sys

REPO_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(REPO_DIR, "scripts"))

import build_deck as bd  # noqa: E402
from diagrams import Canvas, lighten, darken  # noqa: E402
from _i18n import t, register  # noqa: E402

register({
    "  audit: {message}": "  検査: {message}",
    "Done! {n} slides. Open: {url}": "完了! スライド {n} 枚。URL: {url}",
})

TEMPLATE = os.path.join(REPO_DIR, "templates", "scalar-2026.json")

TITLE = "Scalar 製品ラインナップとユースケース"
SUBTITLE = "ScalarDB / ScalarDB Saga / ScalarDB Analytics ・ ScalarDL"
DATE = "2026年8月"

DB_DOCS = "https://scalardb.scalar-labs.com/docs/latest/"
PR_319 = "https://prtimes.jp/main/html/rd/p/000000078.000037795.html"
PR_DL314 = "https://prtimes.jp/main/html/rd/p/000000079.000037795.html"
PR_TSUNEISHI = "https://prtimes.jp/main/html/rd/p/000000071.000037795.html"

# Figure area (left column), shared by every content page
FX, FY, FW, FH = 0.5, 0.98, 5.25, 2.32


# ---------------------------------------------------------------- Shared components

def _pill(d, x, y, w, h, text, accent, *, light=0.88, size=9, bold=False,
          color=None):
    return d.shape(x, y, w, h, kind="ROUND_RECTANGLE",
                   fill=lighten(accent, light), stroke=accent, text=text,
                   size=size, bold=bold, color=color or d.P.text,
                   line_spacing=112)


def _caption(d, text, *, y=None, size=8.5):
    d.label(FX, y if y is not None else FY + FH - 0.24, FW, 0.24, text,
            size=size, align="CENTER", color=d.P.muted)


def _va(d, x1, y1, x2, y2, color=None):
    d.arrow(x1, y1, x2, y2, color=color or d.P.muted, weight=1.0, _anchored=True)


def _panel(d, x, y, w, h, heading, body, accent, *, body_size=9.5,
           heading_size=10.5, line_spacing=130):
    """Surface card with a straight accent bar on top (so: RECTANGLE, no rounding)."""
    d.shape(x, y, w, h, kind="RECTANGLE", fill=d.P.surface, stroke=d.P.border)
    d.shape(x, y, w, 0.06, kind="RECTANGLE", fill=accent, stroke=None)
    d.label(x + 0.16, y + 0.13, w - 0.32, 0.28, heading, size=heading_size,
            bold=True, align="START", color=accent)
    d.label(x + 0.16, y + 0.46, w - 0.34, h - 0.58, body, size=body_size,
            align="START", color=d.P.text, line_spacing=line_spacing)


def _left_bar_band(d, y, h, heading, accent, *, heading_w=1.25):
    """Full-width band with a straight accent bar on the left edge."""
    d.shape(0.5, y, 9.0, h, kind="RECTANGLE", fill=d.P.surface, stroke=d.P.border)
    d.shape(0.5, y, 0.06, h, kind="RECTANGLE", fill=accent, stroke=None)
    d.label(0.68, y, heading_w, h, heading, size=10, bold=True, align="START",
            valign="MIDDLE", color=accent, line_spacing=115)


def _two_col_bullets(d, y, h, items, *, x0=2.0, size=9):
    half = (len(items) + 1) // 2
    for i, col in enumerate([items[:half], items[half:]]):
        if col:
            d.label(x0 + i * 3.7, y + 0.10, 3.55, h - 0.20,
                    "\n".join(f"・{u}" for u in col), size=size, align="START",
                    valign="MIDDLE", color=d.P.text, line_spacing=128)


def _value_band(d, y, heading, text, accent, *, h=0.62):
    d.shape(0.5, y, 9.0, h, kind="RECTANGLE", fill=lighten(accent, 0.9),
            stroke=lighten(accent, 0.5))
    d.label(0.68, y, 1.55, h, heading, size=10, bold=True, align="START",
            valign="MIDDLE", color=accent)
    d.label(2.3, y + 0.05, 7.0, h - 0.10, text, size=9.5, align="START",
            valign="MIDDLE", color=d.P.text, line_spacing=122)


# ---------------------------------------------------------------- Page layouts

def draw_product(d, f, accent):
    """Product page: figure left / overview right / use cases / strengths."""
    if f.get("edition"):
        d.label(4.6, 0.60, 4.9, 0.26, f["edition"], size=9, align="END",
                color=d.P.muted)
    f["figure"](d, accent)
    _panel(d, 6.0, FY, 3.5, FH, "製品概要", f["overview"], accent)
    _left_bar_band(d, 3.40, 0.94, "ユース\nケース", accent)
    _two_col_bullets(d, 3.40, 0.94, f["usecases"])
    _value_band(d, 4.42, "特長", f["value"], accent)


def draw_usecase(d, f, accent):
    """Use-case page: figure left / challenge right / how Scalar solves it / effect."""
    if f.get("badge"):
        d.label(4.6, 0.60, 4.9, 0.26, f["badge"], size=9, align="END",
                color=d.P.muted)
    f["figure"](d, accent)
    _panel(d, 6.0, FY, 3.5, FH, "よくある課題", f["challenge"], accent)
    _left_bar_band(d, 3.40, 0.94, "Scalar の\n解き方", accent)
    _two_col_bullets(d, 3.40, 0.94, f["approach"])
    _value_band(d, 4.42, f["products"], f["effect"], accent)


def draw_case(d, f, accent):
    """Case-study page: figure left / background + solution right / results / source."""
    d.label(0.5, 0.54, 6.0, 0.28, f["org"], size=11, bold=True, align="START",
            color=accent)
    f["figure"](d, accent)
    _panel(d, 6.0, FY, 3.5, 1.24, "背景・課題", f["challenge"], accent,
           body_size=8.5, heading_size=10, line_spacing=124)
    _panel(d, 6.0, 2.26, 3.5, 1.24, "ソリューション", f["solution"], accent,
           body_size=8.5, heading_size=10, line_spacing=124)
    mw = (9.0 - 2 * 0.14) / 3
    for i, (value, caption) in enumerate(f["metrics"]):
        d.metric(0.5 + i * (mw + 0.14), 3.58, mw, 0.82, value, caption,
                 value_size=16, caption_size=8.5,
                 color=accent if i == 0 else None)
    _value_band(d, 4.48, "効果", f["effect"], accent, h=0.62)
    d.label(1.70, 5.14, 7.8, 0.22, f["source"], size=7.5, align="END",
            color=d.P.muted)


# ---------------------------------------------------------------- Figures

def fig_lineup(d, accent):
    """4 products in one row, with the ScalarDB family band above the first three."""
    P = d.P
    accents = [P.primary, P.info, darken(P.primary, 0.3), P.success]
    colw, gap = 2.13, 0.16
    xs = [0.5 + i * (colw + gap) for i in range(4)]

    d.shape(xs[0], 1.00, colw * 3 + gap * 2, 0.42, kind="ROUND_RECTANGLE",
            fill=lighten(P.primary, 0.86), stroke=P.primary,
            text="ScalarDB — Universal HTAP エンジン", size=10.5, bold=True,
            color=P.primaryDark)
    d.shape(xs[3], 1.00, colw, 0.42, kind="ROUND_RECTANGLE",
            fill=lighten(P.success, 0.86), stroke=P.success,
            text="ScalarDL", size=10.5, bold=True, color=darken(P.success, 0.4))

    cols = [
        ("ScalarDB\n（中核）", "server",
         ["異種 DB をまたぐ ACID", "統一 API / SQL", "暗号化・アクセス制御"]),
        ("Saga\n（3.19 新）", "sync",
         ["Saga / TCC の実行基盤", "外部 API・SaaS 連携", "補償処理を自動管理"]),
        ("Analytics", "chart",
         ["ETL なしの横断分析", "Apache Spark で実行", "3.19 でクエリ高速化"]),
        ("改ざん検知\nミドルウェア", "shield",
         ["ビザンチン故障を検知", "10 年超の証拠保全", "Ledger + Auditor"]),
    ]
    top, h = 1.56, 2.34
    for i, (name, icon, bullets) in enumerate(cols):
        a = accents[i]
        d.shape(xs[i], top, colw, h, kind="RECTANGLE", fill=P.surface,
                stroke=P.border)
        d.shape(xs[i], top, colw, 0.06, kind="RECTANGLE", fill=a, stroke=None)
        d.label(xs[i] + 0.12, top + 0.13, colw - 0.24, 0.52, name, size=10.5,
                bold=True, align="CENTER", color=a, line_spacing=110)
        d.icon(icon, xs[i] + colw / 2 - 0.19, top + 0.72, 0.38, color=a)
        d.label(xs[i] + 0.12, top + 1.24, colw - 0.24, 1.00,
                "\n".join(f"・{b}" for b in bullets), size=8.5, align="START",
                color=P.text, line_spacing=132)

    _value_band(d, 4.14,
                "位置づけ",
                "既存のデータベースを置き換えずに、トランザクション・分析・証拠性を「後から足す」ミドルウェア群。"
                "ScalarDB は 3 製品の組み合わせ、ScalarDL は単独でも導入できる。",
                P.primary, h=0.66)


def fig_db_core(d, accent):
    d.icon("server", FX + 2.30, FY + 0.02, 0.34, label="アプリケーション",
           label_size=8, label_w=1.8)
    _pill(d, FX + 0.20, FY + 0.78, 4.85, 0.46,
          "ScalarDB Cluster — Consensus Commit（統一 API / SQL）", accent,
          size=9, bold=True)
    d.icon_row(FX + 0.30, FY + 1.44, 4.65,
               [("database", "RDBMS"), ("stack", "NoSQL"),
                ("cloud", "NewSQL")], size=0.30, label_size=8)
    _va(d, FX + 2.47, FY + 0.66, FX + 2.47, FY + 0.76)
    for cx in (FX + 1.07, FX + 2.62, FX + 4.17):
        _va(d, cx, FY + 1.28, cx, FY + 1.42)
    _caption(d, "1 つのトランザクションが複数・異種の DB へ原子的に反映される")


def fig_db_saga(d, accent):
    steps = [("受注", "document"), ("在庫確保", "stack"), ("決済(外部API)", "cloud"),
             ("承認(人)", "person")]
    bw, gap = 1.14, 0.23
    x0 = FX + 0.10
    _pill(d, FX + 0.10, FY + 0.04, 5.05, 0.40,
          "ScalarDB Saga — Saga / TCC オーケストレータ", accent, size=9,
          bold=True)
    for i, (name, icon) in enumerate(steps):
        bx = x0 + i * (bw + gap)
        d.shape(bx, FY + 0.66, bw, 0.72, kind="ROUND_RECTANGLE",
                fill=d.P.surface, stroke=accent)
        d.icon(icon, bx + bw / 2 - 0.14, FY + 0.74, 0.28, color=accent)
        d.label(bx + 0.04, FY + 1.06, bw - 0.08, 0.28, name, size=8,
                align="CENTER", color=d.P.text)
        if i:
            _va(d, bx - gap, FY + 1.02, bx - 0.02, FY + 1.02, accent)
    d.arrow(x0 + 3 * (bw + gap) + bw / 2, FY + 1.48, x0 + bw / 2, FY + 1.48,
            color=d.P.danger, weight=1.2, dashed=True, _anchored=True)
    d.label(FX + 0.10, FY + 1.54, 5.05, 0.26, "失敗時は逆順に補償処理（TCC は取消）",
            size=8, align="CENTER", color=d.P.danger)
    _caption(d, "2PC に参加できない外部サービスを含んでも整合性を保つ")


def fig_db_analytics(d, accent):
    d.icon_row(FX + 0.20, FY + 0.10, 4.85,
               [("database", "基幹 RDBMS"), ("stack", "NoSQL"),
                ("folder", "ストレージ")], size=0.32, label_size=8)
    for cx in (FX + 1.01, FX + 2.62, FX + 4.24):
        _va(d, cx, FY + 0.74, cx, FY + 0.90)
    _pill(d, FX + 0.20, FY + 0.94, 4.85, 0.46,
          "ScalarDB Analytics（Apache Spark カタログ）", accent, size=9,
          bold=True)
    d.label(FX + 0.20, FY + 1.44, 4.85, 0.24,
            "WHERE 句の条件はバックエンド DB へプッシュダウン（3.19）", size=8,
            align="CENTER", color=d.P.muted)
    _va(d, FX + 2.62, FY + 1.72, FX + 2.62, FY + 1.84)
    _pill(d, FX + 1.20, FY + 1.86, 2.85, 0.36,
          "BI・レポート ／ AI・機械学習", d.P.muted, size=8.5)


def fig_dl_core(d, accent):
    d.icon("server", FX + 2.30, FY + 0.02, 0.32, label="アプリケーション",
           label_size=8, label_w=1.8)
    _va(d, FX + 2.46, FY + 0.62, FX + 2.46, FY + 0.76)
    d.shape(FX + 0.15, FY + 0.80, 2.40, 1.08, kind="RECTANGLE",
            fill=lighten(accent, 0.9), stroke=accent)
    d.label(FX + 0.22, FY + 0.86, 2.26, 0.26, "ScalarDL Ledger", size=9,
            bold=True, align="CENTER", color=darken(accent, 0.35))
    d.label(FX + 0.22, FY + 1.16, 2.26, 0.64,
            "追記型台帳\nハッシュ値の連鎖で\n改変を検知", size=8,
            align="CENTER", color=d.P.text, line_spacing=126)
    d.shape(FX + 2.72, FY + 0.80, 2.30, 1.08, kind="RECTANGLE",
            fill=d.P.surface, stroke=d.P.border)
    d.label(FX + 2.79, FY + 0.86, 2.16, 0.26, "ScalarDL Auditor", size=9,
            bold=True, align="CENTER", color=darken(accent, 0.35))
    d.label(FX + 2.79, FY + 1.16, 2.16, 0.64,
            "独立した管理ドメインで\n同じ結果を検証", size=8,
            align="CENTER", color=d.P.text, line_spacing=126)
    d.arrow(FX + 2.55, FY + 1.34, FX + 2.70, FY + 1.34, color=accent,
            weight=1.2, _anchored=True)
    _caption(d, "2 つの管理ドメインが一致しなければ改ざんとして検知できる")


def fig_uc_microservices(d, accent):
    svc = [("受注サービス", "database"), ("在庫サービス", "database"),
           ("決済 SaaS", "cloud")]
    bw, gap = 1.55, 0.20
    x0 = FX + 0.10
    for i, (name, icon) in enumerate(svc):
        bx = x0 + i * (bw + gap)
        d.shape(bx, FY + 0.04, bw, 0.86, kind="ROUND_RECTANGLE",
                fill=d.P.surface, stroke=accent if i < 2 else d.P.muted)
        d.icon(icon, bx + bw / 2 - 0.14, FY + 0.12, 0.28,
               color=accent if i < 2 else d.P.muted)
        d.label(bx + 0.04, FY + 0.46, bw - 0.08, 0.36, name, size=8,
                align="CENTER", color=d.P.text)
    _pill(d, x0, FY + 1.06, bw * 2 + gap, 0.42,
          "ScalarDB 分散トランザクション（2PC）", accent, size=8.5, bold=True)
    _pill(d, x0, FY + 1.60, bw * 3 + gap * 2, 0.42,
          "ScalarDB Saga（Saga / TCC）", d.P.info, size=8.5, bold=True)
    for cx in (x0 + bw / 2, x0 + bw + gap + bw / 2):
        _va(d, cx, FY + 0.92, cx, FY + 1.04, accent)
    _va(d, x0 + 2 * (bw + gap) + bw / 2, FY + 0.92,
        x0 + 2 * (bw + gap) + bw / 2, FY + 1.58, d.P.info)
    _caption(d, "強い整合性は 2PC、外部連携は Saga —— 業務要件で選び分ける")


def fig_uc_ai_data(d, accent):
    d.icon_row(FX + 0.15, FY + 0.04, 4.95,
               [("database", "基幹 RDBMS"), ("stack", "NoSQL"),
                ("search", "ベクトル\nストア")], size=0.30, label_size=8)
    for cx in (FX + 0.97, FX + 2.62, FX + 4.28):
        _va(d, cx, FY + 0.76, cx, FY + 0.92)
    _pill(d, FX + 0.15, FY + 0.96, 4.95,
          0.44, "ScalarDB 統一 API（暗号化・レコード単位のアクセス制御）",
          accent, size=8.5, bold=True)
    _va(d, FX + 2.62, FY + 1.42, FX + 2.62, FY + 1.52)
    d.icon_row(FX + 0.90, FY + 1.54, 3.45,
               [("bot", "RAG / LLM"), ("chart", "横断分析")],
               size=0.26, label_size=8)
    _caption(d, "データを別基盤へコピーせずに AI から参照できる")


def fig_uc_evidence(d, accent):
    d.icon_row(FX + 0.15, FY + 0.04, 4.95,
               [("bot", "AI の生成物"), ("document", "操作・同意ログ"),
                ("folder", "業務ファイル")], size=0.30, label_size=8)
    for cx in (FX + 0.97, FX + 2.62, FX + 4.28):
        _va(d, cx, FY + 0.76, cx, FY + 0.90)
    _pill(d, FX + 0.15, FY + 0.94, 4.95, 0.40, "ハッシュ値を計算（実データは預けない）",
          d.P.muted, size=8.5)
    _va(d, FX + 2.62, FY + 1.36, FX + 2.62, FY + 1.48)
    _pill(d, FX + 0.15, FY + 1.52, 3.20, 0.44,
          "ScalarDL — 順序を持つハッシュの連鎖", accent, size=8.5, bold=True)
    _pill(d, FX + 3.50, FY + 1.52, 1.60, 0.44, "タイム\nスタンプ", d.P.muted,
          size=8)
    d.arrow(FX + 3.37, FY + 1.74, FX + 3.48, FY + 1.74, color=d.P.muted,
            weight=1.0, _anchored=True)
    _caption(d, "いつ（WHEN）・どの順序で（SEQUENCE）・何が（WHAT）を後から証明する")


def fig_case_tsuneishi(d, accent):
    d.shape(FX + 0.10, FY + 0.18, 1.55, 1.30, kind="RECTANGLE",
            fill=lighten(d.P.muted, 0.85), stroke=d.P.muted)
    d.label(FX + 0.16, FY + 0.32, 1.43, 1.00,
            "十数年\n稼働した\n基幹モノリス\n（ブラック\nボックス化）", size=8,
            align="CENTER", valign="MIDDLE", color=d.P.text, line_spacing=126)
    d.arrow(FX + 1.70, FY + 0.83, FX + 2.00, FY + 0.83, color=accent,
            weight=1.4, _anchored=True)
    for i in range(3):
        for j in range(3):
            d.shape(FX + 2.10 + j * 0.62, FY + 0.20 + i * 0.44, 0.54, 0.36,
                    kind="ROUND_RECTANGLE", fill=lighten(accent, 0.85),
                    stroke=accent)
    d.label(FX + 2.10, FY + 1.54, 1.86, 0.24, "9 マイクロサービス", size=8,
            align="CENTER", color=d.P.text)
    _pill(d, FX + 4.10, FY + 0.20, 1.05, 0.56, "Kong\nKonnect\n(API 管理)",
          d.P.muted, size=7.5)
    _pill(d, FX + 4.10, FY + 0.88, 1.05, 0.56, "ScalarDB\n(整合性)", accent,
          size=7.5, bold=True)
    _caption(d, "業務ドメイン単位で分割し、AI 駆動開発で構築", y=FY + FH - 0.12)


def fig_case_toyota(d, accent):
    _pill(d, FX + 0.10, FY + 0.10, 1.30, 0.52, "Box /\nSharePoint", d.P.muted,
          size=8)
    _va(d, FX + 1.42, FY + 0.36, FX + 1.72, FY + 0.36)
    _pill(d, FX + 1.74, FY + 0.10, 1.30, 0.52, "ファイル変更\nイベント検知",
          d.P.muted, size=8)
    _va(d, FX + 3.06, FY + 0.36, FX + 3.36, FY + 0.36)
    _pill(d, FX + 3.38, FY + 0.10, 1.30, 0.52, "ハッシュ計算", d.P.muted, size=8)
    _va(d, FX + 4.03, FY + 0.64, FX + 4.03, FY + 0.84)
    _pill(d, FX + 0.10, FY + 0.88, 4.58, 0.48,
          "ScalarDL — ファイルのハッシュ値のチェーン（アセット）", accent,
          size=8.5, bold=True)
    _va(d, FX + 2.39, FY + 1.38, FX + 2.39, FY + 1.56)
    _pill(d, FX + 0.90, FY + 1.60, 3.00, 0.44, "時刻認証局のタイムスタンプ（1 日 1 回）",
          d.P.muted, size=8)
    _caption(d, "実データではなくハッシュ値だけを記録して証拠を保全する",
             y=FY + FH - 0.10)


def fig_case_broadcaster(d, accent):
    _pill(d, FX + 0.10, FY + 0.06, 1.55, 0.72, "IT 部門\n番組情報\n(RDBMS)",
          accent, size=8, bold=True)
    for i in range(3):
        d.shape(FX + 1.95 + i * 1.08, FY + 0.06, 0.96, 0.72,
                kind="ROUND_RECTANGLE", fill=d.P.surface, stroke=d.P.muted,
                text="制作局\nコンテンツ\n(NoSQL)", size=7.5, color=d.P.text,
                line_spacing=112)
    _pill(d, FX + 0.10, FY + 0.92, 5.05, 0.42, "API（アクセスを API 化して統制）",
          d.P.muted, size=8.5)
    for cx in (FX + 0.88, FX + 2.43, FX + 3.51, FX + 4.59):
        _va(d, cx, FY + 0.80, cx, FY + 0.90)
    _va(d, FX + 2.62, FY + 1.36, FX + 2.62, FY + 1.50)
    _pill(d, FX + 0.10, FY + 1.54, 5.05, 0.44,
          "ScalarDB — 中央集権と分散管理をまたぐ整合性", accent, size=8.5,
          bold=True)
    _caption(d, "公開・非公開の制御は IT 部門、コンテンツ拡張は制作局",
             y=FY + FH - 0.06)


# ---------------------------------------------------------------- Content

def products(P):
    return [
        dict(title="異種の DB をつないだまま、1 つのトランザクションで守る",
             accent=P.primary, figure=fig_db_core,
             edition="Community / Enterprise Standard / Enterprise Premium（最新 3.19）",
             overview="独自プロトコル「Consensus Commit」により、下位 DB の機能に依存せず "
                      "ACID を保証します。RDBMS・NoSQL・NewSQL を統一 API で扱い、"
                      "既存の DB を移行せずに仮想統合できます。Enterprise では "
                      "Cluster による可用性に加え、認証認可・暗号化・SQL / GraphQL が"
                      "加わります。",
             usecases=["サイロ化した複数 DB の統合管理",
                       "レガシー・メインフレームの移行",
                       "マルチクラウド / ハイブリッドクラウド",
                       "ベンダーロックインの回避"],
             value="既存のデータベースを置き換えずに、アプリからは 1 つの DB のように扱えます。"
                   "DB 側の機能に依存せず、どの DB でも同じ整合性保証が得られます。",
             notes=f"出典: {DB_DOCS}overview/（3.19、エディションは Community / "
                   f"Enterprise Standard / Enterprise Premium）。SQL インターフェース・"
                   f"認証認可のエディション所属は公式ページ間で表記揺れがあるため、"
                   f"個別案件では最新の features 表を確認すること。"),
        dict(title="外部 API も人の承認も含む業務フローを整合させる",
             accent=P.info, figure=fig_db_saga,
             edition="ScalarDB 3.19（2026年8月）で提供開始",
             overview="複数のサービスをまたぐ Saga / TCC のワークフローを実行・管理する"
                      "エンジン兼オーケストレータです。実行状況と状態遷移を一元管理し、"
                      "障害時の再実行や補償処理を制御します。2PC に参加できない "
                      "外部 API・SaaS を含む業務でも整合性を維持できます。",
             usecases=["外部 API・SaaS を含む業務処理",
                       "人の承認やバッチを含む長時間の業務",
                       "非同期処理・リソースの事前確保",
                       "2PC が使えない領域の整合性担保"],
             value="強い整合性が要る処理は 2PC、外部連携や長時間処理は Saga / TCC と"
                   "業務要件に応じて選び分けられます。補償処理の作り込みが不要になります。",
             notes=f"出典: {PR_319}（2026年8月、ScalarDB 3.19 プレスリリース）。"
                   f"「新コンポーネント『ScalarDB Saga』の提供を開始します」と明記。"
                   f"今後 Quarkus をはじめとする MicroProfile 準拠フレームワークとの"
                   f"連携を進める旨がロードマップとして示されている。"),
        dict(title="ETL を作らずに、複数 DB を横断して分析する",
             accent=darken(P.primary, 0.3), figure=fig_db_analytics,
             edition="Enterprise（有償ライセンス）／実行エンジン: Apache Spark",
             overview="ScalarDB 管理下の DB と管理外の DB を、Spark のカタログとして"
                      "統一的に見せる分析コンポーネントです。ETL でコピーせずに、"
                      "複数 DB を横断した SQL 分析を実行できます。3.19 では WHERE 句の"
                      "条件をバックエンド DB へプッシュダウンし、高速化しました。",
             usecases=["部門をまたぐレポーティング",
                       "取引データのリアルタイム分析",
                       "AI / 機械学習向けのデータ収集",
                       "データ基盤の統合・維持コスト削減"],
             value="分析のためのデータ移送と ETL 開発をなくせます。3.19 のプッシュダウン対応で、"
                   "ネットワークと計算資源の使用量も抑えられます。",
             notes=f"出典: {DB_DOCS}scalardb-analytics/design/ および {PR_319}"
                   f"（3.19 でプッシュダウン対応）。Spark 版は有償ライセンス、"
                   f"PostgreSQL 版は OSS。ロードマップとして AI を活用したデータカタログの"
                   f"生成・管理機能の開発が示されている。"),
        dict(title="10 年後も「改ざんされていない」と証明できるようにする",
             accent=P.success, figure=fig_dl_core,
             edition="最新 3.14（2026年8月）／Ledger: Community・Auditor: Enterprise",
             overview="改ざんを含む任意の故障（ビザンチン故障）を検知できるミドルウェアです。"
                      "既存の DB と組み合わせて使い、記録したデータが後から改変されて"
                      "いないことを検証できます。Ledger と Auditor を別の管理ドメインに"
                      "置くことで、運用者自身による改ざんも検知できます。",
             usecases=["電子文書の証拠保全",
                       "監査証跡・トレーサビリティ",
                       "同意と利用履歴の記録",
                       "ブロックチェーンのオフチェーン構築"],
             value="3.14 では正しさの検証に不要なメタデータを自動パージでき、"
                   "長期運用にともなうストレージ使用量と保存コストの増加を抑えられます。",
             notes=f"出典: {PR_DL314}（ScalarDL 3.14、2026年8月）。"
                   f"既存環境のメタデータを消去するツールも提供される。"
                   f"ScalarDL の SQL 対応の正式な姿は TableStore（3.12+）。"),
    ]


def usecases(P):
    return [
        dict(title="サービスを分けても、業務データの整合性は落とさない",
             accent=P.primary, figure=fig_uc_microservices,
             badge="AI 駆動開発とマイクロサービス",
             challenge="サービス単位に分割すると、それぞれが独立した DB や外部システムを"
                       "使うため、サービスをまたぐ整合性の保証が難しくなります。"
                       "片方だけ成功する部分的な不整合は、決済・在庫引き当て・受発注・"
                       "契約といった重要業務に直接影響します。補償処理をアプリ側で"
                       "作り込むと保守コストも上がります。",
             approach=["強い整合性が要る範囲は ScalarDB の 2PC",
                       "3.19 の新 I/F で 2PC を 1 フェーズで記述",
                       "外部 API・長時間処理は ScalarDB Saga",
                       "業務要件に応じて方式を選び分ける"],
             products="使う製品",
             effect="ScalarDB ＋ ScalarDB Saga —— "
                    "サービス分割の自由度を保ったまま、業務全体としての整合性を維持できます。",
             notes=f"出典: {PR_319}。マイクロサービス化は、AI が一度に理解すべき情報量を"
                   f"小さく保ち正確なコード生成を促すため、AI 駆動開発の前提として"
                   f"重要性が高まっている、というのが 3.19 の論旨。"),
        dict(title="散在したデータを、移さずに AI から使えるようにする",
             accent=P.info, figure=fig_uc_ai_data,
             badge="RAG / AI アプリケーションのデータ基盤",
             challenge="AI や RAG で使いたいデータが部門ごとの DB に散在し、"
                       "接続開発とデータのコピーが積み上がります。コピーを重ねるほど"
                       "鮮度と一貫性が落ち、アクセス制御も DB ごとに作り込む必要が"
                       "あります。結果として、AI に渡せるデータの範囲が限られます。",
             approach=["統一 API で異種 DB を仮想統合",
                       "ベクトルストアも同じ API（プレビュー）",
                       "Analytics で ETL なしに横断分析",
                       "暗号化・レコード単位のアクセス制御"],
             products="使う製品",
             effect="ScalarDB ＋ ScalarDB Analytics —— "
                    "データを別基盤へコピーせずに AI へ供給でき、権限と鮮度を保ったまま活用できます。",
             notes="出典: https://www.scalar-labs.com/ja/scalardb（RAG サポート・"
                   "Unified Security）、公式スライド「Scalar製品の適用領域の例」"
                   "（Secure RAG / AI Based System）。ベクトル検索は Enterprise Premium・"
                   "プレビュー提供のため、案件では提供状況を要確認。Analytics の "
                   "AI データカタログ機能は開発中（3.19 プレスリリースの今後の展望）。"),
        dict(title="AI が作った・変えたデータの「いつ・何を」を残す",
             accent=P.success, figure=fig_uc_evidence,
             badge="証拠保全・トレーサビリティ・同意記録",
             challenge="AI が生成・改変したデータが増えるほど、「いつ・何が・どの順序で"
                       "存在したか」を後から示すことが難しくなります。学習データの由来や"
                       "同意の取得履歴の説明を求められる場面も増えています。一方で全"
                       "ファイルへのタイムスタンプ押印は現実的ではありません。",
             approach=["実データではなくハッシュ値を順序付きで記録",
                       "改ざんがあれば検証時に検知できる",
                       "同意記録・利用履歴もアセットとして残す",
                       "Ledger + Auditor で運用者の改ざんも検知"],
             products="使う製品",
             effect="ScalarDL —— 大容量のファイルや大量のログでも、"
                    "実データを預けることなく証拠性を確保できます。",
             notes="出典: 公式スライド「Scalar製品の適用領域の例」（電子文書の証拠保全 / "
                   "同意記録・利用履歴記録 / データ主権の担保）、"
                   "https://scalardl.scalar-labs.com/docs/latest/overview/。"
                   "※ AI 生成物の証拠保全に特化した公表事例は無く、"
                   "公表事例はトヨタ自動車 PCE（知財文書）。適用領域からの整理として提示すること。"),
    ]


def cases(P):
    return [
        dict(title="十数年動かせなかったモノリスを、MVP 実質 3 か月で刷新",
             accent=P.primary, figure=fig_case_tsuneishi,
             org="常石造船株式会社様 — 基幹システムの刷新",
             challenge="十数年にわたり肥大化したモノリスの刷新に着手できず、"
                       "システムがブラックボックス化して市場への対応を"
                       "阻害していました。",
             solution="業務ドメイン単位で 9 つのマイクロサービスに分割。ScalarDB で"
                      "整合性を担保し、Kong Konnect で API を管理。AI 駆動開発で"
                      "構築しました。",
             metrics=[("2 日", "現状分析・再設計の期間"),
                      ("実質 3 か月", "MVP の構築期間"),
                      ("2 名", "常駐した IT 担当者")],
             effect="AI 駆動開発とマイクロサービス化の組み合わせで、"
                    "レガシー刷新の着手から MVP までを短期間で通しました（工数は約 70% 削減と報道）。",
             source="出典: 株式会社Scalar プレスリリース（2026年6月10日）、Kong Konnect 共同発表、MONOist 記事",
             notes=f"出典: {PR_TSUNEISHI} / "
                   f"https://monoist.itmedia.co.jp/mn/articles/2606/25/news030.html（工数 70% 削減）/ "
                   f"https://jp.konghq.com/news/kong-tsuneishi-ai-core-system-modernization。"
                   f"深津 CEO は「マイクロサービス化」「ScalarDB」「Kong Konnect」の組み合わせが"
                   f"エンタープライズモダナイゼーションのリファレンスケースになるとコメント。"),
        dict(title="大量の知財文書に、押印なしで証拠力を持たせる",
             accent=P.success, figure=fig_case_toyota,
             org="トヨタ自動車様 — PCE：電子ファイルの証拠保全",
             challenge="知財のコンタミを回避し、係争時に自社の知財文書の証拠を保全する"
                       "必要がありましたが、全ファイルへのタイムスタンプ押印は"
                       "現実的に困難でした。",
             solution="Box や SharePoint のファイル変更を検知してハッシュを計算し、"
                      "ScalarDL で順序性を持たせて記録。1 日 1 回、アセットの証拠に"
                      "タイムスタンプを付与します。",
             metrics=[("10 年超", "証明できる期間"),
                      ("ハッシュ値のみ", "台帳に置く情報"),
                      ("SaaS 外販", "PCE として提供")],
             effect="自社だけでなく取引先も含めた知財文書の保全を実現。"
                    "PCE（Proof Chain of Evidence）として SaaS 外販にもつながりました。",
             source="出典: 株式会社Scalar 公式導入事例、Microsoft News Center Japan（2022年3月）。基盤は Microsoft Azure",
             notes="出典: Scalar 公式ボイラープレート「トヨタ自動車様 - PCE:電子ファイルの証拠保全」/ "
                   "https://news.microsoft.com/ja-jp/2022/03/31/220331-proof-chain-of-evidence/ / "
                   "https://www.scalar-labs.com/ja/post/scalar-dl-tamper-detection-technology-makes-it-possible。"
                   "最初のユースケースは発明の先使用権の証明。"),
        dict(title="制作局ごとの自由度と、全社の統制を両立する",
             accent=P.primary, figure=fig_case_broadcaster,
             org="大手放送局様 — 公開コンテンツデータ管理システム",
             challenge="オンプレのシングル DB では、制作局ごとの機動的なスキーマ変更や"
                       "アクセス急増への対応ができず、API 化されていない点にも"
                       "課題がありました。",
             solution="公開領域をクラウドへ移行。番組情報は IT 部門が RDBMS で、"
                      "制作局のコンテンツは NoSQL で管理。ScalarDB が両者の整合性を"
                      "担保し、API 化しました。",
             metrics=[("RDBMS + NoSQL", "用途に応じた使い分け"),
                      ("API 化", "セキュリティを担保"),
                      ("従量課金", "アクセス変動に最適化")],
             effect="中央集権と分散管理を両立し、公開・非公開の制御は IT 部門が、"
                    "制作局固有のデータ拡張は各制作局が担えるようになりました。",
             source="出典: 株式会社Scalar 公式導入事例「大手放送局様 - 公開コンテンツデータ管理システム」（企業名非公開）",
             notes="出典: Scalar 公式ボイラープレート「大手放送局様 - 公開コンテンツデータ管理システム」。"
                   "企業名は非公開のため、資料上は必ず「大手放送局様」と表記すること。"),
    ]


# ---------------------------------------------------------------- Generation

def build(deck, template) -> list[str]:
    problems: list[str] = []

    def page(item, drawer):
        ref = deck.add_slide("TITLE_ONLY", title=item["title"],
                             notes=item.get("notes"))
        d = Canvas(deck, ref["slideId"], template)
        drawer(d, item, item["accent"])
        problems.extend(f"{item['title'][:14]}…: {m}" for m in
                        (d.audit_bounds() + d.audit_connectors()
                         + d.audit_overlaps() + d.audit_text_fit()))

    deck.add_slide("COVER", title=TITLE, subtitle=SUBTITLE,
                   body=f"{DATE}\n株式会社Scalar")

    probe = Canvas(deck, "probe", template)
    P = probe.P

    lineup = dict(title="4 つの製品で、散らばったデータを「正しく」使えるようにする",
                  accent=P.primary,
                  notes="出典: https://www.scalar-labs.com/ja/products（ScalarDB = Universal "
                        "HTAP エンジン / ScalarDL = 改ざん検知ミドルウェア）、ScalarDB 3.19 "
                        "プレスリリース（2026年8月、ScalarDB Saga 提供開始）、ScalarDL 3.14"
                        "（2026年8月）。公式のエディション区分は Community / Enterprise Standard / "
                        "Enterprise Premium。「ScalarDB Enterprise Edition」は公式の製品名では"
                        "ないため、この資料では使用しない（research-2026-08 の落とし穴 8）。")
    ref = deck.add_slide("TITLE_ONLY", title=lineup["title"],
                         notes=lineup["notes"])
    d = Canvas(deck, ref["slideId"], template)
    fig_lineup(d, P.primary)
    problems.extend(f"ラインナップ: {m}" for m in
                    (d.audit_bounds() + d.audit_connectors()
                     + d.audit_overlaps() + d.audit_text_fit()))

    for item in products(P):
        page(item, draw_product)
    for item in usecases(P):
        page(item, draw_usecase)
    for item in cases(P):
        page(item, draw_case)

    deck.add_slide("CLOSING")
    deck.add_page_numbers()

    return problems


def main() -> int:
    return bd.run_build_cli(build, template=TEMPLATE, title=TITLE, count=13)


if __name__ == "__main__":
    sys.exit(main())
