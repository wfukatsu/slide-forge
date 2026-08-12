#!/usr/bin/env python3
"""Build and register a new template (master) from a design spec (JSON).

    python scripts/build_template.py --spec design.json --dry-run
    python scripts/build_template.py --spec design.json \
        [--base blank|<template-id>|<URL>] [--emit templates/<id>.json] \
        [--title "<master name>"] [--folder <Drive URL/ID>] [--replace]

The Slides API does not support creating or renaming masters/layouts from
scratch (references/api-notes.md §1). So instead, this script restyles the
layout pages of a base -- by default the Google default master created by
presentations.create(), or a copy of a registered template -- via
batchUpdate, turning it into a master for the new brand. This automates the
derivation steps that used to be done by hand to build templates/corporate.json.

After generation, inspect_template.build_template() emits templates/<id>.json.
Role assignment does not rely on guesswork; it is written deterministically
from the base's layout mapping table (for a blank base: COVER→TITLE /
SECTION→SECTION_HEADER / CONTENT→TITLE_AND_BODY / TITLE_ONLY→TITLE_ONLY /
BLANK→BLANK / CLOSING→MAIN_POINT restyling).

See skills/template-forge/SKILL.md for the design-spec format and workflow.
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _auth  # noqa: E402
import inspect_template  # noqa: E402
from _i18n import t, register  # noqa: E402

register({
    "Build and register a new template (master) from a design spec":
        "デザインスペックから新しいテンプレート(マスター)を生成して登録する",
    "path to the design-spec JSON": "デザインスペック JSON のパス",
    "base master: 'blank' (Google default), a registered template id, or a Slides URL/ID":
        "ベースのマスター: 'blank'(Google 既定)/ 登録テンプレート ID / Slides の URL・ID",
    "output path for the template registration (default: templates/<name>.json)":
        "テンプレート登録の出力先(省略時: templates/<name>.json)",
    "title of the new master presentation (default: spec displayName)":
        "新しいマスタープレゼンテーションのタイトル(省略時: スペックの displayName)",
    "Drive folder URL or ID for the new master": "新しいマスターを置く Drive フォルダの URL または ID",
    "delete the presentation currently registered at --emit after a successful rebuild":
        "再生成成功後に --emit に登録済みの旧プレゼンテーションを Drive から削除する",
    "validate the spec offline and show the styling plan (no API calls)":
        "スペックをオフライン検証してスタイリング計画を表示する(API を呼ばない)",
    "The design spec has problems:": "デザインスペックに問題があります:",
    "name is missing or not a lowercase slug ([a-z0-9-])":
        "name がないか、小文字スラッグ([a-z0-9-])になっていません",
    "displayName is missing": "displayName がありません",
    "brand.colors.{key} is missing or not #RRGGBB": "brand.colors.{key} がないか #RRGGBB 形式ではありません",
    "brand.fonts.{key} is missing": "brand.fonts.{key} がありません",
    "brand.logo.{key}: file not found: {path}": "brand.logo.{key}: ファイルがありません: {path}",
    "style.coverStyle must be one of {allowed}": "style.coverStyle は {allowed} のいずれかです",
    "style.sectionStyle must be one of {allowed}": "style.sectionStyle は {allowed} のいずれかです",
    "base '{base}' is not 'blank', a registered template, or a URL/ID":
        "base '{base}' が 'blank'・登録テンプレート・URL/ID のいずれでもありません",
    "derive.* is only valid when base is not 'blank'":
        "derive.* は base が 'blank' 以外のときだけ指定できます",
    "Validation OK. Styling plan ({total} requests):":
        "検証 OK。スタイリング計画({total} リクエスト):",
    "  {role:12s} {n} requests": "  {role:12s} {n} リクエスト",
    "Creating the base presentation ({base})...": "ベースのプレゼンテーションを作成中({base})...",
    "Copying the base template ({base})...": "ベーステンプレートをコピー中({base})...",
    "Role {role} could not be mapped on the base (missing layout {want})":
        "ロール {role} をベースに割り当てられません(レイアウト {want} がありません)",
    "Styling {n} layout pages ({m} requests)...":
        "{n} レイアウトページをスタイリング中({m} リクエスト)...",
    "  warn: z-order adjustment was rejected (bands stay on top; usually harmless): {err}":
        "  warn: 重なり順の調整が拒否されました(帯が前面に残りますが通常は無害): {err}",
    "  warn: logo could not be inserted ({err}); add it manually in the Slides UI":
        "  warn: ロゴを挿入できませんでした({err})。Slides UI で手動追加してください",
    "Registered: {path}": "登録しました: {path}",
    "Deleted the superseded master {pid} from Drive": "旧マスター {pid} を Drive から削除しました",
    "  warn: could not delete the old master {pid}: {err}":
        "  warn: 旧マスター {pid} を削除できませんでした: {err}",
    "New master: {url}": "新しいマスター: {url}",
    "Next steps:": "次のステップ:",
    "  1. Catalog deck for visual role check: .venv/bin/python scripts/layout_sample.py --template {path}":
        "  1. ロール確認用カタログデッキ: .venv/bin/python scripts/layout_sample.py --template {path}",
    "  2. Inspect it with the slide-qa skill (bands vs placeholders, fonts, contrast)":
        "  2. slide-qa スキルで目視確認する(帯とプレースホルダの重なり・フォント・コントラスト)",
    "  3. Generate decks: scripts/build_deck.py --template {path} --spec deck.json":
        "  3. デッキ生成: scripts/build_deck.py --template {path} --spec deck.json",
    "API error, retrying in {sec}s ({attempt}/{total}): {err}":
        "API エラー。{sec} 秒後に再試行します({attempt}/{total}): {err}",
})

PAGE_W, PAGE_H = 10.0, 5.625
COVER_STYLES = ("band-bottom", "band-left", "minimal")
SECTION_STYLES = ("dark", "rule")
ROLES = ("COVER", "SECTION", "CONTENT", "TITLE_ONLY", "BLANK", "CLOSING")
ROLE_TO_PREDEFINED = {
    "COVER": "TITLE",
    "SECTION": "SECTION_HEADER",
    "CONTENT": "TITLE_AND_BODY",
    "TITLE_ONLY": "TITLE_ONLY",
    "BLANK": "BLANK",
    "CLOSING": "MAIN_POINT",
}
NUMBERED_ROLES = {"SECTION", "CONTENT", "TITLE_ONLY", "BLANK"}
REQUIRED_COLORS = ("primary", "primaryDark", "accent", "background", "backgroundAlt",
                   "textTitle", "textBody", "textMuted", "textOnDark")
_HEX_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")
_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")


# ---------- Validation ----------

def validate_spec(spec: dict, repo_root: str) -> list[str]:
    errors: list[str] = []
    if not _NAME_RE.match(spec.get("name") or ""):
        errors.append(t("name is missing or not a lowercase slug ([a-z0-9-])"))
    if not spec.get("displayName"):
        errors.append(t("displayName is missing"))
    brand = spec.get("brand") or {}
    colors = brand.get("colors") or {}
    for key in REQUIRED_COLORS:
        if not _HEX_RE.match(str(colors.get(key) or "")):
            errors.append(t("brand.colors.{key} is missing or not #RRGGBB", key=key))
    fonts = brand.get("fonts") or {}
    for key in ("heading", "body"):
        if not fonts.get(key):
            errors.append(t("brand.fonts.{key} is missing", key=key))
    logo = brand.get("logo") or {}
    for key in ("source", "onDark"):
        src = logo.get(key)
        if src and not src.startswith(("http://", "https://", "drive:")):
            path = os.path.expanduser(src)
            if not os.path.exists(path):
                errors.append(t("brand.logo.{key}: file not found: {path}",
                                key=key, path=src))
    style = spec.get("style") or {}
    if style.get("coverStyle", "band-bottom") not in COVER_STYLES:
        errors.append(t("style.coverStyle must be one of {allowed}",
                        allowed="/".join(COVER_STYLES)))
    if style.get("sectionStyle", "dark") not in SECTION_STYLES:
        errors.append(t("style.sectionStyle must be one of {allowed}",
                        allowed="/".join(SECTION_STYLES)))
    base = spec.get("base", "blank")
    if base != "blank" and "/" not in base and not _looks_like_id(base):
        if not os.path.exists(os.path.join(repo_root, "templates", f"{base}.json")):
            errors.append(t("base '{base}' is not 'blank', a registered template, "
                            "or a URL/ID", base=base))
    if spec.get("derive") and base == "blank":
        errors.append(t("derive.* is only valid when base is not 'blank'"))
    return errors


def _looks_like_id(s: str) -> bool:
    return len(s) > 20 and re.match(r"^[A-Za-z0-9_-]+$", s) is not None


# ---------- Request building blocks ----------

def _rgb(hex_color: str) -> dict:
    return {"rgbColor": _auth.hex_to_rgb(hex_color)}


def _emu_size(w: float, h: float) -> dict:
    return {"width": {"magnitude": _auth.inches(w), "unit": "EMU"},
            "height": {"magnitude": _auth.inches(h), "unit": "EMU"}}


def _xform(x: float, y: float) -> dict:
    return {"scaleX": 1, "scaleY": 1,
            "translateX": _auth.inches(x), "translateY": _auth.inches(y),
            "unit": "EMU"}


def _bg(page_id: str, hex_color: str) -> dict:
    return {"updatePageProperties": {
        "objectId": page_id,
        "pageProperties": {"pageBackgroundFill": {"solidFill": {"color": _rgb(hex_color)}}},
        "fields": "pageBackgroundFill.solidFill.color",
    }}


def _shape(oid: str, page_id: str, x: float, y: float, w: float, h: float,
           fill_hex: str, kind: str = "RECTANGLE") -> list[dict]:
    return [
        {"createShape": {"objectId": oid, "shapeType": kind,
                         "elementProperties": {"pageObjectId": page_id,
                                               "size": _emu_size(w, h),
                                               "transform": _xform(x, y)}}},
        {"updateShapeProperties": {"objectId": oid,
                                   "shapeProperties": {
                                       "shapeBackgroundFill": {"solidFill": {"color": _rgb(fill_hex)}},
                                       "outline": {"propertyState": "NOT_RENDERED"}},
                                   "fields": "shapeBackgroundFill.solidFill.color,"
                                             "outline.propertyState"}},
    ]


def _text_style(oid: str, *, font: str, size_pt: float, color: str,
                bold: bool = False) -> dict:
    return {"updateTextStyle": {
        "objectId": oid, "textRange": {"type": "ALL"},
        "style": {"fontFamily": font,
                  "fontSize": {"magnitude": size_pt, "unit": "PT"},
                  "bold": bold,
                  "foregroundColor": {"opaqueColor": _rgb(color)}},
        "fields": "fontFamily,fontSize,bold,foregroundColor",
    }}


def _text_box(oid: str, page_id: str, x: float, y: float, w: float, h: float,
              text: str, *, font: str, size_pt: float, color: str) -> list[dict]:
    return [
        {"createShape": {"objectId": oid, "shapeType": "TEXT_BOX",
                         "elementProperties": {"pageObjectId": page_id,
                                               "size": _emu_size(w, h),
                                               "transform": _xform(x, y)}}},
        {"insertText": {"objectId": oid, "text": text}},
        _text_style(oid, font=font, size_pt=size_pt, color=color),
    ]


def _logo_request(oid: str, page_id: str, url: str, x: float, y: float,
                  w: float, h: float) -> dict:
    return {"createImage": {"objectId": oid, "url": url,
                            "elementProperties": {"pageObjectId": page_id,
                                                  "size": _emu_size(w, h),
                                                  "transform": _xform(x, y)}}}


def _logo_box(source: str | None, target_w: float) -> tuple[float, float]:
    """Return the logo's rendered size. For local files, preserve the aspect ratio from the actual dimensions."""
    if source and not source.startswith(("http://", "https://", "drive:")):
        try:
            from PIL import Image
            with Image.open(os.path.expanduser(source)) as im:
                iw, ih = im.size
            if iw:
                return target_w, round(target_w * ih / iw, 3)
        except Exception:
            pass
    return target_w, round(target_w / 3.0, 3)  # assume a 3:1 landscape aspect ratio when the actual size is unknown


