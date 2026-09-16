from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import slide_templates as st  # noqa: E402


def template(slide: dict) -> dict:
    """A minimal template whose only slot is the title."""
    return {
        "schemaVersion": 1,
        "id": "t",
        "displayName": "t",
        "pack": "p",
        "category": "c",
        "description": "d",
        "slots": {"title": {"type": "string", "required": True}},
        "slide": slide,
    }


class LabelResourceTest(unittest.TestCase):
    def test_a_label_resolves_in_each_language(self):
        self.assertEqual(st.resolve_label("gap-analysis.as_is", "ja"), "As-Is（現状）")
        self.assertEqual(st.resolve_label("gap-analysis.as_is", "en"), "As-Is (current)")

    def test_a_missing_translation_falls_back_to_the_default_language(self):
        # A language file that has no entry must not blank the slide; the
        # reviewer needs to see the untranslated word to know to fix it.
        self.assertEqual(st.resolve_label("gap-analysis.as_is", "zz"), "As-Is（現状）")

    def test_an_unknown_key_is_an_error(self):
        with self.assertRaises(st.SlideTemplateError):
            st.resolve_label("no.such.key", "ja")


class RenderTest(unittest.TestCase):
    def slide(self):
        return {"layout": "BLANK",
                "title": {"$slot": "title"},
                "headers": [{"$t": "swot-analysis.axis.positive"},
                            {"$t": "swot-analysis.axis.negative"}]}

    def test_labels_render_in_the_requested_language(self):
        out = st.render_template(template(self.slide()), {"title": "x"}, lang="en")
        self.assertEqual(out["headers"], ["Positive", "Negative"])

    def test_the_default_language_is_japanese(self):
        out = st.render_template(template(self.slide()), {"title": "x"})
        self.assertEqual(out["headers"], ["プラス", "マイナス"])

    def test_element_count_is_unchanged_by_the_marker(self):
        # table arity is derived from len(headers); a $t entry must still count
        # as exactly one element.
        out = st.render_template(template(self.slide()), {"title": "x"})
        self.assertEqual(len(out["headers"]), 2)

    def test_slot_references_ignore_label_markers(self):
        self.assertEqual(st.slot_references(self.slide()), {"title"})

    def test_sibling_keys_are_rejected(self):
        slide = {"layout": "BLANK", "title": {"$slot": "title"},
                 "label": {"$t": "gap-analysis.as_is", "size": 10}}
        with self.assertRaises(st.SlideTemplateError):
            st.render_template(template(slide), {"title": "x"})

    def test_a_non_string_key_is_rejected(self):
        slide = {"layout": "BLANK", "title": {"$slot": "title"},
                 "label": {"$t": 3}}
        with self.assertRaises(st.SlideTemplateError):
            st.render_template(template(slide), {"title": "x"})


if __name__ == "__main__":
    unittest.main()
