#!/usr/bin/env python3
"""Fills the empty image slots of an existing deck with AI-generated images.

When generating from a deck spec, build_deck.py fills the slots for you (by
omitting x/y/w/h). This script instead targets a **deck that already
exists**, adding pictures after the fact to slots — like a cover or
chapter-divider image — that were left empty.

    list:  python scripts/fill_image_slots.py <URL> --dry-run
    run:   python scripts/fill_image_slots.py <URL>
    pick:  python scripts/fill_image_slots.py <URL> --slide 1 --prompt "夜間のビル"

Slot discovery works the same as inspect_template.py, but by default only
targets **slots the template declares** (PICTURE-family placeholders / empty
images). Slots inferred from "another slide places a picture at this same
position" are only used with --include-inferred, since running that over
the whole deck would end up filling in body-text areas too.

**Slots that already have a picture are left untouched.** What gets drawn is
derived from the slide's **heading**, so a slide without a heading needs
--prompt.

This rewrites the deck directly, so take a copy with
scripts/snapshot_version.py before running it.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import _auth  # noqa: E402
import images  # noqa: E402
import inspect_template as it  # noqa: E402
from build_deck import TemplateDeck  # noqa: E402
from diagrams import Canvas  # noqa: E402
from _i18n import t, register  # noqa: E402

register({
    "No image slots found in this deck": "このデッキに画像枠は見つかりませんでした",
    "  slide {n} ({layout}): slot {i} x={x:.2f} y={y:.2f} w={w:.2f} h={h:.2f} "
    "<- {src}":
        "  スライド {n}（{layout}）: 枠 {i} x={x:.2f} y={y:.2f} w={w:.2f} "
        "h={h:.2f} <- {src}",
    "      prompt: {prompt}": "      プロンプト: {prompt}",
    "      skipped: already has a picture": "      対象外: 既に画像が入っています",
    "      skipped: no text on this slide to build a prompt from "
    "(pass --prompt)":
        "      対象外: プロンプトの元になる文字がありません（--prompt を渡してください）",
    "{n} slots would be filled (nothing was changed)":
        "{n} 個の枠に入ります（まだ何も変更していません）",
    "{n} slots to fill": "{n} 個の枠に入れます",
    "  note: one --prompt for {n} frames of the same shape draws the same "
    "picture in each; use --slide to vary them":
        "  note: {n} 個の枠に同じ --prompt を使うので、同じ形の枠には同じ絵が"
        "入ります（変えるなら --slide でスライドごとに指定してください）",
    "Nothing to fill": "入れる枠がありません",
    "  slide {n}: generating…": "  スライド {n}: 生成中…",
    "Done! {n} images placed: {url}": "完了! 画像 {n} 枚: {url}",
    "Slide {n} does not exist (the deck has {total})":
        "スライド {n} はありません（このデッキは {total} 枚）",
})

# Overlap ratio that counts as a match. If an existing image covers a slot
# by more than this fraction, the slot counts as "occupied"
OCCUPIED = 0.5


def _overlap(a: dict, b: dict) -> float:
    ix = max(0.0, min(a["x"] + a["w"], b["x"] + b["w"]) - max(a["x"], b["x"]))
    iy = max(0.0, min(a["y"] + a["h"], b["y"] + b["h"]) - max(a["y"], b["y"]))
    small = min(a["w"] * a["h"], b["w"] * b["h"])
    return (ix * iy) / small if small > 0 else 0.0


def slide_slots(slide: dict, layouts_by_id: dict, *,
                inferred: bool = False) -> list[dict]:
    """Returns the slots on this slide where a picture can be placed.

    Prefers empty slots placed directly on the slide itself (PICTURE
    placeholders, or an image element with no content). Falls back to the
    layout's imageSlots if there are none.
    """
    slots = []
    for el in slide.get("pageElements", []):
        ph = (el.get("shape") or {}).get("placeholder") or el.get("placeholder")
        ptype = (ph or {}).get("type")
        if ptype in it.IMAGE_PLACEHOLDER_TYPES:
            slots.append({**it.geometry(el), "source": "placeholder",
                          "placeholder": ptype})
        elif it.is_empty_image(el):
            slots.append({**it.geometry(el), "source": "slide"})
    if slots:
        return slots
    lid = (slide.get("slideProperties") or {}).get("layoutObjectId")
    slots = list((layouts_by_id.get(lid) or {}).get("imageSlots") or [])
    if not inferred:
        # source="sample" is an inference — "another slide places a picture
        # at this same position" — not a slot the template actually
        # declares. Running it over the whole deck would fill body-text
        # areas with pictures, so only use it when explicitly requested
        slots = [s for s in slots if s.get("source") != "sample"]
    return slots


def existing_images(slide: dict) -> list[dict]:
    """Rectangles of the images already placed on this slide."""
    return [it.geometry(el) for el in slide.get("pageElements", [])
            if "image" in el and not it.is_empty_image(el)]


TITLE_PLACEHOLDERS = ("TITLE", "CENTERED_TITLE")


def _element_text(el: dict) -> str:
    return " ".join(
        (p.get("textRun") or {}).get("content", "").strip()
        for p in ((el.get("shape") or {}).get("text") or {}).get("textElements", [])
    ).strip()


def slide_text(slide: dict) -> str:
    """Returns this slide's heading.

    Mixing in body text would turn bullet points like "① Validate
    ② Distribute …" directly into the drawing prompt. The heading sums up
    what the slide is about in one line, so only that is used as the subject
    for the picture. Uses the TITLE placeholder if there is one; otherwise
    the topmost text.
    """
    els = slide.get("pageElements", [])
    for el in els:
        ptype = ((el.get("shape") or {}).get("placeholder") or {}).get("type")
        if ptype in TITLE_PLACEHOLDERS and _element_text(el):
            return _element_text(el)
    for el in sorted(els, key=lambda e: it.geometry(e)["y"]):
        if _element_text(el):
            return _element_text(el)
    return ""


def prompt_for(slide: dict, given: str | None) -> str | None:
    """The instruction for what to draw on this slide. Derived from the
    slide's text if --prompt isn't given."""
    if given:
        return given
    text = slide_text(slide)
    if not text:
        return None
    # Passing long body text as-is makes the picture too literal, so only
    # use the beginning
    return text[:120]


def main() -> int:
    p = argparse.ArgumentParser(
        description=t("Fill the empty image slots of an existing deck with "
                      "AI-generated pictures"))
    p.add_argument("source", help=t("deck URL or presentation ID"))
    p.add_argument("--template",
                   help=t("path of a registered template.json (defaults to "
                          "analyzing the deck itself)"))
    p.add_argument("--prompt",
                   help=t("what to draw (defaults to the slide's own text)"))
    p.add_argument("--style", default=images.DEFAULT_STYLE,
                   choices=sorted(images.STYLES))
    p.add_argument("--slide", type=int, action="append",
                   help=t("1-based slide number; repeatable (defaults to all)"))
    p.add_argument("--slot", type=int, default=None,
                   help=t("which slot to use when a slide has several (0-based)"))
    p.add_argument("--include-inferred", action="store_true",
                   help=t("also use frames inferred from how other slides in "
                          "the deck place pictures (off by default)"))
    p.add_argument("--dry-run", action="store_true",
                   help=t("list the slots without generating or changing anything"))
    p.add_argument("--force", action="store_true",
                   help=t("regenerate even when the image is already cached"))
    args = p.parse_args()

    pres_id = _auth.presentation_id(args.source)
    creds = _auth.get_credentials()
    slides_svc, drive_svc = _auth.services(creds)
    pres = slides_svc.presentations().get(presentationId=pres_id).execute()

    if args.template:
        with open(args.template, encoding="utf-8") as f:
            template = json.load(f)
    else:
        # Built from the deck itself so this works even without a
        # registered template. This is where the palette (which feeds the
        # generation prompt) and the layout's slots come from
        template = it.build_template(pres, pres.get("title", "deck"))
    layouts_by_id = {l["layoutId"]: l for l in template.get("layouts", {}).values()}

    slides = pres.get("slides", [])
    want = set(args.slide or range(1, len(slides) + 1))
    for n in sorted(want):
        if not 1 <= n <= len(slides):
            print(t("Slide {n} does not exist (the deck has {total})",
                    n=n, total=len(slides)), file=sys.stderr)
            return 1

    jobs = []
    for i, slide in enumerate(slides, start=1):
        if i not in want:
            continue
        slots = slide_slots(slide, layouts_by_id,
                            inferred=args.include_inferred)
        if not slots:
            continue
        taken = existing_images(slide)
        layout_name = (layouts_by_id.get(
            (slide.get("slideProperties") or {}).get("layoutObjectId"))
            or {}).get("displayName", "?")
        for j, slot in enumerate(slots):
            if args.slot is not None and j != args.slot:
                continue
            print(t("  slide {n} ({layout}): slot {i} x={x:.2f} y={y:.2f} "
                    "w={w:.2f} h={h:.2f} <- {src}",
                    n=i, layout=layout_name, i=j, x=slot["x"], y=slot["y"],
                    w=slot["w"], h=slot["h"],
                    src=slot.get("placeholder") or slot.get("source")))
            if any(_overlap(slot, im) >= OCCUPIED for im in taken):
                print(t("      skipped: already has a picture"))
                continue
            prompt = prompt_for(slide, args.prompt)
            if not prompt:
                print(t("      skipped: no text on this slide to build a "
                        "prompt from (pass --prompt)"))
                continue
            print(t("      prompt: {prompt}", prompt=prompt[:70]))
            jobs.append((slide["objectId"], i, slot, prompt))

    if not jobs:
        print(t("No image slots found in this deck") if not slides
              else t("Nothing to fill"))
        return 0
    if args.dry_run:
        print(t("{n} slots would be filled (nothing was changed)", n=len(jobs)))
        return 0

    print(t("{n} slots to fill", n=len(jobs)))
    if args.prompt and len(jobs) > 1:
        # The generation cache key is (model, style, aspect ratio, full
        # prompt text), so slots of the same shape get the same picture.
        # This note prevents every page silently ending up with the same
        # image
        print(t("  note: one --prompt for {n} frames of the same shape draws "
                "the same picture in each; use --slide to vary them",
                n=len(jobs)))
    deck = TemplateDeck(slides_svc, drive_svc, pres_id, template)
    for slide_id, n, slot, prompt in jobs:
        print(t("  slide {n}: generating…", n=n))
        d = Canvas(deck, slide_id, template)
        # x/y/w/h belong to the slot. ai_image draws at whichever ratio
        # comes closest to the slot's aspect ratio, and covers the
        # remaining difference with a crop
        d.ai_image(slot["x"], slot["y"], slot["w"], slot["h"], prompt,
                   style=args.style, force=args.force)
    url = deck.commit()
    print(t("Done! {n} images placed: {url}", n=len(jobs), url=url))
    return 0


if __name__ == "__main__":
    sys.exit(main())
