#!/usr/bin/env python3
"""Scalar 製品機能紹介デッキ(1機能=1スライド・図解付き)。

developers.scalar-labs.com のドキュメント調査(2026-08-01)に基づき、各機能を
「図解 / 機能概要 / ユースケース / 特長」の共通レイアウトで並べる。
ScalarDB 15 機能 + ScalarDL 9 機能。
"""
from __future__ import annotations

import argparse
import os
import sys
from importlib.machinery import SourceFileLoader

SKILL_DIR = os.path.expanduser("~/.claude/skills/google-slides-template")
sys.path.insert(0, os.path.join(SKILL_DIR, "scripts"))

bd = SourceFileLoader("bd", os.path.join(SKILL_DIR, "scripts", "build-deck.py")).load_module()
from diagrams import Canvas, lighten  # noqa: E402

TEMPLATE = os.path.join(SKILL_DIR, "templates", "scalar-2026.json")

TITLE = "Scalar 製品機能のご紹介"
SUBTITLE = "ScalarDB / ScalarDL — 図解・機能概要・ユースケース・特長"
DATE = "2026年8月"

# 図解エリア(左)。全ミニ図はこの枠内に描く
FX, FY, FW, FH = 0.5, 0.98, 5.25, 2.32


# ---------------------------------------------------------------- 共通部品

def _pill(d: Canvas, x, y, w, h, text, accent, *, light=0.88, size=9,
          bold=False, color=None):
    """角丸の帯・チップ。"""
    return d.shape(x, y, w, h, kind="ROUND_RECTANGLE",
                   fill=lighten(accent, light), stroke=accent, text=text,
                   size=size, bold=bold, color=color or d.P.text,
                   line_spacing=112)


def _code(d: Canvas, x, y, w, h, text, *, size=8):
    """コード風の濃色チップ。"""
    return d.shape(x, y, w, h, kind="ROUND_RECTANGLE", fill=d.P.text,
                   stroke=None, text=text, size=size, color="#FFFFFF",
                   line_spacing=118)


def _caption(d: Canvas, text, *, y=None, size=8.5):
    """図解エリア下端の説明文。"""
    d.label(FX, y if y is not None else FY + FH - 0.26, FW, 0.24, text,
            size=size, align="CENTER", color=d.P.muted)


def _va(d: Canvas, x1, y1, x2, y2, color=None):
    d.arrow(x1, y1, x2, y2, color=color or d.P.muted, weight=1.0,
            _anchored=True)


# ---------------------------------------------------------------- ScalarDB 図解

def fig_db_acid(d, accent):
    d.icon("server", 1.35, FY + 0.02, 0.36, label="アプリケーション",
           label_size=8, label_w=1.6)
    _pill(d, 0.7, FY + 0.80, 3.4, 0.44, "ScalarDB — Consensus Commit",
          accent, size=9.5, bold=True)
    d.icon_row(0.9, FY + 1.42, 3.0, [("database", "MySQL"),
                                     ("stack", "DynamoDB")],
               size=0.32, label_size=8)
    _va(d, 1.53, FY + 0.68, 1.53, FY + 0.78)
    for cx in (1.65, 3.15):
        _va(d, cx, FY + 1.26, cx, FY + 1.40)
    d.label(4.35, FY + 0.55, 1.35, 0.95,
            "Prepare →\nCommit\n失敗時は\n自動復旧", size=8, align="START",
            color=d.P.muted, line_spacing=125)
    _caption(d, "1 つのトランザクションが複数 DB へ原子的に反映される")


def fig_db_multistorage(d, accent):
    d.icon("server", 1.35, FY + 0.02, 0.34, label="アプリ", label_size=8)
    _pill(d, 0.7, FY + 0.72, 3.4, 0.4, "統一 API（CRUD / SQL）", accent,
          size=9, bold=True)
    _pill(d, 0.8, FY + 1.34, 1.5, 0.32, "ns: orders", d.P.info, size=8)
    _pill(d, 2.7, FY + 1.34, 1.5, 0.32, "ns: items", d.P.info, size=8)
    d.icon("database", 1.38, FY + 1.84, 0.34, label="MySQL", label_size=7.5)
    d.icon("stack", 3.28, FY + 1.84, 0.34, label="Cassandra", label_size=7.5)
    _va(d, 1.52, FY + 0.60, 1.52, FY + 0.70)
    for cx in (1.55, 3.45):
        _va(d, cx, FY + 1.14, cx, FY + 1.32)
    d.label(4.4, FY + 0.9, 1.3, 0.7, "名前空間ごとに\n格納先を\n自動選択",
            size=8, align="START", color=d.P.muted, line_spacing=125)
    _caption(d, "異なる DB を 1 つの論理 DB として扱い、横断トランザクションも可能")


def fig_db_2pc(d, accent):
    d.cloud_zone(0.55, FY + 0.05, 2.3, 1.62, title="サービス A", title_size=8,
                 color=accent)
    d.cloud_zone(3.2, FY + 0.05, 2.3, 1.62, title="サービス B", title_size=8,
                 color=d.P.info)
    _pill(d, 0.78, FY + 0.5, 1.85, 0.62, "TX マネージャ\n(Coordinator)",
          accent, size=8)
    _pill(d, 3.43, FY + 0.5, 1.85, 0.62, "TX マネージャ\n(Participant)",
          d.P.info, size=8)
    d.line(2.68, FY + 0.81, 3.38, FY + 0.81, color=d.P.muted, weight=1.25,
           start_arrow="FILL_ARROW", end_arrow="FILL_ARROW", _anchored=True)
    d.label(2.28, FY + 0.42, 1.5, 0.22, "Prepare / Commit", size=7.5,
            align="CENTER", color=d.P.muted)
    _caption(d, "全サービスの成功で Commit、1 つでも失敗すれば全体を取り消す",
             y=FY + 1.86)


def fig_db_cluster(d, accent):
    d.icon_row(0.6, FY + 0.15, 2.0, [("browser", "Web"), ("mobile", "モバイル")],
               size=0.32, label_size=7.5)
    d.cloud_zone(2.95, FY + 0.05, 2.6, 1.78, title="Kubernetes", title_size=8)
    for i in range(3):
        _pill(d, 3.12 + i * 0.79, FY + 0.55, 0.72, 0.4, "Node", accent,
              size=8)
    d.label(3.1, FY + 1.15, 2.3, 0.4, "メンバーシップを自動調整\nHelm でデプロイ",
            size=7.5, align="CENTER", color=d.P.muted, line_spacing=120)
    _va(d, 2.62, FY + 0.5, 2.92, FY + 0.7)
    _caption(d, "コンシステントハッシングで最適なノードへ自動ルーティング",
             y=FY + 2.0)


