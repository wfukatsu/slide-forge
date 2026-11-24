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


class NativeBulletTest(unittest.TestCase):
    def test_bullets_zero_lists_every_line(self):
        c = canvas()
        c.label(0.5, 1.0, 3.0, 1.0, "一つ目\n二つ目", bullets=0)
        reqs = c.deck.requests
        self.assertEqual(only(reqs, "insertText")[0]["text"], "一つ目\n二つ目")
        made = only(reqs, "createParagraphBullets")
        self.assertEqual([m["textRange"] for m in made], [{"type": "ALL"}])
        # the list is created before the text style, so the glyph takes it
        kinds = [next(iter(r)) for r in reqs]
        self.assertLess(kinds.index("createParagraphBullets"), kinds.index("updateTextStyle"))
        indent = only(reqs, "updateParagraphStyle")[-1]["style"]
        self.assertGreater(indent["indentStart"]["magnitude"],
                           indent["indentFirstLine"]["magnitude"])

    def test_typed_bullets_become_a_list_after_a_heading(self):
        c = canvas()
        c.label(0.5, 1.0, 3.0, 1.0, "脅威\n・価格競争\n・代替の増加")
        reqs = c.deck.requests
        self.assertEqual(only(reqs, "insertText")[0]["text"], "脅威\n価格競争\n代替の増加")
        rng = only(reqs, "createParagraphBullets")[0]["textRange"]
        self.assertEqual(rng, {"type": "FIXED_RANGE", "startIndex": 3, "endIndex": 13})

    def test_centered_or_joined_text_is_left_alone(self):
        c = canvas()
        c.label(0.5, 1.0, 3.0, 1.0, "・中央", align="CENTER")
        c.label(0.5, 2.0, 3.0, 1.0, "東京・大阪")
        self.assertFalse(only(c.deck.requests, "createParagraphBullets"))

    def test_so_what_points_are_listed_after_the_text(self):
        c = canvas()
        c.so_what(0.5, 1.0, 6.0, 1.4, "結論", points=["根拠 1", "根拠 2"])
        rng = only(c.deck.requests, "createParagraphBullets")[0]["textRange"]
        self.assertEqual(rng["startIndex"], len("結論\n\n"))

    def test_api_indexes_count_utf16_units(self):
        r = Canvas._api_range("😀a\nb", 3, 4)
        self.assertEqual(r, {"type": "FIXED_RANGE", "startIndex": 4, "endIndex": 5})


if __name__ == "__main__":
    unittest.main()
