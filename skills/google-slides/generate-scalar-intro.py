#!/usr/bin/env python3
"""Scalar, Inc. 会社紹介プレゼンテーション生成スクリプト (Google Slides API)

対象: 潜在顧客・営業先向け
テーマ: scalar (Blue #2673BB / Green #63C045)
"""

import os
import json
import mimetypes
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# ── Config ──────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CREDS_FILE = os.path.join(SCRIPT_DIR, "config", "credentials.json")
TOKEN_FILE = os.path.join(SCRIPT_DIR, "config", "token.json")
SKILL_ASSETS_DIR = os.path.join(SCRIPT_DIR, "assets")
CUSTOM_ASSETS_DIR = None
OUTPUT_FOLDER_ID = None

SCOPES = [
    "https://www.googleapis.com/auth/presentations",
    "https://www.googleapis.com/auth/drive.file",
]

# ── Theme: Scalar ───────────────────────────────────────
THEME_FILE = os.path.join(SCRIPT_DIR, "templates", "scalar", "theme.json")
with open(THEME_FILE) as f:
    THEME = json.load(f)

EMU = 914400


def inches(val):
    return int(val * EMU)


def hex_to_rgb(hex_str):
    h = hex_str.lstrip("#")
    return {
        "red": int(h[0:2], 16) / 255.0,
        "green": int(h[2:4], 16) / 255.0,
        "blue": int(h[4:6], 16) / 255.0,
    }


# ── Color Constants ─────────────────────────────────────
class C:
    primary = hex_to_rgb(THEME["colors"]["primary"])          # #2673BB
    primaryDark = hex_to_rgb(THEME["colors"]["primaryDark"])   # #004266
    accent = hex_to_rgb(THEME["colors"]["accent"])             # #0985FC
    success = hex_to_rgb(THEME["colors"]["success"])           # #63C045
    textPrimary = hex_to_rgb(THEME["colors"]["textPrimary"])   # #000000
    textTitle = hex_to_rgb(THEME["colors"]["textTitle"])       # #004266
    textOnDark = hex_to_rgb(THEME["colors"]["textOnDark"])     # #FFFFFF
    textMuted = hex_to_rgb(THEME["colors"]["textMuted"])       # #666666
    textSecondary = hex_to_rgb(THEME["colors"]["textSecondary"])  # #595959
    background = hex_to_rgb(THEME["colors"]["background"])     # #FFFFFF
    surfaceLight = hex_to_rgb(THEME["colors"]["surfaceLight"]) # #F0F4F8
    border = hex_to_rgb(THEME["colors"]["border"])             # #6B7280
    warning = hex_to_rgb(THEME["colors"]["warning"])           # #E8963A


# ── Layout Constants ────────────────────────────────────
PAGE_W = 10.0
PAGE_H = 5.625
CONTENT = THEME["layouts"]["CONTENT"]
L_TITLE_X = CONTENT["elements"]["title"]["x"]
L_TITLE_Y = CONTENT["elements"]["title"]["y"]
L_TITLE_W = CONTENT["elements"]["title"]["w"]
L_TITLE_H = CONTENT["elements"]["title"]["h"]
L_CONTENT_TOP = CONTENT["elements"]["contentTop"]["y"]
L_CONTENT_BOTTOM = CONTENT["elements"]["contentBottom"]["y"]
L_MX = 0.5  # general left margin


# ── Helpers ─────────────────────────────────────────────
def solid_fill(color):
    return {"solidFill": {"color": {"rgbColor": color}}}


def text_style(font_size=18, bold=False, color=None, font_family="Noto Sans JP"):
    style = {
        "fontSize": {"magnitude": font_size, "unit": "PT"},
        "bold": bold,
        "fontFamily": font_family,
    }
    if color:
        style["foregroundColor"] = {"opaqueColor": {"rgbColor": color}}
    return style


def create_shape_request(page_id, shape_id, x, y, w, h, shape_type="RECTANGLE"):
    return {"createShape": {
        "objectId": shape_id,
        "shapeType": shape_type,
        "elementProperties": {
            "pageObjectId": page_id,
            "size": {
                "width": {"magnitude": inches(w), "unit": "EMU"},
                "height": {"magnitude": inches(h), "unit": "EMU"},
            },
            "transform": {
                "scaleX": 1, "scaleY": 1,
                "translateX": inches(x), "translateY": inches(y),
                "unit": "EMU",
            },
        },
    }}


def create_textbox_request(page_id, box_id, x, y, w, h):
    return {"createShape": {
        "objectId": box_id,
        "shapeType": "TEXT_BOX",
        "elementProperties": {
            "pageObjectId": page_id,
            "size": {
                "width": {"magnitude": inches(w), "unit": "EMU"},
                "height": {"magnitude": inches(h), "unit": "EMU"},
            },
            "transform": {
                "scaleX": 1, "scaleY": 1,
                "translateX": inches(x), "translateY": inches(y),
                "unit": "EMU",
            },
        },
    }}


