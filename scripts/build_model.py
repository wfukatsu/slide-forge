#!/usr/bin/env python3
"""Build a planning-model Google Spreadsheet (inputs, formulas, charts) from a JSON spec.

    .venv/bin/python scripts/build_model.py model.json --dry-run          # validate + lay out (offline, free)
    .venv/bin/python scripts/build_model.py model.json --folder <Drive folder URL/ID>
    .venv/bin/python scripts/build_model.py model.json --into <Spreadsheet URL/ID>
    .venv/bin/python scripts/build_model.py model.json --into <ID> --reset-inputs

Where `build_sheet.py` makes line-item estimates (one table per sheet, via
xlsx), this script makes the workbook a business plan is simulated in:
assumption cells the reader edits, time-series tables whose cells are
formulas over those assumptions, a scenario switch, and native Sheets charts
that a deck links to (`sheetsChart` figure in build_deck.py). It writes
through the Sheets API directly, so a rebuild keeps every sheetId and chartId
— the links a deck holds to this workbook survive regeneration.

Spec format:

    {
      "title": "FY27-29 事業計画モデル",
      "sheets": [{
        "name": "前提",
        "widths": [260, 70, 110],          // optional, px for columns A, B, C… (rest: 100)
        "freeze": [0, 2],                  // optional, frozen rows / columns
        "blocks": [
          {"type": "heading", "text": "前提条件"},
          {"type": "note", "text": "黄色のセルを書き換えるとシミュレーションできます"},
          {"type": "inputs", "title": "単価", "rows": [
            {"id": "price_assessment", "label": "Assessment 単価", "value": 400,
             "unit": "万円", "format": "int", "note": "300〜500万円"},
            {"id": "scenario", "label": "シナリオ", "value": "Base",
             "choices": ["保守", "Base", "強気"]},
            {"id": "fy27_total", "label": "FY27 売上", "formula": "={@rev_total:FY27}",
             "unit": "万円"}
          ]},
          {"type": "table", "id": "rev", "title": "売上", "columns": [
             "Q1", "Q2", "Q3", "Q4",
             {"header": "FY27", "formula": "=SUM({first}{row}:{prev}{row})"}],
           "rows": [
             {"id": "cnt_academy", "label": "Academy 件数", "unit": "社",
              "values": [0, 1, 1, 2, null]},
             {"id": "rev_academy", "label": "Academy 売上", "unit": "万円",
              "formula": "={@cnt_academy}*{@price_academy}"},
             {"id": "rev_total", "label": "合計", "unit": "万円", "style": "total",
              "formula": "=SUM({@rev_academy})"}
           ]},
          {"type": "grid", "id": "g_rev", "header": ["四半期", "売上"],
           "cells": [["=TRANSPOSE({hdr:rev})", "=TRANSPOSE({range:rev_total})"]],
           "rows": 5, "formats": [null, "int"]}
        ]
      }],
      "charts": [{
        "id": "rev_by_quarter", "sheet": "前提", "data": "g_rev", "type": "COLUMN",
        "anchor": "H2", "size": [6.0, 3.0], "labels": true
      }]
    }

Layout. Blocks stack down the sheet with one blank row between them. Inputs
put the label in A, the unit in B, the value in C and the note in D. Tables
put the label in A, the unit in B and the columns from C, so tables that share
column headers line up column for column. Grids start at A (category column,
then one column per series) and exist to feed charts.

Cells. A literal number or string is an input: yellow, and kept across
rebuilds (see "Rebuilds"). A string starting with "=" is a formula. "?" is an
empty input cell (a figure the reader still has to supply; formulas read it
as 0), and "" in a table row leaves that cell blank. In a table row,
`values[j]` wins, then the column's formula, then the row's.

Placeholders in formulas:
    {@id}           an input's cell, or a table row's cell in the current column
    {@id:HEADER}    a table row's cell in the column headed HEADER
    {@id:<}         a table row's cell in the column before the current one
    {range:id}      a table row's value cells          ('売上'!C5:G5)
    {range:a..b}    the block of rows a through b of one table
    {hdr:table}     a table's header cells
    {col} {prev} {row} {first} {last}
                    this column's / the previous column's letter, this row,
                    the table's first / last value column letter

Every input id and table-row id also becomes a named range, which is what a
deck binds to (`{{sheet:fy27_total}}`, see sheets_link.py).

Formats: int (#,##0), dec1, dec2, pct (0%), pct1 (0.0%), yen (¥#,##0), text,
or any Sheets number-format pattern.

Charts: `type` COLUMN / BAR / LINE / AREA / COMBO / PIE; `data` names a grid
(column A = categories, one column per series, header row = series names);
`stacked`, `labels` (data labels), `seriesTypes` (COMBO, e.g.
["COLUMN","COLUMN","LINE"]), `colors`, `title`, `legend`
(BOTTOM/RIGHT/TOP/NONE), `vAxisTitle`, `font`. Give `size` in inches as the
box the chart will take on the slide: the chart is drawn at that size
(96 px per inch), so a linked chart keeps its proportions and type size.

Rebuilds. With the same title in the same folder, or with --into, the
existing spreadsheet is rebuilt in place: sheets are matched by name and
charts by id, so their ids — and the URL — stay. Input cells keep the values
the reader typed unless --reset-inputs is given; inputs are matched by id
(and column header for table cells), so moving rows around keeps them.
"""
from __future__ import annotations

import argparse
import copy
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _i18n import t, register  # noqa: E402

