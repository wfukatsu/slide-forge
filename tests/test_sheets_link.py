from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_model as bm  # noqa: E402
import sheets_link as sl  # noqa: E402


MODEL = {
    "title": "model",
    "sheets": [{
        "name": "前提",
        "blocks": [
            {"type": "heading", "text": "前提"},
            {"type": "inputs", "title": "単価", "rows": [
                {"id": "price", "label": "単価", "value": 400, "unit": "万円"},
                {"id": "scenario", "label": "シナリオ", "value": "Base",
                 "choices": ["保守", "Base", "強気"]},
            ]},
        ],
    }, {
        "name": "売上",
        "blocks": [
            {"type": "table", "id": "rev", "title": "売上", "columns": [
                "Q1", "Q2", {"header": "FY", "formula": "=SUM({first}{row}:{prev}{row})"}],
             "rows": [
                {"id": "cnt", "label": "件数", "values": [1, 2, None]},
                {"id": "amount", "label": "売上", "formula": "={@cnt}*{@price}"},
            ]},
            {"type": "inputs", "rows": [
                {"id": "fy_total", "label": "FY 売上", "formula": "={@amount:FY}"}]},
            {"type": "grid", "id": "g", "header": ["期", "売上"],
             "cells": [["=TRANSPOSE({hdr:rev})", "=TRANSPOSE({range:amount})"]],
             "rows": 3},
        ],
    }],
    "charts": [{"id": "c1", "sheet": "売上", "data": "g", "type": "COLUMN"}],
}


class LayoutTest(unittest.TestCase):
    """build_model lays the spec out and resolves placeholders offline."""

    def setUp(self) -> None:
        self.lay = bm.Layout(MODEL)
        self.assertEqual(self.lay.errors, [])

    def cell(self, sheet, ref):
        col = ord(ref[0]) - 65
        return self.lay.cells[sheet][(int(ref[1:]) - 1, col)]

    def test_inputs_land_in_column_c(self):
        self.assertEqual(self.lay.inputs["price"], ("前提", 3, 2))
        self.assertEqual(self.lay.names["price"], "'前提'!$C$4")
        self.assertTrue(self.cell("前提", "C4").is_input)

    def test_row_formula_follows_the_column(self):
        # header row 1, cnt row 2, amount row 3; Q1 in C
        self.assertEqual(self.cell("売上", "C3").value, "='売上'!C2*'前提'!$C$4")
        self.assertEqual(self.cell("売上", "D3").value, "='売上'!D2*'前提'!$C$4")

    def test_column_formula_wins_over_row_formula(self):
        self.assertEqual(self.cell("売上", "E3").value, "=SUM(C3:D3)")
        self.assertEqual(self.cell("売上", "E2").value, "=SUM(C2:D2)")

    def test_header_reference_and_ranges(self):
        self.assertEqual(self.cell("売上", "C5").value, "='売上'!E3")
        self.assertEqual(self.cell("売上", "A8").value, "=TRANSPOSE('売上'!C1:E1)")
        self.assertEqual(self.cell("売上", "B8").value, "=TRANSPOSE('売上'!C3:E3)")
        self.assertEqual(self.lay.grids["g"]["r0"], 6)

    def test_inputs_keep_their_key(self):
        keys = self.lay.input_cells()
        self.assertEqual(keys["cnt|Q2"], "'売上'!D2")
        self.assertNotIn("cnt|FY", keys)

    def test_bad_reference_is_reported(self):
        spec = {"title": "x", "sheets": [{"name": "s", "blocks": [
            {"type": "inputs", "rows": [{"id": "a", "formula": "={@nope}"}]}]}]}
        lay = bm.Layout(spec)
        self.assertTrue(any("unknown id 'nope'" in e for e in lay.errors))

    def test_cell_like_ids_are_rejected(self):
        spec = {"title": "x", "sheets": [{"name": "s", "blocks": [
            {"type": "inputs", "rows": [{"id": "Q1", "value": 1}]}]}]}
        self.assertTrue(bm.Layout(spec).errors)

    def test_chart_spec_uses_grid_columns(self):
        spec = bm.chart_spec(self.lay, self.lay.charts[0], {"前提": 1, "売上": 2})
        basic = spec["basicChart"]
        self.assertEqual(spec["altText"], "sf-chart:c1")
        self.assertEqual(basic["domains"][0]["domain"]["sourceRange"]["sources"][0],
                         {"sheetId": 2, "startRowIndex": 6, "endRowIndex": 10,
                          "startColumnIndex": 0, "endColumnIndex": 1})
        self.assertEqual(len(basic["series"]), 1)


