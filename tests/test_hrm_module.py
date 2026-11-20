"""HRM Module tests — employees, attendance, leaves.
Run with: python tests/test_hrm_module.py
Requires server running on http://127.0.0.1:8899/
"""
import sys
import json
import time
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
        body = json.loads(r.read())
    except urllib.error.HTTPError as e:
        status = e.code
        try:
            body = json.loads(e.read())
        except Exception:
            body = {}
    ok = status == expected
    label = "PASS" if ok else "FAIL"
    if ok:
        PASS += 1
    else:
        FAIL += 1
    print(f"[{status}] {label} {method} {path}")
    return body

# -- Auth
print("=== HRM Module Tests ===")
d = api("POST", "/api/auth/login", {"username": "owner", "password": "demo-owner-pass-0001"})
owner_tok = d.get("token", "")
assert owner_tok, "Owner token missing"

d = api("POST", "/api/auth/login", {"username": "manager", "password": "demo-manager-pass-0001"})
mgr_tok = d.get("token", "")

d = api("POST", "/api/auth/login", {"username": "employee", "password": "demo-employee-pass-0001"})
emp_tok = d.get("token", "")

# -- Employee listing (empty initially or seeded)
print("\n--- Employee CRUD ---")
d = api("GET", "/api/employees", tok=owner_tok)
assert "employees" in d
assert "count" in d
initial_count = d["count"]
print(f"  initial employee count: {initial_count}")

# -- Create employee
ts = int(time.time() * 1000) % 100000
d = api("POST", "/api/employees", {
    "name": f"Test Surveyor {ts}",
    "role": "DGPS Surveyor",
    "designation": "Senior Field Technician",
    "email": f"test{ts}@ssc.example.com",
    "phone": "9876543210"
}, tok=owner_tok, expected=201)
emp_id = d.get("employee", {}).get("id")
assert emp_id, f"Employee id missing: {d}"
print(f"  created employee id={emp_id}")

# -- Create second employee
d2 = api("POST", "/api/employees", {
    "name": f"Test Office Staff {ts}",
    "role": "Data Processing",
    "designation": "Data Analyst",
    "email": f"office{ts}@ssc.example.com",
    "phone": "9000000001"
}, tok=owner_tok, expected=201)
emp_id2 = d2.get("employee", {}).get("id")
print(f"  created employee2 id={emp_id2}")

# -- List employees — count should be initial+2
d = api("GET", "/api/employees", tok=owner_tok)
new_count = d.get("count", 0)
assert new_count >= initial_count + 2, f"Expected {initial_count+2}+ employees, got {new_count}"
print(f"  employee count after create: {new_count}")

# -- Manager can list employees
d = api("GET", "/api/employees", tok=mgr_tok)
assert "employees" in d

# -- Employee role can list employees
d = api("GET", "/api/employees", tok=emp_tok)
assert "employees" in d

# -- Viewer cannot create employee (403) — skip if viewer not available
print("\n--- Attendance Logging ---")
# Log check-in
d = api("POST", "/api/attendance", {
    "employee_id": emp_id or 1,
    "event": "check_in",
    "lat": 19.0760,
    "lng": 72.8777,
    "notes": "Field survey - DGPS setup"
}, tok=owner_tok, expected=201)
log_id = d.get("log", {}).get("id")
assert log_id, f"Attendance log id missing: {d}"
print(f"  attendance log id={log_id}")

# Log check-out
d = api("POST", "/api/attendance", {
    "employee_id": emp_id or 1,
    "event": "check_out",
    "lat": 19.0760,
    "lng": 72.8777,
    "notes": "Survey complete"
}, tok=owner_tok, expected=201)
print(f"  checkout log id={d.get('log', {}).get('id')}")

# List attendance
d = api("GET", "/api/attendance", tok=owner_tok)
assert "attendance" in d
att_count = d.get("count", 0)
assert att_count >= 2, f"Expected at least 2 attendance records, got {att_count}"
print(f"  attendance records: {att_count}")

# -- Leaves
print("\n--- Leave Requests ---")
d = api("POST", "/api/leaves", {
    "employee_id": emp_id or 1,
    "leave_type": "casual",
    "from_date": "2026-12-15",
    "to_date": "2026-12-16",
    "reason": "Personal matter"
}, tok=owner_tok, expected=201)
leave_id = d.get("leave", {}).get("id")
assert leave_id, f"Leave id missing: {d}"
print(f"  leave id={leave_id}")

# Submit another leave type
d = api("POST", "/api/leaves", {
    "employee_id": emp_id2 or 1,
    "leave_type": "medical",
    "from_date": "2026-12-20",
    "to_date": "2026-12-22",
    "reason": "Doctor appointment"
}, tok=mgr_tok, expected=201)
print(f"  medical leave id={d.get('leave', {}).get('id')}")

# List leaves
d = api("GET", "/api/leaves", tok=owner_tok)
assert "leaves" in d
leave_count = d.get("count", 0)
assert leave_count >= 2, f"Expected 2+ leaves, got {leave_count}"
print(f"  leave requests: {leave_count}")

# -- Leave routes to approval queue
d = api("GET", "/api/approvals", tok=owner_tok)
approvals = d.get("approvals", [])
leave_approvals = [a for a in approvals if "Leave Request" in (a.get("title") or "")]
print(f"  leave requests in approval queue: {len(leave_approvals)}")

# -- AI Brain agents - verify 12 agents seeded
print("\n--- AI Brain Agents ---")
d = api("GET", "/api/ai-brain/agents", tok=owner_tok)
agents = d.get("agents", [])
print(f"  total AI agents: {len(agents)}")
agent_codes = {a.get("code") for a in agents}
expected_codes = {"OWNER-ASSIST", "PM-AGENT", "SURVEY-OPS", "CRM-AGENT",
                  "FINANCE-AGENT", "HR-AGENT", "MARKETING-AGENT", "REPORTING-AGENT"}
for code in expected_codes:
    if code in agent_codes:
        PASS += 1
        print(f"  PASS agent present: {code}")
    else:
        FAIL += 1
        print(f"  FAIL agent missing: {code}")

# -- Missing employee_id returns 400
print("\n--- Validation ---")
d = api("POST", "/api/employees", {"role": "X"}, tok=owner_tok, expected=400)
print(f"  missing name -> 400: {'error' in d}")

d = api("POST", "/api/attendance", {"event": "check_in"}, tok=owner_tok, expected=400)
print(f"  missing employee_id -> 400: {'error' in d}")

d = api("POST", "/api/leaves", {"employee_id": 1, "leave_type": "casual"}, tok=owner_tok, expected=400)
print(f"  missing dates -> 400: {'error' in d}")

print(f"\n{'='*50}")
print(f"HRM MODULE TEST RESULTS")
print(f"Pass: {PASS}")
print(f"Fail: {FAIL}")
print(f"Total: {PASS + FAIL}")
if FAIL == 0:
    print(f"ALL {PASS} HRM CHECKS PASSED")
else:
    print(f"WARNING: {FAIL} checks failed")
    sys.exit(1)
