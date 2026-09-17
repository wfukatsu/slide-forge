#!/usr/bin/env python3
"""Build a catalog deck for one slide-template pack.

Six pages per template: the rendered sample, its slot map, the request that
produces it, the input JSON, what the template answers, and its guardrails.
Every page carries a real TITLE placeholder, so the deck must be generated
against a master with real layouts (scalar-2026, corporate, aixdevops) —
`blank-16x9` has none and would draw titles as plain text boxes.

  .venv/bin/python scripts/build_template_catalog_deck.py --pack proposal
  .venv/bin/python scripts/build_deck.py --template templates/scalar-2026.json \
      --spec out/proposal-template-catalog/deck.json --dry-run --strict
"""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _text import em  # noqa: E402
from slide_templates import (SlideTemplateError, load_example,  # noqa: E402
                             load_template, render_template, template_entries)

ROOT = Path(__file__).resolve().parent.parent

# Geometry, tuned against scalar-2026: its title band ends at y=0.477 and the
# master's logo/footer band starts at y=5.197.
TOP = 0.62
# Rows per slot-map page. Tables grow beyond their declared height when cells
# wrap, by an amount the spec cannot predict, so this is a hard cap rather
# than a computed fit.
SLOT_ROWS_PER_PAGE = 8

# Column ratios for the two prose tables. The auditor flags a cell when its
# width modulo the per-line width lands in (0, 1.0] em — a sliver on the last
# wrapped line. That remainder moves with the column width, so these are
# chosen by sweeping them against the auditor, not derived.
GUARD_LABEL_W = float(os.environ.get("CATALOG_GUARD_W", "0.55"))
USAGE_LABEL_W = float(os.environ.get("CATALOG_USAGE_W", "2.2"))
SRC_Y = 4.85
NO_LINE_START = "。、）」』】：；？！,.)]}"
LEVEL = {"descriptive": "descriptive（事実の記述）",
         "causal": "causal（因果の主張）",
         "predictive": "predictive（将来の予測）",
         "diagnostic": "diagnostic（診断・評価）"}

# Hand-written requests read better than derived ones; supply them per pack
# where they exist. Everything else falls back to PROMPT_FROM_METADATA.
PROMPT_OVERRIDES = {
    "iceberg-challenge": "A 社の提案書を作っています。ヒアリングで挙がった「突合の工数」と「締めの遅延」という 2 つの問題について、その下にある構造をまとめた課題整理のページを 1 枚作ってください。下段の根本原因は 3 つまでで、あくまでこちらの読みだと分かるようにしてください。",
    "challenge-solution-map": "合意した課題 3 つそれぞれに対して、どの機能で解決し、業務がどうなるかを 1 対 1 で並べたページを作ってください。解けない課題は無理に当てはめず、対象外として下に書いてください。",
    "scope-in-out": "今回の提案の対象範囲と対象外を並べたページを作ってください。対象外にした理由も添えて、後から膨らまないようにしたいです。",
    "outcome-before-after": "導入後に現場の仕事が何が変わるかを、機能ではなく業務の言葉で before / after に並べたページを作ってください。定量値は算出根拠があるものだけにしてください。",
    "poc-plan": "PoC の目的と合否基準のページを作ってください。基準は数値か YES/NO で答えられる形にし、合格したら次に何が起きるかまで書いてください。",
    "next-step-customer": "本日決めたいことと、次回までの双方の宿題を分けたページを作ってください。今日決めることは 1 つに絞り、こちら側の宿題も必ず入れてください。",
}


def short(name: str) -> str:
    """Title box is one 20pt line; drop the parenthetical from displayName."""
    return re.sub(r"（.*?）", "", name).strip()


def derived_prompt(t: dict) -> str:
    """A request sentence built from the template's own definition.

    Used where no hand-written prompt exists. Reads plainly rather than
    pretending to be a curated example — the page says which it is.
    """
    desc = (t.get("description") or "").rstrip("。")
    q = (t.get("answers") or [""])[0].rstrip("。")
    parts = [f"{desc}ページを 1 枚作ってください。" if desc
             else "このテンプレートのページを 1 枚作ってください。"]
    if q:
        parts.append(f"読み手に「{q}」が伝わる形にしてください。")
    caps = [(n, dens(s.get("maxItems"))) for n, s in (t.get("slots") or {}).items()
            if dens(s.get("maxItems"))]
    if caps:
        n, m = caps[0]
        parts.append(f"項目「{n}」は {m} 件までです。")
    return "".join(parts)


def lead(text, y=TOP):
    return {"type": "lead_in", "x": 0.5, "y": y, "w": 9.0, "text": text}


def src(text, y=SRC_Y):
    return {"type": "source_note", "x": 0.5, "y": y, "w": 9.0, "source": text}