def insert_text_request(box_id, text):
    return {"insertText": {"objectId": box_id, "text": text, "insertionIndex": 0}}


def update_text_style_request(box_id, style, start=0, end=None, text=""):
    end_idx = end if end is not None else len(text)
    if end_idx == 0:
        return None
    return {"updateTextStyle": {
        "objectId": box_id,
        "style": style,
        "textRange": {"type": "FIXED_RANGE", "startIndex": start, "endIndex": end_idx},
        "fields": ",".join(style.keys()),
    }}


def update_paragraph_style_request(box_id, alignment="START", line_spacing=None,
                                    start=0, end=None, text=""):
    end_idx = end if end is not None else len(text)
    if end_idx == 0:
        return None
    ps = {"alignment": alignment}
    fields = ["alignment"]
    if line_spacing:
        ps["lineSpacing"] = line_spacing
        fields.append("lineSpacing")
    return {"updateParagraphStyle": {
        "objectId": box_id,
        "style": ps,
        "textRange": {"type": "FIXED_RANGE", "startIndex": start, "endIndex": end_idx},
        "fields": ",".join(fields),
    }}


def shape_fill_request(shape_id, color):
    return {"updateShapeProperties": {
        "objectId": shape_id,
        "shapeProperties": {"shapeBackgroundFill": solid_fill(color)},
        "fields": "shapeBackgroundFill.solidFill.color",
    }}


def shape_no_border_request(shape_id):
    return {"updateShapeProperties": {
        "objectId": shape_id,
        "shapeProperties": {"outline": {"propertyState": "NOT_RENDERED"}},
        "fields": "outline",
    }}


def shape_border_request(shape_id, color, weight=1.0):
    return {"updateShapeProperties": {
        "objectId": shape_id,
        "shapeProperties": {"outline": {
            "outlineFill": solid_fill(color),
            "weight": {"magnitude": weight, "unit": "PT"},
        }},
        "fields": "outline",
    }}


def page_bg_request(page_id, color):
    return {"updatePageProperties": {
        "objectId": page_id,
        "pageProperties": {"pageBackgroundFill": solid_fill(color)},
        "fields": "pageBackgroundFill.solidFill.color",
    }}


def shape_opacity_request(shape_id, alpha):
    return {"updateShapeProperties": {
        "objectId": shape_id,
        "shapeProperties": {
            "shapeBackgroundFill": {
                "solidFill": {
                    "alpha": alpha,
                }
            }
        },
        "fields": "shapeBackgroundFill.solidFill.alpha",
    }}


# ── Asset Management ────────────────────────────────────
def convert_svg_to_png(svg_path, png_path=None, width=512):
    import cairosvg
    if png_path is None:
        png_path = svg_path.rsplit(".", 1)[0] + ".png"
    cairosvg.svg2png(url=svg_path, write_to=png_path, output_width=width)
    return png_path


def resolve_asset(theme_name, category, filename, custom_assets_dir=None):
    candidates = []
    if custom_assets_dir:
        candidates.append(os.path.join(custom_assets_dir, theme_name, category, filename))
        candidates.append(os.path.join(custom_assets_dir, "shared", category, filename))
    candidates.append(os.path.join(SKILL_ASSETS_DIR, theme_name, category, filename))
    candidates.append(os.path.join(SKILL_ASSETS_DIR, "shared", category, filename))
    for path in candidates:
        if os.path.exists(path):
            if path.lower().endswith(".svg"):
                return convert_svg_to_png(path)
            return path
    return None


def upload_asset(drive_service, file_path, mime_type=None):
    if mime_type is None:
        mime_type, _ = mimetypes.guess_type(file_path)
    media = MediaFileUpload(file_path, mimetype=mime_type)
    file_meta = {"name": os.path.basename(file_path)}
    uploaded = drive_service.files().create(
        body=file_meta, media_body=media, fields="id"
    ).execute()
    file_id = uploaded["id"]
    drive_service.permissions().create(
        fileId=file_id,
        body={"type": "anyone", "role": "reader"},
    ).execute()
    url = f"https://drive.google.com/uc?id={file_id}&export=download"
    return file_id, url


def delete_uploaded_asset(drive_service, file_id):
    drive_service.files().delete(fileId=file_id).execute()


# ── OAuth ───────────────────────────────────────────────
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


