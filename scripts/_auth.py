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

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _i18n import t, register  # noqa: E402

register({
    "credentials.json not found. Place it in one of:\n  {dirs}\n\n"
    "Create an OAuth 2.0 desktop client in the Google Cloud Console and "
    "enable the Slides API and the Drive API.":
        "credentials.json が見つかりません。次のいずれかに配置してください:\n  {dirs}\n\n"
        "Google Cloud Console で OAuth 2.0 デスクトップクライアントを作成し、"
        "Slides API と Drive API を有効化してください。",
    "Token expired; re-authenticating...": "トークンが失効しています。再認証します...",
    "Opening the browser for OAuth consent...": "ブラウザで OAuth 認証を行います...",
    "Invalid hex color: {value}": "不正な hex カラー: {value}",
    "Cannot extract a presentation ID from: {value}":
        "プレゼンテーション ID を抽出できません: {value}",
})

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
    """Return OAuth credentials, automatically refreshing the token if it has expired."""
    creds_path = _find("credentials.json")
    if not creds_path:
        raise SystemExit(t(
            "credentials.json not found. Place it in one of:\n  {dirs}\n\n"
            "Create an OAuth 2.0 desktop client in the Google Cloud Console and "
            "enable the Slides API and the Drive API.",
            dirs="\n  ".join(config_dirs()),
        ))
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
                # Token expired or revoked (invalid_grant); fall back to re-authentication
                print(t("Token expired; re-authenticating..."), file=sys.stderr)
                creds = None
        if not creds or not creds.valid:
            print(t("Opening the browser for OAuth consent..."), file=sys.stderr)
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save with owner-only read/write permissions since it contains the refresh token
        fd = os.open(token_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "w") as f:
            f.write(creds.to_json())
    return creds


def services(creds=None):
    """Return (slides, drive) service clients."""
    creds = creds or get_credentials()
    return (
        build("slides", "v1", credentials=creds),
        build("drive", "v3", credentials=creds),
    )


# ---------- Units & colors ----------

def inches(v: float) -> int:
    return int(round(v * EMU_PER_INCH))


def to_inches(emu: float) -> float:
    return emu / EMU_PER_INCH


def rgb_to_hex(c: dict) -> str:
    """Convert {"red":0.1,"green":0.2,"blue":0.3} format to #RRGGBB.

    The Slides API omits a channel key entirely when its value is 0, so
    .get(k, 0) is required.
    """
    return "#%02X%02X%02X" % tuple(
        round(c.get(k, 0) * 255) for k in ("red", "green", "blue")
    )


def hex_to_rgb(hex_color: str) -> dict:
    h = hex_color.lstrip("#")
    if len(h) != 6:
        raise ValueError(t("Invalid hex color: {value}", value=hex_color))
    return {
        "red": int(h[0:2], 16) / 255,
        "green": int(h[2:4], 16) / 255,
        "blue": int(h[4:6], 16) / 255,
    }


# ---------- ID extraction ----------

_PRES_ID_RE = re.compile(r"/presentations?/d/([a-zA-Z0-9_-]+)")


def presentation_id(url_or_id: str) -> str:
    """Extract the presentation ID from a Google Slides URL. If already an ID, return it as is."""
    m = _PRES_ID_RE.search(url_or_id)
    if m:
        return m.group(1)
    if "/" in url_or_id or " " in url_or_id:
        raise ValueError(t("Cannot extract a presentation ID from: {value}",
                           value=url_or_id))
    return url_or_id


def presentation_url(url_or_id: str) -> str:
    """Normalize a presentation reference to a URL that always opens the right place.

    Inverse of presentation_id(). If an argument that accepts either a URL or an
    ID is recorded as-is, whether it ends up as a URL or an ID depends on how it
    was passed in, and the two get mixed. Fields shown to people (e.g.
    template.json's sourceUrl) should always store an openable URL.
    """
    return f"https://docs.google.com/presentation/d/{presentation_id(url_or_id)}/edit"


_FOLDER_ID_RE = re.compile(r"/folders/([a-zA-Z0-9_-]+)")


def folder_id(url_or_id: str | None) -> str | None:
    """Extract the ID from a Google Drive folder URL. Passes through None unchanged."""
    if not url_or_id:
        return None
    m = _FOLDER_ID_RE.search(url_or_id)
    return m.group(1) if m else url_or_id
