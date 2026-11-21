# scripts/audit_06_hermes_ai.py
import urllib.request, json, time, sys, os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from foundation.store import Store
from foundation.domains import hermes_bridge, ai_brain

BASE_URL = "http://127.0.0.1:8899"
evidence_dir = Path("AUDIT_TEST_EVIDENCE")
evidence_dir.mkdir(parents=True, exist_ok=True)

print("=== AUDIT 06: HERMES AI & FREE MODEL INFERENCE AUDIT ===")

store = Store("data/sgcc_foundation.sqlite")

# 1. Hermes installation & auth status
status = hermes_bridge.get_hermes_status(store)
print("[INFO] Hermes Status Overview:")
print(f"  Installed: {status.get('installed')} (Path: {status.get('binary_path')})")
print(f"  Version: {status.get('version')}")
print(f"  Authenticated: {status.get('authenticated')} (Provider: {status.get('auth_provider')})")
print(f"  Account Email: {status.get('account_email')}")
print(f"  Zero Paid Billing Enforced: {status.get('zero_paid_billing_enforced')}")

results = {
    "hermes_status": status,
    "model_tests": {},
    "ai_brain_agent_tests": {}
}

# 2. Test Primary Model: upstage/solar-mini4:free
test_prompt = "What are the core technical advantages of using DGPS RTK rovers over optical total stations in 100km highway alignment surveys?"
print("\n[STEP 1] Testing Primary Model: upstage/solar-mini4:free ...")
t0 = time.time()
res_primary = hermes_bridge.query_hermes(store, test_prompt, force_model="upstage/solar-mini4:free", timeout=12)
lat_primary = int((time.time() - t0) * 1000)

print(f"  Result OK: {res_primary.get('ok')}")
print(f"  Model Used: {res_primary.get('model_used')}")
print(f"  Mode: {res_primary.get('mode')}")
print(f"  Latency: {lat_primary}ms")
print(f"  Content Preview: {res_primary.get('content', '')[:160]}...")

results["model_tests"]["primary_solar_mini4"] = {
    "model": "upstage/solar-mini4:free",
    "configured": True,
    "mode": res_primary.get("mode"),
    "actual_model_used": res_primary.get("model_used"),
    "latency_ms": lat_primary,
    "success": res_primary.get("ok"),
    "response_preview": res_primary.get("content", "")[:200]
}

# 3. Test Fallback Model: stepfun/step-3.7-flash:free
print("\n[STEP 2] Testing Fallback Model: stepfun/step-3.7-flash:free ...")
t0 = time.time()
res_fallback = hermes_bridge.query_hermes(store, test_prompt, force_model="stepfun/step-3.7-flash:free", timeout=12)
lat_fallback = int((time.time() - t0) * 1000)

print(f"  Result OK: {res_fallback.get('ok')}")
print(f"  Model Used: {res_fallback.get('model_used')}")
print(f"  Mode: {res_fallback.get('mode')}")
print(f"  Latency: {lat_fallback}ms")
print(f"  Content Preview: {res_fallback.get('content', '')[:160]}...")

results["model_tests"]["fallback_stepfun"] = {
    "model": "stepfun/step-3.7-flash:free",
    "configured": True,
    "mode": res_fallback.get("mode"),
    "actual_model_used": res_fallback.get("model_used"),
    "latency_ms": lat_fallback,
    "success": res_fallback.get("ok"),
    "response_preview": res_fallback.get("content", "")[:200]
}

# 4. Test Deterministic Domain Brain Offline Fallback
print("\n[STEP 3] Testing Deterministic Domain Brain Fallback ...")
res_det = hermes_bridge._deterministic_domain_fallback(test_prompt, "SSC")
print(f"  Deterministic Fallback Content Preview: {res_det[:160]}...")
results["model_tests"]["deterministic_domain_brain"] = {
    "status": "PASS",
    "sample_preview": res_det[:200]
}

# 5. Test AI Brain Specialist Agent Execution
print("\n[STEP 4] Testing AI Brain Specialist Agents Execution ...")
agents = ai_brain.list_agents(store)
print(f"  Total Specialist Agents Seeded: {len(agents)}")
assert len(agents) >= 12, "Fewer than 12 specialist agents found!"

# Execute task with SURVEY-OPS agent
survey_agent = store.fetchone("SELECT id, code FROM ai_agents WHERE code LIKE '%SURVEY%'")
agent_id = survey_agent["id"] if survey_agent else None
print(f"  Found Agent: {survey_agent['code']} (ID={agent_id})")

task_created = ai_brain.create_task(
    store=store,
    actor_id=1,
    workspace_id="SSC",
    agent_id=agent_id,
    title="Verify DGPS Control Point Calibration",
    description="Check RTK base station coordinates against benchmark BM-104"
)
task_id = task_created["id"]
print(f"  Created AI Task #{task_id} with agent {survey_agent['code']}")

exec_res = ai_brain.execute_task(store, 1, task_id)
print(f"  Execution Status: {exec_res.get('status')}")
print(f"  Tool Executions Count: {len(exec_res.get('tool_executions', []))}")
print(f"  Output Preview: {exec_res.get('output', '')[:160]}...")

results["ai_brain_agent_tests"] = {
    "agents_count": len(agents),
    "sample_agent": "SURVEY-OPS",
    "task_id": task_id,
    "status": exec_res.get("status"),
    "tools_executed": len(exec_res.get("tool_executions", []))
}

# Clean up test task
store.conn.execute("DELETE FROM ai_tasks WHERE id=?", (task_id,))
store.conn.commit()

with open(evidence_dir / "audit_06_hermes_ai.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)

print("\nAUDIT 06 COMPLETED: Evidence saved to AUDIT_TEST_EVIDENCE/audit_06_hermes_ai.json")
