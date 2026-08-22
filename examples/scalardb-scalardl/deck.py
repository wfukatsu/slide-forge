#!/usr/bin/env python3
"""ScalarDB / ScalarDL 製品機能解説（55 枚）— slide-forge の実例デッキ。

developers.scalar-labs.com の公開ドキュメントに基づく機能カタログ。
1 機能 1 ページで、全ページに図解を持つ構成の見本として同梱している。

    # 座標検査（API を呼ばない）
    ../../.venv/bin/python ../../scripts/validate_layout.py deck.py

    # 生成
    ../../.venv/bin/python ../../scripts/render_deck.py deck.py

TEMPLATE は環境変数 SLIDE_FORGE_TEMPLATE で差し替えられる。既定は
templates/blank-16x9.json（マスター無しで新規プレゼンを作る設定）なので、
自社マスターを使う場合は inspect_template.py で登録したものを指定する。
"""
from __future__ import annotations

import json
import os
import sys

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(_ROOT, "scripts"))

from deckkit import *  # noqa: E402,F403

TITLE = "ScalarDB / ScalarDL 製品機能解説"

TEMPLATE = json.load(open(
    os.environ.get("SLIDE_FORGE_TEMPLATE",
                   os.path.join(_ROOT, "templates", "blank-16x9.json")),
    encoding="utf-8"))

# =====================================================================
# 1. 表紙・全体像
# =====================================================================

# 表紙は TITLE + SUBTITLE だけで構成する。BODY を持つマスターは限られるため、
# 日付やバージョンも subtitle の 2 行目に入れて可搬性を保つ。
plain(layout="COVER",
      title="ScalarDB / ScalarDL 製品機能解説",
      subtitle="異種データベースを横断する ACID トランザクションと、改ざん検知のための機能別リファレンス\n"
               "2026年7月 ／ ScalarDB 3.18・ScalarDL 3.13 時点",
      notes="developers.scalar-labs.com の公開ドキュメントに基づく技術者向け機能カタログ。1機能=1ページ、各ページに図解を付けています。")

plain(layout="SECTION", title="1. 製品全体像",
      body="何を解決する製品群なのか、どのコンポーネントで構成されるのか",
      notes="まず全体像を押さえます。")


@slide("データベースのサイロ化が、整合性とコストを同時に悪化させる",
       note="課題は整合性・鮮度・移植性の3点。ScalarDB は既存DBを置き換えずに、間に入って解決します。")
def s_problem(d):
    pw = (W - 0.5) / 2
    # --- 左: 現状 ---
    zone(d, X0, DY0, pw, 3.30, "現状：DB ごとに個別実装", stroke=lighten(d.P.danger, 0.6),
         fill="#FEF7F8")
    d.shape(X0 + 0.55, DY0 + 0.40, pw - 1.1, 0.42, kind="ROUND_RECTANGLE",
            fill=lighten(d.P.danger, 0.80), stroke=lighten(d.P.danger, 0.5),
            text="アプリケーション", size=9.5, bold=True, color=d.P.text)
    names = ["MySQL", "Cassandra", "DynamoDB", "PostgreSQL"]
    bw, bgap = 0.72, 0.20
    tot = len(names) * bw + (len(names) - 1) * bgap
    sx = X0 + (pw - tot) / 2
    for i, nm in enumerate(names):
        bx = sx + i * (bw + bgap)
        d.line(X0 + pw / 2, DY0 + 0.84, bx + bw / 2, DY0 + 1.62,
               color=lighten(d.P.danger, 0.35), weight=1.0, dashed=True)
        db(d, bx, DY0 + 1.66, bw, 0.60, nm)
    xmark(d, X0 + pw / 2, DY0 + 1.24)
    caption(d, X0 + 0.15, DY0 + 2.52, pw - 0.3,
            "整合性は Saga / 補償トランザクションを自作\n分析は ETL 経由で鮮度が落ちる\nDB 変更＝アプリ改修（ロックイン）",
            color=darken(d.P.danger, 0.15), h=0.7)

    # --- 中央の矢印 ---
    d.arrow_shape(X0 + pw + 0.02, DY0 + 1.30, 0.46, 0.5, fill=lighten(d.P.primary, 0.7))

    # --- 右: ScalarDB 導入後 ---
    rx = X0 + pw + 0.5
    zone(d, rx, DY0, pw, 3.30, "ScalarDB 導入後：横断で1回だけ書く",
         stroke=lighten(d.P.success, 0.5), fill="#F6FCF4")
    d.shape(rx + 0.55, DY0 + 0.40, pw - 1.1, 0.42, kind="ROUND_RECTANGLE",
            fill=lighten(d.P.success, 0.80), stroke=lighten(d.P.success, 0.5),
            text="アプリケーション", size=9.5, bold=True, color=d.P.text)
    d.solid(rx + 0.35, DY0 + 1.02, pw - 0.7, 0.44, "ScalarDB（ACID / 分析を横断で提供）", size=9.5)
    d.arrow(rx + pw / 2, DY0 + 0.84, rx + pw / 2, DY0 + 1.00, color=d.P.primary, weight=1.5)
    sx = rx + (pw - tot) / 2
    for i, nm in enumerate(names):
        bx = sx + i * (bw + bgap)
        d.line(rx + pw / 2, DY0 + 1.48, bx + bw / 2, DY0 + 1.62,
               color=lighten(d.P.primary, 0.35), weight=1.0)
        db(d, bx, DY0 + 1.66, bw, 0.60, nm)
    checkmark(d, rx + pw - 0.30, DY0 + 1.24)
    caption(d, rx + 0.15, DY0 + 2.52, pw - 0.3,
            "既存 DB をそのまま使い、横断 ACID を後付け\nETL なしで現行データを直接分析\nアプリ非改修で DB を差し替え可能",
            color=darken(d.P.success, 0.35), h=0.7)

    foot(d, ["・ScalarDB はアプリと DB の間に入るミドルウェア。既存資産を置き換えずに整合性・鮮度・移植性をまとめて解く"])


@slide("Core / Cluster / Analytics の3層で HTAP を実現する",
       note="Core は OSS、Cluster と Analytics が商用。Cluster は OLTP、Analytics は OLAP と役割が分かれます。")
def s_arch3(d):
    # アプリ層
    aw = (W - 0.4) / 2
    d.shape(X0, DY0, aw, 0.40, kind="ROUND_RECTANGLE", fill=lighten(d.P.primary, 0.88),
            stroke=lighten(d.P.primary, 0.6), text="業務アプリ（OLTP）", size=9.5, bold=True,
            color=d.P.text)
    d.shape(X0 + aw + 0.4, DY0, aw, 0.40, kind="ROUND_RECTANGLE",
            fill=lighten(d.P.info, 0.88), stroke=lighten(d.P.info, 0.6),
            text="BI / 分析（OLAP）", size=9.5, bold=True, color=d.P.text)

    # Cluster / Analytics
    y1 = DY0 + 0.56
    d.arrow(X0 + aw / 2, DY0 + 0.42, X0 + aw / 2, y1 - 0.02, color=d.P.primary, weight=1.5)
    d.arrow(X0 + aw + 0.4 + aw / 2, DY0 + 0.42, X0 + aw + 0.4 + aw / 2, y1 - 0.02,
            color=d.P.info, weight=1.5)
    d.shape(X0, y1, aw, 0.86, kind="ROUND_RECTANGLE", fill=d.P.primary, stroke=None)
    d.label(X0 + 0.12, y1 + 0.07, aw - 0.24, 0.26, "ScalarDB Cluster（商用）", size=10,
            bold=True, align="CENTER", color="#FFFFFF")
    d.label(X0 + 0.12, y1 + 0.34, aw - 0.24, 0.46,
            "SQL / GraphQL / gRPC・認証認可・暗号化\nベクトル検索・レプリケーション",
            size=8.5, align="CENTER", color="#E8F1FA", line_spacing=110)
    d.shape(X0 + aw + 0.4, y1, aw, 0.86, kind="ROUND_RECTANGLE", fill=d.P.info, stroke=None)
    d.label(X0 + aw + 0.52, y1 + 0.07, aw - 0.24, 0.26, "ScalarDB Analytics（商用）",
            size=10, bold=True, align="CENTER", color="#FFFFFF")
    d.label(X0 + aw + 0.52, y1 + 0.34, aw - 0.24, 0.46,
            "Apache Spark プラグイン\nSQL / DataSet API・データカタログ",
            size=8.5, align="CENTER", color="#E8F1FA", line_spacing=110)

    # Core
    y2 = y1 + 1.02
    d.arrow(X0 + aw / 2, y1 + 0.88, X0 + aw / 2, y2 - 0.02, color=d.P.primary, weight=1.5)
    d.arrow(X0 + aw + 0.4 + aw / 2, y1 + 0.88, X0 + aw + 0.4 + aw / 2, y2 - 0.02,
            color=d.P.info, weight=1.5)
    d.shape(X0, y2, W, 0.74, kind="ROUND_RECTANGLE", fill=d.P.primaryDark, stroke=None)
    d.label(X0 + 0.15, y2 + 0.06, W - 0.3, 0.26, "ScalarDB Core（Apache 2.0 / OSS）",
            size=10, bold=True, align="CENTER", color="#FFFFFF")
    d.label(X0 + 0.15, y2 + 0.33, W - 0.3, 0.36,
            "Consensus Commit（DB 非依存のトランザクション管理）　＋　CRUD インターフェース　＋　DB アダプタ層",
            size=9, align="CENTER", color="#D7E6F2")

    # DB 層
    y3 = y2 + 0.92
    names = [("MySQL", "JDBC"), ("PostgreSQL", "JDBC"), ("Oracle / Db2", "JDBC"),
             ("Cassandra", "Cassandra"), ("DynamoDB", "DynamoDB"),
             ("Cosmos DB", "Cosmos DB"), ("S3 / GCS", "Object storage")]
    bw = (W - 0.16 * (len(names) - 1)) / len(names)
    for i, (nm, ad) in enumerate(names):
        bx = X0 + i * (bw + 0.16)
        d.line(X0 + W / 2, y2 + 0.76, bx + bw / 2, y3 - 0.02,
               color=lighten(d.P.primary, 0.5), weight=0.9)
        db(d, bx + 0.06, y3, bw - 0.12, 0.44, nm, sub=ad)

    foot(d, ["・Core が正しさを担保し、Cluster が OLTP のサーバ機能、Analytics が OLAP を担う。"
             "3者は同じ Core のデータモデル上に載る"])


@slide("エディションによって利用できる機能範囲が決まる",
       note="Private Preview の機能を前提にした設計は避けてください。ABAC は現時点で日本国内のお客様限定です。")
def s_editions(d):
    rows = [
        ["DB 横断トランザクション（CRUD）", "●", "●", "●", "GA"],
        ["クラスタリング", "−", "●", "●", "GA"],
        ["非トランザクショナル操作", "−", "●", "●", "GA 3.14+"],
        ["認証・認可 / OIDC JWT", "−", "●", "●", "GA"],
        ["通信暗号化（TLS）", "−", "●", "●", "GA"],
        ["SQL インターフェース", "−", "−", "●", "GA"],
        ["GraphQL インターフェース", "−", "−", "●", "GA"],
        ["保存データ暗号化", "−", "−", "●", "GA 3.14+"],
        ["ABAC（レコード単位認可）", "−", "−", "○", "Preview 3.15+"],
        ["ベクトル検索", "−", "−", "○", "Preview 3.15+"],
        ["リモートレプリケーション", "−", "−", "○", "Preview 3.16+"],
    ]

    def cc(i, j, cell):
        if j in (1, 2, 3):
            if cell == "●":
                return (lighten(d.P.success, 0.80), darken(d.P.success, 0.45))
            if cell == "○":
                return (lighten(d.P.warning, 0.70), darken(d.P.warning, 0.55))
            return (None, lighten(d.P.muted, 0.45))
        return None

    grid(d, X0, DY0, W, ["機能", "Community", "Ent. Standard", "Ent. Premium", "提供状況"],
         rows, col_w=[3.20, 1.30, 1.40, 1.35, 1.75], row_h=0.255, head_h=0.30, cell_colors=cc)
    y = DY0 + 0.30 + len(rows) * 0.255 + 0.08
    d.label(X0, y, W, 0.24,
            "●＝GA で利用可能　　○＝Private Preview　　−＝非提供　　"
            "／ ScalarDB Analytics は別枠の Enterprise Option（GA）",
            size=8.5, align="START", valign="TOP", color=d.P.muted)
    foot(d, ["・機能ページの最下部に提供エディションと提供状況を明記している。採用検討時はここを最初に確認する"])


# =====================================================================
# 2. ScalarDB Core
# =====================================================================

plain(layout="SECTION", title="2. ScalarDB Core — トランザクション基盤",
      body="Consensus Commit、マルチストレージ、データモデル、API",
      notes="OSS である Core の機能群です。")


@slide("Consensus Commit が DB 横断で strict serializable を実現する",
       note="下位DBに求めるのは linearizable な条件付き書き込みだけ。DB側のトランザクション機能は前提にしません。")
def s_cc(d):
    # 左: 3フェーズ
    lw = 3.45
    zone(d, X0, DY0, lw, 2.05, "トランザクションの3フェーズ")
    ph = [("読み込みフェーズ", "read set / write set をローカルに保持"),
          ("検証フェーズ", "後方検証で競合を検出（OCC）"),
          ("書き込みフェーズ", "DB に反映し他トランザクションに可視化")]
    for i, (h_, b_) in enumerate(ph):
        py = DY0 + 0.34 + i * 0.55
        d.shape(X0 + 0.14, py, lw - 0.28, 0.46, kind="ROUND_RECTANGLE",
                fill=lighten(d.P.primary, 0.90), stroke=lighten(d.P.primary, 0.65))
        d.label(X0 + 0.26, py + 0.04, lw - 0.52, 0.22, h_, size=9.5, bold=True,
                align="START", valign="TOP", color=d.P.primaryDark)
        d.label(X0 + 0.26, py + 0.25, lw - 0.52, 0.20, b_, size=8, align="START",
                valign="TOP", color=d.P.text)
        if i < 2:
            d.arrow(X0 + lw / 2, py + 0.47, X0 + lw / 2, py + 0.54, color=d.P.primary, weight=1.3)
    caption(d, X0 + 0.14, DY0 + 2.10, lw - 0.28,
            "同時実行制御＝楽観的同時実行制御（OCC）\nアトミックコミット＝2PC の変種",
            align="START", h=0.5)

    # 右: レコードのメタデータ列 + Coordinator
    rx = X0 + lw + 0.35
    rw = XE - rx
    zone(d, rx, DY0, rw, 1.62, "レコードに付与される管理メタデータ")
    cols = [("アプリ\nデータ", 1.05, lighten(d.P.primary, 0.92)),
            ("tx_id", 0.82, lighten(d.P.info, 0.80)),
            ("version", 0.86, lighten(d.P.info, 0.80)),
            ("state", 0.80, lighten(d.P.info, 0.80)),
            ("before\nimage", 0.95, lighten(d.P.info, 0.80))]
    cw_tot = sum(c[1] for c in cols) + 0.06 * (len(cols) - 1)
    cx = rx + (rw - cw_tot) / 2
    for nm, cw, col in cols:
        d.shape(cx, DY0 + 0.36, cw, 0.44, kind="RECTANGLE", fill=col,
                stroke=lighten(d.P.primary, 0.6), stroke_weight=0.75,
                text=nm, size=8, color=d.P.text, line_spacing=100)
        cx += cw + 0.06
    caption(d, rx + 0.12, DY0 + 0.86, rw - 0.24,
            "state ＝ COMMITTED / PREPARED / DELETED / ABORTED\n"
            "before image を持つためロールバックできる",
            align="START", h=0.5)
    d.label(rx + 0.12, DY0 + 1.32, rw - 0.24, 0.24,
            "※ 下位 DB に求めるのは linearizable な条件付き書き込みのみ",
            size=8, align="START", valign="TOP", color=d.P.muted)

    zone(d, rx, DY0 + 1.76, rw, 1.34, "Coordinator テーブル")
    d.shape(rx + 0.35, DY0 + 2.14, rw - 0.70, 0.42, kind="ROUND_RECTANGLE",
            fill=d.P.primary, stroke=None, text="tx_id → 最終状態", size=9.5,
            bold=True, color="#FFFFFF")
    caption(d, rx + 0.12, DY0 + 2.62, rw - 0.24,
            "トランザクション状態の single source of truth。\nここに COMMITTED が書けた時点でコミット確定。",
            align="START", h=0.5)

    foot(d, ["・下位 DB のトランザクション機能に依存せず、ミドルウェア層だけで ACID（strict serializability）を実現する独自プロトコル"],
         "提供: Community / Enterprise Standard / Enterprise Premium ｜ 状況: GA")


@slide("アトミックコミットは4つのサブフェーズで進み、3番目で確定する",
       note="コミットの確定点は3番目の commit-state。4番目は非同期化できるためレイテンシに直接効きません。")
def s_cc_phases(d):
    LX, LW = X0, 1.30                      # レーン名の列
    CX = X0 + LW + 0.10                    # フェーズ列の開始
    CW = XE - CX
    LH = 1.08                              # レーンの高さ
    y_rec = DY0 + 0.30                     # レコードのレーン
    y_crd = y_rec + LH + 0.34              # Coordinator のレーン

    for ly, nm, col in [(y_rec, "レコード\n（各 DB）", lighten(d.P.primary, 0.50)),
                        (y_crd, "Coordinator\nテーブル", d.P.primary)]:
        d.shape(LX, ly, LW, LH, kind="ROUND_RECTANGLE", fill=col, stroke=None,
                text=nm, size=9, bold=True, color="#FFFFFF", line_spacing=105)
        d.shape(CX, ly, CW, LH, kind="ROUND_RECTANGLE", fill=lighten(col, 0.94),
                stroke=lighten(col, 0.78), stroke_weight=0.75)

    bw, gap = (CW - 0.24 - 3 * 0.20) / 4, 0.20
    phases = [
        ("1. prepare-records", "PREPARED 状態で書き込み\n書き込み競合を検出",
         y_rec, lighten(d.P.primary, 0.78), d.P.text),
        ("2. validate-records", "read set を再読込し\nanti-dependency を検出",
         y_rec, lighten(d.P.warning, 0.58), darken(d.P.warning, 0.55)),
        ("3. commit-state", "COMMITTED を書き込む\n★ ここでコミット確定",
         y_crd, d.P.success, "#FFFFFF"),
        ("4. commit-records", "レコードを COMMITTED に\n（非同期化できる後処理）",
         y_rec, lighten(d.P.primary, 0.78), d.P.text),
    ]
    centers = []
    for i, (nm, body, by, col, txt) in enumerate(phases):
        bx = CX + 0.12 + i * (bw + gap)
        d.shape(bx, by + 0.12, bw, LH - 0.24, kind="ROUND_RECTANGLE", fill=col,
                stroke=None)
        d.label(bx + 0.06, by + 0.20, bw - 0.12, 0.24, nm, size=9, bold=True,
                align="CENTER", color=txt)
        d.label(bx + 0.06, by + 0.45, bw - 0.12, 0.44, body, size=8,
                align="CENTER", color=txt, line_spacing=110)
        centers.append((bx, bx + bw, by + LH / 2))

    # フェーズ間の矢印はレーンをまたぐので、実際の経路どおりに引く
    for i in range(3):
        _, x_end, y1 = centers[i]
        x_start, _, y2 = centers[i + 1]
        d.arrow(x_end + 0.03, y1, x_start - 0.03, y2, color=d.P.primary, weight=1.6)

    # 注記
    d.shape(centers[1][0], y_rec - 0.30, bw, 0.26, kind="ROUND_RECTANGLE",
            fill=lighten(d.P.warning, 0.70), stroke=None,
            text="SERIALIZABLE のときのみ実行", size=7.5, color=darken(d.P.warning, 0.55))
    d.shape(centers[3][0], y_rec - 0.30, bw, 0.26, kind="ROUND_RECTANGLE",
            fill=lighten(d.P.primary, 0.82), stroke=None,
            text="非同期・並列化の対象", size=7.5, color=d.P.primaryDark)

    y = y_crd + LH + 0.16
    d.shape(X0, y, W, 0.40, kind="ROUND_RECTANGLE", fill=lighten(d.P.success, 0.84),
            stroke=lighten(d.P.success, 0.5),
            text="★ コミットの確定点は3番目。Coordinator に COMMITTED が書けた瞬間に、"
                 "そのトランザクションはコミット済みとして扱われる",
            size=9, bold=True, color=darken(d.P.success, 0.45))

    foot(d, ["・4番目は確定後の後処理にすぎないため、非同期化してもコミットのレイテンシには影響しない"],
         "提供: Community / Enterprise Standard / Enterprise Premium ｜ 状況: GA")


@slide("分離レベルは3段階から、正しさと性能のバランスで選ぶ",
       note="既定が SNAPSHOT である点に注意。write skew を許容できない設計なら明示的に SERIALIZABLE を設定してください。")
