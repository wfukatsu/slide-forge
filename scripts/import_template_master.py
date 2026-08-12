#!/usr/bin/env python3
"""Upload templates/masters/<id>.pptx into Drive and re-register the template.

Importing a .pptx makes Google Slides mint fresh object IDs for everything —
layouts, masters, decorations, slides — so the committed templates/<id>.json
stops matching the moment the master lands in a different account. Rather than
patch each ID, this re-runs the normal analysis (inspect_template.py) against
the imported presentation and writes it over the existing registration. Without
--reset-roles that step keeps the human-verified role assignment, so only the
IDs move.

    .venv/bin/python scripts/import_template_master.py --id scalar-2026
    .venv/bin/python scripts/import_template_master.py --all

Run this once per machine after cloning. The layouts and their display names
survive the round trip; only the identifiers change.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from googleapiclient.http import MediaFileUpload

from _auth import get_credentials, services
from _i18n import t, register

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_DIR = ROOT / "templates"
MASTER_DIR = TEMPLATE_DIR / "masters"
PPTX = "application/vnd.openxmlformats-officedocument.presentationml.presentation"

register({
    "no bundled master for {id}: {path} is missing": "{id} の同梱マスターがありません: {path}",
    "unknown template: {id}": "未知のテンプレート: {id}",
    "no bundled masters found in {dir}": "{dir} に同梱マスターがありません",
    "{id}: imported as {url}": "{id}: {url} として取り込みました",
    "{id}: re-registered {n} layouts in {path}": "{id}: {path} に {n} レイアウトを再登録しました",
})


def import_one(drive, template_id: str, *, folder: str | None) -> None:
    reg_path = TEMPLATE_DIR / f"{template_id}.json"
    if not reg_path.exists():
        raise SystemExit(t("unknown template: {id}", id=template_id))
    pptx = MASTER_DIR / f"{template_id}.pptx"
    if not pptx.exists():
        raise SystemExit(t("no bundled master for {id}: {path}",
                           id=template_id, path=pptx.relative_to(ROOT)))
    before = json.loads(reg_path.read_text(encoding="utf-8"))
    display = before.get("displayName") or template_id

    body: dict = {"name": display, "mimeType": "application/vnd.google-apps.presentation"}
    if folder:
        body["parents"] = [folder]
    created = drive.files().create(
        body=body,
        media_body=MediaFileUpload(str(pptx), mimetype=PPTX, resumable=True),
        supportsAllDrives=True, fields="id").execute()
    pid = created["id"]
    url = f"https://docs.google.com/presentation/d/{pid}/edit"
    print(t("{id}: imported as {url}", id=template_id, url=url))

    # Role assignments have been verified by a human. --reset-roles isn't
    # passed, so they're kept.
    subprocess.run([sys.executable, str(ROOT / "scripts/inspect_template.py"), pid,
                    "--emit", str(reg_path), "--name", template_id],
                   cwd=ROOT, check=True)
    after = json.loads(reg_path.read_text(encoding="utf-8"))
    print(t("{id}: re-registered {n} layouts in {path}", id=template_id,
            n=len(after.get("layouts", {})), path=reg_path.relative_to(ROOT)))

    kept = set(before.get("roles", {})) & set(after.get("roles", {}))
    if before.get("roles") and len(kept) < len(before["roles"]):
        lost = sorted(set(before["roles"]) - kept)
        print(f"  warn: roles not carried over: {', '.join(lost)}", file=sys.stderr)


def main() -> int:
    ap = argparse.ArgumentParser(description="Import a bundled master and re-register it")
    ap.add_argument("--id", dest="template_id")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--folder", help="Drive folder ID to import into")
    args = ap.parse_args()
    if not args.template_id and not args.all:
        ap.error("pass --id <template> or --all")
    _, drive = services(get_credentials())
    if args.all:
        ids = sorted(p.stem for p in MASTER_DIR.glob("*.pptx"))
        if not ids:
            raise SystemExit(t("no bundled masters found in {dir}",
                               dir=MASTER_DIR.relative_to(ROOT)))
    else:
        ids = [args.template_id]
    for tid in ids:
        import_one(drive, tid, folder=args.folder)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
