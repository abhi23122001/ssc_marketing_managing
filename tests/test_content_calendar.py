# -*- coding: utf-8 -*-
"""Unit tests for Module 12 (Content Calendar & Content Generation).

Run from the repository root:
    python3 -m unittest discover -s tests -v
Uses only the Python stdlib (no pytest dependency).
"""
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

# --- Load the module under test (stdlib only) ------------------------------
def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, str(path))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod

_SCRIPT_DIR = Path(__file__).resolve().parent.parent / "modules" / "12-content-calendar-content-generation" / "scripts"
sys.path.insert(0, str(_SCRIPT_DIR))
CONTENT_CALENDAR = _load_module("ContentCalendar", _SCRIPT_DIR / "ContentCalendar.py")
CONTENT_GENERATOR = _load_module("ContentGenerator", _SCRIPT_DIR / "ContentGenerator.py")

import csv  # noqa: E402
import types  # stdlib only (used by TestContentGenerator.generate_all test)


class TestContentCalendarSchema(unittest.TestCase):
    def test_fieldnames_(self):
        expected = {
            "id", "date_proposal", "platform", "content_pillar", "topic",
            "format", "target_audience", "language", "status", "proof_required",
            "owner", "approval_record",
        }
        self.assertEqual(set(CONTENT_CALENDAR.FIELDNAMES), expected)

    def test_id_first(self):
        self.assertEqual(CONTENT_CALENDAR.FIELDNAMES[0], "id")


class TestContentCalendarFunctions(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.path = self.tmp / "test.csv"

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp)

    def test_ensure_header_creates_file(self):
        CONTENT_CALENDAR.ensure_header(self.path, CONTENT_CALENDAR.FIELDNAMES)
        self.assertTrue(self.path.exists())

    def test_load_rows_empty(self):
        self.assertEqual(CONTENT_CALENDAR.load_rows(self.path), [])

    def test_save_load_roundtrip(self):
        rows = [
            {"id": "1", "date_proposal": "2026-W48", "platform": "Instagram Reels",
             "content_pillar": "", "topic": "Survey basics", "format": "Reel",
             "target_audience": "EPC", "language": "en", "status": "DRAFT",
             "proof_required": "Own footage", "owner": "Test", "approval_record": "not yet"},
        ]
        CONTENT_CALENDAR.save_rows(self.path, rows, CONTENT_CALENDAR.FIELDNAMES)
        loaded = CONTENT_CALENDAR.load_rows(self.path)
        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0]["topic"], "Survey basics")

    def test_next_id(self):
        self.assertEqual(CONTENT_CALENDAR.next_id([]), 1)
        self.assertEqual(CONTENT_CALENDAR.next_id([{"id": "1"}, {"id": "2"}]), 3)

    def test_validate_row_required_fields(self):
        row = {"id": "1", "date_proposal": "", "platform": "Instagram Reels",
               "content_pillar": "", "topic": "Survey basics", "format": "Reel",
               "target_audience": "EPC", "language": "en", "status": "DRAFT",
               "proof_required": "Own footage", "owner": "Test", "approval_record": "not yet"}
        issues = CONTENT_CALENDAR.validate_row(row, 1, CONTENT_CALENDAR.FIELDNAMES)
        self.assertTrue(any("date_proposal" in i for i in issues))
        self.assertTrue(any("content_pillar" in i for i in issues))

    def test_validate_row_accepted(self):
        row = {"id": "1", "date_proposal": "2026-W48", "platform": "Instagram Reels",
               "content_pillar": "Survey education", "topic": "Survey basics",
               "format": "Reel", "target_audience": "EPC", "language": "en",
               "status": "DRAFT", "proof_required": "Own footage", "owner": "Test",
               "approval_record": "not yet"}
        issues = CONTENT_CALENDAR.validate_row(row, 1, CONTENT_CALENDAR.FIELDNAMES)
        self.assertEqual(issues, [])


class TestContentGenerator(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp)

    def test_slug(self):
        self.assertEqual(CONTENT_GENERATOR._slug("Topographical survey basics"), "topographical-survey-basics")

    def test_slug_special_chars(self):
        self.assertEqual(CONTENT_GENERATOR._slug("Drone/Photogrammetry!"), "drone-photogrammetry")

    def test_platform_sections_reel(self):
        sections = CONTENT_GENERATOR._platform_sections("Instagram Reels", "en", "Survey basics")
        self.assertIn("hook", sections)
        self.assertIn("caption", sections)
        self.assertIn("cta", sections)

    def test_blog_output_written(self):
        row = {
            "date_proposal": "2026-W48", "platform": "Blog",
            "content_pillar": "Survey education", "topic": "Land survey singrauli",
            "format": "Blog", "target_audience": "EPC",
            "language": "en", "status": "DRAFT", "proof_required": "None",
            "owner": "Test Owner", "approval_record": "not yet",
        }
        out = self.tmp / "out"
        CONTENT_GENERATOR.generate_blog_brief(row, out)
        files = list(out.glob("*.md")) + list(out.glob("*.en"))
        self.assertTrue(files)
        text = files[0].read_text(encoding="utf-8")
        self.assertIn("status: DRAFT", text)
        self.assertIn("approval_required: yes", text)
        self.assertNotIn("Drafted by Hermes Agent", text)

    def test_generate_all_counts(self):
        # Build a temporary calendar with one DRAFT row.
        cal = self.tmp / "calendar.csv"
        with cal.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=CONTENT_CALENDAR.FIELDNAMES, lineterminator="\n")
            writer.writeheader()
            writer.writerow({
                "id": "1", "date_proposal": "2026-W48", "platform": "Instagram Reels",
                "content_pillar": "Survey", "topic": "Topo basics", "format": "Reel",
                "target_audience": "EPC", "language": "en", "status": "DRAFT",
                "proof_required": "Own footage", "owner": "Test", "approval_record": "not yet",
            })
        out = self.tmp / "out"
        class _Args:
            calendar = cal
            outdir = out
        rc = CONTENT_GENERATOR.generate_all(_Args())
        self.assertEqual(rc, 0)
        generated = list(out.glob("*.md")) + list(out.glob("*.en"))
        self.assertEqual(len(generated), 1)


if __name__ == "__main__":
    unittest.main()
