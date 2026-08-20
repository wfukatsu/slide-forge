from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_deck as bd  # noqa: E402
import settings  # noqa: E402


class SettingsTest(unittest.TestCase):
    """The switches read from config/settings.json, overridden by the environment."""

    def setUp(self) -> None:
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)
        # A config dir of our own, and neutralized overrides, so neither the
        # developer's real settings.json nor their shell decides whether
        # these tests pass. An empty override is treated as unset.
        env = patch.dict("os.environ", {
            "GSLIDES_CONFIG_DIR": self.dir.name,
            "GSLIDES_IMAGE_GENERATION": "",
            "GSLIDES_OUTPUT": "",
            "GSLIDES_LOCAL_DIR": "",
        })
        env.start()
        self.addCleanup(env.stop)

    def write(self, data: dict) -> None:
        Path(self.dir.name, settings.FILENAME).write_text(
            json.dumps(data), encoding="utf-8")

    # ---------- defaults ----------

    def test_absent_file_keeps_the_previous_behaviour(self):
        self.assertTrue(settings.image_generation_enabled())
        self.assertEqual(settings.output_target(), settings.GOOGLE)

    # ---------- file ----------

    def test_file_switches_both(self):
        self.write({"imageGeneration": "off", "output": "pptx"})
        self.assertFalse(settings.image_generation_enabled())
        self.assertEqual(settings.output_target(), settings.LOCAL)

    def test_save_merges_and_is_read_back(self):
        self.write({"localOutputDir": "~/decks"})
        settings.save({"output": "local"})
        stored = settings.stored()
        self.assertEqual(stored["localOutputDir"], "~/decks")
        self.assertEqual(stored["output"], "local")

    def test_malformed_file_is_reported_not_ignored(self):
        Path(self.dir.name, settings.FILENAME).write_text("{", encoding="utf-8")
        with self.assertRaises(settings.SettingsError):
            settings.load()

    def test_unknown_value_is_rejected(self):
        self.write({"output": "dropbox"})
        with self.assertRaises(settings.SettingsError):
            settings.output_target()

    # ---------- environment / flag precedence ----------

    def test_environment_beats_the_file(self):
        self.write({"imageGeneration": True, "output": "google"})
        with patch.dict("os.environ", {"GSLIDES_IMAGE_GENERATION": "off",
                                       "GSLIDES_OUTPUT": "local"}):
            self.assertFalse(settings.image_generation_enabled())
            self.assertEqual(settings.output_target(), settings.LOCAL)

    def test_cli_override_beats_the_environment(self):
        with patch.dict("os.environ", {"GSLIDES_OUTPUT": "local"}):
            self.assertEqual(settings.output_target("google"), settings.GOOGLE)

    def test_local_dir_is_absolute(self):
        self.write({"localOutputDir": "out/pptx"})
        self.assertTrue(Path(settings.local_output_dir()).is_absolute())
        with patch.dict("os.environ", {"GSLIDES_LOCAL_DIR": "/tmp/decks"}):
            self.assertEqual(settings.local_output_dir(), "/tmp/decks")


class AiImageGateTest(unittest.TestCase):
    """`aiImage` is refused offline when image generation is switched off."""

    SPEC = {
        "title": "t",
        "slides": [{
            "layout": "CONTENT",
            "figures": [{"type": "aiImage", "x": 1, "y": 1, "w": 4, "h": 3,
                         "prompt": "a data flow"}],
        }],
    }
    PAGE = {"widthInches": 10.0, "heightInches": 5.625}

    def test_allowed_when_on(self):
        with patch.object(settings, "image_generation_enabled", return_value=True):
            self.assertEqual(bd.validate_figures(self.SPEC, self.PAGE), [])

    def test_refused_when_off(self):
        with patch.object(settings, "image_generation_enabled", return_value=False):
            problems = bd.validate_figures(self.SPEC, self.PAGE)
        self.assertEqual(len(problems), 1)
        self.assertIn("imageGeneration: off", problems[0])


if __name__ == "__main__":
    unittest.main()
