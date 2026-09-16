#!/usr/bin/env python3
"""Generate a presentation from template.json and a deck spec.

Duplicate the template via the Drive API -> delete the bundled slides -> stack
slides with `createSlide(layoutId)`. Decoration, logo, and footer defined by
the template's master are inherited automatically.

    # validate the spec only (no API calls)
    .venv/bin/python scripts/build_deck.py --template templates/x.json --spec deck.json --dry-run

    # generate
    .venv/bin/python scripts/build_deck.py --template templates/x.json --spec deck.json \
        --title "Document Title" [--folder <DRIVE_FOLDER_URL_OR_ID>]

As a library:
    deck = TemplateDeck.create(template, title="…")
    deck.add_slide("CONTENT", title="…", body=["…"])
    print(deck.commit())
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _auth  # noqa: E402
import settings  # noqa: E402
from _i18n import t, register  # noqa: E402
from _text import (  # noqa: E402
    DEFAULT_FIT, DENSITIES, FIT_MODES, LINE_EM, PRINT_MIN_FONT_PT, TEXT_INSET_X,
    Fit, describe_fit, fit_box, wrapped_lines)

register({
    "Drive folder URL or ID to create the deck in":
        "デッキを作成する Drive フォルダの URL または ID",
    "check coordinates and text volume without calling the API":
        "API を呼ばずに座標・文字量だけ検査する",
    "\ndry-run: {n} problems": "\ndry-run: 指摘 {n} 件",
    "Done! Open: {url}": "完了! URL: {url}",
    "Done! {n} slides. Open: {url}": "完了! スライド {n} 枚。URL: {url}",
    "{where}: 'aiImage' needs Gemini image generation, which is off in the "
    "settings (imageGeneration: off). Turn it on with "
    "scripts/settings.py --image-generation on, or replace the figure with a "
    "shape-drawn one (illustrations / patterns)":
        "{where}: 'aiImage' は Gemini の画像生成を使いますが、設定で OFF に"
        "なっています（imageGeneration: off）。"
        "scripts/settings.py --image-generation on で ON にするか、"
        "図形で描く図（illustrations / patterns）に置き換えてください",
    "where the deliverable goes: google (Drive / Slides) or local "
    "(folder / PowerPoint); defaults to config/settings.json":
        "成果物の出力先: google（Drive / Slides）または local"
        "（フォルダ / PowerPoint）。既定は config/settings.json",
    "  output: local — exporting to PowerPoint...":
        "  出力先: local — PowerPoint に書き出します...",
    "  output: local — after generation the deck is exported to PowerPoint "
    "under {dir}":
        "  出力先: local — 生成後に {dir} へ PowerPoint を書き出します",
    "  PPTX: {path} ({size:.1f} MB)": "  PPTX: {path}（{size:.1f} MB）",
    "  the deck itself stays in Google Slides (nothing is deleted): {url}":
        "  デッキ自体は Google Slides に残ります（削除はしません）: {url}",
    "  warn: the PowerPoint export failed ({err}); the deck is still "
    "available at {url}":
        "  warn: PowerPoint への書き出しに失敗しました（{err}）。"
        "デッキは {url} にあります",
    "  warn: {what} failed with HTTP {code}; retrying in {wait:.0f}s "
    "({attempt}/{attempts})":
        "  warn: {what} が HTTP {code} で失敗。{wait:.0f} 秒後に再試行 "
        "({attempt}/{attempts})",
    "template copy": "テンプレートの複製",
    "presentation create": "プレゼンテーションの新規作成",
    "rename": "デッキ名の変更",
    "no response was received for {what} ({err}); the write may already have "
    "been applied. Check whether the deck was updated before rerunning: {url}":
        "{what} の応答を受け取れませんでした（{err}）。書き込みはサーバー側で"
        "適用済みの可能性があります。デッキが更新済みかを確認してから"
        "再実行してください: {url}",
    "Generation failed; a partially built deck remains: {url} — delete it "
    "manually if it is not needed":
        "生成に失敗しました。作成途中のデッキが残っています: {url} — "
        "不要なら手で削除してください",
    "replace the contents of this existing deck (URL or ID) instead of "
    "creating a new one; the deck URL stays the same":
        "新規作成せず、既存デッキ（URL または ID）の中身を差し替える。"
        "デッキの URL は変わらない",
    "  replacing an existing deck: {n} slides will be removed":
        "  既存デッキを差し替えます: {n} 枚を削除します",
    "  pre-edit revision: {rev} ({time}) — roll back from "
    "File > Version history":
        "  編集前リビジョン: {rev} ({time}) — 差し戻しは"
        "「ファイル → 版の履歴」から",
    "  warn: could not read the revision history ({err}); snapshot the deck "
    "before replacing it":
        "  warn: 版の履歴を取得できませんでした（{err}）。"
        "差し替える前に snapshot_version.py で版を確保してください",
    "the deck {pid} was not built from template '{tpl}' (layouts not found: "
    "{missing}); --into only replaces a deck generated from the same template":
        "デッキ {pid} はテンプレート '{tpl}' から作られていません"
        "（見つからないレイアウト: {missing}）。--into が差し替えられるのは"
        "同じテンプレートで生成したデッキだけです",
    "{pid} is template '{tpl}' itself, not a deck generated from it; "
    "--into must never overwrite the master":
        "{pid} はテンプレート '{tpl}' の原本です（そこから生成したデッキでは"
        "ありません）。--into で原本を上書きすることはできません",
    "template '{tpl}' declares no layoutId for {layouts}; --into needs a "
    "template with real layouts":
        "テンプレート '{tpl}' は {layouts} の layoutId を持ちません"
        "（predefinedLayout で作る種類のテンプレートです）。"
        "--into には実レイアウトを持つテンプレートが必要です",
    "--keep-existing cannot be combined with --into (--into replaces every page)":
        "--keep-existing は --into と併用できません（--into は全ページを入れ替えます）",
    "  note: --folder is ignored with --into (the deck stays in its current folder)":
        "  note: --into では --folder は無視されます（デッキは今のフォルダに留まります）",
    "template.json has no presentationId":
        "template.json に presentationId がありません",
    "  warn: the template expects a {want}in page but Slides created a "
    "{got}in one; coordinates will not line up":
        "  warn: テンプレートは {want}in のページを想定していますが Slides は "
        "{got}in で作成しました。座標が合いません",
    "  note: --keep-existing is ignored by a generationMode: create template "
    "(it bundles no slides)":
        "  note: generationMode: create のテンプレートには同梱スライドが無いため "
        "--keep-existing は無視されます",
    "  warn: template.json existingSlideIds contains IDs that do not exist: "
    "{ids}\n        The template may have been updated; re-analyze it with "
    "inspect_template.py.":
        "  warn: template.json の existingSlideIds に実在しない ID があります: "
        "{ids}\n        テンプレートが更新された可能性があります。"
        "inspect_template.py で再解析してください。",
    "cannot resolve layout '{key}'; available roles: {roles} / "
    "layout keys: {keys}":
        "レイアウト '{key}' を解決できません。"
        "利用可能なロール: {roles} / レイアウトキー: {keys}",
    "body and bodies cannot be specified together":
        "body と bodies は同時に指定できません",
    "layout '{key}' ({name}) has no {ph} placeholder; it declares {declared}":
        "レイアウト '{key}' ({name}) は {ph} プレースホルダを持ちません。"
        "保持しているのは {declared}",
    "layout '{key}' ({name}) has only {slots} BODY slots but {given} were "
    "given (declares: {declared})":
        "レイアウト '{key}' ({name}) の BODY は {slots} 枠しかありませんが "
        "{given} 個指定されています（保持: {declared}）",
    "  warn: notes placeholder for {slide_id} not found; skipped":
        "  warn: {slide_id} のノート枠が見つからずスキップしました",
    "  warn: could not read the size of image {oid}; frame-filling placement "
    "was not applied":
        "  warn: 画像 {oid} の寸法が取れず、枠ぴったりの配置を適用できませんでした",
    "slides[{i}]: 'figures' must be an array":
        "slides[{i}]: 'figures' は配列である必要があります",
    "{where}: missing 'type'": "{where}: 'type' がありません",
    "{where}: unknown type '{kind}' (available: {available})":
        "{where}: 未知の type '{kind}'（利用可能: {available}）",
    "{where}: type '{kind}' is missing required keys: {missing}":
        "{where}: type '{kind}' に必要なキーがありません: {missing}",
    "{where}: 'textMargin' must be a number (inches)":
        "{where}: 'textMargin' は数値（インチ）である必要があります",
    "{where}: 'textMargin' is {v}in; give an inner margin between 0 and 1.0in":
        "{where}: 'textMargin' が {v}in です。0〜1.0in の内側余白を指定してください",
    "{where}: '{k}' must be a number (inches)":
        "{where}: '{k}' は数値（インチ）である必要があります",
    "{where}: extends horizontally past the page ({pw}in) "
    "(x={x} w={w} → right edge {right:.2f}in)":
        "{where}: 横方向がページ({pw}in)からはみ出します"
        "（x={x} w={w} → 右端 {right:.2f}in）",
    "{where}: extends vertically past the page ({ph}in) "
    "(y={y} h={h} → bottom edge {bottom:.2f}in)":
        "{where}: 縦方向がページ({ph}in)からはみ出します"
        "（y={y} h={h} → 下端 {bottom:.2f}in）",
    "{where}: the table overlaps the master logo/footer band "
    "(below y={band:.2f}in) (bottom edge {bottom:.2f}in); reduce the rows or "
    "split it across slides":
        "{where}: 表がマスターのロゴ・フッター帯（y={band:.2f}in 以下）に"
        "重なります（下端 {bottom:.2f}in）。行数を減らすか複数枚に分けること",
    "slides[{i}]: failed to draw figures: {etype}: {e}":
        "slides[{i}]: 図の描画に失敗しました: {etype}: {e}",
    "spec has no slides array": "spec に slides 配列がありません",
    "slides[{list}] ({n} slides){body}": "slides[{list}]（{n} 枚）{body}",
    "Text fitted to its box ({n}); --verbose to list them":
        "箱に合わせて縮めたテキスト {n} 件（一覧は --verbose）",
    "list every slide and every fitted text instead of counting them":
        "スライドと縮めたテキストを件数ではなく一覧で表示する",
    "{where}: missing 'layout'": "{where}: 'layout' がありません",
    "{where}: cannot resolve layout '{key}' (roles: {roles} / keys: {keys})":
        "{where}: レイアウト '{key}' を解決できません "
        "(ロール: {roles} / キー: {keys})",
    "{where}: layout '{key}' ({name}) has no {ph} but '{field}' is specified "
    "(declares: {declared})":
        "{where}: レイアウト '{key}' ({name}) は {ph} を持たないのに "
        "'{field}' が指定されています（保持: {declared}）",
    "{where}: 'body' and 'bodies' cannot be specified together":
        "{where}: 'body' と 'bodies' は同時に指定できません",
    "{where}: 'bodies' must be an array":
        "{where}: 'bodies' は配列である必要があります",
    "{where}: layout '{key}' ({name}) has no BODY but body text is specified "
    "(declares: {declared})":
        "{where}: レイアウト '{key}' ({name}) は BODY を持たないのに"
        "本文が指定されています（保持: {declared}）",
    "{where}: layout '{key}' ({name}) has {slots} BODY slots but {given} were "
    "given (declares: {declared})":
        "{where}: レイアウト '{key}' ({name}) の BODY は {slots} 枠ですが "
        "{given} 個指定されています（保持: {declared}）",
    "generate a presentation from a template":
        "テンプレートからプレゼンテーションを生成する",
    "path to template.json": "template.json のパス",
    "path to the deck-spec JSON": "デッキ仕様 JSON のパス",
    "presentation title (defaults to spec.title)":
        "生成するプレゼンテーションのタイトル（既定は spec.title）",
    "destination Drive folder URL or ID":
        "出力先 Drive フォルダの URL または ID",
    "validate the spec only, without calling the API":
        "API を呼ばず仕様の検証だけ行う",
    "do not draw page numbers": "ページ番号を描画しない",
    "keep the slides bundled with the template":
        "テンプレート同梱スライドを残す",
    "fail if the figure audit (overlaps / text overflow) reports anything":
        "図の検査（重なり・文字溢れ）で 1 件でも出たら失敗にする",
    "The spec has problems:": "仕様に問題があります:",
    "No title (specify --title or spec.title)":
        "タイトルがありません（--title か spec.title を指定してください）",
    "OK: the {n}-slide spec is consistent with the template":
        "OK: {n} 枚のスライド仕様はテンプレートと整合しています",
    "  + {n} figures": "  + 図 {n} 個",
    "Figure audit found {n} findings (images excluded; they need the real "
    "file):":
        "図の検査で {n} 件（画像は実物が要るため対象外）:",
    "figure audit (connectors / overlaps / text overflow): no problems":
        "図の検査（コネクタ・重なり・文字溢れ）: 問題なし",
    "(dry-run: nothing was generated)": "(dry-run: 生成していません)",
    "Figure audit found {n} findings:": "図の検査で {n} 件:",
    "{where}: {slot} does not fit its slot ({size:g}pt). Reduce the text, "
    "lower the font size, or split the slide":
        "{where}: {slot} が枠に収まりません（{size:g}pt）。文を減らすか"
        "文字サイズを下げるか、スライドを分けてください",
    "{slot}: text fitted to the slot ({detail})":
        "{slot}: テキストを枠に合わせました（{detail}）",
    "{where}: 'textFit' must be one of: {modes}":
        "{where}: 'textFit' は {modes} のいずれかです",
    "{where}: 'minFontSize' must be a positive number (pt)":
        "{where}: 'minFontSize' は正の数（pt）である必要があります",
    "Text fitted to its box ({n}):": "テキストを枠に合わせた箇所（{n} 件）:",
    "'density' must be one of: {densities}":
        "'density' は {densities} のいずれかです",
    "{slot} still overflows its slot at {size:g}pt; reduce the text, lower "
    "minFontSize, or split the slide":
        "{slot} は {size:g}pt まで縮めても枠に収まりません。文を減らすか "
        "minFontSize を下げるか、スライドを分けてください",
    "  warn: could not read placeholder styles; text fitting uses "
    "template.json only ({err})":
        "  warn: プレースホルダの書式を読めませんでした。テキストの適合は "
        "template.json の値だけで行います（{err}）",
    "  warn: body text contains characters outside the BMP (emoji etc.); "
    "emphasis ranges may shift":
        "  warn: 本文に BMP 外の文字（絵文字など）が含まれます。"
        "強調の範囲がずれることがあります",
    "  warn: unknown body role '{role}' (known: {known})":
        "  warn: 未知の本文ロール '{role}'（使えるもの: {known}）",
    "  warn: cannot use '{target}' as a link (use https://… or #12)":
        "  warn: '{target}' はリンク先にできません（https://… か #12 の形で）",
    "{where}: body line {n} must be a string or "
    "{{\"text\": …, \"role\": …}}": "{where}: 本文 {n} 行目は文字列か "
                                    "{{\"text\": …, \"role\": …}} で書きます",
    "slides[{i}].figures[{j}]: placed in the image slot of layout "
    "'{layout}' (x={x} y={y} w={w} h={h})":
        "slides[{i}].figures[{j}]: レイアウト '{layout}' の画像枠に配置 "
        "(x={x} y={y} w={w} h={h})",
    "slides[{i}].figures[{j}]: layout '{layout}' has no image slot, "
    "so x/y/w/h are required":
        "slides[{i}].figures[{j}]: レイアウト '{layout}' に画像枠が無いので "
        "x/y/w/h が必要です",
    "slides[{i}].figures[{j}]: slot {n} does not exist "
    "(layout '{layout}' has {total})":
        "slides[{i}].figures[{j}]: 画像枠 {n} は存在しません"
        "（レイアウト '{layout}' の枠は {total} 個）",
    "slides[{i}].figures[{j}]: the layout has an image slot at "
    "(x={x} y={y} w={w} h={h}) but this image is placed elsewhere "
    "(x={fx} y={fy} w={fw} h={fh}). Omit x/y/w/h to use the slot":
        "slides[{i}].figures[{j}]: レイアウトには画像枠"
        "（x={x} y={y} w={w} h={h}）がありますが、画像が別の場所"
        "（x={fx} y={fy} w={fw} h={fh}）に置かれています。"
        "x/y/w/h を省略すると枠に収まります",
})

# CENTERED_TITLE is the cover title of the Google default master
# (template-forge's blank base). Received on the spec as 'title', and used as
# the fallback for layouts that have no TITLE
FILLABLE = ("TITLE", "CENTERED_TITLE", "SUBTITLE", "BODY")

# ---------- Body emphasis (role-tagged lines and inline **emphasis**) ----------

# Default used when the template has no bodyRoles.
# Don't change the size (doing so would throw off the line-count estimate;
# limit adjustments to spaceAbove)
DEFAULT_BODY_ROLES = {
    "heading": {"bold": True, "spaceAbove": 6},
    "strong": {"bold": True},
    "note": {"color": "theme:DARK2"},
    # Mark links with color and underline so they're recognizable (the API
    # doesn't change the appearance just because a link is attached, so without
    # this styling there's no way to tell it's clickable)
    "link": {"color": "theme:ACCENT5", "underline": True},
}
# Keys that can be set in a role. Sorted into text style vs. paragraph style
_TEXT_STYLE_KEYS = ("bold", "italic", "underline", "color", "fontSize")
_PARA_STYLE_KEYS = ("spaceAbove", "spaceBelow")

# Only `**emphasis**` and `[display text](link target)` are supported. Full
# Markdown is not supported (if `#` or `-` were also honored, the resulting
# confusion would cause more breakage than it prevents)
_INLINE = re.compile(r"\*\*(?P<b>.+?)\*\*"
                     r"|\[(?P<t>[^\]]+)\]\((?P<u>[^)]+)\)", re.S)


def parse_inline(text: str) -> tuple[str, list[tuple]]:
    """Strip the markup and return the stripped string plus (start, end, kind, link target).

    kind is "strong" or "link". Ranges are positions from the start of the stripped string.
    """
    out, spans, pos, cursor = [], [], 0, 0
    for m in _INLINE.finditer(text):
        out.append(text[pos:m.start()])
        cursor += m.start() - pos
        if m.group("b") is not None:
            inner, kind, target = m.group("b"), "strong", None
        else:
            inner, kind, target = m.group("t"), "link", m.group("u").strip()
        spans.append((cursor, cursor + len(inner), kind, target))
        out.append(inner)
        cursor += len(inner)
        pos = m.end()
    out.append(text[pos:])
    return "".join(out), spans


def link_target(value: str) -> dict | None:
    """Convert a link target into the Slides API's link representation.

    "https://…" is a URL; "#12" is slide 12 (1-based) of the same deck.
    """
    if not value:
        return None
    if value.startswith("#"):
        try:
            return {"slideIndex": max(0, int(value[1:]) - 1)}
        except ValueError:
            return None
    if value.startswith(("http://", "https://", "mailto:")):
        return {"url": value}
    return None


def normalize_body_lines(value) -> list[tuple[str, str | None]]:
    """Normalize each body line to (text, role).

    A line may be either a plain string or {"text": "…", "role": "heading"}.
    """
    items = value if isinstance(value, list) else [value]
    lines: list[tuple[str, str | None]] = []
    for item in items:
        if isinstance(item, dict):
            lines.append((str(item.get("text", "")), item.get("role")))
        else:
            lines.append((str(item), None))
    return lines

# Random token so object IDs don't collide across processes.
# Sequential numbering alone would collide (e.g. slide_001) when a separate
# process appends to an existing deck
_RUN_TOKEN = uuid.uuid4().hex[:4]


def _retry(call, *, what: str, attempts: int = 4, base_delay: float = 3.0,
           idempotent: bool = True, url: str | None = None):
    """Retry an API call to absorb transient 5xx / 429 errors.

    A template with many slides can genuinely get a 500 Internal Error from
    `files.copy` when the service is under load. Giving up after one try would
    fail the whole generation, so this backs off exponentially and keeps
    trying. Besides HttpError, network exceptions such as socket timeouts
    (OSError) are also retried.

    However, **non-idempotent writes (batchUpdate) must be called with
    idempotent=False**. A timeout (OSError) may mean the server already
    applied the write and only the response was lost; blindly resending it
    risks a double-apply or a 400 that leaves the deck half-built. In that
    case, stop without retrying and raise a clear error prompting the user to
    check (pass the deck URL via `url`). HTTP 5xx / 429 are still safe to
    retry as before, since those indicate the write was not applied.
    """
    import time
    from googleapiclient.errors import HttpError

    for i in range(attempts):
        try:
            return call()
        except (HttpError, OSError) as e:
            if isinstance(e, OSError) and not idempotent:
                raise RuntimeError(t(
                    "no response was received for {what} ({err}); the write "
                    "may already have been applied. Check whether the deck "
                    "was updated before rerunning: {url}",
                    what=what, err=e, url=url or "?")) from e
            code = getattr(getattr(e, "resp", None), "status", None)
            retryable = isinstance(e, OSError) or code in (429, 500, 502, 503, 504)
            if not retryable or i == attempts - 1:
                raise
            code = code or type(e).__name__
            wait = base_delay * (2 ** i)
            print(t("  warn: {what} failed with HTTP {code}; retrying in "
                    "{wait:.0f}s ({attempt}/{attempts})", what=what, code=code,
                    wait=wait, attempt=i + 1, attempts=attempts - 1),
                  file=sys.stderr)
            time.sleep(wait)


# batchUpdate is faster the more it's batched into a single call. Splitting it
# spikes the measured cost per request (measured: 8000 requests as 16 batches
# of 500 = 18.2s vs. one batch = 6.3s), so pack it right up to the limit.
# Parallelizing is counterproductive (concurrent writes to the same
# presentation contend with each other: 4 parallel x 2000 = 20.1s vs.
# sequential 2000 = 12.2s), so **do not do it**.
#
# The limit comes from the Google API's 10MB request body cap. A figure
# request measures around 288 bytes, so with a safety margin this cuts at
# 5MB / 10000 items (measured: 30305 items / 7.5MB completes in 20s).
MAX_REQUESTS_PER_BATCH = 10000
MAX_BATCH_BYTES = 5_000_000


def parse_slide_selection(value: str, slide_count: int) -> list[int]:
    """Parse a comma-separated, one-based page selection into zero-based indices."""
    if not value or not value.strip():
        raise ValueError("--update-slides requires at least one page number")
    indices: list[int] = []
    seen: set[int] = set()
    for raw in value.split(","):
        token = raw.strip()
        if not token or not token.isdecimal():
            raise ValueError(
                f"invalid page number {token!r} in --update-slides; use e.g. 3,7"
            )
        page = int(token)
        if page < 1 or page > slide_count:
            raise ValueError(
                f"page {page} is outside the spec range 1..{slide_count}"
            )
        index = page - 1
        if index in seen:
            raise ValueError(f"page {page} is listed more than once")
        seen.add(index)
        indices.append(index)
    return indices


def _single_batch_size(requests: list[dict]) -> tuple[int, int]:
    return len(requests), sum(
        len(json.dumps(req, ensure_ascii=False).encode()) for req in requests
    )


def _batches(requests: list[dict], max_requests: int = MAX_REQUESTS_PER_BATCH,
             max_bytes: int = MAX_BATCH_BYTES):
    """Split the request list into chunks that fit both the count and byte-size limits.

    Order is preserved. Since batchUpdate runs each chunk sequentially, the
    result is unchanged even if a chunk boundary crosses a slide or figure.
    """
    batch: list[dict] = []
    size = 0
    for req in requests:
        n = len(json.dumps(req, ensure_ascii=False).encode())
        # Even if a single item exceeds the limit on its own, always send it as its own chunk
        if batch and (len(batch) >= max_requests or size + n > max_bytes):
            yield batch
            batch, size = [], 0
        batch.append(req)
        size += n
    if batch:
        yield batch


def draw_slot_name(key: str) -> str:
    """`drawText` key -> slot name: `title` -> TITLE, `bodyx1` -> BODY#1."""
    return key.upper().replace("X", "#") if key[-1].isdigit() else key.upper()


