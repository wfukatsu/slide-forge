#!/usr/bin/env python3
"""Analyzes a Google Slides template (master slides) and generates template.json.

    # Analyze and print a human-readable report
    python scripts/inspect_template.py <URL or ID>

    # Write out template.json
    python scripts/inspect_template.py <URL> --emit templates/my-brand.json --name my-brand

    # Also fetch layout thumbnails (for visual verification)
    python scripts/inspect_template.py <URL> --thumbnails out/thumbs

The generated template.json's `roles` are only a **guess** based on display
names and placeholder composition, so always verify and fix them by looking
at the thumbnails. When overwriting an existing file, the verified `roles`
are carried over (pass `--reset-roles` only if you want to overwrite with
fresh guesses).

`layouts.*.imageSlots` marks "where the template wants to place an image."
In a deck spec, omitting x/y/w/h fits into this slot (see
`references/images.md`).
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
from _i18n import t, register  # noqa: E402

register({
    "Analyze a Google Slides template": "Google Slides テンプレートを解析する",
    "URL or presentation ID of the template": "テンプレートの URL または プレゼンテーション ID",
    "output path for template.json": "template.json の出力先パス",
    "template ID (lowercase letters and hyphens); defaults to the --emit filename":
        "テンプレート ID（英小文字・ハイフン）。既定は --emit のファイル名",
    "output directory for layout thumbnails": "レイアウトのサムネイル出力ディレクトリ",
    "path to dump the raw API response (for debugging)":
        "API の生レスポンスを書き出すパス（デバッグ用）",
    "  existing slides: {n} (deleted on copy)": "  既存スライド: {n} 枚（複製時に削除）",
    "\n  ⚠ This presentation has {n} masters (usually 1):":
        "\n  ⚠ マスターが {n} 個あります（通常は 1 個）:",
    "      {oid:22s} {name!r} {n} layouts": "      {oid:22s} {name!r} レイアウト {n} 種",
    "      Pasting slides from another file adds masters. To use this as a template,":
        "      別ファイルからスライドを貼り付けると増えます。テンプレートとして使うなら",
    "      pick one master lineage and align the roles to it.":
        "      どちらのマスター系統を使うか決め、roles をそちらに寄せること。",
    "\n--- {n} layouts ---": "\n--- レイアウト {n} 種 ---",
    "\n--- Role guesses ---": "\n--- ロール推測 ---",
    "  ← {n} candidates, needs review": "  ← 候補 {n} 件、要確認",
    "                 candidates: {keys}": "                 候補: {keys}",
    "  unassigned roles: {missing}": "  未割当のロール: {missing}",
    "  Always review and fix the roles by eye":
        "  roles を必ず目視で確認・修正してください",
    "\n--- Thumbnails ---": "\n--- サムネイル ---",
    " ({n} samples)": "（実例 {n} 件）",
    "      imageSlot[{n}]  x={x:.3f} y={y:.3f} w={w:.3f} h={h:.3f} "
    "aspect={a} <- {src}{extra}":
        "      画像枠[{n}]  x={x:.3f} y={y:.3f} w={w:.3f} h={h:.3f} "
        "縦横比={a} <- {src}{extra}",
    "overwrite the human-verified roles with fresh guesses":
        "人が確認した roles を推測値で上書きする",
    "  (could not read the previous file: {e})":
        "  （前回のファイルを読めませんでした: {e}）",
    "  kept from the previous file: {keys}":
        "  前回のファイルから引き継ぎ: {keys}",
    "  ⚠ these kept roles point at layouts that no longer exist: {stale}":
        "  ⚠ 引き継いだ roles のうち、存在しないレイアウトを指しているもの: {stale}",
})

# Keywords used to guess a semantic role from a layout's display name
ROLE_KEYWORDS = {
    "COVER": ["title slide", "cover", "表紙", "hyoshi"],
    "SECTION": ["section", "divider", "chapter", "中扉", "sub section", "agenda"],
    "CLOSING": ["clos", "end", "thank", "last", "裏表紙", "終"],
    "BLANK": ["blank", "white", "empty", "白紙"],
}


def slugify(name: str, used: set[str]) -> str:
    """Converts a display name into an UPPER_SNAKE key. Appends a number on collision."""
    key = re.sub(r"[^A-Za-z0-9]+", "_", name).strip("_").upper() or "LAYOUT"
    if key[0].isdigit():
        key = "L_" + key
    base, n = key, 2
    while key in used:
        key, n = f"{base}_{n}", n + 1
    used.add(key)
    return key


def geometry(el: dict) -> dict:
    """Returns a pageElement's position and size in inches."""
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
    """Resolves a color to hex or `theme:XXX`.

    The Slides API nests this differently depending on where it appears:
      solidFill      -> {"color": {"rgbColor"|"themeColor": …}, "alpha": 1}
      foregroundColor-> {"opaqueColor": {"rgbColor"|"themeColor": …}}
    Unwraps each layer in turn so both forms are handled.
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
    """Extracts a placeholder's default text style (first nesting level)."""
    lists = (shape.get("text") or {}).get("lists") or {}
    for lst in lists.values():
        lvl0 = (lst.get("nestingLevel") or {}).get("0")
        if lvl0 is None:
            # nestingLevel's key can arrive in an ordering equivalent to 0 rather than the string "0"
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