# ── SlideBuilder ────────────────────────────────────────
class SlideBuilder:
    def __init__(self, drive_service=None):
        self.requests = []
        self.slide_ids = []
        self._counter = 0
        self.drive_service = drive_service
        self.custom_assets_dir = CUSTOM_ASSETS_DIR
        self._uploaded_assets = []

    def _id(self, prefix="obj"):
        self._counter += 1
        return f"{prefix}_{self._counter:04d}"

    def add_slide(self):
        slide_id = self._id("slide")
        self.requests.append({"createSlide": {
            "objectId": slide_id,
            "slideLayoutReference": {"predefinedLayout": "BLANK"},
        }})
        self.slide_ids.append(slide_id)
        return slide_id

    def set_bg(self, slide_id, color):
        self.requests.append(page_bg_request(slide_id, color))

    def add_rect(self, slide_id, x, y, w, h, fill=None, border_color=None, border_weight=1.0):
        shape_id = self._id("rect")
        self.requests.append(create_shape_request(slide_id, shape_id, x, y, w, h))
        if fill:
            self.requests.append(shape_fill_request(shape_id, fill))
        if border_color:
            self.requests.append(shape_border_request(shape_id, border_color, border_weight))
        else:
            self.requests.append(shape_no_border_request(shape_id))
        return shape_id

    def add_rounded_rect(self, slide_id, x, y, w, h, fill=None, border_color=None,
                          border_weight=1.0, radius=0.08):
        shape_id = self._id("rrect")
        self.requests.append(create_shape_request(
            slide_id, shape_id, x, y, w, h, shape_type="ROUND_RECTANGLE"))
        if fill:
            self.requests.append(shape_fill_request(shape_id, fill))
        if border_color:
            self.requests.append(shape_border_request(shape_id, border_color, border_weight))
        else:
            self.requests.append(shape_no_border_request(shape_id))
        return shape_id

    def add_text(self, slide_id, text, x, y, w, h, *,
                 font_size=18, bold=False, color=None,
                 font_family="Noto Sans JP", alignment="START",
                 valign="TOP", line_spacing=None, italic=False):
        if not text:
            return None
        box_id = self._id("txt")
        self.requests.append(create_textbox_request(slide_id, box_id, x, y, w, h))
        self.requests.append(insert_text_request(box_id, text))
        style = text_style(font_size, bold, color, font_family)
        if italic:
            style["italic"] = True
        req = update_text_style_request(box_id, style, 0, len(text), text)
        if req:
            self.requests.append(req)
        req2 = update_paragraph_style_request(
            box_id, alignment, line_spacing, 0, len(text), text)
        if req2:
            self.requests.append(req2)
        self.requests.append({"updateShapeProperties": {
            "objectId": box_id,
            "shapeProperties": {"contentAlignment": valign},
            "fields": "contentAlignment",
        }})
        return box_id

    def add_bullets(self, slide_id, items, x, y, w, h, *,
                    font_size=14, color=None, font_family="Noto Sans JP",
                    line_spacing=None):
        text = "\n".join(items)
        box_id = self._id("bul")
        self.requests.append(create_textbox_request(slide_id, box_id, x, y, w, h))
        self.requests.append(insert_text_request(box_id, text))
        style = text_style(font_size, False, color, font_family)
        req = update_text_style_request(box_id, style, 0, len(text), text)
        if req:
            self.requests.append(req)
        if line_spacing:
            req2 = update_paragraph_style_request(
                box_id, "START", line_spacing, 0, len(text), text)
            if req2:
                self.requests.append(req2)
        self.requests.append({"createParagraphBullets": {
            "objectId": box_id,
            "textRange": {"type": "ALL"},
            "bulletPreset": "BULLET_DISC_CIRCLE_SQUARE",
        }})
        return box_id

    def add_line(self, slide_id, x, y, w, color=None, weight=0.75):
        line_id = self._id("line")
        self.requests.append({"createLine": {
            "objectId": line_id,
            "lineCategory": "STRAIGHT",
            "elementProperties": {
                "pageObjectId": slide_id,
                "size": {
                    "width": {"magnitude": inches(w), "unit": "EMU"},
                    "height": {"magnitude": 0, "unit": "EMU"},
                },
                "transform": {
                    "scaleX": 1, "scaleY": 1,
                    "translateX": inches(x), "translateY": inches(y),
                    "unit": "EMU",
                },
            },
        }})
        props = {
            "weight": {"magnitude": weight, "unit": "PT"},
        }
        fields = ["weight"]
        if color:
            props["lineFill"] = solid_fill(color)
            fields.append("lineFill")
        self.requests.append({"updateLineProperties": {
            "objectId": line_id,
            "lineProperties": props,
            "fields": ",".join(fields),
        }})
        return line_id

    def add_image(self, slide_id, image_url, x, y, w, h):
        img_id = self._id("img")
        self.requests.append({"createImage": {
            "objectId": img_id,
            "url": image_url,
            "elementProperties": {
                "pageObjectId": slide_id,
                "size": {
                    "width": {"magnitude": inches(w), "unit": "EMU"},
                    "height": {"magnitude": inches(h), "unit": "EMU"},
                },
                "transform": {
                    "scaleX": 1, "scaleY": 1,
                    "translateX": inches(x), "translateY": inches(y),
                    "unit": "EMU",
                },
            },
        }})
        return img_id

    def add_image_from_asset(self, slide_id, theme_name, category, filename, x, y, w, h):
        path = resolve_asset(theme_name, category, filename,
                             custom_assets_dir=self.custom_assets_dir)
        if path is None:
            print(f"  [WARN] Asset not found: {category}/{filename} — skipping")
            return None
        file_id, url = upload_asset(self.drive_service, path)
        self._uploaded_assets.append(file_id)
        return self.add_image(slide_id, url, x, y, w, h)

    def cleanup_uploaded_assets(self):
        for file_id in self._uploaded_assets:
            try:
                delete_uploaded_asset(self.drive_service, file_id)
            except Exception:
                pass
        self._uploaded_assets.clear()

    # ── Composite Helpers ───────────────────────────────
    def add_footer(self, slide_id, page_num, total_pages=None):
        """CONTENT マスターのフッター（ロゴ + 著作権 + ページ番号）"""
        footer = THEME["masterFooter"]
        # ロゴ
        fl = footer["logo"]
        self.add_image_from_asset(slide_id, "scalar", "logos",
                                  "scalar-logo-horizontal-small.png",
                                  fl["x"], fl["y"], fl["w"], fl["h"])
        # 著作権
        cr = footer["copyright"]
        self.add_text(slide_id, cr["text"],
                      cr["x"], cr["y"], cr["w"], cr["h"],
                      font_size=cr["fontSize"], color=C.textMuted,
                      font_family=cr["font"], alignment="CENTER", valign="MIDDLE")
        # ページ番号
        sn = footer["slideNumber"]
        page_text = f"{page_num}" if not total_pages else f"{page_num}/{total_pages}"
        self.add_text(slide_id, page_text,
                      sn["x"], sn["y"], 0.600, sn["h"],
                      font_size=sn["fontSize"], color=C.textMuted,
                      font_family=sn["font"], alignment="END", valign="MIDDLE")

    def add_action_title(self, slide_id, title_text, subtitle_text=None):
        """CONTENT マスターのアクションタイトル"""
        self.add_text(slide_id, title_text,
                      L_TITLE_X, L_TITLE_Y, L_TITLE_W, L_TITLE_H,
                      font_size=THEME["fontSizes"]["contentTitle"],
                      bold=True, color=C.textTitle)
        if subtitle_text:
            st = CONTENT["elements"]["subtitle"]
            self.add_text(slide_id, subtitle_text,
                          st["x"], st["y"], st["w"], st["h"],
                          font_size=THEME["fontSizes"]["subtitle"],
                          color=C.textSecondary)

    def add_content_slide(self, title, page_num, total_pages=None, subtitle=None):
        """標準コンテンツスライド: タイトル + フッター"""
        sid = self.add_slide()
        self.set_bg(sid, C.background)
        self.add_action_title(sid, title, subtitle)
        self.add_footer(sid, page_num, total_pages)
        return sid