def s_isolation(d):
    # 軸
    d.arrow_shape(X0, DY0, W, 0.34, fill=lighten(d.P.primary, 0.80))
    d.label(X0 + 0.2, DY0 + 0.05, 3.0, 0.24, "← 速い", size=9, bold=True,
            align="START", color=d.P.primaryDark)
    d.label(XE - 3.2, DY0 + 0.05, 3.0, 0.24, "正しさが強い →", size=9, bold=True,
            align="END", color=d.P.primaryDark)

    cw = (W - 0.4) / 3
    items = [
        ("READ_COMMITTED", "最速", ["read validation を省略", "最新のコミット済みレコードが",
                                  "返らない可能性がある"], lighten(d.P.primary, 0.55)),
        ("SNAPSHOT（既定）", "中間", ["SERIALIZABLE より高速", "read skew / write skew が",
                                   "起こりうる"], d.P.primary),
        ("SERIALIZABLE", "最も強い", ["strict serializability を保証", "validate-records フェーズが",
                                   "加わるため遅い"], d.P.primaryDark),
    ]
    for i, (nm, tag, lines, col) in enumerate(items):
        cx = X0 + i * (cw + 0.2)
        d.shape(cx, DY0 + 0.50, cw, 1.42, kind="ROUND_RECTANGLE",
                fill=lighten(col, 0.93), stroke=col, stroke_weight=1.25)
        d.shape(cx, DY0 + 0.50, cw, 0.36, kind="RECTANGLE", fill=col, stroke=None,
                text=nm, size=9.5, bold=True, color="#FFFFFF")
        d.label(cx + 0.1, DY0 + 0.92, cw - 0.2, 0.22, tag, size=8.5, bold=True,
                align="CENTER", color=darken(col, 0.2))
        d.label(cx + 0.14, DY0 + 1.16, cw - 0.28, 0.70, "\n".join("・" + s for s in lines),
                size=8.5, align="START", valign="TOP", color=d.P.text, line_spacing=115)

    # アノマリ表
    rows = [["read skew（読み取りの不整合）", "起こる", "起こる", "起こらない"],
            ["write skew（書き込みの歪み）", "起こる", "起こる", "起こらない"],
            ["最新コミット済みが返らない", "起こる", "起こらない", "起こらない"]]

    def cc(i, j, cell):
        if j == 0:
            return None
        return ((lighten(d.P.danger, 0.86), darken(d.P.danger, 0.25)) if cell == "起こる"
                else (lighten(d.P.success, 0.82), darken(d.P.success, 0.45)))

    grid(d, X0, DY0 + 2.10, W, ["許容されるアノマリ", "READ_COMMITTED", "SNAPSHOT", "SERIALIZABLE"],
         rows, col_w=[3.30, 1.90, 1.90, 1.90], row_h=0.285, cell_colors=cc)

    foot(d, ["・複数レコードにまたがる不変条件があるなら SERIALIZABLE。単一レコード参照が主体なら SNAPSHOT / READ_COMMITTED で足りる"],
         "提供: Community / Enterprise Standard / Enterprise Premium ｜ 状況: GA")


@slide("遅延リカバリにより、専用プロセスなしで整合性が回復する",
       note="リカバリ用の常駐プロセスやログ再生の運用が不要になるのが実運用上の利点です。")
def s_recovery(d):
    FW = 6.30                       # フロー図の横幅（右に補足パネルを置く）
    cx = X0 + FW / 2                # フローの中心線
    bh = 0.46

    y = DY0 + 0.08
    d.shape(cx - 1.30, y, 2.60, bh, kind="ROUND_RECTANGLE", fill=lighten(d.P.primary, 0.88),
            stroke=lighten(d.P.primary, 0.6), text="レコードを読む", size=9.5, bold=True,
            color=d.P.text)

    y = y + bh + 0.16
    d.arrow(cx, y - 0.15, cx, y - 0.02, color=d.P.primary, weight=1.5)
    d.shape(cx - 1.85, y, 3.70, 0.74, kind="DIAMOND", fill=lighten(d.P.warning, 0.68),
            stroke=None)
    d.label(cx - 1.55, y + 0.18, 3.10, 0.42, "PREPARED のまま有効期限\n（既定 15 秒）を超過？",
            size=8.5, bold=True, align="CENTER", color=darken(d.P.warning, 0.55),
            line_spacing=105)
    # Yes 分岐（下へ）
    y2 = y + 0.74 + 0.30
    # No 分岐（右下へ。右側の補足パネルと重ならない位置に置く）
    no_x = cx + 1.30
    d.arrow(cx + 1.86, y + 0.37, no_x + 0.62, y2 - 0.02, color=d.P.muted, weight=1.3)
    # To the right of the arrow, not on it: this branch leaves the diamond
    # almost vertically, so a label started at its origin sits on the line
    d.label(cx + 1.95, y + 0.42, 0.45, 0.20, "No", size=8, align="START", color=d.P.muted)
    d.shape(no_x, y2, 1.24, bh, kind="ROUND_RECTANGLE", fill="#FFFFFF",
            stroke=lighten(d.P.muted, 0.3), text="そのまま\n読み進める", size=8,
            color=d.P.text, line_spacing=105)
    d.arrow(cx, y + 0.76, cx, y2 - 0.02, color=d.P.primary, weight=1.6)
    d.label(cx + 0.06, y + 0.80, 0.50, 0.20, "Yes", size=8, align="START", color=d.P.primary)
    d.shape(cx - 1.85, y2, 3.00, bh, kind="ROUND_RECTANGLE", fill=d.P.primary, stroke=None,
            text="Coordinator の最終状態を参照", size=9, bold=True, color="#FFFFFF")

    # 2つの帰結
    y3 = y2 + bh + 0.44
    hw = 2.95
    left_x, right_x = cx - FW / 2 + 0.10, cx + FW / 2 - hw - 0.10
    d.arrow(cx - 0.90, y2 + bh + 0.02, left_x + hw / 2, y3 - 0.02,
            color=d.P.danger, weight=1.5)
    d.arrow(cx - 0.30, y2 + bh + 0.02, right_x + hw / 2, y3 - 0.02,
            color=d.P.success, weight=1.5)
    # ラベルは矢印の経路を避けて外側に寄せる
    d.label(left_x + 0.04, y3 - 0.26, hw - 0.08, 0.22, "COMMITTED なし / ABORTED", size=7.5,
            align="START", color=d.P.muted)
    d.label(right_x + 0.04, y3 - 0.26, hw - 0.08, 0.22, "COMMITTED あり", size=7.5,
            align="END", color=d.P.muted)
    d.shape(left_x, y3, hw, 0.62, kind="ROUND_RECTANGLE",
            fill=lighten(d.P.danger, 0.86), stroke=lighten(d.P.danger, 0.5),
            text="ロールバック\nbefore image で元に戻す", size=9,
            color=darken(d.P.danger, 0.25), line_spacing=110)
    d.shape(right_x, y3, hw, 0.62, kind="ROUND_RECTANGLE",
            fill=lighten(d.P.success, 0.84), stroke=lighten(d.P.success, 0.5),
            text="ロールフォワード\nCOMMITTED まで進める", size=9,
            color=darken(d.P.success, 0.45), line_spacing=110)

    # 右の補足パネル
    px = X0 + FW + 0.30
    pw = XE - px
    zone(d, px, DY0 + 0.08, pw, 1.55, "この設計の効果")
    d.label(px + 0.14, DY0 + 0.42, pw - 0.28,
            1.15,
            "・専用のリカバリプロセスが不要\n"
            "・読み取り経路がリカバリ経路を兼ねる\n"
            "・ログ再生の運用が発生しない",
            size=8.5, align="START", valign="TOP", color=d.P.text, line_spacing=140)
    zone(d, px, DY0 + 1.75, pw, 1.55, "回復のタイミング")
    d.label(px + 0.14, DY0 + 2.09, pw - 0.28, 1.15,
            "コミット済みか否かの判断は、\n"
            "常に Coordinator テーブルの\n"
            "最終状態を正とする。",
            size=8.5, align="START", valign="TOP", color=d.P.text, line_spacing=140)

    foot(d, ["・クラッシュしたトランザクションの未コミットレコードは「次に読まれたとき」に、その状態に応じて遅延回復される"],
         "提供: Community / Enterprise Standard / Enterprise Premium ｜ 状況: GA")


@slide("4つの最適化でプロトコルのオーバーヘッドを削減する",
       note="特にグループコミットは Coordinator テーブルへの書き込みがボトルネックになるワークロードで効果があります。")
def s_optim(d):
    # 1PC の before/after
    zone(d, X0, DY0, W, 1.30, "1フェーズコミット最適化：書き込みが単一 DB のアトミック操作に収まる場合")
    labels = ["prepare-records", "validate-records", "commit-state", "commit-records"]
    bw = 1.62
    for row, (tag, keep, col) in enumerate([("通常", [1, 1, 1, 1], d.P.primary),
                                            ("1PC 最適化", [0, 1, 0, 1], d.P.success)]):
        ry = DY0 + 0.38 + row * 0.44
        d.label(X0 + 0.12, ry + 0.04, 1.05, 0.26, tag, size=9, bold=True,
                align="START", color=d.P.text)
        for i, nm in enumerate(labels):
            bx = X0 + 1.25 + i * (bw + 0.10)
            if keep[i]:
                d.shape(bx, ry, bw, 0.34, kind="ROUND_RECTANGLE", fill=lighten(col, 0.80),
                        stroke=lighten(col, 0.5), text=nm, size=8, color=d.P.text)
            else:
                d.shape(bx, ry, bw, 0.34, kind="ROUND_RECTANGLE", fill="#F2F4F7",
                        stroke=lighten(d.P.muted, 0.55), text="省略", size=8,
                        color=lighten(d.P.muted, 0.15))
    d.label(X0 + 1.25 + 4 * (bw + 0.10) - 0.05, DY0 + 0.60, 1.05, 0.46,
            "→ レイテンシ\n　 大幅削減", size=8.5, bold=True, align="START",
            valign="TOP", color=darken(d.P.success, 0.4), line_spacing=110)

    # 残り3つ
    d.cards(X0, DY0 + 1.44, W, 1.06, [
        ("並列実行", "各フェーズ内の複数レコードへの操作を並列化する"),
        ("非同期コミット / ロールバック", "commit-records とロールバックをコミット応答後に非同期実行"),
        ("グループコミット", "複数トランザクションの commit-state 書き込みを1回にまとめる"),
    ], accent=[d.P.info, d.P.info, d.P.success], title_size=10, body_size=8.5)

    # グループコミットの図
    gy = DY0 + 2.56
    zone(d, X0, gy, W, 0.84, "グループコミットの効果（Coordinator テーブルへの書き込み回数）")
    tx_x, wr_x = X0 + 2.60, X0 + 5.35
    d.label(tx_x, gy + 0.26, 2.40, 0.20, "トランザクション", size=7.5, align="START",
            color=d.P.muted)
    d.label(wr_x, gy + 0.26, 2.40, 0.20, "Coordinator への書き込み", size=7.5,
            align="START", color=d.P.muted)
    for row, (tag, grouped, col) in enumerate([("通常：Tx ごとに1回", False, lighten(d.P.primary, 0.45)),
                                               ("グループコミット", True, d.P.success)]):
        ry = gy + 0.46 + row * 0.23
        d.label(X0 + 0.12, ry - 0.02, 2.40, 0.22, tag, size=8.5, align="START", color=d.P.text)
        for i in range(5):
            d.shape(tx_x + i * 0.38, ry, 0.28, 0.18, kind="RECTANGLE",
                    fill=lighten(d.P.primary, 0.72), stroke=None)
        if grouped:
            d.shape(wr_x, ry, 1.90, 0.18, kind="ROUND_RECTANGLE", fill=col, stroke=None)
        else:
            for i in range(5):
                d.shape(wr_x + i * 0.38, ry, 0.28, 0.18, kind="RECTANGLE", fill=col, stroke=None)
        d.label(X0 + 7.45, ry - 0.03, 1.45, 0.22, "5 回" if not grouped else "1 回",
                size=8.5, bold=True, align="START", color=darken(col, 0.3))

    foot(d, ["・設定次第で性能が大きく変わる。既定値のまま測って判断せず、ベンチマークで最適化の有無を比較すること"],
         "提供: Community / Enterprise Standard / Enterprise Premium ｜ 状況: GA")


@slide("マルチストレージ機能が名前空間単位で DB を振り分ける",
       note="Coordinator テーブルをどのストレージに置くかは重要な設計判断です。トランザクション機能を持つ RDB に置くのが一般的です。")
def s_multistorage(d):
    # 1トランザクション
    d.shape(X0 + 2.7, DY0, 3.6, 0.40, kind="ROUND_RECTANGLE", fill=lighten(d.P.primary, 0.88),
            stroke=lighten(d.P.primary, 0.6),
            text="1つのトランザクション（ACID を維持）", size=9.5, bold=True, color=d.P.text)
    d.arrow(X0 + W / 2, DY0 + 0.42, X0 + W / 2, DY0 + 0.54, color=d.P.primary, weight=1.5)
    d.solid(X0 + 1.9, DY0 + 0.56, 5.2, 0.42, "ScalarDB（storage = multi-storage）", size=9.5)

    # namespace mapping
    y = DY0 + 1.08
    zone(d, X0, y, W, 1.00, "namespace_mapping による振り分け")
    maps = [("user", "cassandra"), ("order", "mysql"), ("coordinator", "mysql"),
            ("（未マッピング）", "default_storage")]
    cw = (W - 0.28 - 0.18 * 3) / 4
    for i, (ns, st) in enumerate(maps):
        cx = X0 + 0.14 + i * (cw + 0.18)
        d.shape(cx, y + 0.36, cw, 0.30, kind="ROUND_RECTANGLE",
                fill=lighten(d.P.info, 0.84), stroke=None, text=f"名前空間 {ns}", size=8.5,
                color=darken(d.P.info, 0.35))
        d.arrow(cx + cw / 2, y + 0.68, cx + cw / 2, y + 0.80, color=d.P.primary, weight=1.2)
        d.shape(cx, y + 0.80, cw, 0.24, kind="RECTANGLE", fill=None,
                stroke=None, text=st, size=8.5, bold=True, color=d.P.primaryDark)

    # ストレージ
    y2 = y + 1.06
    for i, (nm, ns_list, col) in enumerate([("Cassandra", "user", d.P.primary),
                                            ("MySQL", "order / coordinator", d.P.primary)]):
        sx = X0 + 1.30 + i * 3.60
        # sub は上の namespace_mapping と重複し、下の設定ボックスに隠れるので置かない
        db(d, sx, y2, 1.30, 0.52, nm)
    d.shape(X0 + 6.85, y2, 1.60, 0.52, kind="ROUND_RECTANGLE", fill="#F7F9FC",
            stroke=lighten(d.P.muted, 0.5), text="他のストレージ\n（追加可能）", size=8,
            color=d.P.muted, line_spacing=105)

    # 設定
    y3 = y2 + 0.78
    d.shape(X0, y3, W, 0.52, kind="ROUND_RECTANGLE", fill="#F4F6F9",
            stroke=lighten(d.P.muted, 0.6))
    d.label(X0 + 0.14, y3 + 0.03, W - 0.28, 0.48,
            "scalar.db.transaction_manager=consensus-commit　/　scalar.db.storage=multi-storage\n"
            "scalar.db.multi_storage.namespace_mapping=user:cassandra,order:mysql,coordinator:mysql"
            "　/　…default_storage=cassandra",
            size=8.5, align="START", valign="TOP", color=d.P.text, line_spacing=125)

    foot(d, ["・複数のストレージインスタンスを保持し、名前空間→ストレージのマッピングで振り分ける。跨いでも ACID が保たれる"],
         "提供: Community / Enterprise Standard / Enterprise Premium ｜ 状況: GA")


@slide("アダプタ層が RDB・NoSQL・オブジェクトストレージを束ねる",
       note="対応DBは版ごとに増えています。採用検討時は対象バージョンのドキュメントで最終確認してください。")
def s_adapters(d):
    d.shape(X0 + 2.4, DY0, 4.2, 0.40, kind="ROUND_RECTANGLE", fill=lighten(d.P.primary, 0.88),
            stroke=lighten(d.P.primary, 0.6), text="アプリケーション（統一 API）", size=9.5,
            bold=True, color=d.P.text)
    d.arrow(X0 + W / 2, DY0 + 0.42, X0 + W / 2, DY0 + 0.56, color=d.P.primary, weight=1.5)
    d.solid(X0 + 1.6, DY0 + 0.58, 5.8, 0.42, "ScalarDB Core（抽象化レイヤー）", size=9.5)

    groups = [
        ("JDBC アダプタ", ["MySQL", "MariaDB", "TiDB", "PostgreSQL", "YugabyteDB", "AlloyDB",
                        "Aurora (MySQL / PostgreSQL)", "Oracle Database", "SQL Server",
                        "IBM Db2", "Spanner (PG dialect)", "SQLite"], 3.55, d.P.primary),
        ("NoSQL アダプタ", ["Amazon DynamoDB", "Azure Cosmos DB for NoSQL",
                         "Apache Cassandra"], 2.55, d.P.info),
        ("オブジェクトストレージ", ["Amazon S3", "Azure Blob Storage",
                            "Google Cloud Storage"], 2.50, d.P.success),
    ]
    y = DY0 + 1.14
    x = X0
    for nm, items, gw, col in groups:
        d.arrow(X0 + W / 2, DY0 + 1.02, x + gw / 2, y - 0.02,
                color=lighten(col, 0.35), weight=1.3)
        d.shape(x, y, gw, 0.32, kind="ROUND_RECTANGLE", fill=col, stroke=None,
                text=nm, size=9.5, bold=True, color="#FFFFFF")
        per = 2 if gw > 3.0 else 1
        pw = (gw - 0.10 * (per - 1)) / per
        for i, it in enumerate(items):
            r, c = divmod(i, per)
            d.shape(x + c * (pw + 0.10), y + 0.36 + r * 0.25, pw, 0.225,
                    kind="ROUND_RECTANGLE", fill=lighten(col, 0.90),
                    stroke=lighten(col, 0.62), stroke_weight=0.75,
                    text=it, size=8, color=d.P.text)
        x += gw + 0.20

    y2 = y + 0.36 + 6 * 0.25 + 0.08
    d.shape(X0, y2, W, 0.34, kind="ROUND_RECTANGLE", fill=lighten(d.P.success, 0.85),
            stroke=None,
            text="アプリを書き換えずに下位 DB を差し替えられる → 移行・ロックイン回避に効く",
            size=9, bold=True, color=darken(d.P.success, 0.45))

    foot(d, ["・全アダプタが同じ論理データモデルに写すため、上位の API とトランザクションの挙動は DB を問わず変わらない"],
         "提供: Community / Enterprise Standard / Enterprise Premium ｜ 状況: GA（3.18 時点）")


@slide("統一データモデルは Bigtable 系の拡張キーバリューモデルを採る",
       note="RDB出身の設計者ほど正規化に寄せがちですが、ScalarDB ではアクセスパターンからスキーマを決めるのが定石です。")
def s_datamodel(d):
    # 階層
    lw = 2.05
    zone(d, X0, DY0, lw, 2.72, "階層")
    for i, (nm, col) in enumerate([("名前空間", d.P.primaryDark), ("テーブル", d.P.primary),
                                   ("パーティション", lighten(d.P.primary, 0.35)),
                                   ("レコード", lighten(d.P.primary, 0.60)),
                                   ("カラム", lighten(d.P.primary, 0.78))]):
        iy = DY0 + 0.36 + i * 0.45
        d.shape(X0 + 0.14 + i * 0.10, iy, lw - 0.28 - i * 0.10, 0.34,
                kind="ROUND_RECTANGLE", fill=col, stroke=None, text=nm, size=9,
                bold=True, color="#FFFFFF" if i < 4 else d.P.text)
        if i < 4:
            d.arrow(X0 + 0.30 + i * 0.10, iy + 0.35, X0 + 0.30 + i * 0.10, iy + 0.43,
                    color=d.P.muted, weight=1.1)

    # テーブル構造
    rx = X0 + lw + 0.30
    rw = XE - rx
    zone(d, rx, DY0, rw, 1.62, "テーブルのキー構成")
    # Widths follow the longest description line: at 8pt the clustering key's
    # wording needs 2.25in to stay on one line, and the zone has the room
    cols = [("パーティションキー", 2.10, d.P.primary, "パーティションを一意に識別\nハッシュで分散配置"),
            ("クラスタリングキー", 2.25, d.P.info, "パーティション内でレコードを識別\nこの順にソート→レンジスキャン"),
            ("一般カラム", 1.70, lighten(d.P.muted, 0.3), "アプリのデータ")]
    cx = rx + 0.14
    for nm, cw, col, desc in cols:
        d.shape(cx, DY0 + 0.36, cw, 0.32, kind="RECTANGLE", fill=col, stroke="#FFFFFF",
                stroke_weight=0.75, text=nm, size=8.5, bold=True, color="#FFFFFF")
        d.label(cx, DY0 + 0.74, cw, 0.60, desc, size=8, align="START", valign="TOP",
                color=d.P.text, line_spacing=115)
        cx += cw + 0.10
    d.shape(rx + 0.14, DY0 + 1.32, rw - 0.28, 0.24, kind="RECTANGLE",
            fill=lighten(d.P.warning, 0.72), stroke=None,
            text="セカンダリインデックス = 単一カラムのソート済みコピー（パーティション横断の参照に使う）",
            size=8, color=darken(d.P.warning, 0.55))

    # パーティション分散
    zone(d, rx, DY0 + 1.76, rw, 0.96, "パーティションはハッシュでノードに分散する")
    pw2 = (rw - 0.28 - 0.12 * 3) / 4
    for i in range(4):
        px = rx + 0.14 + i * (pw2 + 0.12)
        d.shape(px, DY0 + 2.14, pw2, 0.48, kind="ROUND_RECTANGLE",
                fill=lighten(d.P.primary, 0.90), stroke=lighten(d.P.primary, 0.62),
                text=f"パーティション {i + 1}\n同一ノードに配置", size=7.5,
                color=d.P.text, line_spacing=105)

    # 設計指針
    d.shape(X0, DY0 + 2.86, W, 0.34, kind="ROUND_RECTANGLE", fill=lighten(d.P.success, 0.85),
            stroke=None,
            text="設計指針：正規化ではなくクエリ駆動。単一パーティション参照に寄せると性能が出る",
            size=9, bold=True, color=darken(d.P.success, 0.45))

    foot(d, ["・RDB / NoSQL / NewSQL すべてに写せるよう抽象化されたモデル。ScalarDB のセカンダリインデックスは単一カラムのみ"],
         "提供: Community / Enterprise Standard / Enterprise Premium ｜ 状況: GA")


@slide("Java CRUD API はトランザクションのライフサイクルに沿って使う",
       note="読み取り専用トランザクションを明示すると不要な検証を省けます。Put は非推奨なので Insert / Update / Upsert を使い分けてください。")
