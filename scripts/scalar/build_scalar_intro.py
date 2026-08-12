#!/usr/bin/env python3
"""株式会社Scalar 会社紹介・製品紹介・ユースケース デッキ生成。

scalar-2026-boilerplate を keep_existing で複製し、公式の定型スライド
（会社概要・役員構成・製品概要・導入顧客・事例・クロージング）を活かしつつ、
Web 調査（2026-08-01 実施）に基づく生成スライドを最終位置へ挿入する。

  実行: .venv/bin/python scripts/scalar/build_scalar_intro.py [--folder <URL>]
  検査: .venv/bin/python scripts/scalar/build_scalar_intro.py --dry-run
        （同梱スライドの間引きと文言置換は複製後の実物が要るので飛ばす）
"""
from __future__ import annotations

import argparse
import os
import sys

REPO_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(REPO_DIR, "scripts"))

import build_deck as bd  # noqa: E402
import _auth  # noqa: E402
from diagrams import Canvas, lighten  # noqa: E402
from _i18n import t, register  # noqa: E402

register({
    "Expected 12 bundled slides, got {n}": "同梱スライドが 12 枚でない: {n}",
    "  audit: {message}": "  検査: {message}",
    "Done! {n} slides. Open: {url}": "完了! スライド {n} 枚。URL: {url}",
})

TEMPLATE = os.path.join(REPO_DIR, "templates", "scalar-2026-boilerplate.json")
BRAND = os.path.join(REPO_DIR, "assets", "scalar", "product-logos")
LOGO_DB = os.path.join(BRAND, "scalardb-logo-horizontal.png")
LOGO_DL = os.path.join(BRAND, "scalardl-logo-horizontal.png")

TITLE = "株式会社Scalar ご紹介資料"
SUBTITLE = "会社概要・製品・ユースケース"
DATE = "2026年8月"

# 同梱 12 枚のうち削除する位置（0-origin）: <Proposal Title> 表紙, <Sub Section> 見出し
DROP_KEPT_POSITIONS = (1, 10)


# ---------------------------------------------------------------- 図解スライド

def _band(d: Canvas, x, y, w, h, *, logo=None, text=None, text_size=10.5,
          fill=None, stroke=None):
    """製品の帯。ロゴを左に置き、右に説明を書く。"""
    d.shape(x, y, w, h, kind="ROUND_RECTANGLE",
            fill=fill or lighten(d.P.primary, 0.88), stroke=stroke or d.P.primary)
    tx = x + 0.25
    if logo:
        d.image(x + 0.25, y + (h - 0.34) / 2, 1.45, 0.34, logo, fit="contain",
                alt=os.path.basename(logo))
        tx = x + 1.85
    if text:
        d.label(tx, y, x + w - tx - 0.2, h, text, size=text_size,
                align="START", valign="MIDDLE", color=d.P.text)
    return y + h


def draw_company_data(d: Canvas) -> None:
    """会社データ。数値 3 つ + キー/バリューの行。"""
    d.metric(0.5, 1.05, 2.86, 1.05, "2017年12月", "設立", value_size=17)
    d.metric(3.57, 1.05, 2.86, 1.05, "3拠点", "東京・札幌・サンフランシスコ",
             value_size=17)
    d.metric(6.64, 1.05, 2.86, 1.05, "約50名", "従業員数（2026年7月時点）",
             value_size=17, color=d.P.info)
    rows = [
        ("代表者", "深津 航（Founder / 代表取締役CEO）、山田 浩之（Founder / 代表取締役CTO）"),
        ("米国法人", "US Scalar Labs（CEO and President: Joe McCunney）"),
        ("事業内容", "データマネジメント製品 ScalarDB / ScalarDL の研究開発・提供"),
        ("バリュー", "Quality Obsessed ／ Customer Focus ／ Frontier Spirit"),
        ("実績", "FIBC 2019 グランプリ受賞、国際会議 VLDB に 2 年連続論文採択（2022・2023）"),
    ]
    y = 2.45
    for k, v in rows:
        d.label(0.5, y, 1.35, 0.34, k, size=10.5, bold=True, align="START",
                valign="MIDDLE", color=d.P.primary)
        d.label(1.95, y, 7.55, 0.34, v, size=10.5, align="START",
                valign="MIDDLE", color=d.P.text)
        y += 0.44
    d.label(0.5, y + 0.1, 9.0, 0.3,
            "タグライン: “Absolute data reliability” — 絶対的なデータ信頼性",
            size=10.5, align="CENTER", color=d.P.muted)