# ---------- Base creation and role mapping ----------

def _retry(call, what: str, attempts: int = 4):
    from googleapiclient.errors import HttpError
    for i in range(attempts):
        try:
            return call()
        except HttpError as e:
            status = getattr(e, "status_code", None) or getattr(e.resp, "status", 0)
            if i == attempts - 1 or status not in (429, 500, 502, 503):
                raise
            delay = 3 * (2 ** i)
            print(t("API error, retrying in {sec}s ({attempt}/{total}): {err}",
                    sec=delay, attempt=i + 1, total=attempts, err=f"{what}: {status}"),
                  file=sys.stderr)
            time.sleep(delay)


def create_base(slides, drive, spec: dict, base: str, title: str,
                folder: str | None, repo_root: str) -> tuple[str, dict | None]:
    """Prepare the base and return (presentationId, base_template_json|None)."""
    fid = _auth.folder_id(folder)
    if base == "blank":
        print(t("Creating the base presentation ({base})...", base=base))
        pres = _retry(lambda: slides.presentations().create(
            body={"title": title}).execute(), "presentations.create")
        pid = pres["presentationId"]
        if fid:
            meta = drive.files().get(fileId=pid, fields="parents",
                                     supportsAllDrives=True).execute()
            _retry(lambda: drive.files().update(
                fileId=pid, addParents=fid,
                removeParents=",".join(meta.get("parents", [])), fields="id",
                supportsAllDrives=True,
            ).execute(), "files.update")
        return pid, None

    base_tpl = None
    tpl_path = os.path.join(repo_root, "templates", f"{base}.json")
    if os.path.exists(tpl_path):
        with open(tpl_path, encoding="utf-8") as f:
            base_tpl = json.load(f)
        src = base_tpl["presentationId"]
    else:
        src = _auth.presentation_id(base)
    print(t("Copying the base template ({base})...", base=base))
    body: dict = {"name": title}
    if fid:
        body["parents"] = [fid]
    copied = _retry(lambda: drive.files().copy(
        fileId=src, body=body, fields="id",
        supportsAllDrives=True).execute(), "files.copy")
    pid = copied["id"]

    # Delete every bundled slide (using the actual list -- same convention as build_deck)
    pres = _retry(lambda: slides.presentations().get(
        presentationId=pid, fields="slides.objectId").execute(), "presentations.get")
    reqs = [{"deleteObject": {"objectId": s["objectId"]}}
            for s in pres.get("slides", [])]
    if reqs:
        _retry(lambda: slides.presentations().batchUpdate(
            presentationId=pid, body={"requests": reqs}).execute(),
            "batchUpdate(delete slides)")
    return pid, base_tpl