def table(headers, rows, y, colw, aligns):
    """Fit the rows into the band between y and the source note.

    A fixed row height overflows the master's logo/footer band as soon as a
    template declares more slots or guardrails than the proposal pack does.
    """
    # chars per line in a 8.45-ratio column, and the height one wrapped line
    # needs. Both measured with build_deck.py --dry-run against scalar-2026.
    CAP = {11: 55, 9.5: 70, 7.5: 100}
    LINE_H = {11: 0.185, 9.5: 0.16, 7.5: 0.13}
    HEADER = {11: 0.46, 9.5: 0.42, 7.5: 0.34}

    # Width and height have to be decided together: _tuned_widths changes the
    # column split, which changes per-line width, which changes how many lines
    # a cell wraps to. Deciding the height first left it stale.
    limit = 5.10 - y          # stay clear of the master's footer band at 5.20

    def plan(size):
        cw = _tuned_widths(headers, rows, colw, size)
        total = sum(cw)
        lines = 1
        for i, c in enumerate(cw):
            col_in = 9.0 * c / total
            per = (col_in - CELL_INSET * 2) * 72.0 / size
            if per <= 0:
                continue
            longest = max([em(str(r[i])) for r in rows] + [em(str(headers[i]))],
                          default=0.0)
            lines = max(lines, math.ceil(longest / per))
        row_h = max(0.26, round(LINE_H[size] * lines, 2))
        return cw, row_h, HEADER[size], HEADER[size] + row_h * len(rows)

    chosen = None
    for size in (11, 9.5, 7.5):
        cw, row_h, header_h, total_h = plan(size)
        if total_h <= limit:
            chosen = (size, cw, row_h, header_h)
            break
    if chosen is None:
        cw, row_h, header_h, _ = plan(7.5)
        chosen = (7.5, cw, row_h, header_h)
    size, colw, row_h, header_h = chosen
    return {"type": "table", "x": 0.5, "y": y, "w": 9.0, "headers": headers,
            "rows": rows, "colWidths": colw, "aligns": aligns,
            "size": size, "rowH": row_h, "headerH": header_h}


# The auditor flags a cell when its width modulo the per-line width lands in
# (0, ORPHAN_EM] — a sliver stranded on the last wrapped line. Both quantities
# are computable, so pick a column split where no cell lands there rather than
# guessing: per = (column_in - inset*2) * 72 / size, inset 0.10 for a cell.
CELL_INSET = 0.10
ORPHAN_EM = 1.0


def _orphans(texts, col_in: float, size: float) -> int:
    per = (col_in - CELL_INSET * 2) * 72.0 / size
    if per <= 2.0:                       # auditor skips stacks this narrow
        return 0
    n = 0
    for txt in texts:
        e = em(str(txt))
        if e > per and 0 < (e % per) <= ORPHAN_EM:
            n += 1
    return n


def _tuned_widths(headers, rows, colw, size):
    """Shift width between a two-column table's label and prose columns until
    no cell strands a sliver. A single global split cannot satisfy every pack:
    the remainder moves per cell, so the choice has to be per table."""
    if len(colw) != 2:
        return colw
    total = sum(colw)
    texts = [str(r[1]) for r in rows] + [str(headers[1])]
    best, best_n = colw, None
    for step in range(0, 25):
        label = colw[0] + step * 0.06
        if label >= total - 1.0:
            break
        n = _orphans(texts, total - label, size)
        if n == 0:
            return [round(label, 2), round(total - label, 2)]
        if best_n is None or n < best_n:
            best, best_n = [round(label, 2), round(total - label, 2)], n
    return best


def code(codetext, lang, y, avail, size=9.5, min_h=None):
    """Size the panel to its content. code_block centres text vertically, so a
    panel taller than its text shows empty dark bands above and below."""
    lines = codetext.count("\n") + 1
    while True:
        h = lines * (size * 1.04 * 1.45 / 72) + 0.40
        if h <= avail or size <= 6.5:
            break
        size -= 0.5
    line_h = size * 1.04 * 1.45 / 72
    if h > avail:
        # still too tall at the smallest size: show the shape of the payload,
        # not every row of it
        keep = max(3, int((avail - 0.40) / line_h) - 1)
        kept = codetext.split("\n")[:keep]
        codetext = "\n".join(kept + [f"  … 以下 {lines - keep} 行省略"])
        h = (keep + 1) * line_h + 0.40
    if min_h:
        h = max(h, min_h)
    return {"type": "code_block", "x": 0.7, "y": y, "w": 8.6, "h": round(h, 2),
            "lang": lang, "code": codetext, "size": size}


def despace(t: str) -> str:
    """Collapse runs of spaces. Removing the single space at a Latin/CJK
    boundary would yield 「PoCの目的」, which reads worse than the slightly wide
    gap Slides' own spacing produces."""
    return re.sub(r"[ ]{2,}", " ", t)


