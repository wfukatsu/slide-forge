from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_deck as bd  # noqa: E402


def template() -> dict:
    return {
        "name": "test-template",
        "presentationId": "master-id",
        "layouts": {
            "CONTENT": {
                "layoutId": "layout-content",
                "displayName": "Content",
                "placeholders": ["TITLE"],
                "hasPageNumber": False,
                "elements": {},
            }
        },
    }


def spec(count: int = 5) -> dict:
    return {
        "title": "Test deck",
        "slides": [
            {"layout": "CONTENT", "title": f"Page {i + 1}"}
            for i in range(count)
        ],
    }


class SlideSelectionTest(unittest.TestCase):
    def test_parses_one_based_pages_in_given_order(self):
        self.assertEqual([2, 0, 4], bd.parse_slide_selection("3, 1,5", 5))

    def test_rejects_empty_duplicate_invalid_and_out_of_range_values(self):
        for value in ("", "1,1", "0", "6", "two", "1,"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                bd.parse_slide_selection(value, 5)


class PartialRequestTest(unittest.TestCase):
    def test_only_selected_slides_are_created_and_deleted(self):
        deck = bd.TemplateDeck(None, None, "deck-id", template())
        deck.partial_targets = {1: "old-2", 3: "old-4"}

        bd.build_from_spec(deck, spec(), selected_indices=[1, 3])

        creates = [r["createSlide"] for r in deck.requests if "createSlide" in r]
        deletes = [r["deleteObject"]["objectId"] for r in deck.requests
                   if "deleteObject" in r]
        self.assertEqual([1, 3], [r["insertionIndex"] for r in creates])
        self.assertEqual(["old-2", "old-4"], deletes)
        create_positions = [i for i, r in enumerate(deck.requests) if "createSlide" in r]
        delete_positions = [i for i, r in enumerate(deck.requests) if "deleteObject" in r]
        self.assertLess(create_positions[0], delete_positions[0])
        self.assertLess(delete_positions[0], create_positions[1])
        self.assertLess(create_positions[1], delete_positions[1])
        request_text = repr(deck.requests)
        for untouched in ("old-1", "old-3", "old-5"):
            self.assertNotIn(untouched, request_text)

    def test_partial_commit_refuses_to_split_across_batches(self):
        slides = MagicMock()
        deck = bd.TemplateDeck(slides, MagicMock(), "deck-id", template())
        deck.require_single_batch = True
        deck.requests = [{}] * (bd.MAX_REQUESTS_PER_BATCH + 1)

        with self.assertRaisesRegex(ValueError, "atomic batch limit"):
            deck.commit()
        slides.presentations.assert_not_called()

    def test_page_numbers_use_original_positions(self):
        tpl = template()
        layout = tpl["layouts"]["CONTENT"]
        layout["hasPageNumber"] = True
        layout["elements"] = {
            "slideNumber": {"x": 12.0, "y": 7.0, "w": 0.2, "h": 0.2}
        }
        deck = bd.TemplateDeck(None, None, "deck-id", tpl)
        deck._added = [
            {"slideId": "new-2", "layout": layout},
            {"slideId": "new-4", "layout": layout},
        ]

        self.assertEqual(2, deck.add_page_numbers_at([1, 3]))
        texts = [r["insertText"]["text"] for r in deck.requests
                 if "insertText" in r]
        self.assertEqual(["2", "4"], texts)

    def test_notes_and_full_build_regression_are_scoped(self):
        source = spec(3)
        source["slides"][1]["notes"] = "selected note"
        partial = bd.TemplateDeck(None, None, "deck-id", template())
        partial.partial_targets = {1: "old-2"}
        bd.build_from_spec(partial, source, selected_indices=[1])
        self.assertEqual(1, len(partial._notes))
        self.assertEqual("selected note", partial._notes[0][1])

        full = bd.TemplateDeck(None, None, "deck-id", template())
        bd.build_from_spec(full, source)
        self.assertEqual(3, len([r for r in full.requests if "createSlide" in r]))
        self.assertFalse(any("deleteObject" in r for r in full.requests))


class PartialOpenTest(unittest.TestCase):
    def test_master_is_rejected_before_services_are_loaded(self):
        with patch.object(bd._auth, "services",
                          return_value=(MagicMock(), MagicMock())) as services, \
             patch.object(bd._auth, "presentation_id", return_value="master-id"):
            with self.assertRaisesRegex(ValueError, "must never overwrite the master"):
                bd.TemplateDeck.open_partial(
                    template(), "master-url", selected_indices=[0],
                    expected_slide_count=1, layouts=["CONTENT"]
                )
        services.assert_called_once()

    def test_page_count_mismatch_stops_before_any_write(self):
        slides = MagicMock()
        drive = MagicMock()

        def get_presentation(*, presentationId, fields):
            response = MagicMock()
            if fields == "layouts.objectId":
                response.execute.return_value = {
                    "layouts": [{"objectId": "layout-content"}]
                }
            else:
                response.execute.return_value = {
                    "slides": [{"objectId": f"old-{i}"} for i in range(4)]
                }
            return response

        slides.presentations.return_value.get.side_effect = get_presentation
        with patch.object(bd._auth, "services", return_value=(slides, drive)), \
             patch.object(bd._auth, "presentation_id", return_value="deck-id"):
            with self.assertRaisesRegex(ValueError, "live deck has 4 pages"):
                bd.TemplateDeck.open_partial(
                    template(), "deck-url", selected_indices=[1],
                    expected_slide_count=5, layouts=["CONTENT"]
                )

        slides.presentations.return_value.batchUpdate.assert_not_called()
        drive.files.return_value.update.assert_not_called()


if __name__ == "__main__":
    unittest.main()