def _layout_placeholders(layout_page: dict) -> dict:
    """Return the layout page's placeholders as {TYPE: {objectId, geo}}."""
    out: dict = {}
    for el in layout_page.get("pageElements", []) or []:
        ph = (el.get("shape") or {}).get("placeholder")
        if ph:
            out[ph.get("type", "NONE")] = {
                "objectId": el["objectId"],
                "geo": inspect_template.geometry(el),
            }
    return out


def map_roles(pres: dict, base_tpl: dict | None) -> dict:
    """Deterministically build {role: {"layoutId", "placeholders": {TYPE: {objectId, geo}}}}."""
    layouts = pres.get("layouts", [])
    by_id = {l["objectId"]: l for l in layouts}
    rolemap: dict = {}
    for role in ROLES:
        layout = None
        if base_tpl is None:
            want = ROLE_TO_PREDEFINED[role]
            layout = next((l for l in layouts
                           if l.get("layoutProperties", {}).get("name") == want), None)
        else:
            key = (base_tpl.get("roles") or {}).get(role)
            lid = (base_tpl.get("layouts", {}).get(key) or {}).get("layoutId") if key else None
            layout = by_id.get(lid)
        if layout is None:
            raise SystemExit(t("Role {role} could not be mapped on the base "
                               "(missing layout {want})", role=role,
                               want=ROLE_TO_PREDEFINED[role] if base_tpl is None
                               else f"roles.{role}"))
        rolemap[role] = {"layoutId": layout["objectId"],
                         "placeholders": _layout_placeholders(layout)}
    return rolemap


