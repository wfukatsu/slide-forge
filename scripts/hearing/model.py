#!/usr/bin/env python3
"""The hearing sheet as data — parse Markdown into it, render Markdown back out.

The JSON is the record. Markdown, Excel and Google Spreadsheet are renders of
it, and every one of them can be read back, because each question carries a
stable ID that survives a round trip.

Document shape::

    {
      "schemaVersion": 1,
      "meta": {"customer": ..., "productAddenda": [...], "renders": {...}},
      "headerComment": "<!-- ... -->",       # kept verbatim
      "title": "ヒアリングシート — <顧客名>",
      "blocks": [                            # flat and ordered, so a render is faithful
        {"kind": "heading", "level": 2, "num": "4.2", "title": "..."},
        {"kind": "prose",   "text": "..."},                  # anything not a question table
        {"kind": "meta",    "headers": [...], "align": [...], "rows": [[k, v], ...]},
        {"kind": "questions", "num": "4.2", "headers": [...], "align": [...],
         "questions": [{"id": "4.2-05", "cells": {"確認すること": "...", ...},
                        "followup": {...}, "confirmBack": {...}}]},
        {"kind": "derived", "which": "unconfirmed" | "confirm-back",
         "headers": [...], "align": [...]}                   # rows come from the questions
      ]
    }

`cells` holds the row exactly as the table column headers name it, so this
module never has to know what a particular sheet asks. The few headers it does
recognise are listed in `STD` and are what the rest of the toolchain reads.
"""
from __future__ import annotations

import re
from typing import Any

SCHEMA_VERSION = 1

# Column headers this toolchain understands. Everything else rides along in `cells`.
STD = {
    "ask": ("聞く", "当"),
    "text": ("確認すること", "確認する内容"),
    "answer": ("回答", "顧客の事実（出典）", "顧客の発言（出典）", "顧客の状況（本体 §4.2）"),
    "source": ("出典",),
    "confidence": ("確度",),
    "audience": ("相手", "区分"),
}
CONFIDENCE = ("確認済", "推定", "未確認")
ASK_ON, ASK_OFF = "✔", "☐"

ID_HEADER = "ID"
# The derived sections: their rows are generated from the questions, never hand-kept.
DERIVED_UNCONFIRMED = "unconfirmed"
DERIVED_CONFIRM_BACK = "confirm-back"
DERIVED_HEADERS = {
    DERIVED_UNCONFIRMED: ["ID", "未確認の内容", "確認相手", "手段", "期限", "担当"],
    DERIVED_CONFIRM_BACK: ["ID", "こちらの理解", "確定させる相手", "いつ"],
}
FOLLOWUP_KEYS = ["target", "means", "due", "owner"]
CONFIRM_BACK_KEYS = ["target", "when"]

_HEADING_RE = re.compile(r"^(#{2,3})\s+(.*)$")
_NUM_RE = re.compile(r"^([0-9]+(?:\.[0-9]+)?|[A-Z](?:-[0-9]+)?)[.．]?\s+(.*)$")
_ALIGN_RE = re.compile(r"^\s*\|[\s:|-]+\|\s*$")


class HearingError(Exception):
    pass


# ---------- small helpers ----------

def cell_escape(value: Any) -> str:
    return str(value or "").replace("|", "\\|").replace("\n", "<br>")


def cell_unescape(value: str) -> str:
    return value.replace("<br>", "\n").replace("\\|", "|")


def split_row(line: str) -> list[str]:
    """Split one Markdown table row, honouring escaped pipes."""
    body = line.strip()
    body = body[1:] if body.startswith("|") else body
    body = body[:-1] if body.endswith("|") else body
    out, cur, i = [], "", 0
    while i < len(body):
        ch = body[i]
        if ch == "\\" and i + 1 < len(body) and body[i + 1] == "|":
            cur += "\\|"
            i += 2
            continue
        if ch == "|":
            out.append(cur.strip())
            cur = ""
        else:
            cur += ch
        i += 1
    out.append(cur.strip())
    return [cell_unescape(c) for c in out]


