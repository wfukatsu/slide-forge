#!/usr/bin/env python3
"""スライド上に図解を描くためのプリミティブ。

`build-deck.py` の `TemplateDeck` と組み合わせて使う。プレースホルダだけでは
表現できない図（比較図、フロー、アーキテクチャ、バーチャート等）を、
テンプレートの配色を使って描く。

    import sys; sys.path.insert(0, "<skill>/scripts")
    from importlib.machinery import SourceFileLoader
    bd = SourceFileLoader("bd", "<skill>/scripts/build-deck.py").load_module()
    from diagrams import Canvas

    deck = bd.TemplateDeck.create(template, title="…")
    ref = deck.add_slide("TITLE_ONLY", title="…")
    d = Canvas(deck, ref["slideId"], template)
    d.box(0.5, 1.2, 2.6, 0.9, "Inner Loop", fill=d.P.primary, color="#FFFFFF")
    d.arrow(3.2, 1.65, 4.0, 1.65)

座標はすべてインチ。原点はスライド左上。

図形どうしを結ぶときは座標を手で書かず、次のいずれかを使う。端点がずれていても
Slides API はエラーにしないため、手書きの座標は事故のもとになる。

    a = d.shape(1.0, 1.0, 1.6, 0.6, text="A")   # shape() は objectId を返す
    b = d.shape(4.0, 2.0, 1.6, 0.6, text="B")
    d.connect(a, b)              # API のコネクタ。図形に紐づき、動かすと追従する
    d.link(a, b)                 # 中心を結ぶ線と辺の交点を端点にする
    d.line(..., free=True)       # 軸や引き出し線など、接しないのが正しい線

    for msg in d.audit_connectors():   # 浮いた線・埋まった線を座標の段階で拾う
        print(msg)

構造を正確に示す図はこのモジュール、概念を絵で示す「イメージ図」は
`illustrations`（図形で描く）、`icons`（ブランドのアイコン素材）、
`images`（AI 生成・手持ちの画像）が担当する。すべて Canvas のメソッドとして
生えている。

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
# 色ユーティリティは colors.py に移した。`from diagrams import lighten` のような
# 既存の import を壊さないよう、ここから re-export している。
from colors import (  # noqa: E402,F401
    Palette, contrast_ratio, darken, lighten, mix, readable_on, relative_luminance,
)
from charts import ChartMixin  # noqa: E402
from cloud_icons import CloudIconMixin  # noqa: E402
from icons import IconLibraryMixin  # noqa: E402
from illustrations import IllustrationMixin  # noqa: E402
from images import ImageMixin  # noqa: E402
from patterns import PatternMixin  # noqa: E402


# ---------- 描画 ----------

class Canvas(IllustrationMixin, IconLibraryMixin, CloudIconMixin, ImageMixin,
             ChartMixin, PatternMixin):
    """1 枚のスライドに図形を描くための薄いラッパー。"""

    _seq = 0

    # コネクタの接続サイト（全シェイプ共通で 4 点）
    SITE_TOP, SITE_LEFT, SITE_BOTTOM, SITE_RIGHT = 0, 1, 2, 3

    def __init__(self, deck, slide_id: str, template: dict):
        self.deck = deck
        self.slide_id = slide_id
        self._template_colors = template.get("colors", {})
        self.P = Palette(self._template_colors)
        page = template.get("pageSize", {})
        self.page_w = page.get("widthInches", 10.0)
        self.page_h = page.get("heightInches", 5.625)
        # 描いた図形の実座標。コネクタの接続先を自動で決めるために保持する
        self.rects: dict[str, tuple] = {}
        # 引いた線の記録。端点がどこにも接していないコネクタを検査で拾うために使う
        self.connectors: list[dict] = []
        # 文字を持つ図形の記録。重なりと文字溢れの検査に使う
        self.texts: dict[str, dict] = {}
        # 塗りのある図形の記録。後から描かれると下の文字を覆い隠す
        self.solids: list[dict] = []
        self._seq = 0

    def _oid(self, prefix: str) -> str:
        Canvas._seq += 1
        return f"dg{prefix}{Canvas._seq:04d}"

    def _elem_props(self, x, y, w, h, rotation: float = 0.0,
                    flip_x: bool = False, flip_y: bool = False):
        """要素の位置と大きさ。rotation は度。中心を保ったまま回す。

        Slides API に回転角のフィールドは無く、アフィン変換で表す。
            x' = scaleX·x + shearX·y + translateX
            y' = shearY·x + scaleY·y + translateY

        flip_x / flip_y は鏡像（scale を負にする）。RIGHT_TRIANGLE のように
        左右非対称な図形で、4 隅どの向きの直角三角形も作れるようにするために要る。
        rotation とは併用しない。
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
        """回転後の外接矩形。当たり判定・検査はこちらを使う。"""
        if not rotation:
            return (x, y, w, h)
        th = math.radians(rotation)
        cos, sin = abs(math.cos(th)), abs(math.sin(th))
        nw, nh = w * cos + h * sin, w * sin + h * cos
        return (x + (w - nw) / 2, y + (h - nh) / 2, nw, nh)

    def _solid(self, hex_color, alpha: float = 1.0):
        return {"solidFill": {"color": {"rgbColor": _auth.hex_to_rgb(hex_color)},
                              "alpha": alpha}}

    # ---- 図形 ----

    def shape(self, x, y, w, h, *, kind="RECTANGLE", fill=None, stroke=None,
              stroke_weight=1.0, dash="SOLID", text=None, color=None, size=11,
              bold=False, align="CENTER", valign="MIDDLE", line_spacing=None,
              alpha: float = 1.0, rotation: float = 0.0,
              flip_x: bool = False, flip_y: bool = False,
              font: str | None = None) -> str:
        """図形を描き、objectId を返す。fill=None で塗りなし。

        dash は枠線の線種（SOLID / DASH / DOT / DASH_DOT …）。クラウドの
        ゾーン枠のように「囲い」を示す矩形は破線にする。

        font はフォントファミリー（省略時 Noto Sans JP）。コードブロックには
        "Roboto Mono" のような等幅フォントを指定する。

        alpha は塗りの不透明度（0〜1）。ベン図など重ねて見せる図で使う。
        rotation は度。中心を保ったまま回す。回転した図形は外接矩形で記録するため、
        検査（audit_*）の判定はやや保守的になる。

        **回転した図形に text を入れてはいけない。** 文字も一緒に回るため、180 度なら
        上下逆さま、45 度なら斜めに出る。台形や五角形を反転して使うときは、
        図形は text 無しで描き、文字は別に label() で重ねること
        （label(rotation=270) のような、意図して縦にする用途だけが例外）。
        """
        if text and rotation % 360 not in (0, 90, 270):
            print(f"  warn: 回転 {rotation}度 の図形に文字を入れています。"
                  f"文字も回ります（「{str(text)[:12]}」）。"
                  f"図形は text 無しで描き、label() を重ねてください", file=sys.stderr)
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
                "weight": {"magnitude": int(stroke_weight * 12700), "unit": "EMU"},
                "dashStyle": dash,
            }
            fields.append("outline")
        props["contentAlignment"] = valign
        fields.append("contentAlignment")
        reqs.append({"updateShapeProperties": {
            "objectId": oid, "shapeProperties": props, "fields": ",".join(fields)}})

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
            reqs.append({"updateParagraphStyle": {
                "objectId": oid, "style": pstyle,
                "textRange": {"type": "ALL"}, "fields": ",".join(pfields)}})

        self.deck.requests += reqs
        self._seq += 1
        box = self._aabb(x, y, w, h, rotation)
        self.rects[oid] = (*box, kind)
        # 半透明の塗りは下の文字を透かすので「隠している」とは扱わない
        if fill is not None and alpha >= 0.9:
            self.solids.append({"rect": box, "seq": self._seq,
                                "name": (text or kind).replace("\n", " ")[:20]})
        if text:
            # 回転した枠の中の文字は行送りの向きが変わり、外接矩形での判定が
            # 当てにならない。90/270 度は幅と高さを入れ替えて評価する
            trect = (box[0], box[1], h, w) if rotation % 180 == 90 else box
            self.texts[oid] = {"rect": trect, "kind": kind, "text": text,
                               "size": size, "ls": line_spacing or 100,
                               "fill": fill is not None and alpha >= 0.9,
                               "align": align, "valign": valign, "seq": self._seq}
        return oid

    def box(self, x, y, w, h, text=None, **kw) -> str:
        """角丸の箱。既定は淡い面に primary の枠。"""
        kw.setdefault("kind", "ROUND_RECTANGLE")
        kw.setdefault("fill", self.P.surface)
        kw.setdefault("stroke", self.P.border)
        return self.shape(x, y, w, h, text=text, **kw)

    def solid(self, x, y, w, h, text=None, **kw) -> str:
        """塗りつぶしの箱（見出し用）。"""
        kw.setdefault("kind", "ROUND_RECTANGLE")
        kw.setdefault("fill", self.P.primary)
        kw.setdefault("bold", True)
        return self.shape(x, y, w, h, text=text, **kw)

    def label(self, x, y, w, h, text, *, size=10, color=None, bold=False,
              align="START", valign="TOP", line_spacing=None, rotation=0,
              font=None) -> str:
        """枠も塗りもないテキスト。rotation=270 で縦軸のラベルなどに使える。"""
        return self.shape(x, y, w, h, kind="TEXT_BOX", fill=None, stroke=None,
                          text=text, size=size, color=color or self.P.text, bold=bold,
                          align=align, valign=valign, line_spacing=line_spacing,
                          rotation=rotation, font=font)

    def band(self, x, y, w, h, *, fill=None) -> str:
        """背景の帯。図のグループ化に使う。"""
        return self.shape(x, y, w, h, kind="ROUND_RECTANGLE",
                          fill=fill or self.P.surfaceAlt, stroke=None)

    # ---- コードブロック ----

    # VS Code Dark+ 風。濃色背景 CODE_BG 上でコントラスト比 4.5:1 以上を満たす
    CODE_BG, CODE_FG = "#1F2933", "#E8ECF1"
    _CODE_STYLES = {
        "comment": "#7DBA7D",   # コメント（緑）
        "string":  "#E2A37E",   # 文字列（橙）
        "keyword": "#6FB6EA",   # 予約語（青）
        "number":  "#B5CEA8",   # 数値（淡緑）
        "type":    "#56C9B4",   # 型・クラス（青緑）
        "func":    "#DCDCAA",   # 関数・メソッド（黄）
        "anno":    "#D19FD3",   # アノテーション・ディレクティブ（紫）
        "prop":    "#9CDCFE",   # プロパティ名・フラグ（水色）
    }
    # 言語ごとの字句規則。上にあるものが優先（コメント・文字列を最優先に置く）
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
        # シェル。二重引用符の中身は素通しにして、SQL キーワードを拾えるようにする
        # （TableStore の --statement "CREATE TABLE …" のため）
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
        """(start, end, hex) のリスト。インデックスは UTF-16 単位と一致する
        （BMP 外の文字を含むコードは想定しない）。"""
        rules = cls._CODE_RULES.get(lang)
        if not rules:
            return []
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
        """シンタックスハイライト付きのコードパネル。

        lang は _CODE_RULES のキー（java / graphql / json / bash）。未知の言語は
        単色で描く。高さの見積もりは実効行高（fontSize × lineSpacing × 約1.45）で
        行うこと。
        """
        # 角は直角にする（角丸だと 1 行目・最終行のインデントが角に食われて
        # 見え、他のカード類の直角規約とも揃わない）
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

    # ---- 線・矢印 ----

    def line(self, x1, y1, x2, y2, *, color=None, weight=1.25,
             end_arrow="NONE", start_arrow="NONE", dashed=False,
             free=False, _anchored=False) -> str:
        """座標を直接指定して線を引く。

        図形と図形を結ぶなら connect()（API で接続）か link()（端点を辺に合わせる）
        を使うこと。こちらは端点が図形からずれていても API は何も言わない。
        free=True は「どの図形にも接しないのが正しい線」の明示（軸・区切り線など）。
        """
        oid = self._oid("l")
        # STRAIGHT の線は、要素の矩形の「左上 → 右下」に引かれる。
        # 任意の方向を表すため、外接矩形に正規化した上で軸ごとに反転させる。
        # 反転しないと矢印の頭が意図と逆側に付く。
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
                    "weight": {"magnitude": int(weight * 12700), "unit": "EMU"},
                    "dashStyle": "DASH" if dashed else "SOLID",
                    "startArrow": start_arrow,
                    "endArrow": end_arrow,
                },
                "fields": "lineFill,weight,dashStyle,startArrow,endArrow",
            }},
        ]
        self.connectors.append({
            "oid": oid, "p1": (x1, y1), "p2": (x2, y2),
            "free": free or _anchored, "anchored": _anchored,
        })
        return oid

    def arrow(self, x1, y1, x2, y2, **kw) -> str:
        kw.setdefault("end_arrow", "FILL_ARROW")
        return self.line(x1, y1, x2, y2, **kw)

    # ---- 図形に接続するコネクタ ----

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
        """src から見て dst のある向きの接続サイトを返す。"""
        ax, ay = cls._center(src)
        bx, by = cls._center(dst)
        dx, dy = bx - ax, by - ay
        if abs(dx) >= abs(dy):
            return cls.SITE_RIGHT if dx > 0 else cls.SITE_LEFT
        return cls.SITE_BOTTOM if dy > 0 else cls.SITE_TOP

    def edge_point(self, rect_or_id, toward, *, gap=0.0):
        """矩形の中心から toward(=(x, y)) に向かう線が、辺と交わる点を返す。

        gap を指定すると、その分だけ外側に離す（矢印の頭が枠線に食い込まない）。
        """
        rect = self.rects.get(rect_or_id) if isinstance(rect_or_id, str) else rect_or_id
        if rect is None:
            raise ValueError(f"座標が分からない図形です: {rect_or_id}")
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
        """2つの図形を **API のコネクタとして接続する**。

        src / dst は shape() などが返した objectId。Google Slides 側で図形に
        紐づくため、後から図形を動かしても線が追従する。接続サイトは
        位置関係から自動で決まる（0=上 1=左 2=下 3=右）。

        category="BENT" にするとエルボー（直角折れ）になる。1対多のファンアウトは
        BENT のほうが経路が交差しにくい。
        """
        ra, rb = self.rects.get(src), self.rects.get(dst)
        if ra is None or rb is None:
            raise ValueError("connect() は Canvas が描いた図形どうしにのみ使えます")
        s_site = self._facing_site(ra, rb) if start_site is None else start_site
        e_site = self._facing_site(rb, ra) if end_site is None else end_site
        p1 = self._site_point(ra, s_site)
        p2 = self._site_point(rb, e_site)

        oid = self._oid("c")
        # 接続を設定すると API 側が位置を決めるが、接続が効かなかった場合に
        # 線が原点に残らないよう、初期形状もサイト間の実座標で作っておく
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
                    "weight": {"magnitude": int(weight * 12700), "unit": "EMU"},
                    "dashStyle": "DASH" if dashed else "SOLID",
                    "startArrow": start_arrow,
                    "endArrow": end_arrow,
                },
                "fields": ("startConnection,endConnection,lineFill,weight,"
                           "dashStyle,startArrow,endArrow"),
            }},
        ]
        self.connectors.append({"oid": oid, "p1": p1, "p2": p2,
                                "free": True, "anchored": True})
        return oid

    # ---- コネクタの自己点検 ----

    # 判定のしきい値（インチ）
    CONN_REACH = 0.22       # これ以上どの図形からも離れていたら「接続されていない」
    CONN_BURY = 0.06        # これ以上図形の内側に入っていたら「埋まっている」
    CONN_CONTAINER = 6.0    # 面積がこれを超える図形は容器とみなし判定から外す

    @staticmethod
    def _dist_to_rect(px, py, rect):
        """点から矩形の境界までの符号つき距離。負なら内側（食い込み量）。"""
        x, y, w, h = rect[:4]
        dx = max(x - px, 0.0, px - (x + w))
        dy = max(y - py, 0.0, py - (y + h))
        if dx > 0 or dy > 0:
            return (dx * dx + dy * dy) ** 0.5
        return -min(px - x, (x + w) - px, py - y, (y + h) - py)

    def audit_connectors(self) -> list[str]:
        """端点が図形に接していないコネクタを列挙する。問題が無ければ空リスト。

        Slides API は線の座標をそのまま受け取るだけで、図形との位置関係を検証しない。
        そのため「矢印が浮いている」「枠に食い込んでいる」は生成してサムネイルを
        見るまで気づけない。これを座標の段階で拾う。

        判定から外すもの:
          - free=True を付けた線（軸・目盛り・引き出し線など、接しないのが正しい）
          - connect() / link() で引いた線（定義上、図形に接している）
          - テキストボックス（見える境界が無い）
          - 面積の大きい図形（ゾーンなどの容器。矢印が中を通るのは正常）
        """
        targets = [r for r in self.rects.values()
                   if r[4] != "TEXT_BOX" and r[2] * r[3] <= self.CONN_CONTAINER]
        if not targets:
            return []
        out = []
        for conn in self.connectors:
            if conn["free"]:
                continue
            for name, p in (("始点", conn["p1"]), ("終点", conn["p2"])):
                near = min((self._dist_to_rect(p[0], p[1], r) for r in targets),
                           key=abs)
                if near > self.CONN_REACH:
                    out.append(f"コネクタの{name}がどの図形にも接していません"
                               f"（最寄りの図形まで {near:.2f}in）")
                elif near < -self.CONN_BURY:
                    out.append(f"コネクタの{name}が図形の内部に埋まっています"
                               f"（{-near:.2f}in 食い込み）")
        return out

    # 重なり・文字溢れの判定しきい値
    OVERLAP_MIN = 0.010     # これ以上の面積(in^2)が重なっていたら報告する
    OVERLAP_RATIO = 0.06    # 小さい方の面積に対する重なり比率の下限
    TEXT_SLACK = 0.04       # 文字の必要高さに対して許す余裕(in)
    LINE_EM = 1.45          # Noto Sans JP の行高（フォントサイズに対する倍率）

    @staticmethod
    def _em(t):
        return sum(1.0 if unicodedata.east_asian_width(c) in "WFA" else 0.5 for c in t)

    @staticmethod
    def _overlap_area(a, b):
        ox = min(a[0] + a[2], b[0] + b[2]) - max(a[0], b[0])
        oy = min(a[1] + a[3], b[1] + b[3]) - max(a[1], b[1])
        return (ox * oy) if (ox > 0 and oy > 0) else 0.0

    @staticmethod
    def _contains(outer, inner, slack=0.02):
        return (inner[0] >= outer[0] - slack and inner[1] >= outer[1] - slack
                and inner[0] + inner[2] <= outer[0] + outer[2] + slack
                and inner[1] + inner[3] <= outer[1] + outer[3] + slack)

    # Slides のテキスト枠の既定インセット（左右 0.1in）。ここを引かずに幅で割ると
    # 「1 行に入る文字数」を 1〜2 字多く見積もり、実際には折り返しているのに
    # 検査が素通りする。
    #
    # 縦方向のインセット（0.05in）は**引かない**。Slides は枠から縦に溢れた文字を
    # 切り取らずそのまま描くため、引くと 1 行のラベルが軒並み誤検知になる
    # （実測: 0.24in の枠に 9.5pt の 1 行は問題なく出る）。
    TEXT_INSET_X = 0.10

    def _text_lines(self, m):
        """折り返しを見込んだ行数と、1 行に入る文字数を返す。"""
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
        """実際に文字（または塗り）が占める矩形。

        塗りのある図形は矩形全体が不透明。塗りの無いラベルは、文字が実際に載る
        範囲だけを見る。枠は広くても中央寄せの短い文字なら隣とぶつからないため。
        """
        x, y, w, h = m["rect"]
        if m["fill"]:
            return (x, y, w, h)
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
        """文字が隠れている／ぶつかっている箇所を報告する。

        Slides は後から作った要素を上に描く。したがって

        1. **隠れ** … ある文字より後に描かれた不透明な図形が、その文字に
           かぶさっている。バナーやゾーンが直前のブロックに潜り込む典型がこれ。
        2. **衝突** … 塗りの無いラベルどうしが、実際の文字の範囲でぶつかっている。

        枠ではなく「文字が実際に載る範囲」で判定するため、余白の広いラベルが
        隣に少しかかっているだけでは報告しない。
        """
        items = sorted(self.texts.values(), key=lambda m: m["seq"])
        out, seen = [], set()

        def record(msg, key):
            if key not in seen:
                seen.add(key)
                out.append(msg)

        # 1. 後から描かれた塗り図形が文字を覆う
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
                record(f"文字が後から描いた図形に隠れています（{area:.3f}in²）:"
                       f"「{ta}」を「{sol['name']}」が覆っている",
                       ("hide", ta, sol["name"]))

        # 2. 塗りの無いラベルどうしの衝突
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
                record(f"文字どうしがぶつかっています（{area:.3f}in²）:"
                       f"「{ta}」と「{tb}」", ("hit", *sorted((ta, tb))))
        return out

    BOUNDS_SLACK = 0.02     # この量までのはみ出しは許す（丸め誤差）

    def audit_bounds(self) -> list[str]:
        """スライドの外へ出た図形・線を報告する。

        図の部品は与えられた枠から自分で座標を計算するため、枠の中に収まっていても
        中身が外へ突き抜けることがある（比率のかけ違い）。図形単位で見ないと拾えない。
        """
        out = []
        s = self.BOUNDS_SLACK
        for oid, r in self.rects.items():
            x, y, w, h, kind = r
            over = []
            if x < -s:
                over.append(f"左に {-x:.2f}in")
            if y < -s:
                over.append(f"上に {-y:.2f}in")
            if x + w > self.page_w + s:
                over.append(f"右に {x + w - self.page_w:.2f}in")
            if y + h > self.page_h + s:
                over.append(f"下に {y + h - self.page_h:.2f}in")
            if over:
                name = self.texts.get(oid, {}).get("text", kind)
                out.append(f"図形がスライドの外に出ています（{'/'.join(over)}）:"
                           f"「{str(name).replace(chr(10), ' ')[:20]}」")
        for conn in self.connectors:
            for p in (conn["p1"], conn["p2"]):
                if not (-s <= p[0] <= self.page_w + s and -s <= p[1] <= self.page_h + s):
                    out.append(f"線の端点がスライドの外にあります: "
                               f"({p[0]:.2f}, {p[1]:.2f})")
        return out

    ORPHAN_EM = 1.0     # 折り返しの最終行がこれ以下なら「1文字だけこぼれた」とみなす

    def audit_text_fit(self) -> list[str]:
        """枠に収まらない文字と、みっともない折り返しを報告する。

        1. **溢れ** … 1 行に入る文字数を「幅(pt) ÷ フォントサイズ(pt)」で見積もり、
           必要な行数から必要な高さを出して、宣言した高さと比べる。溢れた文字は
           切れて見える。
        2. **孤立行** … 折り返した結果、最後の行に 1 文字しか残らない状態。
           「…デプロ / イ」のような割れ方は、収まってはいるが明らかに不格好。
           枠を数 mm 広げるか文言を詰めれば消える。
        """
        out = []
        for m in self.texts.values():
            h = m["rect"][3]
            lines, per = self._text_lines(m)
            if per <= 0:
                continue
            need = lines * m["size"] * self.LINE_EM * (m["ls"] / 100.0) / 72.0
            if need > h + self.TEXT_SLACK:
                t = m["text"].replace("\n", " ")[:22]
                out.append(f"枠に対して文字が多すぎます"
                           f"（必要 {need:.2f}in > 枠 {h:.2f}in / {lines}行）:「{t}」")
                continue
            for ln in m["text"].split("\n"):
                e = self._em(ln)
                if e <= per:
                    continue
                tail = e % per
                if 0 < tail <= self.ORPHAN_EM:
                    out.append(f"折り返しの最終行に文字が {tail:.1f} 字しか残りません"
                               f"（1行 {per:.1f} 字）:「{ln[:22]}」")
        return out

    def link(self, src, dst, *, gap=0.04, color=None, weight=1.4, dashed=False,
             end_arrow="FILL_ARROW", start_arrow="NONE") -> str:
        """2つの図形を、**辺のちょうど上を端点にした直線**で結ぶ。

        中心どうしを結ぶ線が辺と交わる点を計算するので、斜めの位置関係でも
        端点が図形にぴったり触れる。API の接続サイト（上下左右の4点）に
        スナップさせたくない場合はこちら。
        """
        ra = self.rects.get(src) if isinstance(src, str) else src
        rb = self.rects.get(dst) if isinstance(dst, str) else dst
        if ra is None or rb is None:
            raise ValueError("link() は座標の分かる図形どうしにのみ使えます")
        p1 = self.edge_point(ra, self._center(rb), gap=gap)
        p2 = self.edge_point(rb, self._center(ra), gap=gap)
        return self.line(p1[0], p1[1], p2[0], p2[1], color=color, weight=weight,
                         dashed=dashed, end_arrow=end_arrow,
                         start_arrow=start_arrow, _anchored=True)

    def arrow_shape(self, x, y, w, h, *, fill=None, text=None, **kw) -> str:
        """太い矢印（工程の流れなど）。"""
        return self.shape(x, y, w, h, kind="RIGHT_ARROW",
                          fill=fill or lighten(self.P.primary, 0.75), stroke=None,
                          text=text, **kw)

    # ---- 複合パーツ ----

    def cards(self, x, y, w, h, items, *, gap=0.22, fill=None, stroke=None,
              title_size=12, body_size=10, accent=None):
        """横並びのカード。items は (見出し, 本文) のリスト。戻り値は下端 y。

        上端に直線のアクセントバーを重ねるため、角は丸めない（RECTANGLE）。
        角丸の縁と直線バーの端が噛み合わず、不揃いに見えるため。
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
                # 本文は見出しの直下から。固定で 0.7 引くと h が小さいとき本文が
                # ほぼ潰れて文字が切れる
                self.label(cx + 0.14, y + 0.50, cw - 0.28, h - 0.58, body,
                           size=body_size, align="START", color=self.P.muted,
                           line_spacing=130)
        return y + h        # 積み上げ規約：戻り値は描画領域の下端 y

    def hbars(self, x, y, w, rows, *, row_h=0.46, gap=0.2, label_w=2.4,
              value_w=1.5, max_value=None, colors=None):
        """横棒グラフ。rows は (ラベル, 数値, 表示文字列) のリスト。戻り値は下端 y。

        出典のある数値にだけ使うこと。
        """
        mx = max_value or max(r[1] for r in rows)
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
        """大きな数値＋説明の組。戻り値は下端 y。出典のある数値にだけ使うこと。"""
        c = color or self.P.primary
        self.shape(x, y, w, h, kind="ROUND_RECTANGLE",
                   fill=lighten(c, 0.9), stroke=lighten(c, 0.55))
        # 枠が低いときは数値を縮める。固定サイズだと説明とぶつかる
        vh = h * 0.52
        vs = min(value_size, vh * 72.0 / self.LINE_EM)
        self.label(x + 0.1, y + 0.08, w - 0.2, vh, value, size=vs,
                   bold=True, align="CENTER", valign="MIDDLE", color=c)
        self.label(x + 0.1, y + 0.10 + vh, w - 0.2, h - vh - 0.16, caption,
                   size=caption_size, align="CENTER", valign="TOP", color=self.P.muted,
                   line_spacing=120)
        return y + h

    def flow(self, x, y, w, h, steps, *, gap=0.34, fill=None, color=None, size=11):
        """左から右への工程フロー。steps は文字列のリスト。戻り値は下端 y。"""
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