def fig_db_sql(d, accent):
    _code(d, 0.6, FY + 0.1, 2.35, 0.95,
          "SELECT o.id, i.name\nFROM orders o\nJOIN items i ON …")
    _pill(d, 3.35, FY + 0.2, 2.05, 0.72, "ScalarDB Cluster\n(SQL)", accent,
          size=9, bold=True)
    _va(d, 3.0, FY + 0.57, 3.32, FY + 0.57)
    d.icon_row(3.55, FY + 1.3, 1.7, [("database", ""), ("stack", "")],
               size=0.32)
    _va(d, 4.38, FY + 0.94, 4.38, FY + 1.28)
    for i, t in enumerate(["JDBC", "Spring Data", "Java API"]):
        _pill(d, 0.62 + i * 0.83, FY + 1.32, 0.76, 0.3, t, accent, size=7,
              light=0.93)
    _caption(d, "標準 SQL の大規模なサブセットで異種 DB 横断トランザクション")


def fig_db_graphql(d, accent):
    _code(d, 0.6, FY + 0.1, 2.35, 1.05,
          "query {\n  order(id: 1) {\n    items { name }\n  }\n}", size=7.5)
    _pill(d, 3.35, FY + 0.2, 2.05, 0.85,
          "Cluster (GraphQL)\nスキーマ自動生成", accent, size=8.5, bold=True)
    _va(d, 3.0, FY + 0.62, 3.32, FY + 0.62)
    d.icon_row(3.55, FY + 1.35, 1.7, [("database", ""), ("stack", "")],
               size=0.32)
    _va(d, 4.38, FY + 1.07, 4.38, FY + 1.33)
    _caption(d, "ScalarDB のスキーマから GraphQL API を自動生成・2PC にも対応")


def fig_db_auth(d, accent):
    d.icon("person", 0.72, FY + 0.35, 0.4, label="ユーザー", label_size=8)
    d.icon("lock", 2.02, FY + 0.12, 0.26)
    _pill(d, 1.85, FY + 0.45, 2.55, 0.66,
          "認証 USERPASS / OIDC\n認可 GRANT + ロール", accent, size=8.5)
    _va(d, 1.32, FY + 0.72, 1.82, FY + 0.72)
    d.icon("database", 4.85, FY + 0.25, 0.34)
    d.icon("stack", 4.85, FY + 0.95, 0.34)
    _va(d, 4.43, FY + 0.72, 4.8, FY + 0.55)
    _va(d, 4.43, FY + 0.82, 4.8, FY + 1.05)
    _caption(d, "テーブル・名前空間単位の最小権限を異種 DB 全体で一元管理",
             y=FY + 1.85)


def fig_db_encrypt(d, accent):
    cols = [("氏名", 1.15, False), ("メール（ENCRYPTED）", 1.85, True),
            ("年齢", 0.85, False)]
    vals = ["山田", "0x8f3a…（BLOB）", "34"]
    x = 0.65
    for (head, w, enc), v in zip(cols, vals):
        c = d.P.danger if enc else d.P.muted
        d.shape(x, FY + 0.3, w, 0.36, kind="RECTANGLE",
                fill=lighten(c, 0.85 if enc else 0.92), stroke=c, text=head,
                size=7.5, bold=enc)
        d.shape(x, FY + 0.66, w, 0.36, kind="RECTANGLE", fill="#FFFFFF",
                stroke=c, text=v, size=7.5)
        x += w
    d.icon("lock", 2.6, FY - 0.02, 0.24, color=d.P.danger)
    d.icon("key", 4.85, FY + 0.3, 0.38, label="鍵管理\nVault / 自己管理",
           label_size=7.5, label_w=1.3)
    d.icon("database", 2.4, FY + 1.36, 0.34, label="暗号化された状態で保存",
           label_size=8, label_w=2.2)
    _va(d, 2.58, FY + 1.04, 2.58, FY + 1.34)
    _caption(d, "アプリからは透過的に暗号化・復号（TDE と同じ使い勝手）")


def fig_db_abac(d, accent):
    d.icon("person", 0.75, FY + 0.55, 0.4, label="属性: 営業部", label_size=8,
           label_w=1.4)
    rows = [("注文 1001　tag: 営業部", True), ("注文 1002　tag: 人事部", False),
            ("注文 1003　tag: 営業部", True)]
    for i, (t, ok) in enumerate(rows):
        y = FY + 0.15 + i * 0.52
        d.shape(2.3, y, 2.4, 0.4, kind="RECTANGLE",
                fill=d.P.surface if ok else lighten(d.P.muted, 0.8),
                stroke=d.P.border, text=t, size=8,
                color=d.P.text if ok else d.P.muted)
        c = d.P.success if ok else d.P.danger
        _pill(d, 4.82, y + 0.04, 0.6, 0.32, "可" if ok else "不可", c,
              size=8, bold=True, color=c)
    _caption(d, "ユーザー属性とレコードのタグが一致した行だけにアクセス可能")


def fig_db_vector(d, accent):
    d.icon("document", 0.72, FY + 0.2, 0.38, label="文書", label_size=8)
    _pill(d, 1.75, FY + 0.22, 1.65, 0.62, "埋め込み生成\nBedrock / OpenAI…",
          accent, size=8)
    _pill(d, 3.75, FY + 0.22, 1.65, 0.62, "ScalarDB\n統一 API", accent,
          size=8.5, bold=True)
    _va(d, 1.32, FY + 0.5, 1.72, FY + 0.5)
    _va(d, 3.43, FY + 0.5, 3.72, FY + 0.5)
    for i, t in enumerate(["OpenSearch", "pgvector", "Azure AI Search"]):
        _pill(d, 0.8 + i * 1.62, FY + 1.42, 1.5, 0.34, t, d.P.info, size=7.5)
    _va(d, 4.58, FY + 0.86, 3.0, FY + 1.4)
    _caption(d, "ストアを差し替えてもアプリのコードは変わらない")


def fig_db_nontx(d, accent):
    d.icon("server", 0.72, FY + 0.62, 0.4, label="アプリ", label_size=8)
    _pill(d, 1.95, FY + 0.18, 2.85, 0.5, "ACID トランザクション（一貫性）",
          accent, size=8.5)
    _pill(d, 1.95, FY + 1.08, 2.85, 0.5, "非トランザクショナル（高速）",
          d.P.info, size=8.5)
    _va(d, 1.32, FY + 0.75, 1.92, FY + 0.45)
    _va(d, 1.32, FY + 0.95, 1.92, FY + 1.3)
    d.icon("database", 5.0, FY + 0.62, 0.4, label="同じ DB", label_size=7.5)
    _va(d, 4.83, FY + 0.45, 4.97, FY + 0.7)
    _va(d, 4.83, FY + 1.3, 4.97, FY + 0.95)
    _caption(d, "ワークロードごとに「保証」と「性能」のバランスを選択できる")