def join_row(cells: list[Any]) -> str:
    return "| " + " | ".join(cell_escape(c) for c in cells) + " |"


def std_header(kind: str, headers: list[str]) -> str | None:
    """Return the actual column header used for a standard field, if present.

    Matched by prefix, because the sheets qualify their headers in place —
    "確認すること（本体 §4.2 のどの回答を見るか）" is still the question column.
    """
    for name in STD[kind]:
        for header in headers:
            if header == name or header.startswith(name):
                return header
    return None


def question_header(headers: list[str]) -> str | None:
    """The column carrying what is being asked.

    Usually 確認すること. In the product addenda the same role is played by a
    differently named column (カテゴリ, 前提条件, 顧客の要求 …), so fall back to
    the first column that is not one of the other standard ones.
    """
    named = std_header("text", headers)
    if named:
        return named
    taken = {std_header(kind, headers) for kind in STD if kind != "text"}
    for header in headers:
        if header not in taken and header not in ("#", ID_HEADER):
            return header
    return None


def get(question: dict, kind: str, headers: list[str]) -> str:
    header = question_header(headers) if kind == "text" else std_header(kind, headers)
    return question["cells"].get(header, "") if header else ""


def _derived_kind(headers: list[str]) -> str | None:
    for which, expected in DERIVED_HEADERS.items():
        if headers == expected:
            return which
    return None


def is_question_table(headers: list[str]) -> bool:
    """A question table is one whose rows carry a confidence.

    That column is what makes a row a fact we are tracking rather than prose,
    and it is the one thing every such table in these sheets has in common.
    """
    return bool(std_header("confidence", headers))


# ---------- parse ----------

def _table_at(lines: list[str], i: int) -> tuple[list[str], list[str], list[list[str]], int] | None:
    """If a Markdown table starts at line i, return (headers, align, rows, next index)."""
    if not lines[i].strip().startswith("|"):
        return None
    if i + 1 >= len(lines) or not _ALIGN_RE.match(lines[i + 1]):
        return None
    headers = split_row(lines[i])
    align = split_row(lines[i + 1])
    rows, j = [], i + 2
    while j < len(lines) and lines[j].strip().startswith("|"):
        rows.append(split_row(lines[j]))
        j += 1
    return headers, align, rows, j


