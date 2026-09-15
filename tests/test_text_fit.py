from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import _text  # noqa: E402
import build_deck as bd  # noqa: E402
from diagrams import Canvas  # noqa: E402


def need_for(text: str, w: float, ls: float = 100):
    return lambda s, i: _text.text_height(text, w, s, line_spacing=ls, inset=i)


class FitBoxTest(unittest.TestCase):
    def test_text_that_fits_is_unchanged(self):
        fit = _text.fit_box(need_for("あ" * 5, 2.0), 0.3, 11, slack=0.04)
        self.assertEqual(fit, _text.Fit(11, 0.10, True))

    def test_margin_is_tightened_before_the_font(self):
        # 11.5 em wraps at the default 0.10in margin and fits at 0.07in
        fit = _text.fit_box(need_for("あ" * 11 + "a", 2.0), 0.3, 11, slack=0.04)
        self.assertEqual(fit.size, 11)
        self.assertAlmostEqual(fit.inset, 0.07)
        self.assertTrue(fit.fits)

    def test_a_line_that_exactly_fills_the_column_wraps(self):
        # 2.6in at 12pt is 15.0 em by the formula; Slides wraps the 15th
        self.assertEqual(_text.wrapped_lines("あ" * 14, 2.5, 12), 1)
        self.assertEqual(_text.wrapped_lines("あ" * 15, 2.5, 12), 2)

    def test_font_shrinks_once_the_margin_is_not_enough(self):
        fit = _text.fit_box(need_for("あ" * 13, 2.0), 0.3, 11, slack=0.04)
        self.assertEqual(fit.size, 10)
        self.assertAlmostEqual(fit.inset, 0.04)
        self.assertTrue(fit.fits)

    def test_gives_up_at_the_floor(self):
        fit = _text.fit_box(need_for("あ" * 40, 2.0), 0.3, 11, slack=0.04)
        self.assertEqual(fit, _text.Fit(8.0, 0.03, False))

    def test_explicit_floor(self):
        fit = _text.fit_box(need_for("あ" * 40, 2.0), 0.3, 11, min_size=10,
                            slack=0.04)
        self.assertEqual(fit.size, 10)
        self.assertFalse(fit.fits)

    def test_grow_keeps_the_anchored_edge(self):
        self.assertEqual(_text.grow_box(1.0, 0.3, 0.5, "TOP"), (1.0, 0.5))
        self.assertAlmostEqual(_text.grow_box(1.0, 0.3, 0.5, "MIDDLE")[0], 0.9)
        self.assertAlmostEqual(_text.grow_box(1.0, 0.3, 0.5, "BOTTOM")[0], 0.8)
        self.assertEqual(_text.grow_box(1.0, 0.6, 0.5, "MIDDLE"), (1.0, 0.6))


def requests_for(reqs, kind, oid):
    return [r[kind] for r in reqs if kind in r and r[kind].get("objectId") == oid]


