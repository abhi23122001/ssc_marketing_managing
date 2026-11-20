# -*- coding: utf-8 -*-
"""Unit tests for shared AutomationPlanner (dry-run only).

Run from the repository root:
    python3 -m unittest discover -s tests -v
Uses only the Python stdlib.
"""
import csv
import tempfile
import unittest
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import shared.scripts.AutomationPlanner as AP


class TestAutomationPlanner(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp)

    def _write_rules(self, rows):
        p = self.tmp / "rules.csv"
        with p.open("w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=["trigger", "action", "approval_required", "description"])
            w.writeheader()
            for r in rows:
                w.writerow(r)
        return p

    def test_validate_rule_accepts_active_state_change(self):
        p = self._write_rules([
            {"trigger": "daily", "action": "scheduler-run", "approval_required": "yes", "description": "x"},
        ])
        rules = AP.load_rules(p)
        self.assertEqual(len(rules), 1)
        self.assertEqual(AP.validate_rule(rules[0]), [])

    def test_validate_rule_flags_state_change_without_approval(self):
        p = self._write_rules([
            {"trigger": "daily", "action": "report-generate", "approval_required": "no", "description": "x"},
        ])
        rules = AP.load_rules(p)
        warnings = AP.validate_rule(rules[0])
        self.assertTrue(any("requires approval_required=yes" in w for w in warnings))

    def test_validate_rule_accepts_non_state_change(self):
        p = self._write_rules([
            {"trigger": "new", "action": "draft-write", "approval_required": "no", "description": "x"},
        ])
        rules = AP.load_rules(p)
        self.assertEqual(AP.validate_rule(rules[0]), [])


if __name__ == "__main__":
    unittest.main()