# ---------- Styling plan ----------

def _ph(rolemap: dict, role: str, *types: str) -> dict | None:
    for tp in types:
        hit = rolemap[role]["placeholders"].get(tp)
        if hit:
            return hit
    return None


def plan_requests(spec: dict, rolemap: dict, logo_urls: dict[str, str],
                  derived: bool) -> tuple[dict[str, list], list[str], list[dict]]:
    """Return (per-role requests, list of band objectIds, logo requests).

    A logo's createImage can fail due to URL reachability, so it is applied
    in a separate, non-fatal batch. Sending bands to the back is handled the
    same way (api-notes: updatePageElementsZOrder on layout pages is
    unverified).
    """
    c = spec["brand"]["colors"]
    f = spec["brand"]["fonts"]
    style = spec.get("style") or {}
    footer = (spec["brand"].get("footer") or {})
    cover_style = style.get("coverStyle", "band-bottom")
    section_style = style.get("sectionStyle", "dark")
    logo = spec["brand"].get("logo") or {}

    reqs: dict[str, list] = {role: [] for role in ROLES}
    bands: list[str] = []
    logos: list[dict] = []
    fresh = not derived   # On a derived base, decoration/footer/background come from
                          # the base and are not created fresh (recoloring is done via
                          # derive.colorMap, text via the styling below)

    def footer_reqs(role: str, page_id: str) -> list[dict]:
        if not fresh or not footer.get("text"):
            return []
        return _text_box(f"tf_footer_{role.lower()}", page_id, 0.32, 5.34, 5.0, 0.2,
                         footer["text"], font=f["body"],
                         size_pt=footer.get("fontSize", 7), color=c["textMuted"])

    # COVER
    role, page = "COVER", rolemap["COVER"]["layoutId"]
    r = reqs[role]
    if fresh:
        r.append(_bg(page, c["background"]))
        if cover_style == "band-bottom":
            r += _shape("tf_cover_band", page, 0, 4.875, PAGE_W, 0.75, c["primary"])
            r += _shape("tf_cover_accent", page, 0, 4.815, PAGE_W, 0.06, c["accent"])
            bands += ["tf_cover_band", "tf_cover_accent"]
        elif cover_style == "band-left":
            r += _shape("tf_cover_band", page, 0, 0, 0.6, PAGE_H, c["primary"])
            r += _shape("tf_cover_accent", page, 0.6, 0, 0.08, PAGE_H, c["accent"])
            bands += ["tf_cover_band", "tf_cover_accent"]
        else:  # minimal
            r += _shape("tf_cover_accent", page, 0.6, 4.9, 1.8, 0.06, c["accent"])
            bands += ["tf_cover_accent"]
    title = _ph(rolemap, role, "CENTERED_TITLE", "TITLE")
    if title:
        r.append(_text_style(title["objectId"], font=f["heading"], size_pt=30,
                             color=c["textTitle"], bold=True))
    subtitle = _ph(rolemap, role, "SUBTITLE")
    if subtitle:
        r.append(_text_style(subtitle["objectId"], font=f["body"], size_pt=14,
                             color=c["textMuted"]))
    if fresh and logo.get("source"):
        w, h = _logo_box(logo["source"], 1.2)
        logos.append(_logo_request("tf_cover_logo", page,
                                   logo_urls.get("source", ""), 9.6 - w - 0.05, 0.35, w, h))

    # SECTION
    role, page = "SECTION", rolemap["SECTION"]["layoutId"]
    r = reqs[role]
    dark = section_style == "dark"
    if fresh:
        r.append(_bg(page, c["primary"] if dark else c["backgroundAlt"]))
    title = _ph(rolemap, role, "TITLE", "CENTERED_TITLE")
    if title:
        r.append(_text_style(title["objectId"], font=f["heading"], size_pt=24,
                             color=c["textOnDark"] if (dark and fresh) else c["textTitle"],
                             bold=True))
        if fresh:
            geo = title["geo"]
            rule_y = min(geo["y"] + geo["h"] + 0.08, PAGE_H - 0.2) if geo["h"] else 3.4
            r += _shape("tf_section_rule", page, geo["x"] or 0.6, rule_y, 3.0, 0.035,
                        c["accent"])
            bands.append("tf_section_rule")

    # CONTENT / TITLE_ONLY: top accent bar + title/body style + footer
    for role in ("CONTENT", "TITLE_ONLY"):
        page = rolemap[role]["layoutId"]
        r = reqs[role]
        if fresh:
            r.append(_bg(page, c["background"]))
            oid = f"tf_{role.lower()}_bar"
            r += _shape(oid, page, 0, 0, PAGE_W, 0.05, c["accent"])
            bands.append(oid)
        title = _ph(rolemap, role, "TITLE", "CENTERED_TITLE")
        if title:
            r.append(_text_style(title["objectId"], font=f["heading"], size_pt=20,
                                 color=c["textTitle"], bold=True))
        body = _ph(rolemap, role, "BODY")
        if body:
            r.append(_text_style(body["objectId"], font=f["body"], size_pt=12,
                                 color=c["textBody"]))
        r += footer_reqs(role, page)

    # BLANK
    role, page = "BLANK", rolemap["BLANK"]["layoutId"]
    if fresh:
        reqs[role].append(_bg(page, c["background"]))
    reqs[role] += footer_reqs(role, page)

    # CLOSING (on a blank base, MAIN_POINT is repurposed as the closing page)
    role, page = "CLOSING", rolemap["CLOSING"]["layoutId"]
    r = reqs[role]
    if fresh:
        r.append(_bg(page, c["primaryDark"]))
    title = _ph(rolemap, role, "TITLE", "CENTERED_TITLE")
    if title:
        r.append(_text_style(title["objectId"], font=f["heading"], size_pt=26,
                             color=c["textOnDark"] if fresh else c["textTitle"],
                             bold=True))
    closing_logo = logo.get("onDark") or logo.get("source")
    if fresh and closing_logo:
        w, h = _logo_box(closing_logo, 1.4)
        logos.append(_logo_request("tf_closing_logo", page,
                                   logo_urls.get("onDark", logo_urls.get("source", "")),
                                   (PAGE_W - w) / 2, 4.4, w, h))

    return reqs, bands, logos


