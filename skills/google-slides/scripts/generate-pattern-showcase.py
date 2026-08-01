#!/usr/bin/env python3
"""Google Slides スキル 全パターンショーケース生成スクリプト

基本スライドパターン 6種 + インフォグラフィクスパターン 12種 + ビジュアル要素 7種
= 全25パターンを1デッキで網羅するサンプル。

使い方:
  source .venv/bin/activate
  python scripts/generate-pattern-showcase.py

設定変数（スクリプト内で編集）:
  CUSTOM_ASSETS_DIR  カスタムアセットフォルダの絶対パス（None=スキルデフォルトのみ）
  OUTPUT_FOLDER_ID   Google Drive 出力先フォルダ ID（None=マイドライブルート）

前提条件:
  - Python 3.10+
  - config/credentials.json 配置済み
  - pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
"""

import sys
if sys.version_info < (3, 10):
    sys.exit("Error: Python 3.10+ が必要です。現在: Python {}.{}".format(*sys.version_info[:2]))

import os
import math
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# ─── 1. セットアップ ───────────────────────────────────────

SCOPES = [
    "https://www.googleapis.com/auth/presentations",
    "https://www.googleapis.com/auth/drive.file",
]

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(SCRIPT_DIR)
CREDS_FILE = os.path.join(SKILL_DIR, "config", "credentials.json")
TOKEN_FILE = os.path.join(SKILL_DIR, "config", "token.json")

CUSTOM_ASSETS_DIR = None
OUTPUT_FOLDER_ID = None


def get_credentials(creds_file, token_file):
    creds = None
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(creds_file, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_file, "w") as f:
            f.write(creds.to_json())
    return creds


# ─── 2. ヘルパー関数 ──────────────────────────────────────

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

def solid_fill(color):
    return {"solidFill": {"color": {"rgbColor": color}}}

def text_style(font_size=18, bold=False, color=None, font_family="M PLUS 1p"):
    style = {
        "fontSize": {"magnitude": font_size, "unit": "PT"},
        "bold": bold,
        "fontFamily": font_family,
    }
    if color:
        style["foregroundColor"] = {"opaqueColor": {"rgbColor": color}}
    return style

