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

FOLDER_MIME = "application/vnd.google-apps.folder"

_FILE_ID_RE = re.compile(r"/d/([a-zA-Z0-9_-]+)")


def file_id(url_or_id: str) -> str:
    """Drive ファイル URL（/d/<ID> 形式）または素の ID から ID を取り出す。"""
    m = _FILE_ID_RE.search(url_or_id)
    if m:
        return m.group(1)
    if "/" in url_or_id:
        raise SystemExit(f"ファイル ID を抽出できません: {url_or_id}")
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
        print(f"既存フォルダを再利用: {name}")
    else:
        body: dict = {"name": name, "mimeType": FOLDER_MIME}
        if parent_id:
            body["parents"] = [parent_id]
        fid = drive.files().create(body=body, fields="id").execute()["id"]
        print(f"フォルダを作成: {name}")
    print(f"  ID:  {fid}")
    print(f"  URL: {folder_url(fid)}")
    return 0


def cmd_upload(drive, folder: str, paths: list[str]) -> int:
    from googleapiclient.http import MediaFileUpload

    fid = _auth.folder_id(folder)
    failed = False
    for path in paths:
        if not os.path.exists(path):
            print(f"  skip（ファイルなし）: {path}", file=sys.stderr)
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
            print(f"  更新: {name}")
        else:
            drive.files().create(
                body={"name": name, "parents": [fid]},
                media_body=media, fields="id",
            ).execute()
            print(f"  追加: {name}")
    print(f"フォルダ: {folder_url(fid)}")
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
        print(f"  移動: {meta['name']}")
    print(f"フォルダ: {folder_url(fid)}")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="Drive フォルダの作成・集約")
    sub = p.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("create", help="フォルダを作成する（同名があれば再利用）")
    c.add_argument("name", help="フォルダ名")
    c.add_argument("--parent", help="親フォルダの URL または ID（省略時はマイドライブ直下）")

    u = sub.add_parser("upload", help="ローカルファイルをフォルダへアップロードする")
    u.add_argument("folder", help="フォルダの URL または ID")
    u.add_argument("paths", nargs="+", help="アップロードするファイル")

    m = sub.add_parser("move", help="Drive 上のファイルをフォルダへ移動する")
    m.add_argument("folder", help="フォルダの URL または ID")
    m.add_argument("sources", nargs="+", help="移動するファイルの URL または ID")

    args = p.parse_args()
    _, drive = _auth.services()

    if args.cmd == "create":
        return cmd_create(drive, args.name, args.parent)
    if args.cmd == "upload":
        return cmd_upload(drive, args.folder, args.paths)
    return cmd_move(drive, args.folder, args.sources)


if __name__ == "__main__":
    sys.exit(main())
