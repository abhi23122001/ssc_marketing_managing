# -*- coding: utf-8 -*-
"""Unit and lifecycle tests for Employee Task Management."""
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from foundation.store import Store
from foundation.domains.task_management import (
    ensure_tasks_schema, create_employee_task, list_employee_tasks,
    accept_task, update_task_progress, submit_task_work_proof,
    review_task, get_admin_workload_summary, list_user_notifications
)


class TestEmployeeTaskManagement(unittest.TestCase):
    def setUp(self):
        self.store = Store()
        ensure_tasks_schema(self.store.conn)

    def test_complete_task_lifecycle(self):
        # 1. Admin creates task for employee (user_id=3)
        task = create_employee_task(self.store, "SSC", 1, {
            "title": "DGPS Control Benchmark Calibration",
            "description": "Establish 2-hr static baseline connected to Survey of India GTS datum.",
            "assigned_to": 3,
            "priority": "urgent",
            "category": "field_survey",
            "project_id": "SITE-SGR-01",
            "deadline_date": "2026-11-25"
        })
        self.assertIsNotNone(task["id"])
        self.assertEqual(task["status"], "assigned")
        self.assertEqual(task["priority"], "urgent")

        # 2. Check notification generated
        notifs = list_user_notifications(self.store, 3, unread_only=True)
        self.assertGreater(len(notifs), 0)
        self.assertIn("New Task Assigned", notifs[0]["title"])

        # 3. Employee accepts task
        accepted = accept_task(self.store, task["id"], 3)
        self.assertEqual(accepted["status"], "accepted")

        # 4. Employee updates progress
        in_prog = update_task_progress(self.store, task["id"], 3, 60, "Static logging underway.")
        self.assertEqual(in_prog["status"], "in_progress")
        self.assertEqual(in_prog["progress_pct"], 60)

        # 5. Employee submits work proof
        submitted = submit_task_work_proof(self.store, task["id"], 3, "Baseline RINEX observations processed. Residual error: 2.4mm.", "sgr-01/baseline.csv")
        self.assertEqual(submitted["status"], "submitted")
        self.assertEqual(submitted["progress_pct"], 100)
        self.assertEqual(submitted["work_proof_url"], "sgr-01/baseline.csv")

        # 6. Manager requests rework
        reworked = review_task(self.store, task["id"], 1, "rework", "Please attach PDOP log chart confirming PDOP < 2.0 throughout session.")
        self.assertEqual(reworked["status"], "rework_requested")
        self.assertIn("PDOP", reworked["rework_notes"])

        # 7. Employee resubmits proof
        resubmitted = submit_task_work_proof(self.store, task["id"], 3, "Attached Trimble PDOP validation report (Max PDOP: 1.4).", "sgr-01/pdop_chart.pdf")
        self.assertEqual(resubmitted["status"], "submitted")

        # 8. Manager approves task
        approved = review_task(self.store, task["id"], 1, "approve", "Accuracy tolerances and PDOP verified. Approved.")
        self.assertEqual(approved["status"], "approved")
        self.assertIsNotNone(approved["closed_at"])

        # 9. Verify Admin Workload Summary
        summary = get_admin_workload_summary(self.store, "SSC")
        self.assertGreaterEqual(summary["total_tasks"], 1)
        self.assertGreaterEqual(summary["completed_count"], 1)
        self.assertIn("employee_performance", summary)

        # 10. Verify Filtered Views
        my_tasks = list_employee_tasks(self.store, "SSC", user_id=3, filter_type="my_tasks")
        self.assertTrue(any(t["id"] == task["id"] for t in my_tasks))


if __name__ == "__main__":
    unittest.main()