register({
    'title is missing':
        'title がありません',
    'sheets is empty':
        'sheets が空です',
    '{where}: id is missing':
        '{where}: id がありません',
    "{where}: duplicate id '{id}'":
        "{where}: id '{id}' が重複しています",
    "{where}: id '{id}' cannot be a named range (use letters, digits and _, start with a letter, and avoid cell-like names such as Q1 or R2C3)":
        "{where}: id '{id}' は名前付き範囲にできません（英数字と _ を使い、英字で始め、Q1 や R2C3 のようなセル番地に見える名前は避ける）",
    '{where}: name is missing':
        '{where}: name がありません',
    "{where}: duplicate or reserved sheet name '{name}'":
        "{where}: シート名 '{name}' が重複しているか予約済みです",
    '{where}: give exactly one of value / formula':
        '{where}: value と formula はどちらか一方だけを指定してください',
    '{where}: columns is empty':
        '{where}: columns が空です',
    '{where}: column headers must be unique':
        '{where}: 列見出しが重複しています',
    '{where}: {got} values do not match the {want} columns':
        '{where}: 値 {got} 個が列数 {want} と一致しません',
    '{where}: header is empty':
        '{where}: header が空です',
    '{where}: wider than the header':
        '{where}: header より列が多いです',
    "{where}: unknown block type '{kind}' (heading / note / inputs / table / grid)":
        "{where}: 未知のブロック type '{kind}'（heading / note / inputs / table / grid）",
    '{ph} used in column A':
        '{ph} が A 列で使われています',
    '{ph} is only usable inside a table row':
        '{ph} は表の行の中でだけ使えます',
    "'{id}' is an input; it has no columns":
        "'{id}' は入力セルなので列を指定できません",
    '{ph} needs a previous column in this table':
        '{ph} にはこの表の前の列が必要です',
    "row '{id}' has no column '{col}'":
        "行 '{id}' に列 '{col}' がありません",
    "row '{id}' has no column '{col}' (columns: {cols})":
        "行 '{id}' に列 '{col}' がありません（列: {cols}）",
    '{ph} needs a column; outside a table write {alt}':
        '{ph} には列が必要です。表の外では {alt} と書いてください',
    "row '{id}' has no column '{col}'; the tables do not share this column":
        "行 '{id}' に列 '{col}' がありません。表どうしでこの列が共通していません",
    "unknown id '{id}'":
        "未知の id '{id}'",
    "unknown row in '{ref}'":
        "'{ref}' に未知の行があります",
    "'{ref}': both rows must be in the same table with an id":
        "'{ref}': 両方の行が id 付きの同じ表にある必要があります",
    "unknown row '{id}'":
        "未知の行 '{id}'",
    "unknown table '{id}'":
        "未知の表 '{id}'",
    'unknown placeholder {ph}':
        '未知のプレースホルダ {ph}',
    '{where}: id missing or duplicated':
        '{where}: id がないか重複しています',
    "{where}: unknown sheet '{name}'":
        "{where}: 未知のシート '{name}'",
    "{where}: data must name a grid (got '{got}')":
        "{where}: data には grid の id を指定してください（指定値: '{got}'）",
    "{where}: unknown type '{kind}' ({allowed})":
        "{where}: 未知の type '{kind}'（{allowed}）",
    '{where}: COMBO needs seriesTypes for each of the {n} series':
        '{where}: COMBO には {n} 系列それぞれの seriesTypes が必要です',
    '{where}: legend must be one of {allowed}':
        '{where}: legend は {allowed} のいずれかです',
    '{where}: size must be [w, h] in inches':
        '{where}: size は [w, h]（インチ）で指定してください',
    "ERROR: give --folder (the deck's Drive folder) or --into <spreadsheet>; a title alone is not a safe target to rebuild":
        "ERROR: --folder（デッキの Drive フォルダ）か --into <スプレッドシート> を指定してください。タイトルだけでは再構築の対象を安全に決められません",
    "Build a planning-model Google Spreadsheet from a JSON spec":
        "JSON スペックから計画モデルの Google Spreadsheet を生成する",
    "path to the model spec JSON": "モデルスペック JSON のパス",
    "validate and lay out only (no API calls)": "検証とレイアウト計算のみ（API を呼ばない）",
    "Drive folder URL or ID for a new spreadsheet":
        "新規スプレッドシートを置く Drive フォルダの URL または ID",
    "rebuild this existing spreadsheet (URL or ID) in place":
        "既存のスプレッドシート（URL または ID）をその場で再構築する",
    "overwrite input cells with the spec values (default: keep what the reader typed)":
        "入力セルをスペックの値で上書きする（既定: 読み手が入力した値を残す）",
    "print every cell address the spec resolved to":
        "スペックが解決したセル番地をすべて表示する",
    "The model spec has problems:": "モデルスペックに問題があります:",
    "Layout OK: {sheets} sheet(s) / {inputs} input cell(s) / {formulas} formula(s) / {charts} chart(s)":
        "レイアウト OK: {sheets} シート / 入力セル {inputs} / 数式 {formulas} / グラフ {charts}",
    "  kept {n} input value(s) the reader had changed":
        "  読み手が変更した入力値 {n} 件を保持しました",
    "  formula errors ({n}):": "  数式エラー（{n} 件）:",
    "  formulas: no errors": "  数式: エラーなし",
    "  note: sheet '{name}' is not in the spec and was left as it is":
        "  注意: シート '{name}' はスペックにないため、そのまま残しました",
    "  note: chart '{id}' is not in the spec and was left as it is (a deck may link to it)":
        "  注意: グラフ '{id}' はスペックにないため残しました（デッキがリンクしている可能性があります）",
})

SPREADSHEET_MIME = "application/vnd.google-apps.spreadsheet"
META_SHEET = "_sf_model"
CHART_TAG = "sf-chart:"
PX_PER_INCH = 96

FORMATS = {
    "int": "#,##0",
    "dec1": "#,##0.0",
    "dec2": "#,##0.00",
    "pct": "0%",
    "pct1": "0.0%",
    "yen": "¥#,##0",
    "text": "@",
}
CHART_TYPES = ("COLUMN", "BAR", "LINE", "AREA", "COMBO", "PIE")
LEGENDS = {"BOTTOM": "BOTTOM_LEGEND", "RIGHT": "RIGHT_LEGEND",
           "TOP": "TOP_LEGEND", "LEFT": "LEFT_LEGEND", "NONE": "NO_LEGEND"}

HEADER_FILL = "1F3864"
INPUT_FILL = "FFF2CC"
INPUT_FONT = "1F4E9F"
TOTAL_FILL = "F2F2F2"
NOTE_COLOR = "808080"
DEFAULT_COLORS = ["#1F3864", "#2E75B6", "#9DC3E6", "#F4B183", "#A9D18E",
                  "#FFD966", "#7F7F7F"]
LABEL_W, UNIT_W, VALUE_W = 240, 64, 100

_PH_RE = re.compile(r"\{(@[^{}]+|range:[^{}]+|hdr:[^{}]+|col|prev|row|first|last)\}")
# A named range may not look like a cell reference (A1, R1C1) or be TRUE/FALSE
_NAME_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_.]{0,249}$")
_CELLISH_RE = re.compile(r"^([A-Za-z]{1,3}\d+|[Rr]\d*[Cc]\d*|true|false)$", re.I)


