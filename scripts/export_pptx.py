#!/usr/bin/env python3
"""Export a generated Google Slides deck to PowerPoint (.pptx).

    python scripts/export_pptx.py <URL or ID> [--out <path.pptx>]
    python scripts/export_pptx.py <URL> --folder <Drive folder URL/ID>

Writes the .pptx via the Drive API's files.export. The appearance is
preserved exactly as generated in Slides, but the export is **a snapshot at
that point in time** — regenerating the deck requires re-exporting.

- files.export has a 10MB limit. If exceeded, it automatically falls back to
  fetching via exportLinks (so decks with many images/diagrams don't fail)
- if --out is omitted, saves to out/pptx/<deck name>.pptx
- passing --folder also uploads the exported .pptx to the same Drive folder,
  alongside the spec and diagram sources (per the Drive folder convention)
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
import drive_folder  # noqa: E402
from _i18n import t, register  # noqa: E402

register({
    "exportLinks has no PPTX URL (possibly missing permissions)":
        "exportLinks に PPTX の URL がありません（権限不足の可能性）",
    "the deck exceeds the files.export size limit; retrying via exportLinks...":
        "デッキが files.export のサイズ上限を超えています。"
        "exportLinks 経由で再取得します...",
    "files.export failed with HTTP {code}: {err}":
        "files.export が HTTP {code} で失敗しました: {err}",
    "Export a Google Slides deck as .pptx":
        "Google Slides デッキを .pptx に書き出す",
    "presentation URL or ID": "プレゼンテーションの URL または ID",
    "output path (default: out/pptx/<deck name>.pptx)":
        "出力パス（省略時: out/pptx/<デッキ名>.pptx）",
    "Drive folder URL or ID to upload the exported .pptx into":
        "書き出した .pptx をアップロードする Drive フォルダの URL または ID",
})

PPTX_MIME = "application/vnd.openxmlformats-officedocument.presentationml.presentation"


def safe_name(name: str) -> str:
    """Turns the deck name into something usable as a filename (keeps Japanese as-is)."""
    cleaned = re.sub(r'[\\/:*?"<>|\s]+', "_", name).strip("_")
    return cleaned[:80] or "deck"


def _is_export_size_limit(e: HttpError) -> bool:
    """Determines whether files.export was rejected for exceeding 10MB.

    A size-limit rejection comes back as HTTP 403 with reason
    "exportSizeLimitExceeded". If 403/404s from permission errors or a wrong
    ID were also routed to the fallback, the real cause would get masked by a
    different error on the exportLinks side, making it hard to diagnose — so
    this checks strictly.
    """
    status = getattr(e, "status_code", None) \
        or getattr(getattr(e, "resp", None), "status", None)
    if status != 403:
        return False
    for d in getattr(e, "error_details", None) or []:
        if isinstance(d, dict) and d.get("reason") == "exportSizeLimitExceeded":
            return True
    # Older googleapiclient versions don't have error_details, so fall back
    # to checking the response body
    return b"exportSizeLimitExceeded" in (getattr(e, "content", b"") or b"")


def _export_via_link(drive, creds, pres_id: str, path: str) -> None:
    """Fallback for decks over 10MB: fetches directly from the exportLinks URL."""
    from google.auth.transport.requests import AuthorizedSession

    meta = drive.files().get(fileId=pres_id, fields="exportLinks",
                             supportsAllDrives=True).execute()
    link = meta.get("exportLinks", {}).get(PPTX_MIME)
    if not link:
        raise SystemExit(t("exportLinks has no PPTX URL (possibly missing permissions)"))
    session = AuthorizedSession(creds)
    # Write to a temp file first and move it into place with os.replace, so an
    # interrupted download doesn't leave a broken .pptx at the final path
    tmp = path + ".part"
    try:
        with session.get(link, stream=True) as r:
            r.raise_for_status()
            with open(tmp, "wb") as f:
                for chunk in r.iter_content(1 << 20):
                    f.write(chunk)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


def export_pptx(drive, creds, pres_id: str, path: str) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    # Same as the exportLinks path: write via a temp file and move it to the
    # final path only on success
    tmp = path + ".part"
    try:
        req = drive.files().export_media(fileId=pres_id, mimeType=PPTX_MIME)
        with open(tmp, "wb") as f:
            dl = MediaIoBaseDownload(f, req)
            done = False
            while not done:
                _, done = dl.next_chunk()
        os.replace(tmp, path)
        return
    except HttpError as e:
        # Only fall back for the size limit; permission errors or a wrong ID raise here
        if not _is_export_size_limit(e):
            status = getattr(e, "status_code", None) \
                or getattr(getattr(e, "resp", None), "status", None)
            raise SystemExit(t("files.export failed with HTTP {code}: {err}",
                               code=status or "?", err=e))
        print(t("the deck exceeds the files.export size limit; retrying via "
                "exportLinks..."), file=sys.stderr)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)
    _export_via_link(drive, creds, pres_id, path)


def main() -> int:
    p = argparse.ArgumentParser(description=t("Export a Google Slides deck as .pptx"))
    p.add_argument("source", help=t("presentation URL or ID"))
    p.add_argument("--out", help=t("output path (default: out/pptx/<deck name>.pptx)"))
    p.add_argument("--folder",
                   help=t("Drive folder URL or ID to upload the exported .pptx into"))
    args = p.parse_args()

    pres_id = _auth.presentation_id(args.source)
    creds = _auth.get_credentials()
    _, drive = _auth.services(creds)

    meta = drive.files().get(fileId=pres_id, fields="name",
                             supportsAllDrives=True).execute()
    path = args.out or os.path.join("out", "pptx", f"{safe_name(meta['name'])}.pptx")

    export_pptx(drive, creds, pres_id, path)
    size = os.path.getsize(path)
    print(meta["name"])
    print(f"  PPTX: {path} ({size / (1 << 20):.1f} MB)")

    if args.folder:
        drive_folder.cmd_upload(drive, args.folder, [path])
    return 0


if __name__ == "__main__":
    sys.exit(main())