def declared_slots(layout: dict) -> list[str]:
    """The slots a layout can fill: real placeholders plus drawn text boxes.

    A `generationMode: create` template has no real layouts, so it declares
    TITLE / SUBTITLE / BODY under `drawText` and they are drawn at explicit
    coordinates instead of mapped onto placeholders. Both kinds are addressed
    by the same spec fields, so both count as declared. validate_layout.py
    resolves slots the same way.
    """
    declared = list(layout.get("placeholders", []))
    for key in layout.get("drawText") or {}:
        name = draw_slot_name(key)
        if name not in declared:
            declared.append(name)
    return declared


def _drawn_text_styles(oid: str, spec: dict) -> list[dict]:
    """Base appearance for a drawn slot, queued after its text is inserted.

    Styling an empty shape does not survive a later insertText, so these
    always follow the insert. Per-slide overrides (titleFontSize,
    bodyFontSize, line spacing) are queued after this and win.
    """
    style: dict = {}
    fields = []
    if spec.get("fontFamily"):
        style["fontFamily"] = spec["fontFamily"]
        fields.append("fontFamily")
    if spec.get("size"):
        style["fontSize"] = {"magnitude": spec["size"], "unit": "PT"}
        fields.append("fontSize")
    if spec.get("bold") is not None:
        style["bold"] = bool(spec["bold"])
        fields.append("bold")
    if spec.get("color"):
        style["foregroundColor"] = {
            "opaqueColor": {"rgbColor": _auth.hex_to_rgb(spec["color"])}}
        fields.append("foregroundColor")

    requests: list[dict] = []
    if fields:
        requests.append({"updateTextStyle": {
            "objectId": oid, "style": style,
            "textRange": {"type": "ALL"}, "fields": ",".join(fields)}})
    para: dict = {}
    if spec.get("align"):
        para["alignment"] = spec["align"]
    if spec.get("lineSpacing"):
        para["lineSpacing"] = spec["lineSpacing"]
    if para:
        requests.append({"updateParagraphStyle": {
            "objectId": oid, "style": para,
            "textRange": {"type": "ALL"}, "fields": ",".join(para)}})
    if spec.get("valign"):
        requests.append({"updateShapeProperties": {
            "objectId": oid,
            "shapeProperties": {"contentAlignment": spec["valign"]},
            "fields": "contentAlignment"}})
    return requests


# ---------- Fitting slot text ----------
#
# Slides' own "shrink text on overflow" cannot be turned on through the API
# (autofitType accepts only NONE), and text that overflows a slot is drawn
# outside it, so a long title or body shows up displaced. fit_slot()
# reproduces the fitting before the requests go out; audit_body_fit() runs
# the same plan offline.

# Allowance against the slot height, as a fraction of it. Line height is
# _text.LINE_EM for every font: Slides lays out Noto Sans JP and Arial lines
# at the same measured height.
SLOT_FIT_SLACK = 0.02


def _slot_one_sided(drawn: bool, align: str | None) -> bool:
    """Whether fitting tightens only one edge of a slot (see _slot_indent)."""
    return not drawn or align != "CENTER"


def _slot_indent(inset: float, drawn: bool, align: str | None = None) -> dict:
    """Paragraph indents that give a slot the fitted inner margin.

    Only the edge the text is not aligned to moves, so a fitted title starts
    exactly where every other title on the deck does. A placeholder always
    moves just its right edge: its own left indent carries bullets and hanging
    indents. A drawn slot moves the right edge for START, the left for END,
    and both for CENTER.
    """
    tighten = TEXT_INSET_X - inset
    if tighten <= 1e-9:
        return {}
    if drawn and align == "CENTER":
        return _auth.indent_style(tighten)
    if drawn and align == "END":
        return _auth.indent_sides(tighten, 0)
    return _auth.indent_sides(0, tighten)


def _slot_key(name: str) -> str:
    """Slot name -> its `elements` / `textStyles` key (CENTERED_TITLE -> title)."""
    return "title" if name in ("TITLE", "CENTERED_TITLE") else name.lower()


def _placeholder_own_style(shape: dict) -> dict:
    """The size and paragraph spacing a placeholder sets itself (not inherited)."""
    out: dict = {}
    elements = (shape.get("text") or {}).get("textElements") or []
    para = next((te["paragraphMarker"].get("style") or {} for te in elements
                 if "paragraphMarker" in te), {})
    run = next((te["textRun"].get("style") or {} for te in elements
                if "textRun" in te), {})
    size = (run.get("fontSize") or {}).get("magnitude")
    if size:
        out["fontSize"] = size
    if para.get("lineSpacing"):
        out["lineSpacing"] = para["lineSpacing"]
    for key in ("spaceAbove", "spaceBelow"):
        if key in para:          # {"unit": "PT"} with no magnitude is an explicit 0
            out[key] = (para[key] or {}).get("magnitude", 0)
    return out


def inherited_slot_styles(pres: dict) -> dict[str, dict[str, dict]]:
    """layoutId -> slot key -> the font size and paragraph spacing a slot really gets.

    A layout placeholder usually sets only some of these and inherits the
    rest from its master placeholder (a BODY with lineSpacing 115 and
    spaceBelow 10pt, say), which template.json does not record. Estimating
    without them undercounts the height badly, so the real deck is read and
    each value resolved up the parentObjectId chain.
    """
    shapes = {}
    for page in (pres.get("masters") or []) + (pres.get("layouts") or []):
        for el in page.get("pageElements") or []:
            if (el.get("shape") or {}).get("placeholder"):
                shapes[el["objectId"]] = el["shape"]
    out: dict[str, dict[str, dict]] = {}
    for layout in pres.get("layouts") or []:
        slots: dict[str, dict] = {}
        for el in layout.get("pageElements") or []:
            shape = el.get("shape") or {}
            ph = shape.get("placeholder")
            if not ph or ph.get("type") not in ("TITLE", "CENTERED_TITLE",
                                                "SUBTITLE", "BODY"):
                continue
            idx = ph.get("index", 0)
            name = ph["type"] if not idx else f"{ph['type']}#{idx}"
            style: dict = {}
            seen = set()
            while shape and id(shape) not in seen:
                seen.add(id(shape))
                for k, v in _placeholder_own_style(shape).items():
                    style.setdefault(k, v)
                parent = (shape.get("placeholder") or {}).get("parentObjectId")
                shape = shapes.get(parent) if parent else None
            slots.setdefault(_slot_key(name), style)
        out[layout["objectId"]] = slots
    return out