def wrap(t: str, n: int = 44) -> str:
    """Character wrap that avoids a closing mark at line start, an ASCII word
    split, and a digit split from its counter."""
    import math
    n = min(n, math.ceil(len(t) / max(1, math.ceil(len(t) / n))))
    out, line = [], ""
    for ch in t:
        if line and len(line) >= n:
            prev = line[-1]
            blocked = (ch in NO_LINE_START
                       or (prev.isascii() and prev.isalnum()
                           and ch.isascii() and ch.isalnum())
                       or (prev.isdigit() and not ch.isascii()))
            if not blocked:
                out.append(line)
                line = ch
                continue
        line += ch
    if line:
        out.append(line)
    return "\n".join(l.strip() for l in out)


def cjson(o, ind=0):
    """Pretty JSON that keeps short string arrays on one line, so a payload
    fits the panel without shrinking the type."""
    pad = "  " * ind
    if isinstance(o, dict):
        items = list(o.items())
        res = ["{"]
        for i, (k, v) in enumerate(items):
            c = "," if i < len(items) - 1 else ""
            if isinstance(v, list) and all(isinstance(x, str) for x in v) \
               and len(", ".join(v)) <= 52 \
               and len(f'{pad}  "{k}": {json.dumps(v, ensure_ascii=False)}') <= 78:
                res.append(f'{pad}  "{k}": {json.dumps(v, ensure_ascii=False)}{c}')
            elif isinstance(v, (dict, list)):
                res.append(f'{pad}  "{k}": {cjson(v, ind + 1)}{c}')
            else:
                res.append(f'{pad}  "{k}": {json.dumps(v, ensure_ascii=False)}{c}')
        res.append(pad + "}")
        return "\n".join(res)
    if isinstance(o, list):
        res = ["["]
        for i, v in enumerate(o):
            c = "," if i < len(o) - 1 else ""
            one = f'{pad}  {json.dumps(v, ensure_ascii=False)}{c}'
            res.append(one if len(one) <= 78 else f'{pad}  {cjson(v, ind + 1)}{c}')
        res.append(pad + "]")
        return "\n".join(res)
    return json.dumps(o, ensure_ascii=False)


def dens(v, density: str | None = None):
    """A slot limit may be a plain number or {"$density": {print, presentation}}."""
    if isinstance(v, dict) and "$density" in v:
        variants = v["$density"]
        return variants.get(density or "print") or next(iter(variants.values()))
    return v


def slot_rows(slots: dict, density: str | None = None) -> list[list[str]]:
    rows = []
    for name, s in (slots or {}).items():
        lim = []
        if dens(s.get("maxLength"), density):
            lim.append(f"最大{dens(s['maxLength'], density)}字")
        if dens(s.get("minItems"), density):
            lim.append(f"{dens(s['minItems'], density)}件以上")
        if dens(s.get("maxItems"), density):
            lim.append(f"{dens(s['maxItems'], density)}件まで")
        rows.append([name, s.get("type", ""), "、".join(lim) or "—",
                     "必須" if s.get("required") else "任意"])
    return rows


def sample_page(rendered: dict, title: str) -> dict:
    """The template's own drawing, with its governing_message promoted to the
    slide's real title and the rest pulled up into the band that frees."""
    figs = [f for f in json.loads(json.dumps(rendered))["figures"]
            if f.get("type") != "governing_message"]
    body = [f for f in figs if f.get("type") != "source_note"]
    if body:
        shift = min(f.get("y", TOP) for f in body) - TOP
        for f in body:
            if "y" in f:
                f["y"] = round(f["y"] - shift, 3)
    for f in figs:
        if f.get("type") == "source_note":
            f["y"] = SRC_Y
    return {"layout": "TITLE_ONLY", "title": title, "figures": figs}


