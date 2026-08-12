#!/usr/bin/env python3
"""Export a registered master to templates/masters/<id>.pptx.

The registration in templates/<id>.json only points at a Drive presentation, so
a clone cannot use a `generationMode: copy` template without access to it. This
writes the master itself into the repository; import_template_master.py puts it
back into a Drive account and re-registers it.

    .venv/bin/python scripts/export_template_master.py --id scalar-2026
    .venv/bin/python scripts/export_template_master.py --all

Drive's export endpoint refuses files over 10MB (`exportSizeLimitExceeded`), and
some masters are past it. There is no API way around the limit: download those
by hand from the Slides UI (File > Download > Microsoft PowerPoint) and save the
file to templates/masters/<id>.pptx yourself. Do not strip slides to get under
the limit — Slides deletes layouts that no slide uses any more, and the bundled
slides listed in `existingSlideIds` are part of what the template offers.
"""
from __future__ import annotations

import argparse
import io
import json
import socket
import sys
import time
from pathlib import Path

from googleapiclient.http import MediaIoBaseDownload

# Masters run 6-8MB, and the default socket timeout isn't enough to read them
# fully, so it fails
socket.setdefaulttimeout(300)

from _auth import get_credentials, services
from _i18n import t, register

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_DIR = ROOT / "templates"
MASTER_DIR = TEMPLATE_DIR / "masters"
PPTX = "application/vnd.openxmlformats-officedocument.presentationml.presentation"

register({
    "{id}: no presentationId (nothing to export; generationMode is probably 'create')":
        "{id}: presentationId がありません（generationMode が 'create' の可能性）",
    "{id}: too large for the Drive export endpoint (10MB limit). Download it by "
    "hand from the Slides UI (File > Download > Microsoft PowerPoint) and save "
    "it as {path}":
        "{id}: Drive のエクスポート上限（10MB）を超えています。Slides の画面から手動で "
        "ダウンロード（ファイル > ダウンロード > Microsoft PowerPoint）し、{path} "
        "として保存してください",
    "unknown template: {id}": "未知のテンプレート: {id}",
})


def registered() -> list[str]:
    return sorted(p.stem for p in TEMPLATE_DIR.glob("*.json"))


def export_one(drive, template_id: str) -> bool:
    path = TEMPLATE_DIR / f"{template_id}.json"
    if not path.exists():
        raise SystemExit(t("unknown template: {id}", id=template_id))
    reg = json.loads(path.read_text(encoding="utf-8"))
    pid = reg.get("presentationId")
    if not pid:
        print(t("{id}: no presentationId (nothing to export; generationMode is "
                "probably 'create')", id=template_id))
        return True
    out = MASTER_DIR / f"{template_id}.pptx"
    data = None
    for attempt in range(3):
        try:
            buf = io.BytesIO()
            dl = MediaIoBaseDownload(
                buf, drive.files().export_media(fileId=pid, mimeType=PPTX))
            done = False
            while not done:
                _, done = dl.next_chunk()
            data = buf.getvalue()
            break
        except Exception as exc:                   # noqa: BLE001 - reported, not raised
            if "exportSizeLimitExceeded" in str(exc):
                print(t("{id}: too large for the Drive export endpoint (10MB limit). "
                        "Download it by hand from the Slides UI (File > Download > "
                        "Microsoft PowerPoint) and save it as {path}",
                        id=template_id, path=out.relative_to(ROOT)), file=sys.stderr)
                return False
            if attempt == 2:
                raise
            print(f"  {template_id}: {type(exc).__name__}, retrying "
                  f"({attempt + 2}/3)", file=sys.stderr)
            time.sleep(3 * (attempt + 1))
    MASTER_DIR.mkdir(parents=True, exist_ok=True)
    out.write_bytes(data)
    print(f"{template_id} -> {out.relative_to(ROOT)} ({len(data) / 1024 / 1024:.2f} MB)")
    return True


def main() -> int:
    ap = argparse.ArgumentParser(description="Export a registered master to .pptx")
    ap.add_argument("--id", dest="template_id")
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args()
    if not args.template_id and not args.all:
        ap.error("pass --id <template> or --all")
    _, drive = services(get_credentials())
    ids = registered() if args.all else [args.template_id]
    ok = True
    for tid in ids:
        ok = export_one(drive, tid) and ok
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