def fit_slot(layout: dict, name: str, value, *, explicit_size=None,
             body: bool = False, drawn: bool | None = None,
             mode: str | None = None, min_size: float | None = None,
             line_spacing=None, space_above=None, space_below=None,
             roles: dict | None = None,
             inherited: dict[str, dict] | None = None) -> tuple[Fit, float] | None:
    """Plan the font size and inner margin that fit a slot's text.

    Returns (fit, base size), or None when the slot's geometry or font size
    is unknown. `inherited` is this layout's entry from inherited_slot_styles
    (read from the real deck at build time); it fills in the font size and
    paragraph spacing template.json lacks, so without it (dry-run) the
    estimate stays on the low side. Text that fits is planned unchanged.
    "grow" is treated as "shrink" here: resizing a template's slot would
    break the layout it belongs to. With "none" the plan is left at the base
    size and only reports whether it fits.
    """
    mode = mode or DEFAULT_FIT
    draw = TemplateDeck._draw_specs(layout).get(name)
    if drawn is None:
        drawn = draw is not None and name not in (layout.get("placeholders") or [])
    key = _slot_key(name)
    style = (layout.get("textStyles") or {}).get(key) or {}
    inh = {} if drawn else ((inherited or {}).get(key) or {})
    if drawn:
        geo = draw
        size = explicit_size or draw.get("size") or style.get("fontSize")
        ls = line_spacing or draw.get("lineSpacing") or 100
    else:
        geo = (layout.get("elements") or {}).get(key)
        size = explicit_size or style.get("fontSize") or inh.get("fontSize")
        ls = line_spacing or inh.get("lineSpacing") or 100
    if space_above is None:
        space_above = inh.get("spaceAbove")
    if space_below is None:
        space_below = inh.get("spaceBelow")
    if not geo or not size:
        return None
    w, h = geo["w"], geo["h"]
    line_em = LINE_EM

    one_side = _slot_one_sided(drawn, geo.get("align"))

    def width(inset):
        return w - (TEXT_INSET_X + inset if one_side else inset * 2)

    if body:
        roles = roles or DEFAULT_BODY_ROLES
        gap = (space_above or 0) + (space_below or 0)
        lines = [(parse_inline(text)[0], roles.get(role) or {})
                 for text, role in normalize_body_lines(value)]

        def need(s, inset):
            total = 0.0
            for plain, st in lines:
                fs = st.get("fontSize", size) * s / size
                total += (wrapped_lines(plain, width(inset), fs) * fs * line_em
                          * ls / 100 + gap
                          + st.get("spaceAbove", 0) + st.get("spaceBelow", 0))
            return total / 72
    else:
        text = "\n".join(value) if isinstance(value, list) else str(value)

        def need(s, inset):
            return wrapped_lines(text, width(inset), s) * s * line_em * ls / 100 / 72

    slack = h * SLOT_FIT_SLACK
    if mode == "none":
        return Fit(size, TEXT_INSET_X,
                   need(size, TEXT_INSET_X) <= h + slack), size
    return fit_box(need, h, size, TEXT_INSET_X, min_size=min_size,
                   slack=slack), size


def _scale_spans(spans: list[dict], scale: float) -> list[dict]:
    """Shrink the role font sizes of body spans along with the fitted body."""
    out = []
    for span in spans:
        fs = span["style"].get("fontSize")
        if fs:
            span = {**span, "style": {**span["style"],
                                      "fontSize": round(fs * scale * 2) / 2}}
        out.append(span)
    return out