def plan_derive_requests(spec: dict, pres: dict) -> list[dict]:
    """Expand derive.colorMap / deleteObjects into requests (derived base only).

    NOT_RENDERED (transparent) fills are the api-notes §3b trap -- filling
    them makes them opaque and covers the master's footer, so they are left
    alone unless explicitly specified.
    """
    derive = spec.get("derive") or {}
    color_map = {k.upper(): v for k, v in (derive.get("colorMap") or {}).items()}
    c = spec["brand"]["colors"]
    reqs: list[dict] = []

    pages = list(pres.get("layouts", [])) + list(pres.get("masters", []))
    for page in pages:
        for el in page.get("pageElements", []) or []:
            shape = el.get("shape")
            if not shape:
                continue
            fill = (shape.get("shapeProperties") or {}).get("shapeBackgroundFill") or {}
            if fill.get("propertyState") == "NOT_RENDERED":
                continue
            hex_now = inspect_template.opaque_hex(fill.get("solidFill"))
            token = color_map.get((hex_now or "").upper())
            if token and token in c:
                reqs.append({"updateShapeProperties": {
                    "objectId": el["objectId"],
                    "shapeProperties": {"shapeBackgroundFill": {
                        "solidFill": {"color": _rgb(c[token])}}},
                    "fields": "shapeBackgroundFill.solidFill.color"}})
    for oid in derive.get("deleteObjects") or []:
        reqs.append({"deleteObject": {"objectId": oid}})
    return reqs


