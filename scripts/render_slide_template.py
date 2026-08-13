#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from slide_templates import (DENSITIES, SlideTemplateError, declared_densities,
                             load_template, render_template)


def main() -> int:
    ap = argparse.ArgumentParser(description="Render one registered slide template")
    ap.add_argument("--template", required=True, dest="template_id")
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--density", choices=DENSITIES,
                    help="density variant to resolve (default: the template's "
                         "defaultDensity; ignored by templates without $density)")
    args = ap.parse_args()
    template, _ = load_template(args.template_id)
    data = json.loads(Path(args.data).read_text(encoding="utf-8"))
    slide = render_template(template, data, density=args.density)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(slide, ensure_ascii=False, indent=2) + "\n",
                   encoding="utf-8")
    density = ""
    if declared_densities(template):
        density = f" [{args.density or template.get('defaultDensity')}]"
    print(f"{args.template_id}{density} -> {out}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (SlideTemplateError, json.JSONDecodeError) as exc:
        raise SystemExit(str(exc)) from exc
