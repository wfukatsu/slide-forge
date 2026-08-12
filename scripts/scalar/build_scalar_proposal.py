#!/usr/bin/env python3
"""Customer-challenge-driven Scalar product proposal deck (problem-solving type, worked example).

The structure concretizes the "problem-solving proposal" from
references/deck-outlines.md for Scalar proposals (design rationale in
references/scalar/proposal-map.md). This file is a sample deal assuming "data
fragmentation in a manufacturer's core system"; for a real deal, rewrite the
PROPOSAL data block at the top with hearing results and rerun.

Ground rules when rewriting:
- Only write customer-specific figures (effort, counts, amounts) that came from
  actual hearings. If not obtained, don't write it (don't leave 〈 〉 placeholders either)
- Only include quantified expected-effect figures that can be backed by a stated
  basis. Otherwise state qualitatively and make explicit that "quantitative
  figures will be measured during the PoC"
- Case studies and pricing follow references/scalar/research-2026-08.md (3-month freshness rule)

  Run:    .venv/bin/python scripts/scalar/build_scalar_proposal.py [--folder <URL>]
  Check:  .venv/bin/python scripts/scalar/build_scalar_proposal.py --dry-run
"""
from __future__ import annotations

import argparse
import os
import sys

REPO_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(REPO_DIR, "scripts"))

import build_deck as bd  # noqa: E402
from diagrams import Canvas, lighten  # noqa: E402
from _i18n import t, register  # noqa: E402

register({
    "  audit: {message}": "  検査: {message}",
    "Done! Open: {url}": "完了! URL: {url}",
    "=== Bill of Materials (BOM) ===": "=== 構成内訳（BOM） ===",
    "[Cloud services ({cloud})]": "[クラウドサービス（{cloud}）]",
    "[Scalar products]": "[Scalar 製品]",
    "  Total (estimated monthly license): {total}": "  合計（ライセンス月額概算）: {total}",
})

TEMPLATE = os.path.join(REPO_DIR, "templates", "scalar-2026.json")

# ============================================================ Proposal data
# For a real deal, rewrite only this block. Figure coordinates and part selection are handled by the drawing code below.