def col_letter(idx: int) -> str:
    """0-based column index -> letters (0 -> A)."""
    s = ""
    idx += 1
    while idx:
        idx, r = divmod(idx - 1, 26)
        s = chr(65 + r) + s
    return s


def quote_sheet(name: str) -> str:
    return "'" + name.replace("'", "''") + "'"


def a1(sheet: str, row: int, col: int, *, absolute: bool = False) -> str:
    """0-based row/col -> 'Sheet'!C5."""
    d = "$" if absolute else ""
    return f"{quote_sheet(sheet)}!{d}{col_letter(col)}{d}{row + 1}"


def a1_range(sheet: str, r0: int, c0: int, r1: int, c1: int) -> str:
    return (f"{quote_sheet(sheet)}!{col_letter(c0)}{r0 + 1}:"
            f"{col_letter(c1)}{r1 + 1}")


def _hex_color(value: str) -> dict:
    v = value.lstrip("#")
    return {"red": int(v[0:2], 16) / 255, "green": int(v[2:4], 16) / 255,
            "blue": int(v[4:6], 16) / 255}


def number_format(fmt: str | None) -> str | None:
    if fmt is None:
        return None
    return FORMATS.get(fmt, fmt)


# ---------- Layout (offline) ----------

class Cell:
    """One cell the build will write."""

    __slots__ = ("value", "fmt", "style", "is_input", "key", "choices", "note",
                 "literal")

    def __init__(self, value, *, fmt=None, style=None, is_input=False, key=None,
                 choices=None, note=None, literal=False):
        self.value = value
        self.fmt = fmt
        self.style = style
        self.is_input = is_input
        self.key = key          # stable id for keeping inputs across rebuilds
        self.choices = choices
        self.note = note
        # labels, units, notes and headers are text even when they start with "="
        self.literal = literal or style in ("heading", "heading2", "note", "header", "unit")


