#!/usr/bin/env python3
"""ScalarDB クラウド構成図 生成スクリプト (Google Slides API)

AWS / Azure / GCP の 3 枚構成。各スライドは ScalarDB の典型的なデプロイ構成を示す。
クラウドアイコン PNG が未配置のため、テキストバッジで代替する。
"""

import sys
if sys.version_info < (3, 10):
    sys.exit("Error: Python 3.10+ が必要です。現在: Python {}.{}".format(*sys.version_info[:2]))

import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# ─── パス設定 ───────────────────────────────────────
SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
CREDS_FILE = os.path.join(SKILL_DIR, "config", "credentials.json")
TOKEN_FILE = os.path.join(SKILL_DIR, "config", "token.json")
SCOPES = [
    "https://www.googleapis.com/auth/presentations",
    "https://www.googleapis.com/auth/drive.file",
]

# ─── テーマ色定数 (scalar theme.json) ──────────────────
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

class C:
    primary       = hex_to_rgb("#2673BB")
    primaryDark   = hex_to_rgb("#004266")
    accent        = hex_to_rgb("#0985FC")
    success       = hex_to_rgb("#63C045")
    textPrimary   = hex_to_rgb("#000000")
    textTitle     = hex_to_rgb("#004266")
    textOnDark    = hex_to_rgb("#FFFFFF")
    textMuted     = hex_to_rgb("#666666")
    textSecondary = hex_to_rgb("#595959")
    background    = hex_to_rgb("#FFFFFF")
    backgroundAlt = hex_to_rgb("#F9FAFA")
    surfaceLight  = hex_to_rgb("#F0F4F8")
    border        = hex_to_rgb("#6B7280")
    calloutBg     = hex_to_rgb("#F0F4F8")
    warning       = hex_to_rgb("#E8963A")
    error         = hex_to_rgb("#DC2626")
    WHITE         = hex_to_rgb("#FFFFFF")

# アーキテクチャ図色
ARCH = {
    "scalar":    hex_to_rgb("#2673BB"),
    "scalar_dk": hex_to_rgb("#004266"),
    "external":  hex_to_rgb("#666666"),
    "client":    hex_to_rgb("#E8963A"),
    "flow_ok":   hex_to_rgb("#63C045"),
    "flow_err":  hex_to_rgb("#DC2626"),
    "cloud":     hex_to_rgb("#0985FC"),
}

VENDOR_COLORS = {
    "aws":   hex_to_rgb("#FF9900"),
    "azure": hex_to_rgb("#0078D4"),
    "gcp":   hex_to_rgb("#4285F4"),
}

# ─── ヘルパー ──────────────────────────────────────
def solid_fill(color):
    return {"solidFill": {"color": {"rgbColor": color}}}

def text_style(font_size=18, bold=False, color=None, font_family="Noto Sans JP"):
    s = {"fontSize": {"magnitude": font_size, "unit": "PT"}, "bold": bold, "fontFamily": font_family}
    if color:
        s["foregroundColor"] = {"opaqueColor": {"rgbColor": color}}
    return s

def create_shape_req(page_id, shape_id, shape_type, x, y, w, h):
    return {"createShape": {
        "objectId": shape_id, "shapeType": shape_type,
        "elementProperties": {
            "pageObjectId": page_id,
            "size": {"width": {"magnitude": inches(w), "unit": "EMU"}, "height": {"magnitude": inches(h), "unit": "EMU"}},
            "transform": {"scaleX": 1, "scaleY": 1, "translateX": inches(x), "translateY": inches(y), "unit": "EMU"},
        },
    }}

def create_textbox_req(page_id, box_id, x, y, w, h):
    return {"createShape": {
        "objectId": box_id, "shapeType": "TEXT_BOX",
        "elementProperties": {
            "pageObjectId": page_id,
            "size": {"width": {"magnitude": inches(w), "unit": "EMU"}, "height": {"magnitude": inches(h), "unit": "EMU"}},
            "transform": {"scaleX": 1, "scaleY": 1, "translateX": inches(x), "translateY": inches(y), "unit": "EMU"},
        },
    }}