# Placeholder types that mean "place an image here."
# Collectively covers what Slides' UI creates as figure/image frames.
IMAGE_PLACEHOLDER_TYPES = {
    "PICTURE", "CLIP_ART", "DIAGRAM", "MEDIA", "OBJECT", "SLIDE_IMAGE",
}


def is_empty_image(el: dict) -> bool:
    """Is this an image element with no content (i.e. an empty frame meant
    for inserting an image)?

    Among the image elements placed on a layout, ones where `contentUrl` is
    empty don't actually render anything. They're frames the template's
    author left with the intent "put a picture here," so they're treated as
    an insertion point rather than decoration.
    """
    img = el.get("image")
    if img is None:
        return False
    return not (img.get("contentUrl") or img.get("sourceUrl"))


def analyze_page(page: dict) -> dict:
    """Extracts the structure of one layout/master page."""
    placeholders: list[str] = []
    elements: dict = {}
    text_styles: dict = {}
    decorations: list[dict] = []
    image_slots: list[dict] = []

    for el in page.get("pageElements", []):
        shape = el.get("shape")
        if shape and shape.get("placeholder"):
            ph = shape["placeholder"]
            ptype = ph.get("type")
            idx = ph.get("index", 0)
            # 2-column/3-column layouts have multiple BODY placeholders at
            # index 0, 1, 2. Index 0 is recorded as "BODY", the rest are
            # distinguished as "BODY#1" etc., and all are recorded.
            name = ptype if idx == 0 else f"{ptype}#{idx}"
            if ptype in IMAGE_PLACEHOLDER_TYPES:
                image_slots.append({
                    **geometry(el), "source": "placeholder",
                    "placeholder": ptype, "objectId": el["objectId"],
                })
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

        # An image with no content isn't decoration — it's an "image insertion frame"
        if is_empty_image(el):
            image_slots.append({
                **geometry(el), "source": "layout",
                "placeholder": None, "objectId": el["objectId"],
            })
            continue

        # Anything that isn't a placeholder = a decorative element the
        # layout carries. Besides shape / image / line, element types
        # include table / video / wordArt / sheetsChart / elementGroup, so
        # rather than hardcoding one, determine it from the actual key present.
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
        "imageSlots": image_slots,
    }


# ---------- Image insertion frames (imageSlots) ----------

def _overlap_ratio(a: dict, b: dict) -> float:
    """Returns the overlap of two frames as a ratio of the smaller area."""
    ix = max(0.0, min(a["x"] + a["w"], b["x"] + b["w"]) - max(a["x"], b["x"]))
    iy = max(0.0, min(a["y"] + a["h"], b["y"] + b["h"]) - max(a["y"], b["y"]))
    small = min(a["w"] * a["h"], b["w"] * b["h"])
    return (ix * iy) / small if small > 0 else 0.0