# ── Batch Execution ─────────────────────────────────────
def execute_batch(slides_service, pres_id, requests, chunk_size=500):
    for i in range(0, len(requests), chunk_size):
        chunk = requests[i:i + chunk_size]
        slides_service.presentations().batchUpdate(
            presentationId=pres_id,
            body={"requests": chunk},
        ).execute()
        print(f"  Batch {i // chunk_size + 1}: {len(chunk)} requests sent")


def move_to_folder(drive_service, file_id, folder_id):
    f = drive_service.files().get(fileId=file_id, fields="parents").execute()
    prev_parents = ",".join(f.get("parents", []))
    drive_service.files().update(
        fileId=file_id,
        addParents=folder_id,
        removeParents=prev_parents,
        fields="id, parents",
    ).execute()


# ════════════════════════════════════════════════════════
#  SLIDES CONTENT
# ════════════════════════════════════════════════════════
TOTAL_SLIDES = 10


def build_slide_01_cover(sb):
    """表紙: Scalar, Inc. 会社紹介"""
    sid = sb.add_slide()
    # 背景: primary
    sb.set_bg(sid, C.primary)
    # 装飾バンド（下部）
    sb.add_rect(sid, 0, 3.667, 10.0, 1.958, fill=C.primaryDark)
    # ロゴ（白、右上）
    sb.add_image_from_asset(sid, "scalar", "logos",
                            "scalar-logo-white-horizontal.png",
                            8.297, 0.419, 1.181, 0.342)
    # タイトル
    sb.add_text(sid, "Scalar, Inc. 会社紹介",
                0.500, 1.292, 8.906, 1.208,
                font_size=30, bold=True, color=C.textOnDark)
    # サブタイトル
    sb.add_text(sid, "信頼できるデータ基盤で、ビジネスの変革を支える",
                0.543, 2.616, 8.863, 0.464,
                font_size=14, color=C.textOnDark)
    # 日付
    sb.add_text(sid, "2026",
                5.891, 3.436, 3.587, 0.200,
                font_size=12, color=C.textOnDark,
                alignment="END")


