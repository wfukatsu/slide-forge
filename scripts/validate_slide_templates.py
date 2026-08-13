#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from slide_templates import (ROOT, SlideTemplateError, declared_densities,
                             load_example, load_template, render_template,
                             template_entries, validate_template_record)


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate registered single-slide templates")
    ap.add_argument("--id", dest="template_id")
    ap.add_argument("--pack")
    ap.add_argument("--deck-template", default="templates/blank-16x9.json")
    ap.add_argument("--skip-layout", action="store_true")
    args = ap.parse_args()
    # load_manifest() enforces id uniqueness across the whole registry, so a
    # --pack/--id filter cannot hide a collision with another pack.
    entries = template_entries(pack=args.pack)
    if args.template_id:
        entries = [entry for entry in entries if entry["id"] == args.template_id]
        if not entries:
            raise SlideTemplateError(f"unknown slide template: {args.template_id}")
    if not entries:
        raise SlideTemplateError(f"no slide templates registered for pack: {args.pack}")
    problems: list[str] = []
    rendered: list[dict] = []
    for entry in entries:
        try:
            template, path = load_template(entry["id"])
            problems.extend(validate_template_record(template, entry, path))
            # A template with $density tokens must render cleanly at every
            # density; the combined dry-run below then audits both variants.
            try:
                densities: tuple = declared_densities(template) or (None,)
            except SlideTemplateError:
                continue                   # already reported by the record check
            for density in densities:
                example, _ = load_example(entry["id"], density)
                slide = render_template(template, example, density=density)
                rendered.append(slide)
            label = "" if densities == (None,) else f" [{'/'.join(densities)}]"
            print(f"ok schema: {entry['id']}{label}")
        except SlideTemplateError as exc:
            problems.append(str(exc))
    if problems:
        print("\n".join(f"ERROR: {problem}" for problem in problems), file=sys.stderr)
        return 1
    if args.skip_layout:
        return 0
    spec = {"title": "Slide template validation", "slides": rendered}
    with tempfile.TemporaryDirectory(prefix="slide-template-") as tmp:
        spec_path = Path(tmp) / "deck.json"
        spec_path.write_text(json.dumps(spec, ensure_ascii=False, indent=2) + "\n",
                             encoding="utf-8")
        command = [sys.executable, str(ROOT / "scripts/build_deck.py"),
                   "--template", args.deck_template, "--spec", str(spec_path),
                   "--dry-run", "--strict"]
        result = subprocess.run(command, cwd=ROOT)
        return result.returncode


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SlideTemplateError as exc:
        raise SystemExit(str(exc)) from exc