PROPOSAL = {
    "customer": "〈お客様名〉",
    "title": "基幹データ統合基盤のご提案",
    "subtitle": "ScalarDB による「止めない」データ統合",
    "date": "2026年8月",

    # Executive summary (situation -> complication -> resolution. Detailed enough for one-slide decision-making)
    "summary": {
        "situation": "受発注・在庫・会計が個別システムに分かれ、データ連携は夜間バッチと手作業の突合に依存している",
        "complication": "部門間のデータ不整合が常態化し、突合・二重入力の運用負荷が増え続け、新サービス開発も既存 DB の制約で停滞している",
        "resolution": "既存システムと DB を替えずに、ScalarDB でトランザクション層を統合する。PoC（2 ヶ月）で技術成立性を検証してから段階導入する",
        "points": [
            "既存 DB を使い続けたまま複数 DB 横断の ACID トランザクションを実現（全面刷新が不要）",
            "スモールスタート: PoC → MVP → 段階展開で、リスクと初期投資を抑える",
            "公表事例で同型の課題を解決済み（帳票業務 約1/5 の実績ほか）",
        ],
    },

    # Current state (write hearing results here)
    "current": {
        "systems": [("browser", "受発注管理\n(MySQL)"),
                    ("stack", "在庫管理\n(PostgreSQL)"),
                    ("chart", "会計\n(Oracle)")],
        "flow_note": "システム間の連携は夜間バッチ + CSV 手作業。翌朝まで各システムの数字が合わない",
        "so_what": "データの「正」がどこにも無く、突合作業が業務として固定化している",
    },

    # Challenges (up to 3 points. Only write challenges agreed on during hearings)
    "challenges": [
        ("二重入力・突合の運用負荷",
         "部門間で同じデータを入力し直し、月次で数字合わせの突合作業が発生している"),
        ("データ不整合による判断遅れ",
         "在庫・受注・会計の数字がリアルタイムに一致せず、締め処理まで経営数値が確定しない"),
        ("新サービス開発の停滞",
         "既存 DB 構成に手を入れられず、データを横断するサービスの企画が実現できない"),
    ],
    # Structure of the challenge (visible problems / root causes)
    "iceberg": {
        "above": ["二重入力・突合工数", "月次締めの遅延", "開発案件の滞留"],
        "below": ["システムごとに DB が分断され、横断トランザクションの仕組みが無い",
                  "整合性の担保が人手とバッチ運用に依存している",
                  "DB 刷新は業務停止リスクが大きく着手できない"],
    },

    # Target state and scope (To-Be, and making explicit what's out of scope)
    "tobe": {
        "before": ["各システムが個別に更新され、整合は夜間バッチ頼み",
                   "横断データはCSV 突合で翌日以降に判明",
                   "新規開発は DB 制約で長期化"],
        "after": ["業務トランザクションが複数 DB へ原子的に反映",
                  "どのシステムから見ても数字が一致",
                  "既存 DB を活かしたまま横断サービスを追加"],
        "scope_out": "対象外: 既存システムの画面・業務ロジックの改修、DB 製品の入れ替え、全社データ分析基盤（本提案の範囲はデータ整合層の構築）",
    },

    # Substance of the proposal (challenge -> solution -> effect mapping table)
    "mapping": [
        ("二重入力・突合の負荷", "複数 DB 横断の ACID トランザクション",
         "入力は 1 回になり、突合作業を廃止できる"),
        ("データ不整合・判断遅れ", "Consensus Commit による強整合",
         "各システムの数字が常に一致し、締めを待たず確認できる"),
        ("新サービス開発の停滞", "統一 API（SQL / GraphQL）+ 既存テーブル取込",
         "既存 DB のまま横断データを扱う新規開発が可能に"),
    ],

    # Comparison (why this solution — "the reason it has to be this")
    "alternatives": {
        "headers": ["評価軸", "全面刷新\n(DB 統合)", "連携バッチ\n増設", "ScalarDB\n(本提案)"],
        "rows": [
            ["既存システムへの影響", "全面改修", "小", "小(既存 DB 継続)"],
            ["データ整合性", "強い", "結果整合\n(タイムラグ)", "強い(ACID)"],
            ["初期投資・期間", "大(数年)", "小", "中(段階導入)"],
            ["整合性の運用負荷", "小", "突合が残る", "小(基盤が保証)"],
            ["将来の拡張", "刷新後は自由", "バッチが増殖", "統一 API で拡張"],
        ],
    },

    # Expected effects (how work changes. Quantitative figures only where hearing/measurement supports them)
    "effects": {
        "before": ["朝一の突合作業から始まる", "月次締め後にようやく数字が確定",
                   "新規案件は「DB がネック」で保留"],
        "after": ["突合そのものが不要になる", "日中いつでも一致した数字を参照",
                  "既存 DB のまま新サービスを企画できる"],
        "so_what": "削減工数などの定量効果は PoC で実測し、本導入の稟議に使える形でご報告する（公表事例では帳票業務 約1/5 の実績）",
    },

    # Case studies (published cases only. Follows research-2026-08.md)
    "cases": [
        ("エナジーソリューションズ (ENS)",
         "電力量 30 分値の管理に ScalarDB を採用。法定帳票業務を約 1/5 に削減"),
        ("常石造船",
         "15 年以上稼働した基幹モノリスを刷新。ScalarDB + AI 駆動開発で MVP を実質 3 ヶ月で構築"),
        ("大手放送局",
         "分断されていたコンテンツデータ管理を ScalarDB で統合（公式導入事例）"),
    ],
    "cases_source": "各社公表資料・Scalar 公式発表（2026年8月時点の調査、詳細は話者ノート参照）",

    # Approach (the PoC and its success criteria are a single package)
    "journey": [
        ("PoC（2 ヶ月）", "対象業務 1 本で技術成立性と性能を実測"),
        ("設計（1 ヶ月）", "対象範囲・移行計画・運用設計を確定"),
        ("MVP 構築（3 ヶ月）", "優先度最上位の業務フローを本番相当で構築"),
        ("段階展開", "業務単位に範囲を拡大。既存は並行稼働で守る"),
    ],
    "poc_criteria": "PoC 成功基準（例）: 対象業務の横断トランザクションが要件性能内で完了すること / 障害時に不整合が残らないこと / 削減効果の実測値が取れること",
    "gantt": {
        "columns": ["1ヶ月目", "2ヶ月目", "3ヶ月目", "4ヶ月目", "5ヶ月目", "6ヶ月目"],
        "rows": [
            ["キックオフ", 0.1, 0.1, "キックオフ"],
            ["PoC(技術検証)", 0.1, 2.0, "成立性・性能の実測"],
            ["評価・判断", 2.0, 2.0, "Go/No-Go"],
            ["設計", 2.0, 3.0],
            ["MVP 構築", 3.0, 6.0, "優先業務フロー"],
        ],
    },

    # System architecture (the standard 3-environment initial proposal. Default cloud is AWS)
    # The figure is examples/scalar-proposal-envs.drawio, rendered to PNG via drawio_export.py.
    # If rewritten for customer requirements, re-export it (see the drawio-diagrams skill)
    "architecture": {
        "diagram": os.path.join(REPO_DIR, "examples", "scalar-proposal-envs.png"),
        "drawio": "examples/scalar-proposal-envs.drawio",
        "cloud": "AWS",
        "caption": "初期提案の 3 環境。ローカルは無料の Community で開発し、"
                   "AWS 側 2 環境は同一構成をサイズ違いで用意して昇格させる",
        "envs": [
            {"name": "開発（ローカル）",
             "purpose": "各開発者の PC で完結する開発・単体検証",
             "services": "Docker Compose（業務アプリ + PostgreSQL コンテナ）",
             "scalar": "ScalarDB Core（Community）",
             "qty": "開発者数分", "monthly": "無料"},
            {"name": "テスト（aidd-infra-test）",
             "purpose": "結合テスト・自動テストの常設環境",
             "services": "EKS / NLB / RDS for PostgreSQL（Single-AZ）/ ECR / CloudWatch / S3",
             "scalar": "ScalarDB Cluster（Enterprise Standard）",
             "qty": "1 Pod", "monthly": "約 $1,022"},
            {"name": "ステージング（aidd-infra-staging）",
             "purpose": "本番同等構成での受入・性能検証",
             "services": "EKS（2 AZ）/ NLB / RDS for PostgreSQL（Multi-AZ）/ "
                         "Secrets Manager / CloudWatch / S3",
             "scalar": "ScalarDB Cluster（Enterprise Standard）",
             "qty": "3 Pod", "monthly": "約 $3,066"},
        ],
        "monthly_total": "約 $4,088/月",
        "monthly_note": "※ Scalar 製品ライセンスのみの概算（$1.40/h × Pod 数 × 730h で算定）。"
                        "AWS インフラ利用料・本番環境は別途",
        "source": "ScalarDB Cluster 価格: AWS Marketplace 公表値（2026年8月時点、Standard エディション）",
    },

    # Team structure (make the customer-side workload visible too)
    "team": ("ステアリングコミッティ\n(月次)",
             [("〈お客様〉PM\n業務部門・情シス", []),
              ("Scalar\nアーキテクト", []),
              ("Scalar\n導入支援", []),
              ("開発パートナー\n(SIer)", [])]),
    "team_roles": [
        ["〈お客様〉", "業務要件の確定、PoC 評価、受入判断（想定稼働: 週数時間〜）"],
        ["Scalar", "アーキテクチャ設計、ScalarDB 導入支援、技術検証の主導"],
        ["開発パートナー", "アプリケーション実装、既存システムの改修影響調査"],
    ],

    # Estimated cost (line items and ranges. Make explicit these are estimates, not fixed values)
    "costs": {
        "rows": [
            ["PoC 支援", "2 ヶ月・Scalar エンジニア支援込み", "個別お見積り"],
            ["ScalarDB Cluster", "テスト 1 Pod + ステージング 3 Pod（構成内訳参照）",
             "約 $4,088/月〜"],
            ["構築・導入支援", "設計〜MVP 構築の伴走支援", "体制により個別お見積り"],
        ],
        "note": "※ 費目・金額は概算の目安。PoC 評価後に確定見積りをご提示",
        "source": "ScalarDB Cluster 価格: AWS Marketplace 公表値（2026年8月時点、Standard エディション）",
    },

    # Risks and mitigations (get ahead of objections)
    "risks": [
        ["既存システムへの影響", "既存 DB はそのまま。PoC は本番系と分離した環境で実施し、段階展開時も業務単位で並行稼働"],
        ["性能要件を満たせない", "PoC の成功基準に性能実測を含め、未達なら本導入に進まない（Go/No-Go を明示）"],
        ["運用・スキルの不安", "Scalar が設計〜構築を伴走。運用設計と引き継ぎまでを導入支援の範囲に含める"],
    ],

    # Next steps (what to decide today -> immediate action)
    "next": ["本日:\n課題認識の\nすり合わせ", "〜2 週間:\nPoC スコープ\n合意", "〜1 ヶ月:\nPoC 開始",
             "3 ヶ月後:\nGo/No-Go\n判断"],
}