def s_crud(d):
    # ライフサイクル
    zone(d, X0, DY0, W, 1.28, "トランザクションのライフサイクル")
    boxes = [("TransactionFactory\n.create()", 1.62, lighten(d.P.primary, 0.86)),
             ("DistributedTransaction\nManager", 1.72, lighten(d.P.primary, 0.86)),
             ("begin() / start()\nbeginReadOnly()", 1.62, d.P.primary),
             ("Get / Scan / Insert\nUpdate / Upsert / Delete", 1.90, lighten(d.P.info, 0.80)),
             ("commit()\nrollback()", 1.35, d.P.success)]
    tot = sum(b[1] for b in boxes) + 0.16 * (len(boxes) - 1)
    cx = X0 + (W - tot) / 2
    for i, (nm, bw, col) in enumerate(boxes):
        txt = "#FFFFFF" if col in (d.P.primary, d.P.success) else d.P.text
        d.shape(cx, DY0 + 0.40, bw, 0.62, kind="ROUND_RECTANGLE", fill=col,
                stroke=None if txt == "#FFFFFF" else lighten(d.P.primary, 0.6),
                text=nm, size=8.5, bold=True, color=txt, line_spacing=105)
        if i < len(boxes) - 1:
            d.arrow(cx + bw + 0.02, DY0 + 0.71, cx + bw + 0.14, DY0 + 0.71,
                    color=d.P.primary, weight=1.4)
        cx += bw + 0.16
    d.label(X0 + 0.14, DY0 + 1.04, W - 0.28,
            0.22, "※ 複数プロセスにまたがる場合は join(transactionId) / resume(transactionId) で参加・再開する",
            size=8, align="START", valign="TOP", color=d.P.muted)

    # 操作一覧
    rows = [["Get", "主キーで単一レコードを取得", "－"],
            ["Scan", "クラスタリングキー範囲・順序指定・クロスパーティション", "－"],
            ["Insert", "新規追加。既存レコードがあれば失敗", "既存なし"],
            ["Update", "既存レコードのみ更新", "既存あり"],
            ["Upsert", "なければ挿入、あれば更新", "問わない"],
            ["Delete", "削除（暗黙の事前読み込みあり）", "－"],
            ["Put", "非推奨（3.13 以降）。Insert / Update / Upsert に置き換える", "－"]]

    def cc(i, j, cell):
        if i == 6:
            return (lighten(d.P.danger, 0.90), darken(d.P.danger, 0.2))
        return None

    grid(d, X0, DY0 + 1.40, W, ["操作", "内容", "前提"], rows,
         col_w=[1.30, 6.20, 1.50], row_h=0.245, head_h=0.30, cell_colors=cc)

    foot(d, ["・トランザクション属性で設定値を操作間に引き継げる。読み取り専用は beginReadOnly() / startReadOnly() で明示する"],
         "提供: Community / Enterprise Standard / Enterprise Premium ｜ 状況: GA")


@slide("Admin API と Schema Loader でスキーマを2経路から管理できる",
       note="DDL がアトミックでないのは重要な制約です。CI/CD でスキーマを適用する場合は失敗時の手当てを設計してください。")
def s_admin(d):
    # 2経路
    d.shape(X0, DY0, 3.9, 0.40, kind="ROUND_RECTANGLE", fill=lighten(d.P.info, 0.84),
            stroke=lighten(d.P.info, 0.55), text="schema.json（宣言的にスキーマを記述）",
            size=9.5, bold=True, color=d.P.text)
    d.shape(X0 + 5.1, DY0, 3.9, 0.40, kind="ROUND_RECTANGLE", fill=lighten(d.P.primary, 0.86),
            stroke=lighten(d.P.primary, 0.6), text="アプリ / CI からプログラム的に操作",
            size=9.5, bold=True, color=d.P.text)
    d.arrow(X0 + 1.95, DY0 + 0.42, X0 + 1.95, DY0 + 0.58, color=d.P.info, weight=1.5)
    d.arrow(X0 + 7.05, DY0 + 0.42, X0 + 7.05, DY0 + 0.58, color=d.P.primary, weight=1.5)
    d.shape(X0, DY0 + 0.60, 3.9, 0.44, kind="ROUND_RECTANGLE", fill=d.P.info, stroke=None,
            text="Schema Loader（CLI）", size=9.5, bold=True, color="#FFFFFF")
    d.shape(X0 + 5.1, DY0 + 0.60, 3.9, 0.44, kind="ROUND_RECTANGLE", fill=d.P.primary,
            stroke=None, text="Admin API（DistributedTransactionAdmin）", size=9.5,
            bold=True, color="#FFFFFF")
    # Kept to the left half of the box: the arrow down to the shared row leaves
    # from the box's center and would run straight through a centered caption
    d.label(X0, DY0 + 1.08, 2.00, 0.22, "Cluster 版は Cluster 経由で適用", size=8,
            align="START", valign="TOP", color=d.P.muted)

    # 下位DB
    y = DY0 + 1.38
    d.arrow(X0 + 1.95, DY0 + 1.06, X0 + W / 2 - 0.4, y - 0.02, color=d.P.info, weight=1.3)
    d.arrow(X0 + 7.05, DY0 + 1.06, X0 + W / 2 + 0.4, y - 0.02, color=d.P.primary, weight=1.3)
    d.shape(X0 + 2.3, y, 4.4, 0.34, kind="ROUND_RECTANGLE", fill=lighten(d.P.primary, 0.88),
            stroke=lighten(d.P.primary, 0.6), text="各下位 DB の DDL に変換して反映", size=9,
            bold=True, color=d.P.text)

    # 機能一覧
    y2 = y + 0.46
    zone(d, X0, y2, W, 1.12, "Admin API でできること")
    items = ["名前空間の作成 / 削除 / 一覧", "テーブル作成", "カラム追加・削除",
             "テーブル名の変更", "カラム型の変更", "TRUNCATE",
             "既存テーブルのインポート", "セカンダリインデックス作成・削除",
             "Coordinator テーブル管理"]
    pills(d, X0 + 0.14, y2 + 0.32, W - 0.28, items, per_row=3, h=0.24, gap=0.08, size=9)

    # 注意
    d.shape(X0, y2 + 1.22, W, 0.34, kind="ROUND_RECTANGLE", fill=lighten(d.P.danger, 0.88),
            stroke=lighten(d.P.danger, 0.55),
            text="⚠ Admin API の呼び出しはアトミックではない。途中失敗で不整合が残りうる",
            size=9, bold=True, color=darken(d.P.danger, 0.25))

    foot(d, ["・宣言的な Schema Loader と手続き的な Admin API のどちらからでも同じスキーマに到達できる"],
         "提供: Community / Enterprise（Cluster Schema Loader は Enterprise Standard 以上）｜ 状況: GA")


@slide("例外の型ごとに再試行可否が決まる — ここを誤ると異常が漏れる",
       note="UnknownTransactionStatusException だけは無条件に再試行してはいけません。アプリ側で結果を確認する手段を用意してください。")
def s_exceptions(d):
    d.shape(X0 + 3.0, DY0, 3.0, 0.36, kind="ROUND_RECTANGLE", fill=d.P.primary, stroke=None,
            text="例外を受け取った", size=9.5, bold=True, color="#FFFFFF")

    groups = [
        ("そのまま再試行してよい", d.P.success,
         [("CrudConflictException", "CRUD 中の一時的な競合"),
          ("CommitConflictException", "コミット時の一時的な失敗"),
          ("TransactionException /\nTransactionNotFoundException", "開始の失敗。再試行の候補")]),
        ("状態確認が必要", d.P.danger,
         [("UnknownTransactionStatus\nException", "コミット結果が不明。\n再試行の前に状態を確認する")]),
        ("アプリのロジックを見直す", lighten(d.P.muted, 0.1),
         [("UnsatisfiedCondition\nException", "ミューテーションの条件が\n満たされなかった")]),
    ]
    gw = (W - 0.4) / 3
    for i, (nm, col, items) in enumerate(groups):
        gx = X0 + i * (gw + 0.2)
        d.arrow(X0 + W / 2, DY0 + 0.38, gx + gw / 2, DY0 + 0.60, color=lighten(col, 0.3),
                weight=1.4)
        d.shape(gx, DY0 + 0.62, gw, 0.34, kind="ROUND_RECTANGLE", fill=col, stroke=None,
                text=nm, size=9.5, bold=True, color="#FFFFFF")
        for j, (ex, desc) in enumerate(items):
            ey = DY0 + 1.04 + j * 0.78
            d.shape(gx, ey, gw, 0.78, kind="ROUND_RECTANGLE", fill=lighten(col, 0.92),
                    stroke=lighten(col, 0.6))
            d.label(gx + 0.10, ey + 0.05, gw - 0.20, 0.34, ex, size=8.5, bold=True,
                    align="START", valign="TOP", color=darken(col, 0.25), line_spacing=105)
            d.label(gx + 0.10, ey + 0.38, gw - 0.20, 0.36, desc, size=8, align="START",
                    valign="TOP", color=d.P.text, line_spacing=110)

    d.shape(X0 + gw + 0.2, DY0 + 1.90, gw, 0.98, kind="ROUND_RECTANGLE",
            fill=lighten(d.P.danger, 0.88), stroke=lighten(d.P.danger, 0.5))
    d.label(X0 + gw + 0.32, DY0 + 1.98, gw - 0.24, 0.84,
            "無条件に再試行してはいけない。\n"
            "Coordinator を含む結果を確認する手段を\nアプリ側に用意しておく。",
            size=8.5, align="START", valign="TOP", color=darken(d.P.danger, 0.25),
            line_spacing=120)

    foot(d, ["・再試行可 / 状態確認要 / ロジック修正の3分類で捉えると実装が整理できる。"
             "扱いを誤ると anomaly やデータ不整合につながる"],
         "提供: Community / Enterprise Standard / Enterprise Premium ｜ 状況: GA")


@slide("非トランザクショナル操作で単発 CRUD の負荷を外せる",
       note="参照系 API やキャッシュ的な用途に向きます。整合性が必要な処理と混在させる場合は接続を分けてください。")
def s_nontx(d):
    pw = (W - 0.4) / 2
    # 通常経路
    zone(d, X0, DY0, pw, 2.50, "transaction_manager = consensus-commit")
    flow = ["begin()", "CRUD（複数可）", "prepare / validate", "commit-state", "commit-records"]
    for i, s in enumerate(flow):
        fy = DY0 + 0.38 + i * 0.40
        d.shape(X0 + 0.30, fy, pw - 0.60, 0.32, kind="ROUND_RECTANGLE",
                fill=lighten(d.P.primary, 0.88), stroke=lighten(d.P.primary, 0.6),
                text=s, size=8.5, color=d.P.text)
        if i < len(flow) - 1:
            d.arrow(X0 + pw / 2, fy + 0.33, X0 + pw / 2, fy + 0.39, color=d.P.primary, weight=1.2)
    caption(d, X0 + 0.20, DY0 + 2.44, pw - 0.40,
            "複数操作の ACID・ロールバックが得られる", h=0.24)

    # single-crud 経路
    rx = X0 + pw + 0.4
    zone(d, rx, DY0, pw, 2.50, "transaction_manager = single-crud-operation",
         stroke=lighten(d.P.success, 0.5), fill="#F7FCF5")
    d.shape(rx + 0.30, DY0 + 0.38, pw - 0.60, 0.32, kind="ROUND_RECTANGLE",
            fill=lighten(d.P.success, 0.84), stroke=lighten(d.P.success, 0.5),
            text="単発の CRUD 1回", size=8.5, color=d.P.text)
    d.arrow(rx + pw / 2, DY0 + 0.71, rx + pw / 2, DY0 + 0.86, color=d.P.success, weight=1.4)
    d.shape(rx + 0.30, DY0 + 0.88, pw - 0.60, 0.32, kind="ROUND_RECTANGLE",
            fill=lighten(d.P.success, 0.84), stroke=lighten(d.P.success, 0.5),
            text="DB へ直接反映", size=8.5, color=d.P.text)
    for i, (t, ok) in enumerate([("begin() は使えない", False),
                                 ("複数ミューテーションを1つに\nまとめられない", False),
                                 ("レイテンシとオーバーヘッドを削減", True)]):
        iy = DY0 + 1.34 + i * 0.38
        d.shape(rx + 0.30, iy, pw - 0.60, 0.34, kind="ROUND_RECTANGLE",
                fill=lighten(d.P.success if ok else d.P.danger, 0.90),
                stroke=lighten(d.P.success if ok else d.P.danger, 0.6),
                text=("✓ " if ok else "× ") + t, size=8,
                color=darken(d.P.success if ok else d.P.danger, 0.3), line_spacing=105)
    caption(d, rx + 0.20, DY0 + 2.44, pw - 0.40,
            "単発の参照・更新が主体のワークロード向け", h=0.24)

    d.shape(X0, DY0 + 2.86, W, 0.34, kind="ROUND_RECTANGLE", fill="#F4F6F9",
            stroke=lighten(d.P.muted, 0.6),
            text="設定: scalar.db.transaction_manager=single-crud-operation（scalardb-cluster-node.properties）",
            size=8.5, color=d.P.text)

    foot(d, ["・複数操作にまたがる整合性やロールバックが不要なケースに限って使う。必要な箇所と接続を分けるのが安全"],
         "提供: Enterprise Standard / Enterprise Premium（3.14+）｜ 状況: GA")


# =====================================================================
# 3. ScalarDB Cluster
# =====================================================================

plain(layout="SECTION", title="3. ScalarDB Cluster — サーバ機能とエンタープライズ機能",
      body="クラスタリング、各種インターフェース、セキュリティ、レプリケーション、AI 連携",
      notes="商用の Cluster が提供する機能群です。")


@slide("Cluster が「同一サーバへのルーティング」問題を自動で解く",
       note="スティッキーセッションの設計・運用が不要になる点が、Core ライブラリを自前でサーバ化する場合との最大の差です。")
def s_cluster(d):
    # 課題
    zone(d, X0, DY0, W, 0.52, None, fill=lighten(d.P.warning, 0.80),
         stroke=lighten(d.P.warning, 0.5))
    d.label(X0 + 0.14, DY0 + 0.10, W - 0.28, 0.34,
            "課題：トランザクション処理はステートフル。同一トランザクションの全リクエストを同じサーバで処理する必要がある",
            size=9.5, bold=True, align="START", valign="TOP", color=darken(d.P.warning, 0.55))

    y = DY0 + 0.60
    # クライアント（縦積み）
    cw2 = 1.30
    client_ids = []
    for i in range(3):
        client_ids.append(
            d.shape(X0, y + 0.20 + i * 0.44, cw2, 0.36, kind="ROUND_RECTANGLE",
                    fill=lighten(d.P.primary, 0.86), stroke=lighten(d.P.primary, 0.6),
                    text=f"Client {i + 1}", size=8, color=d.P.text))
    d.label(X0, y + 1.56, cw2, 0.22, "どのノードでも受付", size=7.5, align="CENTER",
            valign="TOP", color=d.P.muted)

    # クラスタ
    kx = X0 + cw2 + 0.40
    kw = 5.20
    zone(d, kx, y, kw, 1.86, "ScalarDB Cluster（Kubernetes 上のみ）")
    nodes, node_ids = [], []
    for i in range(3):
        nx = kx + 0.24 + i * 1.62
        ny = y + 0.38
        node_ids.append(
            d.shape(nx, ny, 1.44, 0.66, kind="ROUND_RECTANGLE", fill=d.P.primary,
                    stroke=None, text=f"Node {i + 1}\n（全機能を保持）", size=8,
                    bold=True, color="#FFFFFF", line_spacing=105))
        nodes.append((nx, nx + 1.44, ny + 0.33))
    for cid in client_ids:
        d.link(cid, node_ids[0], color=lighten(d.P.primary, 0.35), weight=1.1)
    d.arrow(nodes[0][1] + 0.03, nodes[0][2], nodes[1][0] - 0.03, nodes[1][2],
            color=d.P.success, weight=1.6)
    d.arrow(nodes[1][1] + 0.03, nodes[1][2], nodes[2][0] - 0.03, nodes[2][2],
            color=d.P.success, weight=1.6, dashed=True)
    d.label(kx + 0.24, y + 1.10, kw - 0.48, 0.24,
            "自ノードで処理すべきか判定 → コンシステントハッシングで担当ノードへ転送",
            size=8, bold=True, align="CENTER", valign="TOP", color=darken(d.P.success, 0.4))
    d.label(kx + 0.24, y + 1.34, kw - 0.48, 0.44,
            "異なるトランザクションはクラスタ全体に分散するため、負荷分散も同時に成立する",
            size=8, align="CENTER", valign="TOP", color=d.P.text, line_spacing=115)

    # DB（右）
    dx = kx + kw + 0.40
    dw = XE - dx
    for i, nm in enumerate(["MySQL", "Cassandra", "DynamoDB"]):
        did = d.shape(dx, y + 0.20 + i * 0.44, dw, 0.36, kind="ROUND_RECTANGLE",
                      fill="#FFFFFF", stroke=lighten(d.P.muted, 0.35), text=nm,
                      size=8, color=d.P.text)
        d.link(node_ids[2], did, color=lighten(d.P.primary, 0.4), weight=1.1)
    d.label(dx, y + 1.56, dw, 0.22, "下位 DB 群", size=7.5, align="CENTER", valign="TOP",
            color=d.P.muted)

    # 下段: メンバーシップと効果（全幅の2カード）
    y2 = y + 1.94
    hw = (W - 0.3) / 2
    zone(d, X0, y2, hw, 0.92, "メンバーシップ管理")
    d.label(X0 + 0.14, y2 + 0.32, hw - 0.28, 0.56,
            "Kubernetes API からメンバー情報を取得し、ノードの参加・離脱に自動追従する。"
            "クラスタ構成の変更が自動反映される。",
            size=8.5, align="START", valign="TOP", color=d.P.text, line_spacing=125)
    zone(d, X0 + hw + 0.3, y2, hw, 0.92, "得られること")
    d.label(X0 + hw + 0.44, y2 + 0.32, hw - 0.28, 0.56,
            "・自動フェイルオーバー　・動的なスケーリング\n"
            "・セッションアフィニティや双方向 gRPC の作り込みが不要",
            size=8.5, align="START", valign="TOP", color=d.P.text, line_spacing=125)

    foot(d, ["・従来は同一サーバへ寄せるための作り込みが必要だった部分を、クラスタ側が引き受ける"],
         "提供: Enterprise Standard / Enterprise Premium ｜ 状況: GA")


@slide("スタンドアロンモードで単一コンテナの検証環境を作れる",
       note="Getting Started の多くはスタンドアロンモードを前提にしています。まずここから触るのが最短です。")
def s_standalone(d):
    pw = (W - 0.5) / 2
    # スタンドアロン
    zone(d, X0, DY0, pw, 2.55, "スタンドアロンモード（開発・検証）")
    d.shape(X0 + 0.45, DY0 + 0.40, pw - 0.90, 1.35, kind="ROUND_RECTANGLE",
            fill=lighten(d.P.primary, 0.92), stroke=lighten(d.P.primary, 0.6))
    d.label(X0 + 0.55, DY0 + 0.48, pw - 1.10, 0.24, "1 コンテナ", size=9, bold=True,
            align="CENTER", color=d.P.primaryDark)
    d.shape(X0 + 0.70, DY0 + 0.78, pw - 1.40, 0.86, kind="ROUND_RECTANGLE",
            fill=d.P.primary, stroke=None, text="Cluster ノード × 1\nSQL / 認証認可も利用可",
            size=8.5, bold=True, color="#FFFFFF", line_spacing=110)
    for i, t in enumerate(["Kubernetes の準備が不要", "ローカル開発 / CI の結合テスト",
                           "PoC 初期の機能検証"]):
        d.shape(X0 + 0.30, DY0 + 1.80 + i * 0.29, pw - 0.60, 0.26, kind="ROUND_RECTANGLE",
                fill=lighten(d.P.success, 0.86), stroke=None, text="✓ " + t, size=8,
                color=darken(d.P.success, 0.45))

    # 本番
    rx = X0 + pw + 0.5
    zone(d, rx, DY0, pw, 2.55, "本番（Kubernetes + Helm チャート）")
    d.shape(rx + 0.30, DY0 + 0.40, pw - 0.60, 1.35, kind="ROUND_RECTANGLE",
            fill=lighten(d.P.info, 0.92), stroke=lighten(d.P.info, 0.6))
    d.label(rx + 0.40, DY0 + 0.48, pw - 0.80, 0.24, "Kubernetes クラスタ", size=9,
            bold=True, align="CENTER", color=darken(d.P.info, 0.35))
    for i in range(3):
        d.shape(rx + 0.48 + i * 1.14, DY0 + 0.80, 1.02, 0.82, kind="ROUND_RECTANGLE",
                fill=d.P.primary, stroke=None, text=f"Node {i + 1}", size=8.5, bold=True,
                color="#FFFFFF")
    for i, t in enumerate(["冗長性と自動フェイルオーバー", "動的なスケールアウト",
                           "TLS・監視・バックアップ運用"]):
        d.shape(rx + 0.30, DY0 + 1.80 + i * 0.29, pw - 0.60, 0.26, kind="ROUND_RECTANGLE",
                fill=lighten(d.P.info, 0.86), stroke=None, text="✓ " + t, size=8,
                color=darken(d.P.info, 0.35))

    d.arrow_shape(X0 + pw + 0.02, DY0 + 1.00, 0.46, 0.46, fill=lighten(d.P.primary, 0.7))

    d.shape(X0, DY0 + 2.76, W, 0.40, kind="ROUND_RECTANGLE", fill=lighten(d.P.warning, 0.76),
            stroke=None,
            text="スタンドアロンでは冗長性・自動フェイルオーバーは得られない。本番はあくまで Kubernetes デプロイが前提",
            size=9, bold=True, color=darken(d.P.warning, 0.55))

    foot(d, ["・機能の確認はスタンドアロン、非機能の確認は Kubernetes 構成、と役割を分けて検証を進めると早い"],
         "提供: Enterprise Standard / Enterprise Premium ｜ 状況: GA")


@slide("マイクロサービスは共有クラスタ型を第一候補にする",
       note="2PC は仕組みを理解せずに使うと anomaly を招きます。まず共有クラスタ型で成立しないかを検討してください。")