def build_slide_02_company(sb):
    """会社概要: Scalarはデータミドルウェアで企業のDXを加速する"""
    sid = sb.add_content_slide(
        "Scalarはデータミドルウェアで企業のDXを加速する",
        page_num=2, total_pages=TOTAL_SLIDES)

    # 会社情報の箇条書き
    items = [
        "2017年12月設立 — 創業者: 深津 航 (CEO) & 山田 浩之 (CTO)",
        "ミッション: 信頼性の高いデータ基盤技術を提供し、社会のDXを推進",
        "主力製品: ScalarDB（分散トランザクション）、ScalarDL（改ざん検知台帳）",
        "グローバル展開: 東京本社、シリコンバレー拠点",
        "日本発のデータベースミドルウェア専業ベンダー",
    ]
    sb.add_bullets(sid, items, 0.5, L_CONTENT_TOP + 0.15, 9.0, 3.5,
                   font_size=14, color=C.textPrimary, line_spacing=185)


def build_slide_03_problem(sb):
    """課題提起: 企業のデータ管理はサイロ化と複雑性に直面している"""
    sid = sb.add_slide()
    sb.set_bg(sid, C.background)

    # 左パネル背景（primary）
    sb.add_rect(sid, 0, 0, 5.0, PAGE_H, fill=C.primary)

    # 左パネル: 課題
    sb.add_text(sid, "課題",
                0.5, 0.5, 4.0, 0.4,
                font_size=12, bold=True, color=C.success,
                font_family="Arial")
    sb.add_text(sid, "データサイロが\nビジネスの成長を阻む",
                0.5, 1.0, 4.0, 1.0,
                font_size=18, bold=True, color=C.textOnDark,
                line_spacing=185)
    left_items = [
        "複数DBの一貫性を手動で担保",
        "障害時のデータ不整合リスク",
        "マイクロサービス化でDB間連携が爆発的に増加",
        "既存DB変更は高リスク・高コスト",
    ]
    sb.add_bullets(sid, left_items, 0.5, 2.3, 4.0, 2.5,
                   font_size=13, color=C.textOnDark, line_spacing=185)

    # 右パネル: 解決策
    sb.add_text(sid, "Scalarのアプローチ",
                5.5, 0.5, 4.0, 0.4,
                font_size=12, bold=True, color=C.primary,
                font_family="Arial")
    sb.add_text(sid, "既存DBを変えずに\nACIDトランザクションを統一",
                5.5, 1.0, 4.0, 1.0,
                font_size=18, bold=True, color=C.textTitle,
                line_spacing=185)
    right_items = [
        "ミドルウェア層で分散トランザクションを実現",
        "既存のPostgreSQL, MySQL, DynamoDB等をそのまま利用",
        "データの改ざん検知・ビザンチン障害耐性",
        "マイクロサービスに最適な2PC/Saga対応",
    ]
    sb.add_bullets(sid, right_items, 5.5, 2.3, 4.0, 2.5,
                   font_size=13, color=C.textPrimary, line_spacing=185)

    # フッター
    sb.add_footer(sid, page_num=3, total_pages=TOTAL_SLIDES)


def build_slide_04_scalardb(sb):
    """ScalarDB: 異種DB間のACIDトランザクションを統一する"""
    sid = sb.add_content_slide(
        "ScalarDBで異種DB間のトランザクションを統一する",
        page_num=4, total_pages=TOTAL_SLIDES,
        subtitle="Universal Transaction Manager")

    # 製品ロゴ
    sb.add_image_from_asset(sid, "scalar", "product-logos",
                            "scalardb-logo-horizontal-small.png",
                            0.5, L_CONTENT_TOP + 0.05, 1.5, 0.5)

    # 特徴カード 3列
    features = [
        ("分散ACID", "PostgreSQL, MySQL, DynamoDB,\nCosmos DB等の異種DB間で\nACIDトランザクションを保証"),
        ("既存DB無変更", "アプリ側のミドルウェアとして\n動作。既存のDBスキーマ・\n運用を一切変更不要"),
        ("高可用性", "ScalarDB Clusterによる\n自動フェイルオーバーと\n水平スケーリング"),
    ]
    card_w = 2.85
    gap = 0.22
    start_x = 0.5
    card_y = L_CONTENT_TOP + 0.85

    for i, (title, desc) in enumerate(features):
        cx = start_x + i * (card_w + gap)
        sb.add_rounded_rect(sid, cx, card_y, card_w, 2.8,
                            fill=C.surfaceLight, border_color=C.border, border_weight=0.75)
        # カラーバー上部
        sb.add_rect(sid, cx, card_y, card_w, 0.05, fill=C.primary)
        # タイトル
        sb.add_text(sid, title,
                    cx + 0.15, card_y + 0.2, card_w - 0.3, 0.35,
                    font_size=14, bold=True, color=C.textTitle,
                    alignment="CENTER")
        # 説明
        sb.add_text(sid, desc,
                    cx + 0.15, card_y + 0.65, card_w - 0.3, 2.0,
                    font_size=12, color=C.textPrimary,
                    alignment="CENTER", line_spacing=185)


