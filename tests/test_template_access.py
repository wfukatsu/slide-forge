from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from googleapiclient.errors import HttpError

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_template_access as cta  # noqa: E402


class FakeResp:
    def __init__(self, status: int) -> None:
        self.status = status
        self.reason = "fake"


class FakeDrive:
    """Stands in for the Drive client: one canned answer per file ID."""

    def __init__(self, answers: dict) -> None:
        self.answers = answers

    def files(self):
        return self

    def get(self, fileId, **_kwargs):        # noqa: N803 - Drive's parameter name
        answer = self.answers[fileId]
        self.pending = answer
        return self

    def execute(self):
        if isinstance(self.pending, int):
            raise HttpError(FakeResp(self.pending), b"{}")
        return self.pending


class TemplateAccessTest(unittest.TestCase):
    """Whether a registered template can generate, as setup step 5 asks it."""

    def setUp(self) -> None:
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)
        d = patch.object(cta, "TEMPLATE_DIR", Path(self.dir.name))
        d.start()
        self.addCleanup(d.stop)

    def write(self, template_id: str, reg: dict) -> None:
        Path(self.dir.name, f"{template_id}.json").write_text(
            json.dumps(reg), encoding="utf-8")

    def test_create_mode_needs_no_master(self) -> None:
        self.write("blank", {"generationMode": "create"})
        self.assertFalse(cta.needs_drive("blank"))
        r = cta.check_one(None, "blank")
        self.assertTrue(r["ok"])
        self.assertEqual(r["status"], "no-master-needed")

    def test_reachable_master_is_ok(self) -> None:
        self.write("corp", {"generationMode": "copy", "presentationId": "P1"})
        drive = FakeDrive({"P1": {"name": "Corp Master",
                                  "capabilities": {"canCopy": True}}})
        r = cta.check_one(drive, "corp")
        self.assertTrue(r["ok"])
        self.assertEqual(r["masterName"], "Corp Master")

    def test_no_access_is_not_ok(self) -> None:
        """The case setup branches on: someone else's master, so build your own."""
        self.write("corp", {"generationMode": "copy", "presentationId": "P1"})
        for code in (403, 404):
            r = cta.check_one(FakeDrive({"P1": code}), "corp")
            self.assertFalse(r["ok"])
            self.assertEqual(r["status"], "no-access")

    def test_server_error_is_reported_as_unchecked(self) -> None:
        self.write("corp", {"generationMode": "copy", "presentationId": "P1"})
        r = cta.check_one(FakeDrive({"P1": 500}), "corp")
        self.assertEqual(r["status"], "error")
        self.assertFalse(r["ok"])

    def test_visible_but_not_copyable(self) -> None:
        self.write("corp", {"generationMode": "copy", "presentationId": "P1"})
        drive = FakeDrive({"P1": {"name": "Locked",
                                  "capabilities": {"canCopy": False}}})
        r = cta.check_one(drive, "corp")
        self.assertFalse(r["ok"])
        self.assertEqual(r["status"], "no-copy")

    def test_trashed_master(self) -> None:
        self.write("corp", {"generationMode": "copy", "presentationId": "P1"})
        drive = FakeDrive({"P1": {"name": "Gone", "trashed": True,
                                  "capabilities": {"canCopy": True}}})
        self.assertEqual(cta.check_one(drive, "corp")["status"], "trashed")

    def test_copy_template_without_a_presentation_id(self) -> None:
        self.write("half", {"generationMode": "copy"})
        self.assertFalse(cta.needs_drive("half"))
        r = cta.check_one(None, "half")
        self.assertEqual(r["status"], "unregistered")
        self.assertFalse(r["ok"])


if __name__ == "__main__":
    unittest.main()