def fig_db_repl(d, accent):
    d.cloud_zone(0.55, FY + 0.05, 2.3, 1.72, title="プライマリサイト",
                 title_size=8, color=accent)
    _pill(d, 0.75, FY + 0.5, 1.9, 0.4, "ScalarDB + LogWriter", accent, size=8)
    d.icon("database", 1.5, FY + 1.05, 0.34)
    d.cloud_zone(3.25, FY + 0.05, 2.3, 1.72, title="バックアップサイト",
                 title_size=8, color=d.P.info)
    _pill(d, 3.45, FY + 0.5, 1.9, 0.4, "LogApplier", d.P.info, size=8)
    d.icon("database", 4.2, FY + 1.05, 0.34)
    _va(d, 2.68, FY + 0.7, 3.42, FY + 0.7)
    _caption(d, "同期記録 → 非同期適用。確定分のデータロスはゼロ（RPO 0）",
             y=FY + 1.95)


def fig_db_analytics(d, accent):
    d.icon("person", 0.72, FY, 0.34, label="アナリスト", label_size=7.5,
           label_w=1.0)
    _pill(d, 1.75, FY + 0.08, 1.2, 0.32, "Spark SQL", accent, size=8)
    _pill(d, 0.7, FY + 0.78, 4.4, 0.44,
          "ScalarDB Analytics — 統合カタログ + Spark", accent, size=9,
          bold=True)
    d.icon_row(0.85, FY + 1.52, 4.1, [("database", "PostgreSQL"),
                                      ("stack", "Cassandra"),
                                      ("database", "MySQL")],
               size=0.34, label_size=7.5)
    _va(d, 1.7, FY + 0.42, 1.9, FY + 0.76)
    for cx in (1.53, 2.9, 4.27):
        _va(d, cx, FY + 1.24, cx, FY + 1.5)
    _caption(d, "ETL なし・データ移動なしで複数 DB を横断 JOIN")


def fig_db_mcp(d, accent):
    d.icon("bot", 0.75, FY + 0.05, 0.4, label="LLM / エージェント",
           label_size=8, label_w=1.7)
    _pill(d, 2.1, FY + 0.12, 3.25, 0.44, "MCP Server — SQL / CRUD ツール",
          accent, size=8.5, bold=True)
    _pill(d, 2.1, FY + 0.92, 3.25, 0.4, "ScalarDB（ACID 保証）", accent,
          size=8.5)
    d.icon_row(2.75, FY + 1.44, 2.0, [("database", "PostgreSQL"),
                                     ("stack", "DynamoDB")],
               size=0.28, label_size=7)
    _va(d, 1.6, FY + 0.34, 2.07, FY + 0.34)
    _va(d, 3.72, FY + 0.58, 3.72, FY + 0.9)
    _va(d, 3.72, FY + 1.34, 3.72, FY + 1.42)
    _caption(d, "自然言語からの操作でもデータ整合性が壊れない")


def fig_db_import(d, accent):
    d.icon("database", 0.9, FY + 0.45, 0.44, label="既存 DB（稼働中）",
           label_size=8, label_w=1.7)
    d.label(1.05, FY + 0.12, 1.9, 0.22, "--import（数秒）", size=7.5,
            align="CENTER", color=d.P.muted)
    _va(d, 1.85, FY + 0.67, 3.02, FY + 0.67)
    d.cloud_zone(3.05, FY + 0.05, 2.5, 1.95, title="ScalarDB 管理下",
                 title_size=8, color=accent)
    d.icon("database", 3.95, FY + 0.45, 0.44)
    _pill(d, 3.25, FY + 1.2, 2.1, 0.56, "トランザクション用の\nメタデータ列を自動追加",
          accent, size=7.5)
    _caption(d, "データ移行なし・アプリ停止なしで横断トランザクションの対象に")


# ---------------------------------------------------------------- ScalarDL 図解

def fig_dl_bft(d, accent):
    d.icon("browser", 2.72, FY - 0.02, 0.34, label="クライアント",
           label_size=8, label_w=1.3)
    d.cloud_zone(0.55, FY + 0.68, 2.25, 1.3, title="管理ドメイン A",
                 title_size=8, color=d.P.primary)
    _pill(d, 0.75, FY + 1.1, 1.85, 0.4, "Ledger", d.P.primary, size=9,
          bold=True)
    d.cloud_zone(3.25, FY + 0.68, 2.25, 1.3, title="管理ドメイン B",
                 title_size=8, color=accent)
    _pill(d, 3.45, FY + 1.1, 1.85, 0.4, "Auditor", accent, size=9, bold=True)
    _va(d, 2.6, FY + 0.42, 1.9, FY + 0.66)
    _va(d, 3.2, FY + 0.42, 3.9, FY + 0.66)
    d.line(2.63, FY + 1.3, 3.42, FY + 1.3, color=d.P.danger, weight=1.5,
           start_arrow="FILL_ARROW", end_arrow="FILL_ARROW", _anchored=True)
    _caption(d, "両者の応答をクライアントが突き合わせ、不一致＝改ざんを検知",
             y=FY + 2.06)


def fig_dl_ledger(d, accent):
    d.icon("stack", 0.62, FY + 0.35, 0.34, label="アセット", label_size=7.5)
    for i in range(3):
        _pill(d, 1.5 + i * 1.16, FY + 0.4, 1.0, 0.56, f"age {i}", accent,
              size=8.5, bold=True)
        if i < 2:
            _va(d, 2.53 + i * 1.16, FY + 0.68, 2.63 + i * 1.16, FY + 0.68,
                color=accent)
    d.shape(4.98, FY + 0.4, 0.55, 0.56, kind="ROUND_RECTANGLE",
            fill="#FFFFFF", stroke=accent, text="put", size=8, dash="DASH",
            color=d.P.muted)
    _va(d, 4.88, FY + 0.68, 4.95, FY + 0.68, color=accent)
    d.label(1.5, FY + 1.1, 3.5, 0.22, "各レコードは前のレコードのハッシュを含む",
            size=7.5, align="CENTER", color=d.P.muted)
    d.label(1.5, FY + 1.5, 3.5, 0.3, "追記のみ（更新・削除は不可）", size=8.5,
            align="CENTER", color=d.P.text, bold=True)
    _caption(d, "途中を書き換えるとチェーンが切れ、走査で必ず発覚する")


def fig_dl_auditor(d, accent):
    d.flow(0.6, FY + 0.35, 4.9, 0.72, [
        "① Ordering\nAuditor が順序付け",
        "② Commit\nLedger が実行",
        "③ Validation\nAuditor が検証",
    ], size=7.5)
    d.label(0.6, FY + 1.35, 4.9, 0.24,
            "両者が正直なら同一状態に収束、乖離すれば改ざんを検知", size=8.5,
            align="CENTER", color=d.P.text)
    d.label(0.6, FY + 1.7, 4.9, 0.22,
            "validateLedger が不整合時に INCONSISTENT_STATES を返す",
            size=7.5, align="CENTER", color=d.P.muted)
    _caption(d, "Ledger 管理者すら不正できない第三者検証の仕組み")