def build_slide_05_scalardl(sb):
    """ScalarDL: データ改ざんをリアルタイムに検知・防止する"""
    sid = sb.add_content_slide(
        "ScalarDLでデータ改ざんをリアルタイムに検知・防止",
        page_num=5, total_pages=TOTAL_SLIDES,
        subtitle="Tamper-evident Distributed Ledger")

    # 製品ロゴ
    sb.add_image_from_asset(sid, "scalar", "product-logos",
                            "scalardl-logo-horizontal-small.png",
                            0.5, L_CONTENT_TOP + 0.05, 1.5, 0.5)

    # 特徴カード 3列
    features = [
        ("改ざん検知", "暗号学的証明により\nデータの改ざんや不正変更を\nリアルタイムで検出"),
        ("ビザンチン障害耐性", "Byzantine Fault Detection\nにより、悪意ある改ざんや\nシステム障害からデータを保護"),
        ("高パフォーマンス", "ブロックチェーンと異なり\nコンセンサス不要で高速動作。\n既存DB上で実行可能"),
    ]
    card_w = 2.85
    gap = 0.22
    start_x = 0.5
    card_y = L_CONTENT_TOP + 0.85

    for i, (title, desc) in enumerate(features):
        cx = start_x + i * (card_w + gap)
        sb.add_rounded_rect(sid, cx, card_y, card_w, 2.8,
                            fill=C.surfaceLight, border_color=C.border, border_weight=0.75)
        sb.add_rect(sid, cx, card_y, card_w, 0.05, fill=C.success)
        sb.add_text(sid, title,
                    cx + 0.15, card_y + 0.2, card_w - 0.3, 0.35,
                    font_size=14, bold=True, color=C.textTitle,
                    alignment="CENTER")
        sb.add_text(sid, desc,
                    cx + 0.15, card_y + 0.65, card_w - 0.3, 2.0,
                    font_size=12, color=C.textPrimary,
                    alignment="CENTER", line_spacing=185)


def build_slide_06_architecture(sb):
    """アーキテクチャ: ミドルウェア層が既存DBを統合しデータ一貫性を実現"""
    sid = sb.add_content_slide(
        "ミドルウェア層が既存DBを統合しデータ一貫性を実現",
        page_num=6, total_pages=TOTAL_SLIDES)

    # 3層アーキテクチャ図をシェイプで描画
    body_top = L_CONTENT_TOP + 0.15

    # Layer 1: Application Layer
    layer1_y = body_top
    sb.add_rounded_rect(sid, 0.5, layer1_y, 9.0, 1.0,
                        fill=C.surfaceLight, border_color=C.border, border_weight=0.75)
    sb.add_text(sid, "Application Layer",
                0.6, layer1_y + 0.05, 2.0, 0.25,
                font_size=10, bold=True, color=C.textMuted, font_family="Arial")
    # App boxes
    apps = ["Order Service", "Payment Service", "Inventory Service"]
    app_w = 2.3
    app_gap = 0.35
    app_start_x = 0.5 + (9.0 - (app_w * 3 + app_gap * 2)) / 2
    for i, app in enumerate(apps):
        ax = app_start_x + i * (app_w + app_gap)
        sb.add_rounded_rect(sid, ax, layer1_y + 0.35, app_w, 0.50,
                            fill=C.warning)
        sb.add_text(sid, app,
                    ax, layer1_y + 0.35, app_w, 0.50,
                    font_size=11, bold=True, color=C.textOnDark,
                    alignment="CENTER", valign="MIDDLE", font_family="Arial")

    # Layer 2: Scalar Middleware
    layer2_y = body_top + 1.3
    sb.add_rounded_rect(sid, 0.5, layer2_y, 9.0, 1.0,
                        fill=hex_to_rgb("#E8F0FE"), border_color=C.primary, border_weight=1.5)
    sb.add_text(sid, "Scalar Middleware",
                0.6, layer2_y + 0.05, 2.5, 0.25,
                font_size=10, bold=True, color=C.primary, font_family="Arial")
    mw = ["ScalarDB", "ScalarDL"]
    mw_w = 3.5
    mw_gap = 0.5
    mw_start_x = 0.5 + (9.0 - (mw_w * 2 + mw_gap)) / 2
    for i, m in enumerate(mw):
        mx = mw_start_x + i * (mw_w + mw_gap)
        sb.add_rounded_rect(sid, mx, layer2_y + 0.35, mw_w, 0.50,
                            fill=C.primary)
        sb.add_text(sid, m,
                    mx, layer2_y + 0.35, mw_w, 0.50,
                    font_size=12, bold=True, color=C.textOnDark,
                    alignment="CENTER", valign="MIDDLE", font_family="Arial")

    # Layer 3: Database Layer
    layer3_y = body_top + 2.6
    sb.add_rounded_rect(sid, 0.5, layer3_y, 9.0, 1.2,
                        fill=C.surfaceLight, border_color=C.border, border_weight=0.75)
    sb.add_text(sid, "Database Layer",
                0.6, layer3_y + 0.05, 2.0, 0.25,
                font_size=10, bold=True, color=C.textMuted, font_family="Arial")
    dbs = ["PostgreSQL", "MySQL", "DynamoDB", "Cosmos DB", "Cassandra"]
    db_w = 1.5
    db_gap = 0.18
    db_start_x = 0.5 + (9.0 - (db_w * 5 + db_gap * 4)) / 2
    for i, db in enumerate(dbs):
        dx = db_start_x + i * (db_w + db_gap)
        sb.add_rounded_rect(sid, dx, layer3_y + 0.40, db_w, 0.55,
                            fill=C.textMuted)
        sb.add_text(sid, db,
                    dx, layer3_y + 0.40, db_w, 0.55,
                    font_size=10, bold=True, color=C.textOnDark,
                    alignment="CENTER", valign="MIDDLE", font_family="Arial")


