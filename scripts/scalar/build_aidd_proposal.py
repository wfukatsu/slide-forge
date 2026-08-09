#!/usr/bin/env python3
"""ScalarDB を使った AI 駆動開発の提案デッキ（PoC 提案 / 開発・テストの 2 環境前提）。

build_scalar_proposal.py（3 環境の worked example）を土台に、
「AI 駆動開発を回すための開発環境とテスト環境を用意する」前提へ書き換えたもの。
顧客名は未特定のため〈〇〇株式会社〉の仮置き（汎用の型）。

書き換え時の鉄則（元の worked example と同じ）:
- 顧客固有の数値（工数・件数・金額）はヒアリングで取れたものだけ書く
- 期待効果の定量値は算定根拠を添えられるものだけ。無ければ定性で書き、
  「定量は PoC で実測」と明示する
- 事例・価格は references/scalar/research-2026-08.md 準拠（鮮度 3 ヶ月ルール）

  実行: .venv/bin/python scripts/scalar/build_aidd_proposal.py [--folder <URL>]
  検査: .venv/bin/python scripts/scalar/build_aidd_proposal.py --dry-run
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

# ============================================================ 提案データ

PROPOSAL = {
    "customer": "〇〇株式会社",
    "title": "AI 駆動開発基盤のご提案",
    "subtitle": "ScalarDB を土台に、AI が自走する開発サイクルをつくる",
    "date": "2026年8月",

    # エグゼクティブサマリ（状況 → 課題 → 答え。1 枚で意思決定できる粒度）
    "summary": {
        "situation": "コーディングエージェントを開発に導入し、コードが書かれる速さは確かに上がっている",
        "complication": "一方でデータ整合性の担保がレビュー頼みで、手元に再現環境も常設テスト環境も無いため、"
                        "AI が生成 → テスト → 修正を自走できず、結局リードタイムが縮まっていない",
        "resolution": "ScalarDB を統一データアクセス層に据え、開発（ローカル）とテスト（aidd-infra-test）の"
                      "2 環境を用意する。PoC（2 ヶ月）で AI の自走率とリードタイムを実測してから展開する",
        "points": [
            "整合性は基盤が保証: 分散 ACID により、AI が書いた横断更新をレビューで担保しなくてよくなる",
            "AI が自走できる環境: ローカルは Community 版で無料。全開発者が同一構成でテストまで完走できる",
            "有償はテスト環境 1 Pod のみ: 月額約 $1,022 からスモールスタート（AWS 公表値ベース）",
        ],
    },

    # 現状（ヒアリング結果を書く。ここは汎用の型としての整理）
    "current": {
        "systems": [("bulb", "AI がコードを\n書く"),
                    ("browser", "人がレビューで\n整合性を確認"),
                    ("stack", "共有環境で\nまとめてテスト")],
        "flow_note": "AI の出力は速いが、その後段の確認と検証が人手と順番待ちに依存している",
        "so_what": "速くなったのは「書く」工程だけで、マージまでのリードタイムは変わっていない",
    },

    # 課題（3 点まで。打ち手の対応表と同順・同文言）
    "challenges": [
        ("整合性の担保がレビュー頼み",
         "複数 DB・複数サービスにまたがる更新の整合性が、実装ごとの書き方とレビューに委ねられている"),
        ("手元に再現環境が無い",
         "開発者ごとに環境が異なり、AI が自分でテストを回して直すループが手元で成立しない"),
        ("検証が生成速度に追いつかない",
         "結合テストを回せる常設環境が無く、検証が共有環境の順番待ちと手作業になっている"),
    ],
    # 課題の構造（見えている問題 / 根本原因）
    "iceberg": {
        "above": ["レビュー待ち・指摘の往復", "環境差異による「手元では動く」", "結合テストの順番待ち"],
        "below": ["データアクセス層が DB ごとにばらばらで、整合性の担保が実装者と"
                  "レビュアーの力量に依存している",
                  "全開発者が同一構成をローカルに再現する手段が無い",
                  "AI が自分で結果を確かめられる常設のテスト環境が無い"],
    },

    # 目指す姿とスコープ（To-Be と、やらないことの明示）
    "tobe": {
        "before": ["整合性の正しさを人がレビューで判定",
                   "動作確認は共有環境で順番待ち",
                   "AI の出力は人が検証するまで進まない"],
        "after": ["整合性は ScalarDB が保証し、レビューは業務ロジックに集中",
                  "ローカルとテスト環境の 2 段で即座に検証",
                  "AI が自走してから人のレビューに渡る"],
        "scope_out": "対象外: ステージング・本番環境の構築、既存システムの業務ロジック改修、"
                     "AI コーディングツール自体の選定・調達（本提案の範囲は開発・テストの 2 環境とデータ層）",
    },

    # 提案の中身（課題 → 打ち手 → 効果の対応表）
    "mapping": [
        ("整合性の担保が\nレビュー頼み",
         "ScalarDB の分散 ACID\n（Consensus Commit）",
         "整合性は基盤が保証。レビューは業務ロジックに集中できる"),
        ("手元に\n再現環境が無い",
         "開発環境: Docker Compose +\nScalarDB Core（Community・無料）",
         "全開発者が同一構成。AI が手元でテストまで完走できる"),
        ("検証が\n生成速度に追いつかない",
         "テスト環境 aidd-infra-test:\nEKS + ScalarDB Cluster 1 Pod",
         "CI から結合テストが自動で回り、マージ前に判定できる"),
    ],

    # 比較（なぜこの打ち手か。「これでないといけない理由」）
    "alternatives": {
        "headers": ["評価軸", "AI ツール\n導入のみ", "自作の抽象化層\n+ 共有環境", "ScalarDB + 2 環境\n(本提案)"],
        "rows": [
            ["横断更新の整合性保証", "無し\n(レビュー依存)", "自作分だけ\n(自前で保守)", "基盤が保証\n(分散 ACID)"],
            ["AI の自走（生成→テスト→修正）", "不可\n(検証環境が無い)", "共有環境の\n順番待ち", "ローカルで完走"],
            ["開発者間の環境再現性", "各自バラバラ", "各自バラバラ", "全員同一構成"],
            ["立ち上げ期間", "即日", "設計・実装が必要", "2 環境で 2〜4 週間"],
            ["DB の追加・変更への追従", "都度実装", "自作層の改修", "統一 API のまま"],
        ],
    },

    # 期待効果（業務がどう変わるか。定量はヒアリング/実測が取れたものだけ）
    "effects": {
        "before": ["整合性の担保にレビュー工数を割いている",
                   "環境差異による手戻りが定期的に発生",
                   "結合テストは共有環境の空き待ち"],
        "after": ["レビューは業務ロジックの妥当性に集中",
                  "同一構成なので「手元では動く」が起きない",
                  "push のたびに結合テストが自動で回る"],
        "so_what": "定量効果は PoC で実測して稟議材料にする"
                   "（公表事例では 15 年以上稼働したモノリスを MVP 実質 3 ヶ月で刷新）",
    },

    # 事例（公表事例のみ。research-2026-08.md 準拠）
    "cases": [
        ("常石造船 — 基幹システムの刷新",
         "15 年以上稼働したモノリスを ScalarDB + Kong で刷新。現状分析・再設計 2 日、"
         "MVP 実質 3 ヶ月、9 マイクロサービス構成（2026.6 発表）"),
        ("LayerX Ai Workforce",
         "散在する社内データへの AI からのアクセス基盤として ScalarDB を採用（2024.10）"),
        ("エナジーソリューションズ (ENS)",
         "電力量 30 分値の管理に ScalarDB を採用。法定帳票業務を約 1/5 に削減"),
    ],
    "cases_source": "各社公表資料・Scalar 公式発表（2026年8月時点の調査、出典 URL は話者ノート参照）",

    # 進め方（PoC の成功基準までがワンセット）
    "journey": [
        ("環境構築（2〜4 週間）", "開発（ローカル）とテスト環境を立ち上げる"),
        ("PoC（2 ヶ月）", "対象機能 1 本を AI 駆動開発で実装し実測"),
        ("評価（Go/No-Go）", "自走率・リードタイム・性能で判断"),
        ("展開", "チームと対象範囲を拡大。上位環境は別途設計"),
    ],
    "poc_criteria": "PoC 成功基準（例）: AI が人手介在なしで生成→テスト→修正を完走した割合が目標値に達すること / "
                    "横断トランザクションが要件性能内で完了すること / 着手〜マージのリードタイムの実測値が取れること",
    "gantt": {
        "columns": ["1ヶ月目", "2ヶ月目", "3ヶ月目", "4ヶ月目"],
        "rows": [
            ["キックオフ", 0.1, 0.1, "スコープ合意"],
            ["環境構築", 0.1, 1.0, "開発・テストの 2 環境"],
            ["PoC 実施", 1.0, 3.0, "AI 駆動開発で実装・実測"],
            ["評価・判断", 3.0, 3.4, "Go/No-Go"],
            ["展開計画", 3.4, 4.0],
        ],
    },

    # システム構成（ご指定の 2 環境。クラウド既定は AWS）
    "architecture": {
        "diagram": os.path.join(REPO_DIR, "examples", "scalar-proposal-aidd-envs.png"),
        "drawio": "examples/scalar-proposal-aidd-envs.drawio",
        "cloud": "AWS",
        "caption": "ローカルは無料の Community 版。テスト環境は同じ構成を "
                   "ScalarDB Cluster に置き換えた常設環境",
        "envs": [
            {"name": "開発（ローカル）",
             "purpose": "AI エージェントが生成→テスト→修正を完走する開発・単体検証",
             "services": "Docker Compose（業務アプリ + 自動テスト + PostgreSQL コンテナ）",
             "scalar": "ScalarDB Core（Community）",
             "qty": "開発者数分", "monthly": "無料"},
            {"name": "テスト（aidd-infra-test）",
             "purpose": "CI から結合テストを自動で回す常設環境",
             "services": "EKS / NLB / RDS for PostgreSQL（Single-AZ）/ ECR / CloudWatch / S3",
             "scalar": "ScalarDB Cluster（Enterprise Standard）",
             "qty": "1 Pod", "monthly": "約 $1,022"},
        ],
        "monthly_total": "約 $1,022/月",
        "monthly_note": "※ Scalar 製品ライセンスのみの概算（$1.40/h × Pod 数 × 730h で算定）。"
                        "AWS インフラ利用料は別途。ステージング・本番環境は本提案の範囲外",
        "source": "ScalarDB Cluster 価格: AWS Marketplace 公表値（2026年8月時点、Standard エディション）",
    },

    # 体制（お客様側の負担も見えるように）
    "team": ("PoC 推進会議\n(隔週)",
             [("〇〇株式会社\n開発チーム", []),
              ("Scalar\nアーキテクト", []),
              ("Scalar\n導入支援", [])]),
    "team_roles": [
        ["〇〇株式会社", "対象機能の選定、AI 駆動開発の実施、PoC 評価（想定稼働: 開発者 2〜3 名）"],
        ["Scalar アーキテクト", "データモデル・トランザクション設計、ScalarDB 適用範囲の確定"],
        ["Scalar 導入支援", "2 環境の構築支援、CI 連携、技術 QA と運用の引き継ぎ"],
    ],

    # 概算費用（費目と幅。確定値ではなく概算であることを明示）
    "costs": {
        "rows": [
            ["開発環境（ローカル）", "ScalarDB Core（Community）× 開発者数", "無料"],
            ["テスト環境ライセンス", "ScalarDB Cluster Standard × 1 Pod（常設）", "約 $1,022/月〜"],
            ["PoC 支援", "2 ヶ月・Scalar エンジニアの伴走支援込み", "個別お見積り"],
            ["環境構築支援", "2 環境の構築・CI 連携・運用引き継ぎ", "体制により個別お見積り"],
        ],
        "note": "※ 費目・金額は概算の目安。AWS インフラ利用料は別途。PoC 評価後に確定見積りをご提示",
        "source": "ScalarDB Cluster 価格: AWS Marketplace 公表値（2026年8月時点、Standard エディション）",
    },

    # リスクと対策（先回りして潰す）
    "risks": [
        ["AI が生成したコードの品質が読めない",
         "整合性は ScalarDB が保証し、テスト環境の自動結合テストをマージのゲートにする。"
         "レビュー観点を業務ロジックに絞ることでレビュー精度自体も上がる"],
        ["ローカル（Community）とテスト（Cluster）の機能差",
         "認証認可・SQL/GraphQL・暗号化などは上位エディションの機能。PoC 初期に使用機能を"
         "洗い出し、差異が出るものはテスト環境側で検証する運びとする"],
        ["既存系からの直接書き込み",
         "既存系からの直接書き込みが残ると分離レベルの保証が崩れる。PoC のスコープ定義時に"
         "書き込み経路を洗い出し、経路を ScalarDB に寄せる設計方針を先に確定する"],
        ["性能要件を満たせない",
         "PoC 成功基準に性能実測を含め、未達なら本導入に進まない（Go/No-Go を明示）"],
    ],

    # 次のステップ（今日決めること → 直近のアクション）
    "next": ["本日:\n課題認識の\nすり合わせ", "〜2 週間:\nPoC スコープと\n対象機能の合意",
             "〜1 ヶ月:\n2 環境の\n構築開始", "3〜4 ヶ月後:\nGo/No-Go\n判断"],
}


# ============================================================ 描画

def draw_current(d: Canvas, cur: dict) -> None:
    d.icon_flow(1.1, 1.35, 7.8, cur["systems"], size=0.78, label_size=9.5,
                arrow_color=d.P.muted)
    d.label(1.1, 2.95, 7.8, 0.3, cur["flow_note"], size=10.5,
            align="CENTER", color=d.P.muted)
    d.so_what(0.7, 3.75, 8.6, 0.85, cur["so_what"])


def draw_challenges(d: Canvas, items: list) -> None:
    d.cards(0.6, 1.25, 8.8, 2.1, items, accent=[d.P.primary, d.P.info, d.P.warning],
            title_size=10.5, body_size=9.5)
    d.label(0.6, 3.65, 8.8, 0.3,
            "※ 課題は開発現場のヒアリングに基づく整理。認識齟齬があれば本日修正したい",
            size=9, align="START", color=d.P.muted)


def draw_iceberg(d: Canvas, data: dict) -> None:
    d.iceberg(0.7, 1.1, 8.4, 3.75, data["above"], data["below"],
              above_title="表出している問題", below_title="共通の根本原因", size=10)


def draw_tobe(d: Canvas, tobe: dict) -> None:
    d.before_after(0.6, 1.2, 8.8, 2.7, tobe["before"], tobe["after"],
                   before_title="現状 (As-Is)", after_title="目指す姿 (To-Be)", size=10.5)
    d.shape(0.6, 4.15, 8.8, 0.62, kind="RECTANGLE", fill=d.P.surfaceAlt,
            stroke=d.P.border, text=tobe["scope_out"], size=9.5, color=d.P.muted)


def draw_solution(d: Canvas, _p: dict) -> None:
    """AI 駆動開発 × ScalarDB の提案図（生成→検証ループとデータ層）。"""
    ac = d.P.primary
    d.icon_row(1.5, 1.15, 7.0, [("bot", "AI が生成"), ("check", "自動テスト"),
                                ("sync", "AI が自己修正"), ("people", "人がレビュー")],
               size=0.5, label_size=9)
    d.shape(1.2, 2.35, 7.6, 0.55, kind="ROUND_RECTANGLE", fill=ac, stroke=None,
            text="ScalarDB — 統一 API と分散 ACID（整合性は基盤が保証）",
            size=11, bold=True, color="#FFFFFF")
    d.icon_row(1.7, 3.35, 6.6, [("stack", "開発環境\n(ローカル・無料)"),
                                ("cloud", "テスト環境\n(aidd-infra-test)"),
                                ("database", "既存 DB\n(PostgreSQL 等)")],
               size=0.5, label_size=9)
    for cx in (2.45, 4.2, 5.95, 7.7):
        d.arrow(cx, 1.95, cx, 2.31, color=d.P.muted, weight=1.2, _anchored=True)
    for cx in (2.8, 5.0, 7.2):
        d.arrow(cx, 2.94, cx, 3.31, color=d.P.muted, weight=1.2, _anchored=True)
    d.label(0.7, 4.55, 8.6, 0.55,
            "AI は統一 API に向けて書くだけでよく、横断更新の整合性は基盤が保証。"
            "同じ構成を 2 環境に用意することで、生成→テスト→修正が自走する",
            size=10.5, align="CENTER", color=d.P.muted, line_spacing=130)


def draw_mapping(d: Canvas, rows: list) -> None:
    d.table(0.6, 1.3, 8.8, ["御社の課題", "本提案の打ち手", "実現される状態"],
            [list(r) for r in rows], col_widths=[1.1, 1.2, 1.2], row_h=0.72,
            size=9.5, aligns=["START", "START", "START"])
    d.label(0.6, 4.15, 8.8, 0.3, "各機能の技術詳細は Appendix（機能紹介資料）にてご説明可能",
            size=9, align="START", color=d.P.muted)


def draw_alternatives(d: Canvas, alt: dict) -> None:
    d.table(0.6, 1.2, 8.8, alt["headers"], alt["rows"],
            col_widths=[1.3, 1.0, 1.1, 1.1], row_h=0.55, size=9,
            aligns=["START", "CENTER", "CENTER", "CENTER"])
    d.so_what(0.6, 4.35, 8.8, 0.85,
              "「整合性を基盤に任せる」と「AI が自分で検証できる」の両立が本提案の選定理由")


def draw_effects(d: Canvas, eff: dict) -> None:
    d.before_after(0.6, 1.2, 8.8, 2.5, eff["before"], eff["after"],
                   before_title="導入前の開発", after_title="導入後の開発", size=10.5)
    d.so_what(0.6, 4.0, 8.8, 0.95, eff["so_what"], label="定量化")


def draw_cases(d: Canvas, p: dict) -> None:
    d.cards(0.6, 1.25, 8.8, 2.6, p["cases"],
            accent=[d.P.primary, d.P.info, d.P.success], title_size=10,
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
    rows = [[e["name"].replace("（aidd", "\n（aidd"), e["purpose"], e["services"]]
            for e in arch["envs"]]
    d.table(0.6, 1.35, 8.8, ["環境", "役割", "主な構成サービス"], rows,
            col_widths=[1.2, 1.5, 1.8], row_h=0.95, size=9.5,
            aligns=["START", "START", "START"])
    d.label(0.6, 4.05, 8.8, 0.55,
            f"※ クラウドは {arch['cloud']} を既定として構成。指定があれば同じ役割分担で"
            " GCP / Azure に組み替える。ステージング・本番環境は本提案の範囲外",
            size=9, align="START", color=d.P.muted, line_spacing=125)


def draw_bom_scalar(d: Canvas, arch: dict) -> None:
    rows = [[e["name"], e["scalar"], e["qty"], e["monthly"]] for e in arch["envs"]]
    rows.append(["合計（ライセンス月額）", "", "", arch["monthly_total"]])
    d.table(0.6, 1.35, 8.8, ["環境", "Scalar 製品", "数量", "月額概算"], rows,
            col_widths=[1.5, 1.7, 0.8, 1.0], row_h=0.6, size=9.5,
            aligns=["START", "START", "CENTER", "CENTER"])
    d.label(0.6, 4.05, 8.8, 0.55, arch["monthly_note"], size=9, align="START",
            color=d.P.muted, line_spacing=125)
    d.source_note(0.6, 4.75, 8.8, arch["source"])


def draw_gantt(d: Canvas, g: dict) -> None:
    rows = [tuple(r) for r in g["rows"]]
    d.gantt(0.6, 1.3, 8.8, 2.8, g["columns"], rows, size=9.5)
    d.label(0.6, 4.35, 8.8, 0.3,
            "※ PoC 評価（Go/No-Go）を通過した場合のみ展開計画に進む前提のスケジュール",
            size=9, align="START", color=d.P.muted)


def draw_team(d: Canvas, p: dict) -> None:
    d.orgchart(1.4, 1.15, 7.2, 2.0, p["team"], size=9)
    d.table(0.6, 3.45, 8.8, ["担当", "役割（想定負荷）"],
            [list(r) for r in p["team_roles"]], col_widths=[1.0, 3.2],
            row_h=0.42, size=9.5, aligns=["START", "START"])


def draw_costs(d: Canvas, c: dict) -> None:
    d.table(0.6, 1.3, 8.8, ["費目", "内容", "概算"],
            [list(r) for r in c["rows"]], col_widths=[1.1, 2.0, 1.1],
            row_h=0.52, size=10, aligns=["START", "START", "CENTER"])
    d.label(0.6, 4.1, 8.8, 0.3, c["note"], size=9.5, align="START",
            color=d.P.muted)
    d.source_note(0.6, 4.75, 8.8, c["source"])


def draw_risks(d: Canvas, rows: list) -> None:
    d.table(0.6, 1.25, 8.8, ["想定されるご懸念", "対策"],
            [list(r) for r in rows], col_widths=[1.1, 2.6], row_h=0.72,
            size=9.5, aligns=["START", "START"])


def draw_next(d: Canvas, steps: list) -> None:
    d.flow(0.7, 1.6, 8.6, 1.15, steps, size=10)
    d.so_what(0.7, 3.4, 8.6, 0.85,
              "本日は課題認識の確認と、PoC スコープ検討に進むかどうかのご判断をいただきたい",
              label="お願い")


def print_bom(arch: dict) -> None:
    """構成内訳（サービス一覧と Scalar 製品・数量・月額）をコンソールにも出す。"""
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


# ============================================================ 組み立て

class _DryDeck(bd._StubDeck):
    """--dry-run 用。add_slide / commit を API 抜きで受け流す。"""

    def __init__(self):
        super().__init__()
        self._n = 0

    def add_slide(self, layout, **kw):
        self._n += 1
        self.last = dict(kw, layout=layout)
        return {"slideId": f"dry_{self._n}"}

    def add_page_numbers(self, start=None):
        return 0

    def commit(self, chunk_size=500):
        return "(dry-run: 生成していません)"


def build(deck, template, dry: bool = False) -> list[str]:
    P = PROPOSAL
    problems: list[str] = []

    def drawn(title, fn, *fn_args, notes=None, connectors=False):
        ref = deck.add_slide("TITLE_ONLY", title=title, notes=notes)
        d = Canvas(deck, ref["slideId"], template)
        if dry:
            d.deck.dry = True
        fn(d, *fn_args)
        audits = d.audit_bounds() + d.audit_overlaps() + d.audit_text_fit()
        if connectors:
            audits += d.audit_connectors()
        problems.extend(f"{title[:16]}…: {m}" for m in audits)

    # 0. 表紙
    deck.add_slide("COVER", title=f"{P['customer']}様向け\n{P['title']}",
                   subtitle=P["subtitle"], body=f"{P['date']}\n株式会社Scalar",
                   notes="顧客未特定のため customer は仮置き。実案件では customer / date を書き換える。")

    # 1. エグゼクティブサマリ（結論先出し）
    ref = deck.add_slide(
        "TITLE_ONLY", title="エグゼクティブサマリ — 「書く速さ」ではなく「回る速さ」を上げる",
        notes="決裁者は冒頭の要約しか読まない前提で、課題・解決策・進め方をこの 1 枚に集約する"
              "（才流・HubSpot の提案書構成調査）。")
    d = Canvas(deck, ref["slideId"], template)
    s = P["summary"]
    d.exec_summary(0.6, 1.1, 8.8, 3.95, s["situation"], s["complication"],
                   s["resolution"], points=s["points"], size=10)
    problems.extend(f"サマリ: {m}" for m in
                    (d.audit_bounds() + d.audit_overlaps() + d.audit_text_fit()))

    # 2. 課題の合意形成
    drawn("背景と現状 — AI コーディングは導入したが、開発サイクルは速くなっていない",
          draw_current, P["current"],
          notes="現状認識の合意が提案全体の前提。ヒアリング結果をそのまま書き、推測で補わない。")
    drawn("課題の整理 — 解決すべきは 3 点", draw_challenges, P["challenges"],
          notes="課題は 3 点まで（deck-outlines.md）。順番は打ち手の対応表と揃える。")
    drawn("課題の構造 — 「データ層」と「環境」の 2 つの欠落に帰着する",
          draw_iceberg, P["iceberg"],
          notes="対症療法（レビュー体制の強化・ツールの追加導入）との差別化の土台になるスライド。")

    # 3. ご提案
    deck.add_slide("SECTION", title="ご提案",
                   body="AI が自走できるデータ層と開発・テスト環境")
    drawn("目指す姿 — AI が生成からテストまで自走し、人はレビューに集中する",
          draw_tobe, P["tobe"],
          notes="スコープ外の明示（含まれない範囲を書いて期待値を制御）。"
                "ご指定の前提どおり、上位環境は範囲外とする。")
    drawn("ご提案 — ScalarDB を統一データ層に据えた AI 駆動開発", draw_solution, P,
          connectors=True,
          notes="ScalarDB: Universal HTAP エンジン。Consensus Commit により DB 非依存の "
                "ACID を実現（research-2026-08.md）。密な構成図が必要な案件では "
                "drawio-diagrams スキルで別途作図する。")
    drawn("課題と打ち手の対応 — 3 つの課題すべてに答えを持つ", draw_mapping, P["mapping"],
          notes="課題スライドと同じ順序・同じ文言で対応させる（読み手に再解釈させない）。")
    drawn("打ち手の比較 — AI ツール単体でも自作抽象化層でもない理由",
          draw_alternatives, P["alternatives"],
          notes="稟議には「これでないといけない理由」が必要（才流）。比較軸は顧客の"
                "評価基準（KBF）に合わせて書き換える。")
    drawn("期待効果 — レビュー負荷と手戻りが減り、リードタイムが縮む", draw_effects, P["effects"],
          notes="機能ではなく開発の進み方の変化を語る。根拠のない定量値は書かない。"
                "定量は PoC で実測して稟議材料にする、という筋書きに乗せる。")
    drawn("導入事例 — AI 駆動開発 × ScalarDB の公表実績", draw_cases, P,
          notes="出典: 常石造船 prtimes.jp/main/html/rd/p/000000071.000037795.html / "
                "atmarkit.itmedia.co.jp/ait/articles/2606/29/news054.html / "
                "LayerX prtimes.jp/main/html/rd/p/000000376.000036528.html / "
                "ENS prtimes.jp/main/html/rd/p/000000006.000037795.html。"
                "鮮度 3 ヶ月ルールに従い再調査してから使う。")

    # 4. 進め方
    deck.add_slide("SECTION", title="導入の進め方", body="2 環境を立ち上げ、PoC で実測する")
    drawn("導入アプローチ — 2 環境を立ち上げ、PoC で「自走率」を実測する", draw_journey, P,
          notes="PoC は成功基準（Go/No-Go）までがワンセット。自走率の目標値はヒアリングで決める。")
    drawn("提案システム構成 — 開発（ローカル）とテスト（aidd-infra-test）の 2 環境",
          draw_architecture, P["architecture"],
          notes="ご指定の前提により開発・テストの 2 環境。クラウド既定は AWS。"
                "図の元データは examples/scalar-proposal-aidd-envs.drawio で、"
                "顧客要件に合わせて drawio-diagrams スキルで書き換えてから "
                "scripts/drawio_export.py で PNG を再生成する。")
    drawn("構成内訳（1）— 各環境のサービス構成", draw_bom_services, P["architecture"],
          notes="クラウドサービスのリスト。環境の役割分担（ローカル無料 → テスト常設）が"
                "崩れない範囲でサービスを増減する。")
    drawn("構成内訳（2）— Scalar 製品と数量・月額概算", draw_bom_scalar, P["architecture"],
          notes="$1.40/h × Pod 数 × 730h。価格出典は AWS Marketplace（2026-08 時点）。"
                "Premium 機能（SQL/GraphQL・暗号化・ベクトル検索）を使う場合は $2.79/h で再計算する。")
    drawn("スケジュール案 — 4 ヶ月で Go/No-Go 判断まで", draw_gantt, P["gantt"],
          notes="ヒアリングした開始希望時期・予算年度に合わせて列と行を書き換える。")
    drawn("推進体制案 — 御社開発チームと Scalar の二人三脚", draw_team, P,
          notes="顧客側の負担（想定稼働）を明示すると「工数がかからない」ことが伝わる。")
    drawn("概算費用 — 開発環境は無料、有償はテスト環境 1 Pod から", draw_costs, P["costs"],
          notes="価格を出す位置は解決策・効果の後（HubSpot）。ライセンス単価の出典は "
                "AWS Marketplace 公表値。個別見積り項目を勝手に金額化しない。")
    drawn("想定されるご懸念と対策", draw_risks, P["risks"],
          notes="リスクの先回り（才流 稟議書 8 項目）。ScalarDB 迂回の直接書き込みは "
                "proposal-map.md §4 の制約。隠さず論点として出す。")

    # 5. クロージング
    drawn("次のステップ — 本日ご判断いただきたいこと", draw_next, P["next"],
          notes="次のアクションを明示して送りっぱなしにしない。")
    deck.add_slide("CLOSING")
    deck.add_page_numbers()
    return problems


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--folder", default=None)
    p.add_argument("--dry-run", action="store_true",
                   help="API を呼ばずに座標・文字量だけ検査する")
    args = p.parse_args()

    template = bd.load_template(TEMPLATE)
    P = PROPOSAL
    if args.dry_run:
        deck = _DryDeck()
    else:
        deck = bd.TemplateDeck.create(
            template, title=f"{P['customer']}様向け {P['title']}", folder=args.folder)

    problems = build(deck, template, dry=args.dry_run)
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
