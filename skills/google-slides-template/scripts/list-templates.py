#!/usr/bin/env python3
"""登録済みテンプレートの一覧を出す。対話でテンプレートを選ばせるときの選択肢の材料。

AskUserQuestion の選択肢を手で書くとテンプレートを足したときに腐るので、
`templates/*.json` から実データを読んで出す。`--json` は機械可読な形。

    python scripts/list-templates.py
    python scripts/list-templates.py --json
"""
from __future__ import annotations

import argparse
import glob
import json
import os

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
    if isinstance(derived, dict):      # 派生元は文字列のことも dict のこともある
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
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json", action="store_true", help="JSON で出力する")
    args = ap.parse_args()

    items = [summarize(p) for p in sorted(glob.glob(os.path.join(TEMPLATES, "*.json")))]
    if args.json:
        print(json.dumps(items, ensure_ascii=False, indent=2))
        return 0

    if not items:
        print(f"登録済みテンプレートがありません（{TEMPLATES}）。")
        print("URL から解析して登録する: scripts/inspect-template.py <URL> --emit templates/<id>.json --name <id>")
        return 0

    print(f"{len(items)} 件のテンプレート\n")
    for it in items:
        head = f"{it['id']}  —  {it['displayName']}" if it["displayName"] else it["id"]
        print(head)
        bits = [f"レイアウト {it['layouts']} 種", f"比率 {it['aspectRatio']}"]
        if it["boilerplateSlides"]:
            bits.append(f"定型スライド {it['boilerplateSlides']} 枚同梱")
        if it["derivedFrom"]:
            bits.append(f"派生元 {it['derivedFrom']}")
        print("  " + " / ".join(bits))
        print("  ロール: " + (", ".join(it["roleNames"]) or "（未割当）"))
        if it["rolesNote"]:
            # ロールのメモは長いので 1 行目だけ。全文は --json か template.json を見る
            note = it["rolesNote"].split("。")[0]
            if len(note) < len(it["rolesNote"]):
                note += "。…（全文は --json）"
            print(f"  メモ: {note}")
        print(f"  spec: --template {it['path']}")
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