def draw_history(d: Canvas) -> None:
    """沿革。タイムライン + 補足。"""
    d.timeline(0.5, 1.3, 9.0, [
        ("2017.12", "創業"),
        ("2018.10", "ScalarDB を\nOSS 公開"),
        ("2019", "FIBC 2019\nグランプリ"),
        ("2022.11", "シリーズA\n15億円調達"),
        ("2022-23", "VLDB 2年連続\n論文採択"),
        ("2026", "ScalarDB 3.18\nKong 提携"),
    ], row_h=1.25, size=10, size_title=10)
    d.label(0.5, 3.0, 9.0, 0.3,
            "2023.12 執行役員体制の強化・営業拠点の新設", size=10.5,
            align="CENTER", color=d.P.text)
    d.label(0.5, 3.4, 9.0, 0.3,
            "2025 年以降はパートナー協業を拡大（NSW・ゼンリン・Kong ほか）",
            size=10.5, align="CENTER", color=d.P.text)
    b = _band(d, 1.7, 4.0, 6.6, 0.6,
              text="日本発の研究開発型スタートアップとして、東京・札幌・米国で開発と事業展開を継続",
              text_size=10)


def draw_challenges(d: Canvas) -> None:
    """製品が解決する課題 → 2 製品での解決。"""
    b = d.cards(0.5, 1.05, 9.0, 1.7, [
        ("データのサイロ化", "部門・サービスごとに DB が乱立し、横断的なデータ利用や分析が難しい"),
        ("整合性の作り込み", "複数 DB やマイクロサービス間の一貫性保証をアプリ側で実装すると複雑で高コスト"),
        ("改ざんへの備え", "規制対応や監査で「データが改変されていないこと」の証明が求められる"),
    ], accent=[d.P.primary, d.P.primary, d.P.danger])
    d.shape(2.7, b + 0.2, 4.6, 0.46, kind="ROUND_RECTANGLE",
            fill=d.P.primary, stroke=None, text="Scalar は 2 つの製品でこの課題に応える",
            size=11, bold=True, color="#FFFFFF")
    y = b + 0.9
    _band(d, 0.5, y, 4.4, 0.72, logo=LOGO_DB,
          text="分散データの統合と\nACID トランザクション", text_size=9.5)
    _band(d, 5.1, y, 4.4, 0.72, logo=LOGO_DL,
          text="改ざん検知による\nデータの信頼性保証", text_size=9.5,
          fill=lighten(d.P.success, 0.88), stroke=d.P.success)


def draw_db_arch(d: Canvas) -> None:
    """ScalarDB: アプリ → ScalarDB → 各データベース の 3 層。"""
    d.label(0.5, 0.95, 9.0, 0.24, "アプリケーション", size=9.5, align="START",
            color=d.P.muted)
    d.icon_row(0.9, 1.25, 8.2, [("browser", "Web アプリ"), ("mobile", "モバイル"),
                                ("server", "バッチ"), ("bot", "AI エージェント")],
               size=0.5, label_size=8.5)

    # 帯とゾーンの間には「見出し」と「下向きの矢印」の両方が入る。帯を少し上げて
    # 見出しの分の高さを作り、矢印は見出しより下から引く（重ねると字を貫く）
    band_y = 2.40
    d.shape(0.9, band_y, 8.2, 0.72, kind="ROUND_RECTANGLE",
            fill=lighten(d.P.primary, 0.88), stroke=d.P.primary)
    d.image(1.15, band_y + 0.16, 1.5, 0.42, LOGO_DB, fit="contain", alt="ScalarDB")
    d.label(2.85, band_y + 0.06, 6.0, 0.6,
            "Consensus Commit による DB 非依存の ACID トランザクション（SQL / GraphQL / CRUD / ベクトル検索）",
            size=10, align="START", valign="MIDDLE", color=d.P.text)

    zone_y = 3.55
    caption_y = band_y + 0.74          # 帯のすぐ下
    d.label(0.5, caption_y, 9.0, 0.19, "バックエンドのデータベース", size=9.0,
            align="START", color=d.P.muted)
    for i, (vendor, item) in enumerate([
        ("aws", ("aws:dynamodb", "DynamoDB")),
        ("azure", ("azure:cosmos-db", "Cosmos DB")),
        ("gcp", ("gcp:cloud-spanner", "Spanner")),
    ]):
        zx = 0.9 + i * 2.15
        d.cloud_zone(zx, zone_y, 1.95, 1.5, vendor=vendor, title_size=8)
        d.cloud_icon(item[0], zx + 0.72, zone_y + 0.34, 0.5, label=item[1],
                     label_size=8.5, label_w=1.8)
    ox = 0.9 + 3 * 2.15
    d.cloud_zone(ox, zone_y, 1.95, 1.5, title="オンプレミス / 自前運用", title_size=8)
    d.icon_row(ox + 0.05, zone_y + 0.34, 1.85,
               [("database", "PostgreSQL"), ("stack", "Cassandra")],
               size=0.42, label_size=7.5, gap=0.02)

    for i in range(4):
        cx = 0.9 + 8.2 / 4 * (i + 0.5)
        d.arrow(cx, 2.15, cx, band_y - 0.06, color=d.P.muted, weight=1.0,
                _anchored=True)
    for i in range(4):
        zx = 0.9 + i * 2.15 + 0.975
        d.arrow(zx, caption_y + 0.22, zx, zone_y - 0.04, color=d.P.muted, weight=1.0,
                _anchored=True)