def collect_sample_image_boxes(pres: dict) -> dict[str, list[dict]]:
    """Collects the actual image frames placed in bundled slides, grouped
    by layout.

    The layout's empty frame sometimes only indicates "roughly around
    here"; the actual usage (the pictures in the bundled slides) is closer
    to the intended design.
    """
    out: dict[str, list[dict]] = {}
    for s in pres.get("slides", []):
        lid = (s.get("slideProperties") or {}).get("layoutObjectId")
        if not lid:
            continue
        for el in s.get("pageElements", []):
            if "image" not in el or is_empty_image(el):
                continue
            out.setdefault(lid, []).append(geometry(el))
    return out


# How many times must an image appear in the same spot before it's treated
# as an established frame, based on samples alone? A single occurrence is
# often just "a screenshot that happened to be pasted there."
SAMPLE_SLOT_MIN = 2
MAX_SLOTS_PER_LAYOUT = 4


def _consensus_box(boxes: list[dict]) -> dict:
    """Picks one representative size from samples gathered at the same
    frame (most frequent; ties broken by larger size)."""
    counts: dict[tuple, int] = {}
    for b in boxes:
        key = tuple(round(b[k], 2) for k in ("x", "y", "w", "h"))
        counts[key] = counts.get(key, 0) + 1
    best = max(counts, key=lambda k: (counts[k], k[2] * k[3]))
    return dict(zip(("x", "y", "w", "h"), best))


def merge_image_slots(layout_slots: list[dict],
                      samples: list[dict]) -> list[dict]:
    """Cross-references the layout's frames with samples from the bundled
    slides to finalize the insertion frames.

    - If a placeholder exists, its coordinates are used as-is (the most
      reliable evidence)
    - If the layout has an empty image, it's treated as a frame; if samples
      exist, their size takes precedence (an empty frame sometimes only
      indicates "roughly around here")
    - Even without a frame in the layout, samples placed in the same spot
      {min}+ times are picked up as a de facto frame
    """
    slots = [dict(s) for s in layout_slots]
    # Group samples not tied to any layout frame, by position
    leftovers: list[list[dict]] = []
    for box in samples:
        if any(_overlap_ratio(box, s) >= 0.5 for s in slots):
            continue
        for group in leftovers:
            if _overlap_ratio(box, group[0]) >= 0.5:
                group.append(box)
                break
        else:
            leftovers.append([box])
    for group in leftovers:
        if len(group) >= SAMPLE_SLOT_MIN:
            slots.append({**_consensus_box(group), "source": "sample",
                          "placeholder": None, "objectId": None})

    merged: list[dict] = []
    for slot in slots:
        entry = {k: slot[k] for k in ("x", "y", "w", "h")}
        entry["source"] = slot.get("source")
        if slot.get("placeholder"):
            entry["placeholder"] = slot["placeholder"]
        near = [b for b in samples if _overlap_ratio(b, slot) >= 0.5]
        if near and slot.get("source") == "layout":
            # Prefer the actually-used size over the empty frame's declared size
            chosen = _consensus_box(near)
            if any(abs(chosen[k] - entry[k]) > 0.02 for k in ("x", "y", "w", "h")):
                entry["declared"] = {k: slot[k] for k in ("x", "y", "w", "h")}
                entry.update(chosen)
                entry["sizedBy"] = "sample"
        if near:
            entry["samples"] = len(near)
        entry["aspect"] = round(entry["w"] / entry["h"], 3) if entry["h"] else None
        # After taking the representative value, discard anything that overlaps an existing frame at the same spot
        if any(_overlap_ratio(entry, m) >= 0.6 for m in merged):
            continue
        merged.append(entry)

    # Largest frame first (body images first, small decorations after)
    merged.sort(key=lambda s: -(s["w"] * s["h"]))
    return merged[:MAX_SLOTS_PER_LAYOUT]


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
    """Turns a master's colorScheme into a hex dict.

    Note: each colorScheme entry is `{"type": "...", "color": {"red":..,...}}`,
    with RGB directly under `color` rather than `color.rgbColor` (this
    differs from the structure of other API responses).
    """
    scheme = (master.get("pageProperties") or {}).get("colorScheme") or {}
    out = {}
    for entry in scheme.get("colors", []):
        out[entry["type"].lower()] = _auth.rgb_to_hex(entry.get("color", {}))
    return out


