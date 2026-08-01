#!/usr/bin/env python3
"""アイコンライブラリのカタログデッキを生成するサンプル。

`assets/shared/icons/` の 62 種を全部並べたうえで、`add_icon_row` /
`add_icon_flow` / `add_icon_grid` / `add_icon_cards` の使い方を 1 枚ずつ見せる。
SlideBuilder に `IconLibraryMixin` を混ぜる書き方の実例でもある。

使い方:
  ~/.claude/venvs/gslides/bin/python scripts/generate-icon-gallery.py

前提条件:
  - config/credentials.json 配置済み
  - cairosvg（SVG → PNG 変換。無い場合は素材のグレーのまま入る）
"""

import sys

if sys.version_info < (3, 10):
    sys.exit("Error: Python 3.10+ が必要です。現在: Python {}.{}".format(*sys.version_info[:2]))

import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, SCRIPT_DIR)

import icons  # noqa: E402
from icons import IconLibraryMixin  # noqa: E402

SCOPES = [
    "https://www.googleapis.com/auth/presentations",
    "https://www.googleapis.com/auth/drive",
]
CREDS_FILE = os.path.join(SKILL_DIR, "config", "credentials.json")
TOKEN_FILE = os.path.join(SKILL_DIR, "config", "token.json")
OUTPUT_FOLDER_ID = None

EMU = 914400
PAGE_W, PAGE_H = 10.0, 5.625


def inches(v):
    return int(v * EMU)


def hex_to_rgb(h):
    h = h.lstrip("#")
    return {"red": int(h[0:2], 16) / 255,
            "green": int(h[2:4], 16) / 255,
            "blue": int(h[4:6], 16) / 255}


class C:
    """templates/scalar/theme.json 相当の色。"""
    primary = hex_to_rgb("#2673BB")
    success = hex_to_rgb("#63C045")
    danger = hex_to_rgb("#EE2155")
    warning = hex_to_rgb("#FFB300")
    muted = hex_to_rgb("#6B7280")
    title = hex_to_rgb("#004266")
    text = hex_to_rgb("#000000")
    surface = hex_to_rgb("#F0F4F8")
    border = hex_to_rgb("#C9D6E2")
    white = hex_to_rgb("#FFFFFF")


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
        # リフレッシュトークンを含むため所有者のみ読み書き可で保存する
        fd = os.open(TOKEN_FILE, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "w") as f:
            f.write(creds.to_json())
    return creds


# ─── SlideBuilder（アイコンライブラリを混ぜた最小構成） ────────────────

