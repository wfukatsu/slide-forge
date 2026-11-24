#!/usr/bin/env python3
"""Visual-density audit for a deck spec: does the deck show, or only tell?

A deck can pass every geometry check and still be a document in slide form:
a lead-in line, a table and an implication box on page after page. Whether a
page *should* be a picture is a judgement no script makes, so this audit only
warns, and never changes the exit code. It reports what can be counted from
the spec (``references/slide-patterns.md`` "Show before you tell"):

- a page carrying more words than its density allows (CHAR_LIMIT, measured
  with ``_text.em``: a CJK character is 1, an ASCII character 0.5);
- RUN_LIMIT or more content pages in a row with no picture at all;
- a two-column "item / description" table — parallel items that read better
  as pictogram cards (``cards`` + ``icons``), ``icon_grid`` or ``icon_row``;
- implication boxes (``so_what``) on more than KICKER_SHARE of content pages.

Speaker notes are not counted: they are where the detail is meant to go.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _i18n import t, register  # noqa: E402
from _text import em  # noqa: E402
from reading_level import _figure_strings, _lines, _plain  # noqa: E402

# Visible words per content page, by spec "density". A deck without one is
# held to the middle: most decks without a stated density are talks.
CHAR_LIMIT = {"presentation": 150, "print": 320, None: 220}
RUN_LIMIT = 3
KICKER_SHARE = 0.2
DESC_TABLE_MIN_ROWS = 3
DESC_CELL_EM = 12

# Figures that are words in a box, not a picture. A `cards` figure with
# pictograms (`icons`) counts as a picture.
TEXT_FIGURES = frozenset({
    "lead_in", "so_what", "source_note", "governing_message", "cards",
    "table", "exec_summary", "ghost", "band", "exhibit_frame", "storyline",
    "label", "text", "banner", "kv_rows", "checklist",
})
# Layout names that frame the deck rather than carry content
_STRUCTURAL = ("COVER", "SECTION", "CLOSING", "TITLE_SLIDE", "AGENDA")

register({
    "unset": "density 未指定",
    "{where}: {width:g} characters of text on one page (limit {limit} for "
    "{density}); move detail to the notes, or let a figure carry it":
        "{where}: 1 ページに全角 {width:g} 文字分の文字があります（{density} の"
        "目安は {limit}）。詳細はノートへ移すか、図に語らせてください",
    "{where}: {n} content pages in a row with no picture (pages {first}–"
    "{last}); turn at least one into a figure — flow, funnel, chart, "
    "pictogram cards":
        "{where}: 図のないページが {n} 枚続いています（{first}〜{last} ページ）。"
        "少なくとも 1 枚はフロー・ファネル・グラフ・アイコン付きカードなどの"
        "図にしてください",
    "{where}: a two-column 'item / description' table with {n} rows; "
    "parallel items read better as cards with icons, icon_grid or icon_row":
        "{where}: 「項目・説明」の 2 列の表が {n} 行あります。並列の項目は "
        "icons 付きの cards・icon_grid・icon_row のほうが伝わります",
    "implication boxes (so_what) on {n} of {total} content pages (guideline "
    "≤ {share:.0%}); keep them for implications the figure does not show":
        "結論の囲み（so_what）が本文 {total} ページ中 {n} ページにあります"
        "（目安は {share:.0%} 以下）。図から読み取れない示唆だけに使ってください",
})


def _density_name(density) -> str:
    return density if density in ("presentation", "print") else t("unset")


def is_structural(slide: dict) -> bool:
    layout = str(slide.get("layout", "")).upper()
    return any(k in layout for k in _STRUCTURAL)


def _kind(fig: dict) -> str:
    return str(fig.get("type") or "")


def is_picture(fig: dict) -> bool:
    kind = _kind(fig)
    if kind == "cards":
        return any(fig.get("icons") or [])
    return bool(kind) and kind not in TEXT_FIGURES


def page_width(slide: dict) -> float:
    """Prose on a page (title, body, text figures), in full-width character
    equivalents."""
    total = 0.0
    for key in ("title", "subtitle"):
        if isinstance(slide.get(key), str):
            total += em(_plain(slide[key]).replace("\n", ""))
    bodies = slide.get("bodies")
    if bodies is None and slide.get("body") is not None:
        bodies = [slide["body"]]
    for body in bodies or []:
        total += sum(em(_plain(ln).strip()) for ln in _lines(body))
    # Labels inside a picture (axis ticks, calendar days, code) are part of
    # the picture, not prose to read
    for fig in slide.get("figures") or []:
        if isinstance(fig, dict) and _kind(fig) in TEXT_FIGURES:
            total += sum(em(_plain(s).replace("\n", ""))
                         for s in _figure_strings(fig))
    return total


def _desc_table_rows(fig: dict) -> int:
    """Rows of a two-column table whose second column is prose, else 0."""
    if _kind(fig) != "table":
        return 0
    rows = [r for r in (fig.get("rows") or []) if isinstance(r, (list, tuple))]
    headers = fig.get("headers") or []
    if len(rows) < DESC_TABLE_MIN_ROWS:
        return 0
    if any(len(r) != 2 for r in rows) or (headers and len(headers) != 2):
        return 0
    desc = [em(_plain(str(r[1]))) for r in rows]
    return len(rows) if sum(desc) / len(desc) >= DESC_CELL_EM else 0


def audit(spec: dict) -> list[str]:
    """Advisory findings; an empty list when the deck shows as well as tells."""
    out: list[str] = []
    density = spec.get("density")
    limit = CHAR_LIMIT.get(density, CHAR_LIMIT[None])
    content = 0
    kickers = 0
    run: list[int] = []

    def close_run() -> None:
        if len(run) >= RUN_LIMIT:
            out.append(t(
                "{where}: {n} content pages in a row with no picture (pages "
                "{first}–{last}); turn at least one into a figure — flow, "
                "funnel, chart, pictogram cards",
                where=f"slides[{run[0] - 1}]", n=len(run), first=run[0],
                last=run[-1]))
        run.clear()

    for i, s in enumerate(spec.get("slides", [])):
        if not isinstance(s, dict) or is_structural(s) or s.get("$template"):
            close_run()
            continue
        where = f"slides[{i}] ({s.get('title') or s.get('layout')})"
        figs = [f for f in (s.get("figures") or []) if isinstance(f, dict)]
        if not figs and not s.get("body") and not s.get("bodies"):
            close_run()
            continue
        content += 1
        if any(_kind(f) == "so_what" for f in figs):
            kickers += 1
        width = page_width(s)
        if width > limit:
            out.append(t(
                "{where}: {width:g} characters of text on one page (limit "
                "{limit} for {density}); move detail to the notes, or let a "
                "figure carry it", where=where, width=round(width),
                limit=limit, density=_density_name(density)))
        for f in figs:
            n = _desc_table_rows(f)
            if n:
                out.append(t(
                    "{where}: a two-column 'item / description' table with "
                    "{n} rows; parallel items read better as cards with "
                    "icons, icon_grid or icon_row", where=where, n=n))
        if any(is_picture(f) for f in figs):
            close_run()
        else:
            run.append(i + 1)
    close_run()
    if content >= 5 and kickers / content > KICKER_SHARE:
        out.append(t(
            "implication boxes (so_what) on {n} of {total} content pages "
            "(guideline ≤ {share:.0%}); keep them for implications the "
            "figure does not show", n=kickers, total=content,
            share=KICKER_SHARE))
    return out