def build_template(pres: dict, name: str) -> dict:
    masters = pres.get("masters", [])
    master = masters[0] if masters else {}
    page = pres.get("pageSize", {})
    w = _auth.to_inches(page.get("width", {}).get("magnitude", 0))
    h = _auth.to_inches(page.get("height", {}).get("magnitude", 0))

    colors = extract_colors(master)
    master_info = analyze_page(master) if master else {"decorations": [], "textStyles": {}}

    # Some presentations have multiple masters (pasting slides from another
    # file adds them). The first one is used by default, but which master
    # each layout belongs to is recorded too.
    master_list = []
    for m in masters:
        mp = m.get("masterProperties", {})
        master_list.append({
            "objectId": m["objectId"],
            "displayName": mp.get("displayName"),
            "colors": extract_colors(m),
            "decorations": analyze_page(m)["decorations"],
        })

    sample_boxes = collect_sample_image_boxes(pres)

    layouts: dict = {}
    role_candidates: dict[str, list[str]] = {}
    used_keys: set[str] = set()
    for l in pres.get("layouts", []):
        lp = l.get("layoutProperties", {})
        display = lp.get("displayName") or l["objectId"]
        key = slugify(display, used_keys)
        info = analyze_page(l)
        slots = merge_image_slots(info["imageSlots"],
                                  sample_boxes.get(l["objectId"], []))
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
        if slots:
            layouts[key]["imageSlots"] = slots
        role = guess_role(display, info["placeholders"])
        if role:
            role_candidates.setdefault(role, []).append(key)

    roles = {role: keys[0] for role, keys in role_candidates.items()}

    # Default page-number style. Used if it can be picked up from the master's SLIDE_NUMBER placeholder.
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
        # --source accepts either a URL or an ID, but what's recorded is
        # always an openable URL. Storing the input string verbatim would
        # make the shape change on every re-analysis
        "sourceUrl": _auth.presentation_url(pres["presentationId"]),
        "presentationId": pres["presentationId"],
        "generationMode": "copy",
        "pageSize": {
            "widthInches": round(w, 3),
            "heightInches": round(h, 3),
            "aspectRatio": f"{round(w / h, 3)}:1" if h else None,
        },
        "existingSlideIds": [s["objectId"] for s in pres.get("slides", [])],
        "__existingSlideIds_note": "Bundled slides deleted right after the copy. "
                                   "Re-analyze whenever the template itself is edited",
        "colors": colors,
        "__colors_note": "colorScheme of masters[0]. With multiple masters, "
                         "check masters[].colors too",
        "masters": master_list,
        "pageNumber": page_number,
        "__pageNumber_note": "The Slides API cannot create SLIDE_NUMBER placeholders, "
                             "so build_deck.py draws text boxes in this style",
        "masterDecorations": master_info.get("decorations", []),
        "__masterDecorations_note": "Elements the master lays on every page (logo, "
                                    "copyright, etc.). Inherited automatically by the "
                                    "copy — never draw them yourself",
        "roles": roles,
        "__roles_note": "Guessed from display names and placeholder sets. A human "
                        "must always verify and fix against the layout thumbnails",
        "roleCandidates": role_candidates,
        "__imageSlots_note": "layouts.*.imageSlots is where the template wants a "
                             "picture: a PICTURE-family placeholder, an empty image "
                             "element left in the layout, or the frame the bundled "
                             "slides actually use. Deck specs should place image / "
                             "aiImage figures in these frames — omit x/y/w/h (or set "
                             "\"slot\": N) and build_deck.py fills them in",
        "layouts": layouts,
    }