class CanvasFitTest(unittest.TestCase):
    def setUp(self):
        self.canvas = Canvas(bd._StubDeck(), "slide", {})

    def test_shrink_emits_the_fitted_size_and_margin(self):
        oid = self.canvas.shape(0, 0, 2.0, 0.3, text="あ" * 13, size=11)
        reqs = self.canvas.deck.requests
        style = requests_for(reqs, "updateTextStyle", oid)[0]["style"]
        self.assertEqual(style["fontSize"]["magnitude"], 10)
        para = requests_for(reqs, "updateParagraphStyle", oid)[0]["style"]
        self.assertAlmostEqual(para["indentStart"]["magnitude"], -4.32)
        props = requests_for(reqs, "updateShapeProperties", oid)[0]
        self.assertEqual(props["shapeProperties"]["autofit"],
                         {"autofitType": "NONE"})
        self.assertEqual(self.canvas.texts[oid]["size"], 10)
        self.assertEqual(len(self.canvas.fit_notes), 1)
        self.assertEqual(self.canvas.audit_text_fit(), [])

    def test_text_that_fits_draws_as_before(self):
        oid = self.canvas.shape(0, 0, 2.0, 0.3, text="あ" * 5, size=11)
        reqs = self.canvas.deck.requests
        self.assertEqual(requests_for(reqs, "updateParagraphStyle", oid), [])
        self.assertEqual(self.canvas.fit_notes, [])

    def test_grow_heightens_the_box_around_its_middle(self):
        oid = self.canvas.shape(0, 1.0, 2.0, 0.3, text="あ" * 20, size=11,
                                text_fit="grow")
        x, y, w, h, _ = self.canvas.rects[oid]
        need = _text.text_height("あ" * 20, 2.0, 11)
        self.assertAlmostEqual(h, need)
        self.assertAlmostEqual(y, 1.0 - (need - 0.3) / 2)
        self.assertEqual(self.canvas.texts[oid]["size"], 11)

    def test_none_leaves_the_overflow_to_the_audit(self):
        self.canvas.text_fit = "none"
        self.canvas.shape(0, 0, 2.0, 0.3, text="あ" * 20, size=11)
        self.assertEqual(self.canvas.fit_notes, [])
        self.assertEqual(len(self.canvas.audit_text_fit()), 1)

    def test_unknown_mode_is_rejected(self):
        with self.assertRaises(ValueError):
            self.canvas.shape(0, 0, 2.0, 0.3, text="x", text_fit="squash")


def template() -> dict:
    return {
        "name": "fit-template",
        "presentationId": "master-id",
        "layouts": {
            "CONTENT": {
                "layoutId": "layout-content",
                "displayName": "Content",
                "placeholders": ["TITLE", "BODY"],
                "hasPageNumber": False,
                "elements": {"title": {"x": 0.5, "y": 0.3, "w": 4.0, "h": 0.6},
                             "body": {"x": 0.5, "y": 1.0, "w": 4.0, "h": 1.0}},
                "textStyles": {"title": {"fontSize": 24},
                               "body": {"fontSize": 14}},
            }
        },
    }


class SlotFitTest(unittest.TestCase):
    LONG_TITLE = "あ" * 30

    def test_add_slide_fits_an_overflowing_title(self):
        deck = bd.TemplateDeck(MagicMock(), MagicMock(), "deck", template())
        ref = deck.add_slide("CONTENT", title=self.LONG_TITLE, body=["短い本文"])
        title_id = ref["placeholders"]["TITLE"]
        body_id = ref["placeholders"]["BODY"]
        fit, base = bd.fit_slot(template()["layouts"]["CONTENT"], "TITLE",
                                self.LONG_TITLE)
        self.assertLess(fit.size, base)
        sizes = [r["style"]["fontSize"]["magnitude"]
                 for r in requests_for(deck.requests, "updateTextStyle", title_id)]
        self.assertEqual(sizes, [fit.size])
        # A placeholder keeps its left indent (bullets); only the right edge moves
        for r in requests_for(deck.requests, "updateParagraphStyle", title_id):
            self.assertEqual(set(r["style"]), {"indentEnd"})
        for oid in (title_id, body_id):
            self.assertEqual(
                len(requests_for(deck.requests, "updateShapeProperties", oid)), 1)
        self.assertEqual(requests_for(deck.requests, "updateTextStyle", body_id), [])
        self.assertEqual(len(ref["fitNotes"]), 1)

    def test_unfittable_slot_becomes_a_warning(self):
        deck = bd.TemplateDeck(MagicMock(), MagicMock(), "deck", template())
        ref = deck.add_slide("CONTENT", title="あ" * 80, min_font_size=22)
        self.assertEqual(ref["fitNotes"], [])
        self.assertEqual(len(ref["fitWarnings"]), 1)

    def test_role_sizes_shrink_with_the_body(self):
        tpl = template()
        tpl["bodyRoles"] = {"big": {"fontSize": 20}}
        deck = bd.TemplateDeck(MagicMock(), MagicMock(), "deck", tpl)
        body = [{"text": "大見出し", "role": "big"}] + ["あ" * 40] * 4
        ref = deck.add_slide("CONTENT", body=body)
        body_id = ref["placeholders"]["BODY"]
        sizes = [r["style"]["fontSize"]["magnitude"]
                 for r in requests_for(deck.requests, "updateTextStyle", body_id)]
        self.assertEqual(len(sizes), 2)
        base, role = sizes
        self.assertLess(base, 14)
        self.assertEqual(role, round(20 * base / 14 * 2) / 2)

    def test_audit_notes_what_fitting_fixes(self):
        spec = {"slides": [{"layout": "CONTENT", "title": self.LONG_TITLE}]}
        notes: list[str] = []
        self.assertEqual(bd.audit_body_fit(template(), spec, notes), [])
        self.assertEqual(len(notes), 1)

    def test_audit_reports_what_fitting_cannot_fix(self):
        spec = {"defaults": {"textFit": "none"},
                "slides": [{"layout": "CONTENT", "title": self.LONG_TITLE}]}
        self.assertEqual(len(bd.audit_body_fit(template(), spec)), 1)
        spec = {"defaults": {"minFontSize": 23},
                "slides": [{"layout": "CONTENT", "title": self.LONG_TITLE}]}
        self.assertEqual(len(bd.audit_body_fit(template(), spec)), 1)

    def test_spec_values_are_validated(self):
        spec = {"defaults": {"textFit": "squash"},
                "slides": [{"layout": "CONTENT", "minFontSize": -1}]}
        problems = bd.validate_figures(spec, {}, template())
        self.assertEqual(len(problems), 2)