# ============================================================ Drawing

def draw_current(d: Canvas, cur: dict) -> None:
    d.icon_flow(1.1, 1.35, 7.8, cur["systems"], size=0.78, label_size=9.5,
                arrow_color=d.P.muted)
    d.label(1.1, 2.95, 7.8, 0.3, cur["flow_note"], size=10.5,
            align="CENTER", color=d.P.muted)
    d.so_what(0.7, 3.75, 8.6, 0.85, cur["so_what"])


def draw_challenges(d: Canvas, items: list) -> None:
    d.cards(0.6, 1.25, 8.8, 2.1, items, accent=[d.P.primary, d.P.info, d.P.warning])
    d.label(0.6, 3.65, 8.8, 0.3,
            "※ 課題は御社ヒアリング（実案件では日付・出席者を明記）に基づく整理。認識齟齬があれば本日修正したい",
            size=9, align="START", color=d.P.muted)


def draw_iceberg(d: Canvas, data: dict) -> None:
    # The upper list fits within the iceberg's h*0.30-0.34 area. For 3 lines, h>=3.7 is required
    d.iceberg(0.7, 1.1, 8.4, 3.75, data["above"], data["below"],
              above_title="表出している問題", below_title="共通の根本原因", size=10)


def draw_tobe(d: Canvas, tobe: dict) -> None:
    d.before_after(0.6, 1.2, 8.8, 2.7, tobe["before"], tobe["after"],
                   before_title="現状 (As-Is)", after_title="目指す姿 (To-Be)", size=10.5)
    d.shape(0.6, 4.15, 8.8, 0.62, kind="RECTANGLE", fill=d.P.surfaceAlt,
            stroke=d.P.border, text=tobe["scope_out"], size=9.5, color=d.P.muted)


