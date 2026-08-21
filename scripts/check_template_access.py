#!/usr/bin/env python3
"""Report whether the master each registered template points at is usable.

A `generationMode: copy` template generates by duplicating a real Google Slides
presentation, and `templates/<id>.json` only records its ID. On a fresh clone —
or for anyone outside the organization that owns the master — that presentation
is simply not reachable, and the failure otherwise surfaces as an opaque 404
from Drive in the middle of a deck build.

Setup runs this to find out which templates work with the account that just
authenticated, and to be told what to do about the ones that do not: build your
own master, register one you can open, or import a .pptx.

    .venv/bin/python scripts/check_template_access.py
    .venv/bin/python scripts/check_template_access.py --id scalar-2026
    .venv/bin/python scripts/check_template_access.py --json

Exit code is 0 when every registered template is usable and 1 when at least one
is not, so a setup script can branch on it.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from googleapiclient.errors import HttpError

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _auth import get_credentials, services  # noqa: E402
from _i18n import t, register  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_DIR = ROOT / "templates"

register({
    "Report whether each template's master is reachable":
        "各テンプレートのマスターに到達できるかを確認する",
    "check a single template": "テンプレートを 1 つだけ確認する",
    "output as JSON": "JSON で出力する",
    "unknown template: {id}": "未知のテンプレート: {id}",
    "no master needed (generationMode: create)":
        "マスター不要（generationMode: create）",
    "master reachable: {name}": "マスターに到達できる: {name}",
    "master is in the trash": "マスターがゴミ箱にある",
    "no permission to copy it": "複製する権限がない",
    "no access with this account": "このアカウントではアクセスできない",
    "not registered (no presentationId)": "未登録（presentationId が無い）",
    "Drive could not be asked about it (HTTP {code})":
        "Drive に問い合わせできなかった（HTTP {code}）",
    "{n} of {total} templates are ready to generate.\n":
        "{total} 件中 {n} 件のテンプレートが生成に使える。\n",
    "These templates cannot generate until a master exists in your own Drive: {ids}":
        "これらのテンプレートは、自分の Drive にマスターが用意されるまで生成できない: {ids}",
    "Pick one route per template (README setup step 5):":
        "テンプレートごとに 1 つ選ぶ（README セットアップ手順 5）:",
    "  a. no access to any master — build your own from a design spec:\n"
    "     the template-forge skill, or .venv/bin/python scripts/build_template.py --help":
        "  a. どのマスターにもアクセスできない場合 — デザイン仕様から自分で作る:\n"
        "     template-forge スキル、または .venv/bin/python scripts/build_template.py --help",
    "  b. you can open a master in Drive — register it:\n"
    "     .venv/bin/python scripts/inspect_template.py <URL> --emit templates/<id>.json --name <id>":
        "  b. Drive でマスターを開ける場合 — それを登録する:\n"
        "     .venv/bin/python scripts/inspect_template.py <URL> --emit templates/<id>.json --name <id>",
    "  c. you were handed a .pptx — save it as templates/masters/<id>.pptx, then:\n"
    "     .venv/bin/python scripts/import_template_master.py --id <id>":
        "  c. .pptx を受け取っている場合 — templates/masters/<id>.pptx に置いて:\n"
        "     .venv/bin/python scripts/import_template_master.py --id <id>",
    "Leaving them unusable is fine too: blank-16x9 needs no master, so the "
    "google-slides spec path and every --dry-run validation still work.":
        "使えないままにしておくのでも構わない: blank-16x9 はマスター不要なので、"
        "google-slides の仕様パスと --dry-run の検証はそのまま動く。",
})

# status -> ok? — a template is usable only when its master can be duplicated.
_OK = {"no-master-needed", "ok"}


def registered() -> list[str]:
    return sorted(p.stem for p in TEMPLATE_DIR.glob("*.json"))


def needs_drive(template_id: str) -> bool:
    """True when the registration points at a Drive file we have to look up."""
    path = TEMPLATE_DIR / f"{template_id}.json"
    if not path.exists():
        return False
    reg = json.loads(path.read_text(encoding="utf-8"))
    return reg.get("generationMode") != "create" and bool(reg.get("presentationId"))


def check_one(drive, template_id: str) -> dict:
    """Classify one registration. `drive` is only called for a copy-mode template."""
    path = TEMPLATE_DIR / f"{template_id}.json"
    if not path.exists():
        raise SystemExit(t("unknown template: {id}", id=template_id))
    reg = json.loads(path.read_text(encoding="utf-8"))
    pid = reg.get("presentationId")
    if reg.get("generationMode") == "create":
        status, name = "no-master-needed", ""
        message = t("no master needed (generationMode: create)")
    elif not pid:
        status, name = "unregistered", ""
        message = t("not registered (no presentationId)")
    else:
        try:
            meta = drive.files().get(
                fileId=pid, fields="name,trashed,capabilities/canCopy",
                supportsAllDrives=True).execute()
        except HttpError as exc:
            # 404 covers both "deleted" and "you may not see it" — Drive does not
            # distinguish, and neither answer changes what the user has to do.
            code = getattr(exc, "status_code", None) \
                or getattr(getattr(exc, "resp", None), "status", None)
            if code in (403, 404):
                status, message = "no-access", t("no access with this account")
            else:
                status = "error"
                message = t("Drive could not be asked about it (HTTP {code})",
                            code=code or "?")
            name = ""
        else:
            name = meta.get("name", "")
            if meta.get("trashed"):
                status, message = "trashed", t("master is in the trash")
            elif not meta.get("capabilities", {}).get("canCopy", True):
                status, message = "no-copy", t("no permission to copy it")
            else:
                status, message = "ok", t("master reachable: {name}", name=name)
    return {
        "id": template_id,
        "generationMode": reg.get("generationMode", "copy"),
        "presentationId": pid or "",
        "status": status,
        "ok": status in _OK,
        "masterName": name if status == "ok" else "",
        "message": message,
    }


def main() -> int:
    ap = argparse.ArgumentParser(
        description=t("Report whether each template's master is reachable"))
    ap.add_argument("--id", dest="template_id", help=t("check a single template"))
    ap.add_argument("--json", action="store_true", help=t("output as JSON"))
    args = ap.parse_args()

    ids = [args.template_id] if args.template_id else registered()
    # Auth is needed only when something actually points at a Drive file, so a
    # clone with nothing but blank-16x9 can run this before step 2.
    drive = services(get_credentials())[1] if any(needs_drive(i) for i in ids) else None
    results = [check_one(drive, tid) for tid in ids]

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return 0 if all(r["ok"] for r in results) else 1

    for r in results:
        mark = "OK  " if r["ok"] else "--  "
        print(f"{mark}{r['id']}: {r['message']}")
    good = [r for r in results if r["ok"]]
    print()
    print(t("{n} of {total} templates are ready to generate.\n",
            n=len(good), total=len(results)))

    blocked = [r["id"] for r in results if not r["ok"]]
    if not blocked:
        return 0
    print(t("These templates cannot generate until a master exists in your own "
            "Drive: {ids}", ids=", ".join(blocked)))
    print(t("Pick one route per template (README setup step 5):"))
    print(t("  a. no access to any master — build your own from a design spec:\n"
            "     the template-forge skill, or .venv/bin/python scripts/build_template.py --help"))
    print(t("  b. you can open a master in Drive — register it:\n"
            "     .venv/bin/python scripts/inspect_template.py <URL> --emit templates/<id>.json --name <id>"))
    print(t("  c. you were handed a .pptx — save it as templates/masters/<id>.pptx, then:\n"
            "     .venv/bin/python scripts/import_template_master.py --id <id>"))
    print()
    print(t("Leaving them unusable is fine too: blank-16x9 needs no master, so the "
            "google-slides spec path and every --dry-run validation still work."))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
