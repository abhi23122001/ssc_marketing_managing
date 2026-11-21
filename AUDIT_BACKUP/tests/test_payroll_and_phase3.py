"""Payroll, CRM Follow-ups, CSV Exports, AI Agent Execution, and Security Tests.
Run: python tests/test_payroll_and_phase3.py
"""
import sys
import json
import urllib.request
import urllib.error

BASE = "http://127.0.0.1:8899"
PASS = 0
FAIL = 0

def api(method, path, data=None, tok=None, expected=200):
    global PASS, FAIL
    headers = {"Content-Type": "application/json"}
    if tok:
        headers["Authorization"] = "Bearer " + tok
    req = urllib.request.Request(
        BASE + path,
        data=json.dumps(data).encode() if data else None,
        headers=headers,
        method=method,
    )
    try:
        r = urllib.request.urlopen(req)
        status = r.status
        content_type = r.headers.get("Content-Type", "")
        if "text/csv" in content_type:
            raw = r.read().decode("utf-8")
            body = {"csv": raw}
        else:
            body = json.loads(r.read())
    except urllib.error.HTTPError as e:
        status = e.code
        try:
            body = json.loads(e.read())
        except Exception:
            body = {}
    ok = (status == expected)
    label = "PASS" if ok else f"FAIL (got {status}, expected {expected})"
    if ok:
        PASS += 1
    else:
        FAIL += 1
    print(f"[{status}] {label} {method} {path}")
    return body

print("=== STARTING PAYROLL & ADVANCED FEATURES TEST SUITE ===")

# 1. Login
d = api("POST", "/api/auth/login", {"username": "owner", "password": "demo-owner-pass-0001"})
owner_tok = d.get("token", "")
assert owner_tok, "Owner token missing"

# 2. Test Payroll Calculate Preview
print("\n--- Payroll Calculate Preview ---")
d = api("POST", "/api/payroll/calculate", {"run_month": "2026-11", "base_monthly_salary": 30000.0}, tok=owner_tok)
assert "summary" in d, f"Missing summary: {d}"
summary = d["summary"]
print(f"  Employees: {summary.get('total_employees')}, Total Gross: INR {summary.get('total_gross')}")

# 3. Test Payroll Run Execution
print("\n--- Payroll Run Execution ---")
d = api("POST", "/api/payroll/run", {"run_month": "2026-11", "base_monthly_salary": 30000.0}, tok=owner_tok, expected=201)
assert "payroll_run" in d, f"Missing payroll_run: {d}"
run = d["payroll_run"]
run_id = run["id"]
print(f"  Run #{run_id} created for {run.get('run_month')}, Gross: INR {run.get('total_gross')}, Payslips: {len(run.get('payslips', []))}")
assert len(run.get("payslips", [])) > 0, "No payslips generated"

# 4. Test Get Payroll Run Details
print("\n--- Get Payroll Run Details ---")
d = api("GET", f"/api/payroll/runs/{run_id}", tok=owner_tok)
assert d.get("payroll_run", {}).get("id") == run_id
assert len(d["payroll_run"].get("payslips", [])) > 0

# 5. Test List Payroll Runs
print("\n--- List Payroll Runs ---")
d = api("GET", "/api/payroll/runs", tok=owner_tok)
assert d.get("count", 0) >= 1

# 6. Test List Payslips
print("\n--- List Payslips ---")
d = api("GET", "/api/payroll/payslips", tok=owner_tok)
assert d.get("count", 0) >= 1
slip_id = d["payslips"][0]["id"]
print(f"  First payslip id={slip_id}, employee={d['payslips'][0]['name']}")

# 7. Test Get Single Payslip
print("\n--- Get Single Payslip ---")
d = api("GET", f"/api/payroll/payslips/{slip_id}", tok=owner_tok)
assert d.get("payslip", {}).get("id") == slip_id

# 8. Test Approve Payroll Run
print("\n--- Approve Payroll Run ---")
d = api("POST", f"/api/payroll/runs/{run_id}/approve", tok=owner_tok)
assert d.get("payroll_run", {}).get("status") == "approved"

# 9. Test CRM Follow-Up Scheduling
print("\n--- CRM Follow-Up Scheduling ---")
d = api("POST", "/api/leads/2/follow-up", {"follow_up_date": "2026-12-05", "assigned_employee_id": 1}, tok=owner_tok)
assert d.get("lead", {}).get("follow_up_date") == "2026-12-05"

# 10. Test Due Follow-Ups
print("\n--- Due Follow-Ups Listing ---")
d = api("GET", "/api/leads/due-follow-ups", tok=owner_tok)
assert d.get("count", 0) >= 1
print(f"  Due follow-ups count: {d.get('count')}")

# 11. Test CSV Exports
print("\n--- CSV Exports ---")
d = api("GET", "/api/leads/export", tok=owner_tok)
assert "company" in d.get("csv", "")
print("  Leads CSV export: OK")

d = api("GET", "/api/finance/expenses/export", tok=owner_tok)
assert "category" in d.get("csv", "")
print("  Expenses CSV export: OK")

d = api("GET", "/api/sites/export", tok=owner_tok)
assert "code" in d.get("csv", "")
print("  Sites CSV export: OK")

d = api("GET", "/api/employees/export", tok=owner_tok)
assert "employee_id" in d.get("csv", "")
print("  Employees CSV export: OK")

# 12. Test AI Brain Task Create & Execute with real tool execution
print("\n--- AI Brain Task & Tool Execution ---")
# Create task requesting workspace:list and resource:list
d = api("POST", "/api/ai-brain/tasks", {
    "agent_id": 1,
    "title": "Automated Survey & Workspace Inspection",
    "description": "Inspect available workspace resources and sites",
    "priority": "high",
    "tool_requests": [["workspace:list", {}], ["resource:list", {}], ["sites:read", {}]]
}, tok=owner_tok, expected=201)
task_id = d.get("task", {}).get("id")
assert task_id, f"Task creation failed: {d}"
print(f"  Task #{task_id} created")

# Execute the task
d = api("POST", f"/api/ai-brain/tasks/{task_id}/execute", tok=owner_tok)
task = d.get("task", {})
print(f"  Task execution status: {task.get('status')}")
assert task.get("status") == "completed", f"Task execution failed: {task}"

# Check tool executions log
d = api("GET", f"/api/ai-brain/tasks/{task_id}/executions", tok=owner_tok)
execs = d.get("executions", [])
print(f"  Recorded tool executions: {len(execs)}")
assert len(execs) >= 3, f"Expected 3 tool executions, got {len(execs)}"

# 13. Test Password Complexity Validation
print("\n--- Security: Password Complexity Validation ---")
# Simple password should be rejected with 400
d = api("POST", "/api/auth/password", {"old_password": "demo-owner-pass-0001", "new_password": "short"}, tok=owner_tok, expected=400)
print(f"  Short password rejected: {'error' in d}")

print(f"\n{'='*60}")
print(f"PAYROLL & ADVANCED FEATURES TEST RESULTS: {PASS} PASS, {FAIL} FAIL")
print(f"{'='*60}")
if FAIL > 0:
    sys.exit(1)
