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

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _auth  # noqa: E402

FILLABLE = ("TITLE", "SUBTITLE", "BODY")


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
        slides, drive = _auth.services(creds)
        src = template.get("presentationId")
        fid = _auth.folder_id(folder)

        if src:
            # マスターを複製する。装飾・ロゴ・フッターがレイアウトから継承される
            body: dict = {"name": title}
            if fid:
                body["parents"] = [fid]
            pres_id = drive.files().copy(fileId=src, body=body, fields="id").execute()["id"]
        else:
            # マスター無し。Google の既定レイアウト（predefinedLayout）で新規作成する
            pres_id = slides.presentations().create(
                body={"title": title}, fields="presentationId"
            ).execute()["presentationId"]
            if fid:
                cur = drive.files().get(fileId=pres_id, fields="parents").execute()
                drive.files().update(
                    fileId=pres_id, addParents=fid,
                    removeParents=",".join(cur.get("parents", [])), fields="id",
                ).execute()

        deck = cls(slides, drive, pres_id, template)
        if not keep_existing:
            deck._delete_existing_slides()
        return deck

    def _delete_existing_slides(self) -> None:
        """複製直後に残っているテンプレート同梱スライドを削除する。"""
        pres = self.slides.presentations().get(
            presentationId=self.presentation_id, fields="slides.objectId"
        ).execute()
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
        return f"{prefix}_{self._counter:03d}"

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
        declared = list(layout.get("placeholders", []))
        # drawText を持つレイアウトは、プレースホルダの代わりに座標指定のテキストボックスを
        # 描く。Slides API に要素のサイズを変更するリクエストが無いため、既定レイアウト
        # （predefinedLayout）では文字幅を制御できず折り返してしまう。これを避ける手段。
        drawn = layout.get("drawText", {})
        for key in drawn:
            name = key.upper().replace("X", "#") if "x" in key and key[-1].isdigit() else key.upper()
            if name not in declared:
                declared.append(name)

        if body is not None and bodies is not None:
            raise ValueError("body と bodies は同時に指定できません")
        if body is not None:
            bodies = [body]

        # リクエストを積む前に検証する。失敗しても中途半端な状態を残さないため。
        for ph_type, value in (("TITLE", title), ("SUBTITLE", subtitle)):
            if value is not None and ph_type not in declared:
                raise ValueError(
                    f"レイアウト '{layout_key}' ({layout['displayName']}) は "
                    f"{ph_type} を持ちません。保持しているのは {declared}"
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
        # 既定レイアウトでは論理名と API のプレースホルダ型が違うことがある
        # （例: predefinedLayout=TITLE の見出しは CENTERED_TITLE）
        type_map = layout.get("placeholderTypeMap", {})
        # SLIDE_NUMBER はマッピングしても API に無視されるため対象外（add_page_numbers で描画）
        # drawText で描くものはプレースホルダを割り当てない
        for name in [t for t in declared
                     if t.split("#")[0] in FILLABLE
                     and t.replace("#", "x").lower() not in drawn]:
            ph_type, _, idx = name.partition("#")
            idx = int(idx) if idx else 0
            safe = name.replace("#", "x").lower()
            oid = self._next_id(f"{resolved_key.lower()}_{safe}")
            ph_ids[name] = oid
            mappings.append(
                {"layoutPlaceholder": {"type": type_map.get(ph_type, ph_type),
                                       "index": idx},
                 "objectId": oid}
            )

        if layout.get("layoutId"):
            layout_ref = {"layoutId": layout["layoutId"]}
        elif layout.get("predefinedLayout"):
            layout_ref = {"predefinedLayout": layout["predefinedLayout"]}
        else:
            raise ValueError(
                f"レイアウト '{layout_key}' に layoutId も predefinedLayout もありません")
        create_req: dict = {
            "objectId": slide_id,
            "slideLayoutReference": layout_ref,
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

        # drawText 指定のものは座標指定のテキストボックスとして描く
        for name, value in list(fills):
            key = name.replace("#", "x").lower()
            spec = drawn.get(key)
            if value is None or spec is None:
                continue
            text = "\n".join(value) if isinstance(value, list) else value
            self._draw_text_box(slide_id, spec, text, f"{resolved_key.lower()}_{key}")
            fills.remove((name, value))
            if (name, value) in filled_bodies:
                filled_bodies.remove((name, value))

        for name, value in fills:
            if value is None:
                continue
            text = "\n".join(value) if isinstance(value, list) else value
            self.requests.append(
                {"insertText": {"objectId": ph_ids[name], "text": text}}
            )

        # 既定レイアウト（predefinedLayout）は Google の想定する位置・文字サイズのままなので、
        # template.json の elements / textStyles に寄せる。マスター複製の場合は
        # レイアウト側が既に正しいので applyElementGeometry を立てない。
        #
        # Slides API に「要素のサイズを後から変える」リクエストは無いため、
        # 位置（ABSOLUTE な translate）・上寄せ・文字サイズ・揃えの4点で見た目を合わせる。
        # プレースホルダの枠は透明なので、枠が大きいままでも実害はない。
        if layout.get("applyElementGeometry"):
            for name in ph_ids:
                if dict(fills).get(name) is None:
                    continue
                key = name.split("#")[0].lower()
                el = layout.get("elements", {}).get(key)
                if not el:
                    continue
                oid = ph_ids[name]
                self.requests.append({"updatePageElementTransform": {
                    "objectId": oid,
                    "applyMode": "ABSOLUTE",
                    "transform": {
                        "scaleX": 1, "scaleY": 1,
                        "translateX": _auth.inches(el["x"]),
                        "translateY": _auth.inches(el["y"]),
                        "unit": "EMU",
                    },
                }})
                self.requests.append({"updateShapeProperties": {
                    "objectId": oid,
                    "shapeProperties": {"contentAlignment": "TOP"},
                    "fields": "contentAlignment",
                }})
                st = layout.get("textStyles", {}).get(key, {})
                style, sfields = {}, []
                if st.get("fontSize"):
                    style["fontSize"] = {"magnitude": st["fontSize"], "unit": "PT"}
                    sfields.append("fontSize")
                if st.get("fontFamily"):
                    style["fontFamily"] = st["fontFamily"]
                    sfields.append("fontFamily")
                if "bold" in st:
                    style["bold"] = st["bold"]
                    sfields.append("bold")
                if sfields:
                    self.requests.append({"updateTextStyle": {
                        "objectId": oid, "style": style,
                        "textRange": {"type": "ALL"}, "fields": ",".join(sfields),
                    }})
                if el.get("align"):
                    self.requests.append({"updateParagraphStyle": {
                        "objectId": oid, "style": {"alignment": el["align"]},
                        "textRange": {"type": "ALL"}, "fields": "alignment",
                    }})

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

    def _draw_text_box(self, slide_id: str, spec: dict, text: str, prefix: str) -> str:
        """座標・書式を完全に指定したテキストボックスを描く。

        既定レイアウトのプレースホルダは幅を変更できないため、タイトルなどを
        確実に 1 行に収めたい場合はプレースホルダを使わずこちらで描く。
        spec は {x, y, w, h, size, bold, align, valign, color, lineSpacing}。
        """
        oid = self._next_id(prefix)
        self.requests.append({"createShape": {
            "objectId": oid, "shapeType": "TEXT_BOX",
            "elementProperties": {
                "pageObjectId": slide_id,
                "size": {
                    "width": {"magnitude": _auth.inches(spec["w"]), "unit": "EMU"},
                    "height": {"magnitude": _auth.inches(spec["h"]), "unit": "EMU"},
                },
                "transform": {
                    "scaleX": 1, "scaleY": 1,
                    "translateX": _auth.inches(spec["x"]),
                    "translateY": _auth.inches(spec["y"]),
                    "unit": "EMU",
                },
            },
        }})
        self.requests.append({"updateShapeProperties": {
            "objectId": oid,
            "shapeProperties": {"contentAlignment": spec.get("valign", "TOP")},
            "fields": "contentAlignment",
        }})
        self.requests.append({"insertText": {"objectId": oid, "text": text}})
        style = {
            "fontFamily": spec.get("fontFamily", "Noto Sans JP"),
            "fontSize": {"magnitude": spec.get("size", 14), "unit": "PT"},
            "bold": spec.get("bold", False),
        }
        fields = "fontFamily,fontSize,bold"
        if spec.get("color"):
            style["foregroundColor"] = {
                "opaqueColor": {"rgbColor": _auth.hex_to_rgb(spec["color"])}}
            fields += ",foregroundColor"
        self.requests.append({"updateTextStyle": {
            "objectId": oid, "style": style,
            "textRange": {"type": "ALL"}, "fields": fields,
        }})
        pstyle = {"alignment": spec.get("align", "START")}
        pfields = ["alignment"]
        if spec.get("lineSpacing"):
            pstyle["lineSpacing"] = spec["lineSpacing"]
            pfields.append("lineSpacing")
        self.requests.append({"updateParagraphStyle": {
            "objectId": oid, "style": pstyle,
            "textRange": {"type": "ALL"}, "fields": ",".join(pfields),
        }})
        return oid

    # ---------- ページ番号 ----------

    def add_page_numbers(self, start: int | None = None) -> int:
        """ページ番号をテキストボックスで描画し、描画枚数を返す。

        Slides API は SLIDE_NUMBER プレースホルダを生成できない（createSlide の
        placeholderIdMappings に指定してもエラーにならず黙って無視される）ため、
        レイアウトの slideNumber 座標に合わせて自前で描画する。
        """
        cfg = self.template.get("pageNumber", {})
        start = cfg.get("startAt", 1) if start is None else start
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
        for i in range(0, len(self.requests), chunk_size):
            chunk = self.requests[i : i + chunk_size]
            self.slides.presentations().batchUpdate(
                presentationId=self.presentation_id, body={"requests": chunk}
            ).execute()
            print(f"  batch {i // chunk_size + 1}: {len(chunk)} requests")
        self.requests = []
        if self._notes:
            self._write_notes()
        return f"https://docs.google.com/presentation/d/{self.presentation_id}/edit"

    def _write_notes(self) -> None:
        """スピーカーノートを書き込む。

        ノートの objectId はスライド作成後にしか判明しないため、本体の batchUpdate を
        実行してから presentation を取り直して 2 回目の batchUpdate を投げる。
        """
        pres = self.slides.presentations().get(
            presentationId=self.presentation_id,
            fields="slides(objectId,slideProperties.notesPage.notesProperties.speakerNotesObjectId)",
        ).execute()
        note_ids = {
            s["objectId"]: (
                s.get("slideProperties", {})
                .get("notesPage", {})
                .get("notesProperties", {})
                .get("speakerNotesObjectId")
            )
            for s in pres.get("slides", [])
        }
        reqs = []
        for slide_id, text in self._notes:
            oid = note_ids.get(slide_id)
            if not oid:
                print(f"  warn: {slide_id} のノート枠が見つからずスキップしました", file=sys.stderr)
                continue
            reqs.append({"insertText": {"objectId": oid, "text": text}})
        if reqs:
            self.slides.presentations().batchUpdate(
                presentationId=self.presentation_id, body={"requests": reqs}
            ).execute()
            print(f"  speaker notes: {len(reqs)} slides")
        self._notes = []


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


def build_from_spec(deck: TemplateDeck, spec: dict) -> None:
    defaults = spec.get("defaults", {})
    for s in spec.get("slides", []):
        deck.add_slide(
            s["layout"],
            title=s.get("title"),
            subtitle=s.get("subtitle"),
            body=s.get("body"),
            bodies=s.get("bodies"),
            notes=s.get("notes"),
            body_font_size=s.get("bodyFontSize", defaults.get("bodyFontSize")),
            body_line_spacing=s.get("bodyLineSpacing", defaults.get("bodyLineSpacing")),
        )


def main() -> int:
    p = argparse.ArgumentParser(description="テンプレートからプレゼンテーションを生成する")
    p.add_argument("--template", required=True, help="template.json のパス")
    p.add_argument("--spec", required=True, help="デッキ仕様 JSON のパス")
    p.add_argument("--title", help="生成するプレゼンテーションのタイトル（既定は spec.title）")
    p.add_argument("--folder", help="出力先 Drive フォルダの URL または ID")
    p.add_argument("--dry-run", action="store_true", help="API を呼ばず仕様の検証だけ行う")
    p.add_argument("--no-page-numbers", action="store_true", help="ページ番号を描画しない")
    p.add_argument("--keep-existing", action="store_true", help="テンプレート同梱スライドを残す")
    args = p.parse_args()

    template = load_template(args.template)
    with open(args.spec) as f:
        spec = json.load(f)

    problems = validate_spec(template, spec)
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
            print(f"  {i:2d}. {s['layout']:24s} -> {template['layouts'][resolved]['displayName']}")
        return 0

    deck = TemplateDeck.create(
        template, title=title, folder=args.folder, keep_existing=args.keep_existing
    )
    build_from_spec(deck, spec)
    if not args.no_page_numbers:
        n = deck.add_page_numbers()
        print(f"  page numbers: {n} slides")
    url = deck.commit()
    print(f"Done! {len(deck.slide_ids)} slides created.")
    print(f"Open: {url}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