def load_template(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


class TemplateDeck:
    """Builder that stacks slides on top of a duplicated template."""

    dry_run = False

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
        # Number of bundled template slides kept via keep_existing.
        # add_page_numbers() offsets new-slide numbering by this amount
        self.kept_slides = 0
        # Set to an images.AssetStore when an image is inserted; cleaned up after commit()
        self.assets = None
        # (objectId, x, y, w, h). Since createImage preserves the aspect
        # ratio, images meant to fill a frame exactly are fixed up by
        # overwriting their transform after commit
        self.image_fixups: list[tuple] = []
        # Lists of objectIds to group once everything is drawn. Grouping runs
        # in the post pass, after the image fixups: an ABSOLUTE transform on
        # a grouped child is read in the group's coordinate space, so
        # grouping first would displace the image
        self.pending_groups: list[list[str]] = []
        # --into's title change is deferred until after a successful commit (see open())
        self.pending_title: str | None = None
        # layoutId -> slot key -> font size / paragraph spacing resolved through
        # the master. Read from the real deck by load_inherited_styles();
        # stays empty for a deck made without one (create mode, tests)
        self.inherited_styles: dict[str, dict[str, dict]] = {}
        # Partial page replacement must be atomic. It is never split across batchUpdate calls.
        self.require_single_batch = False
        self.partial_targets: dict[int, str] = {}

    @property
    def url(self) -> str:
        return f"https://docs.google.com/presentation/d/{self.presentation_id}/edit"

    # ---------- Creation ----------

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
        slides, drive = _auth.services(creds)
        if not src:
            if template.get("generationMode") != "create":
                raise ValueError(t("template.json has no presentationId"))
            return cls._create_blank(slides, drive, template, title, folder,
                                     keep_existing=keep_existing)

        body: dict = {"name": title}
        fid = _auth.folder_id(folder)
        if fid:
            body["parents"] = [fid]
        copied = _retry(
            lambda: drive.files().copy(fileId=src, body=body, fields="id",
                                       supportsAllDrives=True).execute(),
            what=t("template copy"))

        deck = cls(slides, drive, copied["id"], template)
        deck.load_inherited_styles()
        if not keep_existing:
            deck._delete_existing_slides()
        else:
            # Count the actual number of kept slides to offset the page-number
            # starting point. template.json's existingSlideIds can go stale
            # after a template update, so check the real thing instead
            pres = _retry(
                lambda: deck.slides.presentations().get(
                    presentationId=deck.presentation_id, fields="slides.objectId"
                ).execute(),
                what="presentations.get")
            deck.kept_slides = len(pres.get("slides", []))
        return deck

    @classmethod
    def _create_blank(
        cls,
        slides,
        drive,
        template: dict,
        title: str,
        folder: str | None,
        keep_existing: bool = False,
    ) -> "TemplateDeck":
        """Start from an empty presentation (`generationMode: create`).

        A template with no `presentationId` has no master to duplicate; it
        declares `predefinedLayout` layouts whose slots are drawn at explicit
        coordinates (see `drawText` in add_slide). `blank-16x9` is the one in
        the repo, and it is the only template a clone can use without a
        master of its own in Drive.
        """
        if keep_existing:
            print(t("  note: --keep-existing is ignored by a generationMode: "
                    "create template (it bundles no slides)"))
        # presentations.create ignores every field but the title, so the page
        # size is whatever Slides defaults to. Say so rather than drawing to a
        # canvas that silently differs from the one the template declares.
        pres = _retry(
            lambda: slides.presentations().create(body={"title": title}).execute(),
            what=t("presentation create"))
        deck = cls(slides, drive, pres["presentationId"], template)
        want = template.get("pageSize", {}).get("widthInches")
        got = pres.get("pageSize", {}).get("width", {}).get("magnitude")
        if want and got and abs(_auth.to_inches(got) - want) > 0.01:
            print(t("  warn: the template expects a {want}in page but Slides "
                    "created a {got}in one; coordinates will not line up",
                    want=want, got=round(_auth.to_inches(got), 2)),
                  file=sys.stderr)
        if folder:
            deck._move_to_folder(folder)
        # A new presentation always opens with one slide, and the deck is
        # built entirely from its own pages
        deck._queue_slide_deletes(
            [sl["objectId"] for sl in pres.get("slides", [])])
        return deck

    def _move_to_folder(self, folder: str) -> None:
        """Move the presentation out of My Drive's root into `folder`."""
        fid = _auth.folder_id(folder)
        if not fid:
            return
        meta = _retry(
            lambda: self.drive.files().get(
                fileId=self.presentation_id, fields="parents",
                supportsAllDrives=True).execute(),
            what="files.get")
        _retry(
            lambda: self.drive.files().update(
                fileId=self.presentation_id, addParents=fid,
                removeParents=",".join(meta.get("parents", [])),
                fields="id", supportsAllDrives=True).execute(),
            what="files.update")

    @classmethod
    def open(
        cls,
        template: dict,
        source: str,
        *,
        layouts=None,
        title: str | None = None,
        creds=None,
    ) -> "TemplateDeck":
        """Open an existing deck and put it in a state where its contents can be fully replaced.

        Where `create()` duplicates the template into a **new URL**, this
        replaces the contents of an already-existing URL in place. It exists
        for material like a per-customer activity plan, where a shared link
        needs to be kept up to date without ever changing.

        **Destructive**. Every current page is deleted. Before calling this,
        capture a version with `scripts/snapshot_version.py` (the pre-edit
        revision is also recorded and printed here).

        Pass `layouts` the layout keys of the slides about to be stacked. This
        is used to confirm the deck actually has this template's master
        before any API calls start hitting it.
        """
        slides, drive = _auth.services(creds)
        pid = _auth.presentation_id(source)
        # Replacing the template's own master would corrupt the source that
        # every deck built from that template depends on. Since the generated
        # deck and the master original are easy to mix up, always stop here
        if pid == template.get("presentationId"):
            raise ValueError(
                t("{pid} is template '{tpl}' itself, not a deck generated from "
                  "it; --into must never overwrite the master",
                  pid=pid, tpl=template.get("name", "?")))
        deck = cls(slides, drive, pid, template)
        deck._require_layouts(layouts)
        deck.load_inherited_styles()
        deck._print_pre_edit_revision()
        removed = deck._queue_slide_deletes(deck._present_slide_ids())
        print(t("  replacing an existing deck: {n} slides will be removed",
                n=removed))
        if title:
            # Calling files.update here would leave a deck with "old contents
            # but a new title" if generation fails. So the rename is only
            # remembered here, and issued once commit() has successfully
            # replaced the contents
            deck.pending_title = title
        return deck

    @classmethod
    def open_partial(
        cls,
        template: dict,
        source: str,
        *,
        selected_indices: list[int],
        expected_slide_count: int,
        layouts=None,
        creds=None,
    ) -> "TemplateDeck":
        """Open a generated deck for atomic replacement of selected pages only."""
        slides, drive = _auth.services(creds)
        pid = _auth.presentation_id(source)
        if pid == template.get("presentationId"):
            raise ValueError(
                t("{pid} is template '{tpl}' itself, not a deck generated from "
                  "it; --into must never overwrite the master",
                  pid=pid, tpl=template.get("name", "?")))
        deck = cls(slides, drive, pid, template)
        deck._require_layouts(layouts)
        deck.load_inherited_styles()
        present = deck._present_slide_ids()
        if len(present) != expected_slide_count:
            raise ValueError(
                "partial update refused: the live deck has "
                f"{len(present)} pages but the source spec has {expected_slide_count}; "
                "refresh the spec or use an explicitly approved full replacement"
            )
        deck.partial_targets = {index: present[index] for index in selected_indices}
        deck.require_single_batch = True
        deck._print_pre_edit_revision()
        pages = ", ".join(str(index + 1) for index in selected_indices)
        print(f"  partial update: only pages {pages} will be replaced")
        print("  warning: replaced pages receive new slide IDs; comments and "
              "links to their old IDs are not preserved")
        return deck

    def load_inherited_styles(self) -> None:
        """Read the deck's layouts and masters for slot fitting (inherited_slot_styles).

        Only placeholder text is requested. Failing to read it is not fatal:
        fitting then falls back to what template.json records.
        """
        fields = ("layouts(objectId,pageElements(objectId,shape(placeholder,"
                  "text.textElements))),masters(objectId,pageElements(objectId,"
                  "shape(placeholder,text.textElements)))")
        from googleapiclient.errors import HttpError
        try:
            pres = _retry(
                lambda: self.slides.presentations().get(
                    presentationId=self.presentation_id, fields=fields
                ).execute(),
                what="presentations.get (placeholder styles)")
        except (HttpError, OSError) as exc:
            print(t("  warn: could not read placeholder styles; text fitting "
                    "uses template.json only ({err})", err=exc), file=sys.stderr)
            return
        if isinstance(pres, dict):
            self.inherited_styles = inherited_slot_styles(pres)

    def _present_slide_ids(self) -> list[str]:
        pres = _retry(
            lambda: self.slides.presentations().get(
                presentationId=self.presentation_id, fields="slides.objectId"
            ).execute(),
            what="presentations.get")
        return [s["objectId"] for s in pres.get("slides", [])]

    def _queue_slide_deletes(self, slide_ids: list[str]) -> int:
        for oid in slide_ids:
            self.requests.append({"deleteObject": {"objectId": oid}})
        return len(slide_ids)

    def _require_layouts(self, layout_keys=None) -> None:
        """Confirm up front that the deck has this template's master.

        Layout objectIds are preserved by Drive's duplication, so they match
        for a deck that originated from this template. This stops the process
        here, with a clear error, when someone tries to replace a deck built
        from a different master — rather than surfacing an unhelpful API
        error at commit time.
        """
        keys = list(layout_keys) if layout_keys else list(self.template.get("layouts", {}))
        needed: dict[str, str] = {}
        without_id: list[str] = []
        for key in keys:
            resolved, spec = self.resolve_layout(key)
            layout_id = spec.get("layoutId")
            if layout_id:
                needed[layout_id] = resolved
            else:
                without_id.append(resolved)
        if without_id:
            # A generationMode: "create" template (e.g. blank-16x9) has no
            # real layouts and is built with predefinedLayout instead. There's
            # no guarantee it matches the replacement target's master, so
            # this case is disallowed
            raise ValueError(
                t("template '{tpl}' declares no layoutId for {layouts}; "
                  "--into needs a template with real layouts",
                  tpl=self.template.get("name", "?"),
                  layouts=", ".join(sorted(set(without_id)))))
        pres = _retry(
            lambda: self.slides.presentations().get(
                presentationId=self.presentation_id, fields="layouts.objectId"
            ).execute(),
            what="presentations.get")
        present = {lay["objectId"] for lay in pres.get("layouts", [])}
        missing = sorted(name for lid, name in needed.items() if lid not in present)
        if missing:
            raise ValueError(
                t("the deck {pid} was not built from template '{tpl}' "
                  "(layouts not found: {missing}); --into only replaces a deck "
                  "generated from the same template",
                  pid=self.presentation_id,
                  tpl=self.template.get("name", "?"),
                  missing=", ".join(missing)))

    def _print_pre_edit_revision(self) -> None:
        """Print the pre-edit revision so it can be rolled back to. Just warns if it can't be read."""
        try:
            # Page through every result the same way snapshot_version.py does,
            # so the latest revision isn't missed even for decks with over
            # 1000 revisions
            revisions: list[dict] = []
            token = None
            while True:
                res = self.drive.revisions().list(
                    fileId=self.presentation_id,
                    fields="nextPageToken,revisions(id,modifiedTime)",
                    pageSize=1000, pageToken=token,
                ).execute()
                revisions.extend(res.get("revisions", []))
                token = res.get("nextPageToken")
                if not token:
                    break
        except Exception as exc:                       # noqa: BLE001 — informational only
            print(t("  warn: could not read the revision history ({err}); "
                    "snapshot the deck before replacing it", err=exc),
                  file=sys.stderr)
            return
        if revisions:
            last = revisions[-1]
            print(t("  pre-edit revision: {rev} ({time}) — roll back from "
                    "File > Version history",
                    rev=last.get("id"), time=last.get("modifiedTime")))

    def _delete_existing_slides(self) -> None:
        """Delete the template's bundled slides that remain right after duplication."""
        present = self._present_slide_ids()
        expected = set(self.template.get("existingSlideIds", []))
        stale = expected - set(present)
        if stale:
            print(
                t("  warn: template.json existingSlideIds contains IDs that "
                  "do not exist: {ids}\n        The template may have been "
                  "updated; re-analyze it with inspect_template.py.",
                  ids=sorted(stale)),
                file=sys.stderr,
            )
        # Delete every slide that actually exists (so none are missed even if
        # the template side gained more slides)
        self._queue_slide_deletes(present)

    # ---------- Layout resolution ----------

    def resolve_layout(self, key: str) -> tuple[str, dict]:
        """Look up a layout definition by role name (e.g. CONTENT) or layout key."""
        layouts = self.template["layouts"]
        resolved = self.template.get("roles", {}).get(key, key)
        if resolved not in layouts:
            roles = sorted(self.template.get("roles", {}))
            raise KeyError(
                t("cannot resolve layout '{key}'; available roles: {roles} / "
                  "layout keys: {keys}", key=key, roles=roles,
                  keys=sorted(layouts))
            )
        return resolved, layouts[resolved]

    # ---------- Adding slides ----------

    def _next_id(self, prefix: str) -> str:
        self._counter += 1
        # objectId is capped at 50 characters; truncate the prefix so long layout names still fit
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
        title_font_size: float | None = None,
        body_font_size: float | None = None,
        body_line_spacing: float | None = None,
        body_space_above: float | None = None,
        body_space_below: float | None = None,
        text_fit: str | None = None,
        min_font_size: float | None = None,
    ) -> dict:
        """Add a slide with the given layout and fill in its placeholders.

        Text that would overflow its slot is fitted to it (`text_fit`,
        "shrink" by default: tighten the inner margin, then the font, no
        smaller than `min_font_size`). What was changed is returned as
        "fitNotes". See fit_slot().

        `bodies` is for 2-column/3-column layouts. It's poured in order into
        BODY placeholder indices 0, 1, 2, …. `body` is equivalent to `bodies=[body]`.

        Returns {"slideId", "placeholders", "layout", "layoutKey"}. Use this
        slideId as pageObjectId if you want to draw additional figures.
        """
        resolved_key, layout = self.resolve_layout(layout_key)
        declared = declared_slots(layout)
        draw_specs = self._draw_specs(layout)

        if body is not None and bodies is not None:
            raise ValueError(t("body and bodies cannot be specified together"))
        if body is not None:
            bodies = [body]

        # Validate before queuing any requests, so a failure doesn't leave anything half-done.
        title_slot = ("TITLE" if "TITLE" in declared
                      else "CENTERED_TITLE" if "CENTERED_TITLE" in declared
                      else None)
        for ph_type, value in ((title_slot or "TITLE", title),
                               ("SUBTITLE", subtitle)):
            if value is not None and ph_type not in declared:
                raise ValueError(
                    t("layout '{key}' ({name}) has no {ph} placeholder; "
                      "it declares {declared}", key=layout_key,
                      name=layout["displayName"], ph=ph_type,
                      declared=declared)
                )
        body_slots = [p for p in declared if p.split("#")[0] == "BODY"]
        if bodies is not None and len(bodies) > len(body_slots):
            raise ValueError(
                t("layout '{key}' ({name}) has only {slots} BODY slots but "
                  "{given} were given (declares: {declared})", key=layout_key,
                  name=layout["displayName"], slots=len(body_slots),
                  given=len(bodies), declared=declared)
            )

        slide_id = self._next_id("slide")
        ph_ids: dict[str, str] = {}
        mappings = []
        # SLIDE_NUMBER is excluded because the API silently ignores it even if
        # mapped (drawn instead by add_page_numbers)
        for name in [t for t in layout.get("placeholders", [])
                     if t.split("#")[0] in FILLABLE]:
            ph_type, _, idx = name.partition("#")
            idx = int(idx) if idx else 0
            safe = name.replace("#", "x").lower()
            oid = self._next_id(f"{resolved_key.lower()}_{safe}")
            ph_ids[name] = oid
            mappings.append(
                {"layoutPlaceholder": {"type": ph_type, "index": idx}, "objectId": oid}
            )

        create_req: dict = {"objectId": slide_id}
        if layout.get("layoutId"):
            create_req["slideLayoutReference"] = {"layoutId": layout["layoutId"]}
        else:
            # A generationMode: "create" template has no real layouts, so the
            # page comes from a predefined one and its slots are drawn below
            create_req["slideLayoutReference"] = {
                "predefinedLayout": layout.get("predefinedLayout", "BLANK")}
        if mappings:
            create_req["placeholderIdMappings"] = mappings
        if index is not None:
            create_req["insertionIndex"] = index
        self.requests.append({"createSlide": create_req})
        self.slide_ids.append(slide_id)
        self._added.append(
            {"slideId": slide_id, "layoutKey": resolved_key, "layout": layout}
        )

        filled_bodies = list(zip(body_slots, bodies or []))

        # Coordinate-positioned slots are drawn as text boxes, and only the
        # ones that get text — an empty drawn box would still be on the page.
        # A real placeholder always wins, so nothing is drawn twice.
        drawn: set[str] = set()
        for name, value in ([(title_slot or "TITLE", title),
                             ("SUBTITLE", subtitle)] + filled_bodies):
            if value is None or name in ph_ids or name not in draw_specs:
                continue
            ph_ids[name] = self._draw_slot(slide_id, draw_specs[name])
            drawn.add(name)

        # Plan how each slot's text fits its slot before any styling is queued
        fits: dict[str, tuple[Fit, float]] = {}
        fit_notes: list[str] = []
        fit_warnings: list[str] = []
        for name, value, explicit, is_body in (
                [(title_slot or "TITLE", title, title_font_size, False),
                 ("SUBTITLE", subtitle, None, False)]
                + [(n, v, body_font_size, True) for n, v in filled_bodies]):
            if value is None or name not in ph_ids:
                continue
            planned = fit_slot(
                layout, name, value, explicit_size=explicit, body=is_body,
                drawn=name in drawn, mode=text_fit, min_size=min_font_size,
                line_spacing=body_line_spacing if is_body else None,
                space_above=body_space_above if is_body else None,
                space_below=body_space_below if is_body else None,
                roles=self.body_roles(),
                inherited=self.inherited_styles.get(layout.get("layoutId")))
            if planned is None:
                continue
            fits[name] = planned
            if not planned[0].fits:
                fit_warnings.append(t(
                    "{slot} still overflows its slot at {size:g}pt; reduce the "
                    "text, lower minFontSize, or split the slide",
                    slot=name, size=planned[0].size))
                continue
            detail = describe_fit(planned[1], TEXT_INSET_X, planned[0])
            if detail:
                fit_notes.append(t("{slot}: text fitted to the slot ({detail})",
                                   slot=name, detail=detail))

        for name, value in ((title_slot or "TITLE", title), ("SUBTITLE", subtitle)):
            if value is None:
                continue
            text = "\n".join(value) if isinstance(value, list) else value
            self.requests.append(
                {"insertText": {"objectId": ph_ids[name], "text": text}}
            )
            if name in drawn:
                self.requests += _drawn_text_styles(ph_ids[name], draw_specs[name])
            # Depending on the template, the title's default size may only fit
            # about 20 characters per line. Shrink long action titles with
            # titleFontSize to fit them on one line; a fitted size wins over it
            size = title_font_size if name == (title_slot or "TITLE") else None
            self._queue_slot_fit(ph_ids[name], fits.get(name), size,
                                 drawn=name in drawn,
                                 align=(draw_specs.get(name) or {}).get("align"))

        # Each body line can have its own role and inline emphasis, so build it while tracking ranges
        body_spans: dict[str, list[dict]] = {}
        for name, value in filled_bodies:
            if value is None:
                continue
            text, spans = self._compose_body(value)
            body_spans[name] = spans
            self.requests.append(
                {"insertText": {"objectId": ph_ids[name], "text": text}}
            )
            if name in drawn:
                self.requests += _drawn_text_styles(ph_ids[name], draw_specs[name])

        # Adjust the body's appearance. A placeholder's default size is often
        # generous, meant for hand-typed text, and Japanese body text looks
        # cramped unless the line spacing is widened (default 100-115%).
        for name, value in filled_bodies:
            if value is None:
                continue
            self._queue_slot_fit(ph_ids[name], fits.get(name), body_font_size,
                                 drawn=name in drawn,
                                 align=(draw_specs.get(name) or {}).get("align"))
            # A placeholder's default may also carry space before/after
            # paragraphs, throwing off the line-count estimate significantly.
            # spaceAbove / spaceBelow can be set explicitly too
            para_style: dict = {}
            if body_line_spacing is not None:
                para_style["lineSpacing"] = body_line_spacing
            if body_space_above is not None:
                para_style["spaceAbove"] = {
                    "magnitude": body_space_above, "unit": "PT"}
            if body_space_below is not None:
                para_style["spaceBelow"] = {
                    "magnitude": body_space_below, "unit": "PT"}
            if para_style:
                self.requests.append({"updateParagraphStyle": {
                    "objectId": ph_ids[name],
                    "style": para_style,
                    "textRange": {"type": "ALL"},
                    "fields": ",".join(para_style),
                }})

        # Role-tagged lines and inline emphasis. **Must be queued after the
        # ALL-range styles** (queuing them first gets overwritten by the
        # blanket style and has no effect)
        for name, spans in body_spans.items():
            fit, base = fits.get(name, (None, None))
            if fit is not None and fit.size != base:
                spans = _scale_spans(spans, fit.size / base)
            self._apply_body_spans(ph_ids[name], spans)

        if notes:
            self._notes.append((slide_id, notes))

        return {
            "slideId": slide_id,
            "placeholders": ph_ids,
            "layout": layout,
            "layoutKey": resolved_key,
            "fitNotes": fit_notes,
            "fitWarnings": fit_warnings,
        }

    def _queue_slot_fit(self, oid: str, planned, size, *, drawn: bool,
                        align: str | None = None) -> None:
        """Queue a filled slot's font size, fitted margin and autofit NONE.

        `size` is the size the spec asked for (or None); a fitted size wins.
        Queued after the slot's own base styles, so it overrides them.
        """
        fit, base = planned or (None, None)
        if fit is not None and fit.size != base:
            size = fit.size
        if size is not None:
            self.requests.append({"updateTextStyle": {
                "objectId": oid,
                "style": {"fontSize": {"magnitude": size, "unit": "PT"}},
                "textRange": {"type": "ALL"},
                "fields": "fontSize",
            }})
        indent = _slot_indent(fit.inset, drawn, align) if fit is not None else {}
        if indent:
            self.requests.append({"updateParagraphStyle": {
                "objectId": oid, "style": indent,
                "textRange": {"type": "ALL"}, "fields": ",".join(indent)}})
        # NONE is the only fitting the API accepts, and the one the text was
        # fitted for. Stating it keeps the PPTX export the same
        self.requests.append({"updateShapeProperties": {
            "objectId": oid,
            "shapeProperties": {"autofit": {"autofitType": "NONE"}},
            "fields": "autofit.autofitType"}})

    # ---------- Drawn slots (generationMode: create) ----------

    @staticmethod
    def _draw_specs(layout: dict) -> dict[str, dict]:
        """Slot name -> how to draw it, merging drawText with its font family."""
        styles = layout.get("textStyles") or {}
        specs = {}
        for key, geo in (layout.get("drawText") or {}).items():
            specs[draw_slot_name(key)] = {
                **geo, "fontFamily": (styles.get(key) or {}).get("fontFamily")}
        return specs

    def _draw_slot(self, slide_id: str, spec: dict) -> str:
        """Queue an empty text box at the slot's coordinates and return its id."""
        oid = self._next_id("drawn")
        self.requests.append(
            {"createShape": {"objectId": oid, "shapeType": "TEXT_BOX",
             "elementProperties": {"pageObjectId": slide_id,
             "size": {"width": {"magnitude": _auth.inches(spec["w"]), "unit": "EMU"},
                      "height": {"magnitude": _auth.inches(spec["h"]), "unit": "EMU"}},
             "transform": {"scaleX": 1, "scaleY": 1,
                           "translateX": _auth.inches(spec["x"]),
                           "translateY": _auth.inches(spec["y"]),
                           "unit": "EMU"}}}})
        return oid

    # ---------- Body emphasis ----------

    def body_roles(self) -> dict:
        """The per-role appearance defined by the template (or the default if none)."""
        return {**DEFAULT_BODY_ROLES, **(self.template.get("bodyRoles") or {})}

    def _resolve_color(self, value: str) -> dict | None:
        """Resolve "#RRGGBB" or "theme:DARK1" to an rgbColor."""
        if not isinstance(value, str):
            return None
        if value.startswith("theme:"):
            hexv = (self.template.get("colors") or {}).get(value[6:].lower())
            if not hexv:
                return None
            value = hexv
        return _auth.hex_to_rgb(value)

    def _compose_body(self, value) -> tuple[str, list[dict]]:
        """Assemble the body into a single string and return range-tagged style specs.

        Indices are counted in UTF-16 units, same as the Slides API.
        """
        roles = self.body_roles()
        parts, spans, cursor = [], [], 0
        for text, role in normalize_body_lines(value):
            plain, inline = parse_inline(text)
            if any(ord(ch) > 0xFFFF for ch in plain):
                print(t("  warn: body text contains characters outside the BMP "
                        "(emoji etc.); emphasis ranges may shift"),
                      file=sys.stderr)
            start = cursor
            end = start + len(plain)
            style = roles.get(role) if role else None
            if role and style is None:
                print(t("  warn: unknown body role '{role}' (known: {known})",
                        role=role, known=sorted(roles)), file=sys.stderr)
            if style:
                spans.append({"start": start, "end": end, "style": style,
                              "paragraph": True})
            for s, e, kind, target in inline:
                span = {"start": start + s, "end": start + e,
                        "style": roles.get(kind, {}), "paragraph": False}
                if kind == "link":
                    link = link_target(target)
                    if link is None:
                        print(t("  warn: cannot use '{target}' as a link "
                                "(use https://… or #12)", target=target),
                              file=sys.stderr)
                        continue
                    span["link"] = link
                spans.append(span)
            parts.append(plain)
            cursor = end + 1        # for the newline
        return "\n".join(parts), spans

    def _apply_body_spans(self, object_id: str, spans: list[dict]) -> None:
        for span in spans:
            if span["end"] <= span["start"]:
                continue          # attaching a role to an empty line is meaningless
            style, fields = {}, []
            for key in _TEXT_STYLE_KEYS:
                if key not in span["style"]:
                    continue
                val = span["style"][key]
                if key == "color":
                    rgb = self._resolve_color(val)
                    if rgb is None:
                        continue
                    style["foregroundColor"] = {"opaqueColor": {"rgbColor": rgb}}
                    fields.append("foregroundColor")
                elif key == "fontSize":
                    style["fontSize"] = {"magnitude": val, "unit": "PT"}
                    fields.append("fontSize")
                else:
                    style[key] = val
                    fields.append(key)
            if span.get("link"):
                style["link"] = span["link"]
                fields.append("link")
            rng = {"type": "FIXED_RANGE",
                   "startIndex": span["start"], "endIndex": span["end"]}
            if fields:
                self.requests.append({"updateTextStyle": {
                    "objectId": object_id, "style": style,
                    "textRange": rng, "fields": ",".join(fields)}})
            if not span.get("paragraph"):
                continue
            para, pfields = {}, []
            for key in _PARA_STYLE_KEYS:
                if key in span["style"]:
                    para[key] = {"magnitude": span["style"][key], "unit": "PT"}
                    pfields.append(key)
            if pfields:
                self.requests.append({"updateParagraphStyle": {
                    "objectId": object_id, "style": para,
                    "textRange": rng, "fields": ",".join(pfields)}})

    # ---------- Page numbers ----------

    def add_page_numbers(self, start: int | None = None) -> int:
        """Draw page numbers as text boxes and return the count drawn.

        The Slides API cannot create a SLIDE_NUMBER placeholder (specifying it
        in createSlide's placeholderIdMappings doesn't error, it's just
        silently ignored), so this draws it manually at the layout's
        slideNumber coordinates.

        Note: numbers are assigned in add_slide() call order. For a deck where
        add_slide(index=...) was used to insert at a specific position, this
        won't match the actual on-page order.
        """
        cfg = self.template.get("pageNumber", {})
        # When stacking after slides kept via keep_existing, advance the
        # numbering start by that many slides
        start = cfg.get("startAt", 1) + self.kept_slides if start is None else start
        return sum(
            self._add_page_number(entry, start + offset, cfg)
            for offset, entry in enumerate(self._added)
        )

    def add_page_numbers_at(self, page_indices: list[int]) -> int:
        """Draw numbers for newly added pages at their original zero-based positions."""
        if len(page_indices) != len(self._added):
            raise ValueError("page number positions must match the added slides")
        cfg = self.template.get("pageNumber", {})
        start = cfg.get("startAt", 1)
        drawn = 0
        for entry, index in zip(self._added, page_indices):
            drawn += self._add_page_number(entry, start + index, cfg)
        return drawn

    def _add_page_number(self, entry: dict, number: int, cfg: dict) -> int:
        """Draw one page number, returning one when the layout declares a slot."""
        layout = entry["layout"]
        geo = layout.get("elements", {}).get("slideNumber")
        if not layout.get("hasPageNumber") or not geo:
            return 0
        font = cfg.get("font", "Arial")
        size = cfg.get("fontSize", 7)
        color = cfg.get("color", "#666666")
        align = cfg.get("align", "END")
        right = geo["x"] + geo["w"]
        w = max(geo["w"], 0.5)
        x = right - w if align == "END" else geo["x"]
        oid = self._next_id("pagenum")
        self.requests += [
            {"createShape": {"objectId": oid, "shapeType": "TEXT_BOX",
             "elementProperties": {"pageObjectId": entry["slideId"],
             "size": {"width": {"magnitude": _auth.inches(w), "unit": "EMU"},
                      "height": {"magnitude": _auth.inches(geo["h"]), "unit": "EMU"}},
             "transform": {"scaleX": 1, "scaleY": 1,
                           "translateX": _auth.inches(x),
                           "translateY": _auth.inches(geo["y"]), "unit": "EMU"}}}},
            {"insertText": {"objectId": oid, "text": str(number)}},
            {"updateTextStyle": {"objectId": oid,
             "style": {"fontFamily": font,
                       "fontSize": {"magnitude": size, "unit": "PT"},
                       "foregroundColor": {"opaqueColor": {
                           "rgbColor": _auth.hex_to_rgb(color)}}},
             "textRange": {"type": "ALL"},
             "fields": "fontFamily,fontSize,foregroundColor"}},
            {"updateParagraphStyle": {"objectId": oid,
             "style": {"alignment": align}, "textRange": {"type": "ALL"},
             "fields": "alignment"}},
        ]
        return 1

    # ---------- Execution ----------

    def commit(self, chunk_size: int = MAX_REQUESTS_PER_BATCH) -> str:
        """Run the accumulated requests via batchUpdate and return the presentation URL."""
        try:
            # Local image uploads run in the background while drawing.
            # createImage's url must be filled in before the request goes out via batchUpdate
            if self.assets is not None:
                n_img = self.assets.flush()
                if n_img:
                    print(f"  images uploaded: {n_img}")
            if self.require_single_batch:
                count, size = _single_batch_size(self.requests)
                if count > MAX_REQUESTS_PER_BATCH or size > MAX_BATCH_BYTES:
                    raise ValueError(
                        "partial update exceeds the atomic batch limit "
                        f"({count} requests / {size} bytes); split it into fewer pages"
                    )
            for n, chunk in enumerate(_batches(self.requests, chunk_size), 1):
                # batchUpdate is non-idempotent; resending after a lost response risks a half-built deck, so stop instead
                _retry(
                    lambda: self.slides.presentations().batchUpdate(
                        presentationId=self.presentation_id, body={"requests": chunk}
                    ).execute(),
                    what=f"batchUpdate ({len(chunk)} requests)",
                    idempotent=False, url=self.url)
                print(f"  batch {n}: {len(chunk)} requests")
            self.requests = []
            if self._notes or self.image_fixups or self.pending_groups:
                self._post_pass()
            # --into's rename happens only after the content replacement has succeeded (see open())
            if self.pending_title:
                _retry(
                    lambda: self.drive.files().update(
                        fileId=self.presentation_id,
                        body={"name": self.pending_title}, fields="id",
                        supportsAllDrives=True).execute(),
                    what=t("rename"))
                self.pending_title = None
        finally:
            # Slides copies images in at insertion time. Even if batchUpdate
            # fails, always clean up here so no temporary upload — shared as
            # "anyone with the link can view" — gets left behind
            if self.assets is not None:
                self.assets.cleanup()
        return self.url

    def _post_pass(self) -> None:
        """A second batchUpdate that uses information only known after slide creation.

        - Speaker notes: the notes frame's objectId isn't in createSlide's response
        - Image dimension fixup: since createImage **always preserves the
          original aspect ratio regardless of the requested size**,
          frame-filling placement (fit="cover" / "stretch") can't be achieved
          at creation time. This reads the raw size of the created element and
          fixes it by overwriting its transform with absolute values.
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
                print(t("  warn: notes placeholder for {slide_id} not found; "
                        "skipped", slide_id=slide_id), file=sys.stderr)
                continue
            reqs.append({"insertText": {"objectId": oid, "text": text}})
        n_notes = len(reqs)

        n_img = 0
        for oid, x, y, w, h in self.image_fixups:
            size = sizes.get(oid) or {}
            mw = size.get("width", {}).get("magnitude")
            mh = size.get("height", {}).get("magnitude")
            if not mw or not mh:
                print(t("  warn: could not read the size of image {oid}; "
                        "frame-filling placement was not applied", oid=oid),
                      file=sys.stderr)
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

        # Grouping goes last: the image transforms above are ABSOLUTE, and on
        # a grouped child they would be read in the group's coordinate space
        n_grp = 0
        for oids in self.pending_groups:
            # objectId is left out on purpose, so the API mints a unique one
            reqs.append({"groupObjects": {"childrenObjectIds": oids}})
            n_grp += 1

        if reqs:
            # batchUpdate is non-idempotent; resending after a lost response risks a half-built deck, so stop instead
            _retry(
                lambda: self.slides.presentations().batchUpdate(
                    presentationId=self.presentation_id, body={"requests": reqs}
                ).execute(),
                what=f"batchUpdate (post pass, {len(reqs)} requests)",
                idempotent=False, url=self.url)
            if n_notes:
                print(f"  speaker notes: {n_notes} slides")
            if n_img:
                print(f"  image fit: {n_img} images")
            if n_grp:
                print(f"  grouped figures: {n_grp}")
        self._notes = []
        self.image_fixups = []
        self.pending_groups = []


# ---------- Figure / image block ----------

# The types usable in a spec's "figures", and the order of keys passed as positional arguments.
# Keys not listed here are converted to snake_case and passed as keyword arguments.
FIGURES: dict[str, tuple[str, list[str]]] = {
    # Illustrative figures (illustrations.py; drawn purely from shapes, no network needed)
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
    "comparison":   ("comparison",   ["x", "y", "w", "h", "columns"]),
    "influence_graph": ("influence_graph", ["x", "y", "w", "h", "people"]),
    "outcome_tree":    ("outcome_tree",    ["x", "y", "w", "h", "nodes"]),
    "journey":      ("journey",      ["x", "y", "w", "h", "items"]),
    "timeline":     ("timeline",     ["x", "y", "w", "items"]),
    # Brand icon assets (icons.py; pasted via Drive, so network access is
    # needed. --dry-run substitutes a same-sized rectangle and checks only the coordinates)
    "asset_icon":       ("asset_icon",       ["name", "x", "y", "size"]),
    "asset_icon_row":   ("asset_icon_row",   ["x", "y", "w", "items"]),
    "asset_icon_flow":  ("asset_icon_flow",  ["x", "y", "w", "items"]),
    "asset_icon_grid":  ("asset_icon_grid",  ["x", "y", "w", "items"]),
    "asset_icon_cards": ("asset_icon_cards", ["x", "y", "w", "h", "items"]),
    # Official cloud-vendor icons (cloud_icons.py). Same as asset_icon:
    # --dry-run substitutes a rectangle and checks only the coordinates
    "cloud_icon":      ("cloud_icon",      ["name", "x", "y", "size"]),
    "cloud_icon_row":  ("cloud_icon_row",  ["x", "y", "w", "items"]),
    "cloud_icon_flow": ("cloud_icon_flow", ["x", "y", "w", "items"]),
    "cloud_icon_grid": ("cloud_icon_grid", ["x", "y", "w", "items"]),
    "cloud_zone":      ("cloud_zone",      ["x", "y", "w", "h"]),
    # Structural diagrams (existing parts from diagrams.py)
    # band is a filled-only rounded rectangle, used as a figure's backdrop
    # (e.g. the white card behind a cover / section-divider). Draw it before
    # the content (drawing it after would cover the content)
    "band":         ("band",         ["x", "y", "w", "h"]),
    "cards":        ("cards",        ["x", "y", "w", "h", "items"]),
    "flow":         ("flow",         ["x", "y", "w", "h", "items"]),
    "hbars":        ("hbars",        ["x", "y", "w", "items"]),
    "metric":       ("metric",       ["x", "y", "w", "h", "value", "caption"]),
    # Tables / charts (charts.py). pie is pasted as an image, but --dry-run
    # substitutes a placeholder and runs the coordinate check itself
    "table":         ("table",         ["x", "y", "w", "headers", "rows"]),
    "vbars":         ("vbars",         ["x", "y", "w", "h", "items"]),
    "vbars_grouped": ("vbars_grouped", ["x", "y", "w", "h", "categories", "series"]),
    "vbars_stacked": ("vbars_stacked", ["x", "y", "w", "h", "categories", "series"]),
    "linechart":     ("linechart",     ["x", "y", "w", "h", "labels", "series"]),
    "pie":           ("pie",           ["x", "y", "size", "items"]),
    "pareto":        ("pareto",        ["x", "y", "w", "h", "items"]),
    # Business-framework diagrams (patterns.py; drawn purely from shapes, no network needed)
    "posmap":         ("posmap",         ["x", "y", "w", "h", "points"]),
    "gantt":          ("gantt",          ["x", "y", "w", "h", "columns", "rows"]),
    "orgchart":       ("orgchart",       ["x", "y", "w", "h", "tree"]),
    "lean_canvas":    ("lean_canvas",    ["x", "y", "w", "h", "blocks"]),
    "nested_circles": ("nested_circles", ["x", "y", "w", "h", "rings"]),
    "testimonial":    ("testimonial",    ["x", "y", "w", "h", "quote", "name"]),
    "fishbone":       ("fishbone",       ["x", "y", "w", "h", "problem",
                                          "categories"]),
    # Event-information diagrams (events.py; drawn purely from shapes, no network needed)
    "event_mode_badge": ("event_mode_badge", ["x", "y", "mode"]),
    "event_overview":   ("event_overview",   ["x", "y", "w", "rows"]),
    "event_timetable":  ("event_timetable",  ["x", "y", "w", "rows"]),
    "event_speakers":   ("event_speakers",   ["x", "y", "w", "speakers"]),
    "event_access":     ("event_access",     ["x", "y", "w", "h"]),
    # Calendar diagrams (calendars.py; drawn purely from shapes, holidays come
    # from the bundled assets/holidays/jp.csv, no network needed)
    "month_calendar":   ("month_calendar",   ["x", "y", "w", "h", "month", "events"]),
    "day_gantt":        ("day_gantt",        ["x", "y", "w", "h", "start", "end",
                                              "rows"]),
    "day_agenda":       ("day_agenda",       ["x", "y", "w", "h", "start", "end",
                                              "items"]),
    "week_timetable":   ("week_timetable",   ["x", "y", "w", "h", "week", "events"]),
    "sprint_calendar":  ("sprint_calendar",  ["x", "y", "w", "h", "start", "sprints"]),
    "year_calendar":    ("year_calendar",    ["x", "y", "w", "h", "startMonth",
                                              "marks"]),
    "deadline_countdown": ("deadline_countdown", ["x", "y", "w", "h", "deadline",
                                                  "today", "label"]),
    "calendar_heatmap": ("calendar_heatmap", ["x", "y", "w", "h", "start", "end",
                                              "values"]),
    "shift_roster":     ("shift_roster",     ["x", "y", "w", "h", "start", "end",
                                              "people", "codes"]),
    # Page components and analysis diagrams (pages.py; drawn purely from shapes, no network needed)
    "governing_message": ("governing_message", ["x", "y", "w", "text"]),
    "lead_in":           ("lead_in",           ["x", "y", "w", "text"]),
    "so_what":           ("so_what",           ["x", "y", "w", "h", "text"]),
    # Native list paragraphs (createParagraphBullets), not "・" in the text
    "list":              ("bullet_list",       ["x", "y", "w", "items"]),
    "source_note":       ("source_note",       ["x", "y", "w", "source"]),
    # exhibit_frame's return value (the inner area) can't be received from
    # JSON. Draw the frame, then draw the contents as a separate figure with
    # its inner coordinates matched by hand (roughly x+0.2 / header bottom +0.45)
    "exhibit_frame":     ("exhibit_frame",     ["x", "y", "w", "h", "number", "title"]),
    "mece_tree":         ("mece_tree",         ["x", "y", "w", "h", "tree"]),
    "waterfall":         ("waterfall",         ["x", "y", "w", "h", "items"]),
    "rating_matrix":     ("rating_matrix",     ["x", "y", "w", "columns", "rows"]),
    "exec_summary":      ("exec_summary",      ["x", "y", "w", "h", "situation",
                                                "complication", "resolution"]),
    "storyline":         ("storyline",         ["x", "y", "w", "titles"]),
    "ghost":             ("ghost",             ["x", "y", "w", "h", "slides"]),
    # Code samples (diagrams.py; monospace + syntax highlighting, no network needed)
    "code_block":   ("code_block",   ["x", "y", "w", "h", "code"]),
    # Images (images.py)
    "image":        ("image",        ["x", "y", "w", "h", "source"]),
    "aiImage":      ("ai_image",     ["x", "y", "w", "h", "prompt"]),
}

# Types that call the API (i.e. cannot be run with --dry-run)
NETWORK_FIGURES = {"image", "aiImage"}

def min_table_row_h(size: float) -> float:
    """The minimum height (in inches) a Slides table row actually takes.

    Setting `minRowHeight` below this value doesn't shrink the row. This is
    the text line height plus cell padding, calibrated to measurements (about
    0.34in at size 9, 0.32in at size 8.5). Use this as a lower bound when estimating height.
    """
    return max(0.28, size * 1.45 / 72 + 0.16)


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
    """Sort a figure block into (positional args, keyword args)."""
    _, order = FIGURES[fig["type"]]
    args = [fig[k] for k in order if k in fig]
    # "group" steers draw_figures, not the figure function. Unknown keys are
    # passed through as keyword arguments, so leaving it in raises TypeError
    kwargs = {_snake(k): v for k, v in fig.items()
              if k not in ("type", "group") and k not in order}
    return args, kwargs


def _check_text_margin(value, where: str) -> list[str]:
    """Reject a textMargin that is not a usable inner margin, in inches."""
    if value is None:
        return []
    if not isinstance(value, (int, float)):
        return [t("{where}: 'textMargin' must be a number (inches)", where=where)]
    if value < 0 or value > 1.0:
        return [t("{where}: 'textMargin' is {v}in; give an inner margin "
                  "between 0 and 1.0in", where=where, v=value)]
    return []


def _text_margin(spec: dict, slide: dict) -> float | None:
    """The inner margin figures on this slide draw text with, in inches.

    `textMargin` on the slide wins over `defaults.textMargin`; None leaves the
    inset Slides bakes in. Lower it to pack a dense page — a figure can still
    override it per call.
    """
    if slide.get("textMargin") is not None:
        return slide["textMargin"]
    return (spec.get("defaults") or {}).get("textMargin")


def _check_text_fit(block: dict, where: str) -> list[str]:
    """Reject a textFit / minFontSize that fitting cannot use."""
    out = []
    mode = block.get("textFit")
    if mode is not None and mode not in FIT_MODES:
        out.append(t("{where}: 'textFit' must be one of: {modes}",
                     where=where, modes=", ".join(FIT_MODES)))
    v = block.get("minFontSize")
    if v is not None and (isinstance(v, bool) or not isinstance(v, (int, float))
                          or v <= 0):
        out.append(t("{where}: 'minFontSize' must be a positive number (pt)",
                     where=where))
    return out


def _text_fit(spec: dict, slide: dict) -> str | None:
    """How text that overflows is fitted on this slide (slide wins over defaults)."""
    if slide.get("textFit") is not None:
        return slide["textFit"]
    return (spec.get("defaults") or {}).get("textFit")


def _min_font_size(spec: dict, slide: dict) -> float | None:
    """The smallest size fitting may shrink text to on this slide, in pt.

    An explicit `minFontSize` (slide, then defaults) wins. Otherwise a print
    deck (`"density": "print"`) may shrink down to PRINT_MIN_FONT_PT — 8, 9
    and 10pt are fine on paper — and a presentation deck keeps the default
    floor (70% of each size, never below 8pt). None means that default.
    """
    if slide.get("minFontSize") is not None:
        return slide["minFontSize"]
    explicit = (spec.get("defaults") or {}).get("minFontSize")
    if explicit is not None:
        return explicit
    if spec.get("density") == "print":
        return PRINT_MIN_FONT_PT
    return None


def _check_density(spec: dict) -> list[str]:
    """Reject a spec-level density that is neither print nor presentation."""
    density = spec.get("density")
    if density is None or density in DENSITIES:
        return []
    return [t("'density' must be one of: {densities}",
              densities=", ".join(DENSITIES))]


# Kinds the Slides API refuses to group, plus images: an image's
# frame-filling transform is applied after creation with ABSOLUTE values,
# which a group's coordinate space would reinterpret (see Deck._post_pass)
UNGROUPABLE = ("TABLE", "IMAGE")


def _group_mode(spec: dict, slide: dict) -> bool:
    """Whether this slide's figures are grouped (slide wins over defaults)."""
    for src in (slide, spec.get("defaults") or {}):
        if "group" in src:
            return bool(src["group"])
    return False


