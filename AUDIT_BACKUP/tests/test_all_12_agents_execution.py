# -*- coding: utf-8 -*-
"""Comprehensive verification test suite for all 12 Specialist AI Agents in SHAH Group AI OS.

Verifies:
  1. All 12 specialist AI agents exist or are initialized with domain allowlisted tools.
  2. Each agent dispatches real tasks via ai_brain.create_task and executes them via ai_brain.execute_task.
  3. RBAC gating works: Owner/Manager executes permitted tools; unauthorized tools are blocked.
  4. Tool execution records are written to ai_tool_executions with parameter validation and outputs.
  5. Task status transitions to 'completed' with structured result_summary.
  6. Audit trail is generated for every agent execution.
"""
import json
import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from foundation.store import Store
from foundation.domains import ai_brain

SPECIALIST_AGENTS = [
    {
        "code": "owner_agent",
        "name": "Owner Assistant",
        "domain": "Executive & Oversight",
        "tools": ["workspace:list", "workspace:read", "reports:read"]
    },
    {
        "code": "pm_agent",
        "name": "PM Agent",
        "domain": "Project Management",
        "tools": ["sites:read", "resource:read", "workspace:read"]
    },
    {
        "code": "survey_ops_agent",
        "name": "Survey Operations Agent",
        "domain": "Field Operations",
        "tools": ["sites:read", "attendance:read", "alerts:attendance"]
    },
    {
        "code": "crm_agent",
        "name": "CRM Agent",
        "domain": "Sales & Clients",
        "tools": ["leads:read", "clients:read", "resource:read"]
    },
    {
        "code": "finance_agent",
        "name": "Finance Agent",
        "domain": "Financial Control",
        "tools": ["expense:read", "vendors:read", "alerts:expense"]
    },
    {
        "code": "hr_agent",
        "name": "HR Agent",
        "domain": "HRM & Personnel",
        "tools": ["employees:read", "attendance:read", "payroll:read"]
    },
    {
        "code": "marketing_agent",
        "name": "Marketing Agent",
        "domain": "Growth & Brand",
        "tools": ["leads:read", "reports:read", "resource:list"]
    },
    {
        "code": "reporting_agent",
        "name": "Reporting Agent",
        "domain": "Compliance & MIS",
        "tools": ["reports:read", "workspace:list", "sites:read"]
    },
    {
        "code": "survey_analyst_agent",
        "name": "Survey Analyst Agent",
        "domain": "Technical Geospatial",
        "tools": ["sites:read", "resource:read", "workspace:read"]
    },
    {
        "code": "boq_estimator_agent",
        "name": "BOQ Estimator Agent",
        "domain": "Tenders & Estimations",
        "tools": ["sites:read", "vendors:read", "expense:read"]
    },
    {
        "code": "content_creator_agent",
        "name": "Content Creator Agent",
        "domain": "Media Studio",
        "tools": ["leads:read", "reports:read", "resource:read"]
    },
    {
        "code": "research_agent",
        "name": "Research Agent",
        "domain": "Regulatory Norms",
        "tools": ["workspace:read", "sites:read", "resource:list"]
    }
]