def draw_db_lineup(d: Canvas) -> None:
    """ScalarDB のラインナップとエディション。"""
    b = d.cards(0.5, 1.05, 9.0, 1.8, [
        ("ScalarDB Core（OSS）", "Apache License 2.0。DB 抽象化と Consensus Commit による ACID トランザクション"),
        ("ScalarDB Cluster", "Kubernetes 上のクラスタリング。認証認可・暗号化・ABAC・SQL / GraphQL・ベクトル検索"),
        ("ScalarDB Analytics", "Apache Spark ベースの横断分析。ScalarDB 管理外の DB も直接データソースにできる"),
    ], accent=[d.P.muted, d.P.primary, d.P.info])
    d.label(0.5, b + 0.15, 9.0, 0.55,
            "エディション: Community（無料・OSS）/ Enterprise Standard / Enterprise Premium\n"
            "AWS・Google Cloud マーケットプレイスまたは BYOL で提供",
            size=9.5, align="CENTER", color=d.P.text, line_spacing=130)
    d.label(0.5, b + 0.85, 9.0, 0.24, "最近の機能進化", size=9.5, align="START",
            color=d.P.muted)
    d.flow(0.5, b + 1.12, 9.0, 0.66, [
        "3.15\nABAC・ベクトル検索",
        "3.16\nリモートレプリケーション",
        "3.17\nスキーマ変更ゼロ導入",
        "3.18\nSpanner 対応・高速化",
    ], size=8.5)


def draw_dl_auditor(d: Canvas) -> None:
    """ScalarDL: Auditor 構成。管理主体を分けて相互に検証する。"""
    d.icon_row(3.6, 0.95, 2.8, [("browser", "クライアント")], size=0.42,
               label_size=9)
    for i, (title, product, note, db, dbname) in enumerate([
        ("運用主体 A", "ScalarDL Ledger", "資産の更新を実行して記録する",
         "aws:dynamodb", "DynamoDB"),
        ("運用主体 B", "ScalarDL Auditor", "同じ要求を独立に記録して突き合わせる",
         "azure:cosmos-db", "Cosmos DB"),
    ]):
        accent = d.P.primary if i == 0 else d.P.success
        zx = 0.5 + i * 4.85
        d.cloud_zone(zx, 1.95, 4.15, 2.55, title=title, title_size=9, color=accent)
        _band(d, zx + 0.25, 2.35, 3.65, 0.5, text=product, text_size=10.5,
              fill=lighten(accent, 0.88), stroke=accent)
        d.label(zx + 0.25, 2.92, 3.65, 0.24, note, size=8.5, align="CENTER",
                color=d.P.muted)
        d.cloud_zone(zx + 0.25, 3.3, 3.65, 1.0,
                     vendor="aws" if i == 0 else "azure", title_size=7.5)
        d.cloud_icon(db, zx + 1.86, 3.52, 0.4, label=dbname, label_size=8,
                     label_w=2.0)
    d.arrow(4.6, 1.62, 3.0, 1.92, color=d.P.muted, weight=1.0, _anchored=True)
    d.arrow(5.4, 1.62, 7.1, 1.92, color=d.P.muted, weight=1.0, _anchored=True)
    d.line(4.68, 2.6, 5.32, 2.6, color=d.P.danger, weight=1.5,
           start_arrow="FILL_ARROW", end_arrow="FILL_ARROW", _anchored=True)
    d.label(3.95, 2.16, 2.1, 0.24, "相互に検証", size=8.5, align="CENTER",
            color=d.P.danger)
    d.label(0.5, 4.62, 9.0, 0.26,
            "片方が改ざんされても、もう片方と突き合わせれば検知できる — 最小 2 つの管理ドメインで成立",
            size=9.5, align="CENTER", color=d.P.muted)


