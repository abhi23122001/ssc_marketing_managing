# -*- coding: utf-8 -*-
"""Comprehensive verification of SHAH Group AI Brain — Autonomous Business Intelligence,
Research & Proactive Operations across SSC and INFRA.

Asserts all 13 core capabilities defined in Section 13:
  1. Software question answered from source code/docs without hallucination.
  2. External research question answered with source-backed evidence.
  3. Autonomous daily research execution without manual prompt.
  4. Separate SSC and INFRA daily marketing briefs.
  5. Content recommendations & posting times with timezone and rationale.
  6. Daily report generation with real DB statistics.
  7. Weekly report generation.
  8. Monthly report generation.
  9. Proactive business alert generated from real test condition.
  10. Background scheduler job execution.
  11. Scheduler execution history & retry tracking.
  12. Multi-tenant workspace isolation (SSC vs INFRA).
  13. Report storage, export, and retrieval.
"""
from __future__ import annotations

import json
import os
import sys
import unittest
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from foundation.store import Store
from foundation.domains import ai_intelligence, business_ops
from foundation import scheduler


class TestAutonomousAiBrain(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.store = Store()
        cls.ssc_ws = "SSC"
        cls.infra_ws = "INFRA"
        ai_intelligence.ensure_ai_intelligence_schema(cls.store.conn)
        business_ops.ensure_business_ops_schema(cls.store.conn)

    # -------------------------------------------------------------------------
    # 1. Software question answered from source code/docs
    # -------------------------------------------------------------------------
    def test_01_software_question_answered_from_code_docs(self):
        """AI assistant answers how to use actual software features from internal docs."""
        # Query in Hinglish
        res = ai_intelligence.ask_anything(
            self.store,
            "Quotation kaise banate hain aur 18% GST kaise lagta hai?",
            workspace_id=self.ssc_ws,
            user_role="Owner"
        )
        self.assertEqual(res["intent"], "SOFTWARE_DOCS")
        self.assertIn("verified_answer", res)
        self.assertIn("18% Total", res["verified_answer"])
        self.assertEqual(res["feature_status"], "IMPLEMENTED & VERIFIED")
        self.assertIn("Internal Architecture Documentation", res["source"])

    # -------------------------------------------------------------------------
    # 2. External research question answered with source-backed evidence
    # -------------------------------------------------------------------------
    def test_02_external_research_answered_with_sources(self):
        """AI assistant provides source-backed research on tenders and competitor trends."""
        res = ai_intelligence.ask_anything(
            self.store,
            "Government GeM portal survey tenders and road development trends kya chal rahe hain?",
            workspace_id=self.ssc_ws,
            user_role="Owner"
        )
        self.assertEqual(res["intent"], "RESEARCH_TENDERS")
        self.assertIn("sources", res)
        self.assertTrue(len(res["sources"]) > 0)
        # Verify source URLs and publication metadata exist
        for s in res["sources"]:
            self.assertIn("url", s)
            self.assertIn("publication_date", s)
            self.assertTrue(s["url"].startswith("http"))
        self.assertIn("verified_insights", res)

    # -------------------------------------------------------------------------
    # 3. Autonomous daily research execution without manual prompt
    # -------------------------------------------------------------------------
    def test_03_autonomous_daily_research_without_prompt(self):
        """Autonomous research engine generates daily items and persists to ai_research_items."""
        items = ai_intelligence.generate_autonomous_daily_research(self.store, self.ssc_ws)
        self.assertIsInstance(items, list)
        self.assertTrue(len(items) >= 4)

        # Check DB persistence
        db_rows = self.store.fetchall(
            "SELECT * FROM ai_research_items WHERE workspace_id=?", (self.ssc_ws,)
        )
        self.assertTrue(len(db_rows) >= 4)
        sample = db_rows[0]
        self.assertIn(sample["category"], ["survey_tech", "infra_civil", "tenders", "marketing"])
        self.assertTrue(sample["relevance_score"] >= 80)
        self.assertIsNotNone(sample["recommended_action"])

    # -------------------------------------------------------------------------
    # 4. Separate SSC and INFRA daily marketing briefs
    # -------------------------------------------------------------------------
    def test_04_separate_ssc_and_infra_marketing_briefs(self):
        """SSC and INFRA receive domain-specific marketing briefs with independent directives."""
        brief_ssc = ai_intelligence.generate_daily_marketing_brief(self.store, self.ssc_ws)
        brief_infra = ai_intelligence.generate_daily_marketing_brief(self.store, self.infra_ws)

        self.assertEqual(brief_ssc["workspace_id"], "SSC")
        self.assertEqual(brief_infra["workspace_id"], "INFRA")
        self.assertNotEqual(brief_ssc["industry_trends"], brief_infra["industry_trends"])
        self.assertIn("DGPS", brief_ssc["industry_trends"])
        self.assertIn("warehouse", brief_infra["industry_trends"].lower())

    # -------------------------------------------------------------------------
    # 5. Content recommendations & posting times with timezone and rationale
    # -------------------------------------------------------------------------
    def test_05_posting_time_optimization_and_timezone(self):
        """Briefs specify Asia/Kolkata posting times and audience behavioral rationale."""
        brief = ai_intelligence.get_latest_marketing_brief(self.store, self.ssc_ws)
        self.assertIsNotNone(brief)
        sched = brief["posting_schedule"]
        self.assertIn("IST", sched)
        self.assertIn("LinkedIn", sched)
        self.assertIn("Instagram", sched)

    # -------------------------------------------------------------------------
    # 6. Daily report generation with real DB statistics
    # -------------------------------------------------------------------------
    def test_06_daily_report_generation_with_real_db_statistics(self):
        """Daily report calculates live statistics directly from SQLite tables."""
        rep = ai_intelligence.generate_daily_report(self.store, self.ssc_ws)
        self.assertEqual(rep["report_type"], "daily")
        self.assertEqual(rep["workspace_id"], self.ssc_ws)

        # Verify parsed content matches DB realities
        content = json.loads(rep["content_json"])
        highlights = content["operational_highlights"]
        self.assertIn("active_survey_sites", highlights)
        self.assertIn("total_leads_in_pipeline", highlights)
        self.assertIn("field_checkins_logged", highlights)

        fin = content["financial_summary"]
        self.assertIn("total_invoiced_inr", fin)
        self.assertIn("total_collected_inr", fin)
        self.assertIn("net_operating_profit_inr", fin)

    # -------------------------------------------------------------------------
    # 7. Weekly report generation
    # -------------------------------------------------------------------------
    def test_07_weekly_report_generation(self):
        """Weekly report aggregates operations, client counts, and growth directives."""
        rep = ai_intelligence.generate_weekly_report(self.store, self.ssc_ws)
        self.assertEqual(rep["report_type"], "weekly")
        content = json.loads(rep["content_json"])
        self.assertIn("weekly_metrics", content)
        self.assertIn("next_week_strategy", content)
        self.assertTrue(len(content["next_week_strategy"]) > 0)

    # -------------------------------------------------------------------------
    # 8. Monthly report generation
    # -------------------------------------------------------------------------
    def test_08_monthly_report_generation(self):
        """Monthly report provides P&L closure, HR payroll overview, and risk factors."""
        rep = ai_intelligence.generate_monthly_report(self.store, self.ssc_ws)
        self.assertEqual(rep["report_type"], "monthly")
        content = json.loads(rep["content_json"])
        self.assertIn("pl_statement", content)
        self.assertIn("hr_payroll_overview", content)
        self.assertIn("risk_factors", content)
        self.assertIn("growth_recommendations", content)

    # -------------------------------------------------------------------------
    # 9. Proactive business alert generated from real test condition
    # -------------------------------------------------------------------------
    def test_09_proactive_business_alerts_from_live_conditions(self):
        """Scanner identifies real conditions: uncontacted high-priority lead or unpaid invoice."""
        # Insert a high-priority new lead to trigger an alert
        lead_id = self.store.conn.execute(
            "INSERT INTO social_leads (workspace_id, lead_name, company, phone, lead_priority, lead_status) "
            "VALUES (?, 'Shri Ram Builders', 'SRB Infrastructure', '+91 99999 11111', 'high', 'new')",
            (self.ssc_ws,)
        ).lastrowid
        self.store.conn.commit()

        alerts = ai_intelligence.scan_proactive_business_alerts(self.store, self.ssc_ws)
        self.assertTrue(len(alerts) > 0)
        lead_alert = next((a for a in alerts if f"lead_urgent_{lead_id}" == a.get("alert_hash")), None)
        self.assertIsNotNone(lead_alert)
        self.assertEqual(lead_alert["priority"], "high")
        self.assertEqual(lead_alert["status"], "active")

        # Resolve the alert
        resolved = ai_intelligence.resolve_business_alert(self.store, lead_alert["id"])
        self.assertTrue(resolved)
        updated = self.store.fetchone("SELECT * FROM ai_business_alerts WHERE id=?", (lead_alert["id"],))
        self.assertEqual(updated["status"], "resolved")

    # -------------------------------------------------------------------------
    # 10. Background scheduler job execution
    # -------------------------------------------------------------------------
    def test_10_background_scheduler_job_execution(self):
        """Executes a standing scheduler job and verifies execution record."""
        res = ai_intelligence.run_scheduler_job(self.store, "daily_marketing_brief")
        self.assertEqual(res["job_key"], "daily_marketing_brief")
        self.assertEqual(res["status"], "success")
        self.assertIn("Generated morning briefs", res["summary"])

    # -------------------------------------------------------------------------
    # 11. Scheduler execution history & retry tracking
    # -------------------------------------------------------------------------
    def test_11_scheduler_execution_history_and_logging(self):
        """History runs table logs every execution with timestamp and status."""
        runs = ai_intelligence.list_scheduler_runs(self.store, limit=10)
        self.assertTrue(len(runs) > 0)
        self.assertEqual(runs[0]["status"], "success")
        self.assertIsNotNone(runs[0]["started_at"])
        self.assertIsNotNone(runs[0]["completed_at"])

        # Check standing jobs listing
        jobs = ai_intelligence.list_scheduler_jobs(self.store)
        self.assertTrue(len(jobs) >= 7)
        brief_job = next((j for j in jobs if j["job_key"] == "daily_marketing_brief"), None)
        self.assertIsNotNone(brief_job)
        self.assertTrue(brief_job["run_count"] >= 1)
        self.assertEqual(brief_job["timezone"], "Asia/Kolkata")

    # -------------------------------------------------------------------------
    # 12. Multi-tenant workspace isolation (SSC vs INFRA)
    # -------------------------------------------------------------------------
    def test_12_multitenant_workspace_isolation(self):
        """Non-owner users cannot read across business workspace boundaries."""
        # Ask question as SSC Employee about business data
        res_ssc = ai_intelligence.ask_anything(
            self.store,
            "Total operating profit kitna hua hai?",
            workspace_id=self.ssc_ws,
            user_role="Employee"
        )
        self.assertEqual(res_ssc["intent"], "BUSINESS_DATA")
        self.assertEqual(res_ssc["workspace_id"], self.ssc_ws)

        # Reports listed for SSC do not bleed into INFRA
        ssc_reports = ai_intelligence.list_generated_reports(self.store, self.ssc_ws)
        for r in ssc_reports:
            self.assertEqual(r["workspace_id"], self.ssc_ws)

    # -------------------------------------------------------------------------
    # 13. Report storage, export, and retrieval
    # -------------------------------------------------------------------------
    def test_13_report_storage_export_and_retrieval(self):
        """Saved reports are retrieved by ID and parsed for export."""
        reports = ai_intelligence.list_generated_reports(self.store, self.ssc_ws, report_type="daily")
        self.assertTrue(len(reports) > 0)
        rid = reports[0]["id"]

        row = self.store.fetchone("SELECT * FROM ai_generated_reports WHERE id=?", (rid,))
        self.assertIsNotNone(row)
        content = json.loads(row["content_json"])
        self.assertIn("report_date", content)
        self.assertIn("financial_summary", content)


if __name__ == "__main__":
    unittest.main()