# ─── SlideBuilder ──────────────────────────────────
class SlideBuilder:
    def __init__(self):
        self.requests = []
        self.slide_ids = []
        self._counter = 0

    def _id(self, prefix="obj"):
        self._counter += 1
        return f"{prefix}_{self._counter:04d}"

    def add_slide(self):
        sid = self._id("slide")
        self.requests.append({"createSlide": {"objectId": sid, "slideLayoutReference": {"predefinedLayout": "BLANK"}}})
        self.slide_ids.append(sid)
        return sid

    def set_bg(self, sid, color):
        self.requests.append({"updatePageProperties": {"objectId": sid, "pageProperties": {"pageBackgroundFill": solid_fill(color)}, "fields": "pageBackgroundFill.solidFill.color"}})

    def add_shape(self, sid, shape_type, x, y, w, h, fill=None, border_color=None, border_weight=1.0):
        shape_id = self._id("shp")
        self.requests.append(create_shape_req(sid, shape_id, shape_type, x, y, w, h))
        if fill:
            self.requests.append({"updateShapeProperties": {"objectId": shape_id, "shapeProperties": {"shapeBackgroundFill": solid_fill(fill)}, "fields": "shapeBackgroundFill.solidFill.color"}})
        if border_color:
            self.requests.append({"updateShapeProperties": {"objectId": shape_id, "shapeProperties": {"outline": {"outlineFill": solid_fill(border_color), "weight": {"magnitude": border_weight, "unit": "PT"}}}, "fields": "outline"}})
        else:
            self.requests.append({"updateShapeProperties": {"objectId": shape_id, "shapeProperties": {"outline": {"propertyState": "NOT_RENDERED"}}, "fields": "outline"}})
        return shape_id

    def shape_opacity(self, shape_id, alpha):
        self.requests.append({"updateShapeProperties": {"objectId": shape_id, "shapeProperties": {"shapeBackgroundFill": {"solidFill": {"alpha": alpha}}}, "fields": "shapeBackgroundFill.solidFill.alpha"}})

    def set_z_order(self, shape_id, op):
        self.requests.append({"updatePageElementsZOrder": {"pageElementObjectIds": [shape_id], "operation": op}})

    def add_text(self, sid, text, x, y, w, h, *, font_size=18, bold=False, color=None, font_family="Noto Sans JP", alignment="START", valign="TOP"):
        box_id = self._id("txt")
        self.requests.append(create_textbox_req(sid, box_id, x, y, w, h))
        self.requests.append({"insertText": {"objectId": box_id, "text": text, "insertionIndex": 0}})
        st = text_style(font_size, bold, color, font_family)
        self.requests.append({"updateTextStyle": {"objectId": box_id, "style": st, "textRange": {"type": "FIXED_RANGE", "startIndex": 0, "endIndex": len(text)}, "fields": ",".join(st.keys())}})
        self.requests.append({"updateParagraphStyle": {"objectId": box_id, "style": {"alignment": alignment}, "textRange": {"type": "FIXED_RANGE", "startIndex": 0, "endIndex": len(text)}, "fields": "alignment"}})
        self.requests.append({"updateShapeProperties": {"objectId": box_id, "shapeProperties": {"contentAlignment": valign}, "fields": "contentAlignment"}})
        return box_id

    def add_connector(self, sid, x1, y1, x2, y2, color=None, weight=1.0, start_arrow=None, end_arrow=None, dash_style="SOLID"):
        line_id = self._id("conn")
        lx, ly = min(x1, x2), min(y1, y2)
        lw, lh = abs(x2 - x1), abs(y2 - y1)
        sx = 1 if x2 >= x1 else -1
        sy = 1 if y2 >= y1 else -1
        self.requests.append({"createLine": {
            "objectId": line_id, "lineCategory": "STRAIGHT",
            "elementProperties": {
                "pageObjectId": sid,
                "size": {"width": {"magnitude": inches(lw) if lw > 0 else 1, "unit": "EMU"}, "height": {"magnitude": inches(lh) if lh > 0 else 1, "unit": "EMU"}},
                "transform": {"scaleX": sx, "scaleY": sy, "translateX": inches(x1 if sx > 0 else x2), "translateY": inches(y1 if sy > 0 else y2), "unit": "EMU"},
            },
        }})
        props = {"weight": {"magnitude": weight, "unit": "PT"}, "dashStyle": dash_style}
        fields = ["weight", "dashStyle"]
        if color:
            props["lineFill"] = solid_fill(color)
            fields.append("lineFill")
        if start_arrow:
            props["startArrow"] = start_arrow
            fields.append("startArrow")
        if end_arrow:
            props["endArrow"] = end_arrow
            fields.append("endArrow")
        self.requests.append({"updateLineProperties": {"objectId": line_id, "lineProperties": props, "fields": ",".join(fields)}})
        return line_id

    def add_line(self, sid, x, y, w, color=None, weight=0.75):
        line_id = self._id("line")
        self.requests.append({"createLine": {
            "objectId": line_id, "lineCategory": "STRAIGHT",
            "elementProperties": {
                "pageObjectId": sid,
                "size": {"width": {"magnitude": inches(w), "unit": "EMU"}, "height": {"magnitude": 0, "unit": "EMU"}},
                "transform": {"scaleX": 1, "scaleY": 1, "translateX": inches(x), "translateY": inches(y), "unit": "EMU"},
            },
        }})
        self.requests.append({"updateLineProperties": {"objectId": line_id, "lineProperties": {"lineFill": solid_fill(color), "weight": {"magnitude": weight, "unit": "PT"}}, "fields": "lineFill,weight"}})
        return line_id

    # ─ コンポジット ─

    def add_zone(self, sid, label, x, y, w, h, fill_color=None, border_color=None, border_dash="SOLID", alpha=0.08, label_position="top-left"):
        fc = fill_color or C.backgroundAlt
        bc = border_color or C.border
        bg_id = self.add_shape(sid, "ROUND_RECTANGLE", x, y, w, h, fill=fc, border_color=bc)
        self.shape_opacity(bg_id, alpha)
        self.set_z_order(bg_id, "SEND_TO_BACK")
        if border_dash != "SOLID":
            self.requests.append({"updateShapeProperties": {"objectId": bg_id, "shapeProperties": {"outline": {"dashStyle": border_dash}}, "fields": "outline.dashStyle"}})
        lc = border_color or C.textMuted
        if label:
            if label_position == "top-left":
                self.add_text(sid, label, x + 0.1, y + 0.05, w * 0.6, 0.2, font_size=9, bold=True, color=lc)
            elif label_position == "top-center":
                self.add_text(sid, label, x, y + 0.05, w, 0.2, font_size=9, bold=True, color=lc, alignment="CENTER")
        return bg_id

    def add_vendor_label(self, sid, vendor, region, zx, zy):
        names = {"aws": "AWS", "gcp": "Google Cloud", "azure": "Microsoft Azure"}
        label = f"{names[vendor]} ({region})"
        self.add_text(sid, label, zx + 0.1, zy + 0.05, 3.0, 0.22, font_size=9, bold=True, color=VENDOR_COLORS[vendor])

    def add_component(self, sid, name, shape_type, x, y, w, h, fill, sublabel=None):
        shape_id = self.add_shape(sid, shape_type, x, y, w, h, fill=fill)
        fs = 9 if len(name) > 12 else 10
        self.add_text(sid, name, x, y, w, h, font_size=fs, bold=True, color=C.WHITE, alignment="CENTER", valign="MIDDLE")
        if sublabel:
            self.add_text(sid, sublabel, x - 0.1, y + h + 0.02, w + 0.2, 0.18, font_size=8, color=C.textSecondary, alignment="CENTER")
        return shape_id

    def add_scalardb(self, sid, x, y, w=2.0, h=0.55, cluster=False):
        if cluster:
            self.add_shape(sid, "ROUND_RECTANGLE", x + 0.05, y + 0.05, w, h, fill=ARCH["scalar_dk"])
            self.add_shape(sid, "ROUND_RECTANGLE", x + 0.025, y + 0.025, w, h, fill=ARCH["scalar_dk"])
        shape_id = self.add_shape(sid, "ROUND_RECTANGLE", x, y, w, h, fill=ARCH["scalar"])
        self.add_text(sid, "ScalarDB", x, y, w, h, font_size=12, bold=True, color=C.WHITE, alignment="CENTER", valign="MIDDLE")
        return shape_id

    def add_cloud_badge(self, sid, name, x, y, size=0.5, color=None):
        c = color or ARCH["external"]
        self.add_shape(sid, "ROUND_RECTANGLE", x, y, size, size, fill=c)
        abbr = name[:3].upper()
        self.add_text(sid, abbr, x, y, size, size, font_size=8, bold=True, color=C.WHITE, alignment="CENTER", valign="MIDDLE")
        self.add_text(sid, name, x - 0.15, y + size + 0.02, size + 0.3, 0.18, font_size=7, color=C.textSecondary, alignment="CENTER")

    def add_data_flow(self, sid, fx, fy, tx, ty, flow_type="normal", label=None):
        styles = {
            "normal":  (ARCH["flow_ok"],  "SOLID", 1.5, None, "FILL_ARROW"),
            "read":    (ARCH["scalar"],   "SOLID", 1.0, None, "FILL_ARROW"),
            "write":   (ARCH["cloud"],    "SOLID", 1.0, None, "FILL_ARROW"),
            "error":   (ARCH["flow_err"], "DASH",  1.0, None, "FILL_ARROW"),
            "bidir":   (ARCH["scalar"],   "SOLID", 1.0, "FILL_ARROW", "FILL_ARROW"),
            "repl":    (ARCH["flow_ok"],  "LONG_DASH", 1.0, None, "FILL_ARROW"),
        }
        col, dash, wt, sa, ea = styles[flow_type]
        self.add_connector(sid, fx, fy, tx, ty, color=col, weight=wt, start_arrow=sa, end_arrow=ea, dash_style=dash)
        if label:
            mx, my = (fx + tx) / 2, (fy + ty) / 2
            is_h = abs(ty - fy) < abs(tx - fx)
            oy = -0.16 if is_h else 0
            ox = 0.1 if not is_h else 0
            self.add_text(sid, label, mx - 0.35 + ox, my - 0.09 + oy, 0.7, 0.18, font_size=7, color=col, alignment="CENTER", valign="MIDDLE")

    def add_footer(self, sid, page_num):
        self.add_text(sid, "Scalar", 0.323, 5.208, 0.952, 0.244, font_size=9, bold=True, color=C.primary, valign="MIDDLE")
        self.add_text(sid, "(C) 2026 Scalar, Inc.", 2.0, 5.30, 6.083, 0.20, font_size=7, color=C.textMuted, font_family="Arial", alignment="CENTER", valign="MIDDLE")
        self.add_text(sid, str(page_num), 9.077, 5.246, 0.600, 0.168, font_size=7, color=C.textMuted, font_family="Arial", alignment="END", valign="MIDDLE")

    def add_legend(self, sid, x, y, items):
        rh = 0.22
        th = len(items) * rh + 0.20
        self.add_shape(sid, "ROUND_RECTANGLE", x, y, 2.3, th, fill=C.background, border_color=C.border, border_weight=0.5)
        self.add_text(sid, "Legend", x + 0.1, y + 0.03, 1.0, 0.18, font_size=8, bold=True, color=C.textTitle)
        for i, item in enumerate(items):
            iy = y + 0.20 + i * rh
            if item["shape"] == "rect":
                self.add_shape(sid, "RECTANGLE", x + 0.1, iy + 0.03, 0.2, 0.14, fill=item["color"])
            elif item["shape"] == "line":
                self.add_connector(sid, x + 0.1, iy + 0.10, x + 0.3, iy + 0.10, color=item["color"], weight=1.5)
            elif item["shape"] == "dash":
                self.add_connector(sid, x + 0.1, iy + 0.10, x + 0.3, iy + 0.10, color=item["color"], weight=1.0, dash_style="DASH")
            self.add_text(sid, item["label"], x + 0.4, iy, 1.8, rh, font_size=8, color=C.textPrimary, valign="MIDDLE")

    def add_content_slide(self, title, page_num):
        sid = self.add_slide()
        self.set_bg(sid, C.background)
        # タイトル
        self.add_text(sid, title, 0.323, 0.303, 9.354, 0.437, font_size=20, bold=True, color=C.textTitle)
        # セパレーター
        self.add_line(sid, 0.323, 0.76, 9.354, color=C.primary, weight=1.5)
        # フッター
        self.add_footer(sid, page_num)
        return sid


