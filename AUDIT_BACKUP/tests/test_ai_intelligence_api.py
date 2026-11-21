# -*- coding: utf-8 -*-
"""API endpoint integration tests for Autonomous AI Brain routes (/api/intelligence/...)."""
from __future__ import annotations

import json
import os
import sys
import unittest
import urllib.request
import urllib.parse
from http.client import HTTPResponse

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from foundation.store import Store
from foundation.auth import issue_token


class TestAiIntelligenceAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base_url = "http://127.0.0.1:8899"
        cls.store = Store()
        cls.owner_token = issue_token(cls.store, "owner")
        cls.headers = {
            "Authorization": f"Bearer {cls.owner_token}",
            "Content-Type": "application/json"
        }

    def _req(self, path: str, method: str = "GET", body: dict | None = None) -> dict:
        url = f"{self.base_url}{path}"
        data = json.dumps(body).encode("utf-8") if body is not None else None
        req = urllib.request.Request(url, data=data, headers=self.headers, method=method)
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def test_01_api_ask_anything(self):
        res = self._req("/api/intelligence/ask", method="POST", body={
            "query": "Total operating profit kitna hua hai?",
            "workspace": "SSC"
        })
        self.assertIn("answer", res)
        self.assertEqual(res["answer"]["intent"], "BUSINESS_DATA")

    def test_02_api_research_get_and_run(self):
        res = self._req("/api/intelligence/research?workspace=SSC")
        self.assertIn("research", res)
        self.assertTrue(len(res["research"]) > 0)

        run_res = self._req("/api/intelligence/research/run", method="POST", body={"workspace": "SSC"})
        self.assertIn("research", run_res)

    def test_03_api_marketing_briefs(self):
        res = self._req("/api/intelligence/briefs?workspace=SSC")
        self.assertIn("brief", res)
        self.assertEqual(res["brief"]["workspace_id"], "SSC")

        gen_res = self._req("/api/intelligence/briefs/generate", method="POST", body={"workspace": "INFRA"})
        self.assertIn("brief", gen_res)
        self.assertEqual(gen_res["brief"]["workspace_id"], "INFRA")

    def test_04_api_alerts(self):
        res = self._req("/api/intelligence/alerts?workspace=SSC")
        self.assertIn("alerts", res)

        scan_res = self._req("/api/intelligence/alerts/scan", method="POST", body={"workspace": "SSC"})
        self.assertIn("alerts", scan_res)
        self.assertIn("count", scan_res)

    def test_05_api_reports(self):
        res = self._req("/api/intelligence/reports?workspace=SSC")
        self.assertIn("reports", res)

        gen_res = self._req("/api/intelligence/reports/generate", method="POST", body={"type": "daily", "workspace": "SSC"})
        self.assertIn("report", gen_res)
        rid = gen_res["report"]["id"]

        detail = self._req(f"/api/intelligence/reports/{rid}")
        self.assertIn("report", detail)
        self.assertEqual(detail["report"]["id"], rid)

    def test_06_api_scheduler(self):
        jobs_res = self._req("/api/intelligence/scheduler/jobs")
        self.assertIn("jobs", jobs_res)
        self.assertTrue(len(jobs_res["jobs"]) >= 7)

        run_res = self._req("/api/intelligence/scheduler/run-now", method="POST", body={"job_key": "proactive_alerts_scan"})
        self.assertIn("run", run_res)
        self.assertEqual(run_res["run"]["status"], "success")

        runs_res = self._req("/api/intelligence/scheduler/runs")
        self.assertIn("runs", runs_res)
        self.assertTrue(len(runs_res["runs"]) > 0)

    def test_07_api_knowledge(self):
        res = self._req("/api/intelligence/knowledge?category=software_docs")
        self.assertIn("knowledge", res)
        self.assertTrue(len(res["knowledge"]) > 0)

        add_res = self._req("/api/intelligence/knowledge", method="POST", body={
            "category": "engineering_standards",
            "title": "Total Station Benchmark Calibration SOP",
            "content": "Minimum 2 independent backsight checks before radiation measurements.",
            "tags": "total_station, calibration",
            "workspace": "SSC"
        })
        self.assertIn("entry", add_res)
        self.assertEqual(add_res["entry"]["title"], "Total Station Benchmark Calibration SOP")


if __name__ == "__main__":
    unittest.main()