def s_microservices(d):
    pw = (W - 0.5) / 2
    # 共有クラスタ型
    zone(d, X0, DY0, pw, 2.42, "共有クラスタ型（1フェーズコミット）★推奨",
         stroke=lighten(d.P.success, 0.5), fill="#F7FCF5")
    sw = (pw - 0.60) / 3
    for i in range(3):
        d.shape(X0 + 0.30 + i * (sw + 0.0), DY0 + 0.36, sw - 0.06, 0.42,
                kind="ROUND_RECTANGLE", fill=lighten(d.P.success, 0.84),
                stroke=lighten(d.P.success, 0.5), text=f"Service {i + 1}", size=8,
                color=d.P.text)
        d.arrow(X0 + 0.30 + i * sw + (sw - 0.06) / 2, DY0 + 0.79,
                X0 + pw / 2, DY0 + 0.98, color=d.P.success, weight=1.3)
    d.shape(X0 + 0.30, DY0 + 1.00, pw - 0.60, 0.44, kind="ROUND_RECTANGLE",
            fill=d.P.success, stroke=None, text="ScalarDB Cluster（1 つ）", size=9.5,
            bold=True, color="#FFFFFF")
    d.label(X0 + 0.30, DY0 + 1.50, pw - 0.60, 0.22, "commit を呼ぶのは1サービスのみ",
            size=8, align="CENTER", color=darken(d.P.success, 0.45))
    for i, t in enumerate(["リソース消費が小さい", "エラーハンドリングが単純"]):
        d.shape(X0 + 0.30, DY0 + 1.76 + i * 0.28, pw - 0.60, 0.24, kind="ROUND_RECTANGLE",
                fill=lighten(d.P.success, 0.88), stroke=None, text="✓ " + t, size=8,
                color=darken(d.P.success, 0.45))

    # 分離クラスタ型
    rx = X0 + pw + 0.5
    zone(d, rx, DY0, pw, 2.42, "分離クラスタ型（2フェーズコミット）")
    for i in range(3):
        cx = rx + 0.30 + i * sw
        d.shape(cx, DY0 + 0.36, sw - 0.06, 0.42, kind="ROUND_RECTANGLE",
                fill=lighten(d.P.primary, 0.86), stroke=lighten(d.P.primary, 0.6),
                text=f"Service {i + 1}", size=8, color=d.P.text)
        d.arrow(cx + (sw - 0.06) / 2, DY0 + 0.79, cx + (sw - 0.06) / 2, DY0 + 0.96,
                color=d.P.primary, weight=1.3)
        d.shape(cx, DY0 + 0.98, sw - 0.06, 0.46, kind="ROUND_RECTANGLE",
                fill=d.P.primary, stroke=None, text=f"Cluster {i + 1}", size=8,
                bold=True, color="#FFFFFF")
    d.shape(rx + 0.30, DY0 + 1.50, pw - 0.60, 0.24, kind="ROUND_RECTANGLE",
            fill=lighten(d.P.primary, 0.82), stroke=None,
            text="全サービスが prepare → 成功なら commit", size=8, bold=True,
            color=d.P.primaryDark)
    for i, (t, ok) in enumerate([("サービスごとの分離と管理責任の分散", True),
                                 ("トランザクションとエラー処理が複雑", False)]):
        d.shape(rx + 0.30, DY0 + 1.78 + i * 0.28, pw - 0.60, 0.24, kind="ROUND_RECTANGLE",
                fill=lighten(d.P.success if ok else d.P.danger, 0.88), stroke=None,
                text=("✓ " if ok else "△ ") + t, size=8,
                color=darken(d.P.success if ok else d.P.danger, 0.4 if ok else 0.25))

    y = DY0 + 2.58
    d.shape(X0, y, W, 0.52, kind="ROUND_RECTANGLE", fill=lighten(d.P.success, 0.86),
            stroke=lighten(d.P.success, 0.5))
    d.label(X0 + 0.14, y + 0.06, W - 0.28, 0.42,
            "Cluster はメモリ上に重要な状態を保持せず DB への経路として振る舞うため、共有クラスタ型でもマイクロサービスの原則は損なわれない\n"
            "※ Coordinator テーブルはどちらのパターンでも必要。Spring Data JDBC は分離クラスタ型（2PC）のみ対応",
            size=8.5, align="START", valign="TOP", color=darken(d.P.success, 0.45),
            line_spacing=120)

    foot(d, ["・2PC の挙動を完全に理解している場合に限り分離クラスタ型を選ぶ。誤用は DB の anomaly につながる"],
         "提供: Enterprise Standard / Enterprise Premium ｜ 状況: GA")


@slide("SQL インターフェースで既存の Java / .NET 資産を活かせる",
       note="SQL インターフェースは Enterprise Premium 限定です。JDBC 経由で BI ツールや既存 ORM を繋げられる点が実用上大きいです。")
def s_sql(d):
    clients = [("ScalarDB SQL API", "Java", d.P.primary),
               ("JDBC ドライバ", "既存 JDBC 資産・BI ツール", d.P.primary),
               ("Spring Data JDBC", "Spring アプリ（2PC のみ）", d.P.info),
               ("LINQ / SQL", ".NET（1PC / 2PC）", d.P.info),
               ("SQL gRPC API", "低レベル統合", lighten(d.P.muted, 0.15))]
    cw = (W - 0.16 * 4) / 5
    for i, (nm, sub, col) in enumerate(clients):
        cx = X0 + i * (cw + 0.16)
        d.shape(cx, DY0, cw, 0.68, kind="ROUND_RECTANGLE", fill=lighten(col, 0.90),
                stroke=lighten(col, 0.6))
        d.label(cx + 0.06, DY0 + 0.08, cw - 0.12, 0.24, nm, size=8.5, bold=True,
                align="CENTER", color=darken(col, 0.25))
        d.label(cx + 0.06, DY0 + 0.32, cw - 0.12, 0.32, sub, size=7.5, align="CENTER",
                color=d.P.text, line_spacing=105)
        d.arrow(cx + cw / 2, DY0 + 0.70, X0 + W / 2, DY0 + 0.92, color=lighten(col, 0.3),
                weight=1.2)

    d.shape(X0 + 1.2, DY0 + 0.94, W - 2.4, 0.46, kind="ROUND_RECTANGLE", fill=d.P.primary,
            stroke=None, text="ScalarDB Cluster SQL", size=10, bold=True, color="#FFFFFF")
    d.arrow(X0 + W / 2, DY0 + 1.42, X0 + W / 2, DY0 + 1.58, color=d.P.primary, weight=1.5)
    d.shape(X0 + 2.4, DY0 + 1.60, 4.2, 0.38, kind="ROUND_RECTANGLE",
            fill=lighten(d.P.primary, 0.88), stroke=lighten(d.P.primary, 0.6),
            text="Consensus Commit → 複数 DB", size=9, bold=True, color=d.P.text)

    # 周辺ツール
    y = DY0 + 2.14
    zone(d, X0, y, W, 1.10, "スキーマ・データ操作の周辺ツール")
    tools = [("SQL CLI", "スキーマ作成・対話的な SQL 実行"),
             ("Schema Loader", "既存テーブルを ScalarDB のモデルに取り込む"),
             ("Data Loader", "データのインポート / エクスポート")]
    tw = (W - 0.28 - 0.16 * 2) / 3
    for i, (nm, sub) in enumerate(tools):
        tx = X0 + 0.14 + i * (tw + 0.16)
        d.shape(tx, y + 0.34, tw, 0.62, kind="ROUND_RECTANGLE",
                fill=lighten(d.P.primary, 0.92), stroke=lighten(d.P.primary, 0.65))
        d.label(tx + 0.08, y + 0.40, tw - 0.16, 0.22, nm, size=9, bold=True,
                align="CENTER", color=d.P.primaryDark)
        d.label(tx + 0.08, y + 0.62, tw - 0.16, 0.32, sub, size=7.5, align="CENTER",
                color=d.P.text, line_spacing=105)

    foot(d, ["・2フェーズコミットインターフェース版の一部（Java / .NET SQL）はドキュメント整備中。採用時は対応状況を確認する"],
         "提供: Enterprise Premium ｜ 状況: GA")


@slide("GraphQL はスキーマを自動生成するため定義作業が不要",
       note="スキーマ自動生成のため、テーブル追加がそのまま API 拡張になります。公開範囲は認証認可・ABAC と組み合わせて制御してください。")
def s_graphql(d):
    # スキーマ自動生成
    zone(d, X0, DY0, W, 1.52, "スキーマの自動生成")
    bw = 2.55
    d.shape(X0 + 0.25, DY0 + 0.44, bw, 0.80, kind="ROUND_RECTANGLE",
            fill=lighten(d.P.primary, 0.90), stroke=lighten(d.P.primary, 0.62),
            text="ScalarDB スキーマ\n（名前空間 / テーブル / カラム）", size=8.5,
            color=d.P.text, line_spacing=115)
    d.arrow_shape(X0 + 0.25 + bw + 0.14, DY0 + 0.60, 1.05, 0.46,
                  fill=lighten(d.P.success, 0.62), text="自動生成", size=8,
                  color=darken(d.P.success, 0.45))
    d.shape(X0 + 0.25 + bw + 1.33, DY0 + 0.44, bw, 0.80, kind="ROUND_RECTANGLE",
            fill=d.P.success, stroke=None,
            text="GraphQL スキーマ\n（Query / Mutation）", size=8.5, bold=True,
            color="#FFFFFF", line_spacing=115)
    d.label(X0 + 0.25 + 2 * bw + 1.50, DY0 + 0.50, 1.95, 0.70,
            "手動でのスキーマ定義が\n不要になる。\nテーブル追加＝API 拡張。",
            size=8.5, align="START", valign="TOP", color=d.P.text, line_spacing=125)

    # 提供機能
    y = DY0 + 1.66
    pw = (W - 0.3) / 2
    zone(d, X0, y, pw, 1.58, "提供される操作")
    for i, t in enumerate(["CRUD 操作（Query / Mutation）",
                           "複数 DB にまたがる複雑なトランザクション",
                           "2フェーズコミットインターフェース"]):
        d.shape(X0 + 0.14, y + 0.36 + i * 0.34, pw - 0.28, 0.30, kind="ROUND_RECTANGLE",
                fill=lighten(d.P.primary, 0.90), stroke=lighten(d.P.primary, 0.62),
                text=t, size=8.5, color=d.P.text)
    d.label(X0 + 0.14, y + 1.34, pw - 0.28, 0.20,
            "2PC により複数プロセス / アプリをまたぐ実行が可能", size=7.5,
            align="START", valign="TOP", color=d.P.muted)

    rx = X0 + pw + 0.3
    zone(d, rx, y, pw, 1.58, "使いどころ")
    d.label(rx + 0.14, y + 0.36, pw - 0.28, 1.10,
            "・フロントエンドから直接データアクセス\n　させる BFF 的な構成\n"
            "・必要なフィールドだけを取得したい参照系\n"
            "・マイクロサービス間の集約エンドポイント",
            size=8.5, align="START", valign="TOP", color=d.P.text, line_spacing=135)

    foot(d, ["・公開範囲の制御は ScalarDB 側の認証認可・ABAC と組み合わせて設計する"],
         "提供: Enterprise Premium ｜ 状況: GA")


@slide("gRPC を共通の境界にして多言語から利用できる",
       note="Go / Python は生成した gRPC スタブを使う形です。.NET は専用 SDK があり機能カバレッジが最も広いです。")
def s_sdk(d):
    langs = [("Java", "Cluster Java Client SDK", "最も広い機能カバレッジ", d.P.primary),
             (".NET", "Cluster .NET Client SDK",
              "分散Tx / SQL / Admin API\nLINQ / 2PC / 認証認可", d.P.primary),
             ("Go", "gRPC 経由", "Getting Started あり", d.P.info),
             ("Python", "gRPC 経由", "Getting Started あり", d.P.info),
             ("Kotlin", "Core ライブラリ", "Getting Started あり", lighten(d.P.muted, 0.1))]
    cw = (W - 0.16 * 4) / 5
    for i, (nm, sdk, sub, col) in enumerate(langs):
        cx = X0 + i * (cw + 0.16)
        d.shape(cx, DY0, cw, 0.98, kind="ROUND_RECTANGLE", fill=lighten(col, 0.90),
                stroke=lighten(col, 0.6))
        d.shape(cx, DY0, cw, 0.30, kind="RECTANGLE", fill=col, stroke=None,
                text=nm, size=9.5, bold=True, color="#FFFFFF")
        d.label(cx + 0.06, DY0 + 0.34, cw - 0.12, 0.22, sdk, size=8, bold=True,
                align="CENTER", color=darken(col, 0.25))
        d.label(cx + 0.06, DY0 + 0.56, cw - 0.12, 0.38, sub, size=7, align="CENTER",
                color=d.P.text, line_spacing=105)
        d.arrow(cx + cw / 2, DY0 + 1.00, X0 + W / 2, DY0 + 1.26, color=lighten(col, 0.3),
                weight=1.2)

    d.shape(X0 + 1.6, DY0 + 1.28, W - 3.2, 0.44, kind="ROUND_RECTANGLE", fill=d.P.primaryDark,
            stroke=None, text="gRPC（CRUD 用 API / SQL 用 API の2系統）", size=10,
            bold=True, color="#FFFFFF")
    d.arrow(X0 + W / 2, DY0 + 1.74, X0 + W / 2, DY0 + 1.90, color=d.P.primary, weight=1.5)
    d.shape(X0 + 2.2, DY0 + 1.92, 4.6, 0.44, kind="ROUND_RECTANGLE", fill=d.P.primary,
            stroke=None, text="ScalarDB Cluster", size=10, bold=True, color="#FFFFFF")

    y = DY0 + 2.52
    zone(d, X0, y, W, 0.78, "この構成の意味")
    d.label(X0 + 0.14, y + 0.32, W - 0.28, 0.40,
            "言語ごとにトランザクション実装を持たず、gRPC を共通の境界に置いている。"
            "そのため新しい言語への対応コストが小さく、挙動も言語間で揃う。",
            size=9, align="START", valign="TOP", color=d.P.text, line_spacing=120)

    foot(d, ["・言語を横断しても Consensus Commit の挙動は同一。クライアント側の実装差が正しさに影響しない"],
         "提供: Enterprise Standard / Enterprise Premium ｜ 状況: GA")


@slide("認証・認可を Cluster に置き DB ごとの権限設計から解放する",
       note="INSERT に SELECT 権限が必要な点は運用でつまずきやすいポイントです。権限設計時に明示的に含めてください。")
def s_auth(d):
    # ユーザーとロール
    lw = 4.30
    zone(d, X0, DY0, lw, 2.24, "ユーザーとロール（RBAC）")
    d.shape(X0 + 0.20, DY0 + 0.36, lw - 0.40, 0.36, kind="ROUND_RECTANGLE",
            fill=d.P.primaryDark, stroke=None, text="スーパーユーザー（全権限）", size=9,
            bold=True, color="#FFFFFF")
    d.label(X0 + 0.20, DY0 + 0.74, lw - 0.40, 0.20,
            "初期管理者は admin / admin。ユーザーと名前空間の管理はここだけ", size=7.5,
            align="CENTER", color=d.P.muted)
    d.arrow(X0 + lw / 2, DY0 + 0.96, X0 + lw / 2, DY0 + 1.10, color=d.P.primary, weight=1.4)
    d.shape(X0 + 0.20, DY0 + 1.12, (lw - 0.50) / 2, 0.36, kind="ROUND_RECTANGLE",
            fill=d.P.primary, stroke=None, text="ロール", size=9, bold=True, color="#FFFFFF")
    d.shape(X0 + 0.30 + (lw - 0.50) / 2, DY0 + 1.12, (lw - 0.50) / 2, 0.36,
            kind="ROUND_RECTANGLE", fill=lighten(d.P.primary, 0.40), stroke=None,
            text="通常ユーザー（初期は権限なし）", size=8, bold=True, color="#FFFFFF")
    d.arrow(X0 + 0.20 + (lw - 0.50) / 4, DY0 + 1.50, X0 + 0.20 + (lw - 0.50) / 4,
            DY0 + 1.62, color=d.P.primary, weight=1.3)
    d.label(X0 + 0.20, DY0 + 1.62, lw - 0.40, 0.52,
            "・ロールで権限を束ね、ユーザーや別ロールに付与（階層化可能）\n"
            "・WITH ADMIN OPTION で付与された側が再付与できる",
            size=8, align="START", valign="TOP", color=d.P.text, line_spacing=120)

    # 権限
    rx = X0 + lw + 0.30
    rw = XE - rx
    zone(d, rx, DY0, rw, 2.24, "9種の権限（テーブル / 名前空間単位）")
    for i, (grp, items, col) in enumerate([
            ("参照", ["SELECT"], d.P.info),
            ("更新", ["INSERT", "UPDATE", "DELETE"], d.P.primary),
            ("スキーマ", ["CREATE", "DROP", "ALTER", "TRUNCATE"], lighten(d.P.muted, 0.1)),
            ("権限管理", ["GRANT"], d.P.success)]):
        iy = DY0 + 0.34 + i * 0.38
        d.label(rx + 0.14, iy + 0.03, 0.80, 0.24, grp, size=8.5, bold=True,
                align="START", color=d.P.text)
        ipw = (rw - 1.10 - 0.08 * 3) / 4
        for j, it in enumerate(items):
            # 4 つ並ぶ行はチップが狭いので文字を落として単語の分断を防ぐ
            pill(d, rx + 0.96 + j * (ipw + 0.08), iy, ipw, 0.28, it,
                 fill=lighten(col, 0.82), color=darken(col, 0.3),
                 size=8 if len(items) <= 3 else 7)
    d.shape(rx + 0.14, DY0 + 2.08 - 0.26, rw - 0.28, 0.32, kind="ROUND_RECTANGLE",
            fill=lighten(d.P.warning, 0.72), stroke=None,
            text="⚠ INSERT / UPDATE / UPSERT はいずれも SELECT 権限も必要（put 由来の設計経緯）",
            size=8, bold=True, color=darken(d.P.warning, 0.55))

    y = DY0 + 2.40
    d.shape(X0, y, W, 0.44, kind="ROUND_RECTANGLE", fill=lighten(d.P.primary, 0.90),
            stroke=lighten(d.P.primary, 0.62))
    d.label(X0 + 0.14, y + 0.05, W - 0.28, 0.36,
            "認証方式：USERPASS（既定）／ OIDC ベースの JWT　　"
            "設定：scalar.db.cluster.auth.enabled=true（トークン有効期限・キャッシュ・pepper も設定可）",
            size=8.5, align="START", valign="TOP", color=d.P.text)

    foot(d, ["・各 DB のネイティブ権限機能を個別に設計せず、Cluster に集約できるのが実運用上の利点"],
         "提供: Enterprise Standard / Enterprise Premium ｜ 状況: GA")


@slide("OIDC ベース JWT でパスワードを配らずに認証できる",
       note="既存の IdP に認証を寄せられるため、パスワードローテーションの運用負荷が下がります。クレーム選定はセキュリティ上の要点です。")
def s_oidc(d):
    # シーケンス
    lanes = [("クライアント\nアプリ", lighten(d.P.primary, 0.45)),
             ("OIDC プロバイダ\n（例: Keycloak）", d.P.info),
             ("ScalarDB\nCluster", d.P.primary)]
    lw = 1.55
    ly = DY0
    for i, (nm, col) in enumerate(lanes):
        lx = X0 + i * ((W - lw) / 2)
        d.shape(lx, ly, lw, 0.52, kind="ROUND_RECTANGLE", fill=col, stroke=None,
                text=nm, size=8.5, bold=True, color="#FFFFFF", line_spacing=105)

    steps = [
        ("① JWT を取得", 0, 1, d.P.info),
        ("② JWT を付けてリクエスト", 0, 2, d.P.primary),
    ]
    y = ly + 0.66
    for i, (t, a, b, col) in enumerate(steps):
        sy = y + i * 0.34
        x1 = X0 + a * ((W - lw) / 2) + lw / 2
        x2 = X0 + b * ((W - lw) / 2) + lw / 2
        d.arrow(x1, sy + 0.16, x2, sy + 0.16, color=col, weight=1.5,
                free=True)      # レーン間の通信線（シーケンス図の書式）
        d.label(min(x1, x2), sy - 0.06, abs(x2 - x1), 0.22, t, size=8, bold=True,
                align="CENTER", color=darken(col, 0.3))

    # Cluster 側の検証
    y2 = y + 0.74
    zone(d, X0, y2, W, 1.42, "ScalarDB Cluster 側の検証（RFC 9068 準拠）")
    vs = [("① メタデータ取得", "issuer の\n.well-known/openid-configuration"),
          ("② JWKS 取得", "署名検証用の鍵セットを\n取得してキャッシュ"),
          ("③ トークン検証", "署名・有効期限・\n標準クレームを検証"),
          ("④ ユーザー突合", "指定クレームから username を\n取り出し ScalarDB ユーザーと照合")]
    vw = (W - 0.28 - 0.14 * 3) / 4
    for i, (nm, sub) in enumerate(vs):
        vx = X0 + 0.14 + i * (vw + 0.14)
        d.shape(vx, y2 + 0.34, vw, 0.90, kind="ROUND_RECTANGLE",
                fill=lighten(d.P.primary, 0.92), stroke=lighten(d.P.primary, 0.65))
        d.label(vx + 0.06, y2 + 0.40, vw - 0.12, 0.24, nm, size=8.5, bold=True,
                align="CENTER", color=d.P.primaryDark)
        d.label(vx + 0.06, y2 + 0.64, vw - 0.12, 0.56, sub, size=7.5, align="CENTER",
                color=d.P.text, line_spacing=110)
        if i < 3:
            d.arrow(vx + vw + 0.02, y2 + 0.79, vx + vw + 0.12, y2 + 0.79,
                    color=d.P.primary, weight=1.3)

    y3 = y2 + 1.54
    d.shape(X0, y3, 5.35, 0.34, kind="ROUND_RECTANGLE", fill="#F4F6F9",
            stroke=lighten(d.P.muted, 0.6),
            text="trusted_issuers / username.claim_name / audience.name",
            size=8, color=d.P.text)
    d.shape(X0 + 5.50, y3, W - 5.50, 0.34, kind="ROUND_RECTANGLE",
            fill=lighten(d.P.danger, 0.88), stroke=None,
            text="⚠ username クレームの選定を誤ると共有事故", size=8, bold=True,
            color=darken(d.P.danger, 0.25))

    foot(d, ["・クライアント側は認証方式を oidc_jwt にして JWT を渡すだけ。ScalarDB のパスワードを持たせる必要がない"],
         "提供: Enterprise Standard / Enterprise Premium ｜ 状況: GA（3.18）")


@slide("ABAC はテーブル単位でなくレコード単位の認可を実現する",
       note="Private Preview かつ提供地域の制約があります。採用前に提供条件を確認してください。")