# ================================================================
#  スライド構成
# ================================================================

def build_aws_slide(sb):
    """Slide 1: ScalarDB on AWS"""
    sid = sb.add_content_slide(
        "ScalarDB on AWS：RDS・DynamoDB 統合トランザクション構成", 1)

    # --- AWS Region Zone ---
    sb.add_zone(sid, "", 0.35, 0.95, 9.3, 4.1,
                fill_color=hex_to_rgb("#FFF8EE"), border_color=VENDOR_COLORS["aws"], alpha=0.06)
    sb.add_vendor_label(sid, "aws", "ap-northeast-1", 0.35, 0.95)

    # VPC
    sb.add_zone(sid, "VPC  10.0.0.0/16", 0.55, 1.35, 8.9, 3.55,
                fill_color=C.surfaceLight, border_color=C.primary, alpha=0.08)

    # Private Subnet A
    sb.add_zone(sid, "Private Subnet (AZ-a)", 0.75, 1.75, 4.1, 2.95,
                fill_color=C.calloutBg, border_color=C.accent, alpha=0.06)

    # Private Subnet B
    sb.add_zone(sid, "Private Subnet (AZ-c)", 5.1, 1.75, 4.15, 2.95,
                fill_color=C.calloutBg, border_color=C.accent, alpha=0.06)

    # --- Components ---
    # Client (top, outside zones)
    cl_x, cl_y, cl_w, cl_h = 3.5, 0.38, 3.0, 0.35
    # (already in title area — put below separator)

    # ALB
    alb_x, alb_y, alb_w, alb_h = 3.8, 1.45, 2.4, 0.28
    sb.add_component(sid, "Application Load Balancer", "ROUND_RECTANGLE",
                     alb_x, alb_y, alb_w, alb_h, ARCH["cloud"])

    # ScalarDB Nodes (Subnet A)
    sdb1_x, sdb1_y, sdb1_w, sdb1_h = 1.1, 2.2, 1.8, 0.5
    sb.add_component(sid, "ScalarDB\nNode 1", "ROUND_RECTANGLE",
                     sdb1_x, sdb1_y, sdb1_w, sdb1_h, ARCH["scalar"])

    sdb2_x, sdb2_y, sdb2_w, sdb2_h = 1.1, 2.95, 1.8, 0.5
    sb.add_component(sid, "ScalarDB\nNode 2", "ROUND_RECTANGLE",
                     sdb2_x, sdb2_y, sdb2_w, sdb2_h, ARCH["scalar"])

    # Scalar Envoy
    env_x, env_y, env_w, env_h = 3.2, 2.55, 1.3, 0.45
    sb.add_component(sid, "Scalar\nEnvoy", "ROUND_RECTANGLE",
                     env_x, env_y, env_w, env_h, ARCH["scalar_dk"])

    # RDS Primary (Subnet B)
    rds1_x, rds1_y, rds1_w, rds1_h = 5.7, 2.1, 0.8, 0.85
    sb.add_component(sid, "RDS\nPrimary", "CAN",
                     rds1_x, rds1_y, rds1_w, rds1_h, ARCH["external"],
                     sublabel="MySQL 8.0")

    # DynamoDB (Subnet B)
    ddb_x, ddb_y, ddb_w, ddb_h = 7.8, 2.1, 0.8, 0.85
    sb.add_component(sid, "Dynamo\nDB", "CAN",
                     ddb_x, ddb_y, ddb_w, ddb_h, ARCH["external"],
                     sublabel="NoSQL")

    # RDS Replica (Subnet B)
    rds2_x, rds2_y, rds2_w, rds2_h = 5.7, 3.55, 0.8, 0.85
    sb.add_component(sid, "RDS\nReplica", "CAN",
                     rds2_x, rds2_y, rds2_w, rds2_h, ARCH["external"],
                     sublabel="Read Replica")

    # --- Connectors ---
    # ALB -> ScalarDB Node 1
    sb.add_data_flow(sid, alb_x + alb_w * 0.3, alb_y + alb_h,
                     sdb1_x + sdb1_w / 2, sdb1_y, "normal")
    # ALB -> ScalarDB Node 2
    sb.add_data_flow(sid, alb_x + alb_w * 0.3, alb_y + alb_h,
                     sdb2_x + sdb2_w / 2, sdb2_y, "normal")
    # ScalarDB -> Envoy
    sb.add_data_flow(sid, sdb1_x + sdb1_w, sdb1_y + sdb1_h / 2,
                     env_x, env_y + env_h * 0.3, "read")
    sb.add_data_flow(sid, sdb2_x + sdb2_w, sdb2_y + sdb2_h / 2,
                     env_x, env_y + env_h * 0.7, "read")
    # Envoy -> RDS Primary
    sb.add_data_flow(sid, env_x + env_w, env_y + env_h * 0.3,
                     rds1_x, rds1_y + rds1_h / 2, "write", "JDBC")
    # Envoy -> DynamoDB
    sb.add_data_flow(sid, env_x + env_w, env_y + env_h * 0.7,
                     ddb_x, ddb_y + ddb_h / 2, "write", "API")
    # RDS Primary -> RDS Replica
    sb.add_data_flow(sid, rds1_x + rds1_w / 2, rds1_y + rds1_h,
                     rds2_x + rds2_w / 2, rds2_y, "repl", "Repl.")

    # --- Legend ---
    sb.add_legend(sid, 7.3, 3.55, [
        {"label": "Scalar 製品",   "color": ARCH["scalar"], "shape": "rect"},
        {"label": "AWS サービス",  "color": ARCH["external"], "shape": "rect"},
        {"label": "データフロー",  "color": ARCH["flow_ok"], "shape": "line"},
    ])