class Layout:
    """Where every block, row and cell of the spec lands. Pure; no API."""

    def __init__(self, spec: dict):
        self.spec = spec
        self.errors: list[str] = []
        self.cells: dict[str, dict[tuple[int, int], Cell]] = {}
        self.widths: dict[str, list[int]] = {}
        self.inputs: dict[str, tuple[str, int, int]] = {}   # id -> (sheet, row, col)
        self.rows: dict[str, dict] = {}     # table-row id -> {sheet, row, c0, c1, table, headers}
        self.tables: dict[str, dict] = {}   # table id -> {sheet, hdr_row, c0, c1, headers, rows: [ids]}
        self.grids: dict[str, dict] = {}    # grid id -> {sheet, r0, c0, nrows, ncols}
        self.names: dict[str, str] = {}     # named range -> A1 range
        self.max_col: dict[str, int] = {}
        self.charts: list[dict] = []
        self._place()
        if not self.errors:
            self._resolve()
            self._check_charts()

    # -- pass 1: positions --
    def _place(self) -> None:
        spec = self.spec
        if not spec.get("title"):
            self.errors.append(t("title is missing"))
        sheets = spec.get("sheets")
        if not isinstance(sheets, list) or not sheets:
            self.errors.append(t("sheets is empty"))
            return
        seen_sheets: set[str] = set()
        seen_ids: set[str] = set()

        def claim(ident, where):
            if not isinstance(ident, str) or not ident:
                self.errors.append(t("{where}: id is missing", where=where))
                return False
            if ident in seen_ids:
                self.errors.append(t("{where}: duplicate id '{id}'", where=where, id=ident))
                return False
            if not _NAME_RE.match(ident) or _CELLISH_RE.match(ident):
                self.errors.append(t(
                    "{where}: id '{id}' cannot be a named range (use letters, "
                    "digits and _, start with a letter, and avoid cell-like names "
                    "such as Q1 or R2C3)", where=where, id=ident))
                return False
            seen_ids.add(ident)
            return True

        for si, sheet in enumerate(sheets):
            where = f"sheets[{si}]"
            name = sheet.get("name")
            if not name:
                self.errors.append(t("{where}: name is missing", where=where))
                continue
            if name in seen_sheets or name == META_SHEET:
                self.errors.append(t("{where}: duplicate or reserved sheet name '{name}'",
                                    where=where, name=name))
                continue
            seen_sheets.add(name)
            cells: dict[tuple[int, int], Cell] = {}
            self.cells[name] = cells
            self.max_col[name] = 3
            r = 0
            for bi, block in enumerate(sheet.get("blocks") or []):
                bw = f"{where}.blocks[{bi}]"
                kind = block.get("type")
                if kind == "heading":
                    cells[(r, 0)] = Cell(block.get("text", ""), style="heading")
                    r += 1
                elif kind == "note":
                    cells[(r, 0)] = Cell(block.get("text", ""), style="note")
                    r += 1
                elif kind == "inputs":
                    if block.get("title"):
                        for c, v in enumerate((block["title"], "単位", "値", "備考")):
                            cells[(r, c)] = Cell(v, style="header")
                        r += 1
                    for ri, row in enumerate(block.get("rows") or []):
                        rw = f"{bw}.rows[{ri}]"
                        if not claim(row.get("id"), rw):
                            continue
                        if ("value" in row) == ("formula" in row):
                            self.errors.append(t("{where}: give exactly one of value / formula", where=rw))
                            continue
                        cells[(r, 0)] = Cell(row.get("label", row["id"]), literal=True,
                                             style="total" if row.get("style") == "total" else None)
                        cells[(r, 1)] = Cell(row.get("unit", ""), style="unit")
                        is_input = "value" in row
                        value = row["value"] if is_input else row["formula"]
                        if value == "?":
                            value = None
                        cells[(r, 2)] = Cell(value,
                                             fmt=row.get("format") or (
                                                 None if isinstance(value, str)
                                                 and not value.startswith("=") else "int"),
                                             is_input=is_input,
                                             key=row["id"], choices=row.get("choices"),
                                             style="total" if row.get("style") == "total" else None)
                        if row.get("note"):
                            cells[(r, 3)] = Cell(row["note"], style="note")
                        self.inputs[row["id"]] = (name, r, 2)
                        self.names[row["id"]] = a1(name, r, 2, absolute=True)
                        r += 1
                elif kind == "table":
                    cols = block.get("columns") or []
                    if not cols:
                        self.errors.append(t("{where}: columns is empty", where=bw))
                        continue
                    headers = [c if isinstance(c, str) else c.get("header", "") for c in cols]
                    if len(set(headers)) != len(headers):
                        self.errors.append(t("{where}: column headers must be unique", where=bw))
                    tid = block.get("id")
                    if tid is not None and not claim(tid, bw):
                        continue
                    c0, c1 = 2, 2 + len(cols) - 1
                    self.max_col[name] = max(self.max_col[name], c1 + 1)
                    cells[(r, 0)] = Cell(block.get("title", ""), style="header")
                    cells[(r, 1)] = Cell("単位", style="header")
                    for j, h in enumerate(headers):
                        cells[(r, c0 + j)] = Cell(h, style="header")
                    hdr_row = r
                    r += 1
                    row_ids = []
                    for ri, row in enumerate(block.get("rows") or []):
                        rw = f"{bw}.rows[{ri}]"
                        rid = row.get("id")
                        if rid is not None and not claim(rid, rw):
                            continue
                        vals = row.get("values")
                        if vals is not None and len(vals) != len(cols):
                            self.errors.append(t(
                                "{where}: {got} values do not match the {want} columns",
                                where=rw, got=len(vals), want=len(cols)))
                            continue
                        style = row.get("style")
                        cells[(r, 0)] = Cell(row.get("label", rid or ""), literal=True,
                                             style="total" if style == "total" else
                                             ("section" if style == "section" else None))
                        cells[(r, 1)] = Cell(row.get("unit", ""), style="unit")
                        if style != "section":
                            for j, col in enumerate(cols):
                                v = vals[j] if vals is not None else None
                                col_formula = None if isinstance(col, str) else col.get("formula")
                                col_fmt = None if isinstance(col, str) else col.get("format")
                                if v == "":
                                    continue
                                if v == "?":
                                    value, is_input = None, True
                                elif v is not None:
                                    value, is_input = v, not (isinstance(v, str) and v.startswith("="))
                                elif col_formula:
                                    value, is_input = col_formula, False
                                elif row.get("formula"):
                                    value, is_input = row["formula"], False
                                else:
                                    continue
                                key = f"{rid}|{headers[j]}" if rid else None
                                cells[(r, c0 + j)] = Cell(
                                    value, fmt=row.get("format") or col_fmt or "int",
                                    is_input=is_input and key is not None, key=key,
                                    style="total" if style == "total" else None)
                        if rid:
                            row_ids.append(rid)
                            self.rows[rid] = {"sheet": name, "row": r, "c0": c0, "c1": c1,
                                              "headers": headers, "table": tid}
                            self.names[rid] = a1_range(name, r, c0, r, c1)
                        r += 1
                    if tid:
                        self.tables[tid] = {"sheet": name, "hdr_row": hdr_row, "c0": c0,
                                            "c1": c1, "headers": headers, "rows": row_ids}
                elif kind == "grid":
                    gid = block.get("id")
                    if not claim(gid, bw):
                        continue
                    header = block.get("header") or []
                    body = block.get("cells") or []
                    if not header:
                        self.errors.append(t("{where}: header is empty", where=bw))
                        continue
                    nrows = block.get("rows", len(body))
                    if block.get("title"):
                        cells[(r, 0)] = Cell(block["title"], style="heading2")
                        r += 1
                    for j, h in enumerate(header):
                        cells[(r, j)] = Cell(h, style="header")
                    fmts = block.get("formats") or []
                    for i, line in enumerate(body):
                        if len(line) > len(header):
                            self.errors.append(t("{where}: wider than the header",
                                                   where=f"{bw}.cells[{i}]"))
                        for j, v in enumerate(line):
                            if v is None:
                                continue
                            is_input = not (isinstance(v, str) and v.startswith("="))
                            cells[(r + 1 + i, j)] = Cell(
                                v, fmt=fmts[j] if j < len(fmts) else None,
                                is_input=is_input and isinstance(v, (int, float)),
                                key=f"{gid}|{i}|{j}")
                    # Spilled formulas (TRANSPOSE, ARRAYFORMULA) fill the rows
                    # below without a cell of their own; give them their format
                    for i in range(len(body), nrows):
                        for j in range(len(header)):
                            if j < len(fmts) and fmts[j]:
                                cells.setdefault((r + 1 + i, j), Cell(None, fmt=fmts[j]))
                    self.grids[gid] = {"sheet": name, "r0": r, "c0": 0,
                                       "nrows": nrows, "ncols": len(header),
                                       "header": header}
                    self.max_col[name] = max(self.max_col[name], len(header))
                    r += 1 + nrows
                else:
                    self.errors.append(t("{where}: unknown block type '{kind}' "
                                         "(heading / note / inputs / table / grid)",
                                         where=bw, kind=kind))
                    continue
                r += 1  # blank row between blocks
            widths = list(sheet.get("widths") or [])
            ncols = max(self.max_col[name], len(widths))
            default = [LABEL_W, UNIT_W] + [VALUE_W] * max(0, ncols - 2)
            self.widths[name] = widths + default[len(widths):ncols]

    # -- pass 2: placeholders --
    def _resolve(self) -> None:
        for sheet, cells in self.cells.items():
            for (r, c), cell in cells.items():
                if isinstance(cell.value, str) and cell.value.startswith("=") \
                        and not cell.literal:
                    try:
                        cell.value = self.resolve(cell.value, sheet, r, c)
                    except ValueError as e:
                        self.errors.append(f"{sheet}!{col_letter(c)}{r + 1}: {e}")

    def _row_ctx(self, sheet: str, r: int) -> dict | None:
        for info in self.rows.values():
            if info["sheet"] == sheet and info["row"] == r:
                return info
        return None

    def resolve(self, formula: str, sheet: str, r: int, c: int) -> str:
        ctx = self._row_ctx(sheet, r)

        def sub(m):
            tok = m.group(1)
            if tok == "col":
                return col_letter(c)
            if tok == "row":
                return str(r + 1)
            if tok == "prev":
                if c == 0:
                    raise ValueError(t("{ph} used in column A", ph="{prev}"))
                return col_letter(c - 1)
            if tok in ("first", "last"):
                if not ctx:
                    raise ValueError(t("{ph} is only usable inside a table row", ph="{" + tok + "}"))
                return col_letter(ctx["c0"] if tok == "first" else ctx["c1"])
            if tok.startswith("@"):
                ref, _, header = tok[1:].partition(":")
                if ref in self.inputs:
                    if header:
                        raise ValueError(t("'{id}' is an input; it has no columns", id=ref))
                    s, rr, cc = self.inputs[ref]
                    return a1(s, rr, cc, absolute=True)
                if ref in self.rows:
                    info = self.rows[ref]
                    if header == "<":
                        # the previous column of the current one
                        if not ctx or not ctx["c0"] < c <= ctx["c1"]:
                            raise ValueError(t("{ph} needs a previous column in this table",
                                             ph="{@" + ref + ":<}"))
                        hdr = ctx["headers"][c - ctx["c0"] - 1]
                        if hdr not in info["headers"]:
                            raise ValueError(t("row '{id}' has no column '{col}'", id=ref, col=hdr))
                        cc = info["c0"] + info["headers"].index(hdr)
                    elif header:
                        if header not in info["headers"]:
                            raise ValueError(t("row '{id}' has no column '{col}' (columns: {cols})",
                                               id=ref, col=header, cols=info["headers"]))
                        cc = info["c0"] + info["headers"].index(header)
                    else:
                        if not ctx:
                            raise ValueError(t("{ph} needs a column; outside a table write {alt}",
                                               ph="{@" + ref + "}", alt="{@" + ref + ":HEADER}"))
                        hdr = ctx["headers"][c - ctx["c0"]] if ctx["c0"] <= c <= ctx["c1"] else None
                        if hdr not in info["headers"]:
                            raise ValueError(t("row '{id}' has no column '{col}'; the tables "
                                               "do not share this column", id=ref, col=hdr))
                        cc = info["c0"] + info["headers"].index(hdr)
                    return a1(info["sheet"], info["row"], cc)
                raise ValueError(t("unknown id '{id}'", id=ref))
            if tok.startswith("range:"):
                ref = tok[6:]
                if ".." in ref:
                    a, b = ref.split("..", 1)
                    if a not in self.rows or b not in self.rows:
                        raise ValueError(t("unknown row in '{ref}'", ref=ref))
                    ia, ib = self.rows[a], self.rows[b]
                    if ia["sheet"] != ib["sheet"] or ia["table"] != ib["table"] or ia["table"] is None:
                        raise ValueError(t("'{ref}': both rows must be in the same table with an id", ref=ref))
                    return a1_range(ia["sheet"], ia["row"], ia["c0"], ib["row"], ib["c1"])
                if ref in self.rows:
                    info = self.rows[ref]
                    return a1_range(info["sheet"], info["row"], info["c0"], info["row"], info["c1"])
                if ref in self.grids:
                    g = self.grids[ref]
                    return a1_range(g["sheet"], g["r0"] + 1, 0, g["r0"] + g["nrows"], g["ncols"] - 1)
                raise ValueError(t("unknown row '{id}'", id=ref))
            if tok.startswith("hdr:"):
                ref = tok[4:]
                if ref not in self.tables:
                    raise ValueError(t("unknown table '{id}'", id=ref))
                tb = self.tables[ref]
                return a1_range(tb["sheet"], tb["hdr_row"], tb["c0"], tb["hdr_row"], tb["c1"])
            raise ValueError(t("unknown placeholder {ph}", ph="{" + tok + "}"))

        return _PH_RE.sub(sub, formula)

    # -- charts --
    def _check_charts(self) -> None:
        seen = set()
        for i, ch in enumerate(self.spec.get("charts") or []):
            where = f"charts[{i}]"
            cid = ch.get("id")
            if not cid or cid in seen:
                self.errors.append(t("{where}: id missing or duplicated", where=where))
                continue
            seen.add(cid)
            if ch.get("sheet") not in self.cells:
                self.errors.append(t("{where}: unknown sheet '{name}'", where=where,
                                     name=ch.get("sheet")))
                continue
            if ch.get("data") not in self.grids:
                self.errors.append(t("{where}: data must name a grid (got '{got}')", where=where,
                                     got=ch.get("data")))
                continue
            kind = ch.get("type", "COLUMN")
            if kind not in CHART_TYPES:
                self.errors.append(t("{where}: unknown type '{kind}' ({allowed})", where=where,
                                     kind=kind, allowed="/".join(CHART_TYPES)))
                continue
            g = self.grids[ch["data"]]
            st = ch.get("seriesTypes")
            if kind == "COMBO" and (not st or len(st) != g["ncols"] - 1):
                self.errors.append(t("{where}: COMBO needs seriesTypes for each of the "
                                     "{n} series", where=where, n=g["ncols"] - 1))
                continue
            if ch.get("legend") and ch["legend"] not in LEGENDS:
                self.errors.append(t("{where}: legend must be one of {allowed}", where=where,
                                     allowed=sorted(LEGENDS)))
                continue
            size = ch.get("size", [6.0, 3.4])
            if not (isinstance(size, list) and len(size) == 2):
                self.errors.append(t("{where}: size must be [w, h] in inches", where=where))
                continue
            self.charts.append(ch)

    def stats(self) -> tuple[int, int]:
        n_in = n_f = 0
        for cells in self.cells.values():
            for cell in cells.values():
                if cell.is_input:
                    n_in += 1
                elif isinstance(cell.value, str) and cell.value.startswith("=") \
                        and not cell.literal:
                    n_f += 1
        return n_in, n_f

    def input_cells(self) -> dict[str, str]:
        """key -> A1 for every input cell (used to keep them across rebuilds)."""
        out = {}
        for sheet, cells in self.cells.items():
            for (r, c), cell in cells.items():
                if cell.is_input and cell.key:
                    out[cell.key] = a1(sheet, r, c)
        return out


