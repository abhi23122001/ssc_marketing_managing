# -*- coding: utf-8 -*-
"""Unit tests for Universal Filter & Export System."""
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from foundation.store import Store
from foundation.domains.filter_system import query_filtered_records, export_filtered_csv
from foundation.domains.task_management import ensure_tasks_schema, create_employee_task


class TestUniversalFilterSystem(unittest.TestCase):
    def setUp(self):
        self.store = Store()
        ensure_tasks_schema(self.store.conn)

        # Seed test tasks with distinct attributes
        create_employee_task(self.store, "SSC", 1, {
            "title": "Alpha Drone Topo Mapping",
            "description": "High resolution contour survey",
            "priority": "urgent",
            "category": "field_survey",
            "deadline_date": "2026-11-20"
        })
        create_employee_task(self.store, "SSC", 1, {
            "title": "Beta Highway Alignment QC",
            "description": "MoRTH Section 300 checks",
            "priority": "low",
            "category": "site_qc",
            "deadline_date": "2026-11-28"
        })

    def test_combined_search_and_filters(self):
        # 1. Search term matching
        res = query_filtered_records(self.store, "tasks", "SSC", {"search": "Drone"})
        self.assertTrue(res["ok"])
        self.assertGreaterEqual(res["pagination"]["total_count"], 1)
        self.assertTrue(any("Drone" in r["title"] for r in res["records"]))

        # 2. Priority filter
        res_urgent = query_filtered_records(self.store, "tasks", "SSC", {"priority": "urgent"})
        self.assertTrue(all(r["priority"] == "urgent" for r in res_urgent["records"]))

        # 3. Combined search + priority + category
        res_comb = query_filtered_records(self.store, "tasks", "SSC", {
            "search": "Highway",
            "priority": "low",
            "category": "site_qc"
        })
        self.assertGreaterEqual(len(res_comb["records"]), 1)
        self.assertIn("Priority: low", res_comb["active_filters"])
        self.assertIn("Category: site_qc", res_comb["active_filters"])

    def test_pagination(self):
        res = query_filtered_records(self.store, "tasks", "SSC", {}, page=1, limit=1)
        self.assertEqual(res["pagination"]["limit"], 1)
        self.assertGreaterEqual(res["pagination"]["total_pages"], 1)

    def test_csv_export(self):
        csv_text, filename = export_filtered_csv(self.store, "tasks", "SSC", {"priority": "urgent"})
        self.assertTrue(filename.startswith("tasks_export_SSC_"))
        self.assertTrue(filename.endswith(".csv"))
        self.assertIn("title", csv_text)
        self.assertIn("Alpha Drone", csv_text)


if __name__ == "__main__":
    unittest.main()