def s_abac(d):
    # タグ照合のマトリクス
    lw = 5.30
    zone(d, X0, DY0, lw, 2.62, "タグの一致でレコード単位に可視・不可視が決まる")
    users = ["User A\nタグ: 機密", "User B\nタグ: 一般"]
    recs = ["Record 1\nタグ: 機密", "Record 2\nタグ: 一般", "Record 3\nタグ: 機密"]
    ux, cw = X0 + 0.20, 1.20
    d.label(ux, DY0 + 0.36, 1.30, 0.22, "ユーザー", size=8, bold=True, align="START",
            color=d.P.muted)
    for j, r in enumerate(recs):
        d.shape(ux + 1.34 + j * cw, DY0 + 0.32, cw - 0.08, 0.44, kind="ROUND_RECTANGLE",
                fill=lighten(d.P.info, 0.86), stroke=None, text=r, size=7.5,
                color=darken(d.P.info, 0.35), line_spacing=100)
    matches = [[True, False, True], [False, True, False]]
    for i, u in enumerate(users):
        uy = DY0 + 0.86 + i * 0.62
        d.shape(ux, uy, 1.26, 0.52, kind="ROUND_RECTANGLE", fill=lighten(d.P.primary, 0.86),
                stroke=None, text=u, size=7.5, color=d.P.primaryDark, line_spacing=100)
        for j in range(3):
            ok = matches[i][j]
            d.shape(ux + 1.34 + j * cw, uy, cw - 0.08, 0.52, kind="ROUND_RECTANGLE",
                    fill=lighten(d.P.success if ok else d.P.danger, 0.84), stroke=None,
                    text="✓ 参照可" if ok else "× 不可視", size=8, bold=True,
                    color=darken(d.P.success if ok else d.P.danger, 0.4 if ok else 0.25))
    d.label(X0 + 0.20, DY0 + 2.18, lw - 0.40, 0.36,
            "ユーザーとレコードの両方にタグ（複数の構成要素を持つ属性）を付与し、\n属性が一致した場合のみアクセスを許す",
            size=8, align="START", valign="TOP", color=d.P.text, line_spacing=120)

    # 利点・用途
    rx = X0 + lw + 0.30
    rw = XE - rx
    zone(d, rx, DY0, rw, 1.26, "利点")
    d.label(rx + 0.14, DY0 + 0.34, rw - 0.28, 0.84,
            "・複数 DB に対して一度設定すれば済む\n"
            "・行レベルセキュリティのような\n　ストアドプロシージャ実装が不要",
            size=8.5, align="START", valign="TOP", color=d.P.text, line_spacing=130)
    zone(d, rx, DY0 + 1.38, rw, 1.24, "ユースケース")
    d.label(rx + 0.14, DY0 + 1.72, rw - 0.28, 0.82,
            "・機微なレコードを権限者のみに限定\n"
            "・マルチテナントで同一テーブルを共有し\n　権限に応じて可視範囲を分ける",
            size=8.5, align="START", valign="TOP", color=d.P.text, line_spacing=130)

    y = DY0 + 2.76
    d.shape(X0, y, W, 0.34, kind="ROUND_RECTANGLE", fill=lighten(d.P.warning, 0.74),
            stroke=None,
            text="⚠ 現時点で日本国内のお客様限定、かつ Private Preview（Enterprise Premium Option）",
            size=9, bold=True, color=darken(d.P.warning, 0.55))

    foot(d, ["・タグの定義と付与だけで済むためコーディングが不要。ただし本番採用は提供条件の確認が前提"],
         "提供: Enterprise Premium Option（3.15+）｜ 状況: Private Preview")


@slide("保存データ暗号化はカラム単位で、アプリから透過的に働く",
       note="WHERE 句に使えない制約があるため、暗号化対象カラムはスキーマ設計段階で決める必要があります。")
def s_encrypt(d):
    # テーブル図
    zone(d, X0, DY0, W, 1.30, "カラムレベル暗号化（アプリの変更は不要）")
    cols = [("user_id\n（主キー）", 1.55, False, "暗号化不可"),
            ("email\n（インデックス）", 1.70, False, "暗号化不可"),
            ("name", 1.35, True, "暗号化可"),
            ("card_no", 1.35, True, "暗号化可"),
            ("memo", 1.35, True, "暗号化可")]
    cx = X0 + 0.20
    for nm, cw, enc, tag in cols:
        col = d.P.success if enc else lighten(d.P.muted, 0.25)
        d.shape(cx, DY0 + 0.36, cw, 0.48, kind="RECTANGLE",
                fill=lighten(col, 0.86) if enc else "#F2F4F7",
                stroke=lighten(col, 0.5), stroke_weight=0.9,
                text=nm, size=8, color=d.P.text, line_spacing=100)
        d.shape(cx, DY0 + 0.86, cw, 0.24, kind="RECTANGLE",
                fill=col if enc else lighten(d.P.muted, 0.6), stroke=None,
                text=("🔒 " if enc else "") + tag, size=7.5, bold=True,
                color="#FFFFFF" if enc else d.P.text)
        cx += cw + 0.08

    # 鍵管理2方式
    y = DY0 + 1.44
    pw = (W - 0.3) / 2
    zone(d, X0, y, pw, 1.36, "① HashiCorp Vault Encryption")
    d.label(X0 + 0.14, y + 0.34, pw - 0.28, 0.94,
            "・transit secrets engine に暗号処理を委譲\n"
            "・鍵種別: aes128-gcm96 / aes256-gcm96 /\n　chacha20-poly1305\n"
            "・認証は現時点で token 方式のみ",
            size=8.5, align="START", valign="TOP", color=d.P.text, line_spacing=125)
    rx = X0 + pw + 0.3
    zone(d, rx, y, pw, 1.36, "② Self-Encryption")
    d.label(rx + 0.14, y + 0.34, pw - 0.28, 0.94,
            "・ScalarDB が DEK を生成・管理\n"
            "・DEK は Kubernetes Secret に保存\n"
            "・テーブル作成時に1テーブル1鍵\n"
            "・DEK はキャッシュ（既定 60 秒で失効）",
            size=8.5, align="START", valign="TOP", color=d.P.text, line_spacing=125)

    # 制約
    y2 = y + 1.50
    d.shape(X0, y2, W, 0.50, kind="ROUND_RECTANGLE", fill=lighten(d.P.danger, 0.88),
            stroke=lighten(d.P.danger, 0.5))
    d.label(X0 + 0.14, y2 + 0.05, W - 0.28, 0.42,
            "制約：主キー列とセカンダリインデックス列は暗号化できない　／　"
            "暗号化した列は WHERE 句・ORDER BY 句に使えない\n"
            "設定：scalar.db.cluster.encryption.enabled=true"
            "（テーブル削除時に DEK を消すオプションは既定で無効）",
            size=8.5, align="START", valign="TOP", color=darken(d.P.danger, 0.25),
            line_spacing=120)

    foot(d, ["・暗号化対象を後から増やすと検索条件の設計に影響する。スキーマ設計の段階で対象カラムを確定させる"],
         "提供: Enterprise Premium（3.14+）｜ 状況: GA")


@slide("通信暗号化はクライアント間・ノード間の両方を保護する",
       note="ノード間通信も暗号化対象です。Analytics で認証を有効化する場合は TLS が必須になります。")
def s_tls(d):
    # 3チャネル
    y = DY0 + 0.20
    d.shape(X0, y, 2.10, 0.56, kind="ROUND_RECTANGLE", fill=lighten(d.P.primary, 0.86),
            stroke=lighten(d.P.primary, 0.6), text="クライアント", size=9.5, bold=True,
            color=d.P.text)
    kx, kw = X0 + 3.00, 3.40
    zone(d, kx, y - 0.30, kw, 1.60, "ScalarDB Cluster")
    for i in range(2):
        d.shape(kx + 0.30 + i * 1.60, y + 0.10, 1.20, 0.56, kind="ROUND_RECTANGLE",
                fill=d.P.primary, stroke=None, text=f"Node {i + 1}", size=9, bold=True,
                color="#FFFFFF")
    d.shape(XE - 2.10, y, 2.10, 0.56, kind="ROUND_RECTANGLE", fill="#FFFFFF",
            stroke=d.P.muted, text="下位 DB", size=9.5, bold=True, color=d.P.text)

    # チャネル①
    d.arrow(X0 + 2.12, y + 0.28, kx + 0.28, y + 0.38, color=d.P.success, weight=2.0,
            start_arrow="FILL_ARROW")
    d.shape(X0 + 2.05, y - 0.34, 1.05, 0.26, kind="ROUND_RECTANGLE", fill=d.P.success,
            stroke=None, text="① TLS", size=8, bold=True, color="#FFFFFF")
    # チャネル②
    d.arrow(kx + 1.52, y + 0.38, kx + 1.88, y + 0.38, color=d.P.success, weight=2.0,
            start_arrow="FILL_ARROW")
    d.shape(kx + 1.20, y + 0.74, 1.00, 0.26, kind="ROUND_RECTANGLE", fill=d.P.success,
            stroke=None, text="② TLS", size=8, bold=True, color="#FFFFFF")
    # チャネル③
    d.arrow(kx + kw + 0.02, y + 0.38, XE - 2.12, y + 0.28, color=lighten(d.P.warning, 0.2),
            weight=2.0, start_arrow="FILL_ARROW")
    d.shape(kx + kw + 0.05, y - 0.34, 1.45, 0.26, kind="ROUND_RECTANGLE",
            fill=lighten(d.P.warning, 0.35), stroke=None, text="③ DB 側で個別設定", size=8,
            bold=True, color=darken(d.P.warning, 0.6))

    # 説明
    y2 = DY0 + 1.60
    rows = [["① クライアント ↔ Cluster ノード", "ScalarDB の TLS 設定", "対応"],
            ["② Cluster ノード ↔ ノード（内部通信）", "ScalarDB の TLS 設定", "対応"],
            ["③ Cluster ノード ↔ 下位 DB", "DB 側で個別に設定", "本番では強く推奨"]]

    def cc(i, j, cell):
        if j == 2:
            return ((lighten(d.P.success, 0.82), darken(d.P.success, 0.45)) if cell == "対応"
                    else (lighten(d.P.warning, 0.70), darken(d.P.warning, 0.55)))
        return None

    grid(d, X0, y2, W, ["対象チャネル", "設定箇所", "ScalarDB の対応"], rows,
         col_w=[4.30, 2.60, 2.10], row_h=0.30, cell_colors=cc)

    y3 = y2 + 0.32 + 3 * 0.30 + 0.04
    d.shape(X0, y3, W, 0.60, kind="ROUND_RECTANGLE", fill="#F4F6F9",
            stroke=lighten(d.P.muted, 0.6))
    d.label(X0 + 0.14, y3 + 0.03, W - 0.28, 0.55,
            "設定：scalar.db.cluster.tls.enabled=true をサーバ・クライアントの双方に設定\n"
            "必要な資材：CA ルート証明書（PEM またはファイルパス）／証明書チェーン／秘密鍵",
            size=8.5, align="START", valign="TOP", color=d.P.text, line_spacing=120)

    foot(d, ["・クライアント側にも同じ設定が必要。片側だけ有効化しても接続は成立しない。"
             "PEM データとファイルパスの両方を指定した場合は PEM が優先。Helm は cert-manager 手順も提供"],
         "提供: Enterprise Standard / Enterprise Premium ｜ 状況: GA")


@slide("リモートレプリケーションが RPO=0 の DR サイトを構成する",
       note="同期・非同期のハイブリッド方式で RPO=0 を実現します。DDL が複製されないため、スキーマ変更の運用手順が必要です。")
def s_replication(d):
    pw = 3.30
    # プライマリ
    zone(d, X0, DY0, pw, 2.30, "プライマリサイト")
    d.shape(X0 + 0.20, DY0 + 0.36, pw - 0.40, 0.34, kind="ROUND_RECTANGLE",
            fill=lighten(d.P.primary, 0.86), stroke=lighten(d.P.primary, 0.6),
            text="クライアントアプリ", size=8.5, color=d.P.text)
    d.arrow(X0 + pw / 2, DY0 + 0.72, X0 + pw / 2, DY0 + 0.84, color=d.P.primary, weight=1.3)
    d.shape(X0 + 0.20, DY0 + 0.86, pw - 0.40, 0.52, kind="ROUND_RECTANGLE",
            fill=d.P.primary, stroke=None, text="Cluster ノード\n＋ LogWriter", size=8.5,
            bold=True, color="#FFFFFF", line_spacing=105)
    d.arrow(X0 + pw / 2, DY0 + 1.40, X0 + pw / 2, DY0 + 1.52, color=d.P.primary, weight=1.3)
    db(d, X0 + pw / 2 - 0.65, DY0 + 1.54, 1.30, 0.42, "プライマリ DB")

    # 共有コンポーネント
    cx = X0 + pw + 0.30
    cw = 2.10
    zone(d, cx, DY0, cw, 2.30, "共有", fill=lighten(d.P.info, 0.95),
         stroke=lighten(d.P.info, 0.6))
    db(d, cx + cw / 2 - 0.70, DY0 + 0.42, 1.40, 0.42, "Coordinator DB",
       sub="トランザクション状態", fill=lighten(d.P.info, 0.85))
    db(d, cx + cw / 2 - 0.70, DY0 + 1.36, 1.40, 0.42, "レプリケーション DB",
       sub="書き込み操作のグループ", fill=lighten(d.P.info, 0.85))

    # バックアップ
    bx = cx + cw + 0.30
    bw = XE - bx
    zone(d, bx, DY0, bw, 2.30, "バックアップサイト", fill="#F7FCF5",
         stroke=lighten(d.P.success, 0.5))
    d.shape(bx + 0.20, DY0 + 0.86, bw - 0.40, 0.52, kind="ROUND_RECTANGLE",
            fill=d.P.success, stroke=None, text="Cluster ノード\n＋ LogApplier", size=8.5,
            bold=True, color="#FFFFFF", line_spacing=105)
    d.arrow(bx + bw / 2, DY0 + 1.40, bx + bw / 2, DY0 + 1.52, color=d.P.success, weight=1.3)
    db(d, bx + bw / 2 - 0.72, DY0 + 1.54, 1.44, 0.42, "バックアップ DB",
       sub="アプリテーブル＋メタデータ")
    d.shape(bx + 0.20, DY0 + 0.36, bw - 0.40, 0.34, kind="ROUND_RECTANGLE",
            fill=lighten(d.P.success, 0.84), stroke=lighten(d.P.success, 0.5),
            text="分析 / BI（リードレプリカ）", size=8.5, color=d.P.text)

    # データの流れ
    d.arrow(X0 + pw - 0.10, DY0 + 1.12, cx + cw / 2 - 0.68, DY0 + 1.50,
            color=d.P.primary, weight=1.6)
    d.arrow(cx + cw / 2 + 0.70, DY0 + 1.50, bx + 0.18, DY0 + 1.12,
            color=d.P.success, weight=1.6)
    d.label(X0 + pw - 0.20, DY0 + 1.90, 1.20, 0.22, "① 記録", size=8, bold=True,
            align="CENTER", color=d.P.primaryDark)
    d.label(cx + cw - 0.30, DY0 + 1.90, 1.20, 0.22, "② 適用", size=8, bold=True,
            align="CENTER", color=darken(d.P.success, 0.4))

    # 用途と制約
    y = DY0 + 2.44
    hw = (W - 0.3) / 2
    d.shape(X0, y, hw, 0.66, kind="ROUND_RECTANGLE", fill=lighten(d.P.success, 0.88),
            stroke=lighten(d.P.success, 0.5))
    d.label(X0 + 0.12, y + 0.05, hw - 0.24, 0.56,
            "用途：災害対策のフェイルオーバー／リードレプリカ\n"
            "（分析・BI）／マルチリージョン・異種クラウド構成",
            size=8, align="START", valign="TOP", color=darken(d.P.success, 0.45),
            line_spacing=120)
    d.shape(X0 + hw + 0.3, y, hw, 0.66, kind="ROUND_RECTANGLE",
            fill=lighten(d.P.danger, 0.88), stroke=lighten(d.P.danger, 0.5))
    d.label(X0 + hw + 0.42, y + 0.05, hw - 0.24, 0.56,
            "制約：バックアップサイトは1つのみ／DDL は複製されず\n"
            "スキーマは手動同期／1フェーズコミット最適化と併用不可",
            size=8, align="START", valign="TOP", color=darken(d.P.danger, 0.25),
            line_spacing=120)

    foot(d, ["・同期・非同期のハイブリッド方式で、書き込み操作をニアリアルタイムに複製し RPO = 0 を保証する"],
         "提供: Enterprise Premium（3.16+）｜ 状況: Private Preview")


@slide("ベクトルストア抽象化で RAG を特定製品に縛られず作れる",
       note="LangChain4j の使い方をほぼそのまま踏襲でき、ファクトリ生成部分だけが異なります。ストア差し替えが設定で済むのが利点です。")
def s_vector(d):
    # RAG フロー
    zone(d, X0, DY0, W, 1.42, "RAG のデータフロー")
    steps = ["社内文書\nマニュアル", "埋め込みモデル\nでベクトル化", "ベクトルストア\nに保存",
             "類似検索", "LLM が\n回答を生成"]
    sw = (W - 0.28 - 0.30 * 4) / 5
    for i, s in enumerate(steps):
        sx = X0 + 0.14 + i * (sw + 0.30)
        col = d.P.primary if i in (1, 2, 3) else lighten(d.P.muted, 0.2)
        d.shape(sx, DY0 + 0.38, sw, 0.80, kind="ROUND_RECTANGLE",
                fill=lighten(col, 0.88) if i not in (1, 2, 3) else col,
                stroke=None if i in (1, 2, 3) else lighten(col, 0.5),
                text=s, size=8.5, bold=(i in (1, 2, 3)),
                color="#FFFFFF" if i in (1, 2, 3) else d.P.text, line_spacing=110)
        if i < 4:
            d.arrow(sx + sw + 0.03, DY0 + 0.78, sx + sw + 0.27, DY0 + 0.78,
                    color=d.P.primary, weight=1.5)
    d.label(X0 + 0.14 + (sw + 0.30), DY0 + 1.20, sw * 3 + 0.60, 0.20,
            "この範囲を ScalarDB が抽象化する", size=8, bold=True, align="CENTER",
            color=d.P.primaryDark)

    # 対応ストア / モデル
    y = DY0 + 1.52
    pw = (W - 0.3) / 2
    zone(d, X0, y, pw, 1.42, "対応ベクトルストア")
    pills(d, X0 + 0.14, y + 0.34, pw - 0.28,
          ["インメモリ（試作用）", "OpenSearch（ローカル / AWS）",
           "Azure Cosmos DB for NoSQL", "Azure AI Search", "pgvector"],
          per_row=1, h=0.19, gap=0.04, size=8)
    rx = X0 + pw + 0.3
    zone(d, rx, y, pw, 1.42, "対応埋め込みモデル")
    pills(d, rx + 0.14, y + 0.34, pw - 0.28,
          ["インプロセス（ONNX ランタイム）", "Amazon Bedrock", "Azure OpenAI",
           "Google Vertex AI", "OpenAI"],
          per_row=1, h=0.19, gap=0.04, size=8, fill=lighten(d.P.info, 0.85),
          color=darken(d.P.info, 0.35))

    y2 = y + 1.54
    d.shape(X0, y2, W, 0.34, kind="ROUND_RECTANGLE", fill="#F4F6F9",
            stroke=lighten(d.P.muted, 0.6),
            text="LangChain4j がベース。ScalarDbEmbeddingClientFactory で生成し、以降は LangChain4j と同じ API で操作する",
            size=8.5, color=d.P.text)

    foot(d, ["・ストアやモデルを設定で差し替えられるため、プロトタイプから本番への移行でアプリを書き換えずに済む"],
         "提供: Enterprise Premium（3.15+）｜ 状況: Private Preview")


@slide("MCP Server が1つのサーバで複数 DB を AI に開放する",
       note="自然言語の依頼を LLM が SQL または SDK 呼び出しに変換します。権限は ScalarDB 側の認証認可で必ず絞ってください。")
def s_mcp(d):
    # 上: AI クライアント
    d.shape(X0 + 2.7, DY0, 3.6, 0.40, kind="ROUND_RECTANGLE", fill=lighten(d.P.primary, 0.86),
            stroke=lighten(d.P.primary, 0.6),
            text="AI クライアント（LLM / エージェント）", size=9.5, bold=True, color=d.P.text)
    d.arrow(X0 + W / 2, DY0 + 0.42, X0 + W / 2, DY0 + 0.56, color=d.P.primary, weight=1.5)
    d.label(X0 + W / 2 + 0.10, DY0 + 0.40, 2.20, 0.20, "STDIO（現時点）", size=7.5,
            align="START", color=d.P.muted)

    # MCP Server と2モード
    zone(d, X0 + 0.9, DY0 + 0.58, W - 1.8, 1.66, "ScalarDB MCP Server")
    mw = (W - 1.8 - 0.28 - 0.20) / 2
    modes = [("SQL モード（Cluster 向け）", d.P.primary,
              ["scalardb_execute_sql（単一ツール）",
               "BEGIN / COMMIT / ROLLBACK の標準構文"]),
             ("CRUD モード（Core 向け）", d.P.info,
              ["scalardb_scan / scalardb_get /",
               "scalardb_create_table などの個別ツール",
               "明示的なトランザクション制御"])]
    for i, (nm, col, items) in enumerate(modes):
        mx = X0 + 0.9 + 0.14 + i * (mw + 0.20)
        d.shape(mx, DY0 + 0.92, mw, 0.30, kind="ROUND_RECTANGLE", fill=col, stroke=None,
                text=nm, size=8.5, bold=True, color="#FFFFFF")
        d.label(mx + 0.06, DY0 + 1.28, mw - 0.12, 0.88,
                "\n".join("・" + s for s in items), size=8, align="START", valign="TOP",
                color=d.P.text, line_spacing=125)

    d.arrow(X0 + W / 2, DY0 + 2.26, X0 + W / 2, DY0 + 2.40, color=d.P.primary, weight=1.5)
    d.shape(X0 + 2.4, DY0 + 2.42, 4.2, 0.38, kind="ROUND_RECTANGLE", fill=d.P.primary,
            stroke=None, text="ScalarDB（Cluster / Core）", size=9.5, bold=True,
            color="#FFFFFF")

    # DB 群
    y = DY0 + 2.94
    names = ["PostgreSQL", "MySQL", "Cosmos DB", "DynamoDB", "Cassandra"]
    bw = (W - 0.20 * 4) / 5
    for i, nm in enumerate(names):
        bx = X0 + i * (bw + 0.20)
        d.line(X0 + W / 2, DY0 + 2.82, bx + bw / 2, y - 0.02,
               color=lighten(d.P.primary, 0.5), weight=0.9)
        d.shape(bx, y, bw, 0.30, kind="ROUND_RECTANGLE", fill="#FFFFFF",
                stroke=lighten(d.P.muted, 0.35), text=nm, size=8, color=d.P.text)

    d.label(X0, DY0 + 3.28 - 0.02, W, 0.20,
            "DB ごとに MCP サーバを立てる必要がない（配布形態は Docker / JAR。SSE によるリモート提供は将来対応予定）",
            size=8, align="CENTER", valign="TOP", color=d.P.muted)

    foot(d, ["・アクセス範囲は ScalarDB の認証認可（必要なら ABAC）で必ず制限する。MCP 側だけでは守れない"],
         "提供: Community / Enterprise ｜ 状況: GA")