def draw_solution(d: Canvas, _p: dict) -> None:
    """The proposal figure for the ScalarDB unified transaction layer."""
    ac = d.P.primary
    d.icon_row(1.5, 1.15, 7.0, [("browser", "受発注"), ("stack", "在庫"),
                                ("chart", "会計"), ("bulb", "新サービス")],
               size=0.5, label_size=9)
    d.shape(1.2, 2.35, 7.6, 0.55, kind="ROUND_RECTANGLE", fill=ac, stroke=None,
            text="ScalarDB Cluster — 複数 DB 横断の ACID トランザクション / 統一 API",
            size=11, bold=True, color="#FFFFFF")
    d.icon_row(1.7, 3.35, 6.6, [("database", "MySQL\n(既存)"),
                                ("database", "PostgreSQL\n(既存)"),
                                ("database", "Oracle\n(既存)")],
               size=0.5, label_size=9)
    for cx in (2.45, 4.2, 5.95, 7.7):
        d.arrow(cx, 1.95, cx, 2.31, color=d.P.muted, weight=1.2, _anchored=True)
    for cx in (2.8, 5.0, 7.2):
        d.arrow(cx, 2.94, cx, 3.31, color=d.P.muted, weight=1.2, _anchored=True)
    d.label(0.7, 4.55, 8.6, 0.55,
            "アプリケーションは ScalarDB の統一 API を通して読み書きするだけで、"
            "複数 DB にまたがる更新の整合性を基盤が保証。既存 DB・既存システムはそのまま",
            size=10.5, align="CENTER", color=d.P.muted, line_spacing=130)


