"""Tie a deck to a Google Spreadsheet: linked charts and bound numbers.

Two things a deck can take from a spreadsheet (one built by build_model.py,
or any other):

- **Linked charts** — the `sheetsChart` figure embeds a Sheets chart with
  `createSheetsChart` (linkingMode LINKED). Slides keeps the link; refreshing
  redraws it from the sheet. `chart` is the chart's id in a build_model spec
  (matched through the chart's alt text `sf-chart:<id>`), its title, or its
  numeric chartId.
- **Bound numbers** — any string in a deck spec may contain
  `{{sheet:NAME}}`, where NAME is a named range (build_model makes one per
  input and table row) or an A1 reference such as `'売上'!G8`. At build time
  the token becomes the cell's *formatted* value, so the sheet decides how
  the number reads (1,260 / 1.3億円 / 52%). The Slides API has no linked
  text, so the element remembers its template in its alt-text description
  (`sf-bind:{…}`), and sync_deck.py rewrites just the bound spans later.

The spreadsheet comes from the deck spec's top-level `"spreadsheet"` (URL or
ID); a `sheetsChart` figure may name its own.
"""
from __future__ import annotations

import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _auth  # noqa: E402
from _i18n import t, register  # noqa: E402

register({
    "{where}: the spec binds {{{{sheet:…}}}} values but has no top-level "
    "'spreadsheet'":
        "{where}: {{{{sheet:…}}}} を使っていますが、トップレベルに "
        "'spreadsheet' がありません",
    "unknown sheet reference(s): {names}": "シートに見つからない参照: {names}",
    "chart '{ref}' was not found in the spreadsheet (charts: {names})":
        "グラフ '{ref}' がスプレッドシートに見つかりません（グラフ: {names}）",
    "  bound numbers: {n} value(s) from the spreadsheet":
        "  バインド数値: スプレッドシートから {n} 件",
    "  warn: bound text not found on its slide, so sync cannot update it: {text}":
        "  警告: バインドした文字列がスライド上に見つからず、同期対象にできません: {text}",
})

TOKEN_RE = re.compile(r"\{\{sheet:([^{}]+)\}\}")
BIND_TAG = "sf-bind:"
CHART_TAG = "sf-chart:"
# Width-alike stand-in used by --dry-run when no cached value exists
DRY_VALUE = "9,999.9"
CACHE_DIR = os.path.join(_auth.SKILL_DIR, "out", "bindings")


def spreadsheet_id(value: str) -> str:
    m = re.search(r"/spreadsheets/d/([A-Za-z0-9_-]+)", value)
    return m.group(1) if m else value.strip()


# ---------- tokens in a spec ----------

def _walk_strings(node, fn):
    """Return a copy of node with fn applied to every string."""
    if isinstance(node, str):
        return fn(node)
    if isinstance(node, list):
        return [_walk_strings(v, fn) for v in node]
    if isinstance(node, dict):
        return {k: _walk_strings(v, fn) for k, v in node.items()}
    return node


def names_in(spec: dict) -> list[str]:
    found: list[str] = []

    def grab(s):
        for m in TOKEN_RE.finditer(s):
            if m.group(1) not in found:
                found.append(m.group(1))
        return s
    _walk_strings(spec, grab)
    return found


def render(template: str, values: dict[str, str]) -> str:
    return TOKEN_RE.sub(lambda m: values.get(m.group(1), m.group(0)), template)


def substitute(spec: dict, values: dict[str, str], plain=lambda s: s
               ) -> tuple[dict, list[list[dict]]]:
    """Fill the tokens in; also return each slide's bindings.

    A binding is {"t": template} for text in a shape, or {"t": template,
    "cell": [k, r, c]} for a cell of the slide's k-th `table` figure (row 0 is
    the header row) — a table cell is pinned to its position, because short
    values such as "1" or "20%" recur across a table and could not be found
    again by their text alone.

    Templates are stored without inline markup (**bold**, [text](url)) since
    that is how the text reads on the slide, which is what sync matches;
    pass the deck builder's markup stripper as `plain`.
    """
    per_slide: list[list[dict]] = []
    for s in spec.get("slides", []):
        found: list[dict] = []

        def add(entry):
            if entry not in found:
                found.append(entry)

        def grab(text):
            if TOKEN_RE.search(text):
                for part in text.split("\n"):
                    if TOKEN_RE.search(part):
                        add({"t": plain(part)})
            return text

        k = 0
        for key, value in s.items():
            if key == "notes":
                # filled in, but not tracked: speaker notes live on the notes
                # page, which sync does not visit
                continue
            if key != "figures":
                _walk_strings(value, grab)
                continue
            for fig in value or []:
                if not (isinstance(fig, dict) and fig.get("type") == "table"):
                    _walk_strings(fig, grab)
                    continue
                grid = [fig.get("headers") or []] + list(fig.get("rows") or [])
                for r, row in enumerate(grid):
                    for c, cell in enumerate(row):
                        if isinstance(cell, str) and TOKEN_RE.search(cell):
                            add({"t": plain(cell), "cell": [k, r, c]})
                k += 1
        per_slide.append(found)
    out = _walk_strings(spec, lambda s: render(s, values) if "{{sheet:" in s else s)
    return out, per_slide


