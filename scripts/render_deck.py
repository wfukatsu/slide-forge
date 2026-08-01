#!/usr/bin/env python3
"""デッキモジュールを Google Slides に生成する。

    python scripts/render_deck.py path/to/mydeck.py --title "タイトル"
    python scripts/render_deck.py mydeck.py --only 1-12        # 部分生成（試作用）
    python scripts/render_deck.py mydeck.py --folder <URL/ID>  # 出力先フォルダ
    python scripts/render_deck.py mydeck.py --dry-run          # 構成の一覧だけ

生成前に validate_layout.py の検査を必ず通す（--skip-validate で外せるが非推奨）。
検査は API を呼ばないので、無駄な生成とクォータ消費を防げる。
"""
from __future__ import annotations

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import deckkit  # noqa: E402
import validate_layout as vl  # noqa: E402
from build_deck import TemplateDeck  # noqa: E402
from diagrams import Canvas  # noqa: E402


def main() -> int:
    p = argparse.ArgumentParser(description="デッキモジュールを Google Slides に生成する")
    p.add_argument("deck", help="デッキモジュールの .py")
    p.add_argument("--template", help="template.json（省略時はデッキの TEMPLATE）")
    p.add_argument("--title", help="プレゼンテーションのタイトル（省略時はデッキの TITLE）")
    p.add_argument("--folder", help="出力先 Drive フォルダの URL または ID")
    p.add_argument("--only", help="1-12 のような範囲。部分生成して見た目を確かめる用")
    p.add_argument("--dry-run", action="store_true", help="API を呼ばず構成を一覧する")
    p.add_argument("--no-page-numbers", action="store_true", help="ページ番号を描かない")
    p.add_argument("--skip-validate", action="store_true",
                   help="座標検査を飛ばす（非推奨）")
    args = p.parse_args()

    mod, slides = vl.load_deck_module(args.deck)
    template = (json.load(open(args.template, encoding="utf-8")) if args.template
                else getattr(mod, "TEMPLATE", None))
    if template is None:
        raise SystemExit("--template を指定するか、デッキに TEMPLATE を定義してください")

    if not args.skip_validate:
        problems = vl.check(template, slides)
        if problems:
            print(f"座標検査で {len(problems)} 件の問題があります。生成を中止します:",
                  file=sys.stderr)
            for msg in problems:
                print("  " + msg, file=sys.stderr)
            print("\n修正後に再実行してください（どうしても生成するなら --skip-validate）",
                  file=sys.stderr)
            return 1

    if args.only:
        a, _, b = args.only.partition("-")
        lo, hi = int(a), int(b or a)
        slides = slides[lo - 1:hi]

    title = args.title or getattr(mod, "TITLE", None)
    if not title:
        raise SystemExit("--title を指定するか、デッキに TITLE を定義してください")

    if args.dry_run:
        print(f"{len(slides)} 枚:")
        for i, s in enumerate(slides, 1):
            resolved, layout = vl.resolve_layout(template, s["layout"])
            name = layout.get("displayName", resolved) if layout else "??"
            mark = "  [図]" if s.get("draw") else ""
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
    return 0


if __name__ == "__main__":
    sys.exit(main())