def draw_mapping(d: Canvas, rows: list) -> None:
    d.table(0.6, 1.3, 8.8, ["御社の課題", "ScalarDB の打ち手", "実現される状態"],
            [list(r) for r in rows], col_widths=[1.0, 1.1, 1.2], row_h=0.62,
            size=10, aligns=["START", "START", "START"])
    d.label(0.6, 4.0, 8.8, 0.3, "各機能の技術詳細は Appendix（機能紹介資料）にてご説明可能",
            size=9, align="START", color=d.P.muted)


def draw_alternatives(d: Canvas, alt: dict) -> None:
    d.table(0.6, 1.2, 8.8, alt["headers"], alt["rows"],
            col_widths=[1.2, 1.0, 1.0, 1.1], row_h=0.5, size=9.5)
    d.so_what(0.6, 4.35, 8.8, 0.85,
              "「既存を止めない」と「強整合」の両立が本提案の選定理由")


def draw_effects(d: Canvas, eff: dict) -> None:
    d.before_after(0.6, 1.2, 8.8, 2.5, eff["before"], eff["after"],
                   before_title="導入前の業務", after_title="導入後の業務", size=10.5)
    d.so_what(0.6, 4.0, 8.8, 0.95, eff["so_what"], label="定量化")


def draw_cases(d: Canvas, p: dict) -> None:
    d.cards(0.6, 1.25, 8.8, 2.3, p["cases"],
            accent=[d.P.primary, d.P.info, d.P.success], title_size=10.5,
            body_size=9.5)
    d.source_note(0.6, 4.75, 8.8, p["cases_source"])


def draw_journey(d: Canvas, p: dict) -> None:
    d.journey(0.6, 1.15, 8.8, 2.5, p["journey"], size=9.5)
    d.shape(0.6, 4.0, 8.8, 0.9, kind="RECTANGLE",
            fill=lighten(d.P.primary, 0.93), stroke=lighten(d.P.primary, 0.6),
            text=p["poc_criteria"], size=9.5, color=d.P.text)


def draw_architecture(d: Canvas, arch: dict) -> None:
    d.image(0.5, 1.05, 9.0, 3.25, arch["diagram"], fit="contain",
            caption=arch["caption"], outline=d.P.border)