# ---------- values ----------

def fetch_values(sheets, sid: str, names: list[str]) -> dict[str, str]:
    """name -> formatted value of the range's first cell."""
    if not names:
        return {}
    from googleapiclient.errors import HttpError
    out: dict[str, str] = {}
    missing = []
    try:
        got = sheets.spreadsheets().values().batchGet(
            spreadsheetId=sid, ranges=names,
            valueRenderOption="FORMATTED_VALUE").execute().get("valueRanges", [])
        for name, vr in zip(names, got):
            vals = vr.get("values") or [[""]]
            out[name] = str(vals[0][0]) if vals[0] else ""
    except HttpError:
        # One bad name fails the whole batch; find which, one at a time
        for name in names:
            try:
                vr = sheets.spreadsheets().values().get(
                    spreadsheetId=sid, range=name,
                    valueRenderOption="FORMATTED_VALUE").execute()
                vals = vr.get("values") or [[""]]
                out[name] = str(vals[0][0]) if vals[0] else ""
            except HttpError:
                missing.append(name)
    if missing:
        raise ValueError(t("unknown sheet reference(s): {names}", names=", ".join(missing)))
    return out


def _cache_path(sid: str) -> str:
    return os.path.join(CACHE_DIR, f"{sid}.json")


def save_cache(sid: str, values: dict[str, str]) -> None:
    os.makedirs(CACHE_DIR, exist_ok=True)
    with open(_cache_path(sid), "w", encoding="utf-8") as f:
        json.dump(values, f, ensure_ascii=False, indent=1)


def dry_values(spec: dict) -> dict[str, str]:
    """Values for --dry-run: the last build's, else a same-width stand-in."""
    names = names_in(spec)
    cached: dict[str, str] = {}
    if spec.get("spreadsheet"):
        try:
            with open(_cache_path(spreadsheet_id(spec["spreadsheet"])), encoding="utf-8") as f:
                cached = json.load(f)
        except (OSError, ValueError):
            pass
    return {n: cached.get(n, DRY_VALUE) for n in names}


def validate(spec: dict) -> list[str]:
    problems = []
    if names_in(spec) and not spec.get("spreadsheet"):
        problems.append(t("{where}: the spec binds {{{{sheet:…}}}} values but has no "
                          "top-level 'spreadsheet'", where="spec"))
    for i, s in enumerate(spec.get("slides", [])):
        for j, fig in enumerate(s.get("figures") or []):
            if isinstance(fig, dict) and fig.get("type") == "sheetsChart" \
                    and not (fig.get("spreadsheet") or spec.get("spreadsheet")):
                problems.append(f"slides[{i}].figures[{j}]: sheetsChart needs "
                                "'spreadsheet' (on the figure or the spec)")
    return problems


# ---------- charts ----------

_chart_cache: dict[str, list[dict]] = {}


def list_charts(sheets, sid: str) -> list[dict]:
    if sid not in _chart_cache:
        meta = sheets.spreadsheets().get(
            spreadsheetId=sid,
            fields="sheets(charts(chartId,spec(title,altText)))").execute()
        _chart_cache[sid] = [c for s in meta.get("sheets", [])
                             for c in s.get("charts", []) or []]
    return _chart_cache[sid]


