#!/usr/bin/env python3
"""Shared OAuth helper for the Google Slides / Drive APIs.

credentials.json / token.json are discovered in this order:

1. `$GSLIDES_CONFIG_DIR` environment variable
2. `<repo>/config/` — the canonical location
"""
from __future__ import annotations

import os
import re
import sys

from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCOPES = [
    "https://www.googleapis.com/auth/presentations",
    "https://www.googleapis.com/auth/drive",
]
EMU_PER_INCH = 914400
EMU_PER_PT = 12700


def config_dirs() -> list[str]:
    dirs = []
    env = os.environ.get("GSLIDES_CONFIG_DIR")
    if env:
        dirs.append(os.path.expanduser(env))
    dirs.append(os.path.join(SKILL_DIR, "config"))
    return dirs


def _find(filename: str) -> str | None:
    for d in config_dirs():
        p = os.path.join(d, filename)
        if os.path.exists(p):
            return p
    return None


def get_credentials():
    """OAuth 認証情報を返す。token が失効していれば自動リフレッシュする。"""
    creds_path = _find("credentials.json")
    if not creds_path:
        raise SystemExit(
            "credentials.json が見つかりません。次のいずれかに配置してください:\n  "
            + "\n  ".join(config_dirs())
            + "\n\nGoogle Cloud Console で OAuth 2.0 デスクトップクライアントを作成し、"
            "Slides API と Drive API を有効化してください。"
        )
    token_path = _find("token.json") or os.path.join(
        os.path.dirname(creds_path), "token.json"
    )

    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except RefreshError:
                # トークンが失効・取り消し済み（invalid_grant）。再認証に落とす
                print("トークンが失効しています。再認証します...", file=sys.stderr)
                creds = None
        if not creds or not creds.valid:
            print("ブラウザで OAuth 認証を行います...", file=sys.stderr)
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
        # リフレッシュトークンを含むため所有者のみ読み書き可で保存する
        fd = os.open(token_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "w") as f:
            f.write(creds.to_json())
    return creds


def services(creds=None):
    """(slides, drive) のサービスクライアントを返す。"""
    creds = creds or get_credentials()
    return (
        build("slides", "v1", credentials=creds),
        build("drive", "v3", credentials=creds),
    )


# ---------- 単位・色 ----------

def inches(v: float) -> int:
    return int(round(v * EMU_PER_INCH))


def to_inches(emu: float) -> float:
    return emu / EMU_PER_INCH


def rgb_to_hex(c: dict) -> str:
    """{"red":0.1,"green":0.2,"blue":0.3} 形式を #RRGGBB に変換する。

    Slides API は値が 0 のチャンネルをキーごと省略するため .get(k, 0) が必須。
    """
    return "#%02X%02X%02X" % tuple(
        round(c.get(k, 0) * 255) for k in ("red", "green", "blue")
    )


def hex_to_rgb(hex_color: str) -> dict:
    h = hex_color.lstrip("#")
    if len(h) != 6:
        raise ValueError(f"不正な hex カラー: {hex_color}")
    return {
        "red": int(h[0:2], 16) / 255,
        "green": int(h[2:4], 16) / 255,
        "blue": int(h[4:6], 16) / 255,
    }


# ---------- ID 抽出 ----------

_PRES_ID_RE = re.compile(r"/presentations?/d/([a-zA-Z0-9_-]+)")


def presentation_id(url_or_id: str) -> str:
    """Google Slides の URL からプレゼンテーション ID を取り出す。ID ならそのまま返す。"""
    m = _PRES_ID_RE.search(url_or_id)
    if m:
        return m.group(1)
    if "/" in url_or_id or " " in url_or_id:
        raise ValueError(f"プレゼンテーション ID を抽出できません: {url_or_id}")
    return url_or_id


_FOLDER_ID_RE = re.compile(r"/folders/([a-zA-Z0-9_-]+)")


def folder_id(url_or_id: str | None) -> str | None:
    """Google Drive フォルダの URL から ID を取り出す。None はそのまま返す。"""
    if not url_or_id:
        return None
    m = _FOLDER_ID_RE.search(url_or_id)
    return m.group(1) if m else url_or_id
