#!/usr/bin/env python3
"""Secure a "version" of an existing presentation before editing it (for rollback).

    .venv/bin/python scripts/snapshot_version.py <URL or ID> [--out out/backups] [--no-export]

What it does:

1. Records and prints the pre-edit head revision ID and its modified time
2. Attempts to pin that revision with keepForever
   (native Slides files may not support this via the API -> warning only)
3. Exports the current PPTX locally as a backup (omit with --no-export)

When inserting or modifying slides in an existing deck the user is already
using (a known URL), always run this script first, report the printed
revision ID and backup path, and only then start editing. Rollback can be
done from the Google Slides UI ("File -> Version history"). Named versions
also can't be created via the API, so add one from that same UI if needed.
"""
from __future__ import annotations

import argparse
import os
import re
import sys

from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _auth  # noqa: E402
from _i18n import t, register  # noqa: E402

register({
    "Warning: PPTX export failed (continuing without a backup): {err}":
        "警告: PPTX エクスポートに失敗しました（バックアップなしで続行）: {err}",
    "Snapshot a deck's revision before editing it": "既存デッキ編集前に版を確保する",
    "presentation URL or ID": "プレゼンテーションの URL または ID",
    "output directory for the PPTX backup": "PPTX バックアップの出力先",
    "skip the PPTX backup": "PPTX バックアップを省略する",
    "Could not list revisions (possibly missing permissions)":
        "リビジョンが取得できませんでした（権限不足の可能性）",
    "  pre-edit revision: {rev} ({time})": "  編集前リビジョン: {rev} ({time})",
    "  keepForever pin: OK": "  keepForever ピン留め: OK",
    "  keepForever pin: unavailable (native Slides files may not support it): {err}":
        "  keepForever ピン留め: 不可（ネイティブ Slides では未対応のことがある）: {err}",
    "  backup: {path}": "  バックアップ: {path}",
    "Roll back via the Slides UI (File → Version history). Report the revision "
    "ID and time above to the user before starting the edit.":
        "差し戻しは Slides UI の「ファイル → 版の履歴」から。"
        "上のリビジョン ID と時刻をユーザーに報告してから編集を始めること。",
})

PPTX_MIME = "application/vnd.openxmlformats-officedocument.presentationml.presentation"


def list_revisions(drive, file_id: str) -> list[dict]:
    revs: list[dict] = []
    token = None
    while True:
        res = drive.revisions().list(
            fileId=file_id,
            fields="nextPageToken,revisions(id,modifiedTime)",
            pageSize=1000,
            pageToken=token,
        ).execute()
        revs.extend(res.get("revisions", []))
        token = res.get("nextPageToken")
        if not token:
            return revs


def export_backup(drive, file_id: str, out_dir: str, name: str, rev: dict) -> str | None:
    os.makedirs(out_dir, exist_ok=True)
    safe = re.sub(r"[^\w\-]+", "_", name).strip("_")[:60] or file_id
    stamp = re.sub(r"[:\-]", "", rev["modifiedTime"]).replace(".000Z", "Z")
    path = os.path.join(out_dir, f"{safe}-rev{rev['id']}-{stamp}.pptx")
    try:
        req = drive.files().export_media(fileId=file_id, mimeType=PPTX_MIME)
        with open(path, "wb") as f:
            dl = MediaIoBaseDownload(f, req)
            done = False
            while not done:
                _, done = dl.next_chunk()
        return path
    except HttpError as e:
        if os.path.exists(path):
            os.remove(path)
        # Export has a 10MB limit, so decks with many images can fail
        print(t("Warning: PPTX export failed (continuing without a backup): {err}",
                err=e), file=sys.stderr)
        return None


def main() -> int:
    p = argparse.ArgumentParser(
        description=t("Snapshot a deck's revision before editing it"))
    p.add_argument("source", help=t("presentation URL or ID"))
    p.add_argument("--out", default="out/backups",
                   help=t("output directory for the PPTX backup"))
    p.add_argument("--no-export", action="store_true", help=t("skip the PPTX backup"))
    args = p.parse_args()

    pres_id = _auth.presentation_id(args.source)
    _, drive = _auth.services()

    meta = drive.files().get(fileId=pres_id, fields="name",
                             supportsAllDrives=True).execute()
    revs = list_revisions(drive, pres_id)
    if not revs:
        raise SystemExit(t("Could not list revisions (possibly missing permissions)"))
    head = revs[-1]

    print(meta["name"])
    print(t("  pre-edit revision: {rev} ({time})",
            rev=head["id"], time=head["modifiedTime"]))

    try:
        drive.revisions().update(
            fileId=pres_id, revisionId=head["id"], body={"keepForever": True}
        ).execute()
        print(t("  keepForever pin: OK"))
    except HttpError as e:
        print(t("  keepForever pin: unavailable (native Slides files may not "
                "support it): {err}",
                err=e.status_code if hasattr(e, "status_code") else e),
              file=sys.stderr)

    if not args.no_export:
        path = export_backup(drive, pres_id, args.out, meta["name"], head)
        if path:
            print(t("  backup: {path}", path=path))

    print(t("Roll back via the Slides UI (File → Version history). Report the "
            "revision ID and time above to the user before starting the edit."))
    return 0


if __name__ == "__main__":
    sys.exit(main())