def draw_bom_services(d: Canvas, arch: dict) -> None:
    # Split the environment name into 2 lines like "テスト\n（aidd-infra-test）". If left as
    # 1 line, the wrapped final line would be under 1 character relative to the column width, which audit_text_fit flags
    rows = [[e["name"].replace("（aidd", "\n（aidd"), e["purpose"], e["services"]]
            for e in arch["envs"]]
    d.table(0.6, 1.3, 8.8, ["環境", "役割", "主な構成サービス"], rows,
            col_widths=[1.2, 1.3, 2.0], row_h=0.72, size=9.5,
            aligns=["START", "START", "START"])
    d.label(0.6, 4.2, 8.8, 0.3,
            f"※ クラウドは {arch['cloud']} を既定として構成。指定があれば同じ役割分担で"
            " GCP / Azure に組み替える",
            size=9, align="START", color=d.P.muted)


def draw_bom_scalar(d: Canvas, arch: dict) -> None:
    rows = [[e["name"], e["scalar"], e["qty"], e["monthly"]] for e in arch["envs"]]
    rows.append(["合計（ライセンス月額）", "", "", arch["monthly_total"]])
    d.table(0.6, 1.25, 8.8, ["環境", "Scalar 製品", "数量", "月額概算"], rows,
            col_widths=[1.5, 1.7, 0.8, 1.0], row_h=0.5, size=9.5,
            aligns=["START", "START", "CENTER", "CENTER"])
    d.label(0.6, 4.0, 8.8, 0.45, arch["monthly_note"], size=9, align="START",
            color=d.P.muted, line_spacing=125)
    d.source_note(0.6, 4.75, 8.8, arch["source"])


def draw_gantt(d: Canvas, g: dict) -> None:
    rows = [tuple(r) for r in g["rows"]]
    d.gantt(0.6, 1.3, 8.8, 2.8, g["columns"], rows, size=9.5)
    d.label(0.6, 4.35, 8.8, 0.3,
            "※ PoC 評価（Go/No-Go）を通過した場合のみ設計以降に進む前提のスケジュール",
            size=9, align="START", color=d.P.muted)


def draw_team(d: Canvas, p: dict) -> None:
    d.orgchart(1.4, 1.15, 7.2, 2.0, p["team"], size=9)
    d.table(0.6, 3.45, 8.8, ["担当", "役割（想定負荷）"],
            [list(r) for r in p["team_roles"]], col_widths=[1.0, 3.2],
            row_h=0.42, size=9.5, aligns=["START", "START"])


def draw_costs(d: Canvas, c: dict) -> None:
    d.table(0.6, 1.3, 8.8, ["費目", "内容", "概算"],
            [list(r) for r in c["rows"]], col_widths=[1.0, 2.0, 1.2],
            row_h=0.52, size=10, aligns=["START", "START", "CENTER"])
    d.label(0.6, 3.6, 8.8, 0.3, c["note"], size=9.5, align="START",
            color=d.P.muted)
    d.source_note(0.6, 4.75, 8.8, c["source"])


def draw_risks(d: Canvas, rows: list) -> None:
    d.table(0.6, 1.3, 8.8, ["想定されるご懸念", "対策"],
            [list(r) for r in rows], col_widths=[1.0, 2.4], row_h=0.62,
            size=10, aligns=["START", "START"])


def draw_next(d: Canvas, steps: list) -> None:
    d.flow(0.7, 1.6, 8.6, 1.15, steps, size=10)
    d.so_what(0.7, 3.4, 8.6, 0.85,
              "本日は課題認識の確認と、PoC スコープ検討に進むかどうかのご判断をいただきたい",
              label="お願い")


def print_bom(arch: dict) -> None:
    """Also print the Bill of Materials (service list plus Scalar products, quantity, and monthly cost) to the console."""
    print("\n" + t("=== Bill of Materials (BOM) ==="))
    print(t("[Cloud services ({cloud})]", cloud=arch["cloud"]))
    for e in arch["envs"]:
        print(f"  - {e['name']}: {e['services']}")
    print(t("[Scalar products]"))
    for e in arch["envs"]:
        print(f"  - {e['name']}: {e['scalar']} × {e['qty']} — {e['monthly']}")
    print(t("  Total (estimated monthly license): {total}",
            total=arch["monthly_total"]))
    print(f"  {arch['monthly_note']}")


