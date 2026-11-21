# SHAH GROUP AI OS — Clean Domain Rebuild Report (M15–M18 + SHAH AI Brain)

**Status: COMPLETE** — Store layer structurally correct, foundation tests 42/42 PASS,
domain modules implemented, smoke-tested and verified with workspace isolation.

**Date: 2026-11-18**

## 1. Objective

Build a clean, working replacement for the broken HR/Attendance/Expense/Payroll
domain implementation, so that M15 (HR/Employee), M16 (Attendance/Workforce),
M17 (Expense/Reimbursement) and M18 (Payroll/Salary) plus the SHAH AI Brain
foundation work correctly inside the existing SHAH GROUP AI OS, with:

- Store layer structurally correct (py_compile passes).
- Domain modules M15–M18 + SHAH AI Brain implemented and smoke-tested.
- Workspace isolation and RBAC enforced (no hard-coded workspaces).
- All progress documented.

## 2. What was found

The existing `foundation/store.py` contained a working core (lines 1–358) overlaid
with appended broken domain CRUD code (lines 359–997):

- `_is_owner()` hard-coded `"SSC"` as the workspace.
- `_current_workspace_id()` hard-coded `"SSC"`.
- `_domain_scope()` was left empty.
- `_domain_list` was defined twice — once empty, once with the wrong body.
- `_json_table_creates` referenced `re` without importing it.
- `add_audit()` / `list_audit()` were flattened as nested module functions
  (indentation broken), and a duplicate `json_dumps` collided.
- `expense.py` missed `cash_advance_id`; `payroll.py` summary logic had bugs;
  `ai_brain.py` had broken local helper duplicates; `attendance_logs` lacked
  `workspace_id`; `employee.list_leaves` raised KeyError.

## 3. What was rebuilt

### 3a. Store layer — `foundation/store.py`

The broken appended block was removed. The file was reduced to a clean 365-line
`Store` class containing:

- `users`, `roles`, `sessions`, `resources`, `approvals`, `audit_logs`,
  `employee_workspaces`, `employee_urls`, `employee_links` (core tables).
- Module-level `json_dumps` / `now_iso` / `_pbkdf2` helpers.
- Class methods `add_audit()` / `list_audit()` (limit-aware).

**Result:** py_compile exits 0. No embedded domain code.

### 3b. Domain service modules — `foundation/domains/`

| File | Module | What it implements |
|---|---|---|
| `__init__.py` | package re-exports | `create_domain_tables`, `seed_domain_demo`, `employee`, `attendance`, `expense`, `payroll`, `ai_brain`, `migrate`, `shared` |
| `migrate.py` | schema + seed | `create_domain_tables()` (idempotent), `seed_domain_demo()` (idempotent, synthetic data) |
| `shared.py` | workspace/shared | `workspace_exists()`, `workspace_or_404()`, `_assert_owned()`, `_audit()`, `_json_dumps()`, `_now_iso()`, `param_quote()` |
| `employee.py` | **M15** | departments, designations, employee profiles + unique IDs, joining/resignation metadata, salary structure, status, leave records |
| `attendance.py` | **M16** | check-in/check-out, GPS + selfie evidence, site-wise attendance, geofencing, late/early/overtime, holidays/weekly off, manager approval |
| `expense.py` | **M17** | expense vendors, travel/fuel/food/lodging/site/equipment expenses, receipts metadata, claims, cash advance + settlement, approval workflow, budget |
| `payroll.py` | **M18** | payroll runs, payslips, `calculate_payroll()`, summary, advances/deductions, reconciliation |
| `ai_brain.py` | SHAH AI Brain | tool allowlist, agent routing (SSC/INFRA/OTHER), alerts (attendance/expense/payroll), approval workflow |

### 3c. Seed data

`seed_domain_demo()` seeds the `data/sgcc_foundation.sqlite` database:

- Workspaces: `SSC` (Shah Surveyors & Consultancy), `INFRA` (Shah Infra), `OTHER`.
- Demo users: Owner, Manager, HR Manager, Finance Manager, Employee, Viewer, plus
  demo employees cross-scoped per workspace (prefix-based, each employee in exactly
  one workspace).
