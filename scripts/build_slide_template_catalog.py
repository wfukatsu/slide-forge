#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from slide_templates import (SlideTemplateError, load_example, load_template,
                             render_template, template_entries)


def main() -> int:
    ap = argparse.ArgumentParser(description="Build a deck spec catalog from slide templates")
    ap.add_argument("--pack", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    entries = template_entries(pack=args.pack)
    if not entries:
        raise SlideTemplateError(f"no slide templates registered for pack: {args.pack}")
    slides = []
    for entry in entries:
        template, _ = load_template(entry["id"])
        example, _ = load_example(entry["id"])
        slides.append(render_template(template, example))
    spec = {"title": f"{args.pack} slide templates", "slides": slides}
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(spec, ensure_ascii=False, indent=2) + "\n",
                   encoding="utf-8")
    print(f"{len(slides)} templates -> {out}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SlideTemplateError as exc:
        raise SystemExit(str(exc)) from exc