def build_azure_slide(sb):
    """Slide 2: ScalarDB on Azure"""
    sid = sb.add_content_slide(
        "ScalarDB は Azure 上で SQL Database と Cosmos DB を統合管理する", 2)

    # --- Azure Region Zone ---
    sb.add_zone(sid, "", 0.35, 0.95, 9.3, 4.1,
                fill_color=hex_to_rgb("#EEF4FF"), border_color=VENDOR_COLORS["azure"], alpha=0.06)
    sb.add_vendor_label(sid, "azure", "Japan East", 0.35, 0.95)

    # VNet
    sb.add_zone(sid, "VNet  10.0.0.0/16", 0.55, 1.35, 8.9, 3.55,
                fill_color=C.surfaceLight, border_color=C.primary, alpha=0.08)

    # Subnet
    sb.add_zone(sid, "Subnet (App)", 0.75, 1.75, 4.1, 2.95,
                fill_color=C.calloutBg, border_color=C.accent, alpha=0.06)
    sb.add_zone(sid, "Subnet (Data)", 5.1, 1.75, 4.15, 2.95,
                fill_color=C.calloutBg, border_color=C.accent, alpha=0.06)

    # --- Components ---
    # Azure LB
    lb_x, lb_y, lb_w, lb_h = 3.8, 1.45, 2.4, 0.28
    sb.add_component(sid, "Azure Load Balancer", "ROUND_RECTANGLE",
                     lb_x, lb_y, lb_w, lb_h, ARCH["cloud"])

    # AKS Cluster label
    sb.add_zone(sid, "AKS Cluster", 0.95, 2.05, 3.7, 2.45,
                fill_color=hex_to_rgb("#E8F0FE"), border_color=ARCH["scalar"], alpha=0.05)

    # ScalarDB Pods
    pod1_x, pod1_y, pod1_w, pod1_h = 1.3, 2.45, 1.5, 0.45
    sb.add_component(sid, "ScalarDB\nPod 1", "ROUND_RECTANGLE",
                     pod1_x, pod1_y, pod1_w, pod1_h, ARCH["scalar"])
    pod2_x, pod2_y, pod2_w, pod2_h = 1.3, 3.15, 1.5, 0.45
    sb.add_component(sid, "ScalarDB\nPod 2", "ROUND_RECTANGLE",
                     pod2_x, pod2_y, pod2_w, pod2_h, ARCH["scalar"])
    pod3_x, pod3_y, pod3_w, pod3_h = 1.3, 3.85, 1.5, 0.45
    sb.add_component(sid, "ScalarDB\nPod 3", "ROUND_RECTANGLE",
                     pod3_x, pod3_y, pod3_w, pod3_h, ARCH["scalar"])

    # Scalar Envoy
    env_x, env_y, env_w, env_h = 3.2, 3.0, 1.2, 0.45
    sb.add_component(sid, "Scalar\nEnvoy", "ROUND_RECTANGLE",
                     env_x, env_y, env_w, env_h, ARCH["scalar_dk"])

    # Azure SQL Database
    sql_x, sql_y, sql_w, sql_h = 5.7, 2.1, 0.9, 0.85
    sb.add_component(sid, "Azure\nSQL DB", "CAN",
                     sql_x, sql_y, sql_w, sql_h, ARCH["external"],
                     sublabel="SQL Database")

    # Cosmos DB
    cos_x, cos_y, cos_w, cos_h = 7.8, 2.1, 0.9, 0.85
    sb.add_component(sid, "Cosmos\nDB", "CAN",
                     cos_x, cos_y, cos_w, cos_h, ARCH["external"],
                     sublabel="NoSQL / Multi-model")

    # Azure Monitor
    mon_x, mon_y, mon_w, mon_h = 5.4, 4.05, 1.5, 0.4
    sb.add_component(sid, "Azure Monitor", "ROUND_RECTANGLE",
                     mon_x, mon_y, mon_w, mon_h, hex_to_rgb("#4B5563"))

    # --- Connectors ---
    # LB -> Pods
    sb.add_data_flow(sid, lb_x + lb_w * 0.3, lb_y + lb_h,
                     pod1_x + pod1_w / 2, pod1_y, "normal")
    sb.add_data_flow(sid, lb_x + lb_w * 0.3, lb_y + lb_h,
                     pod2_x + pod2_w / 2, pod2_y, "normal")
    # Pods -> Envoy
    sb.add_data_flow(sid, pod1_x + pod1_w, pod1_y + pod1_h / 2,
                     env_x, env_y + env_h * 0.3, "read")
    sb.add_data_flow(sid, pod2_x + pod2_w, pod2_y + pod2_h / 2,
                     env_x, env_y + env_h * 0.7, "read")
    # Envoy -> Azure SQL
    sb.add_data_flow(sid, env_x + env_w, env_y + env_h * 0.3,
                     sql_x, sql_y + sql_h / 2, "write", "JDBC")
    # Envoy -> Cosmos DB
    sb.add_data_flow(sid, env_x + env_w, env_y + env_h * 0.7,
                     cos_x, cos_y + cos_h / 2, "write", "API")
    # Monitor (dashed)
    sb.add_connector(sid, pod3_x + pod3_w, pod3_y + pod3_h / 2,
                     mon_x, mon_y + mon_h / 2,
                     color=C.textMuted, weight=0.75, end_arrow="STEALTH_ARROW", dash_style="DASH_DOT")

    # --- Legend ---
    sb.add_legend(sid, 7.5, 3.85, [
        {"label": "Scalar 製品",   "color": ARCH["scalar"], "shape": "rect"},
        {"label": "Azure サービス","color": ARCH["external"], "shape": "rect"},
        {"label": "データフロー",  "color": ARCH["flow_ok"], "shape": "line"},
    ])


