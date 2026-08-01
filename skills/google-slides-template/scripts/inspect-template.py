#!/usr/bin/env python3
"""Google Slides のテンプレート（マスタースライド）を解析して template.json を生成する。

    # 解析して人間可読なレポートを表示
    python scripts/inspect-template.py <URL または ID>

    # template.json を書き出す
    python scripts/inspect-template.py <URL> --emit templates/my-brand.json --name my-brand

    # レイアウトのサムネイルも取得する（視覚確認用）
    python scripts/inspect-template.py <URL> --thumbnails out/thumbs

生成された template.json の `roles` は表示名とプレースホルダ構成からの**推測**なので、
サムネイルを見て必ず人間が確認・修正すること。
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _auth  # noqa: E402

# レイアウト表示名からセマンティックロールを推測するためのキーワード
ROLE_KEYWORDS = {
    "COVER": ["title slide", "cover", "表紙", "hyoshi"],
    "SECTION": ["section", "divider", "chapter", "中扉", "sub section", "agenda"],
    "CLOSING": ["clos", "end", "thank", "last", "裏表紙", "終"],
    "BLANK": ["blank", "white", "empty", "白紙"],
}


def slugify(name: str, used: set[str]) -> str:
    """表示名を UPPER_SNAKE のキーに変換する。衝突時は連番を付ける。"""
    key = re.sub(r"[^A-Za-z0-9]+", "_", name).strip("_").upper() or "LAYOUT"
    if key[0].isdigit():
        key = "L_" + key
    base, n = key, 2
    while key in used:
        key, n = f"{base}_{n}", n + 1
    used.add(key)
    return key


def geometry(el: dict) -> dict:
    """pageElement の位置とサイズをインチで返す。"""
    t = el.get("transform", {}) or {}
    sz = el.get("size", {}) or {}
    w = sz.get("width", {}).get("magnitude", 0) * t.get("scaleX", 1)
    h = sz.get("height", {}).get("magnitude", 0) * t.get("scaleY", 1)
    return {
        "x": round(_auth.to_inches(t.get("translateX", 0)), 3),
        "y": round(_auth.to_inches(t.get("translateY", 0)), 3),
        "w": round(_auth.to_inches(w), 3),
        "h": round(_auth.to_inches(h), 3),
    }


def opaque_hex(color_container: dict | None) -> str | None:
    """色を hex か `theme:XXX` に解決する。

    Slides API は入れ子の形が場所ごとに違う:
      solidFill      -> {"color": {"rgbColor"|"themeColor": …}, "alpha": 1}
      foregroundColor-> {"opaqueColor": {"rgbColor"|"themeColor": …}}
    どちらでも受けられるように順に剥がす。
    """
    if not color_container:
        return None
    c = color_container
    for key in ("opaqueColor", "color"):
        if isinstance(c, dict) and key in c:
            c = c[key]
    if not isinstance(c, dict):
        return None
    if "rgbColor" in c:
        return _auth.rgb_to_hex(c["rgbColor"])
    if "themeColor" in c:
        return f"theme:{c['themeColor']}"
    return None


def placeholder_text_style(shape: dict) -> dict | None:
    """プレースホルダの既定テキストスタイル（第1階層）を取り出す。"""
    lists = (shape.get("text") or {}).get("lists") or {}
    for lst in lists.values():
        lvl0 = (lst.get("nestingLevel") or {}).get("0")
        if lvl0 is None:
            # nestingLevel のキーは "0" ではなく 0 相当の順序で来ることがある
            levels = lst.get("nestingLevel") or {}
            lvl0 = levels.get(0) or (list(levels.values())[0] if levels else None)
        bs = (lvl0 or {}).get("bulletStyle") or {}
        style = {}
        if bs.get("fontFamily"):
            style["fontFamily"] = bs["fontFamily"]
        if bs.get("fontSize"):
            style["fontSize"] = bs["fontSize"].get("magnitude")
        if bs.get("bold") is not None:
            style["bold"] = bs["bold"]
        fg = opaque_hex(bs.get("foregroundColor"))
        if fg:
            style["color"] = fg
        if style:
            return style
    return None


def paragraph_alignment(shape: dict) -> str | None:
    for te in (shape.get("text") or {}).get("textElements", []):
        pm = te.get("paragraphMarker")
        if pm and pm.get("style", {}).get("alignment"):
            return pm["style"]["alignment"]
    return None


PLACEHOLDER_ELEMENT_KEY = {
    "TITLE": "title",
    "CENTERED_TITLE": "title",
    "SUBTITLE": "subtitle",
    "BODY": "body",
    "SLIDE_NUMBER": "slideNumber",
}


def analyze_page(page: dict) -> dict:
    """レイアウト/マスター1ページ分の構造を抽出する。"""
    placeholders: list[str] = []
    elements: dict = {}
    text_styles: dict = {}
    decorations: list[dict] = []

    for el in page.get("pageElements", []):
        shape = el.get("shape")
        if shape and shape.get("placeholder"):
            ph = shape["placeholder"]
            ptype = ph.get("type")
            idx = ph.get("index", 0)
            # 2カラム/3カラムのレイアウトは BODY を index 0,1,2 と複数持つ。
            # index 0 は "BODY"、それ以降は "BODY#1" のように区別して全て記録する。
            name = ptype if idx == 0 else f"{ptype}#{idx}"
            if name in placeholders:
                continue
            placeholders.append(name)
            base = PLACEHOLDER_ELEMENT_KEY.get(ptype)
            if base:
                key = base if idx == 0 else f"{base}#{idx}"
                geo = geometry(el)
                align = paragraph_alignment(shape)
                if align:
                    geo["align"] = align
                elements[key] = geo
                st = placeholder_text_style(shape)
                if st:
                    text_styles[key] = st
            continue

        # プレースホルダ以外＝レイアウトが持つ装飾要素。
        # 要素型は shape / image / line のほか table / video / line / wordArt /
        # sheetsChart / elementGroup があるので、決め打ちせず実際のキーから判定する。
        kind = next(
            (k for k in ("shape", "image", "line", "table", "video",
                         "wordArt", "sheetsChart", "elementGroup") if k in el),
            "unknown",
        )
        entry = {"type": kind, "objectId": el["objectId"], **geometry(el)}
        if kind == "shape":
            sp = el["shape"].get("shapeProperties", {})
            fill = opaque_hex((sp.get("shapeBackgroundFill") or {}).get("solidFill"))
            if fill:
                entry["fill"] = fill
            entry["shapeType"] = el["shape"].get("shapeType")
        elif kind == "line":
            lp = el["line"].get("lineProperties", {})
            color = opaque_hex((lp.get("lineFill") or {}).get("solidFill"))
            if color:
                entry["color"] = color
            entry["weight"] = round(lp.get("weight", {}).get("magnitude", 0) / _auth.EMU_PER_PT, 2)
        elif kind == "elementGroup":
            children = el["elementGroup"].get("children", [])
            entry["childCount"] = len(children)
            entry["childTypes"] = sorted(
                {next((k for k in ("shape", "image", "line", "table", "elementGroup")
                       if k in c), "unknown") for c in children}
            )
        decorations.append(entry)

    return {
        "placeholders": placeholders,
        "elements": elements,
        "textStyles": text_styles,
        "decorations": decorations,
    }


def guess_role(display_name: str, placeholders: list[str]) -> str | None:
    low = display_name.lower()
    for role, words in ROLE_KEYWORDS.items():
        if any(w in low for w in words):
            return role
    has = {p.split("#")[0] for p in placeholders}
    if "TITLE" in has and "SUBTITLE" in has:
        return "COVER"
    if "TITLE" in has and "BODY" in has:
        return "CONTENT"
    if "TITLE" in has:
        return "TITLE_ONLY"
    if not (has - {"SLIDE_NUMBER"}):
        return "BLANK"
    return None


def extract_colors(master: dict) -> dict:
    """マスターの colorScheme を hex 辞書にする。

    注意: colorScheme の各要素は `{"type": "...", "color": {"red":..,...}}` であり、
    `color.rgbColor` ではなく `color` 直下に RGB が入る（他の API 応答と構造が違う）。
    """
    scheme = (master.get("pageProperties") or {}).get("colorScheme") or {}
    out = {}
    for entry in scheme.get("colors", []):
        out[entry["type"].lower()] = _auth.rgb_to_hex(entry.get("color", {}))
    return out


def build_template(pres: dict, name: str, source_url: str) -> dict:
    masters = pres.get("masters", [])
    master = masters[0] if masters else {}
    page = pres.get("pageSize", {})
    w = _auth.to_inches(page.get("width", {}).get("magnitude", 0))
    h = _auth.to_inches(page.get("height", {}).get("magnitude", 0))

    colors = extract_colors(master)
    master_info = analyze_page(master) if master else {"decorations": [], "textStyles": {}}

    # マスターが複数あるプレゼンテーションもある（他ファイルからスライドを貼り付けると増える）。
    # 既定は 1 つ目だが、レイアウトごとにどのマスターに属するかを記録しておく。
    master_list = []
    for m in masters:
        mp = m.get("masterProperties", {})
        master_list.append({
            "objectId": m["objectId"],
            "displayName": mp.get("displayName"),
            "colors": extract_colors(m),
            "decorations": analyze_page(m)["decorations"],
        })

    layouts: dict = {}
    role_candidates: dict[str, list[str]] = {}
    used_keys: set[str] = set()
    for l in pres.get("layouts", []):
        lp = l.get("layoutProperties", {})
        display = lp.get("displayName") or l["objectId"]
        key = slugify(display, used_keys)
        info = analyze_page(l)
        layouts[key] = {
            "layoutId": l["objectId"],
            "displayName": display,
            "masterObjectId": lp.get("masterObjectId"),
            "placeholders": info["placeholders"],
            "hasPageNumber": "SLIDE_NUMBER" in info["placeholders"],
            "elements": info["elements"],
            "textStyles": info["textStyles"],
            "decorations": info["decorations"],
        }
        role = guess_role(display, info["placeholders"])
        if role:
            role_candidates.setdefault(role, []).append(key)

    roles = {role: keys[0] for role, keys in role_candidates.items()}

    # ページ番号の既定スタイル。マスターの SLIDE_NUMBER プレースホルダから拾えれば使う。
    pn_style = master_info.get("textStyles", {}).get("slideNumber") or {}
    page_number = {
        "font": pn_style.get("fontFamily", "Arial"),
        "fontSize": pn_style.get("fontSize", 7),
        "color": pn_style.get("color", "#666666"),
        "align": "END",
        "startAt": 1,
    }
    if str(page_number["color"]).startswith("theme:"):
        page_number["color"] = "#666666"

    return {
        "name": name,
        "displayName": pres.get("title", name),
        "sourceUrl": source_url,
        "presentationId": pres["presentationId"],
        "generationMode": "copy",
        "pageSize": {
            "widthInches": round(w, 3),
            "heightInches": round(h, 3),
            "aspectRatio": f"{round(w / h, 3)}:1" if h else None,
        },
        "existingSlideIds": [s["objectId"] for s in pres.get("slides", [])],
        "__existingSlideIds_note": "複製直後に削除するテンプレート同梱スライド。テンプレート側を編集したら再解析すること",
        "colors": colors,
        "__colors_note": "masters[0] の colorScheme。マスターが複数ある場合は masters[].colors も確認すること",
        "masters": master_list,
        "pageNumber": page_number,
        "__pageNumber_note": "Slides API は SLIDE_NUMBER プレースホルダを生成できないため、build-deck.py がこのスタイルでテキストボックスを描画する",
        "masterDecorations": master_info.get("decorations", []),
        "__masterDecorations_note": "マスターが全ページに敷く要素（ロゴ・著作権表記等）。複製方式では自動継承されるので自前描画しないこと",
        "roles": roles,
        "__roles_note": "表示名とプレースホルダ構成からの推測。サムネイルを見て必ず人間が確認・修正すること",
        "roleCandidates": role_candidates,
        "layouts": layouts,
    }


def print_report(t: dict) -> None:
    print(f"=== {t['displayName']} ===")
    print(f"  id       : {t['presentationId']}")
    ps = t["pageSize"]
    print(f"  page size: {ps['widthInches']} x {ps['heightInches']} in")
    print(f"  colors   : " + ", ".join(f"{k}={v}" for k, v in list(t["colors"].items())[:10]))
    print(f"  既存スライド: {len(t['existingSlideIds'])} 枚（複製時に削除）")
    ms = t.get("masters", [])
    if len(ms) > 1:
        print(f"\n  ⚠ マスターが {len(ms)} 個あります（通常は 1 個）:")
        for m in ms:
            n = sum(1 for l in t["layouts"].values() if l.get("masterObjectId") == m["objectId"])
            print(f"      {m['objectId']:22s} {m['displayName']!r} レイアウト {n} 種")
        print("      別ファイルからスライドを貼り付けると増えます。テンプレートとして使うなら")
        print("      どちらのマスター系統を使うか決め、roles をそちらに寄せること。")
    print(f"\n--- レイアウト {len(t['layouts'])} 種 ---")
    for key, l in t["layouts"].items():
        role = next((r for r, k in t["roles"].items() if k == key), "")
        mtag = ""
        if len(ms) > 1:
            idx = next((i for i, m in enumerate(ms, 1)
                        if m["objectId"] == l.get("masterObjectId")), "?")
            mtag = f"M{idx} "
        print(
            f"  {mtag}{key:26s} {l['layoutId']:20s} {'[' + role + ']' if role else '':16s} "
            f"{l['displayName']!r}"
        )
        print(f"      placeholders={l['placeholders']} decorations={len(l['decorations'])}")
        for ek, geo in l["elements"].items():
            st = l["textStyles"].get(ek, {})
            desc = " ".join(f"{k}={v}" for k, v in st.items())
            print(f"      {ek:12s} x={geo['x']:.3f} y={geo['y']:.3f} "
                  f"w={geo['w']:.3f} h={geo['h']:.3f} {desc}")
    print(f"\n--- ロール推測 ---")
    for role, keys in t["roleCandidates"].items():
        mark = "" if len(keys) == 1 else f"  ← 候補 {len(keys)} 件、要確認"
        print(f"  {role:14s} -> {t['roles'][role]}{mark}")
        if len(keys) > 1:
            print(f"                 候補: {keys}")
    missing = [r for r in ("COVER", "SECTION", "CONTENT", "CLOSING") if r not in t["roles"]]
    if missing:
        print(f"  未割当のロール: {missing}")


def fetch_thumbnails(slides, pres_id: str, template: dict, out_dir: str) -> None:
    os.makedirs(out_dir, exist_ok=True)
    for key, l in template["layouts"].items():
        try:
            res = slides.presentations().pages().getThumbnail(
                presentationId=pres_id,
                pageObjectId=l["layoutId"],
                thumbnailProperties_mimeType="PNG",
                thumbnailProperties_thumbnailSize="MEDIUM",
            ).execute()
            path = os.path.join(out_dir, f"{key}.png")
            urllib.request.urlretrieve(res["contentUrl"], path)
            print(f"  {path}")
        except Exception as e:  # noqa: BLE001
            print(f"  FAIL {key}: {str(e)[:120]}", file=sys.stderr)


def main() -> int:
    p = argparse.ArgumentParser(description="Google Slides テンプレートを解析する")
    p.add_argument("source", help="テンプレートの URL または プレゼンテーション ID")
    p.add_argument("--emit", help="template.json の出力先パス")
    p.add_argument("--name", help="テンプレート ID（英小文字・ハイフン）。既定は --emit のファイル名")
    p.add_argument("--thumbnails", help="レイアウトのサムネイル出力ディレクトリ")
    p.add_argument("--raw", help="API の生レスポンスを書き出すパス（デバッグ用）")
    args = p.parse_args()

    pres_id = _auth.presentation_id(args.source)
    slides, _ = _auth.services()
    pres = slides.presentations().get(presentationId=pres_id).execute()

    if args.raw:
        with open(args.raw, "w") as f:
            json.dump(pres, f, ensure_ascii=False, indent=2)
        print(f"raw -> {args.raw}")

    name = args.name or (
        os.path.splitext(os.path.basename(args.emit))[0] if args.emit else "template"
    )
    template = build_template(pres, name, args.source)
    print_report(template)

    if args.emit:
        os.makedirs(os.path.dirname(os.path.abspath(args.emit)), exist_ok=True)
        with open(args.emit, "w") as f:
            json.dump(template, f, ensure_ascii=False, indent=2)
        print(f"\ntemplate -> {args.emit}")
        print("  roles を必ず目視で確認・修正してください")

    if args.thumbnails:
        print(f"\n--- サムネイル ---")
        fetch_thumbnails(slides, pres_id, template, args.thumbnails)

    return 0


if __name__ == "__main__":
    sys.exit(main())
