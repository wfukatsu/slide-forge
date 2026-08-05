#!/usr/bin/env python3
"""既存プレゼンテーションを編集する前に「版」を確保する（ロールバック用）。

    python scripts/snapshot_version.py <URL または ID> [--out out/backups] [--no-export]

やること:

1. 編集前の先頭リビジョン ID と更新時刻を記録して表示する
2. そのリビジョンの keepForever ピン留めを試みる
   （ネイティブの Slides ファイルでは API がサポートしないことがある → 警告のみ）
3. 現状の PPTX をローカルへエクスポートしてバックアップする（--no-export で省略）

ユーザーがすでに使っている既存デッキ（既知の URL）へスライドの挿入・修正を
行うときは、最初にこのスクリプトを実行し、表示されたリビジョン ID と
バックアップのパスを報告してから編集すること。差し戻しは Google Slides UI の
「ファイル → 版の履歴」から行える。名前付きの版も API では作れないため、
必要なら同 UI から付ける。
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
        # エクスポートは 10MB 制限があるため、画像の多いデッキは失敗しうる
        print(f"警告: PPTX エクスポートに失敗しました（バックアップなしで続行）: {e}",
              file=sys.stderr)
        return None


def main() -> int:
    p = argparse.ArgumentParser(description="既存デッキ編集前に版を確保する")
    p.add_argument("source", help="プレゼンテーションの URL または ID")
    p.add_argument("--out", default="out/backups", help="PPTX バックアップの出力先")
    p.add_argument("--no-export", action="store_true", help="PPTX バックアップを省略する")
    args = p.parse_args()

    pres_id = _auth.presentation_id(args.source)
    _, drive = _auth.services()

    meta = drive.files().get(fileId=pres_id, fields="name").execute()
    revs = list_revisions(drive, pres_id)
    if not revs:
        raise SystemExit("リビジョンが取得できませんでした（権限不足の可能性）")
    head = revs[-1]

    print(meta["name"])
    print(f"  編集前リビジョン: {head['id']} ({head['modifiedTime']})")

    try:
        drive.revisions().update(
            fileId=pres_id, revisionId=head["id"], body={"keepForever": True}
        ).execute()
        print("  keepForever ピン留め: OK")
    except HttpError as e:
        print(f"  keepForever ピン留め: 不可（ネイティブ Slides では未対応のことがある）: "
              f"{e.status_code if hasattr(e, 'status_code') else e}", file=sys.stderr)

    if not args.no_export:
        path = export_backup(drive, pres_id, args.out, meta["name"], head)
        if path:
            print(f"  バックアップ: {path}")

    print("差し戻しは Slides UI の「ファイル → 版の履歴」から。"
          "上のリビジョン ID と時刻をユーザーに報告してから編集を始めること。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