def build_slide_07_usecases(sb):
    """ユースケース: 金融・製造・物流など多業界でデータ信頼性を提供する"""
    sid = sb.add_content_slide(
        "金融・製造・物流など多業界でデータ信頼性を提供する",
        page_num=7, total_pages=TOTAL_SLIDES)

    items = [
        {"icon": "1", "label": "金融・決済",
         "desc": "異種DB間の決済トランザクション\n整合性を保証"},
        {"icon": "2", "label": "製造・サプライチェーン",
         "desc": "部品調達から出荷までの\nデータ一貫性を確保"},
        {"icon": "3", "label": "物流・在庫管理",
         "desc": "リアルタイム在庫の\n正確な可視化"},
        {"icon": "4", "label": "監査・コンプライアンス",
         "desc": "改ざん検知による\nデータ証跡の保全"},
        {"icon": "5", "label": "ヘルスケア",
         "desc": "患者データの\n完全性と信頼性"},
        {"icon": "6", "label": "マイクロサービス基盤",
         "desc": "サービス間の分散\nトランザクション管理"},
    ]

    cols = 3
    rows_count = 2
    cell_w = 2.85
    cell_h = 1.7
    gap_x = 0.22
    gap_y = 0.2
    start_x = 0.5
    start_y = L_CONTENT_TOP + 0.15

    for idx, item in enumerate(items):
        row = idx // cols
        col = idx % cols
        ix = start_x + col * (cell_w + gap_x)
        iy = start_y + row * (cell_h + gap_y)

        # カード
        sb.add_rounded_rect(sid, ix, iy, cell_w, cell_h,
                            fill=C.surfaceLight, border_color=C.border, border_weight=0.75)

        # バッジ（番号）
        badge_size = 0.28
        sb.add_rounded_rect(sid, ix + 0.15, iy + 0.15, badge_size, badge_size,
                            fill=C.primary)
        sb.add_text(sid, item["icon"],
                    ix + 0.15, iy + 0.15, badge_size, badge_size,
                    font_size=12, bold=True, color=C.textOnDark,
                    alignment="CENTER", valign="MIDDLE", font_family="Arial")

        # ラベル
        sb.add_text(sid, item["label"],
                    ix + 0.55, iy + 0.15, cell_w - 0.7, 0.30,
                    font_size=13, bold=True, color=C.textTitle, valign="MIDDLE")

        # 説明
        sb.add_text(sid, item["desc"],
                    ix + 0.15, iy + 0.55, cell_w - 0.3, cell_h - 0.7,
                    font_size=11, color=C.textSecondary, line_spacing=185)


def build_slide_08_kpi(sb):
    """KPI: 主要製品の信頼性と採用実績を数字で示す"""
    sid = sb.add_slide()
    sb.set_bg(sid, C.primary)

    # タイトル
    sb.add_text(sid, "主要製品の信頼性と採用実績を数字で示す",
                0.5, 0.4, 9.0, 0.5,
                font_size=20, bold=True, color=C.textOnDark,
                alignment="CENTER")

    kpis = [
        {"value": "99.99%", "label": "可用性", "desc": "ScalarDB Clusterの\nSLA目標値"},
        {"value": "<5ms", "label": "P99レイテンシ", "desc": "分散トランザクション\n追加オーバーヘッド"},
        {"value": "3+", "label": "メジャーバージョン", "desc": "ScalarDB安定リリース\n(2019年OSS公開)"},
    ]
    n = len(kpis)
    card_w = 2.8
    total_w = card_w * n + 0.3 * (n - 1)
    start_x = (PAGE_W - total_w) / 2
    card_y = 1.5

    for i, kpi in enumerate(kpis):
        cx = start_x + i * (card_w + 0.3)

        # 数値
        val_text = kpi["value"]
        val_size = 48 if len(val_text) <= 6 else 40
        sb.add_text(sid, val_text,
                    cx, card_y, card_w, 1.5,
                    font_size=val_size, bold=True, color=C.textOnDark,
                    font_family="Century Gothic",
                    alignment="CENTER", valign="BOTTOM")

        # ラベル
        sb.add_text(sid, kpi["label"],
                    cx, card_y + 1.6, card_w, 0.4,
                    font_size=14, color=C.textOnDark,
                    alignment="CENTER")

        # 説明
        sb.add_text(sid, kpi["desc"],
                    cx, card_y + 2.1, card_w, 0.6,
                    font_size=11, color=C.textOnDark,
                    alignment="CENTER", line_spacing=170)