def build_gcp_slide(sb):
    """Slide 3: ScalarDB on GCP"""
    sid = sb.add_content_slide(
        "ScalarDB は GCP 上で Cloud Spanner と Cloud SQL を横断管理する", 3)

    # --- GCP Region Zone ---
    sb.add_zone(sid, "", 0.35, 0.95, 9.3, 4.1,
                fill_color=hex_to_rgb("#EDF7ED"), border_color=VENDOR_COLORS["gcp"], alpha=0.06)
    sb.add_vendor_label(sid, "gcp", "asia-northeast1", 0.35, 0.95)

    # VPC
    sb.add_zone(sid, "VPC Network", 0.55, 1.35, 8.9, 3.55,
                fill_color=C.surfaceLight, border_color=C.primary, alpha=0.08)

    # GKE Cluster
    sb.add_zone(sid, "GKE Cluster", 0.75, 1.75, 4.1, 2.95,
                fill_color=hex_to_rgb("#E8F0FE"), border_color=ARCH["scalar"], alpha=0.05)

    # Data zone
    sb.add_zone(sid, "Managed Services", 5.1, 1.75, 4.15, 2.95,
                fill_color=C.calloutBg, border_color=C.accent, alpha=0.06)

    # --- Components ---
    # Cloud Load Balancing
    lb_x, lb_y, lb_w, lb_h = 3.8, 1.45, 2.4, 0.28
    sb.add_component(sid, "Cloud Load Balancing", "ROUND_RECTANGLE",
                     lb_x, lb_y, lb_w, lb_h, ARCH["cloud"])

    # ScalarDB Pods
    pod1_x, pod1_y, pod1_w, pod1_h = 1.3, 2.45, 1.5, 0.45
    sb.add_component(sid, "ScalarDB\nPod 1", "ROUND_RECTANGLE",
                     pod1_x, pod1_y, pod1_w, pod1_h, ARCH["scalar"])
    pod2_x, pod2_y, pod2_w, pod2_h = 1.3, 3.15, 1.5, 0.45
    sb.add_component(sid, "ScalarDB\nPod 2", "ROUND_RECTANGLE",
                     pod2_x, pod2_y, pod2_w, pod2_h, ARCH["scalar"])
    pod3_x, pod3_y, pod3_w, pod3_h = 1.3, 3.85, 1.5, 0.45
    sb.add_component(sid, "ScalarDB\nPod 3", "ROUND_RECTANGLE",
                     pod3_x, pod3_y, pod3_w, pod3_h, ARCH["scalar"])

    # Scalar Envoy
    env_x, env_y, env_w, env_h = 3.2, 3.0, 1.2, 0.45
    sb.add_component(sid, "Scalar\nEnvoy", "ROUND_RECTANGLE",
                     env_x, env_y, env_w, env_h, ARCH["scalar_dk"])

    # Cloud Spanner
    sp_x, sp_y, sp_w, sp_h = 5.7, 2.1, 0.9, 0.85
    sb.add_component(sid, "Cloud\nSpanner", "CAN",
                     sp_x, sp_y, sp_w, sp_h, ARCH["external"],
                     sublabel="NewSQL")

    # Cloud SQL
    csql_x, csql_y, csql_w, csql_h = 7.8, 2.1, 0.9, 0.85
    sb.add_component(sid, "Cloud\nSQL", "CAN",
                     csql_x, csql_y, csql_w, csql_h, ARCH["external"],
                     sublabel="PostgreSQL")

    # Cloud Monitoring
    mon_x, mon_y, mon_w, mon_h = 5.4, 4.05, 1.6, 0.4
    sb.add_component(sid, "Cloud Monitoring", "ROUND_RECTANGLE",
                     mon_x, mon_y, mon_w, mon_h, hex_to_rgb("#4B5563"))

    # --- Connectors ---
    # LB -> Pods
    sb.add_data_flow(sid, lb_x + lb_w * 0.3, lb_y + lb_h,
                     pod1_x + pod1_w / 2, pod1_y, "normal")
    sb.add_data_flow(sid, lb_x + lb_w * 0.3, lb_y + lb_h,
                     pod2_x + pod2_w / 2, pod2_y, "normal")
    # Pods -> Envoy
    sb.add_data_flow(sid, pod1_x + pod1_w, pod1_y + pod1_h / 2,
                     env_x, env_y + env_h * 0.3, "read")
    sb.add_data_flow(sid, pod2_x + pod2_w, pod2_y + pod2_h / 2,
                     env_x, env_y + env_h * 0.7, "read")
    # Envoy -> Cloud Spanner
    sb.add_data_flow(sid, env_x + env_w, env_y + env_h * 0.3,
                     sp_x, sp_y + sp_h / 2, "write", "gRPC")
    # Envoy -> Cloud SQL
    sb.add_data_flow(sid, env_x + env_w, env_y + env_h * 0.7,
                     csql_x, csql_y + csql_h / 2, "write", "JDBC")
    # Monitor (dashed)
    sb.add_connector(sid, pod3_x + pod3_w, pod3_y + pod3_h / 2,
                     mon_x, mon_y + mon_h / 2,
                     color=C.textMuted, weight=0.75, end_arrow="STEALTH_ARROW", dash_style="DASH_DOT")

    # --- Legend ---
    sb.add_legend(sid, 7.5, 3.85, [
        {"label": "Scalar 製品",   "color": ARCH["scalar"], "shape": "rect"},
        {"label": "GCP サービス",  "color": ARCH["external"], "shape": "rect"},
        {"label": "データフロー",  "color": ARCH["flow_ok"], "shape": "line"},
    ])