def parse_markdown(text: str, *, section_prefix: str = "") -> dict:
    """Parse a hearing sheet (or a product addendum) into the document shape."""
    doc: dict = {"schemaVersion": SCHEMA_VERSION, "meta": {}, "headerComment": "",
                 "title": "", "blocks": []}

    if text.lstrip().startswith("<!--"):
        end = text.index("-->") + 3
        doc["headerComment"] = text[:end].strip()
        text = text[end:]

    lines = text.split("\n")
    prose: list[str] = []
    num = section_prefix or ""
    counters: dict[str, int] = {}

    def flush() -> None:
        while prose and not prose[-1].strip():
            prose.pop()
        if prose:
            doc["blocks"].append({"kind": "prose", "text": "\n".join(prose).strip("\n")})
        prose.clear()

    i = 0
    while i < len(lines):
        line = lines[i]

        if not doc["title"] and line.startswith("# "):
            doc["title"] = line[2:].strip()
            i += 1
            continue

        m = _HEADING_RE.match(line)
        if m:
            flush()
            level, body = len(m.group(1)), m.group(2).strip()
            nm = _NUM_RE.match(body)
            if nm:
                num = (section_prefix + nm.group(1)) if section_prefix else nm.group(1)
                title = nm.group(2)
            else:
                title = body
            doc["blocks"].append({"kind": "heading", "level": level,
                                  "num": num if nm else "", "title": title})
            i += 1
            continue

        table = _table_at(lines, i)
        if table:
            headers, align, rows, nxt = table
            if is_question_table(headers):
                flush()
                has_id = headers and headers[0] == ID_HEADER
                cols = headers[1:] if has_id else headers
                aligns = align[1:] if has_id else align
                questions = []
                for row in rows:
                    qid = row[0] if has_id else ""
                    values = row[1:] if has_id else row
                    if not qid:
                        counters[num] = counters.get(num, 0) + 1
                        qid = f"{num or '0'}-{counters[num]:02d}"
                    else:
                        seq = qid.rsplit("-", 1)[-1]
                        if seq.isdigit():
                            counters[num] = max(counters.get(num, 0), int(seq))
                    cells = {h: (values[k] if k < len(values) else "")
                             for k, h in enumerate(cols)}
                    questions.append({"id": qid, "cells": cells,
                                      "followup": {}, "confirmBack": {}})
                doc["blocks"].append({"kind": "questions", "num": num, "headers": cols,
                                      "align": aligns, "questions": questions})
            elif _derived_kind(headers):
                flush()
                which = _derived_kind(headers)
                doc["blocks"].append({"kind": "derived", "which": which,
                                      "headers": headers, "align": align,
                                      "rows": rows})
            elif headers[:2] == ["項目", "値"] and not doc["blocks"]:
                flush()
                doc["blocks"].append({"kind": "meta", "headers": headers,
                                      "align": align, "rows": rows})
                for row in rows:
                    if len(row) >= 2:
                        doc["meta"].setdefault("fields", {})[row[0]] = row[1]
            else:
                prose.extend(lines[i:nxt])
            i = nxt
            continue

        prose.append(line)
        i += 1

    flush()
    return doc


# ---------- derived sections ----------

def _questions(doc: dict) -> list[tuple[dict, dict]]:
    return [(block, q) for block in doc["blocks"] if block["kind"] == "questions"
            for q in block["questions"]]


def all_questions(doc: dict) -> list[dict]:
    return [q for _, q in _questions(doc)]


def find_question(doc: dict, qid: str) -> tuple[dict, dict] | tuple[None, None]:
    for block, q in _questions(doc):
        if q["id"] == qid:
            return block, q
    return None, None


def derived_rows(doc: dict, which: str) -> list[list[str]]:
    """Rows for a derived section. Never hand-kept: they follow the confidences."""
    rows = []
    for block, q in _questions(doc):
        confidence = get(q, "confidence", block["headers"])
        text = get(q, "text", block["headers"])
        if which == DERIVED_UNCONFIRMED:
            if confidence and confidence != "確認済":
                f = q.get("followup") or {}
                rows.append([q["id"], text, f.get("target", ""), f.get("means", ""),
                             f.get("due", ""), f.get("owner", "")])
        elif which == DERIVED_CONFIRM_BACK:
            if confidence == "推定":
                c = q.get("confirmBack") or {}
                answer = get(q, "answer", block["headers"])
                rows.append([q["id"], answer or text, c.get("target", ""), c.get("when", "")])
    return rows


def absorb_derived(doc: dict, which: str, rows: list[list[str]]) -> None:
    """Write an edited derived table back onto the questions it came from."""
    keys = FOLLOWUP_KEYS if which == DERIVED_UNCONFIRMED else CONFIRM_BACK_KEYS
    field = "followup" if which == DERIVED_UNCONFIRMED else "confirmBack"
    for row in rows:
        if not row or not row[0]:
            continue
        _, q = find_question(doc, row[0])
        if q is None:
            continue
        values = row[2:]  # skip ID and the text column, which are rendered from the question
        q[field] = {k: (values[i] if i < len(values) else "") for i, k in enumerate(keys)}


# ---------- render ----------