def print_report(tpl: dict) -> None:
    print(f"=== {tpl['displayName']} ===")
    print(f"  id       : {tpl['presentationId']}")
    ps = tpl["pageSize"]
    print(f"  page size: {ps['widthInches']} x {ps['heightInches']} in")
    print(f"  colors   : " + ", ".join(f"{k}={v}" for k, v in list(tpl["colors"].items())[:10]))
    print(t("  existing slides: {n} (deleted on copy)", n=len(tpl["existingSlideIds"])))
    ms = tpl.get("masters", [])
    if len(ms) > 1:
        print(t("\n  ⚠ This presentation has {n} masters (usually 1):", n=len(ms)))
        for m in ms:
            n = sum(1 for l in tpl["layouts"].values() if l.get("masterObjectId") == m["objectId"])
            print(t("      {oid:22s} {name!r} {n} layouts",
                    oid=m["objectId"], name=m["displayName"], n=n))
        print(t("      Pasting slides from another file adds masters. To use this as a template,"))
        print(t("      pick one master lineage and align the roles to it."))
    print(t("\n--- {n} layouts ---", n=len(tpl["layouts"])))
    for key, l in tpl["layouts"].items():
        role = next((r for r, k in tpl["roles"].items() if k == key), "")
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
        for n, slot in enumerate(l.get("imageSlots") or []):
            src = slot.get("placeholder") or slot.get("source")
            extra = t(" ({n} samples)", n=slot["samples"]) if slot.get("samples") else ""
            print(t("      imageSlot[{n}]  x={x:.3f} y={y:.3f} w={w:.3f} h={h:.3f} "
                    "aspect={a} <- {src}{extra}",
                    n=n, x=slot["x"], y=slot["y"], w=slot["w"], h=slot["h"],
                    a=slot.get("aspect"), src=src, extra=extra))
    print(t("\n--- Role guesses ---"))
    for role, keys in tpl["roleCandidates"].items():
        mark = "" if len(keys) == 1 else t("  ← {n} candidates, needs review", n=len(keys))
        print(f"  {role:14s} -> {tpl['roles'][role]}{mark}")
        if len(keys) > 1:
            print(t("                 candidates: {keys}", keys=keys))
    missing = [r for r in ("COVER", "SECTION", "CONTENT", "CLOSING") if r not in tpl["roles"]]
    if missing:
        print(t("  unassigned roles: {missing}", missing=missing))


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
    p = argparse.ArgumentParser(description=t("Analyze a Google Slides template"))
    p.add_argument("source", help=t("URL or presentation ID of the template"))
    p.add_argument("--emit", help=t("output path for template.json"))
    p.add_argument("--name", help=t("template ID (lowercase letters and hyphens); "
                                    "defaults to the --emit filename"))
    p.add_argument("--thumbnails", help=t("output directory for layout thumbnails"))
    p.add_argument("--raw", help=t("path to dump the raw API response (for debugging)"))
    p.add_argument("--reset-roles", action="store_true",
                   help=t("overwrite the human-verified roles with fresh guesses"))
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
    template = build_template(pres, name)
    print_report(template)

    if args.emit:
        # When overwriting an existing file, keep the fields a human
        # verified and corrected. Since roles are only a guess, a
        # re-analysis must never erase a human's verification.
        keep = {}
        if os.path.exists(args.emit) and not args.reset_roles:
            try:
                with open(args.emit) as f:
                    prev = json.load(f)
                for k in ("roles", "__roles_note", "name", "displayName",
                          "bodyRoles", "__bodyRoles_note"):
                    if k in prev:
                        keep[k] = prev[k]
            except (OSError, ValueError) as e:  # noqa: BLE001
                print(t("  (could not read the previous file: {e})", e=e),
                      file=sys.stderr)
        if keep:
            stale = {r: k for r, k in keep.get("roles", {}).items()
                     if k not in template["layouts"]}
            template.update(keep)
            if args.name:
                template["name"] = args.name
            print(t("  kept from the previous file: {keys}",
                    keys=", ".join(sorted(keep))))
            if stale:
                print(t("  ⚠ these kept roles point at layouts that no longer "
                        "exist: {stale}", stale=stale), file=sys.stderr)
        os.makedirs(os.path.dirname(os.path.abspath(args.emit)), exist_ok=True)
        with open(args.emit, "w") as f:
            json.dump(template, f, ensure_ascii=False, indent=2)
        print(f"\ntemplate -> {args.emit}")
        print(t("  Always review and fix the roles by eye"))

    if args.thumbnails:
        print(t("\n--- Thumbnails ---"))
        fetch_thumbnails(slides, pres_id, template, args.thumbnails)

    return 0


if __name__ == "__main__":
    sys.exit(main())
