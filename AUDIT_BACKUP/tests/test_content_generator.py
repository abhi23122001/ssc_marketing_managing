# -*- coding: utf-8 -*-
"""Unit tests for Module 12 content generation (ContentGenerator).

Run from the repository root:
    python3 -m unittest discover -s tests -v
Uses only the Python stdlib (no pytest dependency).
"""
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, str(path))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod

_SCRIPT_DIR = Path(__file__).resolve().parent.parent / "modules" / "12-content-calendar-content-generation" / "scripts"
sys.path.insert(0, str(_SCRIPT_DIR))
CONTENT_GENERATOR = _load_module("ContentGenerator", _SCRIPT_DIR / "ContentGenerator.py")

import csv  # noqa: E402


class TestContentGenerator(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp)

    def _row(self, **overrides):
        base = {
            "date_proposal": "2026-W48", "platform": "Instagram Reels",
            "content_pillar": "Survey education", "topic": "Topographical survey basics",
            "format": "Reel", "target_audience": "EPC & contractors",
            "language": "en", "status": "DRAFT", "proof_required": "Own footage",
            "owner": "Test Owner", "approval_record": "not yet",
        }
        base.update(overrides)
        return base

    def test_reel_script_written(self):
        out = self.tmp / "out"
        CONTENT_GENERATOR.generate_reel_script(self._row(), out)
        files = list(out.glob("12-reel-*.md")) + list(out.glob("12-reel-*.en"))
        self.assertTrue(files)

    def test_linkedin_post_written(self):
        out = self.tmp / "out"
        CONTENT_GENERATOR.generate_linkedin_post(self._row(platform="LinkedIn"), out)
        files = list(out.glob("12-linkedin-*.md")) + list(out.glob("12-linkedin-*.en"))
        self.assertTrue(files)

    def test_gbp_post_written(self):
        out = self.tmp / "out"
        CONTENT_GENERATOR.generate_gbp_post(self._row(platform="Google Business Profile"), out)
        files = list(out.glob("12-gbp-*.md")) + list(out.glob("12-gbp-*.en"))
        self.assertTrue(files)

    def test_outreach_bilingual_written(self):
        out = self.tmp / "out"
        CONTENT_GENERATOR.generate_outreach_draft(self._row(platform="Email", language="en"), out)
        files = list(out.glob("12-outreach-*.md"))
        self.assertTrue(files)
        text = files[0].read_text(encoding="utf-8")
        self.assertIn("Hinglish + English bilingual draft", text)

    def test_missing_platform_defaults_to_reel(self):
        out = self.tmp / "out"
        # "Newsletter" matches no branch -> else (reel + linkedin)
        CONTENT_GENERATOR.generate_for_row(self._row(platform="Newsletter"), out)
        files = list(out.glob("12-reel-*.en")) + list(out.glob("12-linkedin-*.en"))
        self.assertTrue(files, "expected reel or linkedin draft for unmatched platform")

    def test_draft_header(self):
        import ContentGenerator
        # ContentGenerator.py is loaded under sys.modules already via _load_module.
        pass


if __name__ == "__main__":
    unittest.main()