def master_font_requests(pres: dict, spec: dict) -> list[dict]:
    """Set the default font on the master page's TITLE/BODY placeholders."""
    masters = pres.get("masters", [])
    if not masters:
        return []
    f = spec["brand"]["fonts"]
    reqs = []
    for tp, meta in _layout_placeholders(masters[0]).items():
        font = f["heading"] if tp in ("TITLE", "CENTERED_TITLE") else f["body"]
        reqs.append({"updateTextStyle": {
            "objectId": meta["objectId"], "textRange": {"type": "ALL"},
            "style": {"fontFamily": font}, "fields": "fontFamily"}})
    return reqs


def apply(slides, pid: str, requests: list[dict]) -> None:
    for i in range(0, len(requests), 500):
        chunk = requests[i:i + 500]
        _retry(lambda: slides.presentations().batchUpdate(
            presentationId=pid, body={"requests": chunk}).execute(), "batchUpdate")


# ---------- Registration ----------

def register_template(slides, pid: str, spec: dict, emit_path: str,
                      rolemap: dict, base_desc: str) -> dict:
    pres = _retry(lambda: slides.presentations().get(
        presentationId=pid).execute(), "presentations.get")
    url = f"https://docs.google.com/presentation/d/{pid}/edit"
    tpl = inspect_template.build_template(pres, spec["name"], url)
    tpl["displayName"] = spec["displayName"]

    id_to_key = {l["layoutId"]: key for key, l in tpl["layouts"].items()}
    tpl["roles"] = {role: id_to_key[m["layoutId"]] for role, m in rolemap.items()}
    today = datetime.date.today().isoformat()
    tpl["__roles_note"] = (f"Roles assigned deterministically by build_template.py "
                           f"on {today}; verify visually with layout_sample.py")
    tpl["derivedFrom"] = base_desc
    tpl["__derivedFrom_note"] = (f"Generated by build_template.py on {today} "
                                 f"from design spec '{spec['name']}'")

    footer = spec["brand"].get("footer") or {}
    tpl["pageNumber"] = {
        "font": spec["brand"]["fonts"]["body"],
        "fontSize": footer.get("fontSize", 7),
        "color": spec["brand"]["colors"]["textMuted"],
        "align": "END", "startAt": 1,
    }
    numbered = (spec.get("style") or {}).get("pageNumbers", True)
    for role in ROLES:
        layout = tpl["layouts"][tpl["roles"][role]]
        if numbered and role in NUMBERED_ROLES:
            layout["hasPageNumber"] = True
            layout["elements"].setdefault(
                "slideNumber", {"x": 9.45, "y": 5.34, "w": 0.4, "h": 0.2})
        else:
            # Don't render a page number on the cover/closing (and on every
            # role when page numbers are disabled). Even if the base layout
            # has a SLIDE_NUMBER, build_deck decides based on hasPageNumber
            layout["hasPageNumber"] = False

    os.makedirs(os.path.dirname(emit_path) or ".", exist_ok=True)
    with open(emit_path, "w", encoding="utf-8") as fp:
        json.dump(tpl, fp, ensure_ascii=False, indent=2)
        fp.write("\n")
    print(t("Registered: {path}", path=emit_path))
    return tpl


