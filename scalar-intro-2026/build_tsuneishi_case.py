#!/usr/bin/env python3
"""常石造船様 導入事例デッキ(AI 駆動開発による基幹システム刷新)。

出典(2026-08-02 調査):
- Scalar プレスリリース(2026-06-10): https://prtimes.jp/main/html/rd/p/000000071.000037795.html
- @IT 記事(2026-06-29): https://atmarkit.itmedia.co.jp/ait/articles/2606/29/news054.html
- Kong お知らせ: https://jp.konghq.com/news/kong-tsuneishi-ai-core-system-modernization
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

TITLE = "導入事例: 常石造船様"
SUBTITLE = "AI 駆動開発による基幹システム刷新 — ScalarDB × Kong Konnect"
DATE = "2026年8月"

SRC_PR = "https://prtimes.jp/main/html/rd/p/000000071.000037795.html"
SRC_IT = "https://atmarkit.itmedia.co.jp/ait/articles/2606/29/news054.html"
SRC_KONG = "https://jp.konghq.com/news/kong-tsuneishi-ai-core-system-modernization"
SOURCES = (f"出典: Scalar プレスリリース 2026-06-10 {SRC_PR} / "
           f"@IT 2026-06-29 {SRC_IT} / Kong {SRC_KONG}")


def _pill(d: Canvas, x, y, w, h, text, accent, *, light=0.88, size=9,
          bold=False, color=None):
    return d.shape(x, y, w, h, kind="ROUND_RECTANGLE",
                   fill=lighten(accent, light), stroke=accent, text=text,
                   size=size, bold=bold, color=color or d.P.text,
                   line_spacing=112)


def _band(d: Canvas, y, text, accent, *, h=0.44, size=10.5):
    d.shape(0.5, y, 9.0, h, kind="ROUND_RECTANGLE",
            fill=lighten(accent, 0.9), stroke=lighten(accent, 0.5),
            text=text, size=size, bold=True, color=d.P.text,
            line_spacing=115)


def _varrow(d: Canvas, x, y1, y2):
    d.arrow(x, y1, x, y2, color=d.P.muted, weight=1.1, _anchored=True)


# ---------------------------------------------------------------- 図解

def draw_challenge(d: Canvas):
    """課題: 3 カード + 帯。"""
    cards = [
        ("15 年以上稼働のモノリス",
         "販売・保守・管理などの機能を段階的に拡張してきた基幹システム。"
         "構造が複雑化しドキュメントも不足"),
        ("ブラックボックス化",
         "変更の影響範囲が読めず、対応できる人員も限定。"
         "改修のたびにリスクと工数が膨らむ"),
        ("十数年、刷新に着手できず",
         "刷新は急務と認識しつつも、調査を含めて着手できない状態が続き、"
         "市場変化への対応が停滞"),
    ]
    b = d.cards(0.5, 1.15, 9.0, 1.9, cards, body_size=9.5, accent=d.P.danger)
    d.label(0.5, b + 0.35, 9.0, 0.35,
            "「調査だけで数ヶ月〜数年」が常識だったため、最初の一歩が踏み出せなかった",
            size=11, bold=True, align="CENTER", color=d.P.text)
    _band(d, b + 0.95, "打ち手: AI 駆動開発で「調査・再設計」のコストを桁違いに下げる",
          d.P.primary)


def draw_approach(d: Canvas):
    """アプローチ: 体制 + プロセスフロー + 2 日の内訳。"""
    _pill(d, 0.5, 1.05, 9.0, 0.5,
          "体制: 常石造船の IT 担当者 2 名が Scalar に約 3 ヶ月常駐 — AI エージェントを駆使して一気通貫で推進",
          d.P.info, size=10, bold=True)
    b = d.flow(0.5, 1.95, 9.0, 0.85, [
        "① ソースコード解析\nAI エージェントが\n既存コードを読解",
        "② 現状分析・再設計\nわずか 2 日で完了",
        "③ ドメイン分割\n9 つのマイクロ\nサービスへ",
        "④ MVP 開発\n実質 3 ヶ月で完成",
    ], size=9)
    cards = [
        ("AI が変えたこと",
         "複雑なコードの解析とリファクタリングを AI エージェントが担い、"
         "人手では数ヶ月かかる調査を圧縮"),
        ("人が担ったこと",
         "ビジネスドメインの判断・設計の意思決定・ユーザー部門との調整は"
         "IT 担当者と Scalar が主導"),
    ]
    b = d.cards(0.5, b + 0.35, 9.0, 1.35, cards, body_size=9.5)
    _band(d, b + 0.3, "「調査に数ヶ月」を「2 日」に — 着手できなかった刷新が動き出した",
          d.P.primary)


def draw_architecture(d: Canvas):
    """新基盤の構成図。"""
    d.icon("person", 3.35, 1.0, 0.4, label="ユーザー", label_size=8,
           label_w=1.2)
    d.icon("bot", 5.85, 1.0, 0.4, label="AI エージェント / LLM", label_size=8,
           label_w=1.8)
    _pill(d, 2.3, 1.80, 5.4, 0.44,
          "Kong Konnect — API 管理・認証・ガバナンス", d.P.info, size=9.5,
          bold=True)
    _varrow(d, 3.55, 1.68, 1.78)
    _varrow(d, 6.05, 1.68, 1.78)
    svc_labels = ["販売", "保守", "管理", "… 全 9 サービス"]
    widths = [1.05, 1.05, 1.05, 1.85]
    x = 2.3
    for t, w in zip(svc_labels, widths):
        _pill(d, x, 2.44, w, 0.42, t, d.P.muted, light=0.92, size=8.5)
        x += w + 0.13
    d.label(2.2, 2.90, 2.65, 0.20, "AI 分析に基づきドメイン単位で分割",
            size=8, align="END", color=d.P.muted)
    _varrow(d, 5.0, 2.26, 2.42)
    _pill(d, 2.3, 3.24, 5.4, 0.44,
          "ScalarDB — 分散トランザクションでサービス横断の一貫性", d.P.primary,
          size=9.5, bold=True)
    _varrow(d, 5.0, 2.88, 3.22)
    d.icon("database", 4.05, 3.90, 0.4)
    d.icon("stack", 5.55, 3.90, 0.4)
    d.label(3.3, 4.34, 3.4, 0.20, "各サービスのデータベース", size=8,
            align="CENTER", color=d.P.muted)
    _varrow(d, 4.25, 3.70, 3.88)
    _varrow(d, 5.75, 3.70, 3.88)
    _band(d, 4.62, "AI エージェントからのアクセスも、Kong と ScalarDB で安全に統制",
          d.P.primary, h=0.38, size=10)


def draw_results(d: Canvas):
    """成果: メトリクス 4 つ + 今後。"""
    metrics = [("2日", "現状分析・再設計"), ("約3ヶ月", "MVP 開発"),
               ("2名", "常駐した IT 担当者"), ("9", "マイクロサービス")]
    for i, (v, c) in enumerate(metrics):
        d.metric(0.5 + i * 2.3, 1.1, 2.1, 1.25, v, c, value_size=24)
    cards = [
        ("段階的な本番リリースへ",
         "ユーザー部門と調整しながら、新システムへの本格移行と運用を"
         "段階的に進行中"),
        ("「標準モデル」として展開",
         "Scalar と Kong は本事例を AI 駆動モダナイゼーションの標準モデルと"
         "位置づけ、製造業・エンタープライズへ展開"),
    ]
    b = d.cards(0.5, 2.75, 9.0, 1.4, cards, body_size=9.5)
    _band(d, b + 0.3,
          "深津 CEO:「マイクロサービス化 × ScalarDB × Kong Konnect はモダナイゼーションのリファレンスケース」",
          d.P.primary, size=9.5)


def draw_sales_usage(d: Canvas):
    """営業観点: 提案での使い方。"""
    cards = [
        ("「着手できない」への実証",
         "「調査だけで数ヶ月」を理由に見送られてきた刷新案件に、"
         "「AI で 2 日・MVP 3 ヶ月」の実績を提示できる"),
        ("マイクロサービス化の構成例",
         "9 サービスのデータ一貫性を ScalarDB が担保する実構成。"
         "「Saga を自作しない」提案の裏付けになる"),
        ("AI 活用基盤への布石",
         "AI エージェント・LLM が安全にデータへアクセスできる基盤という、"
         "次の投資テーマへつながる"),
    ]
    b = d.cards(0.5, 1.15, 9.0, 1.9, cards, body_size=9.5)
    d.label(0.5, b + 0.35, 9.0, 0.35,
            "ヒアリングの勘所: 基幹システムの稼働年数 / ドキュメントの有無 / 刷新を見送った回数と理由",
            size=10.5, bold=True, align="CENTER", color=d.P.text)
    _band(d, b + 0.95,
          "「レガシー刷新 × マイクロサービス × AI 駆動」の 3 つの型を一度に実証した事例",
          d.P.primary)


# ---------------------------------------------------------------- 生成

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--folder", default=None)
    args = p.parse_args()

    template = bd.load_template(TEMPLATE)
    deck = bd.TemplateDeck.create(template, title=f"{TITLE}(2026年8月)",
                                  folder=args.folder)
    problems: list[str] = []

    def canvas_slide(title, draw, notes=None):
        ref = deck.add_slide("TITLE_ONLY", title=title, notes=notes)
        d = Canvas(deck, ref["slideId"], template)
        draw(d)
        problems.extend(f"{title[:14]}…: {m}" for m in
                        (d.audit_bounds() + d.audit_connectors()
                         + d.audit_overlaps() + d.audit_text_fit()))

    deck.add_slide("COVER", title=TITLE, subtitle=SUBTITLE,
                   body=f"{DATE}\n株式会社Scalar",
                   notes=f"2026年6月10日 発表の公開事例。{SOURCES}")

    ref = deck.add_slide("TITLE_ONLY",
                         title="十数年手つかずだった基幹システム刷新が、3 ヶ月で MVP に",
                         notes=SOURCES)
    d = Canvas(deck, ref["slideId"], template)
    b = d.table(0.5, 1.1, 9.0, ["項目", "内容"], [
        ["お客様", "常石造船株式会社(ツネイシグループの造船・海運事業の中核。ばら積み船・コンテナ船・タンカー等の建造・修繕)"],
        ["対象", "15 年以上稼働してきた基幹システム(販売・保守・管理などの機能を持つモノリス)"],
        ["採用製品", "ScalarDB(分散データ管理)+ Kong Konnect(API 管理)"],
        ["進め方", "AI 駆動開発 — IT 担当者 2 名が Scalar に約 3 ヶ月常駐し、AI エージェントで解析・設計・開発"],
        ["成果", "現状分析・再設計を 2 日で完了、MVP を実質 3 ヶ月で完成。9 つのマイクロサービスへ再構成"],
        ["発表", "2026 年 6 月(Scalar・Kong 共同発表)"],
    ], col_widths=[1.5, 7.5], row_h=0.52, size=9.5)
    problems.extend(f"サマリ: {m}" for m in
                    (d.audit_bounds() + d.audit_overlaps() + d.audit_text_fit()))

    canvas_slide("課題 — 15 年以上のモノリスがブラックボックス化し、着手できず",
                 draw_challenge, notes=SOURCES)
    canvas_slide("アプローチ — AI 駆動開発で「調査・再設計」を 2 日に圧縮",
                 draw_approach,
                 notes=f"AI エージェントによるソースコード解析とリファクタリング。{SOURCES}")
    canvas_slide("新基盤 — Kong Konnect と ScalarDB が 9 サービスを支える",
                 draw_architecture,
                 notes=f"ScalarDB は複数 DB 間のデータ一貫性のハブ。Kong Konnect は API 管理・認証。{SOURCES}")
    canvas_slide("成果 — 2 名・約 3 ヶ月で MVP、標準モデルとして展開へ",
                 draw_results,
                 notes=f"深津 CEO コメントはプレスリリースより。{SOURCES}")
    canvas_slide("提案での使い方 — 「レガシー刷新に着手できない」お客様への実証事例",
                 draw_sales_usage,
                 notes="「Scalar 提案準備ガイド」の課題の型: レガシー移行型・マイクロサービス型に対応する事例。")
    deck.add_slide("CLOSING")

    deck.add_page_numbers()
    for m in problems:
        print(f"  検査: {m}")
    url = deck.commit()
    print(f"Done! 8 slides. Open: {url}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
