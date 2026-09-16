from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_deck as bd  # noqa: E402
from diagrams import Canvas  # noqa: E402


def canvas() -> Canvas:
    return Canvas(bd._StubDeck(), "slide", {})


def only(reqs, kind):
    return [r[kind] for r in reqs if kind in r]


class BulletListTest(unittest.TestCase):
    def test_draws_a_native_bulleted_list(self):
        c = canvas()
        bottom = c.bullet_list(0.5, 1.0, 9.0, ["最初の項目", "次の項目"])
        reqs = c.deck.requests
        text = only(reqs, "insertText")[0]["text"]
        self.assertEqual(text, "最初の項目\n次の項目")
        bullets = only(reqs, "createParagraphBullets")
        self.assertEqual(len(bullets), 1)
        self.assertEqual(bullets[0]["bulletPreset"], "BULLET_DISC_CIRCLE_SQUARE")
        self.assertEqual(bullets[0]["textRange"], {"type": "ALL"})
        self.assertGreater(bottom, 1.0)

    def test_numbered_style_and_preset_passthrough(self):
        c = canvas()
        c.bullet_list(0.5, 1.0, 9.0, ["a"], style="numbered")
        self.assertEqual(only(c.deck.requests, "createParagraphBullets")[0]["bulletPreset"],
                         "NUMBERED_DIGIT_ALPHA_ROMAN")
        c = canvas()
        c.bullet_list(0.5, 1.0, 9.0, ["a"], preset="BULLET_CHECKBOX")
        self.assertEqual(only(c.deck.requests, "createParagraphBullets")[0]["bulletPreset"],
                         "BULLET_CHECKBOX")

    def test_nesting_is_sent_as_leading_tabs(self):
        c = canvas()
        c.bullet_list(0.5, 1.0, 9.0, [
            {"text": "親", "items": ["子", {"text": "孫", "level": 2}]},
            "親 2",
        ])
        self.assertEqual(only(c.deck.requests, "insertText")[0]["text"],
                         "親\n\t子\n\t\t孫\n親 2")

    def test_bullets_are_queued_after_the_text(self):
        c = canvas()
        c.bullet_list(0.5, 1.0, 9.0, ["a"])
        kinds = [k for r in c.deck.requests for k in r]
        self.assertLess(kinds.index("insertText"), kinds.index("createParagraphBullets"))
        # The list's own paragraph style is queued last, so it wins over the
        # preset's indents (the shape's line spacing is styled before the text)
        last_para = len(kinds) - 1 - kinds[::-1].index("updateParagraphStyle")
        self.assertGreater(last_para, kinds.index("createParagraphBullets"))

    def test_indents_are_only_sent_when_asked_for(self):
        c = canvas()
        c.bullet_list(0.5, 1.0, 9.0, ["a"])
        style = only(c.deck.requests, "updateParagraphStyle")[-1]["style"]
        self.assertEqual(set(style), {"spaceBelow"})
        c = canvas()
        c.bullet_list(0.5, 1.0, 9.0, ["a"], indent_in=0.25, hanging_in=0.12)
        style = only(c.deck.requests, "updateParagraphStyle")[-1]["style"]
        self.assertAlmostEqual(style["indentStart"]["magnitude"], 18.0)
        self.assertAlmostEqual(style["indentFirstLine"]["magnitude"], 9.36)

    def test_rejects_unusable_input(self):
        for bad in ({"items": []}, {"items": [{"note": "no text"}]},
                    {"items": ["a"], "style": "checklist"},
                    {"items": [{"text": "a", "items": [{"text": "b", "items": [
                        {"text": "c", "items": ["d"]}]}]}]}):
            with self.assertRaises(ValueError):
                canvas().bullet_list(0.5, 1.0, 9.0, **bad)

    def test_spec_figure_type_is_registered(self):
        self.assertIn("list", bd.FIGURES)
        spec = {"slides": [{"layout": "CONTENT", "figures": [
            {"type": "list", "x": 0.5, "y": 1.2, "w": 9.0,
             "items": ["一つ目", "二つ目"], "style": "numbered", "itemGapPt": 4}]}]}
        self.assertEqual(bd.validate_figures(spec, {"widthInches": 10.0,
                                                    "heightInches": 5.625}), [])
        c = canvas()
        bd.draw_figures(c, spec["slides"][0]["figures"])
        self.assertEqual(only(c.deck.requests, "createParagraphBullets")[0]["bulletPreset"],
                         "NUMBERED_DIGIT_ALPHA_ROMAN")


if __name__ == "__main__":
    unittest.main()
