#!/usr/bin/env python3
"""Create Drive folders and gather deck-related files into them.

    .venv/bin/python scripts/drive_folder.py create "<folder name>" [--parent <URL/ID>]
    .venv/bin/python scripts/drive_folder.py upload <folder URL/ID> <file> [file ...]
    .venv/bin/python scripts/drive_folder.py move <folder URL/ID> <file URL/ID> [...]

Typical workflow when generating slides: first create a folder named after
the deck, then pass its ID to build_deck.py / render_deck.py's --folder so
the deck itself is generated inside that folder. After generation, use
upload to collect related files — the spec (deck.json / deck.py), diagram
sources (.drawio), exported PNGs, etc. — into the same folder, then report
the folder URL to the user.

- create reuses an existing folder with the same name instead of duplicating it
- upload updates the content of an existing same-named file in the folder
  instead of creating a new one
"""
from __future__ import annotations

import argparse
import mimetypes
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _auth  # noqa: E402
from _i18n import t, register  # noqa: E402

register({
    "Cannot extract a file ID from: {value}": "ファイル ID を抽出できません: {value}",
    "Reusing existing folder: {name}": "既存フォルダを再利用: {name}",
    "Created folder: {name}": "フォルダを作成: {name}",
    "  skip (file not found): {path}": "  skip（ファイルなし）: {path}",
    "  error: {n} files named '{name}' exist in the folder; cannot decide "
    "which one to update. Remove the duplicates or update the file by its ID.":
        "  error: フォルダに同名ファイル '{name}' が {n} 件あり、どれを更新"
        "すべきか決められません。重複を整理するか、ファイル ID を指定して"
        "更新してください。",
    "  updated: {name}": "  更新: {name}",
    "  added: {name}": "  追加: {name}",
    "  moved: {name}": "  移動: {name}",
    "Folder: {url}": "フォルダ: {url}",
    "Create and organize Drive folders": "Drive フォルダの作成・集約",
    "create a folder (reused if one with the same name exists)":
        "フォルダを作成する（同名があれば再利用）",
    "folder name": "フォルダ名",
    "parent folder URL or ID (defaults to My Drive root)":
        "親フォルダの URL または ID（省略時はマイドライブ直下）",
    "upload local files into a folder": "ローカルファイルをフォルダへアップロードする",
    "folder URL or ID": "フォルダの URL または ID",
    "files to upload": "アップロードするファイル",
    "move Drive files into a folder": "Drive 上のファイルをフォルダへ移動する",
    "file URLs or IDs to move": "移動するファイルの URL または ID",
    "Downloaded: {path}": "ダウンロード: {path}",
    "download a Drive file (Google-native files are exported)":
        "Drive のファイルをダウンロードする（Google 形式は変換して書き出す）",
    "output path (extension is added for exports)":
        "出力パス（変換のときは拡張子を補う）",
})

FOLDER_MIME = "application/vnd.google-apps.folder"

_FILE_ID_RE = re.compile(r"/d/([a-zA-Z0-9_-]+)")


def file_id(url_or_id: str) -> str:
    """Extract the ID from a Drive file URL (`/d/<ID>` form) or a bare ID."""
    m = _FILE_ID_RE.search(url_or_id)
    if m:
        return m.group(1)
    if "/" in url_or_id:
        raise SystemExit(t("Cannot extract a file ID from: {value}", value=url_or_id))
    return url_or_id


def folder_url(fid: str) -> str:
    return f"https://drive.google.com/drive/folders/{fid}"


def _escape(name: str) -> str:
    return name.replace("\\", "\\\\").replace("'", "\\'")


def ensure_folder(drive, name: str, parent: str | None = None) -> tuple[str, bool]:
    """Return the folder ID, creating it if it doesn't exist. Returns (ID, was_created).

    The lookup uses an **exact match** on `name = '…'`. `name contains` is
    avoided because it matches on word prefixes and can pick up an unrelated
    folder.
    """
    parent_id = _auth.folder_id(parent) if parent else None
    q = (f"name = '{_escape(name)}' and mimeType = '{FOLDER_MIME}' "
         "and trashed = false")
    if parent_id:
        q += f" and '{parent_id}' in parents"
    hits = drive.files().list(
        q=q, fields="files(id,name)", pageSize=5,
        supportsAllDrives=True, includeItemsFromAllDrives=True,
    ).execute().get("files", [])
    if hits:
        return hits[0]["id"], False
    body: dict = {"name": name, "mimeType": FOLDER_MIME}
    if parent_id:
        body["parents"] = [parent_id]
    fid = drive.files().create(body=body, fields="id",
                               supportsAllDrives=True).execute()["id"]
    return fid, True


EXPORT_MIME = {
    "application/vnd.google-apps.spreadsheet":
        ("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", ".xlsx"),
    "application/vnd.google-apps.document":
        ("application/vnd.openxmlformats-officedocument.wordprocessingml.document", ".docx"),
    "application/vnd.google-apps.presentation":
        ("application/vnd.openxmlformats-officedocument.presentationml.presentation", ".pptx"),
}


