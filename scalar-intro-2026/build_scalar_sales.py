#!/usr/bin/env python3
"""Scalar 営業向け: 提案準備ガイドデッキ(ヒアリング項目の整理 + 製品価値の説明)。

前半でヒアリングすべき情報をビジネス面・技術面で整理し、課題→提案の
マッピングを挟んで、後半に提案へ流用できる製品価値スライド
(ビジネス面・技術面)を置く。事実は scalar-product-slides スキルの
references/research-2026-08.md(2026-08-01 調査)に基づく。
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

TITLE = "Scalar 提案準備ガイド"
SUBTITLE = "お客様ヒアリングの整理と、ScalarDB / ScalarDL の価値の伝え方"
DATE = "2026年8月"

DB_DOCS = "https://scalardb.scalar-labs.com/docs/latest/"
DL_DOCS = "https://scalardl.scalar-labs.com/docs/latest/"


# ---------------------------------------------------------------- 共通部品

def _pill(d: Canvas, x, y, w, h, text, accent, *, light=0.88, size=9,
          bold=False, color=None):
    return d.shape(x, y, w, h, kind="ROUND_RECTANGLE",
                   fill=lighten(accent, light), stroke=accent, text=text,
                   size=size, bold=bold, color=color or d.P.text,
                   line_spacing=112)


def _band(d: Canvas, y, text, accent, *, h=0.46, size=11):
    """スライド下端のメッセージ帯(バー無しなので角丸でよい)。"""
    d.shape(0.5, y, 9.0, h, kind="ROUND_RECTANGLE",
            fill=lighten(accent, 0.9), stroke=lighten(accent, 0.5),
            text=text, size=size, bold=True, color=d.P.text,
            line_spacing=115)


def _point_card(d: Canvas, x, y, w, h, head, lines, accent):
    """右側の「技術ポイント」カード(アクセントバー付きなので直角)。"""
    d.shape(x, y, w, h, kind="RECTANGLE", fill=d.P.surface, stroke=d.P.border)
    d.shape(x, y, w, 0.06, kind="RECTANGLE", fill=accent, stroke=None)
    d.label(x + 0.16, y + 0.14, w - 0.32, 0.3, head, size=11, bold=True,
            align="START", color=accent)
    d.label(x + 0.16, y + 0.52, w - 0.32, h - 0.66,
            "\n".join(f"・{t}" for t in lines), size=9.5, align="START",
            color=d.P.text, line_spacing=138)


# ---------------------------------------------------------------- 図解

def draw_process(d: Canvas):
    """商談プロセス: 3 ステップと本資料の対応。"""
    b = d.flow(0.5, 1.1, 9.0, 0.7,
               ["① 聞く\nヒアリング", "② 構造化する\n課題を型に整理",
                "③ 価値で応える\n提案・PoC"], size=10)
    cards = [
        ("集める(§1)", "ビジネス面・技術面の 5 領域で漏れなく聞く。"
         "課題のコストは数字で取る"),
        ("整理する(§2)", "聞き取った課題を 6 つの型に落とす。"
         "型が決まれば提案が決まる"),
        ("伝える(§3・§4)", "ビジネス価値・技術価値・事例のスライドを"
         "提案書にそのまま流用する"),
    ]
    b = d.cards(0.5, b + 0.5, 9.0, 1.55, cards, body_size=9.5)
    _band(d, b + 0.35,
          "ヒアリングの質が提案の質を決める — 課題のコストが数字で取れていれば、提案は ROI で語れる",
          d.P.primary)


def draw_hearing_map(d: Canvas):
    """ヒアリング 5 領域の全体像。"""
    row1 = [
        ("① 経営・事業の文脈", "DX・モダナイゼーションの方針、新規事業や"
         "データ活用の構想。提案の位置づけを決める"),
        ("② 業務課題とコスト", "不整合の補正・二重入力・監査/帳票対応に"
         "かかる工数と頻度。ROI 試算の材料になる"),
        ("③ 現行システムとデータ", "DB の種類・数・配置、DB 間の連携方法。"
         "提案の技術的な分岐点になる"),
    ]
    row2 = [
        ("④ 非機能・制約", "性能(TPS)・可用性・DR(RPO/RTO)・規制要件。"
         "構成とエディション選定の材料"),
        ("⑤ 商談の条件", "決裁者・選定プロセス・評価基準・予算・時期。"
         "提案の規模と進め方を決める"),
    ]
    b = d.cards(0.5, 1.02, 9.0, 1.6, row1, body_size=9.5)
    cw = (9.0 - 0.44) / 3          # 上段とカード幅を揃えて中央寄せ
    x2 = 0.5 + (9.0 - (cw * 2 + 0.22)) / 2
    b = d.cards(x2, b + 0.22, cw * 2 + 0.22, 1.6, row2, body_size=9.5)
    _band(d, b + 0.3,
          "①②はビジネス面(次頁)、③④は技術面(次々頁)で深掘りする — ⑤は商談運営の必須情報",
          d.P.primary, size=10.5)


def draw_mapping(d: Canvas):
    """課題の型 → 提案する製品・機能。"""
    d.label(0.5, 0.98, 3.9, 0.28, "お客様の課題(ヒアリングで拾う)", size=10,
            bold=True, align="CENTER", color=d.P.text)
    d.label(5.1, 0.98, 3.9, 0.28, "提案する製品・機能", size=10, bold=True,
            align="CENTER", color=d.P.text)
    pairs = [
        ("複数 DB がサイロ化し、整合性は人手・バッチで担保",
         "ScalarDB — マルチストレージ + ACID", d.P.primary),
        ("マイクロサービス間の整合性処理(Saga 等)を自作",
         "ScalarDB — マイクロサービストランザクション", d.P.primary),
        ("レガシー DB を止めずに段階的に移行したい",
         "ScalarDB — 既存テーブルのインポート(--import)", d.P.primary),
        ("複数 DB を横断する分析のたびに ETL を増設",
         "ScalarDB Analytics — ETL レスの横断分析", d.P.info),
        ("改ざん防止・監査証跡の要件がある",
         "ScalarDL — Ledger + Auditor(改ざん検知)", d.P.success),
        ("ブロックチェーンを検討したが重い・高い",
         "ScalarDL — 2 管理ドメインで成立・数万 TPS", d.P.success),
    ]
    for i, (left, right, accent) in enumerate(pairs):
        ry = 1.34 + i * 0.55
        a = d.shape(0.5, ry, 3.9, 0.46, kind="ROUND_RECTANGLE",
                    fill=d.P.surface, stroke=d.P.border, text=left, size=8.5,
                    line_spacing=112)
        b = d.shape(5.1, ry, 3.9, 0.46, kind="ROUND_RECTANGLE",
                    fill=lighten(accent, 0.88), stroke=accent, text=right,
                    size=8.5, bold=True, line_spacing=112)
        d.connect(a, b, color=accent, weight=1.4)
    _band(d, 4.66, "複数の型が同時に当てはまることも多い — 最も痛みが大きい型から提案する",
          d.P.primary, h=0.4, size=10.5)


def draw_db_tech(d: Canvas):
    """ScalarDB 技術価値: DB 非依存 ACID の図解 + ポイント。"""
    fx, fy = 0.5, 1.0
    d.icon("server", fx + 1.95, fy + 0.02, 0.4, label="アプリケーション",
           label_size=8.5, label_w=1.8)
    _pill(d, fx + 0.35, fy + 0.95, 4.4, 0.5,
          "ScalarDB — Consensus Commit(DB 非依存の ACID)", d.P.primary,
          size=9.5, bold=True)
    d.icon_row(fx + 0.45, fy + 1.75, 4.2,
               [("database", "MySQL /\nPostgreSQL"), ("stack", "DynamoDB /\nCassandra"),
                ("database", "Spanner /\nTiDB")], size=0.38, label_size=7.5)
    d.arrow(fx + 2.15, fy + 0.72, fx + 2.15, fy + 0.93, color=d.P.muted,
            weight=1.0, _anchored=True)
    for cx in (fx + 1.15, fx + 2.55, fx + 3.95):
        d.arrow(cx, fy + 1.47, cx, fy + 1.73, color=d.P.muted, weight=1.0,
                _anchored=True)
    d.label(fx, fy + 2.85, 5.2, 0.26,
            "1 つのトランザクションが異種 DB へ原子的に反映される", size=9,
            align="CENTER", color=d.P.muted)
    _point_card(d, 5.95, 1.0, 3.55, 3.15, "技術ポイント", [
        "Consensus Commit による DB 非依存 ACID",
        "RDBMS / NewSQL / NoSQL に対応",
        "2PC でマイクロサービスを横断",
        "Cluster(Kubernetes)で可用性と拡張",
        "SQL / GraphQL / MCP Server の入口",
        "既存 DB は無停止でインポート可能",
    ], d.P.primary)
    _band(d, 4.5, "対応 DB 例: MySQL・PostgreSQL・Oracle・SQL Server・Db2・Aurora\n"
          "Spanner・TiDB・YugabyteDB・DynamoDB・Cassandra・Cosmos DB など",
          d.P.primary, h=0.5, size=9)


def draw_dl_tech(d: Canvas):
    """ScalarDL 技術価値: 2 管理ドメインの突き合わせ図解 + ポイント。"""
    fx, fy = 0.5, 1.0
    d.icon("browser", fx + 2.0, fy, 0.36, label="クライアント", label_size=8.5,
           label_w=1.4)
    d.cloud_zone(fx + 0.05, fy + 0.85, 2.45, 1.45, title="管理ドメイン A",
                 title_size=8.5, color=d.P.primary)
    _pill(d, fx + 0.3, fy + 1.35, 1.95, 0.44, "Ledger(台帳)", d.P.primary,
          size=9.5, bold=True)
    d.cloud_zone(fx + 2.75, fy + 0.85, 2.45, 1.45, title="管理ドメイン B",
                 title_size=8.5, color=d.P.success)
    _pill(d, fx + 3.0, fy + 1.35, 1.95, 0.44, "Auditor(検証)", d.P.success,
          size=9.5, bold=True)
    d.arrow(fx + 1.9, fy + 0.55, fx + 1.25, fy + 0.82, color=d.P.muted,
            weight=1.0, _anchored=True)
    d.arrow(fx + 2.5, fy + 0.55, fx + 3.95, fy + 0.82, color=d.P.muted,
            weight=1.0, _anchored=True)
    d.line(fx + 2.28, fy + 1.57, fx + 2.97, fy + 1.57, color=d.P.danger,
           weight=1.5, start_arrow="FILL_ARROW", end_arrow="FILL_ARROW",
           _anchored=True)
    d.label(fx, fy + 2.5, 5.2, 0.5,
            "両者の応答をクライアントが突き合わせ、不一致 = 改ざんを検知。\n"
            "Ledger の管理者ですら不正できない", size=9, align="CENTER",
            color=d.P.muted, line_spacing=125)
    _point_card(d, 5.95, 1.0, 3.55, 3.15, "技術ポイント", [
        "ビザンチン故障を「検知」する設計",
        "ハッシュチェーンの追記型台帳",
        "署名付き Contract で実行者を統制",
        "ScalarDB 上で動作し ACID を継承",
        "数万 TPS・厳密なファイナリティ",
        "TableStore(SQL) / HashStore も提供",
    ], d.P.success)
    _band(d, 4.5, "ブロックチェーンとの違い: 多ノードの合意で故障を「隠蔽」するのではなく、"
          "独立した 2 ドメインで「検知」する — だから速く・安い",
          d.P.success, h=0.5, size=9.5)


def draw_value_cards(d: Canvas, items, accent, phrase):
    """ビジネス価値: 2×2 カード + 提案の一言。"""
    b = d.cards(0.5, 1.02, 9.0, 1.62, items[:2], body_size=9.5, accent=accent)
    b = d.cards(0.5, b + 0.22, 9.0, 1.62, items[2:], body_size=9.5,
                accent=accent)
    _band(d, b + 0.3, phrase, accent, h=0.44, size=10.5)


# ---------------------------------------------------------------- 生成

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--folder", default=None)
    args = p.parse_args()

    template = bd.load_template(TEMPLATE)
    deck = bd.TemplateDeck.create(template, title=TITLE, folder=args.folder)
    problems: list[str] = []

    def canvas_slide(title, draw, notes=None):
        ref = deck.add_slide("TITLE_ONLY", title=title, notes=notes)
        d = Canvas(deck, ref["slideId"], template)
        draw(d)
        problems.extend(f"{title[:14]}…: {m}" for m in
                        (d.audit_bounds() + d.audit_connectors()
                         + d.audit_overlaps() + d.audit_text_fit()))
        return d

    def table_slide(title, headers, rows, *, col_widths, notes=None,
                    row_h=0.55, size=9.5, note_text=None):
        ref = deck.add_slide("TITLE_ONLY", title=title, notes=notes)
        d = Canvas(deck, ref["slideId"], template)
        b = d.table(0.5, 1.05, 9.0, headers, rows, col_widths=col_widths,
                    row_h=row_h, size=size)
        if note_text:
            d.label(0.5, min(b + 0.15, 4.7), 9.0, 0.3, note_text, size=9,
                    align="START", color=d.P.muted)
        problems.extend(f"{title[:14]}…: {m}" for m in
                        (d.audit_bounds() + d.audit_overlaps()
                         + d.audit_text_fit()))

    # ---- 表紙・目的
    deck.add_slide("COVER", title=TITLE, subtitle=SUBTITLE,
                   body=f"{DATE}\n株式会社Scalar")
    deck.add_slide(
        "CONTENT", title="本資料の目的 — ヒアリングから提案までを 1 冊で支える",
        body=[
            "対象: ScalarDB / ScalarDL の提案を行う営業・プリセールス",
            "§1 ヒアリング: 商談で集めるべき情報をビジネス面・技術面の 5 領域で整理",
            "§2 課題の型: 聞き取った課題を 6 つの型に落とし、提案する製品・機能を決める",
            "§3 ビジネス価値: コスト・リスク・スピードの言葉で語る価値と公表事例",
            "§4 技術価値: 「なぜそれができるのか」を 1 枚で説明する図解",
            "情報源: 公式ドキュメント・公開事例(2026年8月1日 調査)。推測の数値は載せていない",
        ], body_font_size=14, body_line_spacing=150,
        notes="ScalarDB 最新 3.18.0(2026-05-01)、ScalarDL 最新 3.13.0(2026-03-25)。")

    # ---- 商談プロセス
    deck.add_slide("SECTION", title="提案までの流れ",
                   body="聞く → 構造化する → 価値で応える")
    canvas_slide("商談は「聞く → 構造化する → 価値で応える」の 3 ステップで設計する",
                 draw_process,
                 notes="本資料の使い方。ヒアリング(§1)→課題の型(§2)→価値提案(§3・§4)の対応。")

    # ---- §1 ヒアリング
    deck.add_slide("SECTION", title="§1 ヒアリングで集める情報",
                   body="ビジネス面・技術面の 5 領域で漏れなく聞く")
    canvas_slide("ヒアリングは 5 領域 — 業務とシステムの両面から課題を掴む",
                 draw_hearing_map)
    table_slide(
        "ビジネス面は「課題のコスト」を数字で聞き出せるかが勝負",
        ["領域", "主な質問", "提案への活かし方"],
        [["経営・事業の方向性",
          "DX・モダナイゼーションの計画、新規事業やデータ活用の構想",
          "提案の位置づけと投資枠の把握"],
         ["課題のコスト",
          "不整合の補正・二重入力・監査/帳票対応の工数と発生頻度",
          "ROI 試算の分子。PoC の効果測定にも使う"],
         ["体制と意思決定",
          "決裁者、情シスと事業部門の関係、選定プロセスと評価基準",
          "提案先とキーマンの特定"],
         ["予算・時期",
          "予算枠と年度、システム更改・契約更新の期限",
          "提案規模とスケジュール設計"],
         ["成功の定義",
          "何がどうなれば導入成功か(できるだけ定量指標で)",
          "PoC の合格条件へ転用"]],
        col_widths=[1.6, 3.9, 2.8], row_h=0.6,
        note_text="※ 課題のコストが数字で取れれば提案は ROI で語れる(例: ENS 社は法定帳票業務を 1/5 に)",
        notes="ENS 事例(法定帳票業務 1/5)は公表されている唯一の定量効果。出典: scalar-labs.com ニュース。")
    table_slide(
        "技術面は DB 構成と整合性の担保方法が提案の分岐点になる",
        ["領域", "主な質問", "確認ポイント(提案の分岐)"],
        [["DB 構成",
          "DB 製品・数・配置(オンプレ / クラウド / 両方)",
          "異種 DB 混在・サイロは ScalarDB の主戦場"],
         ["連携と整合性",
          "DB 間の同期方法(バッチ / ETL / 手作業)、不整合の頻度",
          "人手の突合・補正作業は課題の証拠"],
         ["アーキテクチャ",
          "マイクロサービス化の状況、Saga 等の整合性処理の自作有無",
          "マイクロサービストランザクションの適用余地"],
         ["レガシー資産",
          "メインフレーム・COBOL 資産、移行計画と停止可否",
          "無停止インポート(--import)の適用余地"],
         ["監査・証跡",
          "改ざん防止・監査証跡・規制要件(金融・エネルギー等)",
          "ScalarDL の適用余地"],
         ["非機能",
          "性能(TPS)・可用性・DR(RPO / RTO)・セキュリティ要件",
          "エディション・構成・DR 提案の選定材料"]],
        col_widths=[1.6, 3.9, 3.0], row_h=0.52, size=9,
        notes=f"機能の適用条件は公式ドキュメント参照: {DB_DOCS} / {DL_DOCS}")

    # ---- §2 課題の型
    deck.add_slide("SECTION", title="§2 課題を型に整理する",
                   body="6 つの型 — 型が決まれば提案が決まる")
    canvas_slide("課題は 6 つの型に整理できる — 型が決まれば提案が決まる",
                 draw_mapping,
                 notes="各機能の詳細は「Scalar 製品機能のご紹介」デッキ(1機能=1スライド)を参照。")

    # ---- §3 ビジネス価値
    deck.add_slide("SECTION", title="§3 製品価値 — ビジネス面",
                   body="コスト・リスク・スピードの言葉で語る")
    canvas_slide(
        "ScalarDB は開発・運用に埋もれた「整合性コスト」を削減する",
        lambda d: draw_value_cards(d, [
            ("整合性ロジックの自作が不要",
             "Saga・TCC や突合バッチの作り込みが不要になり、開発は業務ロジック"
             "に集中できる。保守対象のコードも減る"),
            ("ベンダーロックインの回避",
             "DB 非依存の統一インターフェース。DB・クラウドの変更や混在が"
             "可能になり、将来の選択肢と交渉力を保てる"),
            ("既存資産を活かした段階移行",
             "既存 DB を止めずに短時間で取り込める(--import)。全面作り直しでは"
             "ない現実的なモダナイゼーション路線を描ける"),
            ("不整合起因の障害・手戻りの削減",
             "データ補正・原因調査・障害対応という見えない運用コストを削減。"
             "認証認可・暗号化の一元化で統制もしやすい"),
        ], d.P.primary,
            "提案の一言:「バラバラなデータベースを、1 つの信頼できるデータ基盤として扱えるようにします」"),
        notes=f"機能の裏付け: {DB_DOCS}(Consensus Commit / multi-storage / 2PC / schema-loader-import)")
    canvas_slide(
        "ScalarDL は「データの信頼の証明」を現実的なコストで提供する",
        lambda d: draw_value_cards(d, [
            ("監査・帳票業務の効率化",
             "電力業界の ENS 社では、電力量データの法定帳票業務を 1/5 に削減"
             "(公表事例)。証跡が信頼できると確認作業が減る"),
            ("ブロックチェーンより低コスト",
             "多ノードの合意が不要。独立した 2 つの管理ドメインだけで改ざん"
             "検知が成立し、インフラ・運用コストが小さい"),
            ("業務システムに載る性能",
             "数万 TPS・ACID・厳密なファイナリティ。「証明のために性能を"
             "諦める」必要がない"),
            ("短期間・低コストで構築",
             "TableStore は SQL だけ、HashStore はノーコードで台帳を構築でき、"
             "導入の開発コストを大きく圧縮できる"),
        ], d.P.success,
            "提案の一言:「データが改ざんされていないことを、社外の相手にも証明できるようにします」"),
        notes=f"出典: {DL_DOCS}(overview / design / getting-started-tablestore / getting-started-hashstore)")
    table_slide(
        "規制産業・大企業の公表事例が提案の裏付けになる",
        ["お客様", "製品", "用途", "ポイント"],
        [["トヨタ自動車", "ScalarDL", "知財の証拠保全(PCE)", "Azure 上で稼働"],
         ["ENS", "ScalarDB", "電力量 30 分値の管理", "法定帳票業務を 1/5 に"],
         ["大手放送局", "ScalarDB", "コンテンツデータ管理", "サイロ統合"],
         ["J-POWER", "ScalarDL", "環境価値プラットフォーム", "2025 年稼働開始"],
         ["NSW", "ScalarDB", "メインフレーム移行", "COBOL 資産の近代化"],
         ["LayerX", "ScalarDB", "生成 AI サービスの基盤", "Ai Workforce(2024)"]],
        col_widths=[1.9, 1.4, 3.2, 2.5], row_h=0.5, size=9.5,
        note_text="※ 定量効果の公表は ENS のみ。各事例の詳細は scalar-labs.com のニュース・プレスリリース参照",
        notes="トヨタ・放送局は公式定型スライドあり(会社紹介デッキ参照)。"
              "J-POWER 2025.1〜 / NSW 2025.6 発表 / LayerX 2024.10 発表。")

    # ---- §4 技術価値
    deck.add_slide("SECTION", title="§4 製品価値 — 技術面",
                   body="「なぜそれができるのか」を 1 枚で")
    canvas_slide("ScalarDB — DB に依存しない ACID がすべての価値の源泉",
                 draw_db_tech,
                 notes=f"出典: {DB_DOCS}consensus-commit/ , {DB_DOCS}overview/")
    canvas_slide("ScalarDL — 独立した 2 つの管理ドメインの突き合わせで改ざんを検知",
                 draw_dl_tech,
                 notes=f"出典: {DL_DOCS}overview / {DL_DOCS}design "
                       "完全な検知構成(Auditor)は Enterprise。")

    # ---- まとめ
    deck.add_slide(
        "CONTENT", title="まとめ — ヒアリングで型を見つけ、価値で裏付ける",
        body=[
            "ヒアリングは 5 領域で構造化 — 特に「課題のコスト」を数字で取る",
            "課題は 6 つの型に整理 — 型が決まれば提案する製品・機能が決まる",
            "ビジネス価値は「整合性コストの削減」(ScalarDB)と「信頼の証明」(ScalarDL)で語る",
            "技術価値は「DB 非依存 ACID」「2 管理ドメインの改ざん検知」の 2 枚で説明する",
            "次のアクション: 課題の型に沿った PoC 提案 — 合格条件はヒアリングした「成功の定義」から",
        ], body_font_size=14, body_line_spacing=150)
    deck.add_slide("CLOSING")

    deck.add_page_numbers()
    for m in problems:
        print(f"  検査: {m}")
    url = deck.commit()
    print(f"Done! 18 slides. Open: {url}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