def customer_blocks(doc: dict) -> tuple[list[dict], list[str]]:
    """Blocks that may be handed to a customer, and the titles of the sections dropped.

    A whole top-level section is dropped when its heading is marked
    `customerSafe: false` — asking about the buying committee or the competition
    is fine face to face, but printing it on a sheet the customer keeps is not
    (playbook §3).
    """
    kept: list[dict] = []
    dropped: list[str] = []
    skipping = False
    for block in doc["blocks"]:
        if block["kind"] == "heading" and block.get("level") == 2:
            skipping = block.get("customerSafe") is False
            if skipping:
                dropped.append(f"§{block.get('num', '')} {block['title']}".strip())
        if not skipping:
            kept.append(block)
    return kept, dropped


def render_markdown(doc: dict, *, audience: str = "internal") -> str:
    """Render the document back to Markdown.

    `customer` drops the internal-only columns (source, confidence) and the
    sections marked `customerSafe: false`.
    """
    out: list[str] = []
    if doc.get("headerComment"):
        out.append(doc["headerComment"])
        out.append("")
    if doc.get("title"):
        out.append(f"# {doc['title']}")
        out.append("")

    skip_headers = {"出典", "確度"} if audience == "customer" else set()
    blocks = customer_blocks(doc)[0] if audience == "customer" else doc["blocks"]

    for block in blocks:
        kind = block["kind"]
        if kind == "heading":
            out.append("#" * block["level"] + " " + _heading_text(block))
            out.append("")
        elif kind == "prose":
            out.append(block["text"])
            out.append("")
        elif kind == "meta":
            out.append(join_row(block["headers"]))
            out.append(join_row(block["align"]))
            for row in block["rows"]:
                out.append(join_row(row))
            out.append("")
        elif kind == "questions":
            headers = [h for h in block["headers"] if h not in skip_headers]
            keep = [i for i, h in enumerate(block["headers"]) if h not in skip_headers]
            align = [block["align"][i] for i in keep] if len(block["align"]) == len(block["headers"]) else ["---"] * len(headers)
            out.append(join_row([ID_HEADER] + headers))
            out.append(join_row([":-:"] + align))
            for q in block["questions"]:
                out.append(join_row([q["id"]] + [q["cells"].get(h, "") for h in headers]))
            out.append("")
        elif kind == "derived":
            headers = block.get("headers") or DERIVED_HEADERS[block["which"]]
            out.append(join_row(headers))
            out.append(join_row(block.get("align") or ["---"] * len(headers)))
            rows = derived_rows(doc, block["which"])
            for row in rows or [[""] * len(headers)]:
                out.append(join_row(row))
            out.append("")
    text = "\n".join(out)
    return re.sub(r"\n{3,}", "\n\n", text).rstrip() + "\n"


def _heading_text(block: dict) -> str:
    if block.get("num"):
        return f"{block['num']}. {block['title']}" if "." not in block["num"] else \
               f"{block['num']} {block['title']}"
    return block["title"]


# ---------- validation ----------

def validate(doc: dict) -> list[str]:
    errors: list[str] = []
    if doc.get("schemaVersion") != SCHEMA_VERSION:
        errors.append(f"schemaVersion は {SCHEMA_VERSION} である必要があります")
    seen: set[str] = set()
    for block, q in _questions(doc):
        if not q.get("id"):
            errors.append(f"ID の無い設問があります: {get(q, 'text', block['headers'])[:30]}")
        elif q["id"] in seen:
            errors.append(f"ID が重複しています: {q['id']}")
        seen.add(q.get("id", ""))
        confidence = get(q, "confidence", block["headers"])
        if confidence and confidence not in CONFIDENCE:
            errors.append(f"{q['id']}: 確度 '{confidence}' は使えません（{' / '.join(CONFIDENCE)}）")
    for block in doc["blocks"]:
        if block["kind"] == "derived" and block["which"] not in DERIVED_HEADERS:
            errors.append(f"未知の derived 種別: {block['which']}")
    return errors
