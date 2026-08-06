#!/usr/bin/env python3
"""Drive フォルダの作成と、デッキ関連ファイルの集約。

    python scripts/drive_folder.py create "<フォルダ名>" [--parent <URL/ID>]
    python scripts/drive_folder.py upload <フォルダ URL/ID> <file> [file ...]
    python scripts/drive_folder.py move <フォルダ URL/ID> <ファイル URL/ID> [...]

スライド生成時の運用: まずデッキ名でフォルダを作成し、その ID を
build_deck.py / render_deck.py の --folder に渡してデッキ本体をフォルダ内に
生成する。生成後、スペック（deck.json / deck.py）・図版ソース（.drawio）・
書き出した PNG などの関連ファイルを upload で同じフォルダに収め、
フォルダ URL をユーザーに報告する。

- create は同名フォルダが既にあればそれを再利用する（重複を作らない）
- upload はフォルダ内に同名ファイルがあれば新規作成せず内容を更新する
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
})

FOLDER_MIME = "application/vnd.google-apps.folder"

_FILE_ID_RE = re.compile(r"/d/([a-zA-Z0-9_-]+)")


def file_id(url_or_id: str) -> str:
    """Drive ファイル URL（/d/<ID> 形式）または素の ID から ID を取り出す。"""
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


def cmd_create(drive, name: str, parent: str | None) -> int:
    parent_id = _auth.folder_id(parent) if parent else None
    q = (f"name = '{_escape(name)}' and mimeType = '{FOLDER_MIME}' "
         "and trashed = false")
    if parent_id:
        q += f" and '{parent_id}' in parents"
    hits = drive.files().list(
        q=q, fields="files(id,name)", pageSize=5,
    ).execute().get("files", [])
    if hits:
        fid = hits[0]["id"]
        print(t("Reusing existing folder: {name}", name=name))
    else:
        body: dict = {"name": name, "mimeType": FOLDER_MIME}
        if parent_id:
            body["parents"] = [parent_id]
        fid = drive.files().create(body=body, fields="id").execute()["id"]
        print(t("Created folder: {name}", name=name))
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
        hits = drive.files().list(
            q=(f"name = '{_escape(name)}' and '{fid}' in parents "
               "and trashed = false"),
            fields="files(id)", pageSize=5,
        ).execute().get("files", [])
        if hits:
            drive.files().update(
                fileId=hits[0]["id"], media_body=media, fields="id"
            ).execute()
            print(t("  updated: {name}", name=name))
        else:
            drive.files().create(
                body={"name": name, "parents": [fid]},
                media_body=media, fields="id",
            ).execute()
            print(t("  added: {name}", name=name))
    print(t("Folder: {url}", url=folder_url(fid)))
    return 1 if failed else 0


def cmd_move(drive, folder: str, sources: list[str]) -> int:
    fid = _auth.folder_id(folder)
    for src in sources:
        sid = file_id(src)
        meta = drive.files().get(fileId=sid, fields="name,parents").execute()
        prev = ",".join(meta.get("parents", []))
        drive.files().update(
            fileId=sid, addParents=fid, removeParents=prev, fields="id,parents"
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

    args = p.parse_args()
    _, drive = _auth.services()

    if args.cmd == "create":
        return cmd_create(drive, args.name, args.parent)
    if args.cmd == "upload":
        return cmd_upload(drive, args.folder, args.paths)
    return cmd_move(drive, args.folder, args.sources)


if __name__ == "__main__":
    sys.exit(main())
