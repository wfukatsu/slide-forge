#!/usr/bin/env python3
"""Bring a deck up to date with the spreadsheet it was built from.

    .venv/bin/python scripts/sync_deck.py <deck URL/ID> --dry-run      # show what would change
    .venv/bin/python scripts/sync_deck.py <deck URL/ID>

Two kinds of element are refreshed (see sheets_link.py):

1. Linked Sheets charts (`sheetsChart` figures, or any chart linked by hand)
   are redrawn from the sheet with `refreshSheetsChart`.
2. Text and table cells built from `{{sheet:NAME}}` tokens carry their
   templates in their alt text; each bound span is replaced by the cell's
   current formatted value. Only the numbers change: the surrounding text,
   the styling and the object ids stay as they are. A span whose text was
   edited by hand since the last sync is reported and left alone.

Run snapshot_version.py first on a deck people are already using.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _auth  # noqa: E402
import sheets_link  # noqa: E402
from _i18n import t, register  # noqa: E402

register({
    "Refresh a deck's linked charts and bound numbers from its spreadsheet":
        "デッキのリンクグラフとバインド数値をスプレッドシートから更新する",
    "presentation URL or ID": "プレゼンテーションの URL または ID",
    "list the changes without writing": "書き込まずに変更点だけ表示する",
    "  linked charts: {n}": "  リンクグラフ: {n} 件",
    "  bound numbers: {n} change(s) in {m} element(s)":
        "  バインド数値: {m} 要素で {n} 件の変更",
    "  p.{page}: {old} → {new}": "  p.{page}: {old} → {new}",
    "  warn: p.{page}: the bound text was edited by hand and is left as it is: {text}":
        "  警告: p.{page}: バインド文字列が手で編集されているため更新しません: {text}",
    "dry-run: nothing was written": "dry-run: 何も書き込んでいません",
    "Synced: {url}": "同期しました: {url}",
})


def main() -> int:
    p = argparse.ArgumentParser(
        description=t("Refresh a deck's linked charts and bound numbers from its spreadsheet"))
    p.add_argument("deck", help=t("presentation URL or ID"))
    p.add_argument("--dry-run", action="store_true", help=t("list the changes without writing"))
    args = p.parse_args()

    pid = _auth.presentation_id(args.deck)
    slides, _ = _auth.services()
    sheets = _auth.sheets_service()
    pres = slides.presentations().get(
        presentationId=pid, fields="slides(objectId,pageElements)").execute()

    chart_reqs: list[dict] = []
    tagged: list[tuple[int, dict, dict]] = []
    for page, s in enumerate(pres.get("slides", []), 1):
        for el in sheets_link._flat_elements(s.get("pageElements", [])):
            if "sheetsChart" in el:
                chart_reqs.append({"refreshSheetsChart": {"objectId": el["objectId"]}})
            tag = sheets_link.read_tag(el)
            if tag:
                tagged.append((page, el, tag))

    # One read per spreadsheet for every name any element binds
    wanted: dict[str, set[str]] = {}
    for _, _, tag in tagged:
        for entry in tag.get("b", []):
            wanted.setdefault(tag["s"], set()).update(entry.get("v", {}))
    current: dict[str, dict[str, str]] = {}
    for sid, names in wanted.items():
        current[sid] = sheets_link.fetch_values(sheets, sid, sorted(names))

    text_reqs: list[dict] = []
    n_changes, n_elems = 0, 0
    for page, el, tag in tagged:
        reqs, changes, new_tag, problems = sheets_link.plan_text_updates(
            el, tag, current.get(tag["s"], {}))
        for shown in problems:
            print(t("  warn: p.{page}: the bound text was edited by hand and is "
                    "left as it is: {text}", page=page, text=shown[:60]), file=sys.stderr)
        if not changes:
            continue
        n_elems += 1
        n_changes += len(changes)
        for old, new in changes:
            print(t("  p.{page}: {old} → {new}", page=page, old=old, new=new))
        text_reqs += reqs
        text_reqs.append({"updatePageElementAltText": {
            "objectId": el["objectId"],
            "description": sheets_link.BIND_TAG + json.dumps(
                new_tag, ensure_ascii=False)}})

    print(t("  linked charts: {n}", n=len(chart_reqs)))
    print(t("  bound numbers: {n} change(s) in {m} element(s)", n=n_changes, m=n_elems))
    if args.dry_run:
        print(t("dry-run: nothing was written"))
        return 0
    reqs = chart_reqs + text_reqs
    if reqs:
        slides.presentations().batchUpdate(
            presentationId=pid, body={"requests": reqs}).execute()
    print(t("Synced: {url}", url=f"https://docs.google.com/presentation/d/{pid}/edit"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
