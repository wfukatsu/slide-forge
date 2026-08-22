#!/usr/bin/env python3
"""Render a deck module to Google Slides.

    .venv/bin/python scripts/render_deck.py path/to/mydeck.py --title "Title"
    .venv/bin/python scripts/render_deck.py mydeck.py --only 1-12        # partial render (for prototyping)
    .venv/bin/python scripts/render_deck.py mydeck.py --folder <URL/ID>  # destination folder
    .venv/bin/python scripts/render_deck.py mydeck.py --dry-run          # just list the structure

Always run the validate_layout.py checks before generating (can be skipped
with --skip-validate, but that's not recommended). The checks don't call the
API, so they avoid wasted generation and quota usage.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import deckkit  # noqa: E402
import settings  # noqa: E402
import validate_layout as vl  # noqa: E402
from _i18n import t, register  # noqa: E402
from build_deck import TemplateDeck, deliver_local  # noqa: E402
from diagrams import Canvas  # noqa: E402

register({
    "render a deck module to Google Slides":
        "デッキモジュールを Google Slides に生成する",
    "deck module .py": "デッキモジュールの .py",
    "template.json (defaults to the deck's TEMPLATE)":
        "template.json（省略時はデッキの TEMPLATE）",
    "presentation title (defaults to the deck's TITLE)":
        "プレゼンテーションのタイトル（省略時はデッキの TITLE）",
    "destination Drive folder URL or ID":
        "出力先 Drive フォルダの URL または ID",
    "a range like 1-12; renders a subset to check the look":
        "1-12 のような範囲。部分生成して見た目を確かめる用",
    "list the structure without calling the API":
        "API を呼ばず構成を一覧する",
    "do not render page numbers": "ページ番号を描かない",
    "skip the coordinate checks (not recommended)":
        "座標検査を飛ばす（非推奨）",
    "where the deliverable goes: google (Drive / Slides) or local "
    "(folder / PowerPoint); defaults to config/settings.json":
        "成果物の出力先: google（Drive / Slides）または local"
        "（フォルダ / PowerPoint）。既定は config/settings.json",
    "specify --template or define TEMPLATE in the deck":
        "--template を指定するか、デッキに TEMPLATE を定義してください",
    "The coordinate check found {n} problems; aborting generation:":
        "座標検査で {n} 件の問題があります。生成を中止します:",
    "Fix them and rerun (use --skip-validate to generate anyway)":
        "修正後に再実行してください（どうしても生成するなら --skip-validate）",
    "specify --title or define TITLE in the deck":
        "--title を指定するか、デッキに TITLE を定義してください",
    "{n} slides:": "{n} 枚:",
    "  [figure]": "  [図]",
})


def main() -> int:
    p = argparse.ArgumentParser(
        description=t("render a deck module to Google Slides"))
    p.add_argument("deck", help=t("deck module .py"))
    p.add_argument("--template",
                   help=t("template.json (defaults to the deck's TEMPLATE)"))
    p.add_argument("--title",
                   help=t("presentation title (defaults to the deck's TITLE)"))
    p.add_argument("--folder", help=t("destination Drive folder URL or ID"))
    p.add_argument("--only",
                   help=t("a range like 1-12; renders a subset to check "
                          "the look"))
    p.add_argument("--dry-run", action="store_true",
                   help=t("list the structure without calling the API"))
    p.add_argument("--no-page-numbers", action="store_true",
                   help=t("do not render page numbers"))
    p.add_argument("--skip-validate", action="store_true",
                   help=t("skip the coordinate checks (not recommended)"))
    p.add_argument("--output", metavar="google|local",
                   help=t("where the deliverable goes: google (Drive / Slides) "
                          "or local (folder / PowerPoint); defaults to "
                          "config/settings.json"))
    args = p.parse_args()

    try:
        output_target = settings.output_target(args.output)
    except settings.SettingsError as exc:
        raise SystemExit(f"ERROR: {exc}") from None

    mod, slides = vl.load_deck_module(args.deck)
    if args.template:
        with open(args.template, encoding="utf-8") as f:
            template = json.load(f)
    else:
        template = getattr(mod, "TEMPLATE", None)
    if template is None:
        raise SystemExit(t("specify --template or define TEMPLATE in "
                           "the deck"))

    if not args.skip_validate:
        problems = vl.check(template, slides)
        if problems:
            print(t("The coordinate check found {n} problems; aborting "
                    "generation:", n=len(problems)), file=sys.stderr)
            for msg in problems:
                print("  " + msg, file=sys.stderr)
            print("\n" + t("Fix them and rerun (use --skip-validate to "
                           "generate anyway)"), file=sys.stderr)
            return 1

    if args.only:
        a, _, b = args.only.partition("-")
        lo, hi = int(a), int(b or a)
        slides = slides[lo - 1:hi]

    title = args.title or getattr(mod, "TITLE", None)
    if not title:
        raise SystemExit(t("specify --title or define TITLE in the deck"))

    if args.dry_run:
        print(t("{n} slides:", n=len(slides)))
        for i, s in enumerate(slides, 1):
            resolved, layout = vl.resolve_layout(template, s["layout"])
            name = layout.get("displayName", resolved) if layout else "??"
            mark = t("  [figure]") if s.get("draw") else ""
            print(f"  {i:2d}. {s['layout']:24s} -> {name}{mark}  "
                  f"{(s.get('title') or '')[:44]}")
        return 0

    deck = TemplateDeck.create(template, title=title, folder=args.folder)
    for s in slides:
        ref = deck.add_slide(
            s["layout"], title=s.get("title"), subtitle=s.get("subtitle"),
            body=s.get("body"), bodies=s.get("bodies"), notes=s.get("notes"),
            body_font_size=s.get("bodyFontSize", deckkit.BODY_FONT_SIZE),
            body_line_spacing=s.get("bodyLineSpacing", deckkit.BODY_LINE_SPACING),
        )
        if s.get("draw"):
            s["draw"](Canvas(deck, ref["slideId"], template))
    if not args.no_page_numbers:
        n = deck.add_page_numbers()
        print(f"  page numbers: {n} slides")
    print(f"  requests: {len(deck.requests)}")
    url = deck.commit()
    print(f"Done! {len(deck.slide_ids)} slides created.")
    print(f"Open: {url}")
    if output_target == settings.LOCAL:
        deliver_local(deck, title)
    return 0


if __name__ == "__main__":
    sys.exit(main())