# =====================================================================
# 4. ScalarDB Analytics
# =====================================================================

plain(layout="SECTION", title="4. ScalarDB Analytics — 横断分析",
      body="ユニバーサルデータカタログ、Spark クエリエンジン、認証・認可",
      notes="OLAP 側のコンポーネントです。")


@slide("Analytics はカタログとクエリエンジンを分離した構成をとる",
       note="カタログとエンジンが分離しているため、将来別のクエリエンジンに載せ替える余地があります。")
def s_analytics_arch(d):
    # 上: 利用者
    d.shape(X0 + 0.8, DY0, 3.2, 0.38, kind="ROUND_RECTANGLE", fill=lighten(d.P.info, 0.86),
            stroke=lighten(d.P.info, 0.6), text="BI / 分析アプリ（Spark SQL）", size=9,
            bold=True, color=d.P.text)
    d.shape(XE - 3.6, DY0, 3.2, 0.38, kind="ROUND_RECTANGLE", fill=lighten(d.P.muted, 0.75),
            stroke=lighten(d.P.muted, 0.4), text="運用者（CLI）", size=9, bold=True,
            color=d.P.text)

    # クエリエンジン / サーバ
    y = DY0 + 0.56
    ew = 4.30
    d.arrow(X0 + 2.4, DY0 + 0.40, X0 + ew / 2, y - 0.02, color=d.P.info, weight=1.5)
    d.shape(X0, y, ew, 0.86, kind="ROUND_RECTANGLE", fill=d.P.info, stroke=None)
    d.label(X0 + 0.12, y + 0.08, ew - 0.24, 0.26, "クエリエンジン（Apache Spark プラグイン）",
            size=9.5, bold=True, align="CENTER", color="#FFFFFF")
    d.label(X0 + 0.12, y + 0.36, ew - 0.24, 0.42,
            "ScalarDbAnalyticsCatalog を実装し、登録済みデータソースを\nSpark テーブルとして公開",
            size=8, align="CENTER", color="#E8F4FF", line_spacing=110)

    sx = X0 + ew + 0.40
    sw = XE - sx
    d.arrow(XE - 2.0, DY0 + 0.40, sx + sw / 2, y - 0.02, color=d.P.muted, weight=1.4)
    d.shape(sx, y, sw, 0.86, kind="ROUND_RECTANGLE", fill=d.P.primary, stroke=None)
    d.label(sx + 0.12, y + 0.08, sw - 0.24, 0.26, "ScalarDB Analytics サーバ", size=9.5,
            bold=True, align="CENTER", color="#FFFFFF")
    d.label(sx + 0.12, y + 0.36, sw - 0.24, 0.42,
            "カタログメタデータを管理し、\nエンジンと CLI に API を提供",
            size=8, align="CENTER", color="#D7E6F2", line_spacing=110)
    d.arrow(sx - 0.02, y + 0.43, X0 + ew + 0.02, y + 0.43, color=d.P.success, weight=1.6,
            start_arrow="FILL_ARROW")
    d.label(X0 + ew - 0.15, y - 0.24, 0.75, 0.22, "参照", size=7.5, align="CENTER",
            color=d.P.muted)

    # カタログ
    y2 = y + 1.02
    d.shape(X0 + 1.6, y2, W - 3.2, 0.40, kind="ROUND_RECTANGLE",
            fill=lighten(d.P.primary, 0.86), stroke=lighten(d.P.primary, 0.6),
            text="ユニバーサルデータカタログ（複数のカタログ空間を扱うメタデータ管理）",
            size=9, bold=True, color=d.P.text)
    d.arrow(sx + sw / 2, y + 0.88, X0 + W / 2, y2 - 0.02, color=d.P.primary, weight=1.4)

    # データソース
    y3 = y2 + 0.58
    srcs = [("PostgreSQL", True), ("Cassandra", True), ("DynamoDB", True),
            ("MySQL", False), ("Cosmos DB", False)]
    bw = (W - 0.20 * 4) / 5
    for i, (nm, managed) in enumerate(srcs):
        bx = X0 + i * (bw + 0.20)
        d.line(X0 + W / 2, y2 + 0.42, bx + bw / 2, y3 - 0.02,
               color=lighten(d.P.primary, 0.5), weight=0.9)
        db(d, bx + 0.18, y3, bw - 0.36, 0.42, nm,
           sub="ScalarDB 管理" if managed else "非管理（3.15+）")

    y4 = y3 + 0.92
    d.shape(X0, y4, W, 0.36, kind="ROUND_RECTANGLE", fill=lighten(d.P.success, 0.86),
            stroke=None,
            text="ScalarDB 管理データと非管理データの両方を、同じ SQL から横断して分析できる",
            size=9, bold=True, color=darken(d.P.success, 0.45))

    foot(d, ["・カタログとエンジンが独立しているため、同じカタログに対して異なるクエリエンジンを選べる"],
         "提供: Enterprise Option ｜ 状況: GA")


@slide("ユニバーサルデータカタログが異種ソースを1つの階層に写す",
       note="データソースの能力メタデータを持つため、プッシュダウンできる処理をエンジン側が判断できます。")
def s_catalog(d):
    # 階層ツリー
    lw = 4.20
    zone(d, X0, DY0, lw, 2.66, "カタログの階層構造")
    levels = [("カタログ", "全データソース情報を束ねる最上位", d.P.primaryDark),
              ("データソース", "個々の DB。接続情報と能力メタデータ", d.P.primary),
              ("名前空間", "PostgreSQL の schema / Cassandra の keyspace",
               lighten(d.P.primary, 0.35)),
              ("テーブル", "カラム定義と型情報を持つ実体", lighten(d.P.primary, 0.60))]
    for i, (nm, sub, col) in enumerate(levels):
        iy = DY0 + 0.36 + i * 0.56
        ind = i * 0.22
        d.shape(X0 + 0.16 + ind, iy, 1.30, 0.32, kind="ROUND_RECTANGLE", fill=col,
                stroke=None, text=nm, size=8.5, bold=True, color="#FFFFFF")
        d.label(X0 + 1.54 + ind, iy + 0.02, lw - 1.74 - ind, 0.34, sub, size=7.5,
                align="START", color=d.P.text)
        if i < 3:
            d.line(X0 + 0.30 + ind, iy + 0.33, X0 + 0.30 + ind, iy + 0.55,
                   color=d.P.muted, weight=1.0)
            d.line(X0 + 0.30 + ind, iy + 0.55, X0 + 0.36 + ind + 0.22, iy + 0.55,
                   color=d.P.muted, weight=1.0)
    d.label(X0 + 0.16, DY0 + 2.68 - 0.32, lw - 0.32, 0.26,
            "テーブル参照形式：<カタログ>.<データソース>.<名前空間>.<テーブル>",
            size=7.5, bold=True, align="START", color=d.P.primaryDark)

    # 2つのマッピング
    rx = X0 + lw + 0.30
    rw = XE - rx
    zone(d, rx, DY0, rw, 1.24, "① カタログ構造マッピング")
    d.label(rx + 0.14, DY0 + 0.34, rw - 0.28, 0.82,
            "ソース側の名前空間・テーブル・カラムを\n解決し、共通の階層構造に写す。",
            size=8.5, align="START", valign="TOP", color=d.P.text, line_spacing=130)
    zone(d, rx, DY0 + 1.36, rw, 1.30, "② データ型マッピング")
    d.label(rx + 0.14, DY0 + 1.70, rw - 0.28, 0.44,
            "ネイティブ型を 16 種の共通型に変換する。",
            size=8.5, align="START", valign="TOP", color=d.P.text, line_spacing=130)
    pills(d, rx + 0.14, DY0 + 2.14, rw - 0.28,
          ["BYTE", "INT", "TEXT", "TIMESTAMP", "DECIMAL", "…"],
          per_row=6, h=0.22, gap=0.06, size=7.5)

    y = DY0 + 2.80
    d.shape(X0, y, W, 0.34, kind="ROUND_RECTANGLE", fill=lighten(d.P.primary, 0.90),
            stroke=lighten(d.P.primary, 0.62),
            text="登録は CLI で行う（カタログ作成 → データソース登録）。以降はエンジンがカタログを参照する",
            size=8.5, color=d.P.text)

    foot(d, ["・型を共通化するため、異種ソースを跨いだ結合でも型の突き合わせをアプリ側で意識しなくてよい"],
         "提供: Enterprise Option ｜ 状況: GA")


@slide("Spark SQL から異種ソースを跨いだ結合をそのまま書ける",
       note="ETL を挟まずに現行データへ直接クエリできるのが要点です。Spark ワーカーを増やして性能をスケールさせます。")
def s_analytics_query(d):
    # クエリ例
    zone(d, X0, DY0, W, 1.16, "テーブル参照形式と結合の例")
    d.shape(X0 + 0.16, DY0 + 0.34, W - 0.32, 0.34, kind="RECTANGLE", fill="#F4F6F9",
            stroke=lighten(d.P.muted, 0.6),
            text="spark.sql(\"SELECT * FROM my_catalog.my_source.my_namespace.my_table\").show();",
            size=9, color=d.P.text)
    parts = [("my_catalog", "カタログ名"), ("my_source", "データソース名"),
             ("my_namespace", "名前空間"), ("my_table", "テーブル")]
    pwv = (W - 0.32 - 0.14 * 3) / 4
    for i, (nm, sub) in enumerate(parts):
        px = X0 + 0.16 + i * (pwv + 0.14)
        d.shape(px, DY0 + 0.76, pwv, 0.28, kind="ROUND_RECTANGLE",
                fill=lighten(d.P.primary, 0.86), stroke=None,
                text=f"{nm} = {sub}", size=7.5, color=d.P.primaryDark)

    # 結合図
    y = DY0 + 1.26
    zone(d, X0, y, W, 1.30, "異種ソースを跨いだ結合")
    # 縦積みにする。横並びだと片方への矢印がもう片方を横切る
    # 名前は円柱の左側に置く。右に置くと、円柱から JOIN へ向かう線が通る
    d.label(X0 + 0.16, y + 0.34, 1.30, 0.26, "PostgreSQL・orders", size=7.5,
            align="END", valign="MIDDLE", color=d.P.text)
    src1 = d.shape(X0 + 1.50, y + 0.34, 0.95, 0.26, kind="CAN", fill="#FFFFFF",
                   stroke=d.P.muted)
    d.label(X0 + 0.16, y + 0.84, 1.30, 0.26, "Cassandra・sessions", size=7.5,
            align="END", valign="MIDDLE", color=d.P.text)
    src2 = d.shape(X0 + 1.50, y + 0.84, 0.95, 0.26, kind="CAN", fill="#FFFFFF",
                   stroke=d.P.muted)
    join = d.shape(X0 + 2.90, y + 0.44, 1.75, 0.50, kind="ROUND_RECTANGLE",
                   fill=d.P.info, stroke=None, text="Spark SQL で JOIN", size=9,
                   bold=True, color="#FFFFFF")
    d.link(src1, join, color=d.P.info, weight=1.5)
    d.link(src2, join, color=d.P.info, weight=1.5)
    res = d.shape(X0 + 4.95, y + 0.44, 1.55, 0.50, kind="ROUND_RECTANGLE",
                  fill=lighten(d.P.success, 0.84), stroke=lighten(d.P.success, 0.5),
                  text="結合結果", size=9, bold=True, color=darken(d.P.success, 0.45))
    d.link(join, res, color=d.P.info, weight=1.5)
    d.label(X0 + 6.70, y + 0.40, 2.15, 0.66,
            "ETL でデータウェアハウスへ\n集約する工程が不要になり、\n鮮度が落ちない。",
            size=8, align="START", valign="TOP", color=d.P.text, line_spacing=120)

    # 3つの利用形態
    y2 = y + 1.26
    d.cards(X0, y2, W, 0.90, [
        ("Spark ドライバアプリ", "SparkSession を使う通常の Spark ジョブ"),
        ("Spark Connect アプリ", "Spark Connect プロトコルでリモート接続"),
        ("JDBC アプリ", "マネージド Spark サービスにより可否が異なる"),
    ], accent=[d.P.info, d.P.info, lighten(d.P.muted, 0.2)], title_size=9, body_size=7.5)

    foot(d, ["・前提：Analytics サーバ稼働＋データソース登録済み、対応する Spark と JAR 依存・カタログ登録設定"],
         "提供: Enterprise Option ｜ 状況: GA（非 ScalarDB ソースは 3.15+）")


@slide("Analytics の認可はカタログからテーブルまで階層的に効く",
       note="Cluster に認証を委譲できるため、OLTP と OLAP でユーザー管理を二重化せずに済みます。")
def s_analytics_auth(d):
    # 認証バックエンド
    lw = 4.20
    zone(d, X0, DY0, lw, 1.34, "認証バックエンド（2 択）")
    for i, (nm, sub, col) in enumerate([
            ("Internal", "Analytics 内で資格情報を管理\n（user register CLI コマンド）", d.P.primary),
            ("ScalarDB Cluster", "外部 Cluster に検証を委譲し\nジャストインタイムでプロビジョニング",
             d.P.success)]):
        ix = X0 + 0.14 + i * ((lw - 0.28) / 2 + 0.10)
        iw = (lw - 0.38) / 2
        d.shape(ix, DY0 + 0.34, iw, 0.30, kind="ROUND_RECTANGLE", fill=col, stroke=None,
                text=nm, size=8.5, bold=True, color="#FFFFFF")
        d.label(ix + 0.04, DY0 + 0.68, iw - 0.08, 0.56, sub, size=7.5, align="START",
                valign="TOP", color=d.P.text, line_spacing=115)

    # リソース階層
    rx = X0 + lw + 0.30
    rw = XE - rx
    zone(d, rx, DY0, rw, 2.80, "リソース階層と権限レベル")
    res = [("System", "—", d.P.primaryDark),
           ("Catalog", "read / write / admin", d.P.primary),
           ("Data source", "read / admin", lighten(d.P.primary, 0.35)),
           ("Namespace", "read", lighten(d.P.primary, 0.55)),
           ("Table", "read", lighten(d.P.primary, 0.72))]
    for i, (nm, perm, col) in enumerate(res):
        iy = DY0 + 0.34 + i * 0.42
        ind = i * 0.16
        d.shape(rx + 0.16 + ind, iy, 1.35, 0.34, kind="ROUND_RECTANGLE", fill=col,
                stroke=None, text=nm, size=8.5, bold=True,
                color="#FFFFFF" if i < 4 else d.P.text)
        d.label(rx + 1.60 + ind, iy + 0.05, rw - 1.80 - ind, 0.26, perm, size=8,
                align="START", color=d.P.text)
        if i < 4:
            d.arrow(rx + 0.30 + ind, iy + 0.35, rx + 0.30 + ind + 0.16, iy + 0.45,
                    color=d.P.muted, weight=1.0)
    d.shape(rx + 0.16, DY0 + 2.72 - 0.34, rw - 0.32, 0.30, kind="ROUND_RECTANGLE",
            fill=lighten(d.P.success, 0.84), stroke=None,
            text="CATALOG_READ は配下すべてに継承される", size=8, bold=True,
            color=darken(d.P.success, 0.45))

    # ユーザー種別
    zone(d, X0, DY0 + 1.46, lw, 1.34, "ユーザーとロール")
    d.label(X0 + 0.14, DY0 + 1.80, lw - 0.28, 0.92,
            "・スーパーユーザー：全権限。カタログ作成、\n　ユーザー・ロール管理\n"
            "・通常ユーザー：初期は権限なし（付与が必要）\n"
            "・初回ログインの管理ユーザーに SUPERADMIN",
            size=8.5, align="START", valign="TOP", color=d.P.text, line_spacing=125)

    y = DY0 + 2.92
    d.shape(X0, y, W, 0.36, kind="ROUND_RECTANGLE", fill="#F4F6F9",
            stroke=lighten(d.P.muted, 0.6),
            text="Spark 側：spark.sql.catalog.<catalog>.server.auth.username / password　"
                 "／　認証を有効化する場合 TLS は必須",
            size=8.5, color=d.P.text)

    foot(d, ["・権限はロール経由でも直接でも付与できる。OLTP 側と同じ考え方で設計できる"],
         "提供: Enterprise Option ｜ 状況: GA（3.18）")


# =====================================================================
# 5. 運用・ツール
# =====================================================================

plain(layout="SECTION", title="5. 運用・ツール",
      body="データ移行、バックアップ、監視・管理、Kubernetes デプロイ、性能評価",
      notes="本番運用に必要な周辺機能です。")


@slide("Data Loader が ScalarDB と外部システム間の移動を担う",
       note="全体がアトミックでないため、中断時はログを見て再開範囲を判断する運用設計が必要です。")
def s_dataloader(d):
    # 双方向フロー
    zone(d, X0, DY0, W, 1.28, "インポート / エクスポート")
    d.shape(X0 + 0.30, DY0 + 0.42, 2.00, 0.66, kind="ROUND_RECTANGLE",
            fill=lighten(d.P.info, 0.86), stroke=lighten(d.P.info, 0.6),
            text="ファイル\nJSON / JSONL / CSV", size=8.5, color=d.P.text, line_spacing=110)
    d.shape(X0 + 3.40, DY0 + 0.42, 2.20, 0.66, kind="ROUND_RECTANGLE", fill=d.P.primary,
            stroke=None, text="Data Loader（CLI）", size=9.5, bold=True, color="#FFFFFF")
    d.shape(X0 + 6.70, DY0 + 0.42, 2.00, 0.66, kind="ROUND_RECTANGLE",
            fill=lighten(d.P.primary, 0.86), stroke=lighten(d.P.primary, 0.6),
            text="ScalarDB\n（Core / Cluster）", size=8.5, color=d.P.text, line_spacing=110)
    d.arrow(X0 + 2.32, DY0 + 0.62, X0 + 3.38, DY0 + 0.62, color=d.P.info, weight=1.6)
    d.label(X0 + 2.32, DY0 + 0.38, 1.06, 0.20, "import", size=7.5, align="CENTER",
            color=darken(d.P.info, 0.35))
    d.arrow(X0 + 3.38, DY0 + 0.90, X0 + 2.32, DY0 + 0.90, color=d.P.success, weight=1.6)
    d.label(X0 + 2.32, DY0 + 0.92, 1.06, 0.20, "export", size=7.5, align="CENTER",
            color=darken(d.P.success, 0.4))
    d.arrow(X0 + 5.62, DY0 + 0.62, X0 + 6.68, DY0 + 0.62, color=d.P.info, weight=1.6)
    d.arrow(X0 + 6.68, DY0 + 0.90, X0 + 5.62, DY0 + 0.90, color=d.P.success, weight=1.6)

    # 2モード
    y = DY0 + 1.36
    pw = (W - 0.3) / 2
    zone(d, X0, y, pw, 1.26, "TRANSACTION モード", stroke=lighten(d.P.primary, 0.6))
    d.label(X0 + 0.14, y + 0.34, pw - 0.28, 0.90,
            "・Consensus Commit を使用\n"
            "・トランザクショングループ単位で ACID\n　（既定 100 件）\n"
            "・整合性が必要な投入に使う",
            size=8.5, align="START", valign="TOP", color=d.P.text, line_spacing=125)
    rx = X0 + pw + 0.3
    zone(d, rx, y, pw, 1.26, "STORAGE モード", stroke=lighten(d.P.success, 0.5),
         fill="#F7FCF5")
    d.label(rx + 0.14, y + 0.34, pw - 0.28, 0.90,
            "・非トランザクショナルな単発 CRUD\n"
            "・大量データ投入向け\n"
            "・オーバーヘッドが小さい",
            size=8.5, align="START", valign="TOP", color=d.P.text, line_spacing=125)

    # 操作とマッピング
    y2 = y + 1.32
    hw = (W - 0.3) / 2
    zone(d, X0, y2, hw, 0.78, "インポート操作")
    pills(d, X0 + 0.14, y2 + 0.30, hw - 0.28,
          ["INSERT（新規のみ）", "UPDATE（既存のみ）", "UPSERT"],
          per_row=3, h=0.22, gap=0.08, size=7.5)
    d.label(X0 + 0.14, y2 + 0.55, hw - 0.28, 0.20,
            "マッピングは自動（フィールド名＝カラム名）または制御ファイル", size=7.5,
            align="START", valign="TOP", color=d.P.muted)
    zone(d, X0 + hw + 0.3, y2, hw, 0.78, "エクスポートの絞り込み")
    pills(d, X0 + hw + 0.44, y2 + 0.30, hw - 0.28,
          ["パーティションキー", "クラスタリング範囲", "カラム射影", "件数制限"],
          per_row=4, h=0.22, gap=0.06, size=7,
          fill=lighten(d.P.success, 0.84), color=darken(d.P.success, 0.4))

    foot(d, ["・グループ単位では ACID だが、インポート／エクスポート全体はアトミックでない。中断時はログから再開範囲を判断する"],
         "提供: Community / Enterprise（Cluster 版は Enterprise Standard 以上）｜ 状況: GA")


@slide("バックアップは「pause して静止点を作る」ことが前提になる",
       note="「pause 期間の中間時刻を使う」のは実務上の重要な勘所です。Scalar Manager で pause をスケジュール実行できます。")
