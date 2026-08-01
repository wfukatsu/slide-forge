#!/usr/bin/env python3
"""Google Slides サムネイル取得スクリプト（視覚的 QA 用）

指定した Google Slides プレゼンテーションの全スライドサムネイルを PNG で取得する。

使い方:
  source .venv/bin/activate
  python fetch-thumbnails.py

設定変数（スクリプト内で編集）:
  PRES_ID     対象プレゼンテーション ID（Google Slides URL の /d/ 以降）
  OUTPUT_DIR  サムネイル保存先ディレクトリ（デフォルト: ./thumbnails）

前提条件:
  - Python 3.10+
  - config/credentials.json 配置済み
  - pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
"""

import sys
if sys.version_info < (3, 10):
    sys.exit("Error: Python 3.10+ が必要です。現在: Python {}.{}".format(*sys.version_info[:2]))

import os
import urllib.request
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/presentations",
    "https://www.googleapis.com/auth/drive.file",
]
SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
CREDS_FILE = os.path.join(SKILL_DIR, "config", "credentials.json")
TOKEN_FILE = os.path.join(SKILL_DIR, "config", "token.json")

# ─── 設定変数（使用前に編集してください）────────────────────
PRES_ID = ""  # 対象プレゼンテーション ID を設定
OUTPUT_DIR = os.path.join(SKILL_DIR, "thumbnails")


def get_credentials():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "w") as f:
            f.write(creds.to_json())
    return creds


def main():
    creds = get_credentials()
    slides_service = build("slides", "v1", credentials=creds)
    pres = slides_service.presentations().get(presentationId=PRES_ID).execute()
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for i, slide in enumerate(pres["slides"]):
        thumb = slides_service.presentations().pages().getThumbnail(
            presentationId=PRES_ID,
            pageObjectId=slide["objectId"],
            thumbnailProperties_mimeType="PNG",
            thumbnailProperties_thumbnailSize="LARGE",
        ).execute()
        path = os.path.join(OUTPUT_DIR, f"slide_{i+1:02d}.png")
        urllib.request.urlretrieve(thumb["contentUrl"], path)
        print(f"  Saved: slide_{i+1:02d}.png")
    print(f"\nDone! {len(pres['slides'])} thumbnails saved to {OUTPUT_DIR}")


if __name__ == "__main__":
    if not os.path.exists(CREDS_FILE):
        sys.exit(
            f"Error: {CREDS_FILE} が見つかりません。\n"
            "GCP Console から OAuth クライアント credentials.json をダウンロードし、\n"
            f"{os.path.dirname(CREDS_FILE)}/ に配置してください。"
        )
    if not PRES_ID:
        sys.exit(
            "Error: PRES_ID が設定されていません。\n"
            "スクリプト内の PRES_ID 変数に対象プレゼンテーション ID を設定してください。"
        )
    try:
        main()
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        sys.exit(1)
