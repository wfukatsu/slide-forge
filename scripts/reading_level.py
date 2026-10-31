#!/usr/bin/env python3
"""Reading-level audit for a deck spec: the ELI5 ("explain like I'm 5") mode.

A spec that sets ``"readingLevel": "eli5"`` asks for a deck a newcomer can
follow without a glossary. Most of that is writing (analogies, one idea per
slide, a concrete example — ``references/eli5.md``), which no script can
judge. What can be checked from the spec alone is checked here, so
``build_deck.py --dry-run --strict`` stops a deck that drifted back into
expert prose:

- an acronym (two or more capitals: API, OCC, 2PC) whose first use in the
  deck is not explained in brackets next to it — ``API（ソフト同士の窓口）``
  or ``ソフト同士の窓口（API）``. Terms the audience already knows go in the
  spec's ``"plainTerms"``;
- a title longer than TITLE_MAX_EM full-width equivalents;
- a sentence longer than SENTENCE_MAX_EM;
- more than MAX_POINTS points in one body slot, or an indented sub-point.

Widths are measured with ``_text.em`` (a CJK character is 1, an ASCII
character 0.5), so the same limits work for Japanese and English decks.
Speaker notes are not audited: they are where the detail is meant to go.
"""
from __future__ import annotations

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _i18n import t, register  # noqa: E402
from _text import em  # noqa: E402

READING_LEVELS = ("standard", "eli5")
TITLE_MAX_EM = 30
SENTENCE_MAX_EM = 40
MAX_POINTS = 3

register({
    "'readingLevel' must be one of: {levels}":
        "'readingLevel' は {levels} のいずれかです",
    "'plainTerms' must be an array of strings":
        "'plainTerms' は文字列の配列である必要があります",
    "{where}: '{term}' is used without an explanation. On its first use, "
    "explain it in brackets — '{term}（…）' or '…（{term}）' — or add it to "
    "plainTerms if the audience already knows it":
        "{where}: '{term}' が説明なしで使われています。最初に出てくるところで"
        "「{term}（…）」か「…（{term}）」のように括弧で言い換えるか、聞き手が"
        "知っている言葉なら plainTerms に入れてください",
    "{where}: the title is {width:g} wide (ELI5 limit {limit}); say one idea "
    "in fewer words":
        "{where}: タイトルが全角 {width:g} 文字分あります（ELI5 の上限 "
        "{limit}）。言いたいことを 1 つに絞って短くしてください",
    "{where}: a sentence is {width:g} wide (ELI5 limit {limit}): "
    "'{text}'. Split it in two":
        "{where}: 1 文が全角 {width:g} 文字分あります（ELI5 の上限 {limit}）:"
        " '{text}'。2 つの文に分けてください",
    "{where}: {n} points in one body (ELI5 limit {limit}); keep the "
    "{limit} that matter and move the rest to another slide or the notes":
        "{where}: 本文の項目が {n} 個あります（ELI5 の上限 {limit}）。大事な "
        "{limit} つに絞り、残りは別のスライドかノートへ移してください",
    "{where}: an indented sub-point ('{text}'); ELI5 keeps one level — "
    "make it a point of its own or move it to the notes":
        "{where}: 字下げした下位項目があります（'{text}'）。ELI5 は 1 階層だけ"
        "にします。独立した項目にするかノートへ移してください",
})

# Two or more capitals, digits allowed (API, OCC, 2PC, HTAP). Lookarounds on
# ASCII rather than \b: a Japanese character is a word character, so \b finds
# no boundary in "APIを".
_ACRONYM = re.compile(
    r"(?<![A-Za-z0-9])(?=[A-Z0-9]*[A-Z][A-Z0-9]*[A-Z])[A-Z0-9]{2,}(?![A-Za-z0-9])")
_OPEN = "（("
_SENTENCE_END = re.compile(r"(?<=[。．！？!?])|(?<=\.)\s+")
# Figure keys whose strings are settings, not words a reader sees
_NOT_TEXT = re.compile(
    r"color|fill|stroke|icon|image|url|src|path|font|type|shape|align|anchor|"
    r"dash|id$|layout|lang|kind|style|link|direction|position|arrow|template",
    re.I)
_INLINE = re.compile(r"\*\*(.+?)\*\*|\[([^\]]+)\]\([^)]+\)", re.S)


def is_eli5(spec: dict) -> bool:
    return spec.get("readingLevel") == "eli5"


