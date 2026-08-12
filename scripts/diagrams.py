#!/usr/bin/env python3
"""Primitives for drawing diagrams on a slide.

Used together with `TemplateDeck` from `build_deck.py`. Draws diagrams that
placeholders alone can't express (comparison diagrams, flows, architecture,
bar charts, etc.), using the template's color scheme.

    import sys; sys.path.insert(0, "<skill>/scripts")
    import importlib.util
    spec = importlib.util.spec_from_file_location("bd", "<skill>/scripts/build_deck.py")
    bd = importlib.util.module_from_spec(spec); spec.loader.exec_module(bd)
    from diagrams import Canvas

    deck = bd.TemplateDeck.create(template, title="…")
    ref = deck.add_slide("TITLE_ONLY", title="…")
    d = Canvas(deck, ref["slideId"], template)
    d.box(0.5, 1.2, 2.6, 0.9, "Inner Loop", fill=d.P.primary, color="#FFFFFF")
    d.arrow(3.2, 1.65, 4.0, 1.65)

All coordinates are in inches. The origin is the top-left of the slide.

When connecting shapes to each other, don't write the coordinates by hand —
use one of the following instead. The Slides API doesn't error out even if
endpoints are misaligned, so hand-written coordinates are a common source of
mistakes.

    a = d.shape(1.0, 1.0, 1.6, 0.6, text="A")   # shape() returns an objectId
    b = d.shape(4.0, 2.0, 1.6, 0.6, text="B")
    d.connect(a, b)              # API connector. Bound to the shapes; follows them when moved
    d.link(a, b)                 # a line between centers, endpoints at the edge intersections
    d.line(..., free=True)       # axes, leader lines, etc. — lines that correctly don't touch anything

    for msg in d.audit_connectors():   # catch floating/buried lines at the coordinate stage
        print(msg)

This module is for diagrams that accurately represent structure. "Illustrative
diagrams" that depict a concept visually are handled by `illustrations`
(drawn with shapes), `icons` (brand icon assets), and `images` (AI-generated
or supplied images). All are exposed as Canvas methods.

    d.icon_flow(0.7, 1.2, 8.6, [("person", "利用者"), ("server", "API")])
    d.asset_icon_flow(0.7, 2.4, 8.6, [("job-seeker", "求職者"), ("interview", "面接")])
    d.pyramid(1.6, 2.4, 6.8, 2.4, ["経営指標", "業務指標", "システム指標"])
    d.image(0.6, 1.1, 4.2, 2.6, "assets/photo.png", fit="contain")
    d.ai_image(5.2, 1.1, 4.2, 2.6, "夜間に自動でビルドが回っている様子")
"""
from __future__ import annotations

import math
import os
import re
import sys
import unicodedata

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _auth  # noqa: E402
from _i18n import t, register  # noqa: E402
# Color utilities were moved to colors.py. Re-exported from here so existing
# imports like `from diagrams import lighten` keep working.
from colors import (  # noqa: E402,F401
    Palette, contrast_ratio, darken, lighten, mix, readable_on, relative_luminance,
)
from charts import ChartMixin  # noqa: E402
from cloud_icons import CloudIconMixin  # noqa: E402
from icons import IconLibraryMixin  # noqa: E402
from illustrations import IllustrationMixin  # noqa: E402
from images import ImageMixin  # noqa: E402
from patterns import PatternMixin  # noqa: E402
from pages import PageMixin  # noqa: E402
from events import EventMixin  # noqa: E402

register({
    "  warn: text inside a shape rotated {rotation} degrees will rotate with it "
    "(\"{head}\"). Draw the shape without text and overlay a label()":
        "  warn: 回転 {rotation}度 の図形に文字を入れています。"
        "文字も回ります（「{head}」）。"
        "図形は text 無しで描き、label() を重ねてください",
    "  warn: code_block contains characters outside the BMP (emoji etc.). "
    "Slides API text ranges are in UTF-16 units, so highlight ranges may shift":
        "  warn: code_block に BMP 外の文字（絵文字等）が含まれています。"
        "Slides API の文字範囲は UTF-16 単位のため、ハイライトの色範囲が"
        "ずれる可能性があります",
    "Shape has no recorded geometry: {id}": "座標が分からない図形です: {id}",
    "connect() can only join shapes drawn by this Canvas":
        "connect() は Canvas が描いた図形どうしにのみ使えます",
    "start point": "始点",
    "end point": "終点",
    "The {endpoint} of a connector does not touch any shape "
    "(nearest shape is {near:.2f}in away)":
        "コネクタの{endpoint}がどの図形にも接していません"
        "（最寄りの図形まで {near:.2f}in）",
    "The {endpoint} of a connector is buried inside a shape ({depth:.2f}in deep)":
        "コネクタの{endpoint}が図形の内部に埋まっています（{depth:.2f}in 食い込み）",
    "Text is hidden behind a shape drawn later ({area:.3f}in²): "
    "\"{text}\" is covered by \"{cover}\"":
        "文字が後から描いた図形に隠れています（{area:.3f}in²）:"
        "「{text}」を「{cover}」が覆っている",
    "Text labels collide ({area:.3f}in²): \"{a}\" and \"{b}\"":
        "文字どうしがぶつかっています（{area:.3f}in²）:「{a}」と「{b}」",
    "A line runs across text ({length:.2f}in inside): \"{text}\"":
        "線が文字の上を走っています（{length:.2f}in 分）:「{text}」",
    "{v:.2f}in past the left edge": "左に {v:.2f}in",
    "{v:.2f}in past the top edge": "上に {v:.2f}in",
    "{v:.2f}in past the right edge": "右に {v:.2f}in",
    "{v:.2f}in past the bottom edge": "下に {v:.2f}in",
    "A shape extends beyond the slide ({over}): \"{name}\"":
        "図形がスライドの外に出ています（{over}）:「{name}」",
    "A line endpoint is outside the slide: ({x:.2f}, {y:.2f})":
        "線の端点がスライドの外にあります: ({x:.2f}, {y:.2f})",
    "Too much text for the box (needs {need:.2f}in > box {h:.2f}in / {lines} lines): "
    "\"{text}\"":
        "枠に対して文字が多すぎます"
        "（必要 {need:.2f}in > 枠 {h:.2f}in / {lines}行）:「{text}」",
    "The wrapped last line keeps only {tail:.1f} characters ({per:.1f} per line): "
    "\"{text}\"":
        "折り返しの最終行に文字が {tail:.1f} 字しか残りません"
        "（1行 {per:.1f} 字）:「{text}」",
    "link() can only join shapes with known geometry":
        "link() は座標の分かる図形どうしにのみ使えます",
    "hbars: rows is empty": "hbars: rows が空です",
})