def create_shape_request(page_id, shape_id, x, y, w, h):
    return {"createShape": {
        "objectId": shape_id,
        "shapeType": "RECTANGLE",
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
    return {"updateTextStyle": {
        "objectId": box_id,
        "style": style,
        "textRange": {"type": "FIXED_RANGE", "startIndex": start, "endIndex": end_idx},
        "fields": ",".join(style.keys()),
    }}

def update_paragraph_style_request(box_id, alignment="START", start=0, end=None, text=""):
    end_idx = end if end is not None else len(text)
    return {"updateParagraphStyle": {
        "objectId": box_id,
        "style": {"alignment": alignment},
        "textRange": {"type": "FIXED_RANGE", "startIndex": start, "endIndex": end_idx},
        "fields": "alignment",
    }}

def shape_fill_request(shape_id, color):
    return {"updateShapeProperties": {
        "objectId": shape_id,
        "shapeProperties": {"shapeBackgroundFill": solid_fill(color)},
        "fields": "shapeBackgroundFill.solidFill.color",
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

def shape_no_border_request(shape_id):
    return {"updateShapeProperties": {
        "objectId": shape_id,
        "shapeProperties": {"outline": {"propertyState": "NOT_RENDERED"}},
        "fields": "outline",
    }}

def page_bg_request(page_id, color):
    return {"updatePageProperties": {
        "objectId": page_id,
        "pageProperties": {"pageBackgroundFill": solid_fill(color)},
        "fields": "pageBackgroundFill.solidFill.color",
    }}


# ─── 3. テーマ定数 ────────────────────────────────────────

class C:
    primary     = hex_to_rgb("#2673BB")
    primaryDark = hex_to_rgb("#004266")
    accent      = hex_to_rgb("#0985FC")
    success     = hex_to_rgb("#63C045")
    textPrimary = hex_to_rgb("#000000")
    textTitle   = hex_to_rgb("#004266")
    textOnDark  = hex_to_rgb("#FFFFFF")
    textMuted   = hex_to_rgb("#666666")
    textSecondary = hex_to_rgb("#595959")
    background  = hex_to_rgb("#FFFFFF")
    backgroundAlt = hex_to_rgb("#F9FAFA")
    surfaceLight = hex_to_rgb("#F0F4F8")
    border      = hex_to_rgb("#6B7280")
    calloutBg   = hex_to_rgb("#F0F4F8")
    calloutBorder = hex_to_rgb("#2673BB")
    tableHeader = hex_to_rgb("#2673BB")
    tableHeaderText = hex_to_rgb("#FFFFFF")
    cautionDark = hex_to_rgb("#6B5000")
    warning     = hex_to_rgb("#BE9000")
    error       = hex_to_rgb("#EE2155")
    chart1      = hex_to_rgb("#63C045")
    chart2      = hex_to_rgb("#EE2155")
    chart3      = hex_to_rgb("#0985FC")
    chart4      = hex_to_rgb("#FFEE24")
    chart5      = hex_to_rgb("#2673BB")

class L:
    MX = 0.323
    titleX = 0.323
    titleY = 0.303
    titleW = 9.354
    titleH = 0.437
    bodyY = 0.787
    bodyBottom = 5.208
    CW = 9.354
    footerLogoX = 0.323
    footerLogoY = 5.208
    footerLogoW = 0.952
    footerLogoH = 0.244
    copyrightX = 2.000
    copyrightY = 5.378
    copyrightW = 6.083
    copyrightH = 0.219


# ─── 4. SlideBuilder クラス ───────────────────────────────

class SlideBuilder:
    def __init__(self):
        self.requests = []
        self.slide_ids = []
        self._counter = 0
        self.drive_service = None
        self._uploaded_assets = []
        self.custom_assets_dir = None

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

    def add_text(self, slide_id, text, x, y, w, h, *,
                 font_size=18, bold=False, color=None,
                 font_family="M PLUS 1p", alignment="START", valign="TOP"):
        box_id = self._id("txt")
        self.requests.append(create_textbox_request(slide_id, box_id, x, y, w, h))
        self.requests.append(insert_text_request(box_id, text))
        style = text_style(font_size, bold, color, font_family)
        self.requests.append(update_text_style_request(box_id, style, 0, len(text), text))
        self.requests.append(update_paragraph_style_request(box_id, alignment, 0, len(text), text))
        self.requests.append({"updateShapeProperties": {
            "objectId": box_id,
            "shapeProperties": {"contentAlignment": valign},
            "fields": "contentAlignment",
        }})
        return box_id

    def add_bullets(self, slide_id, items, x, y, w, h, *, font_size=14, color=None):
        text = "\n".join(items)
        box_id = self._id("bul")
        self.requests.append(create_textbox_request(slide_id, box_id, x, y, w, h))
        self.requests.append(insert_text_request(box_id, text))
        style = text_style(font_size, False, color)
        self.requests.append(update_text_style_request(box_id, style, 0, len(text), text))
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
        self.requests.append({"updateLineProperties": {
            "objectId": line_id,
            "lineProperties": {
                "lineFill": solid_fill(color),
                "weight": {"magnitude": weight, "unit": "PT"},
            },
            "fields": "lineFill,weight",
        }})
        return line_id

    def add_shape(self, slide_id, shape_type, x, y, w, h,
                  fill=None, border_color=None, border_weight=1.0):
        shape_id = self._id("shp")
        self.requests.append({"createShape": {
            "objectId": shape_id,
            "shapeType": shape_type,
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
        if fill:
            self.requests.append(shape_fill_request(shape_id, fill))
        if border_color:
            self.requests.append(shape_border_request(shape_id, border_color, border_weight))
        else:
            self.requests.append(shape_no_border_request(shape_id))
        return shape_id

    def add_circle(self, slide_id, cx, cy, r, fill=None, border_color=None):
        return self.add_shape(slide_id, "ELLIPSE",
                              cx - r, cy - r, 2 * r, 2 * r,
                              fill=fill, border_color=border_color)

    def add_rounded_rect(self, slide_id, x, y, w, h, fill=None, border_color=None):
        return self.add_shape(slide_id, "ROUND_RECTANGLE", x, y, w, h,
                              fill=fill, border_color=border_color)

    def add_badge(self, slide_id, cx, cy, r, text, fill, text_color):
        self.add_circle(slide_id, cx, cy, r, fill=fill)
        self.add_text(slide_id, text,
                      cx - r, cy - r, 2 * r, 2 * r,
                      font_size=max(int(r * 28), 10), bold=True,
                      color=text_color, alignment="CENTER", valign="MIDDLE")

    def add_connector(self, slide_id, x1, y1, x2, y2,
                      color=None, weight=1.0,
                      start_arrow=None, end_arrow=None,
                      dash_style="SOLID"):
        line_id = self._id("conn")
        lx, ly = min(x1, x2), min(y1, y2)
        lw, lh = abs(x2 - x1), abs(y2 - y1)
        sx = 1 if x2 >= x1 else -1
        sy = 1 if y2 >= y1 else -1
        self.requests.append({"createLine": {
            "objectId": line_id,
            "lineCategory": "STRAIGHT",
            "elementProperties": {
                "pageObjectId": slide_id,
                "size": {
                    "width": {"magnitude": inches(lw) if lw > 0 else 1, "unit": "EMU"},
                    "height": {"magnitude": inches(lh) if lh > 0 else 1, "unit": "EMU"},
                },
                "transform": {
                    "scaleX": sx, "scaleY": sy,
                    "translateX": inches(x1 if sx > 0 else x2),
                    "translateY": inches(y1 if sy > 0 else y2),
                    "unit": "EMU",
                },
            },
        }})
        line_props = {
            "weight": {"magnitude": weight, "unit": "PT"},
            "dashStyle": dash_style,
        }
        fields = ["weight", "dashStyle"]
        if color:
            line_props["lineFill"] = solid_fill(color)
            fields.append("lineFill")
        if start_arrow:
            line_props["startArrow"] = start_arrow
            fields.append("startArrow")
        if end_arrow:
            line_props["endArrow"] = end_arrow
            fields.append("endArrow")
        self.requests.append({"updateLineProperties": {
            "objectId": line_id,
            "lineProperties": line_props,
            "fields": ",".join(fields),
        }})
        return line_id

    def add_connected_connector(self, slide_id,
                                start_shape_id, start_site,
                                end_shape_id, end_site,
                                color=None, weight=1.0,
                                end_arrow="FILL_ARROW",
                                dash_style="SOLID"):
        line_id = self._id("cconn")
        self.requests.append({"createLine": {
            "objectId": line_id,
            "lineCategory": "STRAIGHT",
            "elementProperties": {
                "pageObjectId": slide_id,
                "size": {
                    "width": {"magnitude": inches(0.1), "unit": "EMU"},
                    "height": {"magnitude": inches(0.1), "unit": "EMU"},
                },
                "transform": {
                    "scaleX": 1, "scaleY": 1,
                    "translateX": 0, "translateY": 0,
                    "unit": "EMU",
                },
            },
        }})
        line_props = {
            "startConnection": {
                "connectedObjectId": start_shape_id,
                "connectionSiteIndex": start_site,
            },
            "endConnection": {
                "connectedObjectId": end_shape_id,
                "connectionSiteIndex": end_site,
            },
            "weight": {"magnitude": weight, "unit": "PT"},
            "dashStyle": dash_style,
        }
        fields = ["startConnection", "endConnection", "weight", "dashStyle"]
        if color:
            line_props["lineFill"] = solid_fill(color)
            fields.append("lineFill")
        if end_arrow:
            line_props["endArrow"] = end_arrow
            fields.append("endArrow")
        self.requests.append({"updateLineProperties": {
            "objectId": line_id,
            "lineProperties": line_props,
            "fields": ",".join(fields),
        }})
        return line_id

    def add_table(self, slide_id, rows, cols, x, y, w, h,
                  data=None, header_fill=None):
        table_id = self._id("tbl")
        self.requests.append({"createTable": {
            "objectId": table_id,
            "rows": rows,
            "columns": cols,
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
        if data:
            for r, row_data in enumerate(data):
                for c, cell_text in enumerate(row_data):
                    self.requests.append({"insertText": {
                        "objectId": table_id,
                        "cellLocation": {"rowIndex": r, "columnIndex": c},
                        "text": str(cell_text),
                        "insertionIndex": 0,
                    }})
        if header_fill:
            for c in range(cols):
                self.requests.append({"updateTableCellProperties": {
                    "objectId": table_id,
                    "tableRange": {
                        "location": {"rowIndex": 0, "columnIndex": c},
                        "rowSpan": 1, "columnSpan": 1,
                    },
                    "tableCellProperties": {
                        "tableCellBackgroundFill": solid_fill(header_fill),
                    },
                    "fields": "tableCellBackgroundFill",
                }})
        return table_id

    def shape_opacity(self, shape_id, alpha):
        self.requests.append({"updateShapeProperties": {
            "objectId": shape_id,
            "shapeProperties": {
                "shapeBackgroundFill": {
                    "solidFill": {"alpha": alpha},
                },
            },
            "fields": "shapeBackgroundFill.solidFill.alpha",
        }})

    def shape_shadow(self, shape_id, blur_radius=3.0, offset_x=2.0, offset_y=2.0,
                     color=None, alpha=0.3):
        shadow_color = color or {"red": 0, "green": 0, "blue": 0}
        self.requests.append({"updateShapeProperties": {
            "objectId": shape_id,
            "shapeProperties": {
                "shadow": {
                    "type": "OUTER",
                    "transform": {
                        "scaleX": 1, "scaleY": 1,
                        "translateX": offset_x * 12700,
                        "translateY": offset_y * 12700,
                        "unit": "EMU",
                    },
                    "alignment": "BOTTOM_LEFT",
                    "blurRadius": {"magnitude": blur_radius, "unit": "PT"},
                    "color": {"rgbColor": shadow_color},
                    "alpha": alpha,
                    "rotateWithShape": True,
                    "propertyState": "RENDERED",
                },
            },
            "fields": "shadow",
        }})

    def shape_rotation(self, shape_id, angle_deg, x=None, y=None, w=None, h=None):
        rad = math.radians(angle_deg)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)
        if x is not None and y is not None and w is not None and h is not None:
            x_emu = inches(x)
            y_emu = inches(y)
            w_emu = inches(w)
            h_emu = inches(h)
            tx = x_emu + w_emu / 2 * (1 - cos_a) + h_emu / 2 * sin_a
            ty = y_emu + h_emu / 2 * (1 - cos_a) - w_emu / 2 * sin_a
            self.requests.append({"updatePageElementTransform": {
                "objectId": shape_id,
                "applyMode": "ABSOLUTE",
                "transform": {
                    "scaleX": cos_a, "scaleY": cos_a,
                    "shearX": -sin_a, "shearY": sin_a,
                    "translateX": tx, "translateY": ty,
                    "unit": "EMU",
                },
            }})
        else:
            self.requests.append({"updatePageElementTransform": {
                "objectId": shape_id,
                "applyMode": "RELATIVE",
                "transform": {
                    "scaleX": cos_a, "scaleY": cos_a,
                    "shearX": -sin_a, "shearY": sin_a,
                    "translateX": 0, "translateY": 0,
                    "unit": "EMU",
                },
            }})

    def group_objects(self, object_ids):
        group_id = self._id("grp")
        self.requests.append({"groupObjects": {
            "groupObjectId": group_id,
            "childrenObjectIds": object_ids,
        }})
        return group_id

    def set_z_order(self, shape_id, operation):
        self.requests.append({"updatePageElementsZOrder": {
            "pageElementObjectIds": [shape_id],
            "operation": operation,
        }})

    # ─── コンポジットメソッド ─────────────────────────────

    def add_footer(self, slide_id, source=None):
        self.add_text(slide_id, "Scalar",
                      L.footerLogoX, L.footerLogoY, L.footerLogoW, L.footerLogoH,
                      font_size=9, bold=True, color=C.primary,
                      font_family="Noto Sans JP", valign="MIDDLE")
        self.add_text(slide_id, "(C) 2026 Scalar, Inc.",
                      L.copyrightX, L.copyrightY, L.copyrightW, L.copyrightH,
                      font_size=7, color=C.textMuted,
                      font_family="Arial", alignment="CENTER", valign="MIDDLE")
        if source:
            self.add_text(slide_id, source,
                          L.MX, L.bodyBottom - 0.25, L.CW, 0.20,
                          font_size=10, color=C.textMuted)

    def add_content_slide(self, action_title, source=None):
        sid = self.add_slide()
        self.set_bg(sid, C.background)
        self.add_text(sid, action_title,
                      L.titleX, L.titleY, L.titleW, L.titleH,
                      font_size=20, bold=True, color=C.textTitle,
                      font_family="Noto Sans JP")
        self.add_footer(sid, source)
        return sid

    def add_section_divider(self, title, subtitle=None):
        sid = self.add_slide()
        self.set_bg(sid, C.background)
        self.add_text(sid, "Scalar", 0.118, 0.179, 1.181, 0.342,
                      font_size=12, bold=True, color=C.primary,
                      font_family="Noto Sans JP", valign="MIDDLE")
        self.add_text(sid, title, 1.438, 2.039, 7.125, 0.590,
                      font_size=24, bold=True, color=C.textTitle,
                      font_family="Noto Sans JP", alignment="CENTER", valign="MIDDLE")
        self.add_line(sid, 1.438, 2.686, 8.562, color=C.primary, weight=2.25)
        if subtitle:
            self.add_text(sid, subtitle, 1.438, 2.759, 7.125, 1.088,
                          font_size=14, color=C.textSecondary, alignment="CENTER")
        self.add_rect(sid, 0, 3.667, 10.0, 1.958, fill=C.primary)
        return sid

    def add_callout(self, slide_id, text, x=6.5, y=1.2, w=3.0, h=0.8):
        self.add_rect(slide_id, x, y, w, h, fill=C.calloutBg)
        self.add_rect(slide_id, x, y, 0.06, h, fill=C.calloutBorder)
        self.add_text(slide_id, text,
                      x + 0.15, y, w - 0.2, h,
                      font_size=12, color=C.textPrimary, valign="MIDDLE")

    def add_feature_slide(self, title, description, bullets, *,
                          source=None, callout=None):
        sid = self.add_content_slide(title, source)
        if callout:
            bul_w = 5.8
            self.add_text(sid, description,
                          L.MX, L.bodyY + 0.05, L.CW, 0.50,
                          font_size=13, color=C.textSecondary)
            self.add_bullets(sid, bullets,
                             L.MX + 0.1, L.bodyY + 0.60, bul_w, 3.5,
                             font_size=13)
            cx = L.MX + bul_w + 0.3
            cw = L.CW - bul_w - 0.3
            self.add_callout(sid, callout,
                             x=cx, y=L.bodyY + 0.70, w=cw, h=1.2)
        else:
            self.add_text(sid, description,
                          L.MX, L.bodyY + 0.05, L.CW, 0.50,
                          font_size=13, color=C.textSecondary)
            self.add_bullets(sid, bullets,
                             L.MX + 0.1, L.bodyY + 0.60, L.CW - 0.1, 3.5,
                             font_size=13)
        return sid

    def add_card_slide(self, title, cards, *, source=None, card_h=3.0):
        sid = self.add_content_slide(title, source)
        n = len(cards)
        card_w = (L.CW - 0.3 * (n - 1)) / n
        for i, (ct, cb) in enumerate(cards):
            x = L.MX + i * (card_w + 0.3)
            y = L.bodyY + 0.10
            self.add_rect(sid, x, y, card_w, card_h,
                          fill=C.background, border_color=C.border)
            self.add_rect(sid, x, y, card_w, 0.05, fill=C.primary)
            self.add_text(sid, ct,
                          x + 0.15, y + 0.20, card_w - 0.3, 0.35,
                          font_size=14, bold=True, color=C.primary)
            self.add_text(sid, cb,
                          x + 0.15, y + 0.65, card_w - 0.3, card_h - 0.8,
                          font_size=12, color=C.textPrimary)
        return sid

    # ─── インフォグラフィクスパターン ─────────────────────

    def add_progress_bar(self, slide_id, x, y, w, h, percent,
                         fill, bg, label=None, label_color=None):
        self.add_rounded_rect(slide_id, x, y, w, h, fill=bg)
        bar_w = max(w * (percent / 100.0), h)
        self.add_rounded_rect(slide_id, x, y, bar_w, h, fill=fill)
        if label:
            self.add_text(slide_id, label,
                          x + w + 0.1, y, 0.6, h,
                          font_size=max(int(h * 40), 10), bold=True,
                          color=label_color or fill,
                          alignment="START", valign="MIDDLE")

    def add_timeline_h(self, slide_id, x, y, w, events, line_color=None, marker_color=None):
        lc = line_color or C.border
        mc = marker_color or C.primary
        n = len(events)
        self.add_line(slide_id, x, y, w, color=lc, weight=2.0)
        for i, evt in enumerate(events):
            ex = x + (w / (n - 1)) * i if n > 1 else x + w / 2
            self.add_circle(slide_id, ex, y, 0.12, fill=mc)
            if i % 2 == 0:
                ty = y - 0.55
            else:
                ty = y + 0.20
            self.add_text(slide_id, evt["label"],
                          ex - 0.6, ty, 1.2, 0.30,
                          font_size=12, bold=True, color=C.textTitle,
                          alignment="CENTER", valign="MIDDLE")
            if evt.get("sublabel"):
                offset = -0.25 if i % 2 == 0 else 0.25
                self.add_text(slide_id, evt["sublabel"],
                              ex - 0.8, ty + offset, 1.6, 0.25,
                              font_size=10, color=C.textSecondary,
                              alignment="CENTER", valign="MIDDLE")

    def add_timeline_v(self, slide_id, x, y, h, events,
                       line_color=None, marker_color=None):
        lc = line_color or C.border
        mc = marker_color or C.primary
        n = len(events)
        spacing = h / (n - 1) if n > 1 else 0
        self.add_connector(slide_id, x, y, x, y + h, color=lc, weight=2.0)
        for i, evt in enumerate(events):
            ey = y + spacing * i
            self.add_circle(slide_id, x, ey, 0.10, fill=mc)
            self.add_text(slide_id, evt["label"],
                          x + 0.25, ey - 0.12, 3.0, 0.25,
                          font_size=12, bold=True, color=C.textTitle)
            if evt.get("sublabel"):
                self.add_text(slide_id, evt["sublabel"],
                              x + 0.25, ey + 0.12, 3.0, 0.20,
                              font_size=10, color=C.textSecondary)

    def add_bar_chart(self, slide_id, x, y, w, h, data,
                      bar_color=None, label_color=None, orientation="vertical"):
        bc = bar_color or C.primary
        lc = label_color or C.textPrimary
        n = len(data)
        max_val = max(d["value"] for d in data) or 1
        if orientation == "vertical":
            bar_w = (w * 0.7) / n
            gap = (w * 0.3) / (n + 1)
            for i, d in enumerate(data):
                bx = x + gap + i * (bar_w + gap)
                bar_h = (d["value"] / max_val) * (h * 0.8)
                by = y + h * 0.8 - bar_h
                self.add_rounded_rect(slide_id, bx, by, bar_w, bar_h, fill=bc)
                self.add_text(slide_id, str(d["value"]),
                              bx, by - 0.22, bar_w, 0.20,
                              font_size=10, bold=True, color=bc,
                              alignment="CENTER")
                self.add_text(slide_id, d["label"],
                              bx, y + h * 0.82, bar_w, 0.20,
                              font_size=10, color=lc,
                              alignment="CENTER")

    def add_donut(self, slide_id, cx, cy, r, segments,
                  center_label=None, center_color=None):
        bg = C.background
        sorted_segs = sorted(segments, key=lambda s: s["value"], reverse=True)
        total = sum(s["value"] for s in sorted_segs)
        inner_ratio = 0.50
        ring_space = r * (1 - inner_ratio)
        current_r = r
        for seg in sorted_segs:
            self.add_circle(slide_id, cx, cy, current_r, fill=seg["color"])
            ring_width = ring_space * (seg["value"] / total) if total else 0
            current_r -= ring_width
        inner_r = r * inner_ratio
        self.add_circle(slide_id, cx, cy, inner_r, fill=bg)
        if center_label:
            self.add_text(slide_id, center_label,
                          cx - inner_r, cy - inner_r * 0.4,
                          inner_r * 2, inner_r * 0.8,
                          font_size=max(int(r * 16), 10), bold=True,
                          color=center_color or C.textTitle,
                          alignment="CENTER", valign="MIDDLE")
        legend_x = cx + r + 0.3
        for i, seg in enumerate(segments):
            ly = cy - r + i * 0.35
            self.add_rect(slide_id, legend_x, ly + 0.04, 0.18, 0.18,
                          fill=seg["color"])
            pct = int(seg["value"] / total * 100) if total else 0
            self.add_text(slide_id, f'{seg["label"]} ({pct}%)',
                          legend_x + 0.25, ly, 1.5, 0.25,
                          font_size=10, color=C.textPrimary)

    def add_pyramid(self, slide_id, x, y, w, h, levels, colors=None):
        n = len(levels)
        level_h = h / n
        if not colors:
            base = C.primary
            colors = []
            for i in range(n):
                t = i / max(n - 1, 1)
                factor = 0.4 + 0.6 * t
                colors.append({
                    "red": base["red"] * factor,
                    "green": base["green"] * factor,
                    "blue": base["blue"] * factor,
                })
        for i, label in enumerate(levels):
            ratio_top = (i + 0.3) / (n + 0.3)
            ratio_bottom = (i + 1.3) / (n + 0.3)
            lw = w * (ratio_top + ratio_bottom) / 2
            lx = x + (w - lw) / 2
            ly = y + i * level_h
            fill = colors[i]
            self.add_shape(slide_id, "TRAPEZOID", lx, ly, lw, level_h * 0.92,
                           fill=fill)
            self.add_text(slide_id, label,
                          lx, ly, lw, level_h * 0.92,
                          font_size=12, bold=True,
                          color=C.textOnDark,
                          alignment="CENTER", valign="MIDDLE")

    def add_icon_text_row(self, slide_id, x, y, items, icon_r=0.2):
        n = len(items)
        item_w = (10.0 - 2 * x) / n if n > 0 else 3.0
        for i, item in enumerate(items):
            ix = x + i * item_w
            ic = item.get("color", C.primary)
            self.add_badge(slide_id, ix + icon_r, y + icon_r,
                           icon_r, item["icon"], fill=ic,
                           text_color=C.textOnDark)
            self.add_text(slide_id, item["title"],
                          ix + icon_r * 2 + 0.15, y, item_w - icon_r * 2 - 0.2, 0.30,
                          font_size=12, bold=True, color=C.textTitle, valign="MIDDLE")
            self.add_text(slide_id, item["desc"],
                          ix, y + icon_r * 2 + 0.15, item_w - 0.1, 0.60,
                          font_size=10, color=C.textSecondary)

    def add_stat_card(self, slide_id, x, y, w, h, value, label,
                      icon_color=None, bg=None, border=None):
        ic = icon_color or C.primary
        card_bg = bg or C.background
        self.add_rounded_rect(slide_id, x, y, w, h,
                              fill=card_bg,
                              border_color=border or C.border)
        self.add_rect(slide_id, x, y, w, 0.025, fill=ic)
        self.add_text(slide_id, value,
                      x + 0.1, y + h * 0.25, w - 0.2, h * 0.40,
                      font_size=28, bold=True, color=C.textTitle,
                      alignment="CENTER", valign="MIDDLE")
        self.add_text(slide_id, label,
                      x + 0.1, y + h * 0.65, w - 0.2, h * 0.25,
                      font_size=10, color=C.textSecondary,
                      alignment="CENTER", valign="TOP")

    def add_comparison(self, slide_id, x, y, w, h, left, right):
        gap = 0.3
        col_w = (w - gap) / 2
        for i, side in enumerate([left, right]):
            cx = x + i * (col_w + gap)
            self.add_rounded_rect(slide_id, cx, y, col_w, h,
                                  fill=C.background, border_color=side["color"])
            self.add_rect(slide_id, cx, y, col_w, 0.05, fill=side["color"])
            self.add_text(slide_id, side["title"],
                          cx + 0.15, y + 0.15, col_w - 0.3, 0.35,
                          font_size=15, bold=True, color=side["color"],
                          alignment="CENTER")
            if side.get("items"):
                self.add_bullets(slide_id, side["items"],
                                 cx + 0.2, y + 0.60, col_w - 0.4, h - 0.75,
                                 font_size=12, color=C.textPrimary)

    def add_flow_diagram(self, slide_id, x, y, steps,
                         box_w=1.8, box_h=0.6, gap=0.5,
                         orientation="horizontal"):
        shape_map = {
            "rect": "RECTANGLE",
            "rounded": "ROUND_RECTANGLE",
            "diamond": "DIAMOND",
        }
        positions = []
        for i, step in enumerate(steps):
            if orientation == "horizontal":
                sx = x + i * (box_w + gap)
                sy = y
            else:
                sx = x
                sy = y + i * (box_h + gap)
            shape_type = shape_map.get(step.get("shape", "rounded"), "ROUND_RECTANGLE")
            fill = step.get("color", C.primary)
            self.add_shape(slide_id, shape_type, sx, sy, box_w, box_h, fill=fill)
            self.add_text(slide_id, step["label"],
                          sx, sy, box_w, box_h,
                          font_size=12, bold=True,
                          color=C.textOnDark,
                          alignment="CENTER", valign="MIDDLE")
            positions.append((sx, sy))
        for i in range(len(positions) - 1):
            sx1, sy1 = positions[i]
            sx2, sy2 = positions[i + 1]
            if orientation == "horizontal":
                self.add_connector(slide_id,
                                   sx1 + box_w, sy1 + box_h / 2,
                                   sx2, sy2 + box_h / 2,
                                   color=C.textMuted, weight=1.5,
                                   end_arrow="FILL_ARROW")
            else:
                self.add_connector(slide_id,
                                   sx1 + box_w / 2, sy1 + box_h,
                                   sx2 + box_w / 2, sy2,
                                   color=C.textMuted, weight=1.5,
                                   end_arrow="FILL_ARROW")

    def add_decision_flow(self, slide_id, nodes, edges,
                          box_w=1.6, box_h=0.5, diamond_size=0.45):
        CONN_TOP, CONN_LEFT, CONN_BOTTOM, CONN_RIGHT = 0, 1, 2, 3
        shape_map = {
            "process": "ROUND_RECTANGLE",
            "decision": "DIAMOND",
            "start": "FLOW_CHART_TERMINATOR",
            "end": "FLOW_CHART_TERMINATOR",
        }
        shape_ids = {}
        centers = {}
        for node in nodes:
            ntype = node.get("type", "process")
            shape = shape_map.get(ntype, "ROUND_RECTANGLE")
            fill = node.get("color", C.primary)
            if ntype == "decision":
                nw, nh = diamond_size * 2, diamond_size * 2
            else:
                nw, nh = box_w, box_h
            nx, ny = node["x"], node["y"]
            sid = self.add_shape(slide_id, shape, nx, ny, nw, nh, fill=fill)
            shape_ids[node["id"]] = sid
            fs = 10 if ntype == "decision" else 12
            self.add_text(slide_id, node["label"],
                          nx, ny, nw, nh,
                          font_size=fs, bold=True,
                          color=C.textOnDark,
                          alignment="CENTER", valign="MIDDLE")
            centers[node["id"]] = (nx + nw / 2, ny + nh / 2)
        for edge in edges:
            fc = centers[edge["from"]]
            tc = centers[edge["to"]]
            dx = tc[0] - fc[0]
            dy = tc[1] - fc[1]
            if abs(dx) > abs(dy):
                if dx > 0:
                    start_site, end_site = CONN_RIGHT, CONN_LEFT
                else:
                    start_site, end_site = CONN_LEFT, CONN_RIGHT
            else:
                if dy > 0:
                    start_site, end_site = CONN_BOTTOM, CONN_TOP
                else:
                    start_site, end_site = CONN_TOP, CONN_BOTTOM
            self.add_connected_connector(
                slide_id,
                shape_ids[edge["from"]], start_site,
                shape_ids[edge["to"]], end_site,
                color=C.textMuted, weight=1.5,
                end_arrow="FILL_ARROW")
            if edge.get("label"):
                mx = (fc[0] + tc[0]) / 2
                my = (fc[1] + tc[1]) / 2
                lw = 0.7
                offset_y = -0.2 if abs(dx) > abs(dy) else 0
                offset_x = 0.15 if abs(dy) >= abs(dx) else 0
                self.add_text(slide_id, edge["label"],
                              mx - lw / 2 + offset_x, my - 0.12 + offset_y,
                              lw, 0.25,
                              font_size=9, bold=True, color=C.textSecondary,
                              alignment="CENTER", valign="MIDDLE")

    def add_venn(self, slide_id, cx, cy, r, sets,
                 overlap_label=None, opacity=0.4):
        n = len(sets)
        positions = []
        if n == 2:
            offset = r * 0.6
            positions = [(cx - offset, cy), (cx + offset, cy)]
        elif n == 3:
            offset = r * 0.55
            for i in range(3):
                angle = math.radians(90 + 120 * i)
                px = cx + offset * math.cos(angle)
                py = cy - offset * math.sin(angle)
                positions.append((px, py))
        for i, s in enumerate(sets):
            px, py = positions[i]
            circle_id = self.add_circle(slide_id, px, py, r, fill=s["color"])
            self.shape_opacity(circle_id, opacity)
        for i, s in enumerate(sets):
            px, py = positions[i]
            dx = px - cx
            dy = py - cy
            dist = math.sqrt(dx * dx + dy * dy) if (dx or dy) else 1
            label_offset = r * 0.75
            lx = px + (dx / dist) * label_offset if dist > 0.01 else px
            ly = py + (dy / dist) * label_offset if dist > 0.01 else py - r
            self.add_text(slide_id, s["label"],
                          lx - 0.8, ly - 0.15, 1.6, 0.30,
                          font_size=12, bold=True, color=s["color"],
                          alignment="CENTER", valign="MIDDLE")
        if overlap_label:
            self.add_text(slide_id, overlap_label,
                          cx - 0.8, cy - 0.15, 1.6, 0.30,
                          font_size=11, bold=True, color=C.textTitle,
                          alignment="CENTER", valign="MIDDLE")


# ─── 5. バッチ実行 ────────────────────────────────────────

def execute_batch(slides_service, pres_id, requests, chunk_size=500):
    for i in range(0, len(requests), chunk_size):
        chunk = requests[i:i + chunk_size]
        slides_service.presentations().batchUpdate(
            presentationId=pres_id,
            body={"requests": chunk},
        ).execute()
        print(f"  Batch {i // chunk_size + 1}: {len(chunk)} requests sent")


# ─── 6. main() ────────────────────────────────────────────

def main():
    creds = get_credentials(CREDS_FILE, TOKEN_FILE)
    slides_service = build("slides", "v1", credentials=creds)
    drive_service = build("drive", "v3", credentials=creds)

    presentation = slides_service.presentations().create(
        body={
            "title": "Google Slides スキル 全パターンショーケース",
            "pageSize": {
                "width": {"magnitude": inches(10.0), "unit": "EMU"},
                "height": {"magnitude": inches(5.625), "unit": "EMU"},
            },
        }
    ).execute()
    pres_id = presentation["presentationId"]

    first_slide_id = presentation["slides"][0]["objectId"]
    sb = SlideBuilder()
    sb.drive_service = drive_service
    sb.custom_assets_dir = CUSTOM_ASSETS_DIR
    sb.requests.append({"deleteObject": {"objectId": first_slide_id}})

    # ====================================================================
    # Slide 1: Cover（表紙）
    # ====================================================================
    sid = sb.add_slide()
    sb.set_bg(sid, C.background)
    sb.add_rect(sid, 0, 3.667, 10.0, 1.958, fill=C.primary)
    sb.add_text(sid, "Scalar", 8.297, 0.419, 1.181, 0.342,
                font_size=12, bold=True, color=C.primary,
                font_family="Noto Sans JP", valign="MIDDLE", alignment="END")
    sb.add_text(sid, "Google Slides スキル\n全パターンショーケース",
                0.500, 1.292, 8.906, 1.208,
                font_size=30, bold=True, color=C.textTitle,
                font_family="Noto Sans JP")
    sb.add_text(sid, "基本スライド 6種 + インフォグラフィクス 12種 + ビジュアル要素 7種",
                0.543, 2.616, 8.863, 0.464,
                font_size=14, color=C.textSecondary,
                font_family="M PLUS 1p")
    sb.add_text(sid, "(C) 2026 Scalar, Inc.",
                5.891, 3.8, 3.587, 0.3,
                font_size=10, color=C.textOnDark,
                font_family="Arial", alignment="END")

    # ====================================================================
    # Slide 2: Section Divider — 基本スライドパターン
    # ====================================================================
    sb.add_section_divider("基本スライドパターン",
                           "Content / Feature / Card / Table")

    # ====================================================================
    # Slide 3: Content Slide（アクションタイトル＋フッター）
    # ====================================================================
    sid = sb.add_content_slide("ScalarDB は異種 DB 間の ACID トランザクションを統合するミドルウェアである")
    sb.add_text(sid, "Content Slide パターン",
                L.MX, L.bodyY + 0.05, L.CW, 0.40,
                font_size=14, bold=True, color=C.primary)
    sb.add_text(sid, "アクションタイトル（結論文）＋ フッター（ロゴ・著作権）で構成される基本パターン。\n全コンテンツスライドのベースとなる。",
                L.MX, L.bodyY + 0.50, L.CW, 0.80,
                font_size=13, color=C.textPrimary)
    sb.add_bullets(sid, [
        "タイトルは結論文（アクションタイトル原則）",
        "フッターにロゴ・著作権・ページ番号を配置",
        "本体はタイトルの根拠を提示",
        "1 スライド = 1 メッセージ",
    ], L.MX + 0.1, L.bodyY + 1.40, L.CW - 0.2, 2.5,
       font_size=13)

    # ====================================================================
    # Slide 4: Feature Slide（説明＋箇条書き＋コールアウト）
    # ====================================================================
    sb.add_feature_slide(
        "ScalarDB は既存 DB を変更せずに ACID トランザクションを実現する",
        "ScalarDB はアプリケーションと既存データベースの間に位置するミドルウェアとして動作します。",
        [
            "異種 DB 間の分散トランザクション",
            "既存 DB のスキーマ変更不要",
            "SQL と NoSQL の統一インターフェース",
            "線形スケーラビリティ",
        ],
        callout="導入実績: 金融・EC・製造業\n50社以上で本番稼働中",
    )

    # ====================================================================
    # Slide 5: Card Slide
    # ====================================================================
    sb.add_card_slide(
        "ScalarDB は 3 つのコア機能で異種 DB 統合を実現する",
        [
            ("Consensus Commit", "2PC ベースの分散トランザクション。\n異種 DB 間で ACID を保証。"),
            ("Universal Transaction", "SQL/NoSQL 統一API。\nDB ごとの個別実装が不要。"),
            ("Analytics Bridge", "OLTP と OLAP を統合。\nリアルタイム分析が可能。"),
        ],
    )

    # ====================================================================
    # Slide 6: Table
    # ====================================================================
    sid = sb.add_content_slide("ScalarDB は主要 DB を網羅的にサポートしている")
    sb.add_table(sid, 5, 4, L.MX, L.bodyY + 0.10, L.CW, 3.5,
                 data=[
                     ["データベース", "タイプ", "トランザクション", "スケール"],
                     ["PostgreSQL", "RDBMS", "ACID 対応", "垂直"],
                     ["Cassandra", "NoSQL", "結果整合性", "水平"],
                     ["DynamoDB", "NoSQL", "条件付き", "水平"],
                     ["CosmosDB", "Multi-model", "セッション", "グローバル"],
                 ],
                 header_fill=C.tableHeader)

    # ====================================================================
    # Slide 7: Section Divider — インフォグラフィクスパターン
    # ====================================================================
    sb.add_section_divider("インフォグラフィクスパターン",
                           "12 種のデータビジュアライゼーション")

    # ====================================================================
    # Slide 8: Stat Card + Progress Bar
    # ====================================================================
    sid = sb.add_content_slide("ScalarDB は高い可用性と低レイテンシを両立する")
    # Stat Cards (3列)
    stats = [
        ("99.99%", "可用性 SLA", C.primary),
        ("< 5ms", "P99 レイテンシ", C.accent),
        ("3x", "スループット向上", C.success),
    ]
    card_w = 2.8
    gap = 0.35
    start_x = (10.0 - (card_w * 3 + gap * 2)) / 2
    for i, (val, lbl, clr) in enumerate(stats):
        sb.add_stat_card(sid, start_x + i * (card_w + gap), L.bodyY + 0.10,
                         card_w, 1.8, val, lbl, icon_color=clr)
    # Progress Bars
    sb.add_text(sid, "導入進捗",
                L.MX, L.bodyY + 2.10, 2.0, 0.30,
                font_size=12, bold=True, color=C.textTitle)
    sb.add_progress_bar(sid, L.MX, L.bodyY + 2.50, 5.5, 0.22, 85,
                        fill=C.primary, bg=C.surfaceLight, label="85%")
    sb.add_progress_bar(sid, L.MX, L.bodyY + 2.90, 5.5, 0.22, 62,
                        fill=C.accent, bg=C.surfaceLight, label="62%")
    sb.add_text(sid, "金融業界",
                L.MX + 6.5, L.bodyY + 2.42, 2.0, 0.30,
                font_size=10, color=C.textSecondary)
    sb.add_text(sid, "製造業界",
                L.MX + 6.5, L.bodyY + 2.82, 2.0, 0.30,
                font_size=10, color=C.textSecondary)

    # ====================================================================
    # Slide 9: Timeline Horizontal
    # ====================================================================
    sid = sb.add_content_slide("ScalarDB は段階的に機能を拡充してきた")
    events_h = [
        {"label": "2020 Q1", "sublabel": "OSS 公開"},
        {"label": "2021 Q2", "sublabel": "商用版リリース"},
        {"label": "2023 Q1", "sublabel": "Analytics 対応"},
        {"label": "2024 Q3", "sublabel": "グローバル展開"},
        {"label": "2026 Q1", "sublabel": "AI 統合"},
    ]
    sb.add_timeline_h(sid, 0.8, 2.5, 8.4, events_h)

    # ====================================================================
    # Slide 10: Bar Chart + Donut Chart
    # ====================================================================
    sid = sb.add_content_slide("四半期ごとの導入数は着実に増加している")
    # Bar Chart (left)
    sb.add_text(sid, "四半期別新規導入数",
                L.MX, L.bodyY + 0.05, 4.0, 0.30,
                font_size=12, bold=True, color=C.textTitle)
    bar_data = [
        {"label": "Q1", "value": 12},
        {"label": "Q2", "value": 18},
        {"label": "Q3", "value": 28},
        {"label": "Q4", "value": 35},
    ]
    sb.add_bar_chart(sid, L.MX, L.bodyY + 0.40, 4.2, 3.5, bar_data)
    # Donut Chart (right)
    sb.add_text(sid, "業種別構成比",
                5.2, L.bodyY + 0.05, 4.0, 0.30,
                font_size=12, bold=True, color=C.textTitle)
    donut_segs = [
        {"label": "金融", "value": 40, "color": C.primary},
        {"label": "EC", "value": 25, "color": C.accent},
        {"label": "製造", "value": 20, "color": C.success},
        {"label": "その他", "value": 15, "color": C.chart2},
    ]
    sb.add_donut(sid, 6.5, L.bodyY + 2.30, 1.2, donut_segs, center_label="100社")

    # ====================================================================
    # Slide 11: Pyramid
    # ====================================================================
    sid = sb.add_content_slide("ScalarDB の導入は 4 段階で進められる")
    colors_pyr = [
        hex_to_rgb("#1B2A4A"),
        hex_to_rgb("#2D4A7A"),
        hex_to_rgb("#4A7AB5"),
        hex_to_rgb("#7AAAE0"),
    ]
    sb.add_pyramid(sid, 2.5, L.bodyY + 0.20, 5.0, 3.8,
                   ["戦略策定", "PoC 実施", "本番導入", "運用最適化"],
                   colors_pyr)

    # ====================================================================
    # Slide 12: Icon + Text Row
    # ====================================================================
    sid = sb.add_content_slide("ScalarDB は 3 つの価値を提供する")
    items = [
        {"icon": "1", "title": "高可用性", "desc": "99.99% SLA を保証し\nダウンタイムを最小化", "color": C.primary},
        {"icon": "2", "title": "低レイテンシ", "desc": "P99 < 5ms の応答で\nリアルタイム処理を実現", "color": C.primary},
        {"icon": "3", "title": "線形拡張", "desc": "ノード追加で性能が\n比例的に向上", "color": C.primary},
    ]
    sb.add_icon_text_row(sid, 0.5, L.bodyY + 0.50, items, icon_r=0.25)

    # ====================================================================
    # Slide 13: Comparison（2列比較）
    # ====================================================================
    sid = sb.add_content_slide("ScalarDB は従来方式の課題を解決する")
    left = {
        "title": "ScalarDB",
        "color": C.primary,
        "items": ["ACID トランザクション保証", "異種 DB 統一 API", "スキーマ変更不要", "水平スケーラブル"],
    }
    right = {
        "title": "従来方式",
        "color": C.textMuted,
        "items": ["結果整合性のみ", "DB ごとに個別実装", "アプリ側の整合性管理", "垂直スケールに依存"],
    }
    sb.add_comparison(sid, 0.5, L.bodyY + 0.10, 9.0, 3.2, left, right)

    # ====================================================================
    # Slide 14: Flow Diagram
    # ====================================================================
    sid = sb.add_content_slide("ScalarDB のトランザクション処理は 4 ステップで完結する")
    steps = [
        {"label": "Begin", "shape": "rounded", "color": hex_to_rgb("#7AAAE0")},
        {"label": "Read/Write", "shape": "rect", "color": hex_to_rgb("#4A7AB5")},
        {"label": "Validate", "shape": "diamond", "color": hex_to_rgb("#2D4A7A")},
        {"label": "Commit", "shape": "rounded", "color": hex_to_rgb("#1B2A4A")},
    ]
    sb.add_flow_diagram(sid, 0.6, L.bodyY + 1.2, steps,
                        box_w=1.8, box_h=0.7, gap=0.55)

    # ====================================================================
    # Slide 15: Decision Flow（分岐フロー）
    # ====================================================================
    sid = sb.add_content_slide("障害発生時のリカバリは自動的に分岐処理される")
    nodes = [
        {"id": 0, "label": "障害検知", "type": "start", "x": 3.2, "y": L.bodyY + 0.10},
        {"id": 1, "label": "復旧可能?", "type": "decision", "x": 3.3, "y": L.bodyY + 0.90,
         "color": hex_to_rgb("#BE9000")},
        {"id": 2, "label": "自動復旧", "type": "process", "x": 1.0, "y": L.bodyY + 2.20},
        {"id": 3, "label": "手動対応", "type": "process", "x": 5.8, "y": L.bodyY + 2.20,
         "color": C.error},
        {"id": 4, "label": "正常稼働", "type": "end", "x": 3.2, "y": L.bodyY + 3.30},
    ]
    edges = [
        {"from": 0, "to": 1},
        {"from": 1, "to": 2, "label": "Yes"},
        {"from": 1, "to": 3, "label": "No"},
        {"from": 2, "to": 4},
        {"from": 3, "to": 4},
    ]
    sb.add_decision_flow(sid, nodes, edges)

    # ====================================================================
    # Slide 16: Timeline Vertical
    # ====================================================================
    sid = sb.add_content_slide("導入プロジェクトは 5 つのフェーズで進行する")
    events_v = [
        {"label": "Phase 1: 要件定義", "sublabel": "2 週間"},
        {"label": "Phase 2: PoC 実施", "sublabel": "4 週間"},
        {"label": "Phase 3: 本番設計", "sublabel": "3 週間"},
        {"label": "Phase 4: 移行実施", "sublabel": "4 週間"},
        {"label": "Phase 5: 運用開始", "sublabel": "継続"},
    ]
    sb.add_timeline_v(sid, 2.0, L.bodyY + 0.30, 3.8, events_v)

    # ====================================================================
    # Slide 17: Venn Diagram
    # ====================================================================
    sid = sb.add_content_slide("ScalarDB は CAP 定理の制約下で最適解を提供する")
    sets = [
        {"label": "可用性", "color": hex_to_rgb("#4A7AB5")},
        {"label": "一貫性", "color": hex_to_rgb("#E8963A")},
        {"label": "分断耐性", "color": hex_to_rgb("#5AA05A")},
    ]
    sb.add_venn(sid, 5.0, 2.8, 1.3, sets, overlap_label="ScalarDB")

    # ====================================================================
    # Slide 18: Section Divider — ビジュアル要素
    # ====================================================================
    sb.add_section_divider("ビジュアル要素",
                           "シェイプ / コネクタ / エフェクト")

    # ====================================================================
    # Slide 19: Shapes Showcase
    # ====================================================================
    sid = sb.add_content_slide("Google Slides API は 141 種類のシェイプタイプをサポートする")

    # Row 1: 基本図形
    sb.add_text(sid, "基本図形",
                L.MX, L.bodyY + 0.05, 2.0, 0.25,
                font_size=10, bold=True, color=C.textTitle)
    sb.add_shape(sid, "RECTANGLE", 0.4, L.bodyY + 0.35, 0.6, 0.5, fill=C.primary)
    sb.add_shape(sid, "ROUND_RECTANGLE", 1.2, L.bodyY + 0.35, 0.6, 0.5, fill=C.accent)
    sb.add_shape(sid, "ELLIPSE", 2.0, L.bodyY + 0.35, 0.6, 0.5, fill=C.success)
    sb.add_shape(sid, "DIAMOND", 2.8, L.bodyY + 0.35, 0.5, 0.5, fill=C.chart2)
    sb.add_shape(sid, "TRIANGLE", 3.5, L.bodyY + 0.35, 0.5, 0.5, fill=C.primary)
    sb.add_shape(sid, "HEXAGON", 4.2, L.bodyY + 0.35, 0.6, 0.5, fill=C.primaryDark)
    sb.add_shape(sid, "CAN", 4.9, L.bodyY + 0.30, 0.5, 0.6, fill=C.accent)

    # Row 2: 矢印 / シェブロン / 星
    sb.add_text(sid, "矢印 / 装飾",
                L.MX, L.bodyY + 1.05, 2.0, 0.25,
                font_size=10, bold=True, color=C.textTitle)
    sb.add_shape(sid, "RIGHT_ARROW", 0.4, L.bodyY + 1.35, 0.8, 0.4, fill=C.primary)
    sb.add_shape(sid, "CHEVRON", 1.4, L.bodyY + 1.35, 0.7, 0.4, fill=C.accent)
    sb.add_shape(sid, "STAR_5", 2.3, L.bodyY + 1.30, 0.5, 0.5, fill=C.chart4)
    sb.add_shape(sid, "HEART", 3.0, L.bodyY + 1.30, 0.5, 0.5, fill=C.chart2)
    sb.add_shape(sid, "CLOUD", 3.7, L.bodyY + 1.30, 0.7, 0.5, fill=C.surfaceLight, border_color=C.border)

    # Row 2 right: フローチャート
    sb.add_text(sid, "フローチャート",
                5.5, L.bodyY + 1.05, 2.0, 0.25,
                font_size=10, bold=True, color=C.textTitle)
    sb.add_shape(sid, "FLOW_CHART_PROCESS", 5.5, L.bodyY + 1.35, 0.7, 0.4, fill=C.primary)
    sb.add_shape(sid, "FLOW_CHART_DECISION", 6.4, L.bodyY + 1.30, 0.5, 0.5, fill=C.warning)
    sb.add_shape(sid, "FLOW_CHART_TERMINATOR", 7.1, L.bodyY + 1.35, 0.7, 0.4, fill=C.success)
    sb.add_shape(sid, "FLOW_CHART_DOCUMENT", 8.0, L.bodyY + 1.35, 0.6, 0.45, fill=C.accent)

    # Row 3: ドロップシャドウ + 透明度 + 回転
    sb.add_text(sid, "エフェクト: Shadow / Opacity / Rotation",
                L.MX, L.bodyY + 2.05, 5.0, 0.25,
                font_size=10, bold=True, color=C.textTitle)

    # Shadow
    shadow_id = sb.add_rounded_rect(sid, 0.5, L.bodyY + 2.40, 1.5, 0.9,
                                     fill=C.primary, border_color=C.primary)
    sb.shape_shadow(shadow_id, blur_radius=4.0, offset_x=3.0, offset_y=3.0, alpha=0.25)
    sb.add_text(sid, "Shadow",
                0.5, L.bodyY + 2.40, 1.5, 0.9,
                font_size=12, bold=True, color=C.textOnDark,
                alignment="CENTER", valign="MIDDLE")

    # Opacity
    opaq_id = sb.add_rounded_rect(sid, 2.5, L.bodyY + 2.40, 1.5, 0.9,
                                   fill=C.accent)
    sb.shape_opacity(opaq_id, 0.4)
    sb.add_text(sid, "Opacity 40%",
                2.5, L.bodyY + 2.40, 1.5, 0.9,
                font_size=12, bold=True, color=C.textTitle,
                alignment="CENTER", valign="MIDDLE")

    # Rotation
    rot_x, rot_y, rot_w, rot_h = 4.7, L.bodyY + 2.40, 1.2, 0.9
    rot_id = sb.add_rounded_rect(sid, rot_x, rot_y, rot_w, rot_h, fill=C.success)
    sb.shape_rotation(rot_id, 15, x=rot_x, y=rot_y, w=rot_w, h=rot_h)
    sb.add_text(sid, "Rotate 15deg",
                rot_x, rot_y, rot_w, rot_h,
                font_size=10, bold=True, color=C.textOnDark,
                alignment="CENTER", valign="MIDDLE")

    # Gradient approximation
    sb.add_text(sid, "Gradient",
                6.5, L.bodyY + 2.05, 3.0, 0.25,
                font_size=10, bold=True, color=C.textTitle)
    gradient_steps = 6
    strip_w = 3.0 / gradient_steps
    color_start = C.primary
    color_end = C.success
    for i in range(gradient_steps):
        t = i / max(gradient_steps - 1, 1)
        blended = {
            "red": color_start["red"] * (1 - t) + color_end["red"] * t,
            "green": color_start["green"] * (1 - t) + color_end["green"] * t,
            "blue": color_start["blue"] * (1 - t) + color_end["blue"] * t,
        }
        sb.add_rect(sid, 6.5 + i * strip_w, L.bodyY + 2.40,
                     strip_w + 0.01, 0.9, fill=blended)

    # ====================================================================
    # Slide 20: Connectors Showcase
    # ====================================================================
    sid = sb.add_content_slide("コネクタ線はシェイプ間を自動追従で接続できる")

    # 座標コネクタ（矢印）
    sb.add_text(sid, "座標指定コネクタ",
                L.MX, L.bodyY + 0.05, 4.0, 0.25,
                font_size=10, bold=True, color=C.textTitle)
    sb.add_connector(sid, 0.5, L.bodyY + 0.60, 3.5, L.bodyY + 0.60,
                     color=C.primary, weight=2.0, end_arrow="FILL_ARROW")
    sb.add_connector(sid, 0.5, L.bodyY + 1.00, 3.5, L.bodyY + 1.00,
                     color=C.accent, weight=1.5, end_arrow="STEALTH_ARROW",
                     dash_style="DASH")
    sb.add_connector(sid, 0.5, L.bodyY + 1.40, 3.5, L.bodyY + 1.40,
                     color=C.success, weight=1.0, end_arrow="OPEN_ARROW",
                     dash_style="DOT")
    sb.add_connector(sid, 0.5, L.bodyY + 1.80, 3.5, L.bodyY + 1.80,
                     color=C.error, weight=1.5,
                     start_arrow="FILL_CIRCLE", end_arrow="FILL_DIAMOND")

    sb.add_text(sid, "FILL_ARROW（実線）", 3.7, L.bodyY + 0.50, 2.0, 0.25,
                font_size=9, color=C.textSecondary)
    sb.add_text(sid, "STEALTH_ARROW（破線）", 3.7, L.bodyY + 0.90, 2.0, 0.25,
                font_size=9, color=C.textSecondary)
    sb.add_text(sid, "OPEN_ARROW（点線）", 3.7, L.bodyY + 1.30, 2.0, 0.25,
                font_size=9, color=C.textSecondary)
    sb.add_text(sid, "CIRCLE → DIAMOND", 3.7, L.bodyY + 1.70, 2.0, 0.25,
                font_size=9, color=C.textSecondary)

    # シェイプ接続コネクタ
    sb.add_text(sid, "シェイプ接続コネクタ",
                6.0, L.bodyY + 0.05, 3.5, 0.25,
                font_size=10, bold=True, color=C.textTitle)
    box_a = sb.add_rounded_rect(sid, 6.2, L.bodyY + 0.50, 1.2, 0.6, fill=C.primary)
    sb.add_text(sid, "Box A", 6.2, L.bodyY + 0.50, 1.2, 0.6,
                font_size=11, bold=True, color=C.textOnDark,
                alignment="CENTER", valign="MIDDLE")
    box_b = sb.add_rounded_rect(sid, 8.2, L.bodyY + 0.50, 1.2, 0.6, fill=C.accent)
    sb.add_text(sid, "Box B", 8.2, L.bodyY + 0.50, 1.2, 0.6,
                font_size=11, bold=True, color=C.textOnDark,
                alignment="CENTER", valign="MIDDLE")
    box_c = sb.add_rounded_rect(sid, 7.2, L.bodyY + 1.60, 1.2, 0.6, fill=C.success)
    sb.add_text(sid, "Box C", 7.2, L.bodyY + 1.60, 1.2, 0.6,
                font_size=11, bold=True, color=C.textOnDark,
                alignment="CENTER", valign="MIDDLE")

    CONN_TOP, CONN_LEFT, CONN_BOTTOM, CONN_RIGHT = 0, 1, 2, 3
    sb.add_connected_connector(sid, box_a, CONN_RIGHT, box_b, CONN_LEFT,
                               color=C.textMuted, weight=1.5)
    sb.add_connected_connector(sid, box_a, CONN_BOTTOM, box_c, CONN_LEFT,
                               color=C.textMuted, weight=1.5)
    sb.add_connected_connector(sid, box_b, CONN_BOTTOM, box_c, CONN_RIGHT,
                               color=C.textMuted, weight=1.5,
                               dash_style="DASH")

    # Group + Z-order demo
    sb.add_text(sid, "グループ化 + Z-order",
                L.MX, L.bodyY + 2.50, 4.0, 0.25,
                font_size=10, bold=True, color=C.textTitle)
    g1 = sb.add_rect(sid, 0.5, L.bodyY + 2.90, 1.0, 0.7, fill=C.primary)
    g2 = sb.add_rect(sid, 0.8, L.bodyY + 3.10, 1.0, 0.7, fill=C.accent)
    sb.set_z_order(g1, "BRING_TO_FRONT")
    sb.add_text(sid, "BRING_TO_FRONT で\n青を前面に", 2.0, L.bodyY + 2.90, 2.5, 0.7,
                font_size=10, color=C.textSecondary)

    # ====================================================================
    # Slide 21: Closing
    # ====================================================================
    sid = sb.add_slide()
    sb.set_bg(sid, C.background)
    sb.add_text(sid, "Scalar", 3.307, 2.323, 3.385, 0.979,
                font_size=36, bold=True, color=C.primary,
                font_family="Noto Sans JP", alignment="CENTER", valign="MIDDLE")
    sb.add_rect(sid, 0, 3.667, 10.0, 1.958, fill=C.primary)
    sb.add_text(sid, "全 25 パターン ショーケース完了",
                2.0, 4.0, 6.0, 0.5,
                font_size=14, color=C.textOnDark,
                alignment="CENTER", valign="MIDDLE")

    # ─── 実行 ────────────────────────────────────────────
    print(f"Total requests: {len(sb.requests)}")
    execute_batch(slides_service, pres_id, sb.requests)

    url = f"https://docs.google.com/presentation/d/{pres_id}/edit"
    print(f"\nDone! {len(sb.slide_ids)} slides created.")
    print(f"Open: {url}")

    if OUTPUT_FOLDER_ID:
        # Drive API でプレゼンテーションを指定フォルダに移動
        file_meta = drive_service.files().get(
            fileId=pres_id, fields="parents"
        ).execute()
        prev_parents = ",".join(file_meta.get("parents", []))
        drive_service.files().update(
            fileId=pres_id,
            addParents=OUTPUT_FOLDER_ID,
            removeParents=prev_parents,
            fields="id, parents",
        ).execute()
        print(f"Moved to folder: {OUTPUT_FOLDER_ID}")


if __name__ == "__main__":
    if not os.path.exists(CREDS_FILE):
        sys.exit(
            f"Error: {CREDS_FILE} が見つかりません。\n"
            "GCP Console から OAuth クライアント credentials.json をダウンロードし、\n"
            f"{os.path.dirname(CREDS_FILE)}/ に配置してください。"
        )
    try:
        main()
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        sys.exit(1)