def draw_figures(canvas, figures: list, *, skip_network: bool = False,
                 group: bool = False) -> None:
    """Draw a figures block onto the Canvas.

    With `group`, the page elements each figure creates are queued to be
    grouped, so a composite figure — a flow's boxes and arrows, a card's
    frame and text — moves as one object in the editor. It changes nothing
    about how the slide looks. Tables and images are left out (`UNGROUPABLE`),
    and a figure that made fewer than 2 groupable elements is skipped, since
    the API requires at least two.
    """
    for fig in figures:
        kind = fig["type"]
        if skip_network and kind in NETWORK_FIGURES:
            continue
        method, _ = FIGURES[kind]
        args, kwargs = _figure_args(fig)
        start = len(canvas.elements)
        getattr(canvas, method)(*args, **kwargs)
        if not group or not fig.get("group", True):
            continue
        # A deck assembled by some other script may not carry the queue
        queue = getattr(canvas.deck, "pending_groups", None)
        if queue is None:
            continue
        oids = [oid for oid, k in canvas.elements[start:]
                if k not in UNGROUPABLE]
        if len(oids) >= 2:
            queue.append(oids)


def validate_figures(spec: dict, page: dict, template: dict | None = None) -> list[str]:
    """Validate a figures block without calling the API.

    When `template` is passed, this also checks overlap with the master's
    logo/footer band. Even content that fits within the page becomes
    unreadable if it overlaps that band, so this catches it here as a defect
    detectable from coordinates alone.
    """
    problems = []
    pw = page.get("widthInches", 10.0)
    ph = page.get("heightInches", 5.625)
    band = footer_band(template) if template else None
    layouts = (template or {}).get("layouts", {})
    roles = (template or {}).get("roles", {})
    problems += _check_text_margin(
        (spec.get("defaults") or {}).get("textMargin"), "defaults")
    problems += _check_text_fit(spec.get("defaults") or {}, "defaults")
    problems += _check_density(spec)
    for i, s in enumerate(spec.get("slides", [])):
        problems += _check_text_margin(s.get("textMargin"), f"slides[{i}]")
        problems += _check_text_fit(s, f"slides[{i}]")
        figs = s.get("figures")
        if figs is None:
            continue
        # A layout with a full-page rectangle covers the master's decoration, so exclude it from the band check
        layout = layouts.get(roles.get(s.get("layout"), s.get("layout")), {})
        covers_footer = any(
            d.get("w", 0) > pw * 0.95 and d.get("h", 0) > ph * 0.9
            for d in (layout.get("decorations") or []))
        if not isinstance(figs, list):
            problems.append(t("slides[{i}]: 'figures' must be an array", i=i))
            continue
        for j, fig in enumerate(figs):
            where = f"slides[{i}].figures[{j}]"
            if not isinstance(fig, dict) or "type" not in fig:
                problems.append(t("{where}: missing 'type'", where=where))
                continue
            kind = fig["type"]
            if kind not in FIGURES:
                problems.append(t(
                    "{where}: unknown type '{kind}' (available: {available})",
                    where=where, kind=kind, available=sorted(FIGURES)))
                continue
            # Caught offline so --dry-run reports it, rather than failing
            # partway through a live generation that already created a deck
            if kind == "aiImage" and not settings.image_generation_enabled():
                problems.append(t(
                    "{where}: 'aiImage' needs Gemini image generation, which "
                    "is off in the settings (imageGeneration: off). Turn it "
                    "on with scripts/settings.py --image-generation on, or "
                    "replace the figure with a shape-drawn one "
                    "(illustrations / patterns)", where=where))
                continue
            _, order = FIGURES[kind]
            missing = [k for k in order if k not in fig]
            if missing:
                problems.append(t(
                    "{where}: type '{kind}' is missing required keys: "
                    "{missing}", where=where, kind=kind, missing=missing))
                continue
            for k in ("x", "y", "w", "h", "textMargin"):
                if k in fig and not isinstance(fig[k], (int, float)):
                    problems.append(t(
                        "{where}: '{k}' must be a number (inches)",
                        where=where, k=k))
            problems += _check_text_margin(fig.get("textMargin"), where)
            # "size" is a spatial quantity (inches) only for types that take
            # size as a positional argument (icon-family, pie). For others
            # like table it's a font size (pt), so using it in place of the
            # height would misread e.g. 8.5pt as 8.5in
            spatial_size = fig.get("size", 0) if "size" in order else 0
            x, y = fig.get("x", 0), fig.get("y", 0)
            w = fig.get("w", spatial_size)
            h = fig.get("h", spatial_size)
            # A table doesn't declare h; estimate it from the row count. A
            # Slides table row has a font-dependent minimum inner height, and
            # setting row_h below it doesn't shrink the row (measured ≈
            # 0.28in). Wrapping stretches it further, so this is a lower-bound estimate
            if kind == "table" and isinstance(fig.get("rows"), list):
                floor = min_table_row_h(fig.get("size", 10))
                rh = max(fig.get("rowH", fig.get("row_h", 0.34)), floor)
                hh = max(fig.get("headerH", fig.get("header_h", 0.38)), floor)
                h = hh + rh * len(fig["rows"])
            if isinstance(x, (int, float)) and isinstance(w, (int, float)):
                if x < 0 or x + w > pw + 0.01:
                    problems.append(t(
                        "{where}: extends horizontally past the page ({pw}in) "
                        "(x={x} w={w} → right edge {right:.2f}in)",
                        where=where, pw=pw, x=x, w=w, right=x + w))
            if isinstance(y, (int, float)) and isinstance(h, (int, float)):
                if y < 0 or y + h > ph + 0.01:
                    problems.append(t(
                        "{where}: extends vertically past the page ({ph}in) "
                        "(y={y} h={h} → bottom edge {bottom:.2f}in)",
                        where=where, ph=ph, y=y, h=h, bottom=y + h))
                # Overlap with the band is checked for **tables only**. A
                # table doesn't declare h, so the height derived from its row
                # count is nearly the actual size, making this check accurate.
                # Shape-based figures often have padding below their declared
                # frame's bottom edge (e.g. posmap's axis-label area), so
                # judging by the declared value would produce false positives.
                # For those, audit_bounds looks at the coordinates actually drawn
                elif (kind == "table" and band and not covers_footer
                      and y + h > band[0] + 0.01
                      and isinstance(x, (int, float)) and isinstance(w, (int, float))
                      and x < band[2] and x + w > band[1]):
                    problems.append(t(
                        "{where}: the table overlaps the master logo/footer "
                        "band (below y={band:.2f}in) (bottom edge "
                        "{bottom:.2f}in); reduce the rows or split it across "
                        "slides", where=where, band=band[0], bottom=y + h))
    return problems