class SlideBuilder(IconLibraryMixin):
    def __init__(self, drive_service):
        self.requests = []
        self.slide_ids = []
        self._counter = 0
        self.drive_service = drive_service
        self._uploaded_assets = []
        self.icon_color = C.primary        # アイコンの既定色
        self.icon_label_color = C.muted    # キャプションの既定色

    def _id(self, prefix="obj"):
        self._counter += 1
        return f"{prefix}_{self._counter:04d}"

    def _elem(self, slide_id, x, y, w, h):
        return {
            "pageObjectId": slide_id,
            "size": {"width": {"magnitude": inches(w), "unit": "EMU"},
                     "height": {"magnitude": inches(h), "unit": "EMU"}},
            "transform": {"scaleX": 1, "scaleY": 1, "translateX": inches(x),
                          "translateY": inches(y), "unit": "EMU"},
        }

    def add_slide(self):
        sid = self._id("slide")
        self.requests.append({"createSlide": {
            "objectId": sid,
            "slideLayoutReference": {"predefinedLayout": "BLANK"}}})
        self.slide_ids.append(sid)
        return sid

    def add_shape(self, slide_id, shape_type, x, y, w, h, fill=None,
                  border_color=None, border_weight=1.0):
        oid = self._id("shp")
        self.requests.append({"createShape": {
            "objectId": oid, "shapeType": shape_type,
            "elementProperties": self._elem(slide_id, x, y, w, h)}})
        if fill:
            self.requests.append({"updateShapeProperties": {
                "objectId": oid,
                "shapeProperties": {"shapeBackgroundFill": {
                    "solidFill": {"color": {"rgbColor": fill}}}},
                "fields": "shapeBackgroundFill.solidFill.color"}})
        if border_color:
            self.requests.append({"updateShapeProperties": {
                "objectId": oid,
                "shapeProperties": {"outline": {
                    "outlineFill": {"solidFill": {"color": {"rgbColor": border_color}}},
                    "weight": {"magnitude": border_weight, "unit": "PT"}}},
                "fields": "outline"}})
        else:
            self.requests.append({"updateShapeProperties": {
                "objectId": oid,
                "shapeProperties": {"outline": {"propertyState": "NOT_RENDERED"}},
                "fields": "outline"}})
        return oid

    def add_rect(self, slide_id, x, y, w, h, fill=None, border_color=None,
                 border_weight=1.0):
        return self.add_shape(slide_id, "RECTANGLE", x, y, w, h, fill=fill,
                              border_color=border_color, border_weight=border_weight)

    def add_rounded_rect(self, slide_id, x, y, w, h, fill=None, border_color=None):
        return self.add_shape(slide_id, "ROUND_RECTANGLE", x, y, w, h, fill=fill,
                              border_color=border_color)

    def add_arrow(self, slide_id, x, y, w, h, direction="right", fill=None):
        kinds = {"right": "RIGHT_ARROW", "left": "LEFT_ARROW",
                 "up": "UP_ARROW", "down": "DOWN_ARROW"}
        return self.add_shape(slide_id, kinds[direction], x, y, w, h, fill=fill)

    def add_text(self, slide_id, text, x, y, w, h, *, font_size=18, bold=False,
                 color=None, font_family="M PLUS 1p", alignment="START",
                 valign="TOP"):
        oid = self._id("txt")
        self.requests.append({"createShape": {
            "objectId": oid, "shapeType": "TEXT_BOX",
            "elementProperties": self._elem(slide_id, x, y, w, h)}})
        self.requests.append({"insertText": {
            "objectId": oid, "text": text, "insertionIndex": 0}})
        style = {"fontSize": {"magnitude": font_size, "unit": "PT"},
                 "bold": bold, "fontFamily": font_family}
        if color:
            style["foregroundColor"] = {"opaqueColor": {"rgbColor": color}}
        self.requests.append({"updateTextStyle": {
            "objectId": oid, "style": style,
            "textRange": {"type": "ALL"}, "fields": ",".join(style)}})
        self.requests.append({"updateParagraphStyle": {
            "objectId": oid, "style": {"alignment": alignment},
            "textRange": {"type": "ALL"}, "fields": "alignment"}})
        self.requests.append({"updateShapeProperties": {
            "objectId": oid, "shapeProperties": {"contentAlignment": valign},
            "fields": "contentAlignment"}})
        return oid

    def add_image(self, slide_id, image_url, x, y, w, h):
        oid = self._id("img")
        self.requests.append({"createImage": {
            "objectId": oid, "url": image_url,
            "elementProperties": self._elem(slide_id, x, y, w, h)}})
        return oid

    # -- 本デッキ用の部品 --

    def title_slide(self, title, subtitle=None):
        sid = self.add_slide()
        self.add_text(sid, title, 0.6, 0.42, 8.8, 0.5, font_size=22, bold=True,
                      color=C.title)
        self.add_rect(sid, 0.6, 0.95, 0.9, 0.045, fill=C.primary)
        if subtitle:
            self.add_text(sid, subtitle, 0.6, 5.05, 8.8, 0.3, font_size=9,
                          color=C.muted)
        return sid

    def cleanup_uploaded_assets(self):
        for fid in self._uploaded_assets:
            try:
                self.drive_service.files().delete(fileId=fid).execute()
            except Exception:
                pass
        self._uploaded_assets.clear()


def wrap(slug, limit=13):
    """長い slug をハイフンで 2 行に折る（キャプションの枠に収めるため）。"""
    if len(slug) <= limit:
        return slug
    parts = slug.split("-")
    head = parts[0]
    for p in parts[1:]:
        if len(head) + 1 + len(p) > limit:
            break
        head += "-" + p
    return head + "-\n" + slug[len(head) + 1:]