def draw_dl_evidence(d: Canvas) -> None:
    """ScalarDL: 改ざん検知の流れ。"""
    d.asset_icon_flow(0.5, 1.35, 9.0, [
        ("personal-info", "資産の更新要求"),
        ("evidence-chain", "ハッシュで\n前の記録につなぐ"),
        ("timestamp", "いつの記録かを残す"),
        ("tamper-check", "後から検証する"),
    ], size=0.8, label_size=9.5)
    d.label(0.5, 3.4, 9.0, 0.3,
            "記録どうしが鎖状につながっているため、途中を書き換えると鎖が切れる",
            size=11, align="CENTER", color=d.P.text)
    d.asset_icon_row(2.2, 3.95, 5.6, [
        ("public-key", "公開鍵で検証"), ("private-key", "秘密鍵で署名"),
    ], size=0.5, label_size=9, color=[d.P.info, d.P.danger])


def draw_db_patterns(d: Canvas) -> None:
    """ScalarDB のユースケースパターン 6 種。"""
    b = d.cards(0.5, 1.0, 9.0, 1.55, [
        ("サイロ化 DB の統合", "統一インターフェースで複数 DB を仮想的に単一 DB として扱う"),
        ("マイクロサービスの一貫性", "DB 非依存の ACID トランザクションでサービス間の整合性を保証"),
        ("レガシー移行", "アプリを作り直さずに DB 移行・メインフレーム脱却を実現"),
    ])
    d.cards(0.5, b + 0.25, 9.0, 1.55, [
        ("マルチクラウド", "クラウドや DB をまたぐトランザクションと統一セキュリティ"),
        ("生成 AI・RAG 基盤", "異種データソースを一貫性保証付きの単一リポジトリに抽象化"),
        ("大量データ処理", "NoSQL 上でも ACID を保証するスケーラブルな基盤"),
    ], accent=d.P.info)


def draw_dl_patterns(d: Canvas) -> None:
    """ScalarDL のユースケースパターン 4 種 + 対象業界。"""
    b = d.cards(0.5, 1.05, 9.0, 1.75, [
        ("改ざん検知", "ビザンチン故障を検知し、アクセス時に即座に改ざんを検出"),
        ("監査証跡・証拠保全", "改ざん検知とタイムスタンプで電子データの証拠力を確保"),
        ("トレーサビリティ", "追記型台帳で原産地や流通経路などの来歴を記録"),
        ("ブロックチェーン代替", "最小 2 管理ドメイン・数万 TPS。既存 DB 上に構築できる"),
    ], accent=d.P.success, title_size=10.5)
    d.label(0.5, b + 0.25, 9.0, 0.3,
            "対象業界の例: 金融 ／ 医療 ／ 製造・サプライチェーン ／ エネルギー ／ 知的財産",
            size=10.5, align="CENTER", color=d.P.text)
    d.asset_icon_row(1.7, b + 0.75, 6.6, [
        ("evidence-chain", "証拠チェーン"), ("timestamp", "タイムスタンプ"),
        ("tamper-check", "改ざん検証"), ("consent", "同意記録"),
    ], size=0.52, label_size=8.5, color=d.P.success)


# ---------------------------------------------------------------- デッキ構成