def resolve_chart(sheets, sid: str, ref) -> int:
    if isinstance(ref, int) or (isinstance(ref, str) and ref.isdigit()):
        return int(ref)
    charts = list_charts(sheets, sid)
    for c in charts:
        if (c.get("spec") or {}).get("altText") == CHART_TAG + ref:
            return c["chartId"]
    for c in charts:
        if (c.get("spec") or {}).get("title") == ref:
            return c["chartId"]
    names = [((c.get("spec") or {}).get("altText") or "").replace(CHART_TAG, "")
             or (c.get("spec") or {}).get("title") or str(c["chartId"]) for c in charts]
    raise ValueError(t("chart '{ref}' was not found in the spreadsheet (charts: {names})",
                       ref=ref, names=", ".join(names)))


class SheetsChartMixin:
    """The `sheetsChart` figure (mixed into diagrams.Canvas)."""

    def sheets_chart(self, x, y, w, h, chart, *, spreadsheet=None, caption=None,
                     caption_size=9) -> str:
        """Embed a Sheets chart, linked, at (x, y, w, h). Returns the objectId.

        Size the chart in the sheet to the same aspect (build_model's `size`)
        — Slides scales the chart image to the box.
        """
        if getattr(self.deck, "dry", False):
            oid = self.shape(x, y, w, h, kind="RECTANGLE", fill=self.P.border, stroke=None)
        else:
            src = spreadsheet or getattr(self.deck, "spreadsheet", None)
            sid = spreadsheet_id(src)
            chart_id = resolve_chart(_sheets(), sid, chart)
            oid = self._oid("sc")
            self.deck.requests.append({"createSheetsChart": {
                "objectId": oid, "spreadsheetId": sid, "chartId": chart_id,
                "linkingMode": "LINKED",
                "elementProperties": self._elem_props(x, y, w, h)}})
            self._seq += 1
            self.rects[oid] = (x, y, w, h, "IMAGE")
            self.elements.append((oid, "IMAGE"))
            self.solids.append({"rect": (x, y, w, h), "seq": self._seq,
                                "name": f"sheetsChart {chart}"})
        if caption:
            self.label(x, y + h + 0.05, w, 0.26, caption, size=caption_size,
                       align="CENTER", valign="TOP", color=self.P.muted)
        return oid


_sheets_client = None


def _sheets():
    global _sheets_client
    if _sheets_client is None:
        _sheets_client = _auth.sheets_service()
    return _sheets_client


# ---------- tagging (after the deck is built) ----------

def element_texts(el: dict) -> list[tuple[tuple[int, int] | None, str]]:
    """[(cell or None, text)] for a shape or every cell of a table."""
    out = []
    if "shape" in el:
        out.append((None, _text_of(el["shape"].get("text"))))
    elif "table" in el:
        for r, row in enumerate(el["table"].get("tableRows", [])):
            for c, cell in enumerate(row.get("tableCells", [])):
                out.append(((r, c), _text_of(cell.get("text"))))
    return out


def _text_of(text: dict | None) -> str:
    if not text:
        return ""
    parts = []
    for te in text.get("textElements", []):
        if "textRun" in te:
            parts.append(te["textRun"].get("content", ""))
        elif "autoText" in te:
            parts.append(te["autoText"].get("content", ""))
    return "".join(parts)


def _flat_elements(elements: list[dict]):
    for el in elements or []:
        if "elementGroup" in el:
            yield from _flat_elements(el["elementGroup"].get("children", []))
        else:
            yield el


# A shape binding is found again by its text; text this short is only trusted
# when it is the whole of the shape's text
_MIN_SUBSTRING = 6


def tag_requests(pres: dict, slide_ids: list[str], per_slide: list[list[dict]],
                 sid: str, values: dict[str, str]) -> tuple[list[dict], list[str]]:
    """updatePageElementAltText requests that remember each element's bindings."""
    reqs, missed = [], []
    slides = {s["objectId"]: s for s in pres.get("slides", [])}
    for slide_id, entries in zip(slide_ids, per_slide):
        if not entries:
            continue
        page = slides.get(slide_id)
        if not page:
            continue
        elements = list(_flat_elements(page.get("pageElements", [])))
        tables = [el for el in elements if "table" in el]
        shapes = [el for el in elements if "shape" in el]
        hits: dict[str, list[dict]] = {}
        for entry in entries:
            tpl = entry["t"]
            shown = render(tpl, values)
            used = {n: values[n] for n in TOKEN_RE.findall(tpl)}
            target, cell = None, None
            if "cell" in entry:
                k, r, c = entry["cell"]
                if k < len(tables):
                    texts = dict(element_texts(tables[k]))
                    if shown in texts.get((r, c), ""):
                        target, cell = tables[k], [r, c]
            else:
                exact = [el for el in shapes
                         if _text_of(el["shape"].get("text")).strip() == shown.strip()]
                loose = [el for el in shapes
                         if shown in _text_of(el["shape"].get("text"))]
                if exact:
                    target = exact[0]
                elif loose and len(shown.strip()) >= _MIN_SUBSTRING:
                    target = loose[0]
            if target is None:
                missed.append(shown)
                continue
            tagged = {"t": tpl, "v": used}
            if cell:
                tagged["c"] = cell
            lst = hits.setdefault(target["objectId"], [])
            if tagged not in lst:
                lst.append(tagged)
        for oid, tagged in hits.items():
            reqs.append({"updatePageElementAltText": {
                "objectId": oid,
                "description": BIND_TAG + json.dumps({"s": sid, "b": tagged},
                                                     ensure_ascii=False)}})
    return reqs, missed


