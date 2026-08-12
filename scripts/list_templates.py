#!/usr/bin/env python3
"""List registered templates. Supplies the choices for interactively selecting a template.

Hand-writing the AskUserQuestion choices would go stale as soon as a template
is added, so this reads the real data from `templates/*.json` and prints it.
`--json` gives a machine-readable form.

    python scripts/list_templates.py
    python scripts/list_templates.py --json
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _i18n import t, register  # noqa: E402

register({
    "List registered templates": "登録済みテンプレートの一覧を出す",
    "output as JSON": "JSON で出力する",
    "No registered templates ({dir}).": "登録済みテンプレートがありません（{dir}）。",
    "Analyze and register one from a URL: scripts/inspect_template.py <URL>"
    " --emit templates/<id>.json --name <id>":
        "URL から解析して登録する: scripts/inspect_template.py <URL>"
        " --emit templates/<id>.json --name <id>",
    "{n} templates\n": "{n} 件のテンプレート\n",
    "{n} layouts": "レイアウト {n} 種",
    "aspect ratio {ratio}": "比率 {ratio}",
    "{n} boilerplate slides included": "定型スライド {n} 枚同梱",
    "derived from {id}": "派生元 {id}",
    "roles: {roles}": "ロール: {roles}",
    "(unassigned)": "（未割当）",
    "... (see --json for the full text)": "。…（全文は --json）",
    "note: {note}": "メモ: {note}",
})

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(HERE)
TEMPLATES = os.path.join(SKILL_DIR, "templates")


def summarize(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        t = json.load(f)
    layouts = t.get("layouts", {}) or {}
    roles = t.get("roles", {}) or {}
    page = t.get("pageSize", {}) or {}
    existing = t.get("existingSlideIds", []) or []
    derived = t.get("derivedFrom", "")
    if isinstance(derived, dict):      # derivedFrom can be either a string or a dict
        derived = derived.get("presentationId", "")
    return {
        "id": t.get("name") or os.path.splitext(os.path.basename(path))[0],
        "path": os.path.relpath(path, SKILL_DIR),
        "displayName": t.get("displayName", ""),
        "layouts": len(layouts),
        "roles": roles,
        "roleNames": sorted(roles),
        "aspectRatio": page.get("aspectRatio", ""),
        "boilerplateSlides": len(existing),
        "rolesNote": t.get("__roles_note", ""),
        "derivedFrom": derived,
        "sourceUrl": t.get("sourceUrl", ""),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=t("List registered templates"))
    ap.add_argument("--json", action="store_true", help=t("output as JSON"))
    args = ap.parse_args()

    items = [summarize(p) for p in sorted(glob.glob(os.path.join(TEMPLATES, "*.json")))]
    if args.json:
        print(json.dumps(items, ensure_ascii=False, indent=2))
        return 0

    if not items:
        print(t("No registered templates ({dir}).", dir=TEMPLATES))
        print(t("Analyze and register one from a URL: scripts/inspect_template.py <URL>"
                " --emit templates/<id>.json --name <id>"))
        return 0

    print(t("{n} templates\n", n=len(items)))
    for it in items:
        head = f"{it['id']}  —  {it['displayName']}" if it["displayName"] else it["id"]
        print(head)
        bits = [t("{n} layouts", n=it["layouts"]),
                t("aspect ratio {ratio}", ratio=it["aspectRatio"])]
        if it["boilerplateSlides"]:
            bits.append(t("{n} boilerplate slides included", n=it["boilerplateSlides"]))
        if it["derivedFrom"]:
            bits.append(t("derived from {id}", id=it["derivedFrom"]))
        print("  " + " / ".join(bits))
        print("  " + t("roles: {roles}",
                       roles=", ".join(it["roleNames"]) or t("(unassigned)")))
        if it["rolesNote"]:
            # The roles note can be long, so show only the first sentence. See --json or template.json for the full text
            note = it["rolesNote"].split("。")[0]
            if len(note) < len(it["rolesNote"]):
                note += t("... (see --json for the full text)")
            print("  " + t("note: {note}", note=note))
        print(f"  spec: --template {it['path']}")
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
