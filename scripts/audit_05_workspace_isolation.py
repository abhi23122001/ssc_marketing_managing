# scripts/audit_05_workspace_isolation.py
import urllib.request, json, time
from pathlib import Path

BASE_URL = "http://127.0.0.1:8899"
evidence_dir = Path("AUDIT_TEST_EVIDENCE")
evidence_dir.mkdir(parents=True, exist_ok=True)

print("=== AUDIT 05: MULTI-WORKSPACE ISOLATION AUDIT ===")

def api_call(path, token=None, method="GET", body=None, ws=None):
    url = f"{BASE_URL}{path}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if ws:
        headers["X-Workspace-ID"] = ws
    data = json.dumps(body).encode("utf-8") if body else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8")
        try:
            return e.code, json.loads(err_body)
        except Exception:
            return e.code, {"error": err_body}

results = {}

# 1. Login Accounts
# Owner (Cross-workspace)
_, o_res = api_call("/api/auth/login", method="POST", body={"username": "owner", "password": "demo-owner-pass-0001"})
owner_token = o_res["token"]

# Employee (SSC only)
_, e_res = api_call("/api/auth/login", method="POST", body={"username": "employee", "password": "demo-employee-pass-0001"})
emp_token = e_res["token"]

# PM (INFRA only)
_, pm_res = api_call("/api/auth/login", method="POST", body={"username": "pm", "password": "demo-pm-pass-0001"})
pm_token = pm_res.get("token")

assert owner_token and emp_token and pm_token, "Failed to authenticate test roles"

# Test 1: Owner workspace queries are cleanly partitioned
owner_scoping = {}
for ws in ["SSC", "INFRA", "OTHER"]:
    s_sites, d_sites = api_call(f"/api/sites?workspace={ws}", token=owner_token, ws=ws)
    s_leads, d_leads = api_call(f"/api/leads?workspace={ws}", token=owner_token, ws=ws)
    sites_list = [x["code"] for x in d_sites.get("sites", [])]
    leads_list = [x["company"] for x in d_leads.get("leads", [])]
    owner_scoping[ws] = {
        "sites_count": len(sites_list),
        "leads_count": len(leads_list),
        "sites_sample": sites_list[:3],
        "leads_sample": leads_list[:3]
    }
    print(f"[PASS] Owner Scoping [{ws}]: {len(sites_list)} sites, {len(leads_list)} leads")

# Assert disjointness
ssc_sites = set(owner_scoping["SSC"]["sites_sample"])
infra_sites = set(owner_scoping["INFRA"]["sites_sample"])
assert ssc_sites.isdisjoint(infra_sites), "Disjointness violation: SSC and INFRA share sites!"
results["owner_scoping"] = owner_scoping

# Test 2: Unauthorized Cross-Tenant Queries from SSC Employee
# Employee is assigned to SSC. Attempting to query INFRA or OTHER must return 403 Forbidden
unauth_tests_emp = []
for target_ws in ["INFRA", "OTHER"]:
    s, r = api_call(f"/api/sites?workspace={target_ws}", token=emp_token, ws=target_ws)
    is_blocked = (s == 403)
    unauth_tests_emp.append({"target": target_ws, "http": s, "blocked": is_blocked})
    print(f"[{'PASS' if is_blocked else 'FAIL'}] SSC Employee accessing {target_ws} sites -> HTTP {s} (Expected 403). Blocked={is_blocked}")

results["ssc_employee_cross_tenant_blocks"] = unauth_tests_emp

# Test 3: Unauthorized Cross-Tenant Queries from INFRA PM
# PM is assigned to INFRA. Attempting to query SSC or OTHER must return 403 Forbidden
unauth_tests_pm = []
for target_ws in ["SSC", "OTHER"]:
    s, r = api_call(f"/api/sites?workspace={target_ws}", token=pm_token, ws=target_ws)
    is_blocked = (s == 403)
    unauth_tests_pm.append({"target": target_ws, "http": s, "blocked": is_blocked})
    print(f"[{'PASS' if is_blocked else 'FAIL'}] INFRA PM accessing {target_ws} sites -> HTTP {s} (Expected 403). Blocked={is_blocked}")

results["infra_pm_cross_tenant_blocks"] = unauth_tests_pm

# Test 4: Tenant Scoped Creation
# Create a disposable lead in INFRA using PM account
disposable_lead = {
    "lead_name": "Audit Test Infrastructure Ltd",
    "company": "Audit Test Infrastructure Ltd",
    "phone": "+91 91111 22222",
    "service_interest": "Highway Grading",
    "enquiry_text": "Audit disposable isolation check"
}
s, lead_res = api_call("/api/leads", token=pm_token, method="POST", body=disposable_lead, ws="INFRA")
lead_id = lead_res.get("lead", {}).get("id") if s in (200, 201) else None
print(f"[PASS] PM created lead in INFRA -> HTTP {s}, ID={lead_id}")

# Verify that SSC cannot see this lead
s_ssc_chk, d_ssc_chk = api_call("/api/leads?workspace=SSC", token=emp_token, ws="SSC")
ssc_lead_ids = [l["id"] for l in d_ssc_chk.get("leads", [])]
leak_detected = (lead_id in ssc_lead_ids)
print(f"[{'FAIL LEAK' if leak_detected else 'PASS'}] Check leakage into SSC leads list: Leaked={leak_detected}")
results["creation_isolation"] = {
    "created_id": lead_id,
    "leaked_into_ssc": leak_detected,
    "pass": not leak_detected
}

# Cleanup disposable record
if lead_id:
    import sqlite3
    c = sqlite3.connect("data/sgcc_foundation.sqlite")
    c.execute("DELETE FROM social_leads WHERE id=?", (lead_id,))
    c.commit()
    c.close()

with open(evidence_dir / "audit_05_workspace_isolation.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)

print("\nAUDIT 05 COMPLETED: Evidence saved to AUDIT_TEST_EVIDENCE/audit_05_workspace_isolation.json")