def main():
    creds = get_credentials()
    slides = build("slides", "v1", credentials=creds)
    drive = build("drive", "v3", credentials=creds)

    pres = slides.presentations().create(
        body={"title": "アイコンライブラリ カタログ"}).execute()
    pid = pres["presentationId"]
    if OUTPUT_FOLDER_ID:
        drive.files().update(fileId=pid, addParents=OUTPUT_FOLDER_ID,
                             removeParents="root", fields="id").execute()

    sb = SlideBuilder(drive)
    table = icons.icons()
    slugs = [s for s in sorted(table) if not s.startswith("scalar-logo")]

    # 1. 表紙
    sid = sb.add_slide()
    sb.add_rect(sid, 0, 0, PAGE_W, PAGE_H, fill=C.primary)
    sb.add_text(sid, "アイコンライブラリ", 0.8, 2.1, 8.4, 0.7, font_size=32,
                bold=True, color=C.white)
    sb.add_text(sid, f"assets/shared/icons/ — Scalar ブランドのピクトグラム {len(table)} 種",
                0.8, 2.95, 8.4, 0.4, font_size=13, color=C.white)

    # 2-4. 全アイコン一覧
    per = 24
    pages = [slugs[i:i + per] for i in range(0, len(slugs), per)]
    for i, page in enumerate(pages, 1):
        sid = sb.title_slide(f"アイコン一覧 {i}/{len(pages)}（add_icon_grid）")
        sb.add_icon_grid(sid, 0.5, 1.25, 9.0, [(s, wrap(s)) for s in page],
                         cols=8, size=0.52, row_gap=0.30, label_size=7)

    # 5. 流れ
    sid = sb.title_slide("流れを見せる（add_icon_flow）")
    sb.add_icon_flow(sid, 0.5, 1.35, 9.0, [
        ("job-seeker", "求職者"), ("signup", "会員登録"), ("screening", "書類選考"),
        ("interview", "面接"), ("job-offer", "内定")], size=0.86)
    sb.add_icon_flow(sid, 0.5, 3.25, 9.0, [
        ("personal-info", "個人情報"), ("consent", "同意"), ("data-bank", "情報銀行"),
        ("data-consumer", "利活用企業"), ("data-usage", "利用状況の把握")], size=0.86)

    # 6. カード
    sid = sb.title_slide("説明を添える（add_icon_cards）")
    sb.add_icon_cards(sid, 0.5, 1.3, 9.0, 3.4, [
        ("evidence-chain", "証拠チェーン", "取引を鎖状につなぎ、後からの書き換えを検知する"),
        ("tamper-check", "改ざん検知", "記録時のままであることを検証する"),
        ("timestamp", "タイムスタンプ", "いつ記録されたかを第三者が確認できる形で残す"),
        ("public-key", "公開鍵", "署名の検証に使う。公開してよい鍵"),
        ("private-key", "秘密鍵", "署名の生成に使う。持ち主だけの鍵"),
        ("shared-key", "共通鍵", "暗号化と復号に同じ鍵を使う方式"),
    ], cols=3, fill=C.surface, border_color=C.border, title_color=C.title,
        body_color=C.muted)

    # 7. 色
    sid = sb.title_slide("色はテーマの配色から選ぶ（color / icon_color）")
    sb.add_icon_row(sid, 0.5, 1.45, 9.0, [
        ("security", "既定（icon_color）"), ("mail", "既定"), ("notice", "既定"),
        ("search", "既定")], size=0.9, label_size=10)
    sb.add_icon_row(sid, 0.5, 3.2, 9.0, [
        ("security", "成功色"), ("mail", "警告色"), ("notice", "注意色"),
        ("search", "抑えた色")], size=0.9, label_size=10,
        color=[C.success, C.danger, C.warning, C.muted])

    # 8. ロゴ
    sid = sb.title_slide("ロゴ（scalar-logo は色指定を受け付けない）")
    sb.add_icon_row(sid, 2.0, 1.7, 6.0, [
        ("scalar-logo", "scalar-logo\nブランド色で固定（color は無視）"),
        ("scalar-logo-mono", "scalar-logo-mono\n単色なので color で染まる")],
        size=1.4, label_size=10, color=C.danger)

    # 既定の空スライドを消す
    first = slides.presentations().get(presentationId=pid).execute()["slides"][0]
    sb.requests.append({"deleteObject": {"objectId": first["objectId"]}})

    for i in range(0, len(sb.requests), 500):
        chunk = sb.requests[i:i + 500]
        slides.presentations().batchUpdate(
            presentationId=pid, body={"requests": chunk}).execute()
        print(f"  batch {i // 500 + 1}: {len(chunk)} requests")

    sb.cleanup_uploaded_assets()
    print(f"Done! {len(sb.slide_ids)} slides created.")
    print(f"Open: https://docs.google.com/presentation/d/{pid}/edit")
    return 0


if __name__ == "__main__":
    sys.exit(main())