# ============================================================ Assembly

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--folder", default=None)
    p.add_argument("--dry-run", action="store_true",
                   help="API を呼ばずに座標・文字量だけ検査する")
    args = p.parse_args()

    P = PROPOSAL
    template = bd.load_template(TEMPLATE)
    if args.dry_run:
        deck = bd.DryRunDeck(template)
    else:
        deck = bd.TemplateDeck.create(
            template, title=f"{P['customer']}様向け {P['title']}", folder=args.folder)
    problems: list[str] = []

    def drawn(title, fn, *fn_args, notes=None, connectors=False):
        ref = deck.add_slide("TITLE_ONLY", title=title, notes=notes)
        d = Canvas(deck, ref["slideId"], template)
        fn(d, *fn_args)
        audits = d.audit_bounds() + d.audit_overlaps() + d.audit_text_fit()
        if connectors:
            audits += d.audit_connectors()
        problems.extend(f"{title[:14]}…: {m}" for m in audits)

    # 0. Cover
    deck.add_slide("COVER", title=f"{P['customer']}様向け\n{P['title']}",
                   subtitle=P["subtitle"], body=f"{P['date']}\n株式会社Scalar",
                   notes="実案件では customer / date を書き換える。")

    # 1. Executive summary (conclusion first. Detailed enough for one-slide decision-making)
    ref = deck.add_slide(
        "TITLE_ONLY", title="エグゼクティブサマリ — 既存を止めずにデータ分断を解消する",
        notes="才流・HubSpot の提案書構成調査より: 決裁者は冒頭の要約しか読まない前提で、"
              "課題・解決策・進め方をこの 1 枚に集約する。")
    d = Canvas(deck, ref["slideId"], template)
    s = P["summary"]
    d.exec_summary(0.6, 1.1, 8.8, 3.95, s["situation"], s["complication"],
                   s["resolution"], points=s["points"], size=10)
    problems.extend(f"サマリ: {m}" for m in
                    (d.audit_bounds() + d.audit_overlaps() + d.audit_text_fit()))

    # 2. Building agreement on the challenge (placed before the solution)
    drawn("背景と現状 — システムごとにデータが分断されている", draw_current, P["current"],
          notes="現状認識の合意が提案全体の前提。ヒアリング結果をそのまま書き、"
                "推測で補わない。図の DB 名・システム名は実環境に合わせる。")
    drawn("課題の整理 — 解決すべきは 3 点", draw_challenges, P["challenges"],
          notes="課題は 3 点まで（deck-outlines.md）。順番は打ち手の対応表と揃える。")
    drawn("課題の構造 — 3 つの問題は同じ根本原因から生じている", draw_iceberg, P["iceberg"],
          notes="対症療法（RPA で突合を自動化等）との差別化の土台になるスライド。")

    # 3. The proposal
    deck.add_slide("SECTION", title="ご提案", body="目指す姿と ScalarDB による解決策")
    drawn("目指す姿 — 既存システムを活かしたまま、数字が常に一致する状態へ",
          draw_tobe, P["tobe"],
          notes="スコープ外の明示（HubSpot: 含まれない業務を明記して期待値を制御）。")
    drawn("ご提案 — ScalarDB による統合トランザクション層", draw_solution, P,
          connectors=True,
          notes="ScalarDB: Universal HTAP エンジン。Consensus Commit により既存 DB を"
                "替えずに複数 DB 横断の ACID を実現（research-2026-08.md）。"
                "密な構成図が必要な案件では drawio-diagrams スキルで別途作図する。")
    drawn("課題と打ち手の対応 — 3 つの課題すべてに答えを持つ", draw_mapping, P["mapping"],
          notes="課題スライドと同じ順序・同じ文言で対応させる（読み手に再解釈させない）。")
    drawn("打ち手の比較 — 既存を止めずに強整合を保てるのは本提案のみ",
          draw_alternatives, P["alternatives"],
          notes="才流: 稟議には「これでないといけない理由」が必要。比較軸は顧客の"
                "評価基準（KBF）に合わせて書き換える。")
    drawn("期待効果 — 突合作業が業務から消える", draw_effects, P["effects"],
          notes="機能ではなく業務の変化を語る（才流の模擬商談検証）。根拠のない定量値は"
                "書かない。PoC で実測し稟議材料にする、という筋書きに乗せる。")
    drawn("導入事例 — 同型の課題を公表事例で解決済み", draw_cases, P,
          notes="出典: ENS(法定帳票 約1/5・唯一の公表定量効果) / 常石造船(2026.6 発表、"
                "MVP 実質 3 ヶ月) / 大手放送局(公式 boilerplate 掲載)。"
                "research-2026-08.md の鮮度 3 ヶ月ルールに従い再調査してから使う。")

    # 4. Approach
    deck.add_slide("SECTION", title="導入の進め方", body="スモールスタートで確実に")
    drawn("導入アプローチ — PoC で検証してから段階導入", draw_journey, P,
          notes="PoC は成功基準（Go/No-Go）までがワンセット（エンプラ IT 提案の定石）。")
    drawn("提案システム構成 — 開発・テスト・ステージングの 3 環境", draw_architecture,
          P["architecture"],
          notes="初期提案の標準 3 環境（ローカル / aidd-infra-test / aidd-infra-staging）。"
                "クラウド既定は AWS。図の元データは examples/scalar-proposal-envs.drawio で、"
                "顧客要件に合わせて drawio-diagrams スキルで書き換えてから "
                "scripts/drawio_export.py で PNG を再生成する。環境名・本番環境の扱いは"
                "ヒアリングに合わせて変更する。")
    drawn("構成内訳（1）— 各環境のサービス構成", draw_bom_services, P["architecture"],
          notes="クラウドサービスのリスト。環境の役割分担（ローカル無料 → テスト最小 → "
                "ステージング本番同等）が崩れない範囲でサービスを増減する。")
    drawn("構成内訳（2）— Scalar 製品と数量・月額概算", draw_bom_scalar, P["architecture"],
          notes="Scalar 製品の数量と月額概算。数量の指定が無い場合は既定サイズ"
                "（テスト 1 Pod / ステージング 3 Pod）で月額を算定する。"
                "$1.40/h × Pod 数 × 730h。価格出典は AWS Marketplace（2026-08 時点）。")
    drawn("スケジュール案 — 6 ヶ月で MVP まで", draw_gantt, P["gantt"],
          notes="ヒアリングした導入希望時期・予算年度に合わせて列と行を書き換える。")
    drawn("推進体制案 — 御社・Scalar・開発パートナーの三者体制", draw_team, P,
          notes="顧客側の負担（想定稼働）を明示すると「工数がかからない」ことが伝わる。")
    drawn("概算費用 — スモールスタートを前提とした費用構成", draw_costs, P["costs"],
          notes="価格を出す位置は解決策・効果の後（HubSpot）。ライセンス単価の出典は "
                "AWS Marketplace 公表値。個別見積り項目を勝手に金額化しない。")
    drawn("想定されるご懸念と対策", draw_risks, P["risks"],
          notes="リスクの先回り（才流 稟議書 8 項目）。顧客から出た懸念は必ずここに足す。")

    # 5. Closing
    drawn("次のステップ — 本日ご判断いただきたいこと", draw_next, P["next"],
          notes="次のアクションを明示して送りっぱなしにしない（HubSpot)。")
    deck.add_slide("CLOSING")

    deck.add_page_numbers()
    for m in problems:
        print(t("  audit: {message}", message=m))
    if args.dry_run:
        print(f"\ndry-run: {len(problems)} problems")
        return 1 if problems else 0

    url = deck.commit()
    print(t("Done! Open: {url}", url=url))
    print_bom(P["architecture"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
