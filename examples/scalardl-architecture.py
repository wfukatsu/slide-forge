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
BRAND = os.path.join(SKILL_DIR, "assets", "scalar", "product-logos")
LOGO_DL = os.path.join(BRAND, "scalardl-logo-horizontal.png")


def _band(d: Canvas, x, y, w, h, *, logo=None, text=None, text_size=10.5,
          fill=None, stroke=None) -> str:
    """製品の帯。ロゴを左に置き、右に説明を書く。矢印でつなげるよう帯の id を返す。"""
    oid = d.shape(x, y, w, h, kind="ROUND_RECTANGLE",
                  fill=fill or lighten(d.P.primary, 0.88),
                  stroke=stroke or d.P.primary)
    tx = x + 0.25
    if logo:
        d.image(x + 0.25, y + (h - 0.34) / 2, 1.45, 0.34, logo, fit="contain",
                alt=os.path.basename(logo))
        tx = x + 1.85
    if text:
        d.label(tx, y, x + w - tx - 0.2, h, text, size=text_size,
                align="START", valign="MIDDLE", color=d.P.text)
    return oid


def draw_stack(d: Canvas) -> None:
    """クライアント → ScalarDL → ScalarDB → データベース の 4 層。

    矢印はすべて箱の辺から辺へ引く（node() + vlink()）。アイコンやキャプションを
    狙って座標を打つと、矢印が宙に浮くか文字の上で止まる。
    """
    d.label(0.5, 0.92, 9.0, 0.22, "クライアント", size=9, align="START",
            color=d.P.muted)
    clients = [d.node(1.2 + i * 2.6, 1.16, 2.4, 0.52, t, icon=ic,
                      icon_size=0.34, horizontal=True, size=9,
                      icon_color=d.P.primary)
               for i, (ic, t) in enumerate([("browser", "業務アプリ"),
                                            ("mobile", "モバイル"),
                                            ("server", "外部システム")])]
    dl = _band(d, 1.2, 1.98, 7.6, 0.62, logo=LOGO_DL,
               text="コントラクトを実行し、資産の履歴をハッシュでつないで残す")
    db = _band(d, 1.2, 2.88, 7.6, 0.5, text="ScalarDB（トランザクション層）",
               text_size=10, fill=lighten(d.P.info, 0.9), stroke=d.P.info)
    for c in clients:
        d.vlink(c, dl, color=d.P.muted, weight=1.0)
    d.vlink(dl, db, color=d.P.muted, weight=1.0)

    # 見出しは枠の下に置く。上から入る矢印と重ねないため
    y = 3.66
    dbs = []
    for i, (vendor, name, label) in enumerate([
        ("aws", "aws:dynamodb", "DynamoDB"),
        ("azure", "azure:cosmos-db", "Cosmos DB"),
        ("gcp", "gcp:cloud-spanner", "Spanner"),
    ]):
        zx = 1.2 + i * 1.95
        d.cloud_zone(zx, y, 1.75, 1.3, vendor=vendor, title_size=7.5,
                     title_at="bottom")
        dbs.append(d.node(zx + 0.25, y + 0.1, 1.25, 0.86, label,
                          cloud_icon=name, icon_size=0.4, size=8))
    ox = 1.2 + 3 * 1.95
    d.cloud_zone(ox, y, 1.75, 1.3, title="自前運用", title_size=7.5,
                 title_at="bottom")
    for k, (ic, label) in enumerate([("database", "PostgreSQL"),
                                     ("stack", "Cassandra")]):
        dbs.append(d.node(ox + 0.06 + k * 0.83, y + 0.1, 0.8, 0.86, label,
                          icon=ic, icon_size=0.34, size=7,
                          icon_color=d.P.primary))
    for n in dbs:
        d.vlink(db, n, color=d.P.muted, weight=1.0)


def draw_auditor(d: Canvas) -> None:
    """Auditor 構成。管理主体を分けて相互に検証する。"""
    client = d.node(4.25, 0.95, 1.5, 0.56, "クライアント", icon="browser",
                    icon_size=0.38, horizontal=True, size=9,
                    icon_color=d.P.primary)
    bands = []
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
        bands.append(_band(d, zx + 0.25, 2.35, 3.65, 0.5, text=product,
                           text_size=10.5, fill=lighten(accent, 0.88),
                           stroke=accent))
        d.label(zx + 0.25, 2.92, 3.65, 0.24, note, size=8.5, align="CENTER",
                color=d.P.muted)
        d.cloud_zone(zx + 0.25, 3.3, 3.65, 1.0,
                     vendor="aws" if i == 0 else "azure", title_size=7.5)
        d.cloud_icon(db, zx + 1.86, 3.52, 0.4, label=dbname, label_size=8,
                     label_w=2.0)

    # クライアントから両方へ。Ledger と Auditor は互いに検証し合う
    for band in bands:
        d.link(client, band, gap=0.0, color=d.P.muted, weight=1.0)
    d.hlink(bands[0], bands[1], color=d.P.danger, weight=1.5,
            start_arrow="FILL_ARROW")
    d.label(3.95, 2.0, 2.1, 0.24, "相互に検証", size=8.5, align="CENTER",
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