class _StubDeck:
    """A dummy for driving Canvas under --dry-run. Never calls the API."""

    # Brand icons are images, so the real thing can't be fetched. The Canvas
    # side checks this flag and substitutes a same-sized rectangle, running
    # only the coordinate check
    dry = True

    def __init__(self):
        self.requests: list[dict] = []
        self.assets = None
        self.image_fixups: list[tuple] = []
        self.pending_groups: list[list[str]] = []


class DryRunDeck(_StubDeck):
    """A --dry-run stand-in for TemplateDeck.

    Since it passes add_slide / add_page_numbers / commit through without the
    API, a script that assembles a deck in code (scripts/scalar/*.py) can run
    only the coordinate/text-volume checks just by swapping in this deck.

    Like TemplateDeck, the template stays readable as `.template`, since
    scripts that draw their own page numbers look here for it.
    """

    def __init__(self, template: dict | None = None):
        super().__init__()
        self.template = template or {}
        self._n = 0
        self._counter = 0

    def _next_id(self, prefix: str) -> str:
        self._counter += 1
        return f"{prefix[:40]}_dry_{self._counter:03d}"

    def add_slide(self, layout_key, **kw):
        """Return a value shaped the same as TemplateDeck.add_slide.

        The caller may read the page-number position from ref["layout"], so slideId alone isn't enough.
        """
        self._n += 1
        self.last = dict(kw, layout=layout_key)
        resolved = self.template.get("roles", {}).get(layout_key, layout_key)
        return {
            "slideId": f"dry_{self._n}",
            "placeholders": {},
            "layout": (self.template.get("layouts", {}) or {}).get(resolved, {}),
            "layoutKey": resolved,
        }

    dry_run = True

    def add_page_numbers(self, start=None):
        return 0

    def commit(self, chunk_size=500):
        return t("(dry-run: nothing was generated)")


