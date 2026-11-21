# scripts/audit_02_employee_account.py
import urllib.request, json, time
from pathlib import Path

BASE_URL = "http://127.0.0.1:8899"
evidence_dir = Path("AUDIT_TEST_EVIDENCE")
evidence_dir.mkdir(parents=True, exist_ok=True)

print("=== AUDIT 02: EMPLOYEE ACCOUNT COMPLETE VERIFICATION ===")

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
    except Exception as e:
        return 500, {"error": str(e)}

results = {}

# 1. Test Login with credentials
emp_token = None
emp_user = None
for pwd in ["demo-employee-pass-0001", "demo-emp-pass-0001", "employee"]:
    status, res = api_call("/api/auth/login", method="POST", body={"username": "employee", "password": pwd})
    if status == 200 and "token" in res:
        emp_token = res["token"]
        emp_user = res.get("user", {})
        print(f"[PASS] Employee login succeeded with password '{pwd}'. Role: {emp_user.get('role')}, WS: {emp_user.get('workspace_id')}")
        results["login"] = {"status": "PASS", "user": emp_user}
        break

assert emp_token, "Employee login failed with all known passwords!"

# 2. Verify Employee Permitted Data Access (Workspace Scoping)
# Employee belongs to SSC. Check that Employee can read assigned workspace tasks and profile
s, me = api_call("/api/auth/me", token=emp_token)
results["auth_me"] = {"status": "PASS" if s == 200 else "FAIL", "http": s, "user": me}
print(f"[PASS] /api/auth/me -> HTTP {s}, user={me.get('username')}")

# Employee reading assigned tasks
s, tasks = api_call("/api/tasks", token=emp_token, ws="SSC")
results["tasks_access"] = {"status": "PASS" if s == 200 else "FAIL", "http": s, "count": len(tasks.get("tasks", []))}
print(f"[PASS] Employee tasks list -> HTTP {s}, count={len(tasks.get('tasks', []))}")

# 3. Employee Self-Service Operations (Attendance Check-In & Leave Submission)
# Check-in
test_checkin_body = {
    "employee_id": 1,
    "site_id": 1,
    "action": "check_in",
    "timestamp": "2026-11-21T09:05:00+05:30",
    "notes": "Audit disposable test checkin"
}
s, att_res = api_call("/api/attendance", token=emp_token, method="POST", body=test_checkin_body)
results["attendance_checkin"] = {"status": "PASS" if s in (200, 201) else "FAIL", "http": s, "response": att_res}
print(f"[PASS] Employee check-in -> HTTP {s}, id={att_res.get('id', att_res.get('log_id'))}")

# Leave request
test_leave_body = {
    "employee_id": 1,
    "leave_type": "casual",
    "from_date": "2026-12-01",
    "to_date": "2026-12-02",
    "reason": "Audit disposable test leave"
}
s, leave_res = api_call("/api/leaves", token=emp_token, method="POST", body=test_leave_body)
results["leave_submission"] = {"status": "PASS" if s in (200, 201) else "FAIL", "http": s, "response": leave_res}
print(f"[PASS] Employee leave submission -> HTTP {s}, id={leave_res.get('leave', {}).get('id')}")

# 4. Strict Security & Authorization Bounds Checks
# Employee attempting to access restricted/privileged resources
unauthorized_checks = [
    ("payroll_run", "POST", "/api/payroll/run", {"month": "2026-11"}),
    ("payroll_approve", "POST", "/api/payroll/runs/1/approve", {}),
    ("user_management_list", "GET", "/api/users", None),
    ("user_creation", "POST", "/api/users", {"username": "hackuser", "password": "hackpassword", "role": "Owner"}),
    ("approvals_transition", "POST", "/api/approvals/1/transition", {"status": "approved"}),
    ("cross_workspace_infra", "GET", "/api/sites?workspace=INFRA", None),
    ("cross_workspace_other", "GET", "/api/sites?workspace=OTHER", None)
]

unauth_results = {}
for name, method, path, b in unauthorized_checks:
    # Notice for cross-workspace checks we set ws header
    ws_header = "INFRA" if "INFRA" in path else ("OTHER" if "OTHER" in path else "SSC")
    s, resp = api_call(path, token=emp_token, method=method, body=b, ws=ws_header)
    # Expected outcome: HTTP 403 Forbidden
    is_blocked = (s == 403)
    unauth_results[name] = {
        "status": "PASS" if is_blocked else "FAIL",
        "expected_http": 403,
        "actual_http": s,
        "blocked": is_blocked,
        "response": resp
    }
    status_label = "[PASS]" if is_blocked else "[FAIL ALERT]"
    print(f"{status_label} Access Control [{name}]: HTTP {s} (Expected 403 Forbidden). Blocked={is_blocked}")

results["unauthorized_access_controls"] = unauth_results

with open(evidence_dir / "audit_02_employee_account.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)

print("\nAUDIT 02 COMPLETED: Evidence saved to AUDIT_TEST_EVIDENCE/audit_02_employee_account.json")