def fig_dl_contract(d, accent):
    d.icon("code", 0.75, FY + 0.1, 0.4, label="Java Contract", label_size=8,
           label_w=1.5)
    d.icon("key", 0.78, FY + 1.15, 0.36, label="所有者の秘密鍵",
           label_size=7.5, label_w=1.5)
    _pill(d, 2.25, FY + 0.62, 1.95, 0.52, "署名付きで\n登録・実行", accent,
          size=8.5)
    _pill(d, 4.55, FY + 0.62, 1.0, 0.52, "Ledger", accent, size=9, bold=True)
    _va(d, 1.4, FY + 0.45, 2.2, FY + 0.75)
    _va(d, 1.4, FY + 1.3, 2.2, FY + 1.0)
    _va(d, 4.23, FY + 0.88, 4.52, FY + 0.88)
    _caption(d, "署名が一致する所有者だけが実行でき、ロジックの改ざんも検知")


def fig_dl_function(d, accent):
    _pill(d, 0.7, FY + 0.25, 2.2, 0.7, "Contract\n台帳（不変・証跡）", accent,
          size=8.5, bold=True)
    _pill(d, 3.1, FY + 0.25, 2.2, 0.7, "Function\n業務データ（可変）",
          d.P.info, size=8.5, bold=True)
    _pill(d, 0.7, FY + 1.35, 4.6, 0.5,
          "1 つの ACID トランザクションで原子的に実行（ScalarDB）",
          d.P.primary, size=8.5)
    _va(d, 1.8, FY + 0.97, 1.8, FY + 1.33)
    _va(d, 4.2, FY + 0.97, 4.2, FY + 1.33)
    _caption(d, "決済の例: 取引証跡（Contract）と残高（Function）がズレない")


def fig_dl_table(d, accent):
    _code(d, 0.6, FY + 0.1, 2.3, 1.0,
          "CREATE TABLE …\nSELECT … JOIN …\nSELECT history(…)")
    _pill(d, 3.2, FY + 0.18, 2.3, 0.72,
          "事前定義コントラクト\n（bootstrap で自動登録）", accent, size=8)
    _pill(d, 3.6, FY + 1.35, 1.5, 0.42, "Ledger", accent, size=9, bold=True)
    _va(d, 2.95, FY + 0.55, 3.17, FY + 0.55)
    _va(d, 4.35, FY + 0.92, 4.35, FY + 1.33)
    _caption(d, "SQL だけで改ざん検知テーブル — コントラクト開発はゼロ")


def fig_dl_hash(d, accent):
    d.icon("document", 0.75, FY + 0.08, 0.36, label="ファイル・ログ",
           label_size=7.5, label_w=1.5)
    _pill(d, 2.3, FY + 0.15, 1.8, 0.5, "ハッシュ値のみ格納", accent, size=8.5)
    _pill(d, 4.45, FY + 0.15, 1.05, 0.5, "Ledger", accent, size=9, bold=True)
    d.label(1.35, FY + 0.02, 1.0, 0.2, "ハッシュ化", size=7, align="CENTER",
            color=d.P.muted)
    _va(d, 1.4, FY + 0.4, 2.27, FY + 0.4)
    _va(d, 4.13, FY + 0.4, 4.42, FY + 0.4)
    d.icon("documents", 0.75, FY + 1.25, 0.36, label="コレクション（集合）",
           label_size=7.5, label_w=1.7)
    d.label(2.3, FY + 1.35, 3.2, 0.4, "追加・除去の履歴も台帳で管理し、\n不正な差し替えを検知",
            size=8, align="START", color=d.P.text, line_spacing=120)
    _caption(d, "実データを預けずに証拠保全 — 大容量ファイルにも適用できる")


def fig_dl_ns(d, accent):
    d.cloud_zone(0.6, FY + 0.05, 4.9, 1.85, title="ScalarDL Ledger（1 デプロイ）",
                 title_size=8.5, color=accent)
    for i, t in enumerate(["tenant-a", "tenant-b"]):
        zx = 0.85 + i * 2.32
        d.cloud_zone(zx, FY + 0.5, 2.1, 1.2, title=f"namespace: {t}",
                     title_size=7.5, color=d.P.info)
        d.icon("person", zx + 0.85, FY + 0.85, 0.32,
               label=f"テナント {'AB'[i]}", label_size=7.5, label_w=1.1)
    _caption(d, "Restricted access なら相互アクセスを完全に遮断できる",
             y=FY + 2.06)


def fig_dl_proof(d, accent):
    _pill(d, 0.7, FY + 0.45, 1.5, 0.5, "Ledger", accent, size=9, bold=True)
    _pill(d, 2.55, FY + 0.35, 1.75, 0.7, "Asset Proof\nハッシュ + 署名",
          accent, size=8.5)
    d.icon("person", 4.75, FY + 0.35, 0.4, label="クライアントの\n手元に保全",
           label_size=7.5, label_w=1.4)
    _va(d, 2.23, FY + 0.7, 2.52, FY + 0.7)
    _va(d, 4.33, FY + 0.7, 4.7, FY + 0.7)
    d.label(0.7, FY + 1.55, 4.6, 0.3, "実行のたびに「実行時点の証拠」が発行される",
            size=8.5, align="CENTER", color=d.P.text)
    _caption(d, "後から Ledger 側を書き換えても、手元の証拠との乖離で検知")


# ---------------------------------------------------------------- レイアウト

def draw_feature(d: Canvas, f: dict, accent) -> None:
    """機能スライド共通: 左=図解 / 右=機能概要 / 下=ユースケース + 特長。"""
    if f.get("edition"):
        d.label(5.0, 0.60, 4.5, 0.26, f["edition"], size=9, align="END",
                color=d.P.muted)
    f["figure"](d, accent)

    x, y, w, h = 6.0, FY, 3.5, FH
    d.shape(x, y, w, h, kind="RECTANGLE", fill=d.P.surface,
            stroke=d.P.border)
    d.shape(x, y, w, 0.06, kind="RECTANGLE", fill=accent, stroke=None)
    d.label(x + 0.16, y + 0.13, 3.2, 0.28, "機能概要", size=10.5, bold=True,
            align="START", color=accent)
    d.label(x + 0.16, y + 0.48, 3.18, h - 0.6, f["overview"], size=9.5,
            align="START", color=d.P.text, line_spacing=130)

    uy = 3.44
    d.shape(0.5, uy, 9.0, 0.82, kind="RECTANGLE", fill=d.P.surface,
            stroke=d.P.border)
    d.shape(0.5, uy, 0.06, 0.82, kind="RECTANGLE", fill=accent, stroke=None)
    d.label(0.68, uy, 1.25, 0.82, "ユース\nケース", size=10, bold=True,
            align="START", valign="MIDDLE", color=accent, line_spacing=115)
    us = f["usecases"]
    half = (len(us) + 1) // 2
    for i, col in enumerate([us[:half], us[half:]]):
        if col:
            d.label(2.0 + i * 3.7, uy + 0.10, 3.55, 0.66,
                    "\n".join(f"・{u}" for u in col), size=9, align="START",
                    valign="MIDDLE", color=d.P.text, line_spacing=128)

    vy = 4.40
    d.shape(0.5, vy, 9.0, 0.62, kind="RECTANGLE",
            fill=lighten(accent, 0.9), stroke=lighten(accent, 0.5))
    d.label(0.68, vy, 1.5, 0.62, "特長", size=10, bold=True,
            align="START", valign="MIDDLE", color=accent)
    d.label(2.3, vy + 0.05, 7.0, 0.52, f["value"], size=9.5, align="START",
            valign="MIDDLE", color=d.P.text, line_spacing=122)


