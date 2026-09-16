from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_deck as bd  # noqa: E402


def swot_data() -> dict:
    return {
        "title": "自社の戦略ポジション",
        "quadrants": ["強み: 既存顧客基盤", "弱み: 海外実績",
                      "機会: 規制対応需要", "脅威: 低価格競合"],
        "insight": "規制対応需要に既存顧客基盤を当てるのが最短",
        "source": "2026 年 3 月 経営会議資料",
    }


class ExpansionTest(unittest.TestCase):
    def test_a_template_slide_becomes_a_real_slide(self):
        spec = {"slides": [{"$template": "swot-analysis", "data": swot_data()}]}
        notes, problems = bd.expand_slide_templates(spec)
        self.assertEqual(problems, [])
        self.assertEqual(len(notes), 1)
        slide = spec["slides"][0]
        # validate_spec requires a layout on every slide; that is what the
        # expansion has to supply.
        self.assertIn("layout", slide)
        self.assertNotIn("$template", slide)
        self.assertTrue(slide.get("figures"))

    def test_slides_without_a_template_are_untouched(self):
        plain = {"layout": "CONTENT", "title": "そのまま"}
        spec = {"slides": [plain, {"$template": "swot-analysis", "data": swot_data()}]}
        notes, problems = bd.expand_slide_templates(spec)
        self.assertEqual(problems, [])
        self.assertEqual(len(notes), 1)
        self.assertIs(spec["slides"][0], plain)

    def test_sibling_keys_are_merged_over_the_rendered_slide(self):
        spec = {"slides": [{"$template": "swot-analysis", "data": swot_data(),
                            "notes": "発表者メモ"}]}
        bd.expand_slide_templates(spec)
        self.assertEqual(spec["slides"][0]["notes"], "発表者メモ")

    def test_unknown_template_is_a_problem_not_a_crash(self):
        spec = {"slides": [{"$template": "no-such-template", "data": {}}]}
        notes, problems = bd.expand_slide_templates(spec)
        self.assertEqual(notes, [])
        self.assertEqual(len(problems), 1)
        self.assertIn("no-such-template", problems[0])
        # the offending slide is left in place for the caller to report on
        self.assertIn("$template", spec["slides"][0])

    def test_missing_required_slot_is_reported(self):
        data = swot_data()
        del data["insight"]
        spec = {"slides": [{"$template": "swot-analysis", "data": data}]}
        _, problems = bd.expand_slide_templates(spec)
        self.assertEqual(len(problems), 1)
        self.assertIn("insight", problems[0])

    def test_bad_shapes_are_rejected(self):
        for slide in ({"$template": "", "data": {}},
                      {"$template": "swot-analysis", "data": "not-an-object"}):
            with self.subTest(slide=slide):
                _, problems = bd.expand_slide_templates({"slides": [slide]})
                self.assertEqual(len(problems), 1)

    def test_spec_level_density_is_used_when_the_slide_omits_it(self):
        spec = {"density": "print",
                "slides": [{"$template": "swot-analysis", "data": swot_data()}]}
        _, problems = bd.expand_slide_templates(spec)
        self.assertEqual(problems, [])

    def test_no_slides_array_is_harmless(self):
        self.assertEqual(bd.expand_slide_templates({}), ([], []))


if __name__ == "__main__":
    unittest.main()