def s_backup(d):
    # タイムライン
    zone(d, X0, DY0, W, 1.62, "pause による静止点の作り方")
    tl_y = DY0 + 0.78
    d.line(X0 + 0.30, tl_y, XE - 0.30, tl_y, color=lighten(d.P.muted, 0.3),
           weight=1.5, free=True)                                     # 軸
    # 復旧ポイント（中間時刻）はマーカー自体に持たせる。別ラベル＋縦矢印にすると
    # 他のマーカーの説明文と、下の表の見出し行に重なる。
    marks = [(0.95, "通常運転", lighten(d.P.muted, 0.2)),
             (2.40, "pause 開始\nリクエストをドレイン", d.P.warning),
             (4.44, "★ 復旧ポイント\npause 期間の中間時刻", d.P.danger),
             (6.30, "unpause\n通常運転に復帰", d.P.primary)]
    for mx, label, col in marks:
        d.shape(X0 + mx, tl_y - 0.09, 0.18, 0.18, kind="ELLIPSE", fill=col, stroke=None)
        d.label(X0 + mx - 0.85, tl_y + 0.15, 1.90, 0.44, label, size=7.5, bold=True,
                align="CENTER", color=darken(col, 0.35), line_spacing=105)
    # 静止帯（pause 開始 〜 unpause）
    d.shape(X0 + 2.49, tl_y - 0.36, 3.90, 0.24, kind="ROUND_RECTANGLE",
            fill=lighten(d.P.success, 0.80), stroke=None,
            text="この期間にスナップショット / PITR で取得", size=7.5, bold=True,
            color=darken(d.P.success, 0.45))

    # 要件と DB 別方針
    y = DY0 + 1.68
    rows = [["MySQL / PostgreSQL / SQLite 等",
             "mysqldump --single-transaction / pg_dump", "不要（無停止で可）"],
            ["DynamoDB / Cosmos DB / Cassandra",
             "静止期間にスナップショット、または PITR", "必要"],
            ["PITR 対応（DynamoDB / Cosmos DB / YugabyteDB）",
             "保持期間内の任意時刻を指定して復旧", "必要"]]

    def cc(i, j, cell):
        if j == 2:
            return ((lighten(d.P.success, 0.82), darken(d.P.success, 0.45))
                    if "不要" in cell else (lighten(d.P.warning, 0.70), darken(d.P.warning, 0.55)))
        return None

    grid(d, X0, y, W, ["下位 DB", "取得方法", "pause"], rows,
         col_w=[3.60, 3.80, 1.60], row_h=0.29, head_h=0.30, cell_colors=cc)

    y2 = y + 0.30 + 3 * 0.29 + 0.10
    d.shape(X0, y2, W, 0.46, kind="ROUND_RECTANGLE", fill=lighten(d.P.primary, 0.90),
            stroke=lighten(d.P.primary, 0.62))
    d.label(X0 + 0.14, y2 + 0.02, W - 0.28, 0.42,
            "要件：Coordinator テーブルを含む全 ScalarDB 管理テーブルが、トランザクション整合状態か自動復旧可能であること\n"
            "pause の手段：アプリが Scalar Admin インターフェースを実装、または Cluster を利用（Scalar Admin クライアントツールで実行）",
            size=8.5, align="START", valign="TOP", color=d.P.text, line_spacing=120)

    foot(d, ["・pause は実行中トランザクションを失わずに停止できる。中間時刻を使うのはクライアントとサーバの時刻ずれを吸収するため"],
         "提供: Community / Enterprise ｜ 状況: GA")


@slide("Scalar Manager が個別ツールの使い分けを1画面に集約する",
       note="運用担当の学習コストを下げる目的のコンポーネントです。バックアップの pause 運用と組み合わせて使います。")
def s_manager(d):
    # 従来 → 集約
    lw = 3.10
    zone(d, X0, DY0, lw, 2.30, "従来：ツールを個別に使い分け",
         stroke=lighten(d.P.warning, 0.5), fill="#FFFCF4")
    tools = ["kubectl", "Prometheus", "Grafana", "Loki", "各種 CLI"]
    for i, t in enumerate(tools):
        d.shape(X0 + 0.30, DY0 + 0.40 + i * 0.36, lw - 0.60, 0.30,
                kind="ROUND_RECTANGLE", fill="#FFFFFF", stroke=lighten(d.P.muted, 0.4),
                text=t, size=8.5, color=d.P.text)

    d.arrow_shape(X0 + lw + 0.06, DY0 + 0.95, 0.50, 0.46, fill=lighten(d.P.primary, 0.7))

    # Scalar Manager
    mx = X0 + lw + 0.66
    mw = XE - mx
    zone(d, mx, DY0, mw, 2.30, "Scalar Manager（GUI で集約）")
    d.shape(mx + 0.20, DY0 + 0.36, mw - 0.40, 0.36, kind="ROUND_RECTANGLE",
            fill=d.P.primary, stroke=None,
            text="Kubernetes 環境における集中管理・監視", size=9, bold=True, color="#FFFFFF")
    feats = [("クラスタの可視化と監視",
              "健全性・Pod ログ・ハードウェア使用率・RPS。Grafana ダッシュボードを統合し、リアルタイムと時系列で参照"),
             ("pause / unpause 管理",
              "複数 DB の整合性を確保する pause ジョブを実行・スケジュールし、停止状態を GUI で管理"),
             ("ユーザー管理とアクセス制御",
              "アカウント作成・ロール割当・Grafana との SSO 連携")]
    for i, (nm, sub) in enumerate(feats):
        fy = DY0 + 0.78 + i * 0.56
        d.shape(mx + 0.20, fy, mw - 0.40, 0.54, kind="ROUND_RECTANGLE",
                fill=lighten(d.P.primary, 0.92), stroke=lighten(d.P.primary, 0.65))
        d.label(mx + 0.30, fy + 0.03, mw - 0.60, 0.20, nm, size=8.5, bold=True,
                align="START", valign="TOP", color=d.P.primaryDark)
        d.label(mx + 0.30, fy + 0.22, mw - 0.60, 0.30, sub, size=7, align="START",
                valign="TOP", color=d.P.text)

    y = DY0 + 2.44
    d.shape(X0, y, W, 0.50, kind="ROUND_RECTANGLE", fill="#F4F6F9",
            stroke=lighten(d.P.muted, 0.6))
    d.label(X0 + 0.14, y + 0.04, W - 0.28, 0.42,
            "既存の Prometheus / Grafana / Loki を置き換えるのではなく、それらを集約する構成\n"
            "ポート 13000 へのアクセスが必要",
            size=8.5, align="START", valign="TOP", color=d.P.text, line_spacing=120)

    foot(d, ["・pause のスケジュール実行ができるため、バックアップ運用の自動化とセットで検討する"],
         "提供: Enterprise ｜ 状況: GA")


@slide("Helm チャートで各コンポーネントのデプロイが標準化される",
       note="プロダクションチェックリストは本番移行前のレビュー資料としてそのまま使えます。")
def s_helm(d):
    # K8s クラスタ図
    zone(d, X0, DY0, W, 2.06, "Kubernetes クラスタ")
    d.shape(X0 + 0.30, DY0 + 0.40, 1.30, 0.44, kind="ROUND_RECTANGLE",
            fill=lighten(d.P.muted, 0.7), stroke=lighten(d.P.muted, 0.35),
            text="Envoy", size=8.5, bold=True, color=d.P.text)
    d.arrow(X0 + 1.62, DY0 + 0.62, X0 + 1.94, DY0 + 0.62, color=d.P.primary, weight=1.4)
    for i in range(3):
        d.shape(X0 + 1.96 + i * 1.10, DY0 + 0.40, 1.02, 0.44, kind="ROUND_RECTANGLE",
                fill=d.P.primary, stroke=None, text=f"Cluster\nNode {i + 1}", size=7.5,
                bold=True, color="#FFFFFF", line_spacing=100)
    d.shape(X0 + 5.35, DY0 + 0.40, 1.60, 0.44, kind="ROUND_RECTANGLE", fill=d.P.info,
            stroke=None, text="Analytics Server", size=8, bold=True, color="#FFFFFF")
    d.shape(X0 + 7.10, DY0 + 0.40, 1.60, 0.44, kind="ROUND_RECTANGLE",
            fill=lighten(d.P.primary, 0.35), stroke=None, text="GraphQL", size=8,
            bold=True, color="#FFFFFF")
    for i, (nm, col) in enumerate([("ScalarDL Ledger", d.P.primaryDark),
                                   ("ScalarDL Auditor", d.P.primaryDark),
                                   ("Scalar Manager", d.P.success),
                                   ("Scalar Admin for K8s", d.P.success)]):
        d.shape(X0 + 0.30 + i * 2.13, DY0 + 0.98, 2.03, 0.40, kind="ROUND_RECTANGLE",
                fill=lighten(col, 0.88), stroke=lighten(col, 0.55), text=nm, size=8,
                color=darken(col, 0.2))
    d.label(X0 + 0.30, DY0 + 1.48, W - 0.60, 0.24,
            "すべて Helm チャートで導入する（Schema Loader 用のチャートも提供）", size=8,
            align="CENTER", valign="TOP", color=d.P.muted)
    d.shape(X0 + 2.40, DY0 + 1.72, 4.20, 0.28, kind="ROUND_RECTANGLE",
            fill=lighten(d.P.primary, 0.88), stroke=lighten(d.P.primary, 0.6),
            text="下位 DB（クラスタ外のマネージドサービス等）", size=8, color=d.P.text)

    # 手順とチェックリスト
    y = DY0 + 2.00
    d.cards(X0, y, W, 1.00, [
        ("対応環境", "Amazon EKS / Azure AKS のクラスタ作成手順、マニュアルデプロイ手順"),
        ("TLS 構成", "cert-manager を使った構成手順を含む"),
        ("運用の導入", "ログ収集・監視、Secret による資格情報管理、ボリュームマウント"),
    ], accent=[d.P.primary, d.P.success, d.P.info], title_size=9, body_size=8)

    y2 = y + 1.10
    d.shape(X0, y2, W, 0.32, kind="ROUND_RECTANGLE", fill=lighten(d.P.success, 0.86),
            stroke=None,
            text="AWS / Google Cloud Marketplace 経由のデプロイにも対応。本番前はコンポーネント別のプロダクションチェックリストで確認する",
            size=8.5, bold=True, color=darken(d.P.success, 0.45))

    foot(d, ["・ScalarDB と ScalarDL が同じ Helm・監視・バックアップの枠組みに乗るため、運用の作り込みを共通化できる"],
         "提供: Community / Enterprise ｜ 状況: GA")


@slide("ベンチマークツールで採用前に自環境の性能を確認する",
       note="設定次第で性能が大きく変わるため、既定値のまま測って判断しないことが重要です。数値は必ず自環境で取得してください。")
def s_benchmark(d):
    # ループ図
    lw = 4.05
    zone(d, X0, DY0, lw, 2.66, "測定と設定調整のループ")
    steps = ["構成を決める\n（DB / ノード数 / 配置）", "設定を変える\n（分離レベル・最適化）",
             "ベンチマークを実行", "結果を比較して判断"]
    for i, s in enumerate(steps):
        sy = DY0 + 0.38 + i * 0.56
        d.shape(X0 + 0.55, sy, lw - 1.10, 0.40, kind="ROUND_RECTANGLE",
                fill=lighten(d.P.primary, 0.90), stroke=lighten(d.P.primary, 0.62),
                text=s, size=8.5, color=d.P.text, line_spacing=105)
        if i < 3:
            d.arrow(X0 + lw / 2, sy + 0.41, X0 + lw / 2, sy + 0.55, color=d.P.primary,
                    weight=1.4)
    # 戻りの矢印（エルボー）。角の2点は経路の折れ点なので図形には接しない
    d.line(X0 + lw - 0.52, DY0 + 2.30, X0 + lw - 0.28, DY0 + 2.30, color=d.P.success,
           weight=1.5, free=True)
    d.line(X0 + lw - 0.28, DY0 + 2.30, X0 + lw - 0.28, DY0 + 0.60, color=d.P.success,
           weight=1.5, free=True)
    d.arrow(X0 + lw - 0.28, DY0 + 0.60, X0 + lw - 0.52, DY0 + 0.60, color=d.P.success,
            weight=1.5, free=True)

    # 変えるべき変数
    rx = X0 + lw + 0.30
    rw = XE - rx
    zone(d, rx, DY0, rw, 2.66, "測定時に変えるべき主な変数")
    vars_ = [("分離レベル", "SNAPSHOT / SERIALIZABLE / READ_COMMITTED"),
             ("1フェーズコミット最適化", "有効 / 無効"),
             ("グループコミット", "有効 / 無効"),
             ("非同期コミット", "有効 / 無効"),
             ("Coordinator テーブルの配置", "マルチストレージ構成でどの DB に置くか"),
             ("下位 DB とノード数", "DB 種別・インスタンスサイズ・台数")]
    for i, (nm, sub) in enumerate(vars_):
        vy = DY0 + 0.36 + i * 0.38
        d.shape(rx + 0.14, vy, 1.85, 0.32, kind="ROUND_RECTANGLE",
                fill=lighten(d.P.info, 0.84), stroke=None, text=nm, size=8,
                color=darken(d.P.info, 0.35))
        d.label(rx + 2.06, vy + 0.05, rw - 2.26, 0.26, sub, size=7.5, align="START",
                color=d.P.text)

    y = DY0 + 2.80
    d.shape(X0, y, W, 0.34, kind="ROUND_RECTANGLE", fill=lighten(d.P.warning, 0.74),
            stroke=None,
            text="⚠ 公称値ではなく自環境の実測で判断する。本デッキには性能数値を載せていない",
            size=9, bold=True, color=darken(d.P.warning, 0.55))

    foot(d, ["・PoC 段階のサイジングと構成比較（DB 選定・ノード数）の根拠づけに使う"],
         "提供: Community / Enterprise ｜ 状況: GA")


# =====================================================================
# 6. ScalarDL
# =====================================================================

plain(layout="SECTION", title="6. ScalarDL — 改ざん検知ミドルウェア",
      body="ビザンチン障害検知、アセットとハッシュチェーン、Ledger と Auditor、HashStore / TableStore",
      notes="ScalarDB とは別系統の製品です。")


@slide("ScalarDL は改ざんを「使われる前に」検知する",
       note="ブロックチェーンではなく、既存 DB の上に耐改ざん性を後付けするアプローチです。検知タイミングの考え方が特徴的です。")
def s_scalardl(d):
    # 2サーバ構成
    zone(d, X0, DY0, W, 1.90, "2 サーバ構成")
    d.shape(X0 + 3.30, DY0 + 0.36, 2.40, 0.40, kind="ROUND_RECTANGLE",
            fill=lighten(d.P.primary, 0.86), stroke=lighten(d.P.primary, 0.6),
            text="クライアント", size=9.5, bold=True, color=d.P.text)
    sw = 3.30
    for i, (nm, role, col) in enumerate([
            ("Ledger", "トランザクションを実行・コミットする主サーバ", d.P.primary),
            ("Auditor", "トランザクションを事前順序付けし、検証する副サーバ", d.P.success)]):
        sx = X0 + 0.90 + i * (sw + 0.60)
        d.arrow(X0 + 4.50, DY0 + 0.78, sx + sw / 2, DY0 + 0.94, color=col, weight=1.5)
        d.shape(sx, DY0 + 0.96, sw, 0.74, kind="ROUND_RECTANGLE", fill=col, stroke=None)
        d.label(sx + 0.10, DY0 + 1.02, sw - 0.20, 0.26, nm, size=10, bold=True,
                align="CENTER", color="#FFFFFF")
        d.label(sx + 0.10, DY0 + 1.28, sw - 0.20, 0.38, role, size=8, align="CENTER",
                color="#FFFFFF", line_spacing=110)
    d.arrow(X0 + 0.90 + sw + 0.02, DY0 + 1.33, X0 + 0.90 + sw + 0.58, DY0 + 1.33,
            color=d.P.danger, weight=1.6, start_arrow="FILL_ARROW")
    d.label(X0 + 0.90 + sw - 0.30, DY0 + 1.72, 1.20, 0.20, "相互検証", size=8, bold=True,
            align="CENTER", color=darken(d.P.danger, 0.25))

    # 設計目標
    y = DY0 + 1.96
    d.cards(X0, y, W, 0.92, [
        ("正確性（correctness）", "改ざんや悪意ある攻撃を検知できる"),
        ("スケーラビリティ", "独自のコンセンサスアルゴリズムで規模を保つ"),
        ("データベース非依存", "既存の DB の上に耐改ざん性を後付けする"),
    ], accent=[d.P.primary, d.P.info, d.P.success], title_size=9, body_size=8)

    # 検知タイミング
    y2 = y + 1.00
    d.shape(X0, y2, W, 0.46, kind="ROUND_RECTANGLE", fill=lighten(d.P.warning, 0.76),
            stroke=lighten(d.P.warning, 0.5))
    d.label(X0 + 0.14, y2 + 0.05, W - 0.28, 0.44,
            "重要な性質：障害を即座に検知するのではなく、「乖離した状態が使われようとしたときに\n"
            "クライアントが必ず検知できる」ことを保証する",
            size=8.5, bold=True, align="START", valign="TOP",
            color=darken(d.P.warning, 0.55), line_spacing=120)

    foot(d, ["・任意の障害（ビザンチン障害＝データ改ざん、悪意ある攻撃）を検知する middleware"],
         "エディション: Community / Enterprise ｜ バージョン: 3.13")


@slide("データはアセットのハッシュチェーンとして表現される",
       note="更新で上書きせず履歴を積む前提のモデルです。データモデリングの考え方が RDB とは異なります。")
def s_asset(d):
    # ハッシュチェーン
    zone(d, X0, DY0, W, 1.92, "アセット（asset ID）のレコード列は age 順のハッシュチェーンをなす")
    bw, gap = 1.85, 0.42
    for i in range(4):
        bx = X0 + 0.30 + i * (bw + gap)
        tampered = (i == 2)
        col = d.P.danger if tampered else d.P.primary
        d.shape(bx, DY0 + 0.44, bw, 0.92, kind="ROUND_RECTANGLE",
                fill=lighten(col, 0.90), stroke=col, stroke_weight=1.1)
        d.label(bx + 0.06, DY0 + 0.50, bw - 0.12, 0.22, f"age = {i}", size=8.5, bold=True,
                align="CENTER", color=darken(col, 0.25))
        d.shape(bx + 0.10, DY0 + 0.74, bw - 0.20, 0.24, kind="RECTANGLE",
                fill="#FFFFFF", stroke=lighten(col, 0.6), stroke_weight=0.75,
                text="データ", size=7.5, color=d.P.text)
        d.shape(bx + 0.10, DY0 + 1.02, bw - 0.20, 0.24, kind="RECTANGLE",
                fill=lighten(col, 0.80), stroke=None,
                text="prev hash" if i > 0 else "（先頭）", size=7.5,
                color=darken(col, 0.3))
        if i < 3:
            d.arrow(bx + bw + 0.03, DY0 + 0.90, bx + bw + gap - 0.03, DY0 + 0.90,
                    color=d.P.primary, weight=1.6)
    xmark(d, X0 + 0.30 + 2 * (bw + gap) + bw / 2, DY0 + 1.48, r=0.13)
    d.label(X0 + 0.30 + 2 * (bw + gap) - 0.40, DY0 + 1.62, bw + 0.80, 0.24,
            "途中を改ざんするとハッシュが繋がらない", size=7.5, bold=True,
            align="CENTER", color=darken(d.P.danger, 0.25))

    # アセット間チェーン
    y = DY0 + 2.06
    lw = 5.30
    zone(d, X0, y, lw, 1.06, "ビジネスロジックはアセット間の関係を作る")
    d.shape(X0 + 0.30, y + 0.42, 1.45, 0.42, kind="ROUND_RECTANGLE",
            fill=lighten(d.P.primary, 0.88), stroke=lighten(d.P.primary, 0.6),
            text="口座 A", size=8.5, color=d.P.text)
    d.shape(X0 + 2.10, y + 0.42, 1.10, 0.42, kind="ROUND_RECTANGLE", fill=d.P.primary,
            stroke=None, text="振込", size=8.5, bold=True, color="#FFFFFF")
    d.shape(X0 + 3.55, y + 0.42, 1.45, 0.42, kind="ROUND_RECTANGLE",
            fill=lighten(d.P.primary, 0.88), stroke=lighten(d.P.primary, 0.6),
            text="口座 B", size=8.5, color=d.P.text)
    d.arrow(X0 + 1.77, y + 0.63, X0 + 2.08, y + 0.63, color=d.P.primary, weight=1.4)
    d.arrow(X0 + 3.22, y + 0.63, X0 + 3.53, y + 0.63, color=d.P.primary, weight=1.4)

    rx = X0 + lw + 0.30
    rw = XE - rx
    zone(d, rx, y, rw, 1.06, "モデルの特徴")
    d.label(rx + 0.14, y + 0.36, rw - 0.28, 0.64,
            "・アセットは任意のデータを扱えるが、\n　履歴系列として捉えるのが自然\n"
            "・レコードは asset ID と age で識別",
            size=8.5, align="START", valign="TOP", color=d.P.text, line_spacing=120)

    foot(d, ["・各レコードが直前のレコードのハッシュを含むため、チェーンを辿ることで途中の改ざんを検知できる"],
         "エディション: Community / Enterprise ｜ 状況: GA")


@slide("コントラクトへの電子署名が実行者と改変を検証可能にする",
       note="アプリのロジックそのものが署名対象になるのが特徴です。Function はコントラクト外の副作用を扱う仕組みです。")