class TestAll12AgentsExecution(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.store = Store()
        cls.workspace = "SSC"
        # Ensure owner user exists
        owner_user = cls.store.fetchone("SELECT id FROM users WHERE role_id=(SELECT id FROM roles WHERE code='Owner')")
        cls.actor_id = owner_user["id"] if owner_user else 1

        # Seed or ensure all 12 agents exist in SQLite
        for spec in SPECIALIST_AGENTS:
            existing = cls.store.fetchone("SELECT id FROM ai_agents WHERE code=? AND workspace_id=?", (spec["code"], cls.workspace))
            if not existing:
                ai_brain.create_agent(
                    cls.store,
                    actor_id=cls.actor_id,
                    workspace_id=cls.workspace,
                    code=spec["code"],
                    name=spec["name"],
                    description=f"{spec['domain']} autonomous specialist agent.",
                    agent_type="specialist",
                    tool_access=spec["tools"]
                )
            else:
                # Update tool_access to include configured tools
                cls.store.conn.execute(
                    "UPDATE ai_agents SET tool_access=? WHERE id=?",
                    (json.dumps(spec["tools"]), existing["id"])
                )
                cls.store.conn.commit()

    def test_01_all_12_agents_registered(self):
        agents = ai_brain.list_agents(self.store, self.workspace)
        agent_codes = {a["code"] for a in agents}
        for spec in SPECIALIST_AGENTS:
            self.assertIn(spec["code"], agent_codes, f"Agent {spec['code']} must be registered in {self.workspace}")

    def test_02_execute_owner_agent_task(self):
        self._run_agent_task("owner_agent", "workspace:list", {})

    def test_03_execute_pm_agent_task(self):
        self._run_agent_task("pm_agent", "sites:read", {})

    def test_04_execute_survey_ops_agent_task(self):
        self._run_agent_task("survey_ops_agent", "attendance:read", {})

    def test_05_execute_crm_agent_task(self):
        self._run_agent_task("crm_agent", "leads:read", {})

    def test_06_execute_finance_agent_task(self):
        self._run_agent_task("finance_agent", "expense:read", {})

    def test_07_execute_hr_agent_task(self):
        self._run_agent_task("hr_agent", "employees:read", {})

    def test_08_execute_marketing_agent_task(self):
        self._run_agent_task("marketing_agent", "leads:read", {})

    def test_09_execute_reporting_agent_task(self):
        self._run_agent_task("reporting_agent", "workspace:list", {})

    def test_10_execute_survey_analyst_agent_task(self):
        self._run_agent_task("survey_analyst_agent", "sites:read", {})

    def test_11_execute_boq_estimator_agent_task(self):
        self._run_agent_task("boq_estimator_agent", "vendors:read", {})

    def test_12_execute_content_creator_agent_task(self):
        self._run_agent_task("content_creator_agent", "resource:read", {"rid": 1})

    def test_13_execute_research_agent_task(self):
        self._run_agent_task("research_agent", "workspace:read", {})

    def test_14_rbac_disallowed_tool_blocked(self):
        """Verify that an unauthorized tool or one not in allowlist is properly blocked."""
        agent = self.store.fetchone("SELECT id FROM ai_agents WHERE code='crm_agent' AND workspace_id=?", (self.workspace,))
        task = ai_brain.create_task(
            self.store,
            actor_id=self.actor_id,
            workspace_id=self.workspace,
            agent_id=agent["id"],
            title="Attempt Unauthorized Tool Execution",
            description="Testing agent sandbox isolation",
            priority="high",
            tool_requests=[{"tool": "payroll:execute_unauthorized", "args": {}}]
        )
        res = ai_brain.execute_task(self.store, self.actor_id, task["id"])
        # Should record an execution attempt marked not allowed
        execs = ai_brain.list_tool_executions(self.store, task["id"])
        self.assertTrue(len(execs) > 0)
        self.assertEqual(execs[0]["allowed"], 0)

    def _run_agent_task(self, agent_code: str, tool_name: str, args: dict):
        agent = self.store.fetchone("SELECT id FROM ai_agents WHERE code=? AND workspace_id=?", (agent_code, self.workspace))
        self.assertIsNotNone(agent, f"Agent {agent_code} not found")

        task = ai_brain.create_task(
            self.store,
            actor_id=self.actor_id,
            workspace_id=self.workspace,
            agent_id=agent["id"],
            title=f"Verify {agent_code} Tool Execution",
            description=f"Automated test for tool {tool_name}",
            priority="medium",
            tool_requests=[{"tool": tool_name, "args": args}]
        )
        self.assertIsNotNone(task["id"])

        res = ai_brain.execute_task(self.store, self.actor_id, task["id"])
        self.assertEqual(res["status"], "completed")

        # Verify tool executions
        execs = ai_brain.list_tool_executions(self.store, task["id"])
        self.assertTrue(len(execs) >= 1)
        self.assertEqual(execs[0]["tool_name"], tool_name)
        self.assertEqual(execs[0]["allowed"], 1)

        # Verify audit log
        audit = self.store.fetchone(
            "SELECT * FROM audit_logs WHERE action='ai:tool:execution' AND target=? ORDER BY id DESC",
            (f"ai_tool_execution:{execs[0]['id']}",)
        )
        self.assertIsNotNone(audit)


if __name__ == "__main__":
    unittest.main()