def build_slide_09_summary(sb):
    """サマリー: Scalarが選ばれる3つの理由"""
    sid = sb.add_slide()
    sb.set_bg(sid, C.primary)

    sb.add_text(sid, "Scalarが選ばれる3つの理由",
                0.5, 0.5, 9.0, 0.6,
                font_size=24, bold=True, color=C.textOnDark)

    points = [
        "異種DB間でACIDトランザクションを保証する唯一のミドルウェア — 既存DBの変更不要",
        "暗号学的証明によるデータ改ざん検知 — コンプライアンスと監査対応を自動化",
        "日本発グローバル展開のデータ基盤 — 金融・製造・物流での採用実績",
    ]
    y = 1.4
    for i, point in enumerate(points):
        sb.add_text(sid, f"  {point}",
                    0.7, y + i * 0.55, 8.5, 0.5,
                    font_size=14, color=C.textOnDark,
                    line_spacing=185)

    y_offset = 1.4 + len(points) * 0.55 + 0.4

    sb.add_text(sid, "ネクストステップ:",
                0.5, y_offset, 3.0, 0.3,
                font_size=12, bold=True, color=C.success)
    steps = [
        "技術概要のご説明（1時間）",
        "PoC（概念実証）の実施",
        "本番環境への導入計画の策定",
    ]
    for i, step in enumerate(steps):
        sb.add_text(sid, f"  {i+1}. {step}",
                    0.7, y_offset + 0.35 + i * 0.35, 8.3, 0.3,
                    font_size=12, color=C.textOnDark)


def build_slide_10_closing(sb):
    """お問い合わせ"""
    sid = sb.add_slide()
    sb.set_bg(sid, C.background)

    # 装飾バンド（下部）
    sb.add_rect(sid, 0, 3.667, 10.0, 1.958, fill=C.primary)

    # メッセージ
    sb.add_text(sid, "お問い合わせ・詳細のご案内",
                2.0, 0.8, 6.0, 0.5,
                font_size=16, color=C.textPrimary, alignment="CENTER")

    # ロゴ（中央）
    sb.add_image_from_asset(sid, "scalar", "logos",
                            "scalar-logo-horizontal.png",
                            3.5, 1.5, 3.0, 0.87)

    # 連絡先
    contact = "Scalar, Inc.\nhttps://scalar-labs.com\ninfo@scalar-labs.com"
    sb.add_text(sid, contact,
                2.5, 2.5, 5.0, 1.0,
                font_size=12, color=C.textSecondary,
                alignment="CENTER", line_spacing=180)


# ════════════════════════════════════════════════════════
#  MAIN
# ════════════════════════════════════════════════════════
def main():
    print("Authenticating...")
    creds = get_credentials()
    slides_service = build("slides", "v1", credentials=creds)
    drive_service = build("drive", "v3", credentials=creds)

    print("Creating presentation...")
    presentation = slides_service.presentations().create(
        body={
            "title": "Scalar, Inc. 会社紹介",
            "pageSize": {
                "width": {"magnitude": inches(PAGE_W), "unit": "EMU"},
                "height": {"magnitude": inches(PAGE_H), "unit": "EMU"},
            },
        }
    ).execute()
    pres_id = presentation["presentationId"]
    first_slide_id = presentation["slides"][0]["objectId"]

    sb = SlideBuilder(drive_service=drive_service)
    sb.requests.append({"deleteObject": {"objectId": first_slide_id}})

    print("Building slides...")
    build_slide_01_cover(sb)
    build_slide_02_company(sb)
    build_slide_03_problem(sb)
    build_slide_04_scalardb(sb)
    build_slide_05_scalardl(sb)
    build_slide_06_architecture(sb)
    build_slide_07_usecases(sb)
    build_slide_08_kpi(sb)
    build_slide_09_summary(sb)
    build_slide_10_closing(sb)

    print(f"Executing {len(sb.requests)} requests...")
    execute_batch(slides_service, pres_id, sb.requests)

    if OUTPUT_FOLDER_ID:
        print(f"Moving to folder {OUTPUT_FOLDER_ID}...")
        move_to_folder(drive_service, pres_id, OUTPUT_FOLDER_ID)

    print("Cleaning up uploaded assets...")
    sb.cleanup_uploaded_assets()

    url = f"https://docs.google.com/presentation/d/{pres_id}/edit"
    print(f"\nDone! {len(sb.slide_ids)} slides created.")
    print(f"Open: {url}")
    return url


if __name__ == "__main__":
    main()