def s_contract(d):
    # 署名フロー
    zone(d, X0, DY0, W, 1.70, "コントラクトの登録と実行")
    steps = [("コントラクト\n（ビジネスロジック）", lighten(d.P.primary, 0.88), d.P.text),
             ("所有者の秘密鍵で\n電子署名", d.P.primary, "#FFFFFF"),
             ("Ledger が署名を検証", d.P.success, "#FFFFFF"),
             ("アセットの読み書きを実行", lighten(d.P.primary, 0.88), d.P.text)]
    bw = (W - 0.32 - 0.34 * 3) / 4
    for i, (nm, col, txt) in enumerate(steps):
        bx = X0 + 0.16 + i * (bw + 0.34)
        d.shape(bx, DY0 + 0.44, bw, 0.80, kind="ROUND_RECTANGLE", fill=col,
                stroke=None if txt == "#FFFFFF" else lighten(d.P.primary, 0.6),
                text=nm, size=8.5, bold=(txt == "#FFFFFF"), color=txt, line_spacing=110)
        if i < 3:
            d.arrow(bx + bw + 0.03, DY0 + 0.84, bx + bw + 0.31, DY0 + 0.84,
                    color=d.P.primary, weight=1.6)
    d.label(X0 + 0.16, DY0 + 1.32, W - 0.32, 0.24,
            "コントラクトは定義されたインターフェースを通じてのみアセットを読み書きする",
            size=8, align="CENTER", valign="TOP", color=d.P.muted)

    # 担保されること
    y = DY0 + 1.84
    pw = (W - 0.3) / 2
    zone(d, X0, y, pw, 0.98, "署名によって担保されること")
    for i, t in enumerate(["許可された当事者のみがコントラクトを実行できる",
                           "コントラクトへの悪意ある変更を検知できる"]):
        d.shape(X0 + 0.14, y + 0.34, pw - 0.28, 0.26, kind="ROUND_RECTANGLE",
                fill=lighten(d.P.success, 0.86), stroke=None, text="✓ " + t, size=8,
                color=darken(d.P.success, 0.45)) if i == 0 else \
            d.shape(X0 + 0.14, y + 0.64, pw - 0.28, 0.26, kind="ROUND_RECTANGLE",
                    fill=lighten(d.P.success, 0.86), stroke=None, text="✓ " + t, size=8,
                    color=darken(d.P.success, 0.45))

    rx = X0 + pw + 0.3
    zone(d, rx, y, pw, 0.98, "周辺の仕組み")
    d.label(rx + 0.14, y + 0.32, pw - 0.28, 0.60,
            "・鍵と証明書の管理：CA サーバ / CA クライアント\n"
            "・汎用コントラクト：典型的な操作は自前実装が不要",
            size=8, align="START", valign="TOP", color=d.P.text, line_spacing=125)

    y2 = y + 1.12
    d.shape(X0, y2, W, 0.34, kind="ROUND_RECTANGLE", fill="#F4F6F9",
            stroke=lighten(d.P.muted, 0.6),
            text="コントラクトと Function のライフサイクル管理（登録・更新）の手順もドキュメント化されている",
            size=8.5, color=d.P.text)

    foot(d, ["・署名対象がアプリのロジックそのものであるため、ロジックの差し替えによる不正も検知対象になる"],
         "エディション: Community / Enterprise ｜ 状況: GA")


@slide("Ledger と Auditor の相互検証が障害を露見させる",
       note="Auditor を Ledger と同じ管理下に置くと相互検証の意味が薄れます。運用主体の分離が設計上の要点です。")
def s_auditor(d):
    # 3フェーズ
    zone(d, X0, DY0, W, 1.86, "3 フェーズの流れ")
    ph = [("① Ordering", "Auditor", "競合解析に基づき\nトランザクションを事前順序付け", d.P.success),
          ("② Commit", "Ledger", "順序付けられたトランザクションを\n実行・コミット", d.P.primary),
          ("③ Validation", "Auditor", "Ledger の順序付けを検証し\n再実行する", d.P.success)]
    bw = (W - 0.32 - 0.40 * 2) / 3
    for i, (nm, who, body, col) in enumerate(ph):
        bx = X0 + 0.16 + i * (bw + 0.40)
        d.shape(bx, DY0 + 0.40, bw, 1.04, kind="ROUND_RECTANGLE", fill=lighten(col, 0.90),
                stroke=col, stroke_weight=1.1)
        d.shape(bx, DY0 + 0.40, bw, 0.30, kind="RECTANGLE", fill=col, stroke=None,
                text=f"{nm}（{who}）", size=8.5, bold=True, color="#FFFFFF")
        d.label(bx + 0.08, DY0 + 0.76, bw - 0.16, 0.60, body, size=8, align="CENTER",
                color=d.P.text, line_spacing=115)
        if i < 2:
            d.arrow(bx + bw + 0.04, DY0 + 0.92, bx + bw + 0.36, DY0 + 0.92,
                    color=d.P.primary, weight=1.6)
    d.label(X0 + 0.16, DY0 + 1.50, W - 0.32, 0.24,
            "両サーバが正直なら、同一の正しい（strict serializable な）状態に到達する",
            size=8.5, bold=True, align="CENTER", valign="TOP", color=d.P.primaryDark)

    # 検知の原理
    y = DY0 + 2.00
    lw = 5.60
    zone(d, X0, y, lw, 1.14, "いずれかがビザンチン障害を起こすと…")
    d.shape(X0 + 0.25, y + 0.42, 1.58, 0.46, kind="ROUND_RECTANGLE",
            fill=lighten(d.P.primary, 0.86), stroke=lighten(d.P.primary, 0.6),
            text="Ledger の状態", size=8, color=d.P.text)
    d.shape(X0 + 2.27, y + 0.42, 1.58, 0.46, kind="ROUND_RECTANGLE",
            fill=lighten(d.P.danger, 0.86), stroke=lighten(d.P.danger, 0.5),
            text="Auditor の状態", size=8, color=darken(d.P.danger, 0.25))
    # Fill the whole gap between the two boxes: ≠ is a full-width glyph, and
    # 0.34in leaves it less room than the margin a text frame carries
    d.label(X0 + 1.83, y + 0.50, 0.44, 0.30, "≠", size=13, bold=True, align="CENTER",
            valign="MIDDLE", color=d.P.danger)
    d.arrow(X0 + 3.87, y + 0.65, X0 + 4.15, y + 0.65, color=d.P.danger, weight=1.6)
    d.shape(X0 + 4.17, y + 0.42, 1.20, 0.46, kind="ROUND_RECTANGLE", fill=d.P.danger,
            stroke=None, text="応答が\n食い違う", size=8, bold=True, color="#FFFFFF",
            line_spacing=100)
    d.label(X0 + 0.25, y + 0.92, lw - 0.50, 0.20,
            "→ クライアントが食い違いとして障害を検知する", size=8, bold=True,
            align="START", valign="TOP", color=darken(d.P.danger, 0.25))

    rx = X0 + lw + 0.30
    rw = XE - rx
    zone(d, rx, y, rw, 1.14, "信頼の分離")
    d.label(rx + 0.14, y + 0.34, rw - 0.28, 0.74,
            "Ledger と Auditor を別ネットワーク /\n別管理主体に置くことで、\n"
            "相互検証の意味が強まる。\n（ネットワークピアリングの手順あり）",
            size=8, align="START", valign="TOP", color=d.P.text, line_spacing=118)

    foot(d, ["・Auditor は Enterprise 提供。同一管理下に置くと相互検証が形式的になるため、運用主体の分離が前提"],
         "エディション: Enterprise（Auditor）｜ 状況: GA")


@slide("HashStore はコントラクトを書かずに証跡を保全する",
       note="データ本体は外部に置いたまま、ハッシュだけを ScalarDL で守る構成が取れます。コンプライアンス対応に向きます。")
def s_hashstore(d):
    # 検知フロー
    zone(d, X0, DY0, W, 1.62, "改ざんの検知方式")
    d.shape(X0 + 0.30, DY0 + 0.44, 1.90, 0.62, kind="ROUND_RECTANGLE",
            fill=lighten(d.P.muted, 0.72), stroke=lighten(d.P.muted, 0.4),
            text="外部のオブジェクト\nファイル / 監査ログ / ディレクトリ", size=8,
            color=d.P.text, line_spacing=110)
    d.arrow(X0 + 2.22, DY0 + 0.75, X0 + 2.58, DY0 + 0.75, color=d.P.primary, weight=1.5)
    d.shape(X0 + 2.60, DY0 + 0.44, 1.55, 0.62, kind="ROUND_RECTANGLE",
            fill=lighten(d.P.primary, 0.88), stroke=lighten(d.P.primary, 0.6),
            text="ハッシュ値を計算", size=8.5, color=d.P.text)
    d.arrow(X0 + 4.17, DY0 + 0.75, X0 + 4.53, DY0 + 0.75, color=d.P.primary, weight=1.5)
    d.shape(X0 + 4.55, DY0 + 0.44, 1.80, 0.62, kind="ROUND_RECTANGLE", fill=d.P.primary,
            stroke=None, text="ScalarDL の台帳に\n耐改ざん・不変で記録", size=8, bold=True,
            color="#FFFFFF", line_spacing=110)
    d.arrow(X0 + 6.37, DY0 + 0.75, X0 + 6.73, DY0 + 0.75, color=d.P.danger, weight=1.5)
    d.shape(X0 + 6.75, DY0 + 0.44, 1.95, 0.62, kind="ROUND_RECTANGLE",
            fill=lighten(d.P.danger, 0.88), stroke=lighten(d.P.danger, 0.5),
            text="再計算した値と比較し\nfaulty_versions を特定", size=8,
            color=darken(d.P.danger, 0.25), line_spacing=110)
    d.label(X0 + 0.30, DY0 + 1.16, W - 0.60, 0.24,
            "データ本体は外部に置いたまま、ハッシュだけを ScalarDL で守れる（独自コントラクトの実装は不要）",
            size=8, align="CENTER", valign="TOP", color=d.P.muted)

    # 2つの管理対象 + API
    y = DY0 + 1.76
    pw = (W - 0.3) / 2
    zone(d, X0, y, pw, 1.56, "2 つの管理対象")
    for i, (nm, sub) in enumerate([("オブジェクトの真正性",
                                    "ファイル・監査ログ等のハッシュ値を記録"),
                                   ("コレクションの真正性",
                                    "どのオブジェクトが集合に属するかを管理し、不正な削除・改変を防ぐ")]):
        iy = y + 0.34 + i * 0.48
        d.shape(X0 + 0.14, iy, pw - 0.28, 0.44, kind="ROUND_RECTANGLE",
                fill=lighten(d.P.primary, 0.90), stroke=lighten(d.P.primary, 0.62))
        d.label(X0 + 0.24, iy + 0.03, pw - 0.48, 0.20, nm, size=8.5, bold=True,
                align="START", valign="TOP", color=d.P.primaryDark)
        d.label(X0 + 0.24, iy + 0.22, pw - 0.48, 0.20, sub, size=7, align="START",
                valign="TOP", color=d.P.text)

    rx = X0 + pw + 0.3
    zone(d, rx, y, pw, 1.56, "主な API")
    pills(d, rx + 0.14, y + 0.34, pw - 0.28,
          ["put-object", "get-object", "compare-object-versions",
           "create-collection", "add-to-collection", "remove-from-collection",
           "get-collection-history", "validate-ledger"],
          per_row=2, h=0.20, gap=0.05, size=7)
    d.label(rx + 0.14, y + 1.30, pw - 0.28, 0.22,
            "用途：監査証跡の保護 / ファイル完全性検証 / 証拠保全", size=7.5,
            align="START", valign="TOP", color=d.P.muted)

    foot(d, ["・低レベルな台帳抽象の上に載る高レベル抽象。デジタル証拠の保全をコントラクト実装なしで実現する"],
         "エディション: Community / Enterprise ｜ 状況: GA")


@slide("TableStore は SQL とリレーショナルモデルで書ける",
       note="既存のリレーショナル設計の知識を活かせるため、ScalarDL の導入障壁を下げる選択肢です。")
def s_tablestore(d):
    # SQL → 履歴
    zone(d, X0, DY0, W, 1.56, "SQL で操作し、変更履歴は台帳に積まれる")
    d.shape(X0 + 0.30, DY0 + 0.42, 2.10, 0.62, kind="ROUND_RECTANGLE",
            fill=lighten(d.P.primary, 0.88), stroke=lighten(d.P.primary, 0.6),
            text="SELECT / INSERT\nUPDATE / JOIN", size=8.5, color=d.P.text,
            line_spacing=110)
    d.arrow(X0 + 2.42, DY0 + 0.73, X0 + 2.78, DY0 + 0.73, color=d.P.primary, weight=1.5)
    d.shape(X0 + 2.80, DY0 + 0.42, 1.85, 0.62, kind="ROUND_RECTANGLE", fill=d.P.primary,
            stroke=None, text="TableStore", size=9.5, bold=True, color="#FFFFFF")
    d.arrow(X0 + 4.67, DY0 + 0.73, X0 + 5.03, DY0 + 0.73, color=d.P.primary, weight=1.5)
    # 履歴チェーン
    for i in range(3):
        hx = X0 + 5.05 + i * 1.28
        d.shape(hx, DY0 + 0.42, 1.10, 0.62, kind="ROUND_RECTANGLE",
                fill=lighten(d.P.success, 0.88), stroke=lighten(d.P.success, 0.5),
                text=f"版 {i + 1}\nJSON レコード", size=7.5,
                color=darken(d.P.success, 0.45), line_spacing=105)
        if i < 2:
            d.arrow(hx + 1.12, DY0 + 0.73, hx + 1.26, DY0 + 0.73,
                    color=d.P.success, weight=1.4)
    d.label(X0 + 5.05, DY0 + 1.10, 3.65, 0.24, "全変更の履歴を保持（レコード履歴を取得できる）",
            size=7.5, align="CENTER", valign="TOP", color=d.P.muted)

    # 機能
    y = DY0 + 1.64
    zone(d, X0, y, W, 1.06, "主な機能")
    feats = [("SQL インターフェース", "SELECT / INSERT / UPDATE / JOIN"),
             ("柔軟なスキーマ", "レコードは JSON。事前のカラム定義が不要"),
             ("監査証跡", "全変更の履歴を保持し履歴を取得できる"),
             ("セカンダリインデックス", "主キー / インデックスキーで取得"),
             ("データ検証", "validate-ledger で暗号学的に検証")]
    fw = (W - 0.28 - 0.12 * 4) / 5
    for i, (nm, sub) in enumerate(feats):
        fx = X0 + 0.14 + i * (fw + 0.12)
        d.shape(fx, y + 0.34, fw, 0.62, kind="ROUND_RECTANGLE",
                fill=lighten(d.P.primary, 0.92), stroke=lighten(d.P.primary, 0.65))
        d.label(fx + 0.06, y + 0.38, fw - 0.12, 0.24, nm, size=8, bold=True,
                align="CENTER", color=d.P.primaryDark, line_spacing=100)
        d.label(fx + 0.06, y + 0.62, fw - 0.12, 0.32, sub, size=7, align="CENTER",
                color=d.P.text, line_spacing=105)

    # HashStore との違い
    y2 = y + 1.18
    pw = (W - 0.3) / 2
    d.shape(X0, y2, pw, 0.58, kind="ROUND_RECTANGLE", fill=lighten(d.P.info, 0.88),
            stroke=lighten(d.P.info, 0.6))
    d.label(X0 + 0.12, y2 + 0.05, pw - 0.24, 0.50,
            "HashStore：ハッシュによる証跡保全に特化。\nデータ本体は外部に置く。",
            size=8, align="START", valign="TOP", color=darken(d.P.info, 0.35),
            line_spacing=120)
    d.shape(X0 + pw + 0.3, y2, pw, 0.58, kind="ROUND_RECTANGLE",
            fill=lighten(d.P.success, 0.86), stroke=lighten(d.P.success, 0.5))
    d.label(X0 + pw + 0.42, y2 + 0.05, pw - 0.24, 0.50,
            "TableStore：SQL による本格的なデータ管理まで\nカバーする。データ本体も台帳内に置く。",
            size=8, align="START", valign="TOP", color=darken(d.P.success, 0.45),
            line_spacing=120)

    foot(d, ["・用途：耐改ざんな記録管理、監査証跡のコンプライアンス対応、不変な履歴の保持"],
         "エディション: Community / Enterprise ｜ 状況: GA")


# =====================================================================
# 7. まとめ
# =====================================================================

plain(layout="SECTION", title="7. まとめ",
      body="製品の使い分けと次のステップ",
      notes="最後に整理します。")


@slide("目的が整合性・分析なら ScalarDB、真正性・監査なら ScalarDL",
       note="目的が「整合性・分析」なら ScalarDB、「真正性・監査」なら ScalarDL という整理が実務的です。")
def s_choice(d):
    pw = (W - 0.4) / 2
    # ScalarDB
    zone(d, X0, DY0, pw, 2.52, "ScalarDB を選ぶ場面", stroke=lighten(d.P.primary, 0.6))
    d.shape(X0 + 0.20, DY0 + 0.34, pw - 0.40, 0.34, kind="ROUND_RECTANGLE",
            fill=d.P.primary, stroke=None, text="整合性・鮮度・移植性の課題", size=9,
            bold=True, color="#FFFFFF")
    for i, t in enumerate(["複数 DB にまたがる更新の整合性を\nアプリで自作したくない",
                           "ETL を挟まずに現行データを\n横断分析したい（Analytics）",
                           "DB 移行やマルチクラウド構成で\nロックインを避けたい"]):
        d.shape(X0 + 0.20, DY0 + 0.76 + i * 0.52, pw - 0.40, 0.46,
                kind="ROUND_RECTANGLE", fill=lighten(d.P.primary, 0.90),
                stroke=lighten(d.P.primary, 0.62), text=t, size=8.5, color=d.P.text,
                line_spacing=110)
    d.label(X0 + 0.20, DY0 + 2.30, pw - 0.40, 0.22,
            "→ Core / Cluster / Analytics", size=8.5, bold=True, align="CENTER",
            color=d.P.primaryDark)

    # ScalarDL
    rx = X0 + pw + 0.4
    zone(d, rx, DY0, pw, 2.52, "ScalarDL を選ぶ場面", stroke=lighten(d.P.success, 0.5),
         fill="#F7FCF5")
    d.shape(rx + 0.20, DY0 + 0.34, pw - 0.40, 0.34, kind="ROUND_RECTANGLE",
            fill=d.P.success, stroke=None, text="真正性・監査の課題", size=9, bold=True,
            color="#FFFFFF")
    for i, t in enumerate(["改ざんや内部不正を、使われる前に\n検知できる状態にしたい",
                           "監査証跡・証拠保全に暗号学的な\n裏付けを持たせたい",
                           "運用主体を分離した相互検証\n（Ledger / Auditor）を成立させたい"]):
        d.shape(rx + 0.20, DY0 + 0.76 + i * 0.52, pw - 0.40, 0.46,
                kind="ROUND_RECTANGLE", fill=lighten(d.P.success, 0.90),
                stroke=lighten(d.P.success, 0.55), text=t, size=8.5, color=d.P.text,
                line_spacing=110)
    d.label(rx + 0.20, DY0 + 2.30, pw - 0.40, 0.22,
            "→ Ledger / Auditor / HashStore / TableStore", size=8.5, bold=True,
            align="CENTER", color=darken(d.P.success, 0.45))

    # 併用
    y = DY0 + 2.66
    d.shape(X0, y, W, 0.48, kind="ROUND_RECTANGLE", fill=lighten(d.P.primary, 0.90),
            stroke=lighten(d.P.primary, 0.62))
    d.label(X0 + 0.14, y + 0.04, W - 0.28, 0.40,
            "併用：両者は独立した製品であり、下位 DB を共有した構成も取りうる。\n"
            "Helm チャート・Scalar Manager・pause を用いたバックアップ運用は共通の枠組みで扱える。",
            size=8.5, align="START", valign="TOP", color=d.P.text, line_spacing=120)

    foot(d, ["・「整合性が欲しいのか、真正性が欲しいのか」を最初に切り分けると製品選定が早い"])


@slide("検証はスタンドアロン → ベンチマーク → 本番確認の順で進む",
       note="Private Preview 機能を前提にした設計は避け、GA 機能で成立する構成を基本線にしてください。")
def s_next(d):
    steps = [("スタンドアロンで動かす", "Cluster を起動し CRUD / SQL を実際に実行する"),
             ("データモデルを設計する", "対象 DB のアダプタと、実際のアクセスパターンに沿ったスキーマ"),
             ("分離レベルを決めて測る", "ベンチマークツールで設定差の影響を自環境で測定する"),
             ("必要機能とエディションを確認", "認証認可・暗号化・ABAC 等の提供状況（GA / Private Preview）"),
             ("Kubernetes に構築する", "Helm チャートで導入し、pause を含むバックアップ運用を設計"),
             ("チェックリストでレビュー", "コンポーネント別のプロダクションチェックリストで確認する")]
    pw = (W - 0.4) / 2
    for i, (h_, b_) in enumerate(steps):
        col_i, row_i = divmod(i, 3)
        sx = X0 + col_i * (pw + 0.4)
        sy = DY0 + 0.10 + row_i * 0.78
        d.shape(sx, sy, 0.42, 0.42, kind="ELLIPSE", fill=d.P.primary, stroke=None,
                text=str(i + 1), size=11, bold=True, color="#FFFFFF")
        d.shape(sx + 0.54, sy, pw - 0.54, 0.62, kind="ROUND_RECTANGLE",
                fill=lighten(d.P.primary, 0.92), stroke=lighten(d.P.primary, 0.65))
        d.label(sx + 0.68, sy + 0.05, pw - 0.82, 0.24, h_, size=9, bold=True,
                align="START", valign="TOP", color=d.P.primaryDark)
        d.label(sx + 0.68, sy + 0.28, pw - 0.82, 0.30, b_, size=7.5, align="START",
                valign="TOP", color=d.P.text, line_spacing=110)
        if row_i < 2:
            d.arrow(sx + 0.21, sy + 0.64, sx + 0.21, sy + 0.76, color=d.P.primary,
                    weight=1.4)
    # 3 → 4 の接続は列間の余白を通るエルボーで引く（本文の上を横切らせない）
    xg = X0 + pw + 0.20
    d.line(X0 + pw - 0.60, DY0 + 2.36, xg, DY0 + 2.36, color=d.P.primary, weight=1.3,
           dashed=True)
    d.line(xg, DY0 + 0.31, xg, DY0 + 2.36, color=d.P.primary, weight=1.3, dashed=True)
    d.arrow(xg, DY0 + 0.31, X0 + pw + 0.38, DY0 + 0.31, color=d.P.primary, weight=1.3)

    y = DY0 + 2.56
    d.shape(X0, y, W, 0.58, kind="ROUND_RECTANGLE", fill=lighten(d.P.warning, 0.76),
            stroke=lighten(d.P.warning, 0.5))
    d.label(X0 + 0.14, y + 0.06, W - 0.28, 0.48,
            "Private Preview 機能（ABAC / ベクトル検索 / リモートレプリケーション）を前提にした設計は避け、\n"
            "GA 機能で成立する構成を基本線に置く。",
            size=9, bold=True, align="START", valign="TOP", color=darken(d.P.warning, 0.55),
            line_spacing=120)

    foot(d, ["参照: https://developers.scalar-labs.com/　（ScalarDB / ScalarDL の各 latest ドキュメント）"])


plain(layout="CLOSING", notes="以上です。")