def check_spec(spec: dict) -> list[str]:
    """Reject a readingLevel or plainTerms the audit cannot use."""
    out = []
    level = spec.get("readingLevel")
    if level is not None and level not in READING_LEVELS:
        out.append(t("'readingLevel' must be one of: {levels}",
                     levels=", ".join(READING_LEVELS)))
    terms = spec.get("plainTerms")
    if terms is not None and (not isinstance(terms, list)
                              or not all(isinstance(x, str) for x in terms)):
        out.append(t("'plainTerms' must be an array of strings"))
    return out


def _plain(text: str) -> str:
    return _INLINE.sub(lambda m: m.group(1) or m.group(2), text)


def _lines(value) -> list[str]:
    """Body lines as raw strings (indentation kept), from any body form."""
    if value is None:
        return []
    items = value if isinstance(value, list) else [value]
    out = []
    for item in items:
        if isinstance(item, dict):
            if item.get("role") == "heading":
                continue
            item = item.get("text", "")
        if isinstance(item, str):
            out.extend(item.split("\n"))
    return out


def _figure_strings(node, key: str = ""):
    """Every string in a figure a reader would see."""
    if isinstance(node, str):
        if (not _NOT_TEXT.search(key) and node.strip()
                and not node.startswith(("#", "http", "theme:"))):
            yield node
    elif isinstance(node, dict):
        for k, v in node.items():
            yield from _figure_strings(v, k)
    elif isinstance(node, list):
        for v in node:
            yield from _figure_strings(v, key)


def _sentences(line: str) -> list[str]:
    return [s.strip() for s in _SENTENCE_END.split(line) if s and s.strip()]


def _explained(text: str, start: int, end: int) -> bool:
    """Whether the acronym at text[start:end] sits next to a bracket."""
    after = text[end:].lstrip(" ")[:1]
    before = text[:start].rstrip(" ")[-1:]
    # An empty neighbour is no bracket ("" is in every string)
    return bool(after and after in _OPEN) or bool(before and before in _OPEN)


def audit(spec: dict) -> list[str]:
    """Findings for an ELI5 deck; an empty list for any other deck."""
    if not is_eli5(spec):
        return []
    out: list[str] = []
    known = {x for x in (spec.get("plainTerms") or []) if isinstance(x, str)}
    seen: set[str] = set()

    def terms(where: str, text: str) -> None:
        for m in _ACRONYM.finditer(text):
            term = m.group(0)
            # 20XX, XX: a placeholder for a value still to come, not a term
            if (term in known or term in seen
                    or set(term) <= set("0123456789X")):
                continue
            seen.add(term)
            if not _explained(text, m.start(), m.end()):
                out.append(t(
                    "{where}: '{term}' is used without an explanation. On its "
                    "first use, explain it in brackets — '{term}（…）' or "
                    "'…（{term}）' — or add it to plainTerms if the audience "
                    "already knows it", where=where, term=term))

    for i, s in enumerate(spec.get("slides", [])):
        where = f"slides[{i}] ({s.get('title') or s.get('layout')})"
        title = s.get("title")
        if isinstance(title, str):
            plain = _plain(title)
            terms(where, plain)
            width = em(plain.replace("\n", ""))
            if width > TITLE_MAX_EM:
                out.append(t(
                    "{where}: the title is {width:g} wide (ELI5 limit "
                    "{limit}); say one idea in fewer words",
                    where=where, width=width, limit=TITLE_MAX_EM))
        if isinstance(s.get("subtitle"), str):
            terms(where, _plain(s["subtitle"]))
        bodies = s.get("bodies")
        if bodies is None and s.get("body") is not None:
            bodies = [s["body"]]
        for body in bodies or []:
            lines = [ln for ln in _lines(body) if ln.strip()]
            top = [ln for ln in lines if not ln[:1].isspace()]
            if len(top) > MAX_POINTS:
                out.append(t(
                    "{where}: {n} points in one body (ELI5 limit {limit}); "
                    "keep the {limit} that matter and move the rest to "
                    "another slide or the notes",
                    where=where, n=len(top), limit=MAX_POINTS))
            for ln in lines:
                plain = _plain(ln).strip()
                if ln[:1].isspace():
                    out.append(t(
                        "{where}: an indented sub-point ('{text}'); ELI5 keeps "
                        "one level — make it a point of its own or move it to "
                        "the notes", where=where, text=plain))
                terms(where, plain)
                for sentence in _sentences(plain):
                    width = em(sentence)
                    if width > SENTENCE_MAX_EM:
                        out.append(t(
                            "{where}: a sentence is {width:g} wide (ELI5 limit "
                            "{limit}): '{text}'. Split it in two",
                            where=where, width=width, limit=SENTENCE_MAX_EM,
                            text=sentence))
        for fig in s.get("figures") or []:
            for text in _figure_strings(fig):
                terms(where, _plain(text))
    return out
