#!/usr/bin/env python3
"""生成済み Google Slides デッキを PowerPoint (.pptx) にエクスポートする。

    python scripts/export_pptx.py <URL または ID> [--out <path.pptx>]
    python scripts/export_pptx.py <URL> --folder <Drive フォルダ URL/ID>

Drive API の files.export で .pptx を書き出す。見た目は Slides で生成した
とおりに保たれるが、エクスポートは**その時点のスナップショット**であり、
デッキを再生成したら再エクスポートが必要。

- files.export には 10MB 制限がある。超えた場合は exportLinks 経由で
  自動的に取得し直す（画像・図版の多いデッキでも失敗しない）
- --out 省略時は out/pptx/<デッキ名>.pptx に保存する
- --folder を渡すと、書き出した .pptx を同じ Drive フォルダにも
  アップロードして仕様・図版ソースと並べて保管する（Drive フォルダルール）
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
    "files.export failed ({err}); retrying via exportLinks...":
        "files.export が失敗（{err}）。exportLinks 経由で再取得します...",
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
    """デッキ名をファイル名に使える形へ落とす（日本語はそのまま残す）。"""
    cleaned = re.sub(r'[\\/:*?"<>|\s]+', "_", name).strip("_")
    return cleaned[:80] or "deck"


def _export_via_link(drive, creds, pres_id: str, path: str) -> None:
    """10MB 超のデッキ向けフォールバック。exportLinks の URL から直接取得する。"""
    from google.auth.transport.requests import AuthorizedSession

    meta = drive.files().get(fileId=pres_id, fields="exportLinks",
                             supportsAllDrives=True).execute()
    link = meta.get("exportLinks", {}).get(PPTX_MIME)
    if not link:
        raise SystemExit(t("exportLinks has no PPTX URL (possibly missing permissions)"))
    session = AuthorizedSession(creds)
    with session.get(link, stream=True) as r:
        r.raise_for_status()
        with open(path, "wb") as f:
            for chunk in r.iter_content(1 << 20):
                f.write(chunk)


def export_pptx(drive, creds, pres_id: str, path: str) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    try:
        req = drive.files().export_media(fileId=pres_id, mimeType=PPTX_MIME)
        with open(path, "wb") as f:
            dl = MediaIoBaseDownload(f, req)
            done = False
            while not done:
                _, done = dl.next_chunk()
    except HttpError as e:
        if os.path.exists(path):
            os.remove(path)
        print(t("files.export failed ({err}); retrying via exportLinks...",
                err=e.status_code if hasattr(e, "status_code") else e),
              file=sys.stderr)
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
