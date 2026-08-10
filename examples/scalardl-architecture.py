#!/usr/bin/env python3
"""ScalarDL の構成図を作る実例。

`scalardb-architecture.py` と同じ組み立て方で、**3 つのアイコン系統を混ぜる**例に
なっている。

- `cloud_icons`  … バックエンドのマネージドデータベース（ベンダー公式・改変禁止）
- `icons`        … 「証拠チェーン」「改ざん検知」などの業務語彙（Scalar ブランド）
- `illustrations`… 自前運用の DB やクライアントなど、一般的な部品

    # リポジトリのルートで実行する
    .venv/bin/python scripts/fetch_cloud_icons.py   # 初回だけ（アイコンは未同梱）
    .venv/bin/python examples/scalardl-architecture.py [--folder <DriveフォルダURL>]
"""
from __future__ import annotations

import argparse
import os
import sys
from importlib.machinery import SourceFileLoader

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(SKILL_DIR, "scripts"))

bd = SourceFileLoader("bd", os.path.join(SKILL_DIR, "scripts", "build_deck.py")).load_module()
from diagrams import Canvas, lighten  # noqa: E402

TEMPLATE = os.path.join(SKILL_DIR, "templates", "scalar-2026.json")
BRAND = os.path.join(SKILL_DIR, "assets", "brand", "product-logos")
LOGO_DL = os.path.join(BRAND, "scalardl-logo-horizontal.png")


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


def draw_stack(d: Canvas) -> None:
    """クライアント → ScalarDL → ScalarDB → データベース の 4 層。"""
    d.label(0.5, 0.92, 9.0, 0.22, "クライアント", size=9, align="START",
            color=d.P.muted)
    d.icon_row(1.2, 1.16, 7.6, [("browser", "業務アプリ"), ("mobile", "モバイル"),
                                ("server", "外部システム")],
               size=0.42, label_size=8.5)

    y = _band(d, 1.2, 2.05, 7.6, 0.62, logo=LOGO_DL,
              text="コントラクトを実行し、資産の履歴をハッシュでつないで残す")
    y = _band(d, 1.2, y + 0.42, 7.6, 0.5, text="ScalarDB（トランザクション層）",
              text_size=10, fill=lighten(d.P.info, 0.9), stroke=d.P.info) + 0.42

    d.label(0.5, y - 0.24, 9.0, 0.22, "バックエンドのデータベース", size=9,
            align="START", color=d.P.muted)
    for i, (vendor, name, label) in enumerate([
        ("aws", "aws:dynamodb", "DynamoDB"),
        ("azure", "azure:cosmos-db", "Cosmos DB"),
        ("gcp", "gcp:cloud-spanner", "Spanner"),
    ]):
        zx = 1.2 + i * 1.95
        d.cloud_zone(zx, y, 1.75, 1.12, vendor=vendor, title_size=7.5)
        d.cloud_icon(name, zx + 0.65, y + 0.3, 0.42, label=label, label_size=8,
                     label_w=1.6)
    ox = 1.2 + 3 * 1.95
    d.cloud_zone(ox, y, 1.75, 1.12, title="自前運用", title_size=7.5)
    d.icon_row(ox + 0.05, y + 0.3, 1.65,
               [("database", "PostgreSQL"), ("stack", "Cassandra")],
               size=0.36, label_size=7.5, gap=0.02)

    # 層をつなぐ（上下の縦矢印）
    for cx in (5.0,):
        d.arrow(cx, 1.92, cx, 2.03, color=d.P.muted, weight=1.0, _anchored=True)
        d.arrow(cx, 2.67, cx, 3.07, color=d.P.muted, weight=1.0, _anchored=True)
        d.arrow(cx, 3.57, cx, y - 0.02, color=d.P.muted, weight=1.0, _anchored=True)


def draw_auditor(d: Canvas) -> None:
    """Auditor 構成。管理主体を分けて相互に検証する。"""
    d.icon_row(3.6, 0.95, 2.8, [("browser", "クライアント")], size=0.42,
               label_size=9)

    for i, (title, product, note, db, dbname) in enumerate([
        ("運用主体 A", "ScalarDL Ledger", "資産の更新を実行して記録する",
         "aws:dynamodb", "DynamoDB"),
        ("運用主体 B", "ScalarDL Auditor", "同じ要求を独立に記録して突き合わせる",
         "azure:cosmos-db", "Cosmos DB"),
    ]):
        # 管理主体が別であることが一目で分かるよう、枠と帯の色を変える
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

    # クライアントから両方へ。Ledger と Auditor は互いに検証し合う
    d.arrow(4.6, 1.62, 3.0, 1.92, color=d.P.muted, weight=1.0, _anchored=True)
    d.arrow(5.4, 1.62, 7.1, 1.92, color=d.P.muted, weight=1.0, _anchored=True)
    d.line(4.68, 2.6, 5.32, 2.6, color=d.P.danger, weight=1.5,
           start_arrow="FILL_ARROW", end_arrow="FILL_ARROW", _anchored=True)
    d.label(3.95, 2.16, 2.1, 0.24, "相互に検証", size=8.5, align="CENTER",
            color=d.P.danger)
    d.label(0.5, 4.62, 9.0, 0.26,
            "片方が改ざんされても、もう片方と突き合わせれば検知できる",
            size=9.5, align="CENTER", color=d.P.muted)


def draw_evidence(d: Canvas) -> None:
    """改ざん検知の流れ。Scalar のブランドアイコンで見せる。"""
    d.asset_icon_flow(0.5, 1.35, 9.0, [
        ("personal-info", "資産の更新要求"),
        ("evidence-chain", "ハッシュで\n前の記録につなぐ"),
        ("timestamp", "いつの記録かを残す"),
        ("tamper-check", "後から検証する"),
    ], size=0.8, label_size=9.5)
    d.label(0.5, 3.4, 9.0, 0.3,
            "記録どうしが鎖状につながっているため、途中を書き換えると鎖が切れる",
            size=11, align="CENTER", color=d.P.text)
    # public-key と private-key は**素材の絵が同じ**（icons.json の sameArtAs）。
    # 並べるときは色を変えて区別する（references/icons.md「素材側の既知の不備」）
    d.asset_icon_row(2.2, 3.95, 5.6, [
        ("public-key", "公開鍵で検証"), ("private-key", "秘密鍵で署名"),
    ], size=0.5, label_size=9, color=[d.P.info, d.P.danger])


def main() -> int:
    p = argparse.ArgumentParser(description="ScalarDL の構成図デッキを作る")
    p.add_argument("--folder", help="出力先の Drive フォルダ URL または ID")
    p.add_argument("--title", default="ScalarDL 構成図")
    args = p.parse_args()

    template = bd.load_template(TEMPLATE)
    deck = bd.TemplateDeck.create(template, title=args.title, folder=args.folder)

    problems = []
    for title, draw in [
        ("ScalarDL は資産の履歴を改ざん検知できる形で残す", draw_stack),
        ("Auditor 構成: 管理主体を分けて相互に検証する", draw_auditor),
        ("改ざんはどう検知されるか", draw_evidence),
    ]:
        ref = deck.add_slide("TITLE_ONLY", title=title)
        d = Canvas(deck, ref["slideId"], template)
        draw(d)
        problems += [f"{title[:18]}…: {m}" for m in
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