def build(pack: str, density: str | None = None) -> dict:
    entries = template_entries(pack=pack)
    if not entries:
        raise SlideTemplateError(f"no slide templates registered for pack: {pack}")

    slides = [{
        "layout": "COVER",
        "title": "スライドテンプレート カタログ",
        "subtitle": f"{pack} パック 全 {len(entries)} 種 — 作例・入力・使い方",
    }]

    for entry in entries:
        tid = entry["id"]
        t, _ = load_template(tid)
        ex, _ = load_example(tid, density)
        rendered = render_template(t, ex, density=density)
        lab = short(t.get("displayName") or tid)
        q = (t.get("answers") or ["—"])[0]

        # 1. the sample
        gm = next((f["text"] for f in rendered["figures"]
                   if f.get("type") == "governing_message"), None)
        slides.append(sample_page(rendered, gm or lab))

        # 2. slot map — paginated. A table's declared height is not what gets
        # rendered: rows grow to fit their text, and that growth is not
        # predictable from the spec (charts.py: row_h is a minimum). Capping
        # the rows per page bounds the result by construction instead.
        all_slots = slot_rows(t.get("slots"), density)
        chunks = [all_slots[i:i + SLOT_ROWS_PER_PAGE]
                  for i in range(0, len(all_slots), SLOT_ROWS_PER_PAGE)] or [[]]
        for part, chunk in enumerate(chunks):
            suffix = "" if part == 0 else f"（続き {part + 1}/{len(chunks)}）"
            slides.append({"layout": "TITLE_ONLY",
                           "title": f"{lab} — 作例と入力項目の対応{suffix}",
                           "figures": [
                lead("前ページの作例を、テンプレートが受け取る入力項目に対応づけています。"
                     if part == 0 else "入力項目の続きです。"),
                table(["入力項目", "型", "制約", "要否"], chunk,
                      TOP + 0.38, [2.2, 2.4, 2.6, 1.8],
                      ["START", "START", "START", "CENTER"]),
                src(f"slide-templates/{pack}/{tid}/template.json の slots 定義"),
            ]})

        # 3. the request that produces it
        hand = PROMPT_OVERRIDES.get(tid)
        prompt = hand or derived_prompt(t)
        cb = code(wrap(despace(prompt)), "text", TOP + 0.38, 2.6,
                  size=13, min_h=1.3)
        slides.append({"layout": "TITLE_ONLY",
                       "title": f"{lab} — こう頼めば出てきます", "figures": [
            lead("実際に入力する日本語の依頼文の例です。"),
            cb,
            {"type": "so_what", "x": 0.5, "y": round(cb["y"] + cb["h"] + 0.35, 2),
             "w": 9.0, "h": 1.0, "text": f"答える問い —「{q}」",
             "label": "このテンプレートを選ぶ判断"},
            src("依頼文は例。実際には顧客名・課題・数値を差し替える" if hand else
                "依頼文はテンプレート定義（description / answers / slots）から生成した例"),
        ]})

        # 4. the input it becomes
        slides.append({"layout": "TITLE_ONLY", "title": f"{lab} — 入力データ",
                       "figures": [
            lead("テンプレートが受け取る JSON です。作例はこの内容で描かれています。"),
            (jcode := code(cjson(ex), "json", TOP + 0.38, 3.6, min_h=2.4)),
            src(f"slide-templates/{pack}/{tid}/example.json"
                + ("（長いため一部を省略）" if "行省略" in jcode["code"] else "")),
        ]})

        # 5. what it is for
        slides.append({"layout": "TITLE_ONLY",
                       "title": f"{lab} — 答える問いと向く場面", "figures": [
            lead("何を示す 1 枚なのか、どの段階で使うのかを整理しています。"),
            table(["観点", "内容"], [
                ["答える問い", q],
                ["何を示す図か", t.get("description", "—")],
                ["推論レベル", LEVEL.get(t.get("inferenceLevel", ""),
                                     t.get("inferenceLevel", "—"))],
                ["対応レイアウト",
                 "、".join(t.get("compatibleLayouts") or ["BLANK"])
                 + "（背景のみのページに描画する）"],
                ["テンプレート ID", f"{pack} / {tid}"],
            ], TOP + 0.38, [USAGE_LABEL_W, 9.0 - USAGE_LABEL_W],
                  ["START", "START"]),
            src(f"slide-templates/{pack}/{tid}/template.json"),
        ]})

        # 6. how it breaks
        guards = t.get("guardrails") or []
        rows = ([[str(i + 1), re.sub(r"\*\*", "", g)] for i, g in enumerate(guards)]
                or [["—", "このテンプレートにはガードレールが定義されていない"]])
        slides.append({"layout": "TITLE_ONLY",
                       "title": f"{lab} — 壊れる典型的な使い方", "figures": [
            lead("テンプレートに埋め込まれたガードレールです。作成時に必ず確認します。"),
            table(["#", "気をつけること"], rows,
                  TOP + 0.38, [GUARD_LABEL_W, 9.0 - GUARD_LABEL_W],
                  ["CENTER", "START"]),
            src(f"slide-templates/{pack}/{tid}/template.json の guardrails"),
        ]})

    return {"title": f"スライドテンプレート カタログ — {pack} パック",
            "slides": slides}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--pack", required=True)
    ap.add_argument("--out", help="default: out/<pack>-template-catalog/deck.json")
    ap.add_argument("--density", choices=("print", "presentation"))
    args = ap.parse_args()

    deck = build(args.pack, args.density)
    out = Path(args.out) if args.out else \
        ROOT / f"out/{args.pack}-template-catalog/deck.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(deck, ensure_ascii=False, indent=2) + "\n",
                   encoding="utf-8")
    n = len(deck["slides"])
    print(f"{n} slides ({(n - 1) // 6} templates) -> {out}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SlideTemplateError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