# ================================================================
#  メイン
# ================================================================

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

def execute_batch(slides_service, pres_id, requests, chunk_size=500):
    for i in range(0, len(requests), chunk_size):
        chunk = requests[i:i + chunk_size]
        slides_service.presentations().batchUpdate(
            presentationId=pres_id, body={"requests": chunk}
        ).execute()
        print(f"  Batch {i // chunk_size + 1}: {len(chunk)} requests sent")

def main():
    creds = get_credentials()
    slides_service = build("slides", "v1", credentials=creds)

    # プレゼンテーション作成
    pres = slides_service.presentations().create(body={
        "title": "ScalarDB クラウド構成図 (AWS / Azure / GCP)",
        "pageSize": {
            "width": {"magnitude": inches(10.0), "unit": "EMU"},
            "height": {"magnitude": inches(5.625), "unit": "EMU"},
        },
    }).execute()
    pres_id = pres["presentationId"]
    first_slide_id = pres["slides"][0]["objectId"]

    sb = SlideBuilder()
    sb.requests.append({"deleteObject": {"objectId": first_slide_id}})

    # 3 枚のスライドを構築
    build_aws_slide(sb)
    build_azure_slide(sb)
    build_gcp_slide(sb)

    # 一括実行
    print(f"\nBuilding {len(sb.slide_ids)} slides ({len(sb.requests)} requests)...")
    execute_batch(slides_service, pres_id, sb.requests)

    url = f"https://docs.google.com/presentation/d/{pres_id}/edit"
    print(f"\nDone! {len(sb.slide_ids)} slides created.")
    print(f"Open: {url}")
    return url


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