def run_build_cli(build, *, template, title, create_kwargs=None, epilogue=None,
                  count=None, description=None, argv=None) -> int:
    """The CLI every hand-built deck script wants.

    `build(deck, template)` draws the slides and returns the audit findings;
    this owns everything around it — the ``--folder`` / ``--dry-run`` pair,
    choosing between a stand-in deck and a real one, printing the findings, and
    the exit code that lets ``--dry-run`` stand as a gate in a pipeline. Written
    once because five scripts had drifted into five copies of it.

    `title` may be a callable, for a title that depends on the deck's data.
    `count` (int or callable) adds the slide count to the closing line.
    `epilogue` runs after a successful commit (a bill of materials, say).
    """
    p = argparse.ArgumentParser(description=description)
    p.add_argument("--folder", default=None,
                   help=t("Drive folder URL or ID to create the deck in"))
    p.add_argument("--dry-run", action="store_true",
                   help=t("check coordinates and text volume without calling the API"))
    args = p.parse_args(argv)

    tpl = load_template(template) if isinstance(template, str) else template
    if args.dry_run:
        deck = DryRunDeck(tpl)
    else:
        deck = TemplateDeck.create(tpl, title=title() if callable(title) else title,
                                   folder=args.folder, **(create_kwargs or {}))

    problems = build(deck, tpl)
    for message in problems:
        print(t("  audit: {message}", message=message))
    if args.dry_run:
        print(t("\ndry-run: {n} problems", n=len(problems)))
        return 1 if problems else 0

    url = deck.commit()
    if count is None:
        print(t("Done! Open: {url}", url=url))
    else:
        print(t("Done! {n} slides. Open: {url}",
                n=count() if callable(count) else count, url=url))
    if epilogue is not None:
        epilogue()
    return 0


def audit_figures(template: dict, spec: dict,
                  notes: list[str] | None = None) -> list[str]:
    """Expand figures into actual coordinates and check overlap/text overflow without the API.

    Catches at the spec stage defects that would otherwise go unnoticed until
    the deck is generated and its thumbnail is inspected. Images are excluded
    from this check because they require fetching the real file.
    """
    from diagrams import Canvas  # deferred import (not needed on every run outside --dry-run)

    out = []
    for i, s in enumerate(spec.get("slides", [])):
        figs = s.get("figures")
        if not figs:
            continue
        canvas = Canvas(_StubDeck(), f"dry_{i}", template)
        # The audit measures text width, and the furniture Canvas prints itself
        # wraps differently per language. Measuring Japanese for a deck that
        # will generate in English would report overflow that never happens.
        canvas.lang = s.get("lang") or spec.get("lang") or canvas.lang
        canvas.text_margin = _text_margin(spec, s)
        canvas.text_fit = _text_fit(spec, s)
        canvas.min_font_size = _min_font_size(spec, s)
        try:
            draw_figures(canvas, figs, skip_network=True,
                         group=_group_mode(spec, s))
        except Exception as e:  # an argument mismatch may only surface here
            out.append(t("slides[{i}]: failed to draw figures: {etype}: {e}",
                         i=i, etype=type(e).__name__, e=e))
            continue
        for msg in canvas.audit_all():
            out.append(f"slides[{i}]: {msg}")
        if notes is not None:
            notes += [f"slides[{i}]: {msg}" for msg in canvas.fit_notes]
    out += audit_body_fit(template, spec, notes)
    out += audit_image_slots(template, spec)
    return out


# ---------- Spec validation and assembly ----------

def footer_band(template: dict) -> tuple[float, float, float] | None:
    """Return the top y and x range of the band (logo, copyright notice) the master places at the bottom edge.

    Placing a figure under the assumption that the whole page down to the
    bottom edge is usable makes it overlap the logo or footer. A check that
    only looks at the page size can't catch this, so this derives a "nothing
    can be placed below here" line from the decoration's actual coordinates.
    Returns None if there's nothing to derive it from.
    """
    page_h = template.get("pageSize", {}).get("heightInches", 5.625)
    decs = [d for d in template.get("masterDecorations", []) or []
            if isinstance(d.get("y"), (int, float)) and d["y"] > page_h * 0.75]
    if not decs:
        return None
    top = min(d["y"] for d in decs)
    x0 = min(d.get("x", 0.0) for d in decs)
    x1 = max(d.get("x", 0.0) + d.get("w", 0.0) for d in decs)
    return top, x0, x1


IMAGE_FIGURES = ("image", "aiImage")
_SLOT_KEYS = ("x", "y", "w", "h")


def layout_image_slots(template: dict, layout_key: str) -> list[dict]:
    """Return the image insertion slots a slide layout has."""
    resolved = template.get("roles", {}).get(layout_key, layout_key)
    return (template.get("layouts", {}).get(resolved, {}) or {}).get("imageSlots") or []


def resolve_image_slots(template: dict, spec: dict) -> list[str]:
    """Fill in image / aiImage coordinates from the layout's insertion slots.

    If the template has already decided "put the picture here", that's the
    correct place to put it. In the spec, x/y/w/h are omitted (when there are
    multiple slots, "slot": N picks one). Rewrites the spec in place and
    returns a list of explanatory notes about what was filled in.

    fit defaults to "cover" when omitted. Since a slot's aspect ratio is part
    of the design, filling the slot is the more natural default than
    letterboxing with padding (contain).
    """
    notes: list[str] = []
    for i, s in enumerate(spec.get("slides", [])):
        figs = s.get("figures")
        if not figs or not isinstance(figs, list):
            continue
        slots = layout_image_slots(template, s.get("layout", ""))
        auto = 0
        for j, fig in enumerate(figs):
            if not isinstance(fig, dict) or fig.get("type") not in IMAGE_FIGURES:
                continue
            explicit = fig.pop("slot", None)
            has_box = all(k in fig for k in _SLOT_KEYS)
            if has_box and explicit is None:
                continue
            if not slots:
                if explicit is not None or not has_box:
                    notes.append(t(
                        "slides[{i}].figures[{j}]: layout '{layout}' has no image "
                        "slot, so x/y/w/h are required",
                        i=i, j=j, layout=s.get("layout")))
                continue
            n = explicit if isinstance(explicit, int) else auto
            if n >= len(slots):
                notes.append(t(
                    "slides[{i}].figures[{j}]: slot {n} does not exist "
                    "(layout '{layout}' has {total})",
                    i=i, j=j, n=n, layout=s.get("layout"), total=len(slots)))
                continue
            slot = slots[n]
            fig.update({k: slot[k] for k in _SLOT_KEYS})
            fig.setdefault("fit", "cover")
            auto = n + 1
            notes.append(t(
                "slides[{i}].figures[{j}]: placed in the image slot of layout "
                "'{layout}' (x={x} y={y} w={w} h={h})",
                i=i, j=j, layout=s.get("layout"),
                x=slot["x"], y=slot["y"], w=slot["w"], h=slot["h"]))
    return notes


def audit_body_fit(template: dict, spec: dict,
                   notes: list[str] | None = None) -> list[str]:
    """Estimate whether each slot's text fits its slot, without calling the API.

    Covers the title, subtitle and body slots, and runs the same plan as
    add_slide (fit_slot): text the fitting brings into its slot is recorded in
    `notes` rather than reported; only text that still overflows at the
    smallest allowed size (or with textFit "none") is a finding. The API
    doesn't error on overflow — Slides draws it outside the slot — so it would
    otherwise go unnoticed until the thumbnail is viewed.

    A role-tagged line (e.g. a heading) adds its spaceAbove. When paragraph
    spacing is left at the template default, the actual margin is unknown, so
    this **estimates on the low side** (biased toward missing a real overflow
    rather than raising a false positive).
    """
    out = []
    defaults = spec.get("defaults", {})
    layouts = template.get("layouts", {})
    roles = template.get("roles", {})
    role_styles = {**DEFAULT_BODY_ROLES, **(template.get("bodyRoles") or {})}

    for i, s in enumerate(spec.get("slides", [])):
        layout = layouts.get(roles.get(s.get("layout"), s.get("layout")))
        if not layout:
            continue
        declared = declared_slots(layout)
        title_slot = ("CENTERED_TITLE" if ("CENTERED_TITLE" in declared
                                           and "TITLE" not in declared)
                      else "TITLE")
        bodies = s.get("bodies")
        if bodies is None and s.get("body") is not None:
            bodies = [s["body"]]
        body_slots = [p for p in declared if p.split("#")[0] == "BODY"]
        body_kw = {
            "line_spacing": s.get("bodyLineSpacing", defaults.get("bodyLineSpacing")),
            "space_above": s.get("bodySpaceAbove", defaults.get("bodySpaceAbove")),
            "space_below": s.get("bodySpaceBelow", defaults.get("bodySpaceBelow")),
        }
        entries = [(title_slot, s.get("title"),
                    s.get("titleFontSize", defaults.get("titleFontSize")), False),
                   ("SUBTITLE", s.get("subtitle"), None, False)]
        entries += [(name, value,
                     s.get("bodyFontSize", defaults.get("bodyFontSize")), True)
                    for name, value in zip(body_slots, bodies or [])]
        where = f"slides[{i}] ({s.get('title') or s.get('layout')})"
        for name, value, explicit, is_body in entries:
            if value is None or name not in declared:
                continue
            planned = fit_slot(
                layout, name, value, explicit_size=explicit, body=is_body,
                mode=_text_fit(spec, s), min_size=_min_font_size(spec, s),
                roles=role_styles, **(body_kw if is_body else {}))
            if planned is None:
                continue
            fit, base = planned
            if not fit.fits:
                out.append(t(
                    "{where}: {slot} does not fit its slot ({size:g}pt). Reduce "
                    "the text, lower the font size, or split the slide",
                    where=where, slot=name, size=fit.size))
                continue
            detail = describe_fit(base, TEXT_INSET_X, fit)
            if detail and notes is not None:
                notes.append(f"{where}: " + t(
                    "{slot}: text fitted to the slot ({detail})",
                    slot=name, detail=detail))
    return out


def audit_image_slots(template: dict, spec: dict) -> list[str]:
    """Check whether an image is placed off-slot even though the template has a slot for it.

    Catches the mistake of placing an image elsewhere without ever noticing the slot exists.
    """
    out = []
    for i, s in enumerate(spec.get("slides", [])):
        slots = layout_image_slots(template, s.get("layout", ""))
        if not slots:
            continue
        for j, fig in enumerate(s.get("figures") or []):
            if not isinstance(fig, dict) or fig.get("type") not in IMAGE_FIGURES:
                continue
            if not all(k in fig for k in _SLOT_KEYS):
                continue
            if any(_boxes_overlap(fig, slot) >= 0.5 for slot in slots):
                continue
            near = slots[0]
            out.append(t(
                "slides[{i}].figures[{j}]: the layout has an image slot at "
                "(x={x} y={y} w={w} h={h}) but this image is placed elsewhere "
                "(x={fx} y={fy} w={fw} h={fh}). Omit x/y/w/h to use the slot",
                i=i, j=j, x=near["x"], y=near["y"], w=near["w"], h=near["h"],
                fx=fig["x"], fy=fig["y"], fw=fig["w"], fh=fig["h"]))
    return out


def _boxes_overlap(a: dict, b: dict) -> float:
    ix = max(0.0, min(a["x"] + a["w"], b["x"] + b["w"]) - max(a["x"], b["x"]))
    iy = max(0.0, min(a["y"] + a["h"], b["y"] + b["h"]) - max(a["y"], b["y"]))
    small = min(a["w"] * a["h"], b["w"] * b["h"])
    return (ix * iy) / small if small > 0 else 0.0


def expand_slide_templates(spec: dict) -> tuple[list[str], list[str]]:
    """Expand slides written as {"$template": <id>, "data": {...}} in place.

    A slide that names a registered slide template (slide-templates/) is
    replaced by the slide that template renders, so a spec can name a template
    instead of spelling out its figures. Sibling keys other than $template /
    data / density are merged over the rendered slide, which lets a spec attach
    "notes" or retarget "layout" without editing the template.

    Density and language each come from the slide, then the spec, then the
    template's own default — so one deck can stay in one language without
    repeating it on every slide. Returns (notes, problems). This runs before validate_spec, which
    requires every slide to carry a layout — an unexpanded $template slide has
    none, so expansion has to happen first for dry-run, --into and generation
    alike.
    """
    slides = spec.get("slides")
    if not isinstance(slides, list):
        return [], []
    # Imported lazily so specs that never name a template don't pay for the
    # registry, and build_deck stays importable without slide-templates/.
    from slide_templates import load_template as _load_slide_template
    from slide_templates import render_template as _render_slide_template

    notes: list[str] = []
    problems: list[str] = []
    for i, s in enumerate(slides):
        if not isinstance(s, dict) or "$template" not in s:
            continue
        where = f"slides[{i}]"
        template_id = s.get("$template")
        if not isinstance(template_id, str) or not template_id:
            problems.append(t("{where}: '$template' must be a template id",
                              where=where))
            continue
        data = s.get("data", {})
        if not isinstance(data, dict):
            problems.append(t("{where}: 'data' must be an object", where=where))
            continue
        density = s.get("density", spec.get("density"))
        lang = s.get("lang", spec.get("lang"))
        try:
            slide_template, _ = _load_slide_template(template_id)
            rendered = _render_slide_template(slide_template, data,
                                              density=density, lang=lang)
        except (ValueError, KeyError, OSError) as exc:
            problems.append(f"{where} ($template {template_id}): {exc}")
            continue
        rendered.update({k: v for k, v in s.items()
                         if k not in ("$template", "data", "density", "lang")})
        if lang:
            # Density is fully resolved into the rendered slide here, but the
            # language is not: the figures this expanded to are drawn later by
            # Canvas._label(), which reads the slide's own lang. Dropping it
            # left an English slide printing "出典:" and Japanese weekday heads,
            # because the canvas fell back to the deck-wide language.
            rendered["lang"] = lang
        slides[i] = rendered
        notes.append(t("{where}: expanded slide template '{id}'",
                       where=where, id=template_id))
    return notes, problems


_WHERE_RE = re.compile(r"^(slides\[(\d+)\])(.*)$", re.S)


def collapse_problems(problems: list[str]) -> list[str]:
    """Merge problems that differ only by their ``slides[N]`` prefix.

    One wrong layout key in a 46-slide deck printed the same sentence 45
    times, each repeating the full roles/keys lists (~250 B a line, ~2.7k
    tokens of agent context) to convey a single fact. Report the fact once
    and list the slides it applies to.
    """
    order: list[str] = []
    groups: dict[str, list[str]] = {}
    for msg in problems:
        m = _WHERE_RE.match(msg)
        body = m.group(3) if m else msg
        if body not in groups:
            order.append(body)
            groups[body] = []
        if m:
            groups[body].append(m.group(2))
    out: list[str] = []
    for body in order:
        idx = groups[body]
        if not idx:
            out.append(body)
        elif len(idx) == 1:
            out.append(f"slides[{idx[0]}]{body}")
        else:
            out.append(t("slides[{list}] ({n} slides){body}",
                         list=",".join(idx), n=len(idx), body=body))
    return out


