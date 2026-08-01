#!/usr/bin/env python3
"""ScalarDB の構成図を作る実例。

クラウドアイコン（`cloud_icons`）・ピクトグラム（`illustrations`）・ブランドの
ロゴ（`assets/brand/`）・コネクタ（`diagrams`）を 1 枚に混ぜる典型例。

デッキ仕様（JSON）の `figures` では**線を引けない**ため、層と層を矢印で結ぶ
構成図は本ファイルのように `Canvas` を直に使う。

    cd ~/.claude/skills/google-slides-template
    .venv/bin/python scripts/fetch-cloud-icons.py   # 初回だけ（アイコンは未同梱）
    .venv/bin/python examples/scalardb-architecture.py [--folder <DriveフォルダURL>]

ライセンス: クラウドアイコンは各ベンダーの資産（`references/cloud-icons.md`）。
色の変更・回転・反転は禁止。ここでもそのまま貼っている。
"""
from __future__ import annotations

import argparse
import os
import sys
from importlib.machinery import SourceFileLoader

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(SKILL_DIR, "scripts"))

bd = SourceFileLoader("bd", os.path.join(SKILL_DIR, "scripts", "build-deck.py")).load_module()
from diagrams import Canvas, lighten  # noqa: E402

TEMPLATE = os.path.join(SKILL_DIR, "templates", "scalar-2026.json")
LOGO = os.path.join(SKILL_DIR, "assets", "brand", "product-logos",
                    "scalardb-logo-horizontal.png")


def draw_overview(d: Canvas) -> None:
    """アプリ → ScalarDB → 各データベース の 3 層。"""
    # 1) アプリ層
    d.label(0.5, 0.95, 9.0, 0.24, "アプリケーション", size=9.5, align="START",
            color=d.P.muted)
    d.icon_row(0.9, 1.25, 8.2, [("browser", "Web アプリ"), ("mobile", "モバイル"),
                                ("server", "バッチ"), ("bot", "エージェント")],
               size=0.5, label_size=8.5)

    # 2) ScalarDB 層（ロゴ + 帯）。ロゴは画像なので枠を先に敷いて上に載せる
    band_y = 2.45
    d.shape(0.9, band_y, 8.2, 0.72, kind="ROUND_RECTANGLE",
            fill=lighten(d.P.primary, 0.88), stroke=d.P.primary)
    d.image(1.15, band_y + 0.16, 1.5, 0.42, LOGO, fit="contain",
            alt="ScalarDB")
    d.label(2.85, band_y + 0.06, 6.0, 0.6,
            "1 つのトランザクションで複数のデータベースをまたいで整合性を保つ",
            size=10.5, align="START", valign="MIDDLE", color=d.P.text)

    # 3) データベース層。マネージドは公式アイコン、自前運用は図形のピクトグラム
    zone_y = 3.55
    d.label(0.5, zone_y - 0.28, 9.0, 0.24, "バックエンドのデータベース", size=9.5,
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
    # 自前運用のデータベースには公式アイコンが無いので図形で描く
    ox = 0.9 + 3 * 2.15
    d.cloud_zone(ox, zone_y, 1.95, 1.5, title="オンプレミス / 自前運用", title_size=8)
    d.icon_row(ox + 0.05, zone_y + 0.34, 1.85,
               [("database", "PostgreSQL"), ("stack", "Cassandra")],
               size=0.42, label_size=7.5, gap=0.02)

    # 4) 層をつなぐ
    for i in range(4):
        cx = 0.9 + 8.2 / 4 * (i + 0.5)
        d.arrow(cx, 2.15, cx, band_y - 0.06, color=d.P.muted, weight=1.0,
                _anchored=True)
    for i in range(4):
        zx = 0.9 + i * 2.15 + 0.975
        d.arrow(zx, band_y + 0.78, zx, zone_y - 0.04, color=d.P.muted, weight=1.0,
                _anchored=True)


def draw_multi_region(d: Canvas) -> None:
    """マルチリージョン構成。ゾーンを入れ子にする例。"""
    for i, (region, db) in enumerate([("ap-northeast-1（東京）", "aws:aurora"),
                                      ("us-east-1（バージニア）", "aws:aurora")]):
        zx = 0.5 + i * 4.6
        d.cloud_zone(zx, 1.0, 4.4, 3.4, vendor="aws", title=f"AWS  {region}",
                     title_size=8.5)
        d.cloud_zone(zx + 0.25, 1.45, 3.9, 2.75, title="VPC", title_size=8,
                     color=d.P.muted)
        b = d.cloud_icon_row(zx + 0.4, 1.85, 3.6, [
            ("aws:elastic-kubernetes-service", "EKS"),
        ], size=0.52, label_size=8)
        d.shape(zx + 0.5, b + 0.12, 3.4, 0.42, kind="ROUND_RECTANGLE",
                fill=lighten(d.P.primary, 0.88), stroke=d.P.primary,
                text="ScalarDB Cluster", size=9.5, bold=True, color=d.P.text)
        d.cloud_icon(db, zx + 1.94, b + 0.72, 0.5, label="Aurora", label_size=8,
                     label_w=1.6)
    # リージョン間
    d.arrow(4.95, 2.7, 5.55, 2.7, color=d.P.muted, weight=1.25, _anchored=True)
    d.label(3.9, 4.5, 2.7, 0.26, "非同期レプリケーション", size=8.5,
            align="CENTER", color=d.P.muted)


def main() -> int:
    p = argparse.ArgumentParser(description="ScalarDB の構成図デッキを作る")
    p.add_argument("--folder", help="出力先の Drive フォルダ URL または ID")
    p.add_argument("--title", default="ScalarDB 構成図")
    args = p.parse_args()

    template = bd.load_template(TEMPLATE)
    deck = bd.TemplateDeck.create(template, title=args.title, folder=args.folder)

    problems = []
    for title, draw in [
        ("ScalarDB は複数のデータベースを 1 つのトランザクションにまとめる", draw_overview),
        ("マルチリージョン構成", draw_multi_region),
    ]:
        ref = deck.add_slide("TITLE_ONLY", title=title)
        d = Canvas(deck, ref["slideId"], template)
        draw(d)
        problems += [f"{title[:20]}…: {m}" for m in
                     (d.audit_bounds() + d.audit_connectors()
                      + d.audit_overlaps() + d.audit_text_fit())]

    for m in problems:
        print(f"  検査: {m}")
    deck.add_page_numbers()
    url = deck.commit()
    print(f"Done! Open: {url}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
