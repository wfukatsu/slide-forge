#!/usr/bin/env python3
"""template.json とデッキ仕様からプレゼンテーションを生成する。

テンプレートを Drive API で複製 → 同梱スライドを削除 → `createSlide(layoutId)` で
スライドを積む。テンプレートのマスターが定義する装飾・ロゴ・フッターは自動継承される。

    # 仕様の検証だけ（API 呼び出しなし）
    python scripts/build-deck.py --template templates/x.json --spec deck.json --dry-run

    # 生成
    python scripts/build-deck.py --template templates/x.json --spec deck.json \
        --title "資料タイトル" [--folder <DRIVE_FOLDER_URL_OR_ID>]

ライブラリとして:
    deck = TemplateDeck.create(template, title="…")
    deck.add_slide("CONTENT", title="…", body=["…"])
    print(deck.commit())
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _auth  # noqa: E402

FILLABLE = ("TITLE", "SUBTITLE", "BODY")

# オブジェクト ID をプロセス間で衝突させないためのランダムトークン。
# 連番だけだと、既存デッキへ別プロセスから追記したとき slide_001 等が衝突する
_RUN_TOKEN = uuid.uuid4().hex[:4]


def _retry(call, *, what: str, attempts: int = 4, base_delay: float = 3.0):
    """一時的な 5xx / 429 を吸収して API 呼び出しを繰り返す。

    枚数の多いテンプレートの `files.copy` は、混んでいるときに 500 Internal Error を
    返すことが実際にある。1 回で諦めると生成が丸ごと落ちるので指数バックオフで粘る。
    HttpError 以外に、socket timeout 等のネットワーク例外（OSError）も再試行する。
    """
    import time
    from googleapiclient.errors import HttpError

    for i in range(attempts):
        try:
            return call()
        except (HttpError, OSError) as e:
            code = getattr(getattr(e, "resp", None), "status", None)
            retryable = isinstance(e, OSError) or code in (429, 500, 502, 503, 504)
            if not retryable or i == attempts - 1:
                raise
            code = code or type(e).__name__
            wait = base_delay * (2 ** i)
            print(f"  warn: {what} が HTTP {code} で失敗。{wait:.0f} 秒後に再試行 "
                  f"({i + 1}/{attempts - 1})", file=sys.stderr)
            time.sleep(wait)


def load_template(path: str) -> dict:
    with open(path) as f:
        return json.load(f)


class TemplateDeck:
    """テンプレートを複製した上にスライドを積んでいくビルダー。"""

    def __init__(self, slides_service, drive_service, presentation_id: str, template: dict):
        self.slides = slides_service
        self.drive = drive_service
        self.presentation_id = presentation_id
        self.template = template
        self.requests: list[dict] = []
        self.slide_ids: list[str] = []
        self._added: list[dict] = []
        self._notes: list[tuple[str, str]] = []  # (slideId, notes)
        self._counter = 0
        # keep_existing で残したテンプレート同梱スライドの枚数。
        # add_page_numbers() が新規スライドの番号をこの分だけずらす
        self.kept_slides = 0
        # 画像を挿入したときに images.AssetStore が入る。commit() の後で後始末する
        self.assets = None
        # (objectId, x, y, w, h)。createImage は比率を保つため、枠ぴったりに
        # 敷きたい画像は commit 後に transform を上書きして直す
        self.image_fixups: list[tuple] = []

    # ---------- 生成 ----------

    @classmethod
    def create(
        cls,
        template: dict,
        title: str,
        folder: str | None = None,
        creds=None,
        keep_existing: bool = False,
    ) -> "TemplateDeck":
        src = template.get("presentationId")
        if not src:
            raise ValueError("template.json に presentationId がありません")
        slides, drive = _auth.services(creds)

        body: dict = {"name": title}
        fid = _auth.folder_id(folder)
        if fid:
            body["parents"] = [fid]
        copied = _retry(
            lambda: drive.files().copy(fileId=src, body=body, fields="id").execute(),
            what="テンプレートの複製")

        deck = cls(slides, drive, copied["id"], template)
        if not keep_existing:
            deck._delete_existing_slides()
        else:
            # 残したスライドの実枚数を数え、ページ番号の起点をずらす。
            # template.json の existingSlideIds はテンプレート更新で古くなり得るため実物を見る
            pres = _retry(
                lambda: deck.slides.presentations().get(
                    presentationId=deck.presentation_id, fields="slides.objectId"
                ).execute(),
                what="presentations.get")
            deck.kept_slides = len(pres.get("slides", []))
        return deck

    def _delete_existing_slides(self) -> None:
        """複製直後に残っているテンプレート同梱スライドを削除する。"""
        pres = _retry(
            lambda: self.slides.presentations().get(
                presentationId=self.presentation_id, fields="slides.objectId"
            ).execute(),
            what="presentations.get")
        present = [s["objectId"] for s in pres.get("slides", [])]
        expected = set(self.template.get("existingSlideIds", []))
        stale = expected - set(present)
        if stale:
            print(
                f"  warn: template.json の existingSlideIds に実在しない ID があります: "
                f"{sorted(stale)}\n"
                f"        テンプレートが更新された可能性があります。inspect-template.py で再解析してください。",
                file=sys.stderr,
            )
        # 実在するスライドは全て削除する（テンプレート側でスライドが増えていても取りこぼさない）
        for oid in present:
            self.requests.append({"deleteObject": {"objectId": oid}})

    # ---------- レイアウト解決 ----------

    def resolve_layout(self, key: str) -> tuple[str, dict]:
        """ロール名（CONTENT 等）またはレイアウトキーからレイアウト定義を引く。"""
        layouts = self.template["layouts"]
        resolved = self.template.get("roles", {}).get(key, key)
        if resolved not in layouts:
            roles = sorted(self.template.get("roles", {}))
            raise KeyError(
                f"レイアウト '{key}' を解決できません。"
                f"利用可能なロール: {roles} / レイアウトキー: {sorted(layouts)}"
            )
        return resolved, layouts[resolved]

    # ---------- スライド追加 ----------

    def _next_id(self, prefix: str) -> str:
        self._counter += 1
        # objectId は 50 文字まで。長いレイアウト名でも収まるよう prefix を丸める
        return f"{prefix[:40]}_{_RUN_TOKEN}_{self._counter:03d}"

    def add_slide(
        self,
        layout_key: str,
        *,
        title: str | None = None,
        subtitle: str | None = None,
        body: str | list[str] | None = None,
        bodies: list | None = None,
        notes: str | None = None,
        index: int | None = None,
        body_font_size: float | None = None,
        body_line_spacing: float | None = None,
    ) -> dict:
        """レイアウトを指定してスライドを追加し、プレースホルダを埋める。

        `bodies` は 2カラム/3カラムのレイアウト用。BODY プレースホルダの index 0,1,2… に
        順番に流し込む。`body` は `bodies=[body]` と等価。

        戻り値は {"slideId", "placeholders", "layout", "layoutKey"}。
        追加の図形を描きたい場合はこの slideId を pageObjectId に使う。
        """
        resolved_key, layout = self.resolve_layout(layout_key)
        declared = layout.get("placeholders", [])

        if body is not None and bodies is not None:
            raise ValueError("body と bodies は同時に指定できません")
        if body is not None:
            bodies = [body]

        # リクエストを積む前に検証する。失敗しても中途半端な状態を残さないため。
        for ph_type, value in (("TITLE", title), ("SUBTITLE", subtitle)):
            if value is not None and ph_type not in declared:
                raise ValueError(
                    f"レイアウト '{layout_key}' ({layout['displayName']}) は "
                    f"{ph_type} プレースホルダを持ちません。保持しているのは {declared}"
                )
        body_slots = [p for p in declared if p.split("#")[0] == "BODY"]
        if bodies is not None and len(bodies) > len(body_slots):
            raise ValueError(
                f"レイアウト '{layout_key}' ({layout['displayName']}) の BODY は "
                f"{len(body_slots)} 枠しかありませんが {len(bodies)} 個指定されています"
                f"（保持: {declared}）"
            )

        slide_id = self._next_id("slide")
        ph_ids: dict[str, str] = {}
        mappings = []
        # SLIDE_NUMBER はマッピングしても API に無視されるため対象外（add_page_numbers で描画）
        for name in [t for t in declared if t.split("#")[0] in FILLABLE]:
            ph_type, _, idx = name.partition("#")
            idx = int(idx) if idx else 0
            safe = name.replace("#", "x").lower()
            oid = self._next_id(f"{resolved_key.lower()}_{safe}")
            ph_ids[name] = oid
            mappings.append(
                {"layoutPlaceholder": {"type": ph_type, "index": idx}, "objectId": oid}
            )

        create_req: dict = {
            "objectId": slide_id,
            "slideLayoutReference": {"layoutId": layout["layoutId"]},
        }
        if mappings:
            create_req["placeholderIdMappings"] = mappings
        if index is not None:
            create_req["insertionIndex"] = index
        self.requests.append({"createSlide": create_req})
        self.slide_ids.append(slide_id)
        self._added.append(
            {"slideId": slide_id, "layoutKey": resolved_key, "layout": layout}
        )

        fills = [("TITLE", title), ("SUBTITLE", subtitle)]
        filled_bodies = list(zip(body_slots, bodies or []))
        fills += filled_bodies
        for name, value in fills:
            if value is None:
                continue
            text = "\n".join(value) if isinstance(value, list) else value
            self.requests.append(
                {"insertText": {"objectId": ph_ids[name], "text": text}}
            )

        # 本文の見た目調整。プレースホルダの既定サイズは手書き向けに大きめなことが多く、
        # 日本語の本文は行間を広げないと詰まって見える（既定 100〜115%）。
        for name, value in filled_bodies:
            if value is None:
                continue
            if body_font_size is not None:
                self.requests.append({"updateTextStyle": {
                    "objectId": ph_ids[name],
                    "style": {"fontSize": {"magnitude": body_font_size, "unit": "PT"}},
                    "textRange": {"type": "ALL"},
                    "fields": "fontSize",
                }})
            if body_line_spacing is not None:
                self.requests.append({"updateParagraphStyle": {
                    "objectId": ph_ids[name],
                    "style": {"lineSpacing": body_line_spacing},
                    "textRange": {"type": "ALL"},
                    "fields": "lineSpacing",
                }})

        if notes:
            self._notes.append((slide_id, notes))

        return {
            "slideId": slide_id,
            "placeholders": ph_ids,
            "layout": layout,
            "layoutKey": resolved_key,
        }

    # ---------- ページ番号 ----------

    def add_page_numbers(self, start: int | None = None) -> int:
        """ページ番号をテキストボックスで描画し、描画枚数を返す。

        Slides API は SLIDE_NUMBER プレースホルダを生成できない（createSlide の
        placeholderIdMappings に指定してもエラーにならず黙って無視される）ため、
        レイアウトの slideNumber 座標に合わせて自前で描画する。

        注意: 番号は add_slide() の呼び出し順に振る。add_slide(index=...) で
        挿入位置を指定したデッキでは実際の並び順と一致しない。
        """
        cfg = self.template.get("pageNumber", {})
        # keep_existing で残したスライドの後に積む場合は、その枚数分だけ番号を進める
        start = cfg.get("startAt", 1) + self.kept_slides if start is None else start
        font = cfg.get("font", "Arial")
        size = cfg.get("fontSize", 7)
        color = cfg.get("color", "#666666")
        align = cfg.get("align", "END")

        drawn = 0
        for offset, entry in enumerate(self._added):
            layout = entry["layout"]
            geo = layout.get("elements", {}).get("slideNumber")
            if not layout.get("hasPageNumber") or not geo:
                continue
            # 元の枠は数 mm 幅しかなく 2 桁で切れるため、右端を保ったまま最小 0.5in に広げる
            right = geo["x"] + geo["w"]
            w = max(geo["w"], 0.5)
            x = right - w if align == "END" else geo["x"]
            oid = self._next_id("pagenum")
            self.requests += [
                {
                    "createShape": {
                        "objectId": oid,
                        "shapeType": "TEXT_BOX",
                        "elementProperties": {
                            "pageObjectId": entry["slideId"],
                            "size": {
                                "width": {"magnitude": _auth.inches(w), "unit": "EMU"},
                                "height": {"magnitude": _auth.inches(geo["h"]), "unit": "EMU"},
                            },
                            "transform": {
                                "scaleX": 1, "scaleY": 1,
                                "translateX": _auth.inches(x),
                                "translateY": _auth.inches(geo["y"]),
                                "unit": "EMU",
                            },
                        },
                    }
                },
                {"insertText": {"objectId": oid, "text": str(start + offset)}},
                {
                    "updateTextStyle": {
                        "objectId": oid,
                        "style": {
                            "fontFamily": font,
                            "fontSize": {"magnitude": size, "unit": "PT"},
                            "foregroundColor": {
                                "opaqueColor": {"rgbColor": _auth.hex_to_rgb(color)}
                            },
                        },
                        "textRange": {"type": "ALL"},
                        "fields": "fontFamily,fontSize,foregroundColor",
                    }
                },
                {
                    "updateParagraphStyle": {
                        "objectId": oid,
                        "style": {"alignment": align},
                        "textRange": {"type": "ALL"},
                        "fields": "alignment",
                    }
                },
            ]
            drawn += 1
        return drawn

    # ---------- 実行 ----------

    def commit(self, chunk_size: int = 500) -> str:
        """溜めたリクエストを batchUpdate で実行し、プレゼンテーション URL を返す。"""
        try:
            for i in range(0, len(self.requests), chunk_size):
                chunk = self.requests[i : i + chunk_size]
                _retry(
                    lambda: self.slides.presentations().batchUpdate(
                        presentationId=self.presentation_id, body={"requests": chunk}
                    ).execute(),
                    what=f"batchUpdate ({len(chunk)} requests)")
                print(f"  batch {i // chunk_size + 1}: {len(chunk)} requests")
            self.requests = []
            if self._notes or self.image_fixups:
                self._post_pass()
        finally:
            # Slides は挿入時に画像を中へコピーする。batchUpdate が失敗した場合も、
            # 「リンクを知る全員が閲覧可」で共有した一時アップロードを残さないよう
            # 必ずここで畳む
            if self.assets is not None:
                self.assets.cleanup()
        return f"https://docs.google.com/presentation/d/{self.presentation_id}/edit"

    def _post_pass(self) -> None:
        """スライド作成後にしか分からない情報を使う 2 回目の batchUpdate。

        - スピーカーノート … ノート枠の objectId は createSlide のレスポンスに無い
        - 画像の寸法補正 … createImage は**指定サイズに関係なく元の縦横比を保つ**ため、
          枠を埋める配置（fit="cover" / "stretch"）は作成時には実現できない。
          生成された要素の素の大きさを読み、transform を絶対値で置き換えて直す。
        """
        pres = _retry(
            lambda: self.slides.presentations().get(
                presentationId=self.presentation_id,
                fields=("slides(objectId,"
                        "slideProperties.notesPage.notesProperties.speakerNotesObjectId,"
                        "pageElements(objectId,size))"),
            ).execute(),
            what="presentations.get (post pass)")
        slides = pres.get("slides", [])
        note_ids = {
            s["objectId"]: (
                s.get("slideProperties", {})
                .get("notesPage", {})
                .get("notesProperties", {})
                .get("speakerNotesObjectId")
            )
            for s in slides
        }
        sizes = {
            el["objectId"]: el.get("size", {})
            for s in slides for el in s.get("pageElements", [])
        }

        reqs = []
        for slide_id, text in self._notes:
            oid = note_ids.get(slide_id)
            if not oid:
                print(f"  warn: {slide_id} のノート枠が見つからずスキップしました", file=sys.stderr)
                continue
            reqs.append({"insertText": {"objectId": oid, "text": text}})
        n_notes = len(reqs)

        n_img = 0
        for oid, x, y, w, h in self.image_fixups:
            size = sizes.get(oid) or {}
            mw = size.get("width", {}).get("magnitude")
            mh = size.get("height", {}).get("magnitude")
            if not mw or not mh:
                print(f"  warn: 画像 {oid} の寸法が取れず、枠ぴったりの配置を"
                      f"適用できませんでした", file=sys.stderr)
                continue
            reqs.append({"updatePageElementTransform": {
                "objectId": oid,
                "applyMode": "ABSOLUTE",
                "transform": {
                    "scaleX": _auth.inches(w) / mw,
                    "scaleY": _auth.inches(h) / mh,
                    "translateX": _auth.inches(x),
                    "translateY": _auth.inches(y),
                    "unit": "EMU",
                },
            }})
            n_img += 1

        if reqs:
            _retry(
                lambda: self.slides.presentations().batchUpdate(
                    presentationId=self.presentation_id, body={"requests": reqs}
                ).execute(),
                what=f"batchUpdate (post pass, {len(reqs)} requests)")
            if n_notes:
                print(f"  speaker notes: {n_notes} slides")
            if n_img:
                print(f"  image fit: {n_img} images")
        self._notes = []
        self.image_fixups = []


# ---------- 図・画像のブロック ----------

# spec の "figures" で使える type と、位置引数として渡すキーの並び。
# ここに無いキーは snake_case に直してキーワード引数として渡す。
FIGURES: dict[str, tuple[str, list[str]]] = {
    # イメージ図（illustrations.py・図形だけで描く。ネットワーク不要）
    "icon":         ("icon",         ["name", "x", "y", "size"]),
    "icon_row":     ("icon_row",     ["x", "y", "w", "items"]),
    "icon_flow":    ("icon_flow",    ["x", "y", "w", "items"]),
    "icon_grid":    ("icon_grid",    ["x", "y", "w", "items"]),
    "pyramid":      ("pyramid",      ["x", "y", "w", "h", "items"]),
    "funnel":       ("funnel",       ["x", "y", "w", "h", "items"]),
    "venn":         ("venn",         ["x", "y", "w", "h", "items"]),
    "iceberg":      ("iceberg",      ["x", "y", "w", "h", "above", "below"]),
    "balance":      ("balance",      ["x", "y", "w", "h", "left", "right"]),
    "steps":        ("steps",        ["x", "y", "w", "h", "items"]),
    "layers":       ("layers",       ["x", "y", "w", "h", "items"]),
    "hub":          ("hub",          ["x", "y", "w", "h", "center", "items"]),
    "matrix":       ("matrix",       ["x", "y", "w", "h", "items"]),
    "before_after": ("before_after", ["x", "y", "w", "h", "before", "after"]),
    "journey":      ("journey",      ["x", "y", "w", "h", "items"]),
    "timeline":     ("timeline",     ["x", "y", "w", "items"]),
    # ブランドのアイコン素材（icons.py・Drive 経由で貼るので通信が要る。
    # --dry-run では同じ大きさの矩形に置き換えて座標だけ検査する）
    "asset_icon":       ("asset_icon",       ["name", "x", "y", "size"]),
    "asset_icon_row":   ("asset_icon_row",   ["x", "y", "w", "items"]),
    "asset_icon_flow":  ("asset_icon_flow",  ["x", "y", "w", "items"]),
    "asset_icon_grid":  ("asset_icon_grid",  ["x", "y", "w", "items"]),
    "asset_icon_cards": ("asset_icon_cards", ["x", "y", "w", "h", "items"]),
    # クラウドベンダーの公式アイコン（cloud_icons.py）。asset_icon と同じく
    # --dry-run では矩形に置き換えて座標だけ検査する
    "cloud_icon":      ("cloud_icon",      ["name", "x", "y", "size"]),
    "cloud_icon_row":  ("cloud_icon_row",  ["x", "y", "w", "items"]),
    "cloud_icon_flow": ("cloud_icon_flow", ["x", "y", "w", "items"]),
    "cloud_icon_grid": ("cloud_icon_grid", ["x", "y", "w", "items"]),
    "cloud_zone":      ("cloud_zone",      ["x", "y", "w", "h"]),
    # 構造図（diagrams.py の既存パーツ）
    "cards":        ("cards",        ["x", "y", "w", "h", "items"]),
    "flow":         ("flow",         ["x", "y", "w", "h", "items"]),
    "hbars":        ("hbars",        ["x", "y", "w", "items"]),
    "metric":       ("metric",       ["x", "y", "w", "h", "value", "caption"]),
    # 表・グラフ（charts.py）。pie は画像で貼るが、--dry-run では
    # プレースホルダに置き換えて自分で座標検査を通す
    "table":         ("table",         ["x", "y", "w", "headers", "rows"]),
    "vbars":         ("vbars",         ["x", "y", "w", "h", "items"]),
    "vbars_grouped": ("vbars_grouped", ["x", "y", "w", "h", "categories", "series"]),
    "vbars_stacked": ("vbars_stacked", ["x", "y", "w", "h", "categories", "series"]),
    "linechart":     ("linechart",     ["x", "y", "w", "h", "labels", "series"]),
    "pie":           ("pie",           ["x", "y", "size", "items"]),
    # ビジネスフレームワーク図（patterns.py・図形だけで描く。ネットワーク不要）
    "posmap":         ("posmap",         ["x", "y", "w", "h", "points"]),
    "gantt":          ("gantt",          ["x", "y", "w", "h", "columns", "rows"]),
    "orgchart":       ("orgchart",       ["x", "y", "w", "h", "tree"]),
    "lean_canvas":    ("lean_canvas",    ["x", "y", "w", "h", "blocks"]),
    "nested_circles": ("nested_circles", ["x", "y", "w", "h", "rings"]),
    "testimonial":    ("testimonial",    ["x", "y", "w", "h", "quote", "name"]),
    # 印刷物用デッキの型（mckinsey.py・図形だけで描く。ネットワーク不要）
    "governing_message": ("governing_message", ["x", "y", "w", "text"]),
    "lead_in":           ("lead_in",           ["x", "y", "w", "text"]),
    "so_what":           ("so_what",           ["x", "y", "w", "h", "text"]),
    "source_note":       ("source_note",       ["x", "y", "w", "source"]),
    # exhibit_frame の戻り値（内側領域）は JSON からは受け取れない。枠を描き、
    # 中身は内側座標（x+0.2 / ヘッダー下 +0.45 目安）を手で合わせて別の図で描く
    "exhibit_frame":     ("exhibit_frame",     ["x", "y", "w", "h", "number", "title"]),
    "mece_tree":         ("mece_tree",         ["x", "y", "w", "h", "tree"]),
    "waterfall":         ("waterfall",         ["x", "y", "w", "h", "items"]),
    "rating_matrix":     ("rating_matrix",     ["x", "y", "w", "columns", "rows"]),
    "exec_summary":      ("exec_summary",      ["x", "y", "w", "h", "situation",
                                                "complication", "resolution"]),
    "storyline":         ("storyline",         ["x", "y", "w", "titles"]),
    "ghost":             ("ghost",             ["x", "y", "w", "h", "slides"]),
    # コードサンプル（diagrams.py。等幅 + シンタックスハイライト。ネットワーク不要）
    "code_block":   ("code_block",   ["x", "y", "w", "h", "code"]),
    # 画像（images.py）
    "image":        ("image",        ["x", "y", "w", "h", "source"]),
    "aiImage":      ("ai_image",     ["x", "y", "w", "h", "prompt"]),
}

# API を呼ぶ（＝ --dry-run では実行できない）type
NETWORK_FIGURES = {"image", "aiImage"}

# Slides のテーブル行が実際に取る最小の高さ（インチ・実測）。`minRowHeight` を
# これより小さくしても行は縮まないので、高さの見積もりはこの値で下から抑える
MIN_TABLE_ROW_H = 0.28


def _snake(key: str) -> str:
    out = []
    for ch in key:
        if ch.isupper():
            out.append("_")
            out.append(ch.lower())
        else:
            out.append(ch)
    return "".join(out)


def _figure_args(fig: dict) -> tuple[list, dict]:
    """図のブロックを (位置引数, キーワード引数) に振り分ける。"""
    _, order = FIGURES[fig["type"]]
    args = [fig[k] for k in order if k in fig]
    kwargs = {_snake(k): v for k, v in fig.items()
              if k != "type" and k not in order}
    return args, kwargs


def draw_figures(canvas, figures: list, *, skip_network: bool = False) -> None:
    """figures ブロックを Canvas に描く。"""
    for fig in figures:
        kind = fig["type"]
        if skip_network and kind in NETWORK_FIGURES:
            continue
        method, _ = FIGURES[kind]
        args, kwargs = _figure_args(fig)
        getattr(canvas, method)(*args, **kwargs)


def validate_figures(spec: dict, page: dict) -> list[str]:
    """figures ブロックを、API を呼ばずに検証する。"""
    problems = []
    pw = page.get("widthInches", 10.0)
    ph = page.get("heightInches", 5.625)
    for i, s in enumerate(spec.get("slides", [])):
        figs = s.get("figures")
        if figs is None:
            continue
        if not isinstance(figs, list):
            problems.append(f"slides[{i}]: 'figures' は配列である必要があります")
            continue
        for j, fig in enumerate(figs):
            where = f"slides[{i}].figures[{j}]"
            if not isinstance(fig, dict) or "type" not in fig:
                problems.append(f"{where}: 'type' がありません")
                continue
            kind = fig["type"]
            if kind not in FIGURES:
                problems.append(
                    f"{where}: 未知の type '{kind}'（利用可能: {sorted(FIGURES)}）")
                continue
            _, order = FIGURES[kind]
            missing = [k for k in order if k not in fig]
            if missing:
                problems.append(f"{where}: type '{kind}' に必要なキーがありません: {missing}")
                continue
            for k in ("x", "y", "w", "h"):
                if k in fig and not isinstance(fig[k], (int, float)):
                    problems.append(f"{where}: '{k}' は数値（インチ）である必要があります")
            # "size" が空間量（インチ）なのは位置引数に size を持つ type
            # （icon 系・pie）だけ。table 等ではフォントサイズ（pt）なので、
            # 高さの代わりに使うと 8.5pt を 8.5in と誤読してしまう
            spatial_size = fig.get("size", 0) if "size" in order else 0
            x, y = fig.get("x", 0), fig.get("y", 0)
            w = fig.get("w", spatial_size)
            h = fig.get("h", spatial_size)
            # 表は h を宣言しない。行数から見積もる。Slides のテーブル行には
            # フォントに応じた最小内寸があり、row_h をそれ未満にしても縮まない
            # （実測 ≒ 0.28in）。折り返せばさらに伸びるので、これは下限の見積もり
            if kind == "table" and isinstance(fig.get("rows"), list):
                rh = max(fig.get("rowH", fig.get("row_h", 0.34)), MIN_TABLE_ROW_H)
                hh = max(fig.get("headerH", fig.get("header_h", 0.38)), MIN_TABLE_ROW_H)
                h = hh + rh * len(fig["rows"])
            if isinstance(x, (int, float)) and isinstance(w, (int, float)):
                if x < 0 or x + w > pw + 0.01:
                    problems.append(
                        f"{where}: 横方向がページ({pw}in)からはみ出します"
                        f"（x={x} w={w} → 右端 {x + w:.2f}in）")
            if isinstance(y, (int, float)) and isinstance(h, (int, float)):
                if y < 0 or y + h > ph + 0.01:
                    problems.append(
                        f"{where}: 縦方向がページ({ph}in)からはみ出します"
                        f"（y={y} h={h} → 下端 {y + h:.2f}in）")
    return problems


class _StubDeck:
    """--dry-run で Canvas を動かすためのダミー。API は一切呼ばない。"""

    # ブランドアイコンは画像なので実物を取りに行けない。Canvas 側はこの旗を見て
    # 同じ大きさの矩形に置き換え、座標の検査だけ通す
    dry = True

    def __init__(self):
        self.requests: list[dict] = []
        self.assets = None
        self.image_fixups: list[tuple] = []


def audit_figures(template: dict, spec: dict) -> list[str]:
    """figures を実際に座標へ展開し、重なり・文字溢れを API 抜きで検査する。

    生成してサムネイルを見るまで気づけない不具合を、仕様の段階で拾う。
    画像は実物を取りに行く必要があるためこの検査からは外れる。
    """
    from diagrams import Canvas  # 遅延 import（--dry-run 以外では毎回は要らない）

    out = []
    for i, s in enumerate(spec.get("slides", [])):
        figs = s.get("figures")
        if not figs:
            continue
        canvas = Canvas(_StubDeck(), f"dry_{i}", template)
        try:
            draw_figures(canvas, figs, skip_network=True)
        except Exception as e:  # 引数の不整合はここで初めて分かることがある
            out.append(f"slides[{i}]: 図の描画に失敗しました: {type(e).__name__}: {e}")
            continue
        for msg in (canvas.audit_bounds() + canvas.audit_connectors()
                    + canvas.audit_overlaps() + canvas.audit_text_fit()):
            out.append(f"slides[{i}]: {msg}")
    return out


# ---------- 仕様の検証と組み立て ----------

def validate_spec(template: dict, spec: dict) -> list[str]:
    """デッキ仕様をテンプレートと突き合わせ、問題点のリストを返す（空なら OK）。"""
    problems = []
    slides = spec.get("slides")
    if not isinstance(slides, list) or not slides:
        return ["spec に slides 配列がありません"]

    layouts = template["layouts"]
    roles = template.get("roles", {})
    for i, s in enumerate(slides):
        where = f"slides[{i}]"
        key = s.get("layout")
        if not key:
            problems.append(f"{where}: 'layout' がありません")
            continue
        resolved = roles.get(key, key)
        layout = layouts.get(resolved)
        if not layout:
            problems.append(
                f"{where}: レイアウト '{key}' を解決できません "
                f"(ロール: {sorted(roles)} / キー: {sorted(layouts)})"
            )
            continue
        declared = layout.get("placeholders", [])
        for field, ph in (("title", "TITLE"), ("subtitle", "SUBTITLE")):
            if s.get(field) is not None and ph not in declared:
                problems.append(
                    f"{where}: レイアウト '{key}' ({layout['displayName']}) は "
                    f"{ph} を持たないのに '{field}' が指定されています（保持: {declared}）"
                )
        if s.get("body") is not None and s.get("bodies") is not None:
            problems.append(f"{where}: 'body' と 'bodies' は同時に指定できません")
            continue
        bodies = s.get("bodies")
        if bodies is None and s.get("body") is not None:
            bodies = [s["body"]]
        if bodies is not None:
            if not isinstance(bodies, list):
                problems.append(f"{where}: 'bodies' は配列である必要があります")
                continue
            slots = [p for p in declared if p.split("#")[0] == "BODY"]
            if not slots:
                problems.append(
                    f"{where}: レイアウト '{key}' ({layout['displayName']}) は "
                    f"BODY を持たないのに本文が指定されています（保持: {declared}）"
                )
            elif len(bodies) > len(slots):
                problems.append(
                    f"{where}: レイアウト '{key}' ({layout['displayName']}) の BODY は "
                    f"{len(slots)} 枠ですが {len(bodies)} 個指定されています（保持: {declared}）"
                )
    return problems


def build_from_spec(deck: TemplateDeck, spec: dict) -> list[str]:
    """spec からスライドを積む。図を描いた場合は検査結果を返す。"""
    defaults = spec.get("defaults", {})
    warnings: list[str] = []
    for i, s in enumerate(spec.get("slides", [])):
        ref = deck.add_slide(
            s["layout"],
            title=s.get("title"),
            subtitle=s.get("subtitle"),
            body=s.get("body"),
            bodies=s.get("bodies"),
            notes=s.get("notes"),
            body_font_size=s.get("bodyFontSize", defaults.get("bodyFontSize")),
            body_line_spacing=s.get("bodyLineSpacing", defaults.get("bodyLineSpacing")),
        )
        figs = s.get("figures")
        if not figs:
            continue
        from diagrams import Canvas  # 図を使う spec のときだけ読み込む
        canvas = Canvas(deck, ref["slideId"], deck.template)
        draw_figures(canvas, figs)
        for msg in (canvas.audit_bounds() + canvas.audit_connectors()
                    + canvas.audit_overlaps() + canvas.audit_text_fit()):
            warnings.append(f"slides[{i}] ({s.get('title') or s['layout']}): {msg}")
    return warnings


def main() -> int:
    p = argparse.ArgumentParser(description="テンプレートからプレゼンテーションを生成する")
    p.add_argument("--template", required=True, help="template.json のパス")
    p.add_argument("--spec", required=True, help="デッキ仕様 JSON のパス")
    p.add_argument("--title", help="生成するプレゼンテーションのタイトル（既定は spec.title）")
    p.add_argument("--folder", help="出力先 Drive フォルダの URL または ID")
    p.add_argument("--dry-run", action="store_true", help="API を呼ばず仕様の検証だけ行う")
    p.add_argument("--no-page-numbers", action="store_true", help="ページ番号を描画しない")
    p.add_argument("--keep-existing", action="store_true", help="テンプレート同梱スライドを残す")
    p.add_argument("--strict", action="store_true",
                   help="図の検査（重なり・文字溢れ）で 1 件でも出たら失敗にする")
    args = p.parse_args()

    template = load_template(args.template)
    with open(args.spec) as f:
        spec = json.load(f)

    problems = validate_spec(template, spec)
    problems += validate_figures(spec, template.get("pageSize", {}))
    if problems:
        print("仕様に問題があります:", file=sys.stderr)
        for msg in problems:
            print(f"  - {msg}", file=sys.stderr)
        return 1

    title = args.title or spec.get("title")
    if not title:
        print("タイトルがありません（--title か spec.title を指定してください）", file=sys.stderr)
        return 1

    if args.dry_run:
        print(f"OK: {len(spec['slides'])} 枚のスライド仕様はテンプレートと整合しています")
        for i, s in enumerate(spec["slides"], 1):
            resolved = template.get("roles", {}).get(s["layout"], s["layout"])
            n_fig = len(s.get("figures") or [])
            extra = f"  + 図 {n_fig} 個" if n_fig else ""
            print(f"  {i:2d}. {s['layout']:24s} -> "
                  f"{template['layouts'][resolved]['displayName']}{extra}")
        findings = audit_figures(template, spec)
        if findings:
            print(f"\n図の検査で {len(findings)} 件（画像は実物が要るため対象外）:",
                  file=sys.stderr)
            for msg in findings:
                print(f"  - {msg}", file=sys.stderr)
            return 1 if args.strict else 0
        if any(s.get("figures") for s in spec["slides"]):
            print("図の検査（コネクタ・重なり・文字溢れ）: 問題なし")
        return 0

    deck = TemplateDeck.create(
        template, title=title, folder=args.folder, keep_existing=args.keep_existing
    )
    warnings = build_from_spec(deck, spec)
    if not args.no_page_numbers:
        n = deck.add_page_numbers()
        print(f"  page numbers: {n} slides")
    url = deck.commit()
    print(f"Done! {len(deck.slide_ids)} slides created.")
    if warnings:
        print(f"\n図の検査で {len(warnings)} 件:", file=sys.stderr)
        for msg in warnings:
            print(f"  - {msg}", file=sys.stderr)
    print(f"Open: {url}")
    return 1 if (warnings and args.strict) else 0


if __name__ == "__main__":
    sys.exit(main())