class InheritedStyleTest(unittest.TestCase):
    PRES = {
        "masters": [{"objectId": "m", "pageElements": [
            {"objectId": "m_body", "shape": {
                "placeholder": {"type": "BODY"},
                "text": {"textElements": [
                    {"paragraphMarker": {"style": {
                        "lineSpacing": 115, "spaceAbove": {"unit": "PT"},
                        "spaceBelow": {"magnitude": 10, "unit": "PT"}}}},
                    {"textRun": {"style": {"fontSize": {"magnitude": 16}}}}]}}},
        ]}],
        "layouts": [{"objectId": "layout-content", "pageElements": [
            {"objectId": "l_body", "shape": {
                "placeholder": {"type": "BODY", "parentObjectId": "m_body"},
                "text": {"textElements": [
                    {"paragraphMarker": {"style": {"direction": "LEFT_TO_RIGHT"}}},
                    {"textRun": {"style": {"fontFamily": "Arial"}}}]}}},
            {"objectId": "l_body1", "shape": {
                "placeholder": {"type": "BODY", "index": 1,
                                "parentObjectId": "m_body"},
                "text": {"textElements": [
                    {"textRun": {"style": {"fontSize": {"magnitude": 12}}}}]}}},
        ]}],
    }

    def test_values_resolve_through_the_master(self):
        styles = bd.inherited_slot_styles(self.PRES)["layout-content"]
        self.assertEqual(styles["body"], {"fontSize": 16, "lineSpacing": 115,
                                          "spaceAbove": 0, "spaceBelow": 10})
        self.assertEqual(styles["body#1"]["fontSize"], 12)
        self.assertEqual(styles["body#1"]["spaceBelow"], 10)

    def test_inherited_spacing_counts_toward_the_fit(self):
        layout = template()["layouts"]["CONTENT"]
        del layout["textStyles"]["body"]
        body = ["あ" * 20] * 4
        self.assertIsNone(bd.fit_slot(layout, "BODY", body, body=True))
        inherited = bd.inherited_slot_styles(self.PRES)["layout-content"]
        fit, base = bd.fit_slot(layout, "BODY", body, body=True,
                                inherited=inherited)
        self.assertEqual(base, 16)
        self.assertLess(fit.size, 16)


if __name__ == "__main__":
    unittest.main()