def validate(spec: dict) -> tuple[Layout, list[str]]:
    lay = Layout(spec)
    return lay, lay.errors


# ---------- Requests ----------

def _grid_range(sheet_id: int, r0: int, c0: int, r1: int, c1: int) -> dict:
    """Inclusive 0-based bounds -> GridRange (end-exclusive)."""
    return {"sheetId": sheet_id, "startRowIndex": r0, "endRowIndex": r1 + 1,
            "startColumnIndex": c0, "endColumnIndex": c1 + 1}


def _cell_format(cell: Cell) -> tuple[dict, list[str]]:
    fmt: dict = {}
    fields: list[str] = []
    text: dict = {}
    style = cell.style
    if style == "header":
        fmt["backgroundColor"] = _hex_color(HEADER_FILL)
        text.update(bold=True, foregroundColor=_hex_color("FFFFFF"))
        fmt["horizontalAlignment"] = "CENTER"
    elif style == "heading":
        text.update(bold=True, fontSize=14)
    elif style == "heading2":
        text.update(bold=True, fontSize=11)
    elif style == "note":
        text.update(foregroundColor=_hex_color(NOTE_COLOR), fontSize=9)
    elif style == "unit":
        text.update(foregroundColor=_hex_color(NOTE_COLOR))
        fmt["horizontalAlignment"] = "CENTER"
    elif style == "total":
        text.update(bold=True)
        fmt["backgroundColor"] = _hex_color(TOTAL_FILL)
    elif style == "section":
        text.update(bold=True)
    if cell.is_input:
        fmt["backgroundColor"] = _hex_color(INPUT_FILL)
        text["foregroundColor"] = _hex_color(INPUT_FONT)
    pattern = number_format(cell.fmt)
    if pattern and pattern != "@":
        fmt["numberFormat"] = {"type": "NUMBER", "pattern": pattern}
    elif pattern == "@":
        fmt["numberFormat"] = {"type": "TEXT"}
    if text:
        fmt["textFormat"] = text
    for k in fmt:
        fields.append(f"userEnteredFormat.{k}")
    return fmt, fields