- Departments, sites, attendance, claims, payroll runs — all synthetic, all
  workspace-scoped.

## 4. Test evidence

### 4a. py_compile

    python3 -m py_compile foundation/store.py            → exit 0
    python3 -m py_compile foundation/domains/*.py        → COMPILE_OK (7 files)

### 4b. Foundation test battery

    python3 foundation/tests/run_foundation_tests.py
    TOTAL: 42   PASS: 42   FAIL: 0   LOG: docs/TEST-RESULTS.md
    → exit 0, no FAIL lines

### 4c. Domain smoke test

    SMOKE OK: emp 1 claims 1 | alerts 0 1 1

Covered: employee/department creation, leave, site creation, check-in, geofence
policy enforcement, payroll attendance summary, AI-brain alerts.

### 4d. Workspace isolation test

Cross-workspace checks performed and passed:

- Owner (Owner role) reaches all workspaces (consolidated).
- A non-owner member is blocked from another workspace's data.
- Cross-workspace leave creation raises `PermissionError`.
- Attendance records are scoped by `workspace_id`.
- Owner consolidated report returns totals spanning `SSC` + `INFRA`.

## 5. Security and isolation rules applied

- Workspace context comes from the authenticated request — never hardcoded.
- `Owner` (code "Owner") may access all authorized workspaces; members are
  restricted to their own workspace.
- All employee/site/expense/payroll updates use fixed allowlisted column names
  and parameterized SQL.
- No arbitrary user-controlled SQL column names in `update_employee`.
- RBAC/approval/audit are never bypassed.
- All domain functions require `workspace_id`; no hardcoded `"SSC"` anywhere.
- `ai_brain.py` uses a fixed tool allowlist; sensitive operations require
  explicit allowlist + owner approval.
- Demo data is synthetic. No real bank transfers, payments, or external
  communications.

## 6. Integration status

The owner dashboard (`foundation/dashboard/dashboard.html`) is wired to the
backend through `_handle_dashboard` (`/api/dashboard/overview|projects|finance|
employees|marketing|crm|approvals|settings|ai`) in `foundation/api.py`.
A real-HTTP verification verified **13/13 checks PASS**, including the dashboard
endpoints and the `auth/me` endpoint shape.

Remaining (Phase 6A/6B items, separate from the foundation platform):

1. Full UI on top of the dashboard shell.
2. CRM <-> foundation sync bridge (`data/leads.csv` to SQLite).
3. Approval escalation / balance-holder rules (`approval.py` TODO).
4. Report generation (`report:list`, `report:read` roles).
5. AI-brain tool wiring (`ai:brain:query`).

## 7. Files changed (this session)

Added (clean rebuild):

- `foundation/domains/__init__.py`
- `foundation/domains/migrate.py`
- `foundation/domains/shared.py`
- `foundation/domains/employee.py`
- `foundation/domains/attendance.py`
- `foundation/domains/expense.py`
- `foundation/domains/payroll.py`
- `foundation/domains/ai_brain.py`

Patched (bug fixes):

- `foundation/store.py` — removed broken app-level domain code, reduced to clean
  365-line Store; `list_audit` now accepts optional `limit`; `json_dumps` at
  module level; `add_audit`/`list_audit` restored as class methods.
- `foundation/domains/migrate.py` — seed cursor/lastrowid and column fixes.
- `foundation/domains/employee.py` — `list_leaves` workspace resolution.
- `foundation/domains/attendance.py` — `summary_monthly` aggregation fix;
  `record_checkin` inserts `workspace_id`.
- `foundation/domains/expense.py` — `datetime`/`_now_iso`; `settle_cash_advance`.
- `foundation/domains/payroll.py` — `calculate_payroll` overtime loop fix;
  `compute_overtime`/`compute_worked_hours` imports.
- `foundation/domains/ai_brain.py` — shared-import refactor; alert ORDER BY fix.

## 8. Confirmation

- Store layer structurally correct: py_compile exit 0, no embedded domain code.
- Core tests green: 42/42 PASS.
- Domain modules implemented and smoke-tested.
- Workspace isolation and RBAC enforced.
- All progress documented in `docs/AUTONOMOUS-DEVELOPMENT-REPORT.md` (overall)
  and this report.
