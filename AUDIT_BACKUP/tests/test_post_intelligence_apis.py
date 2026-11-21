# -*- coding: utf-8 -*-
"""Integration tests for Hermes, Internet Research, Studio, Tasks, and Universal Filters."""
import json
import os
import sys
import urllib.request
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from foundation.store import Store
from foundation.auth import issue_token


class TestPostIntelligenceAPIs(unittest.TestCase):
    BASE_URL = "http://127.0.0.1:8899"

    @classmethod
    def setUpClass(cls):
        cls.store = Store()
        cls.token = issue_token(cls.store, "owner")

    def _get(self, path):
        req = urllib.request.Request(
            f"{self.BASE_URL}{path}",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        with urllib.request.urlopen(req, timeout=50) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))

    def _post(self, path, body):
        req = urllib.request.Request(
            f"{self.BASE_URL}{path}",
            headers={"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"},
            data=json.dumps(body).encode("utf-8")
        )
        with urllib.request.urlopen(req, timeout=50) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))

    def test_01_hermes_status(self):
        status, data = self._get("/api/intelligence/hermes/status")
        self.assertEqual(status, 200)
        self.assertTrue(data["installed"])
        self.assertTrue(data["authenticated"])
        self.assertEqual(data["primary_model"], "upstage/solar-mini4:free")
        self.assertTrue(data["zero_paid_billing_enforced"])

    def test_02_hermes_live_query(self):
        status, data = self._post("/api/intelligence/hermes/query", {
            "prompt": "Respond with exactly: HERMES_ORCHESTRATOR_ONLINE"
        })
        self.assertEqual(status, 200)
        self.assertTrue(data["ok"])
        self.assertIn("HERMES_ORCHESTRATOR_ONLINE", data["content"])
        self.assertEqual(data["model_used"], "upstage/solar-mini4:free")

    def test_03_live_internet_research(self):
        status, data = self._post("/api/intelligence/research/live", {
            "query": "DGPS survey tolerances India Survey of India",
            "category": "survey_tech"
        })
        self.assertEqual(status, 200)
        self.assertTrue(data["ok"])
        self.assertGreaterEqual(data["sources_count"], 1)
        self.assertGreaterEqual(len(data["citations"]), 1)
        self.assertGreaterEqual(len(data["facts"]), 1)
        self.assertGreaterEqual(len(data["recommendations"]), 1)

    def test_04_studio_templates_and_projects(self):
        # 1. List templates
        status, data = self._get("/api/studio/templates")
        self.assertEqual(status, 200)
        self.assertGreaterEqual(len(data["templates"]), 2)

        # 2. Save project
        tmpl = data["templates"][0]
        status, p_data = self._post("/api/studio/projects", {
            "title": "API Automated Field Showcase Reel",
            "project_type": "reel_video",
            "aspect_ratio": "9:16",
            "timeline": tmpl["config"]
        })
        self.assertEqual(status, 200)
        pid = p_data["project"]["id"]

        # 3. Get project
        status, g_data = self._get(f"/api/studio/projects/{pid}")
        self.assertEqual(status, 200)
        self.assertEqual(g_data["project"]["title"], "API Automated Field Showcase Reel")

    def test_05_employee_tasks_and_workload(self):
        # 1. Create task
        status, t_data = self._post("/api/tasks", {
            "title": "Live API Inspection Task",
            "description": "Verify sensor leveling on total station.",
            "assigned_to": 2,
            "priority": "high",
            "deadline_date": "2026-11-26"
        })
        self.assertEqual(status, 201)
        tid = t_data["task"]["id"]

        # 2. List tasks
        status, l_data = self._get("/api/tasks?filter_type=my_tasks")
        self.assertEqual(status, 200)
        self.assertIn("tasks", l_data)

        # 3. Workload summary
        status, w_data = self._get("/api/tasks/workload")
        self.assertEqual(status, 200)
        self.assertIn("total_tasks", w_data)
        self.assertIn("employee_performance", w_data)

    def test_06_universal_filters(self):
        # 1. Filtered query
        status, f_data = self._get("/api/filter/tasks?priority=high")
        self.assertEqual(status, 200)
        self.assertTrue(f_data["ok"])
        self.assertIn("pagination", f_data)
        self.assertIn("active_filters", f_data)


if __name__ == "__main__":
    unittest.main()
