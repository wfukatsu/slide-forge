#!/usr/bin/env python3
"""Generates a "layout sample" deck that lays out every layout in the
template, one per slide.

A catalog for checking, with actual text flowed in, how each layout looks,
which placeholders it has, and which role it's assigned to. Also used to
visually verify that role assignments are correct.

    .venv/bin/python scripts/layout_sample.py --template templates/scalar-2026.json
    .venv/bin/python scripts/layout_sample.py --template templates/aixdevops.json --only-roles
"""
from __future__ import annotations

import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_deck as bd  # noqa: E402
from _i18n import t, register  # noqa: E402
from diagrams import Canvas, lighten  # noqa: E402
from slide_templates import DEFAULT_LANG, resolve_label  # noqa: E402

register({
    "Generate a layout sample deck": "レイアウトサンプルを生成する",
    "path to template.json": "template.json のパス",
    "title of the generated presentation": "生成するプレゼンテーションのタイトル",
    "URL or ID of the destination Drive folder": "出力先 Drive フォルダの URL または ID",
    "output only layouts that have a role assigned":
        "ロールが割り当てられたレイアウトだけを出力する",
    "do not draw the annotation band at the bottom": "下部の説明帯を描かない",
    "only list the target layouts": "対象レイアウトの一覧だけ表示する",
    "{name}: {n} layouts": "{name}: {n} レイアウト",
    "  {layouts} layouts / page numbers on {pages} slides":
        "  {layouts} レイアウト / ページ番号 {pages} 枚",
    "language of the sample deck's own labels, from slide-templates/i18n/":
        "サンプルデッキ自身のラベルの言語（slide-templates/i18n/ から引く）",
})

# Deliberately Japanese. This deck exists to show how text flows through a
# layout, and CJK is what exercises wrapping and line height. It is sample
# copy standing in for the caller's content, not a word the tool prints for
# itself, so it does not come from the label resource.
SAMPLE_BODY = [
    "本文プレースホルダのサンプルです。",
    "このレイアウトに文字を流し込むと、この位置・この大きさで表示されます。",
    "折り返しと行間の見え方もここで確認できます。",
]
SAMPLE_COLUMN = ["カラムのサンプル", "この枠に文字が入ります", "折り返しの確認用"]


def roles_of(template: dict, key: str) -> list[str]:
    return [r for r, k in template.get("roles", {}).items() if k == key]


def annotate(deck, template: dict, slide_id: str, key: str, layout: dict, index: int):
    """Draws a band at the bottom of the slide showing the layout's identity."""
    d = Canvas(deck, slide_id, template)
    roles = roles_of(template, key)
    ph = layout.get("placeholders", [])
    geo = layout.get("elements", {})

    y = 4.60
    d.band(0.4, y, 9.2, 0.34, fill=lighten(d.P.primary, 0.9))
    left = f"{index:02d}  {key}   « {layout.get('displayName', '')} »"
    d.label(0.55, y + 0.03, 4.6, 0.28, left, size=9, bold=True,
            color=d.P.primaryDark, valign="MIDDLE")

    # Keep the right side to a single line. Wrapping would overflow the band
    parts = [" / ".join(roles) if roles else d._label("layout_sample.no_role"),
             ", ".join(ph) if ph else d._label("layout_sample.no_placeholder")]
    if "body" in geo:
        b = geo["body"]
        parts.append(f"body {b['w']:.2f}×{b['h']:.2f}in")
    d.label(4.9, y + 0.03, 4.55, 0.28, "  │  ".join(parts), size=7.5,
            color=d.P.muted, align="END", valign="MIDDLE")


def sample_text(key: str, layout: dict, template: dict,
                lang: str = DEFAULT_LANG) -> dict:
    """Assembles sample copy suited to the placeholders a layout has."""
    ph = layout.get("placeholders", [])
    roles = roles_of(template, key)
    out: dict = {}
    if "TITLE" in ph:
        # The title is just the layout key. Including the display name too
        # would wrap and crowd into the body
        out["title"] = key
    if "SUBTITLE" in ph:
        name = layout.get("displayName", "")
        sep = resolve_label("layout_sample.name_sep", lang)
        out["subtitle"] = f"{name}{sep}" + (
            resolve_label("layout_sample.role_prefix", lang) + " / ".join(roles)
            if roles else resolve_label("layout_sample.no_role", lang))
    body_slots = [p for p in ph if p.split("#")[0] == "BODY"]
    if len(body_slots) == 1:
        out["body"] = SAMPLE_BODY
    elif len(body_slots) > 1:
        out["bodies"] = [
            [resolve_label("layout_sample.column_n", lang).format(i=i + 1)]
            + SAMPLE_COLUMN for i in range(len(body_slots))
        ]
    return out


def main() -> int:
    p = argparse.ArgumentParser(description=t("Generate a layout sample deck"))
    p.add_argument("--template", required=True, help=t("path to template.json"))
    p.add_argument("--title", help=t("title of the generated presentation"))
    p.add_argument("--folder", help=t("URL or ID of the destination Drive folder"))
    p.add_argument("--only-roles", action="store_true",
                   help=t("output only layouts that have a role assigned"))
    p.add_argument("--no-annotation", action="store_true",
                   help=t("do not draw the annotation band at the bottom"))
    p.add_argument("--dry-run", action="store_true",
                   help=t("only list the target layouts"))
    p.add_argument("--lang", default=DEFAULT_LANG,
                   help=t("language of the sample deck's own labels, "
                          "from slide-templates/i18n/"))
    args = p.parse_args()

    template = bd.load_template(args.template)
    keys = [k for k in template["layouts"] if not k.startswith("__")]
    if args.only_roles:
        used = set(template.get("roles", {}).values())
        keys = [k for k in keys if k in used]

    if args.dry_run:
        print(t("{name}: {n} layouts", name=template["displayName"], n=len(keys)))
        for i, k in enumerate(keys, 1):
            l = template["layouts"][k]
            print(f"  {i:2d}. {k:28s} {str(roles_of(template, k)):34s} "
                  f"{l.get('placeholders')}")
        return 0

    title = args.title or resolve_label(
        "layout_sample.deck_title", args.lang).format(name=template["displayName"])
    deck = bd.TemplateDeck.create(template, title=title, folder=args.folder)
    deck.lang = args.lang          # Canvas._label() in annotate() reads this

    for i, key in enumerate(keys, 1):
        layout = template["layouts"][key]
        ref = deck.add_slide(key, **sample_text(key, layout, template, args.lang),
                             notes=f"{key} / {layout.get('displayName')} / "
                                   f"layoutId={layout['layoutId']} / "
                                   f"placeholders={layout.get('placeholders')}")
        if not args.no_annotation:
            annotate(deck, template, ref["slideId"], key, layout, i)

    n = deck.add_page_numbers()
    print(t("  {layouts} layouts / page numbers on {pages} slides",
            layouts=len(keys), pages=n))
    print(f"Open: {deck.commit()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