def download(drive, fid: str, out_path: str) -> str:
    """Download a Drive file to `out_path`.

    Google-native files (Spreadsheet / Document / Slides) are exported to their
    Office equivalent, which is what makes a filled-in Google Spreadsheet
    readable with the Drive scope alone — no Sheets scope, so no re-auth.
    """
    import io
    from googleapiclient.http import MediaIoBaseDownload

    meta = drive.files().get(fileId=fid, fields="name,mimeType",
                             supportsAllDrives=True).execute()
    mime = meta.get("mimeType", "")
    if mime in EXPORT_MIME:
        target, ext = EXPORT_MIME[mime]
        if not out_path.endswith(ext):
            out_path += ext
        request = drive.files().export_media(fileId=fid, mimeType=target)
    else:
        request = drive.files().get_media(fileId=fid, supportsAllDrives=True)

    os.makedirs(os.path.dirname(os.path.abspath(out_path)) or ".", exist_ok=True)
    with io.FileIO(out_path, "wb") as fh:
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()
    return out_path


def cmd_download(drive, source: str, out: str | None) -> int:
    fid = file_id(source)
    path = download(drive, fid, out or os.path.join("out", "drive", fid))
    print(t("Downloaded: {path}", path=path))
    return 0


def cmd_create(drive, name: str, parent: str | None) -> int:
    fid, created = ensure_folder(drive, name, parent)
    print(t("Created folder: {name}", name=name) if created
          else t("Reusing existing folder: {name}", name=name))
    print(f"  ID:  {fid}")
    print(f"  URL: {folder_url(fid)}")
    return 0


def cmd_upload(drive, folder: str, paths: list[str]) -> int:
    from googleapiclient.http import MediaFileUpload

    fid = _auth.folder_id(folder)
    failed = False
    for path in paths:
        if not os.path.exists(path):
            print(t("  skip (file not found): {path}", path=path), file=sys.stderr)
            failed = True
            continue
        name = os.path.basename(path)
        mime = mimetypes.guess_type(path)[0] or "application/octet-stream"
        media = MediaFileUpload(path, mimetype=mime, resumable=False)
        # Excluding folders from the search: picking up a same-named
        # **subfolder** as the update target would try to overwrite a folder
        # with a file and break things
        hits = drive.files().list(
            q=(f"name = '{_escape(name)}' and '{fid}' in parents "
               f"and mimeType != '{FOLDER_MIME}' "
               "and trashed = false"),
            fields="files(id)", pageSize=5,
            supportsAllDrives=True, includeItemsFromAllDrives=True,
        ).execute().get("files", [])
        if len(hits) > 1:
            # Updating without being able to decide which one to target risks
            # overwriting the wrong file. Stop here and ask the user to clean up.
            print(t("  error: {n} files named '{name}' exist in the folder; "
                    "cannot decide which one to update. Remove the duplicates "
                    "or update the file by its ID.", n=len(hits), name=name),
                  file=sys.stderr)
            failed = True
            continue
        if hits:
            drive.files().update(
                fileId=hits[0]["id"], media_body=media, fields="id",
                supportsAllDrives=True,
            ).execute()
            print(t("  updated: {name}", name=name))
        else:
            drive.files().create(
                body={"name": name, "parents": [fid]},
                media_body=media, fields="id", supportsAllDrives=True,
            ).execute()
            print(t("  added: {name}", name=name))
    print(t("Folder: {url}", url=folder_url(fid)))
    return 1 if failed else 0


def cmd_move(drive, folder: str, sources: list[str]) -> int:
    fid = _auth.folder_id(folder)
    for src in sources:
        sid = file_id(src)
        meta = drive.files().get(fileId=sid, fields="name,parents",
                                 supportsAllDrives=True).execute()
        prev = ",".join(meta.get("parents", []))
        drive.files().update(
            fileId=sid, addParents=fid, removeParents=prev,
            fields="id,parents", supportsAllDrives=True,
        ).execute()
        print(t("  moved: {name}", name=meta["name"]))
    print(t("Folder: {url}", url=folder_url(fid)))
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=t("Create and organize Drive folders"))
    sub = p.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("create",
                       help=t("create a folder (reused if one with the same name exists)"))
    c.add_argument("name", help=t("folder name"))
    c.add_argument("--parent", help=t("parent folder URL or ID (defaults to My Drive root)"))

    u = sub.add_parser("upload", help=t("upload local files into a folder"))
    u.add_argument("folder", help=t("folder URL or ID"))
    u.add_argument("paths", nargs="+", help=t("files to upload"))

    m = sub.add_parser("move", help=t("move Drive files into a folder"))
    m.add_argument("folder", help=t("folder URL or ID"))
    m.add_argument("sources", nargs="+", help=t("file URLs or IDs to move"))

    d = sub.add_parser("download",
                       help=t("download a Drive file (Google-native files are exported)"))
    d.add_argument("source", help=t("file URL or ID"))
    d.add_argument("--out", help=t("output path (extension is added for exports)"))

    args = p.parse_args()
    _, drive = _auth.services()

    if args.cmd == "create":
        return cmd_create(drive, args.name, args.parent)
    if args.cmd == "upload":
        return cmd_upload(drive, args.folder, args.paths)
    if args.cmd == "download":
        return cmd_download(drive, args.source, args.out)
    return cmd_move(drive, args.folder, args.sources)


if __name__ == "__main__":
    sys.exit(main())