def validate_spec(template: dict, spec: dict) -> list[str]:
    """Check the deck spec against the template and return a list of problems (empty means OK)."""
    problems = []
    slides = spec.get("slides")
    if not isinstance(slides, list) or not slides:
        return [t("spec has no slides array")]

    layouts = template["layouts"]
    roles = template.get("roles", {})
    for i, s in enumerate(slides):
        where = f"slides[{i}]"
        key = s.get("layout")
        if not key:
            problems.append(t("{where}: missing 'layout'", where=where))
            continue
        resolved = roles.get(key, key)
        layout = layouts.get(resolved)
        if not layout:
            problems.append(
                t("{where}: cannot resolve layout '{key}' "
                  "(roles: {roles} / keys: {keys})", where=where, key=key,
                  roles=sorted(roles), keys=sorted(layouts))
            )
            continue
        declared = declared_slots(layout)
        title_ph = "CENTERED_TITLE" if ("CENTERED_TITLE" in declared
                                        and "TITLE" not in declared) else "TITLE"
        for field, ph in (("title", title_ph), ("subtitle", "SUBTITLE")):
            if s.get(field) is not None and ph not in declared:
                problems.append(
                    t("{where}: layout '{key}' ({name}) has no {ph} but "
                      "'{field}' is specified (declares: {declared})",
                      where=where, key=key, name=layout["displayName"], ph=ph,
                      field=field, declared=declared)
                )
        if s.get("body") is not None and s.get("bodies") is not None:
            problems.append(t("{where}: 'body' and 'bodies' cannot be "
                              "specified together", where=where))
            continue
        bodies = s.get("bodies")
        if bodies is None and s.get("body") is not None:
            bodies = [s["body"]]
        if bodies is not None:
            if not isinstance(bodies, list):
                problems.append(t("{where}: 'bodies' must be an array",
                                  where=where))
                continue
            for col in bodies:
                for n, line in enumerate(col if isinstance(col, list) else [col], 1):
                    if isinstance(line, str):
                        continue
                    if isinstance(line, dict) and "text" in line:
                        continue
                    problems.append(t(
                        '{where}: body line {n} must be a string or '
                        '{{"text": …, "role": …}}', where=where, n=n))
            slots = [p for p in declared if p.split("#")[0] == "BODY"]
            if not slots:
                problems.append(
                    t("{where}: layout '{key}' ({name}) has no BODY but body "
                      "text is specified (declares: {declared})", where=where,
                      key=key, name=layout["displayName"], declared=declared)
                )
            elif len(bodies) > len(slots):
                problems.append(
                    t("{where}: layout '{key}' ({name}) has {slots} BODY "
                      "slots but {given} were given (declares: {declared})",
                      where=where, key=key, name=layout["displayName"],
                      slots=len(slots), given=len(bodies), declared=declared)
                )
    return problems


def build_from_spec(
    deck: TemplateDeck,
    spec: dict,
    selected_indices: list[int] | None = None,
) -> list[str]:
    """Stack slides from the spec. Returns audit findings if any figures were drawn."""
    defaults = spec.get("defaults", {})
    warnings: list[str] = []
    slides = spec.get("slides", [])
    indices = range(len(slides)) if selected_indices is None else selected_indices
    for i in indices:
        s = slides[i]
        ref = deck.add_slide(
            s["layout"],
            title=s.get("title"),
            subtitle=s.get("subtitle"),
            body=s.get("body"),
            bodies=s.get("bodies"),
            notes=s.get("notes"),
            title_font_size=s.get("titleFontSize", defaults.get("titleFontSize")),
            body_font_size=s.get("bodyFontSize", defaults.get("bodyFontSize")),
            body_line_spacing=s.get("bodyLineSpacing", defaults.get("bodyLineSpacing")),
            body_space_above=s.get("bodySpaceAbove", defaults.get("bodySpaceAbove")),
            body_space_below=s.get("bodySpaceBelow", defaults.get("bodySpaceBelow")),
            index=i if selected_indices is not None else None,
            text_fit=_text_fit(spec, s),
            min_font_size=_min_font_size(spec, s),
        )
        where = f"slides[{i}] ({s.get('title') or s['layout']})"
        for msg in ref.get("fitNotes") or []:
            print(f"  fit: {where}: {msg}")
        warnings += [f"{where}: {msg}" for msg in ref.get("fitWarnings") or []]
        figs = s.get("figures")
        if not figs:
            if selected_indices is not None:
                deck.requests.append({"deleteObject": {
                    "objectId": deck.partial_targets[i]
                }})
            continue
        from diagrams import Canvas  # only loaded for a spec that uses figures
        canvas = Canvas(deck, ref["slideId"], deck.template)
        # Per slide, like the audit does: the canvas inherits deck.lang, which
        # only carries the spec-level language, so without this a slide asking
        # for another language still draws its own furniture — weekday heads,
        # "Source:" — in the deck's language.
        canvas.lang = s.get("lang") or spec.get("lang") or canvas.lang
        canvas.text_margin = _text_margin(spec, s)
        canvas.text_fit = _text_fit(spec, s)
        canvas.min_font_size = _min_font_size(spec, s)
        draw_figures(canvas, figs, group=_group_mode(spec, s))
        for msg in canvas.fit_notes:
            print(f"  fit: {where}: {msg}")
        for msg in canvas.audit_all():
            warnings.append(f"slides[{i}] ({s.get('title') or s['layout']}): {msg}")
        if selected_indices is not None:
            deck.requests.append({"deleteObject": {
                "objectId": deck.partial_targets[i]
            }})
    return warnings


def deliver_local(deck: "TemplateDeck", title: str | None) -> str | None:
    """Export the freshly built deck to `.pptx` in the local output folder.

    The engine always draws through the Slides API, so `output: local` is
    about the *deliverable*, not the build: the deck is exported to
    PowerPoint under `settings.local_output_dir()` and the Slides original is
    deliberately left in place (this toolkit never deletes for you).

    A failed export is reported, not raised — the deck itself was generated
    successfully by that point, and losing that fact to an export error would
    be a worse outcome than an export the user can retry with
    `scripts/export_pptx.py`.
    """
    import export_pptx  # local: pulls in the Drive export helpers only when used

    name = title or (deck.pending_title or "deck")
    out_dir = settings.local_output_dir()
    path = os.path.join(out_dir, f"{export_pptx.safe_name(name)}.pptx")
    print(t("  output: local — exporting to PowerPoint..."))
    try:
        export_pptx.export_pptx(deck.drive, _auth.get_credentials(),
                                deck.presentation_id, path)
    except (Exception, SystemExit) as exc:  # export_pptx signals errors with SystemExit
        print(t("  warn: the PowerPoint export failed ({err}); the deck is "
                "still available at {url}", err=exc, url=deck.url),
              file=sys.stderr)
        return None
    print(t("  PPTX: {path} ({size:.1f} MB)", path=path,
            size=os.path.getsize(path) / (1 << 20)))
    print(t("  the deck itself stays in Google Slides (nothing is deleted): "
            "{url}", url=deck.url))
    return path


def main() -> int:
    p = argparse.ArgumentParser(
        description=t("generate a presentation from a template"))
    p.add_argument("--template", required=True,
                   help=t("path to template.json"))
    p.add_argument("--spec", required=True,
                   help=t("path to the deck-spec JSON"))
    p.add_argument("--title",
                   help=t("presentation title (defaults to spec.title)"))
    p.add_argument("--folder", help=t("destination Drive folder URL or ID"))
    p.add_argument("--into", metavar="DECK",
                   help=t("replace the contents of this existing deck "
                          "(URL or ID) instead of creating a new one; the "
                          "deck URL stays the same"))
    p.add_argument("--update-slides", metavar="PAGES",
                   help="with --into, replace only these one-based pages "
                        "from the complete spec (for example: 3,7)")
    p.add_argument("--dry-run", action="store_true",
                   help=t("validate the spec only, without calling the API"))
    p.add_argument("--no-page-numbers", action="store_true",
                   help=t("do not draw page numbers"))
    p.add_argument("--keep-existing", action="store_true",
                   help=t("keep the slides bundled with the template"))
    p.add_argument("--strict", action="store_true",
                   help=t("fail if the figure audit (overlaps / text "
                          "overflow) reports anything"))
    p.add_argument("--verbose", action="store_true",
                   help=t("list every slide and every fitted text instead of "
                          "counting them"))
    p.add_argument("--output", metavar="google|local",
                   help=t("where the deliverable goes: google (Drive / Slides) "
                          "or local (folder / PowerPoint); defaults to "
                          "config/settings.json"))
    args = p.parse_args()

    try:
        output_target = settings.output_target(args.output)
    except settings.SettingsError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    template = load_template(args.template)
    with open(args.spec, encoding="utf-8") as f:
        spec = json.load(f)

    # Slides that name a slide template become real slides before anything
    # counts, validates or draws them.
    tpl_notes, tpl_problems = expand_slide_templates(spec)
    for msg in tpl_notes:
        print(f"  {msg}")
    if tpl_problems:
        print(t("The spec has problems:"), file=sys.stderr)
        for msg in tpl_problems:
            print(f"  - {msg}", file=sys.stderr)
        return 1

    selected_indices: list[int] | None = None
    if args.update_slides is not None:
        if not args.into:
            print("ERROR: --update-slides requires --into", file=sys.stderr)
            return 1
        if args.keep_existing:
            print("ERROR: --update-slides cannot be combined with --keep-existing",
                  file=sys.stderr)
            return 1
        if args.title:
            print("ERROR: --title cannot be combined with --update-slides; "
                  "partial updates preserve the Drive title", file=sys.stderr)
            return 1
        if args.folder:
            print("ERROR: --folder cannot be combined with --update-slides; "
                  "partial updates preserve the Drive folder", file=sys.stderr)
            return 1
        try:
            selected_indices = parse_slide_selection(
                args.update_slides, len(spec.get("slides", []))
            )
        except ValueError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 1

    # Resolve the layout's image slots to coordinates before validation
    # (everything downstream — validation, audit, generation — looks at the resolved coordinates)
    slot_notes = resolve_image_slots(template, spec)
    if args.verbose:
        for msg in slot_notes:
            print(f"  {msg}")

    problems = validate_spec(template, spec)
    problems += validate_figures(spec, template.get("pageSize", {}), template)
    if problems:
        print(t("The spec has problems:"), file=sys.stderr)
        for msg in collapse_problems(problems):
            print(f"  - {msg}", file=sys.stderr)
        return 1

    title = args.title or spec.get("title")
    if not title and selected_indices is None:
        print(t("No title (specify --title or spec.title)"), file=sys.stderr)
        return 1

    if args.dry_run:
        print(t("OK: the {n}-slide spec is consistent with the template",
                n=len(spec["slides"])))
        if args.verbose:
            for i, s in enumerate(spec["slides"], 1):
                resolved = template.get("roles", {}).get(s["layout"],
                                                        s["layout"])
                n_fig = len(s.get("figures") or [])
                extra = t("  + {n} figures", n=n_fig) if n_fig else ""
                print(f"  {i:2d}. {s['layout']:24s} -> "
                      f"{template['layouts'][resolved]['displayName']}{extra}")
        fit_notes: list[str] = []
        findings = audit_figures(template, spec, fit_notes)
        if fit_notes:
            if args.verbose:
                print(t("Text fitted to its box ({n}):", n=len(fit_notes)))
                for msg in fit_notes:
                    print(f"  - {msg}")
            else:
                print(t("Text fitted to its box ({n}); --verbose to list them",
                        n=len(fit_notes)))
        if findings:
            print("\n" + t("Figure audit found {n} findings (images excluded; "
                           "they need the real file):", n=len(findings)),
                  file=sys.stderr)
            for msg in findings:
                print(f"  - {msg}", file=sys.stderr)
            return 1 if args.strict else 0
        if any(s.get("figures") for s in spec["slides"]):
            print(t("figure audit (connectors / overlaps / text overflow): "
                    "no problems"))
        if output_target == settings.LOCAL:
            print(t("  output: local — after generation the deck is exported "
                    "to PowerPoint under {dir}",
                    dir=settings.local_output_dir()))
        if selected_indices is not None:
            pages = ", ".join(str(index + 1) for index in selected_indices)
            print(f"partial update plan: replace pages {pages}; all other pages stay unchanged")
            print("live write will also verify page count, slide IDs, and template layouts")
        return 0

    if args.into:
        if args.keep_existing:
            print(t("--keep-existing cannot be combined with --into "
                    "(--into replaces every page)"), file=sys.stderr)
            return 1
        if args.folder:
            print(t("  note: --folder is ignored with --into "
                    "(the deck stays in its current folder)"))
        try:
            if selected_indices is not None:
                deck = TemplateDeck.open_partial(
                    template, args.into,
                    selected_indices=selected_indices,
                    expected_slide_count=len(spec["slides"]),
                    layouts=[spec["slides"][i]["layout"] for i in selected_indices],
                )
            else:
                deck = TemplateDeck.open(
                    template, args.into, title=title,
                    layouts=[s["layout"] for s in spec["slides"]],
                )
        except ValueError as exc:
            # A wrong replacement target is reliably stopped right here.
            # No traceback, just a clear message about what happened
            print(f"ERROR: {exc}", file=sys.stderr)
            return 1
    else:
        deck = TemplateDeck.create(
            template, title=title, folder=args.folder,
            keep_existing=args.keep_existing,
        )
    # The drawing layer prints furniture of its own around the caller's content
    # ("Source:", weekday heads, the so-what label). Canvas reads the language
    # off the deck, so one spec settles it once for templates and drawing alike.
    deck.lang = spec.get("lang")
    try:
        warnings = build_from_spec(deck, spec, selected_indices=selected_indices)
        if not args.no_page_numbers:
            n = (deck.add_page_numbers_at(selected_indices)
                 if selected_indices is not None else deck.add_page_numbers())
            print(f"  page numbers: {n} slides")
        url = deck.commit()
    except Exception:
        # Don't silently orphan a deck that files.copy already created. It's
        # not auto-deleted (a lesson learned from a past deletion incident:
        # the policy is not to add more destructive operations on our side).
        # --into replaces an existing deck, so no guidance is needed there
        if not args.into:
            print(t("Generation failed; a partially built deck remains: "
                    "{url} — delete it manually if it is not needed",
                    url=deck.url), file=sys.stderr)
        raise
    if selected_indices is not None:
        pages = ", ".join(str(index + 1) for index in selected_indices)
        print(f"Done! pages {pages} replaced; all other pages were left unchanged.")
        print("Note: replaced pages receive new slide IDs; comments and links to old IDs are not preserved.")
    else:
        print(f"Done! {len(deck.slide_ids)} slides created.")
    if warnings:
        print("\n" + t("Figure audit found {n} findings:", n=len(warnings)),
              file=sys.stderr)
        for msg in warnings:
            print(f"  - {msg}", file=sys.stderr)
    print(f"Open: {url}")
    if output_target == settings.LOCAL:
        deliver_local(deck, title)
    return 1 if (warnings and args.strict) else 0


if __name__ == "__main__":
    sys.exit(main())