# ---------- Drawing ----------

# Random token to avoid object ID collisions across processes
import uuid  # noqa: E402
_RUN_TOKEN = uuid.uuid4().hex[:4]

# Default values immediately after createShape (confirmed empirically). Lets us
# skip sending updateShapeProperties / updateParagraphStyle calls that would
# just set the same values. batchUpdate's duration is roughly proportional to
# the number of requests, so this omission directly shortens generation time
# (about 19% saved on a real deck).
#
#   Other than TEXT_BOX ... fill/outline come from the theme (not NOT_RENDERED),
#                            contentAlignment=MIDDLE, paragraph alignment=CENTER
#   TEXT_BOX     ... both fill and outline are NOT_RENDERED, contentAlignment=TOP,
#                    paragraph alignment=START
_DEFAULT_VALIGN = {"TEXT_BOX": "TOP"}
_DEFAULT_ALIGN = {"TEXT_BOX": "START"}


def _default_align(kind: str) -> str:
    return _DEFAULT_ALIGN.get(kind, "CENTER")


class Canvas(IllustrationMixin, IconLibraryMixin, CloudIconMixin, ImageMixin,
             ChartMixin, PatternMixin, PageMixin, EventMixin):
    """Thin wrapper for drawing shapes on a single slide."""

    _seq = 0

    # Connector connection sites (4 points, common to all shapes)
    SITE_TOP, SITE_LEFT, SITE_BOTTOM, SITE_RIGHT = 0, 1, 2, 3

    def __init__(self, deck, slide_id: str, template: dict):
        self.deck = deck
        self.slide_id = slide_id
        self._template_colors = template.get("colors", {})
        self.P = Palette(self._template_colors)
        page = template.get("pageSize", {})
        self.page_w = page.get("widthInches", 10.0)
        self.page_h = page.get("heightInches", 5.625)
        # Actual coordinates of drawn shapes. Kept so connector endpoints can be
        # determined automatically.
        self.rects: dict[str, tuple] = {}
        # Record of drawn lines. Used by the audit to catch connectors whose
        # endpoints don't touch anything.
        self.connectors: list[dict] = []
        # Record of shapes that have text. Used to audit overlaps and text overflow.
        self.texts: dict[str, dict] = {}
        # Record of filled shapes. If drawn later, they can cover text underneath.
        self.solids: list[dict] = []
        self._seq = 0

    def _oid(self, prefix: str) -> str:
        Canvas._seq += 1
        # _RUN_TOKEN is a per-process random value. With a plain sequence number
        # alone, a second drawing pass from a different process onto an existing
        # deck would renumber starting from dg*0001 and collide.
        return f"dg{_RUN_TOKEN}{prefix}{Canvas._seq:04d}"

    def _elem_props(self, x, y, w, h, rotation: float = 0.0,
                    flip_x: bool = False, flip_y: bool = False):
        """Element position and size. rotation is in degrees; rotates in place around the center.

        The Slides API has no rotation-angle field, so it's expressed as an affine transform.
            x' = scaleX·x + shearX·y + translateX
            y' = shearY·x + scaleY·y + translateY

        flip_x / flip_y produce a mirror image (negative scale). Needed for
        left-right asymmetric shapes like RIGHT_TRIANGLE, so a right triangle
        facing any of the 4 corners can be made. Not combined with rotation.
        """
        if (flip_x or flip_y) and not rotation:
            transform = {
                "scaleX": -1 if flip_x else 1,
                "scaleY": -1 if flip_y else 1,
                "translateX": _auth.inches(x + (w if flip_x else 0)),
                "translateY": _auth.inches(y + (h if flip_y else 0)),
                "unit": "EMU",
            }
        elif rotation:
            th = math.radians(rotation)
            cos, sin = math.cos(th), math.sin(th)
            cx, cy = x + w / 2, y + h / 2
            transform = {
                "scaleX": cos, "scaleY": cos, "shearX": -sin, "shearY": sin,
                "translateX": _auth.inches(cx - (cos * (w / 2) - sin * (h / 2))),
                "translateY": _auth.inches(cy - (sin * (w / 2) + cos * (h / 2))),
                "unit": "EMU",
            }
        else:
            transform = {
                "scaleX": 1, "scaleY": 1,
                "translateX": _auth.inches(x), "translateY": _auth.inches(y),
                "unit": "EMU",
            }
        return {
            "pageObjectId": self.slide_id,
            "size": {
                "width": {"magnitude": _auth.inches(w), "unit": "EMU"},
                "height": {"magnitude": _auth.inches(h), "unit": "EMU"},
            },
            "transform": transform,
        }

    @staticmethod
    def _aabb(x, y, w, h, rotation: float = 0.0):
        """Bounding box after rotation. Use this for hit testing and audits."""
        if not rotation:
            return (x, y, w, h)
        th = math.radians(rotation)
        cos, sin = abs(math.cos(th)), abs(math.sin(th))
        nw, nh = w * cos + h * sin, w * sin + h * cos
        return (x + (w - nw) / 2, y + (h - nh) / 2, nw, nh)

    def _solid(self, hex_color, alpha: float = 1.0):
        return {"solidFill": {"color": {"rgbColor": _auth.hex_to_rgb(hex_color)},
                              "alpha": alpha}}

    # ---- Shapes ----

    def shape(self, x, y, w, h, *, kind="RECTANGLE", fill=None, stroke=None,
              stroke_weight=1.0, dash="SOLID", text=None, color=None, size=11,
              bold=False, align="CENTER", valign="MIDDLE", line_spacing=None,
              alpha: float = 1.0, rotation: float = 0.0,
              flip_x: bool = False, flip_y: bool = False,
              font: str | None = None) -> str:
        """Draw a shape and return its objectId. fill=None means no fill.

        dash is the outline's line style (SOLID / DASH / DOT / DASH_DOT, …). Use a
        dashed rectangle for shapes indicating an "enclosure," like a cloud zone
        boundary.

        font is the font family (defaults to Noto Sans JP). For code blocks, specify
        a monospace font such as "Roboto Mono".

        alpha is the fill opacity (0-1). Used for diagrams that show overlap, like
        Venn diagrams.
        rotation is in degrees; rotates in place around the center. Rotated shapes
        are recorded by their bounding box, so audit (audit_*) checks become somewhat
        conservative.

        **Never put text in a rotated shape.** The text rotates along with it, so at
        180 degrees it comes out upside down, and at 45 degrees it comes out at an
        angle. When using a flipped trapezoid or pentagon, draw the shape without
        text and overlay the text separately with label() (the only exception being
        an intentionally vertical use like label(rotation=270)).
        """
        if text and rotation % 360 not in (0, 90, 270):
            print(t("  warn: text inside a shape rotated {rotation} degrees will "
                    "rotate with it (\"{head}\"). Draw the shape without text and "
                    "overlay a label()", rotation=rotation, head=str(text)[:12]),
                  file=sys.stderr)
        oid = self._oid("s")
        reqs = [{"createShape": {
            "objectId": oid, "shapeType": kind,
            "elementProperties": self._elem_props(
                x, y, w, h, rotation, flip_x, flip_y)}}]

        props, fields = {}, []
        if fill is None:
            props["shapeBackgroundFill"] = {"propertyState": "NOT_RENDERED"}
            fields.append("shapeBackgroundFill")
        else:
            props["shapeBackgroundFill"] = self._solid(fill, alpha)
            fields.append("shapeBackgroundFill.solidFill")
        if stroke is None:
            props["outline"] = {"propertyState": "NOT_RENDERED"}
            fields.append("outline")
        else:
            props["outline"] = {
                "outlineFill": self._solid(stroke),
                "weight": {"magnitude": int(stroke_weight * _auth.EMU_PER_PT), "unit": "EMU"},
                "dashStyle": dash,
            }
            fields.append("outline")
        props["contentAlignment"] = valign
        fields.append("contentAlignment")
        # A plain TEXT_BOX defaults to "no fill, no outline, top-aligned," so a
        # request that just specifies the same thing can be skipped entirely (this
        # covers most calls to label())
        if not (kind == "TEXT_BOX" and fill is None and stroke is None
                and valign == _DEFAULT_VALIGN["TEXT_BOX"]):
            reqs.append({"updateShapeProperties": {
                "objectId": oid, "shapeProperties": props,
                "fields": ",".join(fields)}})

        if text:
            reqs.append({"insertText": {"objectId": oid, "text": text}})
            fg = color or (readable_on(fill) if fill else self.P.text)
            reqs.append({"updateTextStyle": {
                "objectId": oid,
                "style": {
                    "fontFamily": font or "Noto Sans JP",
                    "fontSize": {"magnitude": size, "unit": "PT"},
                    "bold": bold,
                    "foregroundColor": {"opaqueColor": {"rgbColor": _auth.hex_to_rgb(fg)}},
                },
                "textRange": {"type": "ALL"},
                "fields": "fontFamily,fontSize,bold,foregroundColor",
            }})
            pstyle, pfields = {"alignment": align}, ["alignment"]
            if line_spacing:
                pstyle["lineSpacing"] = line_spacing
                pfields.append("lineSpacing")
            # If no line spacing was given and alignment is already the default,
            # the paragraph style doesn't need to be touched
            if line_spacing or align != _default_align(kind):
                reqs.append({"updateParagraphStyle": {
                    "objectId": oid, "style": pstyle,
                    "textRange": {"type": "ALL"}, "fields": ",".join(pfields)}})

        self.deck.requests += reqs
        self._seq += 1
        box = self._aabb(x, y, w, h, rotation)
        self.rects[oid] = (*box, kind)
        # A semi-transparent fill lets text underneath show through, so it isn't
        # treated as "hiding" it
        if fill is not None and alpha >= 0.9:
            self.solids.append({"rect": box, "seq": self._seq,
                                "name": (text or kind).replace("\n", " ")[:20]})
        if text:
            # Text inside a rotated box has its line-flow direction changed, so
            # judging by the bounding box isn't reliable. For 90/270 degrees,
            # evaluate with width and height swapped
            trect = (box[0], box[1], h, w) if rotation % 180 == 90 else box
            self.texts[oid] = {"rect": trect, "kind": kind, "text": text,
                               "size": size, "ls": line_spacing or 100,
                               "fill": fill is not None and alpha >= 0.9,
                               "align": align, "valign": valign, "seq": self._seq}
        return oid

    def box(self, x, y, w, h, text=None, **kw) -> str:
        """Rounded box. Defaults to a pale fill with a primary-colored outline."""
        kw.setdefault("kind", "ROUND_RECTANGLE")
        kw.setdefault("fill", self.P.surface)
        kw.setdefault("stroke", self.P.border)
        return self.shape(x, y, w, h, text=text, **kw)

    def solid(self, x, y, w, h, text=None, **kw) -> str:
        """Filled box (for headings)."""
        kw.setdefault("kind", "ROUND_RECTANGLE")
        kw.setdefault("fill", self.P.primary)
        kw.setdefault("bold", True)
        return self.shape(x, y, w, h, text=text, **kw)

    def label(self, x, y, w, h, text, *, size=10, color=None, bold=False,
              align="START", valign="TOP", line_spacing=None, rotation=0,
              font=None) -> str:
        """Text with no outline or fill. rotation=270 can be used for things like a vertical axis label."""
        return self.shape(x, y, w, h, kind="TEXT_BOX", fill=None, stroke=None,
                          text=text, size=size, color=color or self.P.text, bold=bold,
                          align=align, valign=valign, line_spacing=line_spacing,
                          rotation=rotation, font=font)

    def band(self, x, y, w, h, *, fill=None, kind="ROUND_RECTANGLE",
             stroke=None) -> str:
        """Background band. Used to group parts of a diagram.

        `kind="RECTANGLE"` gives a square-cornered backdrop. Use it in cases where
        rounded corners wouldn't match the original template artwork, such as a
        white card laid under a cover page or section divider.
        """
        return self.shape(x, y, w, h, kind=kind,
                          fill=fill or self.P.surfaceAlt, stroke=stroke)

    # ---- Code blocks ----

    # VS Code Dark+ style. Satisfies a contrast ratio of 4.5:1 or higher against the dark CODE_BG background
    CODE_BG, CODE_FG = "#1F2933", "#E8ECF1"
    _CODE_STYLES = {
        "comment": "#7DBA7D",   # comment (green)
        "string":  "#E2A37E",   # string (orange)
        "keyword": "#6FB6EA",   # keyword (blue)
        "number":  "#B5CEA8",   # number (light green)
        "type":    "#56C9B4",   # type/class (teal)
        "func":    "#DCDCAA",   # function/method (yellow)
        "anno":    "#D19FD3",   # annotation/directive (purple)
        "prop":    "#9CDCFE",   # property name/flag (light blue)
    }
    # Per-language lexical rules. Earlier entries take priority (comments and strings are placed first)
    _CODE_RULES = {
        "java": [
            ("comment", r"//[^\n]*"),
            ("string", r'"(?:[^"\\\n]|\\.)*"'),
            ("anno", r"@\w+"),
            ("keyword", r"\b(?:public|class|extends|return|try|catch|new|"
                        r"if|else|null|int|long|void|static|final|import)\b"),
            ("number", r"\b\d[\d_.]*[FLfl]?\b"),
            ("type", r"\b[A-Z][A-Za-z0-9_]*\b"),
            ("func", r"\b[a-z]\w*(?=\()"),
        ],
        "graphql": [
            ("comment", r"#[^\n]*"),
            ("string", r'"(?:[^"\\\n]|\\.)*"'),
            ("anno", r"@\w+"),
            ("keyword", r"\b(?:query|mutation|true|false)\b"),
            ("number", r"\b\d+\b"),
            ("prop", r"\b\w+(?=\s*:)"),
        ],
        "json": [
            ("prop", r'"(?:[^"\\\n]|\\.)*"(?=\s*:)'),
            ("string", r'"(?:[^"\\\n]|\\.)*"'),
            ("keyword", r"\b(?:true|false|null)\b"),
            ("number", r"-?\b\d[\d.]*\b"),
        ],
        # Shell. Leave the contents of double quotes untouched so SQL keywords can
        # still be picked up (for TableStore's --statement "CREATE TABLE …")
        "bash": [
            ("comment", r"#[^\n]*"),
            ("string", r"'[^'\n]*'"),
            ("prop", r"(?<!\w)--[\w-]+"),
            ("func", r"(?<=\$ )[\w./-]+|\bhistory(?=\()"),
            ("keyword", r"\b(?:CREATE|TABLE|INSERT|INTO|VALUES|SELECT|FROM|"
                        r"JOIN|ON|WHERE|UPDATE|SET|PRIMARY|KEY|STRING|LIMIT)\b"),
        ],
    }

    @classmethod
    def _highlight(cls, code: str, lang: str):
        """List of (start, end, hex). Indices match UTF-16 units (code containing
        characters outside the BMP is not expected)."""
        rules = cls._CODE_RULES.get(lang)
        if not rules:
            return []
        if any(ord(ch) > 0xFFFF for ch in code):
            print(t("  warn: code_block contains characters outside the BMP "
                    "(emoji etc.). Slides API text ranges are in UTF-16 units, "
                    "so highlight ranges may shift"), file=sys.stderr)
        pattern = "|".join(f"(?P<{name}_{i}>{rx})"
                           for i, (name, rx) in enumerate(rules))
        spans = []
        for m in re.finditer(pattern, code):
            kind = m.lastgroup.rsplit("_", 1)[0]
            spans.append((m.start(), m.end(), cls._CODE_STYLES[kind]))
        return spans

    def code_block(self, x, y, w, h, code, *, lang="java", size=7.5,
                   line_spacing=104, bg=None, fg=None,
                   font="Roboto Mono") -> str:
        """Code panel with syntax highlighting.

        lang is a key into _CODE_RULES (java / graphql / json / bash). Unknown
        languages are drawn in a single color. Estimate height using the effective
        line height (fontSize × lineSpacing × about 1.45).
        """
        # Keep the corners square (rounded corners would visually eat into the
        # indentation of the first and last lines, and wouldn't match the
        # square-corner convention used by other cards)
        oid = self.shape(x, y, w, h, kind="RECTANGLE",
                         fill=bg or self.CODE_BG, stroke=None, text=code,
                         size=size, color=fg or self.CODE_FG, align="START",
                         valign="MIDDLE", line_spacing=line_spacing, font=font)
        for start, end, color in self._highlight(code, lang):
            self.deck.requests.append({"updateTextStyle": {
                "objectId": oid,
                "style": {"foregroundColor": {
                    "opaqueColor": {"rgbColor": _auth.hex_to_rgb(color)}}},
                "textRange": {"type": "FIXED_RANGE",
                              "startIndex": start, "endIndex": end},
                "fields": "foregroundColor"}})
        return oid

    # ---- Lines and arrows ----

    def line(self, x1, y1, x2, y2, *, color=None, weight=1.25,
             end_arrow="NONE", start_arrow="NONE", dashed=False,
             free=False, _anchored=False) -> str:
        """Draw a line by specifying coordinates directly.

        To connect two shapes, use connect() (API-level connection) or link()
        (snaps endpoints to the edge). This method won't complain even if the
        endpoints are offset from the shapes.
        free=True explicitly marks "a line that correctly doesn't touch any shape"
        (axes, dividers, etc.).
        """
        oid = self._oid("l")
        # A STRAIGHT line is drawn from the element rectangle's "top-left to
        # bottom-right." To represent an arbitrary direction, normalize to the
        # bounding box and then flip per axis. Without the flip, the arrowhead
        # ends up on the opposite side from what was intended.
        x, y = min(x1, x2), min(y1, y2)
        w, h = max(abs(x2 - x1), 0.001), max(abs(y2 - y1), 0.001)
        sx = -1 if x2 < x1 else 1
        sy = -1 if y2 < y1 else 1
        props = self._elem_props(x, y, w, h)
        props["transform"] = {
            "scaleX": sx, "scaleY": sy,
            "translateX": _auth.inches(x + (w if sx < 0 else 0)),
            "translateY": _auth.inches(y + (h if sy < 0 else 0)),
            "unit": "EMU",
        }
        self.deck.requests += [
            {"createLine": {"objectId": oid, "lineCategory": "STRAIGHT",
                            "elementProperties": props}},
            {"updateLineProperties": {
                "objectId": oid,
                "lineProperties": {
                    "lineFill": self._solid(color or self.P.muted),
                    "weight": {"magnitude": int(weight * _auth.EMU_PER_PT), "unit": "EMU"},
                    "dashStyle": "DASH" if dashed else "SOLID",
                    "startArrow": start_arrow,
                    "endArrow": end_arrow,
                },
                "fields": "lineFill,weight,dashStyle,startArrow,endArrow",
            }},
        ]
        self._seq += 1
        self.connectors.append({
            "oid": oid, "p1": (x1, y1), "p2": (x2, y2),
            "free": free or _anchored, "anchored": _anchored,
            "seq": self._seq,
        })
        return oid

    def arrow(self, x1, y1, x2, y2, **kw) -> str:
        kw.setdefault("end_arrow", "FILL_ARROW")
        return self.line(x1, y1, x2, y2, **kw)

    # ---- Connectors that attach to shapes ----

    @staticmethod
    def _center(rect):
        x, y, w, h = rect[:4]
        return x + w / 2, y + h / 2

    @classmethod
    def _site_point(cls, rect, site):
        x, y, w, h = rect[:4]
        return {
            cls.SITE_TOP: (x + w / 2, y),
            cls.SITE_LEFT: (x, y + h / 2),
            cls.SITE_BOTTOM: (x + w / 2, y + h),
            cls.SITE_RIGHT: (x + w, y + h / 2),
        }[site]

    @classmethod
    def _facing_site(cls, src, dst):
        """Return the connection site on the side facing dst, as seen from src."""
        ax, ay = cls._center(src)
        bx, by = cls._center(dst)
        dx, dy = bx - ax, by - ay
        if abs(dx) >= abs(dy):
            return cls.SITE_RIGHT if dx > 0 else cls.SITE_LEFT
        return cls.SITE_BOTTOM if dy > 0 else cls.SITE_TOP

    def edge_point(self, rect_or_id, toward, *, gap=0.0):
        """Return the point where a line from the rectangle's center toward
        toward(=(x, y)) crosses the edge.

        If gap is given, offset outward by that amount (so the arrowhead doesn't
        dig into the outline).
        """
        rect = self.rects.get(rect_or_id) if isinstance(rect_or_id, str) else rect_or_id
        if rect is None:
            raise ValueError(t("Shape has no recorded geometry: {id}", id=rect_or_id))
        cx, cy = self._center(rect)
        w, h = rect[2], rect[3]
        dx, dy = toward[0] - cx, toward[1] - cy
        if dx == 0 and dy == 0:
            return cx, cy
        sx = (w / 2) / abs(dx) if dx else float("inf")
        sy = (h / 2) / abs(dy) if dy else float("inf")
        s = min(sx, sy)
        px, py = cx + dx * s, cy + dy * s
        if gap:
            L = math.hypot(dx, dy)
            px += dx / L * gap
            py += dy / L * gap
        return px, py

    def connect(self, src, dst, *, color=None, weight=1.4, dashed=False,
                end_arrow="FILL_ARROW", start_arrow="NONE",
                category="STRAIGHT", start_site=None, end_site=None) -> str:
        """Connect two shapes **as an API-level connector**.

        src / dst are objectIds returned by shape() or similar. Because they're
        bound to the shapes on the Google Slides side, the line follows if a shape
        is moved later. The connection site is chosen automatically from the
        relative position (0=top 1=left 2=bottom 3=right).

        category="BENT" produces an elbow (right-angle bend). For one-to-many
        fan-out, BENT routes are less likely to cross each other.
        """
        ra, rb = self.rects.get(src), self.rects.get(dst)
        if ra is None or rb is None:
            raise ValueError(t("connect() can only join shapes drawn by this Canvas"))
        s_site = self._facing_site(ra, rb) if start_site is None else start_site
        e_site = self._facing_site(rb, ra) if end_site is None else end_site
        p1 = self._site_point(ra, s_site)
        p2 = self._site_point(rb, e_site)

        oid = self._oid("c")
        # Setting a connection lets the API side determine the position, but in
        # case the connection doesn't take effect, also create the initial shape
        # at the actual coordinates between the sites so the line doesn't end up
        # stuck at the origin
        x, y = min(p1[0], p2[0]), min(p1[1], p2[1])
        w = max(abs(p2[0] - p1[0]), 0.001)
        h = max(abs(p2[1] - p1[1]), 0.001)
        props = self._elem_props(x, y, w, h)
        props["transform"] = {
            "scaleX": -1 if p2[0] < p1[0] else 1,
            "scaleY": -1 if p2[1] < p1[1] else 1,
            "translateX": _auth.inches(x + (w if p2[0] < p1[0] else 0)),
            "translateY": _auth.inches(y + (h if p2[1] < p1[1] else 0)),
            "unit": "EMU",
        }
        self.deck.requests += [
            {"createLine": {"objectId": oid, "lineCategory": category,
                            "elementProperties": props}},
            {"updateLineProperties": {
                "objectId": oid,
                "lineProperties": {
                    "startConnection": {"connectedObjectId": src,
                                        "connectionSiteIndex": s_site},
                    "endConnection": {"connectedObjectId": dst,
                                      "connectionSiteIndex": e_site},
                    "lineFill": self._solid(color or self.P.primary),
                    "weight": {"magnitude": int(weight * _auth.EMU_PER_PT), "unit": "EMU"},
                    "dashStyle": "DASH" if dashed else "SOLID",
                    "startArrow": start_arrow,
                    "endArrow": end_arrow,
                },
                "fields": ("startConnection,endConnection,lineFill,weight,"
                           "dashStyle,startArrow,endArrow"),
            }},
        ]
        self._seq += 1
        self.connectors.append({"oid": oid, "p1": p1, "p2": p2,
                                "free": True, "anchored": True,
                                "seq": self._seq})
        return oid

    # ---- Connector self-checks ----

    # Judgment thresholds (inches)
    CONN_REACH = 0.22       # farther than this from any shape counts as "not connected"
    CONN_BURY = 0.06        # deeper than this inside a shape counts as "buried"
    CONN_CONTAINER = 6.0    # shapes with area beyond this are treated as containers and excluded from the check

    @staticmethod
    def _dist_to_rect(px, py, rect):
        """Signed distance from a point to the rectangle's boundary. Negative means inside (the amount of overlap)."""
        x, y, w, h = rect[:4]
        dx = max(x - px, 0.0, px - (x + w))
        dy = max(y - py, 0.0, py - (y + h))
        if dx > 0 or dy > 0:
            return (dx * dx + dy * dy) ** 0.5
        return -min(px - x, (x + w) - px, py - y, (y + h) - py)

    def audit_connectors(self) -> list[str]:
        """Enumerate connectors whose endpoints don't touch a shape. Returns an
        empty list if there's no problem.

        The Slides API just takes line coordinates as given and doesn't validate
        their position relative to shapes. So "the arrow is floating" or "it's
        buried in the outline" wouldn't be noticed until the deck is generated and
        the thumbnail is checked. This catches it at the coordinate stage instead.

        Excluded from the check:
          - lines marked free=True (axes, tick marks, leader lines, etc., where not
            touching is correct)
          - lines drawn with connect() / link() (touch a shape by definition)
          - text boxes (no visible boundary)
          - shapes with a large area (containers like zones; it's normal for an
            arrow to pass through them)
        """
        targets = [r for r in self.rects.values()
                   if r[4] != "TEXT_BOX" and r[2] * r[3] <= self.CONN_CONTAINER]
        if not targets:
            return []
        out = []
        for conn in self.connectors:
            if conn["free"]:
                continue
            for name, p in ((t("start point"), conn["p1"]),
                            (t("end point"), conn["p2"])):
                near = min((self._dist_to_rect(p[0], p[1], r) for r in targets),
                           key=abs)
                if near > self.CONN_REACH:
                    out.append(t("The {endpoint} of a connector does not touch any "
                                 "shape (nearest shape is {near:.2f}in away)",
                                 endpoint=name, near=near))
                elif near < -self.CONN_BURY:
                    out.append(t("The {endpoint} of a connector is buried inside a "
                                 "shape ({depth:.2f}in deep)",
                                 endpoint=name, depth=-near))
        return out

    # Thresholds for overlap / text-overflow checks
    OVERLAP_MIN = 0.010     # report if the overlapping area (in^2) is at least this much
    OVERLAP_RATIO = 0.06    # lower bound on the overlap ratio relative to the smaller area
    # Length (in) of a line running through text. It's normal for an arrowhead's
    # tip to graze the edge of a character, so only catch lines that "run through"
    # more than this
    LINE_CROSS_MIN = 0.06
    TEXT_SLACK = 0.04       # allowance (in) against the text's required height
    LINE_EM = 1.45          # Noto Sans JP line height (multiplier relative to font size)

    @staticmethod
    def _em(t):
        return sum(1.0 if unicodedata.east_asian_width(c) in "WFA" else 0.5 for c in t)

    @staticmethod
    def _overlap_area(a, b):
        ox = min(a[0] + a[2], b[0] + b[2]) - max(a[0], b[0])
        oy = min(a[1] + a[3], b[1] + b[3]) - max(a[1], b[1])
        return (ox * oy) if (ox > 0 and oy > 0) else 0.0

    @staticmethod
    def _segment_in_rect(p1, p2, rect) -> float:
        """Return the length (in) of the segment that lies inside the rectangle.
        0 if it merely touches.

        Clips to the parameter t range using Liang-Barsky, and measures the length
        of the remaining interval.
        """
        x, y, w, h = rect
        dx, dy = p2[0] - p1[0], p2[1] - p1[1]
        t0, t1 = 0.0, 1.0
        for p, q in ((-dx, p1[0] - x), (dx, x + w - p1[0]),
                     (-dy, p1[1] - y), (dy, y + h - p1[1])):
            if p == 0:
                if q < 0:
                    return 0.0     # parallel to the edge, running outside
                continue
            r = q / p
            if p < 0:
                if r > t1:
                    return 0.0
                t0 = max(t0, r)
            else:
                if r < t0:
                    return 0.0
                t1 = min(t1, r)
        if t1 <= t0:
            return 0.0
        return (t1 - t0) * math.hypot(dx, dy)

    @staticmethod
    def _contains(outer, inner, slack=0.02):
        return (inner[0] >= outer[0] - slack and inner[1] >= outer[1] - slack
                and inner[0] + inner[2] <= outer[0] + outer[2] + slack
                and inner[1] + inner[3] <= outer[1] + outer[3] + slack)

    # Slides' default text-box inset (0.1in on each side). Dividing by the width
    # without subtracting this overestimates "characters per line" by 1-2
    # characters, so the check passes through text that actually wraps.
    #
    # The vertical inset (0.05in) is **not** subtracted. Slides draws text that
    # overflows the box vertically without clipping it, so subtracting it would
    # make single-line labels false-positive across the board (measured: a single
    # line at 9.5pt renders fine in a 0.24in box).
    TEXT_INSET_X = 0.10

    def _text_lines(self, m):
        """Return the number of lines accounting for wrapping, and the number of characters that fit per line."""
        w = max(m["rect"][2] - self.TEXT_INSET_X * 2, 0.01)
        per = (w * 72.0) / m["size"]
        if per <= 0:
            return 1, per
        n = 0
        for ln in m["text"].split("\n"):
            e = self._em(ln)
            n += max(1, int(e / per) + (1 if e % per else 0))
        return n, per

    def _ink_rect(self, m):
        """The rectangle actually occupied by the text (or the fill).

        A filled shape is opaque across its whole rectangle. An unfilled label only
        looks at the range the text actually occupies, since even with a wide box,
        short centered text won't collide with its neighbor.
        """
        if m["fill"]:
            return tuple(m["rect"])
        return self._glyph_rect(m)

    def _glyph_rect(self, m):
        """The rectangle the characters themselves occupy. Doesn't look at fill.

        Even for a filled shape, whether a line crossing through it **overlaps the
        text** is determined by the character positions, not the box. _ink_rect
        treats a filled shape as an opaque panel (needed for the hidden-text
        check), so use this one instead for checks that only need the character
        range.
        """
        x, y, w, h = m["rect"]
        lines, per = self._text_lines(m)
        longest = max((self._em(l) for l in m["text"].split("\n")), default=0)
        tw = min(w, min(longest, per) * m["size"] / 72.0 + 0.10)
        th = min(h, lines * m["size"] * self.LINE_EM * (m["ls"] / 100.0) / 72.0)
        if m["align"] == "CENTER":
            x += (w - tw) / 2
        elif m["align"] == "END":
            x += w - tw
        if m["valign"] == "MIDDLE":
            y += (h - th) / 2
        elif m["valign"] in ("BOTTOM", "END"):
            y += h - th
        return (x, y, tw, th)

    def audit_overlaps(self) -> list[str]:
        """Report places where text is hidden or colliding.

        Slides draws elements created later on top. So:

        1. **Hidden** ... an opaque shape drawn after some text covers that text.
           The typical case is a banner or zone that creeps into the block right
           before it.
        2. **Collision** ... unfilled labels colliding with each other, judged by
           the actual character range.
        3. **A line piercing text** ... a connector or arrow running across text.
           Lines have no draw order (they're not recorded as filled shapes) and
           fall under neither 1 nor 2, so they need to be checked separately.

        Judged by "the range the text actually occupies" rather than the box, so a
        label with generous padding that only slightly overlaps its neighbor isn't
        reported.
        """
        items = sorted(self.texts.values(), key=lambda m: m["seq"])
        out, seen = [], set()

        def record(msg, key):
            if key not in seen:
                seen.add(key)
                out.append(msg)

        # 1. A filled shape drawn later covers the text
        for a in items:
            ra = self._ink_rect(a)
            ta = a["text"].replace("\n", " ")[:20]
            for sol in self.solids:
                if sol["seq"] <= a["seq"]:
                    continue
                area = self._overlap_area(ra, sol["rect"])
                if area < self.OVERLAP_MIN:
                    continue
                if area / max(ra[2] * ra[3], 1e-9) < self.OVERLAP_RATIO:
                    continue
                record(t("Text is hidden behind a shape drawn later ({area:.3f}in²): "
                         "\"{text}\" is covered by \"{cover}\"",
                         area=area, text=ta, cover=sol["name"]),
                       ("hide", ta, sol["name"]))

        # 2. Collision between unfilled labels
        labels = [m for m in items if not m["fill"]]
        for i, a in enumerate(labels):
            ra = self._ink_rect(a)
            for b in labels[i + 1:]:
                rb = self._ink_rect(b)
                area = self._overlap_area(ra, rb)
                if area < self.OVERLAP_MIN:
                    continue
                small = min(ra[2] * ra[3], rb[2] * rb[3])
                if small <= 0 or area / small < self.OVERLAP_RATIO:
                    continue
                ta = a["text"].replace("\n", " ")[:20]
                tb = b["text"].replace("\n", " ")[:20]
                record(t("Text labels collide ({area:.3f}in²): \"{a}\" and \"{b}\"",
                         area=area, a=ta, b=tb), ("hit", *sorted((ta, tb))))

        # 3. Lines/arrows running across text
        #
        # It's not uncommon to draw a line first and then place a filled shape on
        # top of it (hub() extends lines from the center to each node's center, and
        # then overlays the node boxes afterward). In this case, the line is hidden
        # under the fill and isn't a defect. If an opaque shape drawn after the
        # line covers that text, don't report it.
        for a in items:
            ga = self._glyph_rect(a)
            if ga[2] <= 0 or ga[3] <= 0:
                continue
            ta = a["text"].replace("\n", " ")[:20]
            for conn in self.connectors:
                inside = self._segment_in_rect(conn["p1"], conn["p2"], ga)
                if inside < self.LINE_CROSS_MIN:
                    continue
                if any(sol["seq"] > conn["seq"] and self._contains(sol["rect"], ga)
                       for sol in self.solids):
                    continue
                record(t("A line runs across text ({length:.2f}in inside): "
                         "\"{text}\"", length=inside, text=ta),
                       ("cross", ta, conn["oid"]))
        return out

    BOUNDS_SLACK = 0.02     # allow overflow up to this amount (rounding error)

    def audit_bounds(self) -> list[str]:
        """Report shapes/lines that go outside the slide.

        Diagram components compute their own coordinates from a given bounding box,
        so even if the box itself fits, the contents inside it can poke outside
        (a ratio miscalculation). This can only be caught by checking per shape.
        """
        out = []
        s = self.BOUNDS_SLACK
        for oid, r in self.rects.items():
            x, y, w, h, kind = r
            over = []
            if x < -s:
                over.append(t("{v:.2f}in past the left edge", v=-x))
            if y < -s:
                over.append(t("{v:.2f}in past the top edge", v=-y))
            if x + w > self.page_w + s:
                over.append(t("{v:.2f}in past the right edge", v=x + w - self.page_w))
            if y + h > self.page_h + s:
                over.append(t("{v:.2f}in past the bottom edge", v=y + h - self.page_h))
            if over:
                name = self.texts.get(oid, {}).get("text", kind)
                out.append(t("A shape extends beyond the slide ({over}): \"{name}\"",
                             over="/".join(over),
                             name=str(name).replace(chr(10), " ")[:20]))
        for conn in self.connectors:
            for p in (conn["p1"], conn["p2"]):
                if not (-s <= p[0] <= self.page_w + s and -s <= p[1] <= self.page_h + s):
                    out.append(t("A line endpoint is outside the slide: "
                                 "({x:.2f}, {y:.2f})", x=p[0], y=p[1]))
        return out

    ORPHAN_EM = 1.0     # if the wrapped last line is at or below this, treat it as "a single stray character"

    def audit_text_fit(self) -> list[str]:
        """Report text that doesn't fit its box, and ugly line wraps.

        1. **Overflow** ... estimate characters per line as "width(pt) ÷
           fontSize(pt)", derive the required height from the number of lines
           needed, and compare it to the declared height. Overflowing text appears
           clipped.
        2. **Orphan line** ... a case where wrapping leaves only 1 character on the
           last line. A break like "...Deplo / y" fits within the box but is
           clearly ugly. Widening the box by a few mm, or tightening the wording,
           fixes it.
        """
        out = []
        for m in self.texts.values():
            h = m["rect"][3]
            lines, per = self._text_lines(m)
            if per <= 0:
                continue
            need = lines * m["size"] * self.LINE_EM * (m["ls"] / 100.0) / 72.0
            if need > h + self.TEXT_SLACK:
                txt = m["text"].replace("\n", " ")[:22]
                out.append(t("Too much text for the box (needs {need:.2f}in > box "
                             "{h:.2f}in / {lines} lines): \"{text}\"",
                             need=need, h=h, lines=lines, text=txt))
                continue
            for ln in m["text"].split("\n"):
                e = self._em(ln)
                if e <= per:
                    continue
                tail = e % per
                if 0 < tail <= self.ORPHAN_EM:
                    out.append(t("The wrapped last line keeps only {tail:.1f} "
                                 "characters ({per:.1f} per line): \"{text}\"",
                                 tail=tail, per=per, text=ln[:22]))
        return out

    def link(self, src, dst, *, gap=0.04, color=None, weight=1.4, dashed=False,
             end_arrow="FILL_ARROW", start_arrow="NONE") -> str:
        """Connect two shapes with a straight line **whose endpoints sit exactly
        on the edges**.

        Computes the point where a line between the centers crosses each edge, so
        even at a diagonal, the endpoints touch the shapes exactly. Use this when
        you don't want to snap to the API's connection sites (the 4 points top,
        bottom, left, right).
        """
        ra = self.rects.get(src) if isinstance(src, str) else src
        rb = self.rects.get(dst) if isinstance(dst, str) else dst
        if ra is None or rb is None:
            raise ValueError(t("link() can only join shapes with known geometry"))
        p1 = self.edge_point(ra, self._center(rb), gap=gap)
        p2 = self.edge_point(rb, self._center(ra), gap=gap)
        return self.line(p1[0], p1[1], p2[0], p2[1], color=color, weight=weight,
                         dashed=dashed, end_arrow=end_arrow,
                         start_arrow=start_arrow, _anchored=True)

    def arrow_shape(self, x, y, w, h, *, fill=None, text=None, **kw) -> str:
        """Thick arrow (for things like a process flow)."""
        return self.shape(x, y, w, h, kind="RIGHT_ARROW",
                          fill=fill or lighten(self.P.primary, 0.75), stroke=None,
                          text=text, **kw)

    # ---- Composite parts ----

    def cards(self, x, y, w, h, items, *, gap=0.22, fill=None, stroke=None,
              title_size=12, body_size=10, accent=None):
        """Side-by-side cards. items is a list of (heading, body) pairs. Returns
        the bottom edge y.

        Corners are not rounded (RECTANGLE), because a straight accent bar is
        overlaid at the top edge. A rounded corner and the straight bar's edge
        wouldn't line up and would look uneven.
        """
        n = len(items)
        cw = (w - gap * (n - 1)) / n
        out = []
        for i, item in enumerate(items):
            head, body = (item if isinstance(item, (tuple, list)) else (item, None))
            cx = x + i * (cw + gap)
            out.append(self.shape(cx, y, cw, h, kind="RECTANGLE",
                                  fill=fill or self.P.surface,
                                  stroke=stroke or self.P.border))
            bar_c = accent[i] if isinstance(accent, (list, tuple)) else (accent or self.P.primary)
            self.shape(cx, y, cw, 0.06, kind="RECTANGLE", fill=bar_c, stroke=None)
            self.label(cx + 0.14, y + 0.16, cw - 0.28, 0.34, head,
                       size=title_size, bold=True, align="START", color=self.P.text)
            if body:
                # Body text starts right below the heading. Subtracting a fixed
                # 0.7 would nearly crush the body and clip its text when h is small
                self.label(cx + 0.14, y + 0.50, cw - 0.28, h - 0.58, body,
                           size=body_size, align="START", color=self.P.muted,
                           line_spacing=130)
        return y + h        # stacking convention: return the bottom edge y of the drawn area

    def hbars(self, x, y, w, rows, *, row_h=0.46, gap=0.2, label_w=2.4,
              value_w=1.5, max_value=None, colors=None):
        """Horizontal bar chart. rows is a list of (label, value, display string).
        Returns the bottom edge y.

        Use only for values that have a cited source.
        """
        if not rows:
            raise ValueError(t("hbars: rows is empty"))
        mx = max_value if max_value is not None else max(r[1] for r in rows)
        if mx <= 0:
            mx = 1.0  # when every row is 0, draw only an empty track (avoids division by zero)
        track_x = x + label_w
        track_w = w - label_w - value_w
        for i, (name, value, caption) in enumerate(rows):
            ry = y + i * (row_h + gap)
            self.label(x, ry, label_w - 0.12, row_h, name, size=11,
                       align="START", valign="MIDDLE", color=self.P.text)
            self.shape(track_x, ry + row_h * 0.18, track_w, row_h * 0.64,
                       kind="ROUND_RECTANGLE", fill=lighten(self.P.primary, 0.9), stroke=None)
            ratio = max(0.02, value / mx)
            fill = (colors[i] if colors else self.P.primary)
            self.shape(track_x, ry + row_h * 0.18, track_w * ratio, row_h * 0.64,
                       kind="ROUND_RECTANGLE", fill=fill, stroke=None)
            self.label(track_x + track_w + 0.12, ry, value_w - 0.12, row_h, caption,
                       size=12, bold=True, align="START", valign="MIDDLE", color=fill)
        return y + len(rows) * (row_h + gap) - gap

    def metric(self, x, y, w, h, value, caption, *, color=None, value_size=26,
               caption_size=10):
        """A large value plus caption. Returns the bottom edge y. Use only for values that have a cited source."""
        c = color or self.P.primary
        self.shape(x, y, w, h, kind="ROUND_RECTANGLE",
                   fill=lighten(c, 0.9), stroke=lighten(c, 0.55))
        # Shrink the value when the box is short. A fixed size would collide with the caption
        vh = h * 0.52
        vs = min(value_size, vh * 72.0 / self.LINE_EM)
        self.label(x + 0.1, y + 0.08, w - 0.2, vh, value, size=vs,
                   bold=True, align="CENTER", valign="MIDDLE", color=c)
        self.label(x + 0.1, y + 0.10 + vh, w - 0.2, h - vh - 0.16, caption,
                   size=caption_size, align="CENTER", valign="TOP", color=self.P.muted,
                   line_spacing=120)
        return y + h

    def flow(self, x, y, w, h, steps, *, gap=0.34, fill=None, color=None, size=11):
        """Left-to-right process flow. steps is a list of strings. Returns the bottom edge y."""
        n = len(steps)
        bw = (w - gap * (n - 1)) / n
        for i, s in enumerate(steps):
            bx = x + i * (bw + gap)
            self.shape(bx, y, bw, h, kind="ROUND_RECTANGLE",
                       fill=fill or self.P.surface, stroke=self.P.border,
                       text=s, size=size, color=color or self.P.text, bold=True,
                       line_spacing=115)
            if i < n - 1:
                cy = y + h / 2
                self.arrow(bx + bw + 0.06, cy, bx + bw + gap - 0.06, cy,
                           color=self.P.primary, weight=1.5, _anchored=True)
        return y + h