# ---------- main ----------

def main() -> int:
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    p = argparse.ArgumentParser(
        description=t("Build and register a new template (master) from a design spec"))
    p.add_argument("--spec", required=True, help=t("path to the design-spec JSON"))
    p.add_argument("--base", help=t("base master: 'blank' (Google default), a registered "
                                    "template id, or a Slides URL/ID"))
    p.add_argument("--emit", help=t("output path for the template registration "
                                    "(default: templates/<name>.json)"))
    p.add_argument("--title", help=t("title of the new master presentation "
                                     "(default: spec displayName)"))
    p.add_argument("--folder", help=t("Drive folder URL or ID for the new master"))
    p.add_argument("--replace", action="store_true",
                   help=t("delete the presentation currently registered at --emit "
                          "after a successful rebuild"))
    p.add_argument("--dry-run", action="store_true",
                   help=t("validate the spec offline and show the styling plan "
                          "(no API calls)"))
    args = p.parse_args()

    with open(args.spec, encoding="utf-8") as fp:
        spec = json.load(fp)
    if args.base:
        spec["base"] = args.base
    base = spec.get("base", "blank")

    errors = validate_spec(spec, repo_root)
    if errors:
        print(t("The design spec has problems:"), file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    if args.dry_run:
        # Build requests using a synthetic rolemap to show the scale (no API calls)
        fake_geo = {"x": 0.6, "y": 2.4, "w": 8.8, "h": 0.9}
        fake = {role: {"layoutId": f"dry_{role}",
                       "placeholders": {tp: {"objectId": f"dry_{role}_{tp}",
                                             "geo": fake_geo}
                                        for tp in ("TITLE", "CENTERED_TITLE",
                                                   "SUBTITLE", "BODY")}}
                for role in ROLES}
        reqs, _, logos = plan_requests(
            spec, fake, {"source": "https://example.invalid/logo.png",
                         "onDark": "https://example.invalid/logo.png"},
            derived=base != "blank")
        total = sum(len(v) for v in reqs.values()) + len(logos)
        print(t("Validation OK. Styling plan ({total} requests):", total=total))
        for role in ROLES:
            print(t("  {role:12s} {n} requests", role=role, n=len(reqs[role])))
        return 0

    title = args.title or spec["displayName"]
    emit_path = args.emit or os.path.join(repo_root, "templates", f"{spec['name']}.json")
    old_pid = None
    if args.replace and os.path.exists(emit_path):
        with open(emit_path, encoding="utf-8") as fp:
            old_pid = json.load(fp).get("presentationId")

    slides, drive = _auth.services()
    pid, base_tpl = create_base(slides, drive, spec, base, title,
                                args.folder, repo_root)
    pres = _retry(lambda: slides.presentations().get(
        presentationId=pid).execute(), "presentations.get")
    rolemap = map_roles(pres, base_tpl)

    logo = spec["brand"].get("logo") or {}
    logo_urls: dict[str, str] = {}
    store = None
    if logo.get("source") or logo.get("onDark"):
        from images import AssetStore
        store = AssetStore(drive)
        for key in ("source", "onDark"):
            if logo.get(key):
                logo_urls[key] = store.url_for(logo[key])

    try:
        reqs, bands, logos = plan_requests(spec, rolemap, logo_urls,
                                           derived=base != "blank")
        flat = master_font_requests(pres, spec)
        for role in ROLES:
            flat += reqs[role]
        if base != "blank":
            flat += plan_derive_requests(spec, pres)
        print(t("Styling {n} layout pages ({m} requests)...",
                n=len(ROLES), m=len(flat)))
        apply(slides, pid, flat)

        if bands:
            # updatePageElementsZOrder requires the elements in a single
            # request to be on the same page, so split into one request per band
            try:
                apply(slides, pid, [{"updatePageElementsZOrder": {
                    "pageElementObjectIds": [b], "operation": "SEND_TO_BACK"}}
                    for b in bands])
            except Exception as e:
                print(t("  warn: z-order adjustment was rejected (bands stay on "
                        "top; usually harmless): {err}", err=e), file=sys.stderr)
        if logos:
            try:
                apply(slides, pid, logos)
            except Exception as e:
                print(t("  warn: logo could not be inserted ({err}); add it "
                        "manually in the Slides UI", err=e), file=sys.stderr)
    finally:
        if store:
            store.cleanup()

    base_desc = ("google-default-master" if base == "blank"
                 else base_tpl["presentationId"] if base_tpl else base)
    register_template(slides, pid, spec, emit_path, rolemap, base_desc)

    if old_pid and old_pid != pid:
        try:
            drive.files().delete(fileId=old_pid,
                                 supportsAllDrives=True).execute()
            print(t("Deleted the superseded master {pid} from Drive", pid=old_pid))
        except Exception as e:
            print(t("  warn: could not delete the old master {pid}: {err}",
                    pid=old_pid, err=e), file=sys.stderr)

    print(t("New master: {url}",
            url=f"https://docs.google.com/presentation/d/{pid}/edit"))
    print(t("Next steps:"))
    print(t("  1. Catalog deck for visual role check: .venv/bin/python "
            "scripts/layout_sample.py --template {path}", path=emit_path))
    print(t("  2. Inspect it with the slide-qa skill (bands vs placeholders, "
            "fonts, contrast)"))
    print(t("  3. Generate decks: scripts/build_deck.py --template {path} "
            "--spec deck.json", path=emit_path))
    return 0


if __name__ == "__main__":
    sys.exit(main())