def _user_value(value, literal: bool = False) -> dict:
    if value is None:
        return {}
    if isinstance(value, bool):
        return {"boolValue": value}
    if isinstance(value, (int, float)):
        return {"numberValue": value}
    s = str(value)
    if s.startswith("=") and not literal:
        return {"formulaValue": s}
    return {"stringValue": s}


def cell_requests(lay: Layout, sheet_ids: dict[str, int],
                  overrides: dict[str, object]) -> list[dict]:
    """updateCells requests that write every value and format, row by row."""
    reqs: list[dict] = []
    for sheet, cells in lay.cells.items():
        sid = sheet_ids[sheet]
        by_row: dict[int, dict[int, Cell]] = {}
        for (r, c), cell in cells.items():
            by_row.setdefault(r, {})[c] = cell
        for r in sorted(by_row):
            row = by_row[r]
            for c in sorted(row):
                cell = row[c]
                value = overrides.get(cell.key, cell.value) if cell.is_input else cell.value
                data: dict = ({"userEnteredValue": _user_value(value, cell.literal)}
                              if value is not None else {})
                fmt, fields = _cell_format(cell)
                if fmt:
                    data["userEnteredFormat"] = fmt
                if cell.choices:
                    data["dataValidation"] = {
                        "condition": {"type": "ONE_OF_LIST", "values": [
                            {"userEnteredValue": str(v)} for v in cell.choices]},
                        "showCustomUi": True, "strict": True}
                if not data:
                    continue
                f = (["userEnteredValue"] if "userEnteredValue" in data else []) + fields
                if "dataValidation" in data:
                    f.append("dataValidation")
                reqs.append({"updateCells": {
                    "range": _grid_range(sid, r, c, r, c),
                    "rows": [{"values": [data]}],
                    "fields": ",".join(f)}})
    return reqs


def chart_spec(lay: Layout, ch: dict, sheet_ids: dict[str, int]) -> dict:
    g = lay.grids[ch["data"]]
    sid = sheet_ids[g["sheet"]]
    r0, r1 = g["r0"], g["r0"] + g["nrows"]
    kind = ch.get("type", "COLUMN")
    colors = ch.get("colors") or DEFAULT_COLORS
    spec: dict = {"altText": CHART_TAG + ch["id"], "hiddenDimensionStrategy": "SKIP_HIDDEN_ROWS_AND_COLUMNS"}
    if ch.get("title"):
        spec["title"] = ch["title"]
        spec["titleTextFormat"] = {"bold": True, "fontSize": ch.get("titleSize", 12)}
    if ch.get("font"):
        spec["fontName"] = ch["font"]
    domain_src = {"sourceRange": {"sources": [_grid_range(sid, r0, 0, r1, 0)]}}
    legend = LEGENDS[ch.get("legend", "BOTTOM")]
    if kind == "PIE":
        spec["pieChart"] = {
            "legendPosition": legend if legend != "BOTTOM_LEGEND" else "RIGHT_LEGEND",
            "domain": domain_src,
            "series": {"sourceRange": {"sources": [_grid_range(sid, r0, 1, r1, 1)]}},
            "pieHole": ch.get("pieHole", 0.5)}
        return spec
    series = []
    for j in range(1, g["ncols"]):
        s: dict = {"series": {"sourceRange": {"sources": [_grid_range(sid, r0, j, r1, j)]}},
                   "targetAxis": "BOTTOM_AXIS" if kind == "BAR" else "LEFT_AXIS",
                   "colorStyle": {"rgbColor": _hex_color(colors[(j - 1) % len(colors)])}}
        if kind == "COMBO":
            s["type"] = ch["seriesTypes"][j - 1]
        if ch.get("labels"):
            s["dataLabel"] = {"type": "DATA", "textFormat": {"fontSize": ch.get("labelSize", 9)}}
        if kind in ("LINE", "COMBO") and (kind == "LINE" or ch["seriesTypes"][j - 1] == "LINE"):
            s["lineStyle"] = {"width": 3}
            s["pointStyle"] = {"shape": "CIRCLE", "size": 6}
        series.append(s)
    basic: dict = {
        "chartType": kind,
        "legendPosition": legend,
        "headerCount": 1,
        "domains": [{"domain": domain_src}],
        "series": series,
        "axis": [],
    }
    if ch.get("stacked"):
        basic["stackedType"] = "STACKED"
        if ch.get("labels"):
            basic["totalDataLabel"] = {"type": "DATA", "textFormat": {"bold": True}}
    if ch.get("vAxisTitle"):
        basic["axis"].append({"position": "BOTTOM_AXIS" if kind == "BAR" else "LEFT_AXIS",
                              "title": ch["vAxisTitle"]})
    if not basic["axis"]:
        del basic["axis"]
    spec["basicChart"] = basic
    return spec