def tag_deck(slides_service, presentation_id: str, slide_ids: list[str],
             per_slide: list[list[str]], sid: str, values: dict[str, str]) -> None:
    pres = slides_service.presentations().get(
        presentationId=presentation_id,
        fields="slides(objectId,pageElements)").execute()
    reqs, missed = tag_requests(pres, slide_ids, per_slide, sid, values)
    for text in missed:
        print(t("  warn: bound text not found on its slide, so sync cannot update "
                "it: {text}", text=text[:60]), file=sys.stderr)
    if reqs:
        slides_service.presentations().batchUpdate(
            presentationId=presentation_id, body={"requests": reqs}).execute()


# ---------- sync (used by sync_deck.py) ----------

def _utf16(s: str) -> int:
    return len(s.encode("utf-16-le")) // 2


def plan_text_updates(el: dict, tag: dict, new_values: dict[str, str]
                      ) -> tuple[list[dict], list[tuple[str, str]], dict, list[str]]:
    """Requests that swap each bound span for its new value, keeping styles.

    For every bound template, the text as last rendered is located in the
    element (or one of its table cells); each token's span is rewritten by
    inserting the new value right after the old one — so it inherits the old
    value's style — then deleting the old one. Spans are processed from the
    end so earlier indices stay valid.

    Returns (requests, [(old, new)], updated tag, problems).
    """
    reqs: list[dict] = []
    changes: list[tuple[str, str]] = []
    problems: list[str] = []
    new_tag = {"s": tag["s"], "b": []}
    texts = element_texts(el)
    edits: dict = {}  # cell -> list of (start, end, new)
    for entry in tag.get("b", []):
        tpl, old_vals = entry["t"], entry.get("v", {})
        shown = render(tpl, old_vals)
        new_vals = {n: new_values.get(n, old_vals.get(n, "")) for n in old_vals}
        located = False
        pinned = tuple(entry["c"]) if entry.get("c") else None
        for cell, text in texts:
            if pinned is not None and cell != pinned:
                continue
            pos = text.find(shown)
            if pos < 0:
                continue
            located = True
            # walk the template to find each token's span inside `shown`
            cursor, at = 0, pos
            for m in TOKEN_RE.finditer(tpl):
                literal = tpl[cursor:m.start()]
                at += len(literal)
                name = m.group(1)
                old = old_vals.get(name, "")
                new = new_vals.get(name, old)
                if old != new:
                    edits.setdefault(cell, []).append((at, at + len(old), new, text))
                    changes.append((old, new))
                at += len(old)
                cursor = m.end()
            break
        if not located:
            problems.append(shown)
            new_tag["b"].append(entry)
        else:
            new_tag["b"].append(dict(entry, v=new_vals))
    for cell, spans in edits.items():
        for start, end, new, text in sorted(spans, key=lambda s: -s[0]):
            s16, e16 = _utf16(text[:start]), _utf16(text[:end])
            base = {"objectId": el["objectId"]}
            if cell is not None:
                base["cellLocation"] = {"rowIndex": cell[0], "columnIndex": cell[1]}
            if new:
                reqs.append({"insertText": dict(base, text=new, insertionIndex=e16)})
            if e16 > s16:
                reqs.append({"deleteText": dict(base, textRange={
                    "type": "FIXED_RANGE", "startIndex": s16, "endIndex": e16})})
    return reqs, changes, new_tag, problems


def read_tag(el: dict) -> dict | None:
    desc = el.get("description") or ""
    if not desc.startswith(BIND_TAG):
        return None
    try:
        return json.loads(desc[len(BIND_TAG):])
    except ValueError:
        return None