def build_plan():
    """最終ページ順。("kept", 削除後の同梱スライド序数) か ("new", 種別, spec)。"""
    return [
        ("kept", 0),   # 表紙（テキスト置換）
        ("kept", 1),   # 免責事項
        ("new", "content", dict(
            title="本日のアジェンダ",
            body=[
                "1. 会社紹介 — 会社概要・ビジョン・沿革・直近のトピックス",
                "2. 製品紹介 — ScalarDB / ScalarDL の概要・アーキテクチャ・エディション",
                "3. ユースケース — 適用領域・導入顧客・事例・活用パターン",
            ],
            notes="本資料は 2026-08-01 時点の公開情報（scalar-labs.com / developers.scalar-labs.com / 各社プレスリリース）に基づく。")),
        ("new", "section", dict(title="1. 会社紹介",
                                body="会社概要・ビジョン・沿革・直近のトピックス")),
        ("kept", 2),   # 会社概要 VISION
        ("kept", 3),   # 役員構成
        ("new", "figure", dict(
            title="日本発、グローバル展開を目指す B2B ソフトウェア企業",
            draw=draw_company_data,
            notes="出典: scalar-labs.com/ja/company、STARTUP DB（従業員数 約50名は 2026年7月時点）。資本金は一次情報未確認のため非掲載。")),
        ("new", "figure", dict(
            title="創業から約 8 年、研究開発と事業展開を積み重ねてきた",
            draw=draw_history,
            notes="出典: 各プレスリリース。シリーズA 15億円（2022年11月、三井住友海上キャピタル等）。VLDB 採択は 2022・2023 年。")),
        ("new", "content", dict(
            title="直近 1 年でも製品強化とパートナー協業が加速している",
            body=[
                "2026.05　ScalarDB 3.18 リリース — ABAC 強化・Google Cloud Spanner 対応・性能向上",
                "2026.03　ScalarDL 3.13 リリース — ネームスペース管理・Java 21 対応",
                "2026.01　Kong 社とパートナーシップ締結 — API 基盤 × 分散データ基盤で内製化を支援",
                "2025.12　ScalarDB 3.17 — スキーマ変更「ゼロ」での既存 DB 導入を実現",
                "2025.10　ScalarDB MCP Server 公開 — LLM・AI エージェントからの活用に対応",
                "2025.10　ゼンリンと AI 活用不動産提案サービスを共同開発",
                "2025.06　NSW とメインフレームモダナイゼーションサービスを強化",
                "2025.04　24/7 対応型コーポレート PPA の実証に成功（電力分野）",
            ],
            notes="出典: scalar-labs.com/ja/news、各社プレスリリース。ScalarDL 3.13 のリリース日は公式リリースノート（2026-03-25）準拠。")),
        ("new", "section", dict(title="2. 製品紹介",
                                body="ScalarDB / ScalarDL — 概要・アーキテクチャ・エディション")),
        ("kept", 4),   # Scalar Product Overview
        ("new", "figure", dict(
            title="データ活用の現場には「分散」と「信頼」の 2 つの壁がある",
            draw=draw_challenges)),
        ("new", "content", dict(
            title="ScalarDB: 異種複数 DB を仮想統合する Universal HTAP エンジン",
            body=[
                "アプリとデータベースの間に立つミドルウェア。異種複数の DB を仮想的に統合し、DB 横断の ACID トランザクションとリアルタイム分析を実現",
                "独自の分散トランザクションプロトコル「Consensus Commit」により、特定 DB の機能に依存せずトランザクションを保証",
                "対応 DB: MySQL・PostgreSQL・Oracle・SQL Server・Db2 などの RDBMS、Aurora・Spanner・YugabyteDB などの NewSQL、DynamoDB・Cassandra・Cosmos DB などの NoSQL",
                "インターフェース: Java API / SQL（JDBC）/ GraphQL / .NET SDK / gRPC",
                "Core は 2018 年から OSS（Apache License 2.0）として公開。VLDB 2023 採択論文に基づく技術基盤",
            ],
            notes="出典: scalardb.scalar-labs.com/docs/latest/（overview / design / requirements）。最新バージョンは 3.18.0（2026-05-01）。")),
        ("new", "figure", dict(
            title="1 つのトランザクションで複数のデータベースをまたいで整合性を保つ",
            draw=draw_db_arch,
            notes="ScalarDB Cluster は Kubernetes 上で稼働。トランザクション保証にはアプリが ScalarDB を経由してアクセスすることが前提。")),
        ("new", "figure", dict(
            title="OSS の Core から企業向け Cluster・Analytics まで段階的に選べる",
            draw=draw_db_lineup,
            notes="料金例（マーケットプレイス・Pod=2vCPU/4GB 相当）: Enterprise Standard $1.40/h、Premium $2.79/h（AWS）。SQL インターフェースの所属エディションは公式ドキュメント間で表記揺れあり。")),
        ("new", "content", dict(
            title="ScalarDL: 改ざんを「防ぐ」のではなく確実に「検知」する",
            body=[
                "データ改ざんを含む「ビザンチン故障」を検知するミドルウェア。改ざんが起きていないことを検証できる（tamper-evident）データベースを実現",
                "わずか 2 つの管理ドメインで検知が成立し、ブロックチェーンのような多数のノードや合意形成を必要としない",
                "数万 TPS までリニアにスケールし、ACID・正確なファイナリティ・線形化可能な一貫性を提供",
                "データは Asset（資産）として追記型で管理し、Contract（デジタル署名付きビジネスロジック）で操作",
                "内部で ScalarDB を活用し、MySQL・PostgreSQL・DynamoDB など様々な DB 上に構築可能",
                "VLDB 2022 採択論文に基づく技術。エディションは Community / Enterprise",
            ],
            notes="出典: scalardl.scalar-labs.com/docs/latest/（overview / design）。最新バージョンは 3.13.0（2026-03-25）。")),
        ("new", "figure", dict(
            title="管理主体を分けた Ledger と Auditor が相互に検証し合う",
            draw=draw_dl_auditor,
            notes="検知プロトコル: Auditor が事前順序付け → Ledger が実行・コミット → Auditor が検証。改ざんがあれば両者の状態が乖離し、クライアントが応答の不一致で検知する。")),
        ("new", "figure", dict(
            title="記録は鎖状につながり、書き換えれば必ず検知される",
            draw=draw_dl_evidence)),
        ("new", "section", dict(title="3. ユースケース",
                                body="適用領域・導入顧客・事例・活用パターン")),
        ("kept", 5),   # 適用領域の例
        ("kept", 6),   # 導入顧客
        ("kept", 7),   # トヨタ PCE 事例
        ("kept", 8),   # 大手放送局 事例
        ("new", "figure", dict(
            title="ScalarDB はデータ統合・一貫性・モダナイゼーションで効く",
            draw=draw_db_patterns,
            notes="出典: scalardb.scalar-labs.com/docs/latest/overview/。生成 AI・RAG は LayerX「Ai Workforce」協業（2024.10）、レガシー移行は NSW 協業が対応する公表事例。")),
        ("new", "figure", dict(
            title="ScalarDL は証拠保全・トレーサビリティ・監査で効く",
            draw=draw_dl_patterns,
            notes="出典: scalardl.scalar-labs.com/docs/latest/overview/。証拠保全はトヨタ PCE、トレーサビリティは環境価値プラットフォームが対応する公表事例。")),
        ("new", "content", dict(
            title="エネルギー・金融・AI まで、公表事例は広がり続けている",
            body=[
                "イーネットワークシステムズ: 電力量 30 分値の格納基盤に ScalarDB を採用し、法定帳票の作成業務を 5 分の 1 に短縮",
                "J-POWER・インダストリー・ワン・NSW: 再エネの環境価値を追跡する「環境価値プラットフォーム」を ScalarDL で共同開発（2025 年〜）",
                "NSW: COBOL 資産を大幅修正せずオープン環境へ移行するメインフレームモダナイゼーションを ScalarDB で共同展開",
                "LayerX「Ai Workforce」: サイロ化した異種データソースを ScalarDB で単一リポジトリ化し、生成 AI によるドキュメント生成の精度を向上（2024 年〜）",
                "トヨタファイナンシャルサービス: 分散型台帳による B2C 取引データ管理の実証で、真正性・追跡可能性を確認",
            ],
            body_font_size=13,
            notes="出典: 各社プレスリリース（ENS 事例インタビュー、J-POWER 2025-01-06、NSW 2023、LayerX 2024-10-09、トヨタファイナンシャルサービス 2020-03）。定量効果が公表されているのは ENS の 1/5 のみ。")),
        ("kept", 9),   # クロージング
    ]