def chart_position(lay: Layout, ch: dict, sheet_ids: dict[str, int]) -> dict:
    anchor = ch.get("anchor", "H2")
    m = re.match(r"^([A-Z]+)(\d+)$", anchor)
    col = 0
    for chr_ in m.group(1):
        col = col * 26 + (ord(chr_) - 64)
    w, h = ch.get("size", [6.0, 3.4])
    return {"overlayPosition": {
        "anchorCell": {"sheetId": sheet_ids[ch["sheet"]],
                       "rowIndex": int(m.group(2)) - 1, "columnIndex": col - 1},
        "widthPixels": int(w * PX_PER_INCH), "heightPixels": int(h * PX_PER_INCH)}}


# ---------- Build ----------

def _spreadsheet_id(value: str) -> str:
    m = re.search(r"/spreadsheets/d/([A-Za-z0-9_-]+)", value)
    return m.group(1) if m else value


def _find_existing(drive, title: str, folder: str | None) -> str | None:
    import _auth
    import drive_folder
    q = (f"name = '{drive_folder._escape(title)}' and mimeType = '{SPREADSHEET_MIME}' "
         "and trashed = false")
    if folder:
        q += f" and '{_auth.folder_id(folder)}' in parents"
    hits = drive.files().list(q=q, fields="files(id)", pageSize=5,
                              supportsAllDrives=True,
                              includeItemsFromAllDrives=True).execute().get("files", [])
    return hits[0]["id"] if hits else None


def build(lay: Layout, *, into: str | None, folder: str | None,
          reset_inputs: bool) -> str:
    import _auth
    _, drive = _auth.services()
    sheets = _auth.sheets_service()
    spec = lay.spec
    sid = _spreadsheet_id(into) if into else _find_existing(drive, spec["title"], folder)
    created = False
    if not sid:
        body: dict = {"name": spec["title"], "mimeType": SPREADSHEET_MIME}
        if folder:
            body["parents"] = [_auth.folder_id(folder)]
        sid = drive.files().create(body=body, fields="id",
                                   supportsAllDrives=True).execute()["id"]
        created = True
    ss = sheets.spreadsheets()
    meta = ss.get(spreadsheetId=sid, fields=(
        "properties.title,namedRanges,sheets(properties(sheetId,title,index),"
        "charts(chartId,spec(altText)))")).execute()
    present = {s["properties"]["title"]: s for s in meta.get("sheets", [])}

    # Keep what the reader typed: read the old input cells first
    overrides: dict[str, object] = {}
    if META_SHEET in present and not reset_inputs:
        raw = ss.values().get(spreadsheetId=sid, range=f"{META_SHEET}!A1").execute()
        try:
            old = json.loads(raw.get("values", [[""]])[0][0])
        except (ValueError, IndexError):
            old = {}
        old_inputs = old.get("inputs", {})
        keys = [k for k in old_inputs if k in lay.input_cells()]
        if keys:
            got = ss.values().batchGet(
                spreadsheetId=sid, ranges=[old_inputs[k] for k in keys],
                valueRenderOption="FORMULA").execute().get("valueRanges", [])
            for k, vr in zip(keys, got):
                vals = vr.get("values")
                if vals and vals[0]:
                    overrides[k] = vals[0][0]

    # 1. sheets: rename the blank default on a fresh file, add the rest, order them
    reqs: list[dict] = []
    order = [s["name"] for s in spec["sheets"]]
    if created:
        first = meta["sheets"][0]["properties"]
        reqs.append({"updateSheetProperties": {
            "properties": {"sheetId": first["sheetId"], "title": order[0]},
            "fields": "title"}})
        present = {order[0]: {"properties": dict(first, title=order[0])}}
    for name in order + [META_SHEET]:
        if name not in present:
            reqs.append({"addSheet": {"properties": {
                "title": name, "hidden": name == META_SHEET}}})
    if reqs:
        resp = ss.batchUpdate(spreadsheetId=sid, body={"requests": reqs}).execute()
        for rep in resp.get("replies", []):
            if "addSheet" in rep:
                p = rep["addSheet"]["properties"]
                present[p["title"]] = {"properties": p}
    sheet_ids = {name: present[name]["properties"]["sheetId"] for name in present}
    for name in present:
        if name not in order and name != META_SHEET:
            print(t("  note: sheet '{name}' is not in the spec and was left as it is",
                    name=name))

    # 2. clear the managed sheets and named ranges, then write everything
    reqs = []
    for i, name in enumerate(order):
        reqs.append({"updateSheetProperties": {
            "properties": {"sheetId": sheet_ids[name], "index": i},
            "fields": "index"}})
        reqs.append({"updateCells": {"range": {"sheetId": sheet_ids[name]},
                                     "fields": "userEnteredValue,userEnteredFormat,dataValidation,note"}})
        reqs.append({"unmergeCells": {"range": {"sheetId": sheet_ids[name]}}})
    managed = set(lay.names)
    for nr in meta.get("namedRanges", []):
        if nr["name"] in managed:
            reqs.append({"deleteNamedRange": {"namedRangeId": nr["namedRangeId"]}})
    for name, ref in lay.names.items():
        reqs.append({"addNamedRange": {"namedRange": {
            "name": name, "range": _a1_to_grid(ref, sheet_ids)}}})
    reqs += cell_requests(lay, sheet_ids, overrides)
    for name, widths in lay.widths.items():
        for c, w in enumerate(widths):
            reqs.append({"updateDimensionProperties": {
                "range": {"sheetId": sheet_ids[name], "dimension": "COLUMNS",
                          "startIndex": c, "endIndex": c + 1},
                "properties": {"pixelSize": w}, "fields": "pixelSize"}})
    for s in spec["sheets"]:
        fr = s.get("freeze") or [0, 0]
        reqs.append({"updateSheetProperties": {
            "properties": {"sheetId": sheet_ids[s["name"]], "gridProperties": {
                "frozenRowCount": fr[0], "frozenColumnCount": fr[1],
                "hideGridlines": bool(s.get("hideGridlines", False))}},
            "fields": "gridProperties.frozenRowCount,gridProperties.frozenColumnCount,"
                      "gridProperties.hideGridlines"}})
    # the meta sheet remembers where inputs live, for the next rebuild
    meta_json = json.dumps({"version": 1, "inputs": lay.input_cells()}, ensure_ascii=False)
    reqs.append({"updateCells": {
        "range": _grid_range(sheet_ids[META_SHEET], 0, 0, 0, 0),
        "rows": [{"values": [{"userEnteredValue": {"stringValue": meta_json}}]}],
        "fields": "userEnteredValue"}})
    for chunk in _chunks(reqs, 400):
        ss.batchUpdate(spreadsheetId=sid, body={"requests": chunk}).execute()

    # 3. charts: update by id (keeps chartId, so linked slides keep working)
    existing = {}
    for s in meta.get("sheets", []):
        for c in s.get("charts", []) or []:
            alt = (c.get("spec") or {}).get("altText") or ""
            if alt.startswith(CHART_TAG):
                existing[alt[len(CHART_TAG):]] = c["chartId"]
    reqs = []
    for ch in lay.charts:
        cs = chart_spec(lay, ch, sheet_ids)
        pos = chart_position(lay, ch, sheet_ids)
        if ch["id"] in existing:
            cid = existing[ch["id"]]
            reqs.append({"updateChartSpec": {"chartId": cid, "spec": cs}})
            reqs.append({"updateEmbeddedObjectPosition": {
                "objectId": cid, "newPosition": pos,
                "fields": "anchorCell,widthPixels,heightPixels"}})
        else:
            reqs.append({"addChart": {"chart": {"spec": cs, "position": pos}}})
    for cid_name in existing:
        if cid_name not in {c["id"] for c in lay.charts}:
            print(t("  note: chart '{id}' is not in the spec and was left as it is "
                    "(a deck may link to it)", id=cid_name))
    if reqs:
        ss.batchUpdate(spreadsheetId=sid, body={"requests": reqs}).execute()

    changed = {k: v for k, v in overrides.items()
               if k in lay.input_cells() and _input_value(lay, k) != v}
    if changed:
        print(t("  kept {n} input value(s) the reader had changed", n=len(changed)))
    return sid