class BindingTest(unittest.TestCase):
    """{{sheet:…}} tokens: substitution, tagging and in-place sync."""

    def test_substitute_and_templates(self):
        spec = {"slides": [{"title": "売上 {{sheet:fy}}"},
                           {"body": ["**{{sheet:fy}}** を目指す", "固定"]},
                           {"figures": [{"type": "table", "headers": ["", "{{sheet:fy}}"],
                                         "rows": [["優先", "1"], ["件数", "{{sheet:n}}"]]}]}]}
        out, per = sl.substitute(spec, {"fy": "1.26億円", "n": "1"},
                                 plain=lambda s: s.replace("**", ""))
        self.assertEqual(out["slides"][0]["title"], "売上 1.26億円")
        self.assertEqual(out["slides"][1]["body"][0], "**1.26億円** を目指す")
        self.assertEqual(per[0], [{"t": "売上 {{sheet:fy}}"}])
        self.assertEqual(per[1], [{"t": "{{sheet:fy}} を目指す"}])
        self.assertEqual(per[2], [{"t": "{{sheet:fy}}", "cell": [0, 0, 1]},
                                  {"t": "{{sheet:n}}", "cell": [0, 2, 1]}])

    def test_table_binding_is_pinned_to_its_cell(self):
        table = {"objectId": "t1", "table": {"tableRows": [
            {"tableCells": [self._cell("優先"), self._cell("人数")]},
            {"tableCells": [self._cell("1"), self._cell("1")]}]}}
        pres = {"slides": [{"objectId": "p1", "pageElements": [
            self._shape("タイトル 1\n"), table]}]}
        reqs, missed = sl.tag_requests(pres, ["p1"], [[{"t": "{{sheet:n}}", "cell": [0, 1, 1]}]],
                                       "SID", {"n": "1"})
        self.assertEqual(missed, [])
        self.assertEqual(len(reqs), 1)
        self.assertEqual(reqs[0]["updatePageElementAltText"]["objectId"], "t1")
        el = dict(table, description=reqs[0]["updatePageElementAltText"]["description"])
        out, _, _, _ = sl.plan_text_updates(el, sl.read_tag(el), {"n": "2"})
        self.assertEqual(out[0]["insertText"]["cellLocation"], {"rowIndex": 1, "columnIndex": 1})

    def test_short_shape_text_needs_an_exact_match(self):
        pres = {"slides": [{"objectId": "p1", "pageElements": [
            self._shape("FY27 は 20% 増\n"), dict(self._shape("20%\n"), objectId="m1")]}]}
        reqs, _ = sl.tag_requests(pres, ["p1"], [[{"t": "{{sheet:r}}"}]], "SID", {"r": "20%"})
        self.assertEqual(reqs[0]["updatePageElementAltText"]["objectId"], "m1")

    @staticmethod
    def _cell(text):
        return {"text": {"textElements": [{"textRun": {"content": text + "\n"}}]}}

    def _shape(self, text):
        return {"objectId": "s1", "shape": {"text": {"textElements": [
            {"textRun": {"content": text}}]}}}

    def test_tag_then_sync_rewrites_only_the_value(self):
        pres = {"slides": [{"objectId": "p1", "pageElements": [
            self._shape("FY27 売上は 1.26億円 (前年比 😀 120%)\n")]}]}
        reqs, missed = sl.tag_requests(
            pres, ["p1"], [[{"t": "FY27 売上は {{sheet:fy}} (前年比 😀 {{sheet:yoy}})"}]],
            "SID", {"fy": "1.26億円", "yoy": "120%"})
        self.assertEqual(missed, [])
        desc = reqs[0]["updatePageElementAltText"]["description"]
        el = dict(pres["slides"][0]["pageElements"][0], description=desc)
        tag = sl.read_tag(el)
        out, changes, new_tag, problems = sl.plan_text_updates(
            el, tag, {"fy": "1.40億円", "yoy": "135%"})
        self.assertEqual(problems, [])
        self.assertCountEqual(changes, [("1.26億円", "1.40億円"), ("120%", "135%")])
        # yoy comes later in the text, so it is rewritten first; 😀 is two UTF-16 units
        ins = [r["insertText"] for r in out if "insertText" in r]
        self.assertEqual(ins[0]["text"], "135%")
        self.assertEqual(ins[0]["insertionIndex"], len("FY27 売上は 1.26億円 (前年比 ") + 2 + 1 + 4)
        self.assertEqual(ins[1]["insertionIndex"], len("FY27 売上は 1.26億円"))
        self.assertEqual(new_tag["b"][0]["v"], {"fy": "1.40億円", "yoy": "135%"})

    def test_edited_text_is_left_alone(self):
        el = self._shape("手で書き換えた\n")
        tag = {"s": "SID", "b": [{"t": "売上 {{sheet:fy}}", "v": {"fy": "1"}}]}
        reqs, changes, _, problems = sl.plan_text_updates(el, tag, {"fy": "2"})
        self.assertEqual((reqs, changes), ([], []))
        self.assertEqual(problems, ["売上 1"])

    def test_table_cells_get_cell_location(self):
        el = {"objectId": "t1", "table": {"tableRows": [{"tableCells": [
            {"text": {"textElements": [{"textRun": {"content": "合計\n"}}]}},
            {"text": {"textElements": [{"textRun": {"content": "5,400\n"}}]}}]}]}}
        tag = {"s": "SID", "b": [{"t": "{{sheet:y1}}", "v": {"y1": "5,400"}}]}
        reqs, _, _, _ = sl.plan_text_updates(el, tag, {"y1": "6,000"})
        self.assertEqual(reqs[0]["insertText"]["cellLocation"],
                         {"rowIndex": 0, "columnIndex": 1})


if __name__ == "__main__":
    unittest.main()