# ---------------------------------------------------------------- 生成

def draw_page_number(deck, ref, number: int) -> None:
    """生成スライドへ最終ページ位置の番号を描く（add_page_numbers の単票版）。"""
    cfg = deck.template.get("pageNumber", {})
    layout = ref["layout"]
    geo = layout.get("elements", {}).get("slideNumber")
    if not layout.get("hasPageNumber") or not geo:
        return
    right = geo["x"] + geo["w"]
    w = max(geo["w"], 0.5)
    x = right - w
    oid = deck._next_id("pagenum")
    deck.requests += [
        {"createShape": {
            "objectId": oid, "shapeType": "TEXT_BOX",
            "elementProperties": {
                "pageObjectId": ref["slideId"],
                "size": {"width": {"magnitude": _auth.inches(w), "unit": "EMU"},
                         "height": {"magnitude": _auth.inches(geo["h"]), "unit": "EMU"}},
                "transform": {"scaleX": 1, "scaleY": 1,
                              "translateX": _auth.inches(x),
                              "translateY": _auth.inches(geo["y"]), "unit": "EMU"},
            }}},
        {"insertText": {"objectId": oid, "text": str(number)}},
        {"updateTextStyle": {
            "objectId": oid,
            "style": {"fontFamily": cfg.get("font", "Arial"),
                      "fontSize": {"magnitude": cfg.get("fontSize", 7), "unit": "PT"},
                      "foregroundColor": {"opaqueColor": {
                          "rgbColor": _auth.hex_to_rgb(cfg.get("color", "#666666"))}}},
            "textRange": {"type": "ALL"},
            "fields": "fontFamily,fontSize,foregroundColor"}},
        {"updateParagraphStyle": {
            "objectId": oid, "style": {"alignment": "END"},
            "textRange": {"type": "ALL"}, "fields": "alignment"}},
    ]


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--folder", default=None)
    p.add_argument("--dry-run", action="store_true",
                   help="API を呼ばずに座標・文字量だけ検査する")
    args = p.parse_args()

    template = bd.load_template(TEMPLATE)
    if args.dry_run:
        deck = bd.DryRunDeck(template)
    else:
        deck = bd.TemplateDeck.create(template, title=TITLE, folder=args.folder,
                                      keep_existing=True)

    # 残した同梱スライドの間引きと表紙の文言置換。どちらも複製後の実物が要る
    # （ID を引くのに API を叩く）ので、--dry-run では丸ごと飛ばす。ここで作る
    # のはリクエストだけで、以降の作図と検査には影響しない
    if not args.dry_run:
        pres = deck.slides.presentations().get(
            presentationId=deck.presentation_id, fields="slides.objectId").execute()
        ids = [s["objectId"] for s in pres.get("slides", [])]
        # assert は python -O で消えるので、明示的に検査する
        if len(ids) != 12:
            raise RuntimeError(t("Expected 12 bundled slides, got {n}", n=len(ids)))
        for pos in DROP_KEPT_POSITIONS:
            deck.requests.append({"deleteObject": {"objectId": ids[pos]}})

        # 表紙の文言置換（<Proposal Title> の表紙は上で削除済み）
        for old, new in [("<Presentation Title>", TITLE), ("<Sub Title>", SUBTITLE),
                         ("YYYY月MM月", DATE), ("YYYY年MM月", DATE)]:
            deck.requests.append({"replaceAllText": {
                "containsText": {"text": old, "matchCase": True},
                "replaceText": new}})

    plan = build_plan()
    problems: list[str] = []
    for i, entry in enumerate(plan):
        if entry[0] == "kept":
            continue
        _, kind, spec = entry
        notes = spec.get("notes")
        if kind == "content":
            ref = deck.add_slide(
                "CONTENT", title=spec["title"], body=spec["body"], notes=notes,
                index=i, body_font_size=spec.get("body_font_size", 14),
                body_line_spacing=150)
        elif kind == "section":
            ref = deck.add_slide("SECTION", title=spec["title"],
                                 body=spec.get("body"), notes=notes, index=i)
        elif kind == "figure":
            ref = deck.add_slide("TITLE_ONLY", title=spec["title"], notes=notes,
                                 index=i)
            d = Canvas(deck, ref["slideId"], template)
            spec["draw"](d)
            problems += [f"p{i + 1} {spec['title'][:14]}…: {m}" for m in
                         (d.audit_bounds() + d.audit_connectors()
                          + d.audit_overlaps() + d.audit_text_fit())]
        else:
            raise ValueError(kind)
        draw_page_number(deck, ref, i + 1)

    for m in problems:
        print(t("  audit: {message}", message=m))

    if args.dry_run:
        print(f"\ndry-run: {len(problems)} problems")
        return 1 if problems else 0

    url = deck.commit()
    print(t("Done! {n} slides. Open: {url}", n=len(plan), url=url))
    return 0


if __name__ == "__main__":
    sys.exit(main())