def _input_value(lay: Layout, key: str):
    for cells in lay.cells.values():
        for cell in cells.values():
            if cell.key == key:
                return cell.value
    return None


def _chunks(items: list, n: int):
    for i in range(0, len(items), n):
        yield items[i:i + n]


def _a1_to_grid(ref: str, sheet_ids: dict[str, int]) -> dict:
    m = re.match(r"^'((?:[^']|'')+)'!\$?([A-Z]+)\$?(\d+)(?::\$?([A-Z]+)\$?(\d+))?$", ref)
    sheet = m.group(1).replace("''", "'")

    def ci(letters):
        n = 0
        for ch in letters:
            n = n * 26 + ord(ch) - 64
        return n - 1
    c0, r0 = ci(m.group(2)), int(m.group(3)) - 1
    c1, r1 = (ci(m.group(4)), int(m.group(5)) - 1) if m.group(4) else (c0, r0)
    return _grid_range(sheet_ids[sheet], r0, c0, r1, c1)


ERROR_VALUES = ("#REF!", "#NAME?", "#DIV/0!", "#VALUE!", "#N/A", "#ERROR!", "#NUM!", "#NULL!")


def check_errors(sid: str, lay: Layout) -> list[str]:
    """Read back every managed sheet's computed values and list formula errors."""
    import _auth
    sheets = _auth.sheets_service()
    names = list(lay.cells)
    got = sheets.spreadsheets().values().batchGet(
        spreadsheetId=sid, ranges=[quote_sheet(n) for n in names],
        valueRenderOption="FORMATTED_VALUE").execute().get("valueRanges", [])
    out = []
    for name, vr in zip(names, got):
        for r, row in enumerate(vr.get("values", [])):
            for c, v in enumerate(row):
                if isinstance(v, str) and v.strip() in ERROR_VALUES:
                    src = lay.cells[name].get((r, c))
                    out.append(f"{name}!{col_letter(c)}{r + 1}: {v}"
                               + (f"  ({src.value})" if src else ""))
    return out


def main() -> int:
    p = argparse.ArgumentParser(
        description=t("Build a planning-model Google Spreadsheet from a JSON spec"))
    p.add_argument("spec", help=t("path to the model spec JSON"))
    p.add_argument("--dry-run", action="store_true",
                   help=t("validate and lay out only (no API calls)"))
    p.add_argument("--folder", help=t("Drive folder URL or ID for a new spreadsheet"))
    p.add_argument("--into", help=t("rebuild this existing spreadsheet (URL or ID) in place"))
    p.add_argument("--reset-inputs", action="store_true",
                   help=t("overwrite input cells with the spec values (default: keep "
                          "what the reader typed)"))
    p.add_argument("--print-layout", action="store_true",
                   help=t("print every cell address the spec resolved to"))
    args = p.parse_args()

    with open(args.spec, encoding="utf-8") as f:
        spec = json.load(f)
    lay, errors = validate(copy.deepcopy(spec))
    if errors:
        print(t("The model spec has problems:"), file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1
    n_in, n_f = lay.stats()
    print(t("Layout OK: {sheets} sheet(s) / {inputs} input cell(s) / {formulas} "
            "formula(s) / {charts} chart(s)", sheets=len(lay.cells), inputs=n_in,
            formulas=n_f, charts=len(lay.charts)))
    if args.print_layout:
        for name, ref in sorted(lay.names.items()):
            print(f"  {name:28s} {ref}")
        for sheet, cells in lay.cells.items():
            for (r, c), cell in sorted(cells.items()):
                if isinstance(cell.value, str) and cell.value.startswith("="):
                    print(f"  {sheet}!{col_letter(c)}{r + 1}  {cell.value}")
    if args.dry_run:
        return 0
    if not (args.folder or args.into):
        # Without a folder the title would be looked up across all of Drive,
        # and a same-named spreadsheet found there would be rebuilt in place
        print(t("ERROR: give --folder (the deck's Drive folder) or --into "
                "<spreadsheet>; a title alone is not a safe target to rebuild"),
              file=sys.stderr)
        return 1

    sid = build(lay, into=args.into, folder=args.folder, reset_inputs=args.reset_inputs)
    errs = check_errors(sid, lay)
    if errs:
        print(t("  formula errors ({n}):", n=len(errs)), file=sys.stderr)
        for e in errs:
            print(f"    {e}", file=sys.stderr)
    else:
        print(t("  formulas: no errors"))
    print(f"  Google Spreadsheet: https://docs.google.com/spreadsheets/d/{sid}/edit")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
