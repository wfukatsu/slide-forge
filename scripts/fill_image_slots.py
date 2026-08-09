#!/usr/bin/env python3
"""既存デッキの空いている画像枠に、AI 生成した画像を入れる。

デッキ仕様から生成するときは build_deck.py が枠へ入れてくれる（x/y/w/h を
省略する）。こちらは**もう出来ているデッキ**が対象で、表紙や章扉の絵が
空のまま残っているものに後から絵を入れる。

    一覧:   python scripts/fill_image_slots.py <URL> --dry-run
    実行:   python scripts/fill_image_slots.py <URL>
    指定:   python scripts/fill_image_slots.py <URL> --slide 1 --prompt "夜間のビル"

枠の探し方は inspect_template.py と同じ（PICTURE 系プレースホルダ / レイアウトに
残った中身の無い image / 同梱スライドが繰り返し使っている位置）。**既に画像が
載っている枠は触らない。** 何を描くかはスライドの文字から起こすので、文字の無い
スライドには --prompt が要る。

デッキを直接書き換えるため、実行前に scripts/snapshot_version.py で複製を取ること。
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

# 枠と見なす重なり具合。既にある画像がこの割合を超えて枠に被っていれば「埋まっている」
OCCUPIED = 0.5


def _overlap(a: dict, b: dict) -> float:
    ix = max(0.0, min(a["x"] + a["w"], b["x"] + b["w"]) - max(a["x"], b["x"]))
    iy = max(0.0, min(a["y"] + a["h"], b["y"] + b["h"]) - max(a["y"], b["y"]))
    small = min(a["w"] * a["h"], b["w"] * b["h"])
    return (ix * iy) / small if small > 0 else 0.0


def slide_slots(slide: dict, layouts_by_id: dict) -> list[dict]:
    """このスライドで絵を入れられる枠を返す。

    スライド自身に置かれた空の枠（PICTURE プレースホルダ・中身の無い image）を
    優先する。無ければレイアウト側の imageSlots を使う。
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
    return list((layouts_by_id.get(lid) or {}).get("imageSlots") or [])


def existing_images(slide: dict) -> list[dict]:
    """このスライドに既に載っている画像の矩形。"""
    return [it.geometry(el) for el in slide.get("pageElements", [])
            if "image" in el and not it.is_empty_image(el)]


def slide_text(slide: dict) -> str:
    """スライドの文字を、上にあるものから拾って 1 本につなぐ。"""
    out = []
    for el in sorted(slide.get("pageElements", []),
                     key=lambda e: it.geometry(e)["y"]):
        for p in ((el.get("shape") or {}).get("text") or {}).get("textElements", []):
            s = (p.get("textRun") or {}).get("content", "").strip()
            if s:
                out.append(s)
    return " ".join(out).strip()


def prompt_for(slide: dict, given: str | None) -> str | None:
    """このスライドに描く絵の指示。--prompt が無ければ文字から起こす。"""
    if given:
        return given
    text = slide_text(slide)
    if not text:
        return None
    # 長い本文をそのまま渡すと絵が説明的になりすぎるので頭だけ使う
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
        # 登録済みテンプレートが無くても動くよう、そのデッキ自身から作る。
        # 配色（生成プロンプトに載る）とレイアウトの枠がここで揃う
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
        slots = slide_slots(slide, layouts_by_id)
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
        # 生成のキャッシュキーは (モデル, スタイル, 比率, プロンプト全文) なので、
        # 同じ形の枠には同じ絵が入る。気づかずに全ページ同じ絵になるのを防ぐ
        print(t("  note: one --prompt for {n} frames of the same shape draws "
                "the same picture in each; use --slide to vary them",
                n=len(jobs)))
    deck = TemplateDeck(slides_svc, drive_svc, pres_id, template)
    for slide_id, n, slot, prompt in jobs:
        print(t("  slide {n}: generating…", n=n))
        d = Canvas(deck, slide_id, template)
        # x/y/w/h は枠のもの。ai_image が枠の比に最も近い比率で描き、
        # 残りの差は cover の切り取りで埋める
        d.ai_image(slot["x"], slot["y"], slot["w"], slot["h"], prompt,
                   style=args.style, force=args.force)
    url = deck.commit()
    print(t("Done! {n} images placed: {url}", n=len(jobs), url=url))
    return 0


if __name__ == "__main__":
    sys.exit(main())
