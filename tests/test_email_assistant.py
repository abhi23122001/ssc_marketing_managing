# -*- coding: utf-8 -*-
"""Unit tests for Module 14 email assistant (EmailAssistant).

Run from the repository root:
    python3 -m unittest discover -s tests -v
Uses only the Python stdlib (no pytest dependency).
"""
import importlib.util
import sys
import tempfile
import unittest
from email.message import EmailMessage
from pathlib import Path

def _load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, str(path))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod

_SCRIPT_DIR = Path(__file__).resolve().parent.parent / "modules" / "14-email-assistant" / "scripts"
sys.path.insert(0, str(_SCRIPT_DIR))
EMAIL_ASSISTANT = _load_module("EmailAssistant", _SCRIPT_DIR / "EmailAssistant.py")

import csv  # noqa: E402


class TestClassify(unittest.TestCase):
    def test_ntpc(self):
        s, f, b = "Coal order query", "coal@ntpc.example.com", "we need 5000 tons coal for ntpc project"
        self.assertEqual(EMAIL_ASSISTANT.classify(s, f, b), "NTPC")

    def test_clients(self):
        s, f, b = "Client update", "client@example.com", "progress on your project"
        self.assertEqual(EMAIL_ASSISTANT.classify(s, f, b), "Clients")

    def test_contractors(self):
        s, f, b = "Contractor availability", "survey.contractor@example.com", "available for site work"
        self.assertEqual(EMAIL_ASSISTANT.classify(s, f, b), "Contractors")

    def test_vendors(self):
        s, f, b = "Vendor enquiry", "vendor@example.com", "we supply equipment"
        self.assertEqual(EMAIL_ASSISTANT.classify(s, f, b), "Vendors")

    def test_finance(self):
        s, f, b = "Invoice received", "billing@example.com", "invoice for services"
        self.assertEqual(EMAIL_ASSISTANT.classify(s, f, b), "Finance")

    def test_hr(self):
        s, f, b = "Resume for interview", "hr@example.com", "candidate resume for interview"
        self.assertEqual(EMAIL_ASSISTANT.classify(s, f, b), "HR")

    def test_personal(self):
        s, f, b = "Birthday wishes", "friend@example.com", "happy birthday"
        self.assertEqual(EMAIL_ASSISTANT.classify(s, f, b), "Personal")

    def test_notifications(self):
        s, f, b = "Out of office notice", "no-reply@example.com", "auto reply"
        self.assertEqual(EMAIL_ASSISTANT.classify(s, f, b), "Notifications")


class TestPriority(unittest.TestCase):
    def test_high(self):
        s, f, b = "URGENT: today", "client@example.com", "action required today"
        self.assertEqual(EMAIL_ASSISTANT.priority(s, f, b, "Finance"), "High")

    def test_low_notif(self):
        s, f, b = "Weekly report", "no-reply@example.com", "auto-generated report"
        self.assertEqual(EMAIL_ASSISTANT.priority(s, f, b, "Notifications"), "Low")


class TestFollowUp(unittest.TestCase):
    def test_followup_notes(self):
        recs = EMAIL_ASSISTANT.follow_up_recommendations("x", "y", "z", "HR", "Medium")
        self.assertTrue(any("schedule" in r.lower() or "interview" in r.lower() for r in recs))


class TestSummarize(unittest.TestCase):
    def test_summary_returns_bullets(self):
        out = EMAIL_ASSISTANT.summarize("t", "f", "this is a long body. second sentence. third one.", 3)
        self.assertTrue(all(isinstance(x, str) for x in out))


class TestAnalyze(unittest.TestCase):
    def test_analyze_returns_dict(self):
        res = EMAIL_ASSISTANT.analyze_email("t", "f", "b")
        self.assertIn("category", res)
        self.assertIn("priority", res)
        self.assertIn("summary", res)
        self.assertIn("follow_up", res)
        self.assertIn("bilingual", res)


class TestBilingual(unittest.TestCase):
    def test_bilingual_has_english_and_hinglish(self):
        res = EMAIL_ASSISTANT.analyze_email("t", "f", "b")
        self.assertIn("draft_en", res["bilingual"])
        self.assertIn("draft_hi", res["bilingual"])


class TestParseEmailFile(unittest.TestCase):
    def test_parsest_eml(self):
        msg = EmailMessage()
        msg["Subject"] = "Test email"
        msg["From"] = "sender@example.com"
        msg.set_content("This is a test body.")
        tmp = Path(tempfile.mkdtemp()) / "test.eml"
        tmp.write_bytes(msg.as_bytes())
        subject, frm, body = EMAIL_ASSISTANT.parse_email_file(tmp)
        self.assertEqual(subject, "Test email")
        self.assertEqual(frm, "sender@example.com")
        self.assertIn("test body", body)
        import shutil
        shutil.rmtree(tmp.parent)


if __name__ == "__main__":
    unittest.main()
