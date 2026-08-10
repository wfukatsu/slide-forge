#!/usr/bin/env python3
from __future__ import annotations

import argparse

from slide_templates import SlideTemplateError, template_entries


def main() -> int:
    ap = argparse.ArgumentParser(description="List registered single-slide templates")
    ap.add_argument("--pack")
    ap.add_argument("--tag")
    args = ap.parse_args()
    entries = template_entries(pack=args.pack)
    if args.tag:
        entries = [entry for entry in entries if args.tag in entry.get("tags", [])]
    for entry in entries:
        print(f"{entry['id']:<24} {entry['displayName']} [{entry['pack']}/{entry['category']}]")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SlideTemplateError as exc:
        raise SystemExit(str(exc)) from exc