def draw_feature_map(d: Canvas, groups, accent) -> None:
    """機能マップ: 2×2 のグループカード。"""
    for i, (head, items) in enumerate(groups):
        gx = 0.5 + (i % 2) * 4.61
        gy = 1.0 + (i // 2) * 2.0
        d.shape(gx, gy, 4.39, 1.85, kind="RECTANGLE",
                fill=d.P.surface, stroke=d.P.border)
        d.shape(gx, gy, 4.39, 0.06, kind="RECTANGLE", fill=accent, stroke=None)
        d.label(gx + 0.16, gy + 0.13, 4.05, 0.28, head, size=11, bold=True,
                align="START", color=accent)
        d.label(gx + 0.16, gy + 0.48, 4.07, 1.3,
                "\n".join(f"・{x}" for x in items), size=9.5, align="START",
                color=d.P.text, line_spacing=128)


# ---------------------------------------------------------------- ScalarDB

DB_DOCS = "https://scalardb.scalar-labs.com/docs/latest/"

FEATURES_DB = [
    dict(title="ACID トランザクション — あらゆる DB に同じ保証を",
         figure=fig_db_acid,
         overview="独自の分散トランザクションプロトコル「Consensus Commit」により、下位 DB の"
                  "トランザクション機能に依存せず ACID を保証。楽観的並行性制御と準備→コミットの"
                  "2 フェーズ構造で動作し、障害時は遅延リカバリで自動復旧する。分離レベルは"
                  "SNAPSHOT / SERIALIZABLE 等を選択可能。",
         usecases=["Cassandra・DynamoDB 等への ACID 付与",
                   "複数 DB にまたがる一貫した更新",
                   "マイクロサービス間のデータ一貫性"],
         value="DB 側の機能に頼らず ScalarDB 層で ACID を実現。NoSQL を含む対応 DB すべてで同一のトランザクション保証が得られる。",
         edition="全エディション（Community 〜）",
         notes=f"出典: {DB_DOCS}consensus-commit/ 最適化: 並列実行・非同期コミット・ワンフェーズコミット（3.16+、3.18 で拡張）・グループコミット。"),
    dict(title="マルチストレージ — 異種 DB を 1 つの DB のように",
         figure=fig_db_multistorage,
         overview="ストレージ抽象化層と DB ごとのアダプタにより、異種 DB を単一 API で操作する。"
                  "名前空間→ストレージのマッピングを設定すると操作対象に応じて DB が自動選択され、"
                  "複数 DB にまたがる 1 つのトランザクションを ACID で実行できる。",
         usecases=["サイロ化した複数 DB の統一管理",
                   "異種 DB 間の一貫性維持",
                   "データメッシュの簡素化",
                   "アプリのポータブル化・DB 移行"],
         value="DB ごとの API・整合性モデルの違いをアプリから隠蔽。読み取り中心のフェデレーションと異なり、書き込みトランザクションまで横断対応。",
         edition="全エディション（Core 機能）",
         notes=f"出典: {DB_DOCS}multi-storage-transactions/ , {DB_DOCS}overview/"),
    dict(title="マイクロサービストランザクション — Saga を自作しない",
         figure=fig_db_2pc,
         overview="2 フェーズコミットインターフェースにより、複数のサービスがそれぞれトランザクション"
                  "マネージャを持ち、Coordinator（begin）と Participant（join）が Prepare → Validate → "
                  "Commit を協調実行する。サービスをまたぐ更新を ACID で保証する。",
         usecases=["database-per-service 構成の整合性",
                   "独立運用サービス間のデータ更新",
                   "GraphQL / Cluster 経由でも利用可"],
         value="Saga や TCC の独自実装・補償ロジックの作り込みが不要になり、分散システムでも単一 DB と同じ感覚でトランザクションを書ける。",
         edition="全エディション",
         notes=f"出典: {DB_DOCS}two-phase-commit-transactions/"),
    dict(title="ScalarDB Cluster — エンタープライズ運用の中核",
         figure=fig_db_cluster,
         overview="ScalarDB 機能を提供するクラスタノード群。各ノードがコンシステントハッシングで"
                  "リクエストを適切なノードへルーティングし、ノードの参加・離脱時は Kubernetes API で"
                  "メンバーシップを自動調整する。Helm Chart でデプロイし Kubernetes 上で稼働。",
         usecases=["本番環境のスケールアウト・高可用",
                   "複数リクエストにまたがる処理",
                   ".NET や gRPC など多言語の入口"],
         value="ライブラリ組み込み型（Core）では難しいスケーラビリティ・可用性・多言語アクセス・サーバー側機能（認証・暗号化等）を提供する。",
         edition="Enterprise Standard 以上",
         notes=f"出典: {DB_DOCS}scalardb-cluster/"),
    dict(title="SQL インターフェース — 使い慣れた SQL・JDBC で",
         figure=fig_db_sql,
         overview="SQL で ScalarDB Cluster と通信できるインターフェース層。標準 SQL の大規模な"
                  "サブセットをサポートし、JDBC・Java SQL API・Spring Data JDBC の 3 形態を提供する。"
                  "3.18 では executeBatch API や Spring Boot 4 対応が追加された。",
         usecases=["既存 JDBC アプリからの接続",
                   "Spring エコシステムでの開発",
                   "SQL に慣れた開発者の新規開発"],
         value="独自 Java API を学ばずに、使い慣れた SQL / JDBC / Spring の流儀で異種 DB 横断トランザクションを利用できる。",
         edition="Enterprise Premium",
         notes=f"出典: {DB_DOCS}scalardb-sql/ ※標準 SQL と完全互換ではない点に注意。"),
    dict(title="GraphQL インターフェース — API を自動生成する",
         figure=fig_db_graphql,
         overview="GraphQL で ScalarDB Cluster と通信するインターフェース層。ScalarDB のスキーマから"
                  "GraphQL スキーマを自動生成し、CRUD 操作と複数 DB にまたがるトランザクションを"
                  "GraphQL 経由で実行できる。2 フェーズコミットにも対応する。",
         usecases=["フロントエンド向け統一クエリ",
                   "型安全なバックエンド API",
                   "マルチプロセストランザクション"],
         value="型安全で柔軟なデータ取得という GraphQL の利点とトランザクション管理を両立し、スキーマ自動生成で API 実装工数を削減する。",
         edition="Enterprise Premium",
         notes=f"出典: {DB_DOCS}scalardb-graphql/"),
    dict(title="認証・認可 — 異種 DB のアクセス統制を一元化",
         figure=fig_db_auth,
         overview="Cluster のユーザー認証と権限管理を提供。認証は USERPASS と OIDC（Keycloak 等の"
                  "JWT、3.18 で追加）の 2 方式。認可は 9 種の権限（SELECT / INSERT / GRANT 等）を"
                  "名前空間・テーブル単位で付与でき、階層対応のロールで一括管理できる。",
         usecases=["共有データ基盤のアクセス統制",
                   "テーブル単位の最小権限運用",
                   "OIDC で既存 IdP と統合"],
         value="異種 DB ごとにバラバラだった認証・権限管理を ScalarDB 層で一元化できる。",
         edition="Enterprise Standard 以上　※OIDC は 3.18+",
         notes=f"出典: {DB_DOCS}scalardb-cluster/scalardb-auth-with-sql/ ※エディションは features 表（Standard 以上）準拠。個別ページに Premium タグあり要確認。"),
    dict(title="保存時暗号化 — DB を問わず同じポリシーを適用",
         figure=fig_db_encrypt,
         overview="カラムレベルの透過的暗号化。ENCRYPTED を指定したカラムをアプリに意識させず"
                  "暗号化・復号する。鍵管理は HashiCorp Vault への委譲と、ScalarDB 自身が DEK を"
                  "管理する自己暗号化（AES256_GCM 等）の 2 方式から選べる。",
         usecases=["個人情報・機微情報カラムの保護",
                   "TDE がない DB での規制対応",
                   "Vault による全社鍵管理へ統合"],
         value="DB 製品ごとの暗号化機能の差異に依存せず、異種 DB 全体で一貫したカラム暗号化ポリシーを適用できる。",
         edition="Enterprise Premium / 3.14+",
         notes=f"出典: {DB_DOCS}scalardb-cluster/encrypt-data-at-rest/ 制限: 主キー・インデックス・WHERE/ORDER BY 対象カラムは暗号化不可。"),
    dict(title="ABAC — 行レベルの細粒度アクセス制御",
         figure=fig_db_abac,
         overview="テーブル単位ではなくレコード（行）単位のアクセス制御。ユーザーの属性とレコードの"
                  "属性（タグ）のマッチングでアクセス可否を判定する。ストアドプロシージャのような"
                  "コードを書かず、タグの設定だけで行レベル制御を実現する。",
         usecases=["統合データ基盤のきめ細かい統制",
                   "行単位で見せ分けるマルチテナント"],
         value="行レベルセキュリティを DB 実装非依存・設定ベースで実現し、複雑な独自実装を排除する。",
         edition="Enterprise Premium オプション / 3.15+　※プライベートプレビュー",
         notes=f"出典: {DB_DOCS}scalardb-cluster/authorize-with-abac/ ※現在は日本の顧客向けプライベートプレビュー。"),
    dict(title="ベクトル検索 — AI アプリのストアを抽象化",
         figure=fig_db_vector,
         overview="複数のベクトルストアを抽象化し、統一 API で埋め込みの格納・検索を行える"
                  "（実装は LangChain4j を活用）。OpenSearch・Azure AI Search・pgvector 等のストアと、"
                  "Bedrock・Azure OpenAI・Vertex AI・OpenAI 等の埋め込みモデルに対応。",
         usecases=["RAG による LLM への知識注入",
                   "ストアにロックインされない開発"],
         value="トランザクショナルデータと同じ「統一インターフェース」の思想でベクトルストアも抽象化し、ストアの乗り換え・混在を容易にする。",
         edition="Enterprise Premium / 3.15+　※パブリックプレビュー",
         notes=f"出典: {DB_DOCS}scalardb-cluster/getting-started-with-vector-search/"),
    dict(title="非トランザクショナル操作 — 性能と一貫性を選べる",
         figure=fig_db_nontx,
         overview="複数操作にまたがる ACID 保証を外す代わりに、より高い性能で異種 DB への統一 CRUD を"
                  "実行する。CRUD インターフェース（Core）、SQL インターフェース（Cluster）、"
                  "Storage API（Primitive CRUD）の 3 つの実行手段を提供する。",
         usecases=["スループット最優先の処理",
                   "統一アクセスだけ使いたいアプリ",
                   "移行・バッチの単純 CRUD"],
         value="統一インターフェースの恩恵をトランザクションのオーバーヘッドなしで享受でき、ワークロードごとにトレードオフを選択できる。",
         edition="Enterprise Standard 以上 / 3.14+",
         notes=f"出典: {DB_DOCS}develop-run-non-transactional-operations-overview/"),
    dict(title="リモートレプリケーション — 異種 DB 環境を RPO=0 で守る",
         figure=fig_db_repl,
         overview="プライマリからバックアップサイトへの同期+非同期ハイブリッドレプリケーション。"
                  "トランザクション確定時に LogWriter が書き込みを同期記録し（確定分のデータロス"
                  "ゼロ = RPO 0）、バックアップ側の LogApplier が依存関係を計算して非同期適用する。",
         usecases=["災害復旧（フェイルオーバー）",
                   "クラウド・リージョン間の分散",
                   "バックアップ側で分析・BI"],
         value="DB 製品ごとのレプリケーション機能に依存せず、異種 DB 混在環境の全体を RPO=0 で DR 保護できる。",
         edition="Enterprise Premium / 3.16+　※プライベートプレビュー",
         notes=f"出典: {DB_DOCS}scalardb-cluster/remote-replication/ 制限: 複数バックアップ未対応、DDL 非複製、2PC・ワンフェーズコミット最適化と併用不可。"),
    dict(title="ScalarDB Analytics — ETL レスの横断分析",
         figure=fig_db_analytics,
         overview="異種データソース横断のフェデレーテッド分析エンジン。Analytics サーバーが全データ"
                  "ソースのメタデータをカタログとして統合管理し、実行エンジンに Apache Spark を使用。"
                  "ScalarDB 管理下の DB と管理外の DB の両方を、データを移動せずに結合できる。",
         usecases=["複数 DB 横断のビジネス分析",
                   "運用 DB へのリアルタイム分析",
                   "ETL レスのデータ統合ビュー"],
         value="ETL パイプラインを構築することなく、トランザクション整合性を保った最新データへ横断的に分析クエリを投げられる。",
         edition="Analytics ライセンス / 3.14+",
         notes=f"出典: {DB_DOCS}scalardb-analytics/quickstart/ 管理外 DB のデータソース化は 3.15+。"),
    dict(title="MCP Server — LLM から安全にデータへ",
         figure=fig_db_mcp,
         overview="LLM が ScalarDB 経由でデータへアクセス・管理できる Model Context Protocol 実装。"
                  "SQL モードと CRUD モードのツール群（スキーマ管理・トランザクション制御を含む）を"
                  "提供し、複数操作のグループ化時は ACID トランザクションで全成功／全失敗を保証。",
         usecases=["自然言語での異種 DB 問い合わせ",
                   "AI エージェントの安全なデータ操作"],
         value="単一の MCP サーバーで異種 DB 群を LLM に開放でき、LLM による操作でもデータ整合性が壊れない点が差別化。",
         edition="全エディション（MCP Server 0.9.x / ScalarDB 3.16+）",
         notes=f"出典: {DB_DOCS}scalardb-mcp-server/getting-started-with-scalardb-mcp-server/ 現在は STDIO（ローカル）のみ。"),
    dict(title="既存テーブルのインポート — 既存 DB を止めずに取り込む",
         figure=fig_db_import,
         overview="Schema Loader の --import オプションで、既存 JDBC データベースのテーブルを"
                  "データ移行なしに ScalarDB 管理下へ取り込む。トランザクション用メタデータが"
                  "自動追加され、処理は数秒で DB サイズに比例しない。MySQL・PostgreSQL・Oracle・"
                  "SQL Server・Db2・Spanner 等に対応。",
         usecases=["稼働中 DB の無停止での組み込み",
                   "段階的なモダナイゼーション"],
         value="既存資産を作り直さず、短時間の自動処理だけで異種 DB 横断トランザクションの対象にできる。",
         edition="Core ツール（Schema Loader）",
         notes=f"出典: {DB_DOCS}schema-loader-import/ 制限: 主キー必須、decimal / json / enum / uuid 等は非対応。"),
]

DB_MAP = [
    ("トランザクション基盤（Core / OSS）",
     ["ACID トランザクション（Consensus Commit）", "マルチストレージ（統一インターフェース）",
      "マイクロサービストランザクション", "既存テーブルのインポート"]),
    ("クラスタとインターフェース",
     ["ScalarDB Cluster（クラスタリング）", "SQL インターフェース（JDBC / Spring Data）",
      "GraphQL インターフェース", "MCP Server（LLM 連携）", "非トランザクショナル操作"]),
    ("セキュリティ・ガバナンス",
     ["認証・認可（USERPASS / OIDC）", "保存時暗号化（カラムレベル）",
      "属性ベースアクセス制御（ABAC）"]),
    ("分析・AI・事業継続",
     ["ScalarDB Analytics（横断分析）", "ベクトル検索", "リモートレプリケーション（DR）"]),
]

# ---------------------------------------------------------------- ScalarDL

DL_DOCS = "https://scalardl.scalar-labs.com/docs/latest/"

FEATURES_DL = [
    dict(title="ビザンチン故障検知 — 改ざんを確実に検知する",
         figure=fig_dl_bft,
         overview="データ改ざんや悪意ある攻撃を含む任意の故障（ビザンチン故障）を検知するミドルウェア。"
                  "故障を「隠蔽」するブロックチェーンと異なり「検知」に特化し、独立管理された 2 ノード"
                  "（Ledger + Auditor）だけで成立する。プロトコルは Ordering → Commit → Validation の"
                  "3 段階。",
         usecases=["GDPR / CCPA 等での完全性証明",
                   "サプライチェーンの監査証跡",
                   "監査ログの保全・不正検知"],
         value="ブロックチェーンは最低 4〜数千ノード必要なところを 2 つの管理ドメインで実現し、数万 TPS 級の性能と ACID・厳密なファイナリティを両立。",
         edition="完全な検知構成は Enterprise（Auditor が必要）",
         notes=f"出典: {DL_DOCS}overview / {DL_DOCS}design"),
    dict(title="Ledger — ハッシュチェーンでつながる追記型台帳",
         figure=fig_dl_ledger,
         overview="データを「アセットの集合」として抽象化する追記専用台帳。各アセットは asset_id と"
                  "age（履歴バージョン）で識別される履歴列で構成され、レコードはハッシュチェーンを"
                  "形成する。中間レコードの削除・更新はチェーン走査で検知できる。操作は get / put / "
                  "scan。",
         usecases=["取引ログ・監査証跡の管理",
                   "改ざん検知が必要な業務レコード",
                   "証跡系アプリの構築"],
         value="通常の DB（RDB / NoSQL）の上に被せるだけで追記型・改ざん検知可能な台帳が得られ、既存 DB 資産と運用をそのまま活かせる。",
         edition="Community 〜（BYOL 版は Enterprise）",
         notes=f"出典: {DL_DOCS}design / {DL_DOCS}data-modeling"),
    dict(title="Auditor — 独立した第三者検証で信頼を担保",
         figure=fig_dl_auditor,
         overview="Ledger とは別の管理ドメインで運用されるセカンダリサーバ。トランザクションを事前"
                  "順序付けし、Ledger のコミット後に結果を検証・自らも実行する。両者の状態乖離＝"
                  "改ざん・不正をクライアントが検知でき、validateLedger は不整合検出時に "
                  "INCONSISTENT_STATES を返す。",
         usecases=["別組織による第三者検証体制",
                   "規制産業の監査要件対応",
                   "管理者不正も検知するゼロトラスト"],
         value="たった 2 つの独立管理ノードでビザンチン故障検知を実現し、ブロックチェーンの多ノード合意より低コスト・高性能。",
         edition="Enterprise のみ",
         notes=f"出典: {DL_DOCS}design / {DL_DOCS}libraries-and-tools"),
    dict(title="Contract — 署名されたビジネスロジック",
         figure=fig_dl_contract,
         overview="基底クラスを継承した Java プログラムとして記述するビジネスロジック。コントラクトと"
                  "引数は所有者の秘密鍵でデジタル署名され、所有者のみが実行できる。決定性が必須要件で、"
                  "ネストした呼び出しは全体が ACID に実行される。呼び出し元 ID によるアクセス制御も可能。",
         usecases=["資産移転・取引記録のロジック",
                   "実行者を制限した特権的操作",
                   "ネスト実行による複合処理"],
         value="ロジック自体が署名で保護されるため「誰が・どのロジックで」更新したかまで検証でき、処理の改ざんも検知できる。",
         edition="Community / Enterprise",
         notes=f"出典: {DL_DOCS}how-to-write-contract"),
    dict(title="Function — 台帳と業務データを 1 トランザクションで",
         figure=fig_dl_function,
         overview="追記専用の台帳では扱えない「更新・削除が必要な通常のアプリケーションデータ」を"
                  "管理する仕組み。Function 内では ScalarDB インターフェースで Get / Put / Delete が"
                  "可能で、Contract と Function は ScalarDB の分散 ACID トランザクションにより"
                  "原子的に実行される。",
         usecases=["決済: 残高と証跡を同時更新",
                   "台帳と業務 DB の一貫性維持",
                   "更新・削除が必要なマスタ管理"],
         value="「外部 DB + 台帳にログ」という従来構成の不整合リスクを排除し、証跡と業務データを単一 ACID トランザクションで更新できる。",
         edition="Community / Enterprise",
         notes=f"出典: {DL_DOCS}how-to-write-function / {DL_DOCS}data-modeling"),
    dict(title="TableStore — SQL だけで作る改ざん検知テーブル",
         figure=fig_dl_table,
         overview="台帳抽象の上の高レベル抽象で、SQL によるテーブルベースのデータ管理を提供する。"
                  "CREATE TABLE / SELECT / UPDATE / JOIN とセカンダリインデックスに対応し、history() "
                  "関数で全変更履歴を照会できる。bootstrap コマンドが事前定義コントラクトを自動登録"
                  "するため、コントラクト開発は不要。",
         usecases=["DB 感覚で作る改ざん検知アプリ",
                   "history() での監査照会",
                   "SQL 資産を活かした短期構築"],
         value="Java コントラクト開発なし（ローコード）で、SQL だけで改ざん検知可能なテーブルを扱える。台帳導入の開発コストを大きく下げる。",
         edition="Community / Enterprise / 3.12+",
         notes=f"出典: {DL_DOCS}getting-started-tablestore"),
    dict(title="HashStore — ノーコードのデジタル証拠保全",
         figure=fig_dl_hash,
         overview="デジタル証拠保全に特化した高レベル抽象。ファイル・監査ログ等のオブジェクトの"
                  "ハッシュ値と、オブジェクト集合（コレクション）を、コントラクトを書かずに不変管理"
                  "する。put-object / compare-object-versions によるオブジェクト真正性と、コレクション"
                  "の履歴管理を提供。",
         usecases=["ファイル完全性の検証",
                   "監査対象セットの改変検知",
                   "chain of custody の記録"],
         value="実データではなくハッシュのみを台帳に置くため大容量ファイルにも適用でき、開発ゼロ（ノーコード）で証拠保全を実現する。",
         edition="Community / Enterprise / 3.12+",
         notes=f"出典: {DL_DOCS}getting-started-hashstore"),
    dict(title="ネームスペース — 1 つの台帳でマルチテナント",
         figure=fig_dl_ns,
         overview="アセット・クレデンシャル・コントラクト・ファンクションを namespace 単位で論理分離"
                  "する。複数 namespace へアクセスできる Cross-namespace access と、その namespace の"
                  "クライアントのみが操作できる完全分離の Restricted access の 2 モデルを提供する。",
         usecases=["SaaS のテナント分離",
                   "複数システムの 1 Ledger 集約"],
         value="1 つの Ledger デプロイで複数テナント・アプリを安全に収容でき、テナントごとに台帳を建てる運用・インフラコストを削減する。",
         edition="Community / Enterprise / 3.13+",
         notes=f"出典: {DL_DOCS}manage-namespaces"),
    dict(title="Asset Proof — 実行時証拠で事後改ざんを防ぐ",
         figure=fig_dl_proof,
         overview="コントラクト実行時に Ledger が生成する暗号学的証拠。アセットの ID と age、実行 "
                  "nonce、入力参照、現在・直前のハッシュ、デジタル署名で構成される。証拠をクライアント"
                  "側に保全することで、事後的な Ledger 側の改ざんを状態の乖離として検知可能にする。",
         usecases=["Ledger 事後改ざんリスクの低減",
                   "取引の否認防止・証拠保存"],
         value="Ledger 単体構成でも「実行時点のスナップショット証拠」を外部化でき、改ざんのハードルを大幅に上げる軽量な保証手段。",
         edition="Community / Enterprise",
         notes=f"出典: {DL_DOCS}how-to-write-applications"),
]

DL_MAP = [
    ("コア（改ざん検知の仕組み）",
     ["ビザンチン故障検知", "Ledger（追記型台帳・アセット管理）", "Auditor（独立検証）",
      "Asset Proof（実行時証拠）"]),
    ("開発モデル",
     ["Contract（署名付きビジネスロジック）", "Function（可変データの原子的更新）"]),
    ("高レベル抽象（ローコード / ノーコード）",
     ["TableStore（SQL テーブル台帳）3.12+", "HashStore（デジタル証拠保全）3.12+"]),
    ("運用",
     ["ネームスペース管理（マルチテナント）3.13+", "validateLedger（台帳検証 API）",
      "認証: デジタル署名 / HMAC"]),
]


# ---------------------------------------------------------------- 生成

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--folder", default=None)
    args = p.parse_args()

    template = bd.load_template(TEMPLATE)
    deck = bd.TemplateDeck.create(template, title=TITLE, folder=args.folder)
    problems: list[str] = []

    deck.add_slide("COVER", title=TITLE, subtitle=SUBTITLE,
                   body=f"{DATE}\n株式会社Scalar")
    deck.add_slide(
        "CONTENT", title="本資料の見方", body=[
            "各機能を 1 スライドずつ「図解 / 機能概要 / ユースケース / 特長」で整理",
            "対象: ScalarDB 15 機能、ScalarDL 9 機能（各セクション冒頭に機能マップ）",
            "情報源: developers.scalar-labs.com の公式ドキュメント（2026年8月1日 調査）",
            "バージョン表記（3.15+ など）は機能が導入されたバージョン、右上はエディション",
            "※ プレビュー提供中の機能はその旨を明記",
        ], body_font_size=14, body_line_spacing=150,
        notes="ScalarDB 最新 3.18.0（2026-05-01）、ScalarDL 最新 3.13.0（2026-03-25）。")

    def product_section(section_title, section_body, map_title, map_groups,
                        features, accent_key):
        deck.add_slide("SECTION", title=section_title, body=section_body)
        ref = deck.add_slide("TITLE_ONLY", title=map_title)
        d = Canvas(deck, ref["slideId"], template)
        draw_feature_map(d, map_groups, getattr(d.P, accent_key))
        problems.extend(f"{map_title[:12]}…: {m}" for m in
                        (d.audit_bounds() + d.audit_overlaps() + d.audit_text_fit()))
        for f in features:
            ref = deck.add_slide("TITLE_ONLY", title=f["title"],
                                 notes=f.get("notes"))
            d = Canvas(deck, ref["slideId"], template)
            draw_feature(d, f, getattr(d.P, accent_key))
            problems.extend(f"{f['title'][:12]}…: {m}" for m in
                            (d.audit_bounds() + d.audit_connectors()
                             + d.audit_overlaps() + d.audit_text_fit()))

    product_section(
        "ScalarDB", "Universal HTAP エンジン — 15 機能",
        "ScalarDB 機能マップ: 基盤・接続・セキュリティ・分析の 4 領域",
        DB_MAP, FEATURES_DB, "primary")
    product_section(
        "ScalarDL", "ビザンチン故障検知ミドルウェア — 9 機能",
        "ScalarDL 機能マップ: コア・開発・高レベル抽象・運用の 4 領域",
        DL_MAP, FEATURES_DL, "success")

    deck.add_slide("CLOSING")

    deck.add_page_numbers()
    for m in problems:
        print(f"  検査: {m}")
    url = deck.commit()
    total = 2 + 2 * 2 + len(FEATURES_DB) + len(FEATURES_DL) + 1
    print(f"Done! {total} slides. Open: {url}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
