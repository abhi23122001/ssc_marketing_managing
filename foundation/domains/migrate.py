"""One-time domain schema creation and synthetic demo-seed.

Domain tables live alongside the core store tables in the same SQLite file.
They are created once (idempotent) and are never modified by later migrations.
Demo seeding is synthetic only and is guarded by an idempotent flag so a running
system is never re-seeded on every Store() construction.
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta

from .m19_schema import create_m19_tables, seed_m19_demo

_DOMAIN_SCHEMA = """
CREATE TABLE IF NOT EXISTS departments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workspace_id TEXT,
    code TEXT UNIQUE NOT NULL,
    label TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workspace_id TEXT,
    employee_id TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    designation TEXT NOT NULL DEFAULT '',
    department_id INTEGER,
    hire_date TEXT NOT NULL DEFAULT '',
    resignation_date TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'active',  -- active, resigned, left
    email TEXT NOT NULL DEFAULT '',
    phone TEXT NOT NULL DEFAULT '',
    manager_id INTEGER,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE SET NULL,
    FOREIGN KEY (manager_id) REFERENCES employees(id) ON DELETE SET NULL
);
CREATE TABLE IF NOT EXISTS employee_documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER NOT NULL,
    doc_type TEXT NOT NULL,
    doc_url TEXT NOT NULL DEFAULT '',
    uploaded_by INTEGER NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS leaves (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER NOT NULL,
    type TEXT NOT NULL DEFAULT 'annual',  -- annual, sick, casual, leave_without_pay
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    days REAL NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'applied',  -- applied, approved, rejected, carried
    approved_by INTEGER,
    reason TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE,
    FOREIGN KEY (approved_by) REFERENCES employees(id) ON DELETE SET NULL
);
CREATE TABLE IF NOT EXISTS sites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workspace_id TEXT,
    name TEXT NOT NULL,
    code TEXT UNIQUE NOT NULL,
    address TEXT NOT NULL DEFAULT '',
    geofence_radius_m REAL NOT NULL DEFAULT 100,
    field_policy_required INTEGER NOT NULL DEFAULT 0,  -- 1 = GPS/selfie/geofencing mandatory
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS geofences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    site_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    polygon_json TEXT NOT NULL DEFAULT '{}',
    enabled INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (site_id) REFERENCES sites(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS attendance_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workspace_id TEXT,
    employee_id INTEGER NOT NULL,
    site_id INTEGER NOT NULL,
    check_in TEXT NOT NULL,
    check_out TEXT NOT NULL DEFAULT '',
    gps_lat REAL NOT NULL DEFAULT 0,
    gps_lng REAL NOT NULL DEFAULT 0,
    geofence_passed INTEGER NOT NULL DEFAULT 0,
    selfie_taken INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'present',  -- present, absent, late, early, no_show
    notes TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE,
    FOREIGN KEY (site_id) REFERENCES sites(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS cash_advance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workspace_id TEXT,
    employee_id INTEGER NOT NULL,
    amount REAL NOT NULL DEFAULT 0,
    currency TEXT NOT NULL DEFAULT 'INR',
    status TEXT NOT NULL DEFAULT 'advanced',  -- advanced, settled, partially_settled
    advance_date TEXT NOT NULL DEFAULT (datetime('now')),
    settled_at TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS expense_claims (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workspace_id TEXT,
    employee_id INTEGER NOT NULL,
    project_id TEXT NOT NULL DEFAULT '',
    category TEXT NOT NULL DEFAULT 'travel',  -- travel, food_lodging, fuel, site_expense, equipment_maintenance, other
    amount REAL NOT NULL DEFAULT 0,
    currency TEXT NOT NULL DEFAULT 'INR',
    receipt_url TEXT NOT NULL DEFAULT '',
    cash_advance_id INTEGER,
    status TEXT NOT NULL DEFAULT 'submitted',  -- submitted, pending_approval, approved, rejected, settled
    submitted_by INTEGER NOT NULL,
    notes TEXT NOT NULL DEFAULT '',
    submitted_at TEXT NOT NULL DEFAULT (datetime('now')),
    approved_by INTEGER,
    approved_at TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS expense_vendors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workspace_id TEXT,
    name TEXT NOT NULL,
    category TEXT NOT NULL DEFAULT 'vendor',
    contact TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS payroll_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workspace_id TEXT,
    run_month TEXT NOT NULL,
    period TEXT NOT NULL DEFAULT 'monthly',
    run_by INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'draft',  -- draft, ready, approved
    total_gross REAL NOT NULL DEFAULT 0,
    total_deductions REAL NOT NULL DEFAULT 0,
    total_in_hand REAL NOT NULL DEFAULT 0,
    ledger_snapshot TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    processed_at TEXT,
    FOREIGN KEY (run_by) REFERENCES employees(id) ON DELETE SET NULL
);
CREATE TABLE IF NOT EXISTS payslips (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    payroll_run_id INTEGER NOT NULL,
    employee_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    month TEXT NOT NULL,
    gross REAL NOT NULL DEFAULT 0,
    deductions REAL NOT NULL DEFAULT 0,
    in_hand REAL NOT NULL DEFAULT 0,
    report_url TEXT NOT NULL DEFAULT '',
    generated_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (payroll_run_id) REFERENCES payroll_runs(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS ai_agents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workspace_id TEXT,
    code TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    agent_type TEXT NOT NULL DEFAULT 'general',
    tool_access TEXT NOT NULL DEFAULT '{}',
    status TEXT NOT NULL DEFAULT 'active',
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS ai_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workspace_id TEXT,
    agent_id INTEGER,
    title TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    priority TEXT NOT NULL DEFAULT 'medium',
    assigned_to INTEGER,
    status TEXT NOT NULL DEFAULT 'open',  -- open, in_progress, completed, blocked, cancelled
    result_summary TEXT NOT NULL DEFAULT '',
    audit_note TEXT NOT NULL DEFAULT '',
    tool_requests TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    started_at TEXT,
    completed_at TEXT,
    FOREIGN KEY (agent_id) REFERENCES ai_agents(id) ON DELETE SET NULL,
    FOREIGN KEY (assigned_to) REFERENCES employees(id) ON DELETE SET NULL
);
CREATE TABLE IF NOT EXISTS ai_tool_executions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ai_task_id INTEGER,
    tool_name TEXT NOT NULL,
    args TEXT NOT NULL DEFAULT '{}',
    allowed INTEGER NOT NULL DEFAULT 0,
    result TEXT NOT NULL DEFAULT '{}',
    executed_by INTEGER,
    started_at TEXT NOT NULL DEFAULT (datetime('now')),
    completed_at TEXT,
    FOREIGN KEY (ai_task_id) REFERENCES ai_tasks(id) ON DELETE CASCADE,
    FOREIGN KEY (executed_by) REFERENCES employees(id) ON DELETE SET NULL
);
""".lstrip()


def create_domain_tables(conn) -> None:
    """Create every domain table only if it is absent."""
    if conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name='departments'"
    ).fetchone():
        return
    conn.executescript(_DOMAIN_SCHEMA)
    conn.commit()


# ---------------------------------------------------------------------------
# Synthetic demo seed (idempotent). Synthetic data ONLY.
# ---------------------------------------------------------------------------
_DEMO_DEPARTMENTS = [
    {"code": "ENG", "label": "Engineering"},
    {"code": "HR", "label": "Human Resources"},
    {"code": "FIN", "label": "Finance"},
    {"code": "OPS", "label": "Operations"},
]

_DEMO_EMPLOYEES = [
    # SSC workspace sample
    {"employee_id": "SSC-001", "name": "Aarav Sharma", "designation": "Survey Team Lead",
     "department": "ENG", "hire_date": "2024-03-01", "email": "aarav.sharma@ssc.example", "phone": "+91 98765 01001"},
    {"employee_id": "SSC-002", "name": "Baanu Devi", "designation": "Surveyor (Field)",
     "department": "ENG", "hire_date": "2024-06-15", "email": "baanu.devi@ssc.example", "phone": "+91 98765 01002"},
    {"employee_id": "SSC-003", "name": "Chetan Patil", "designation": "Junior Surveyor",
     "department": "ENG", "hire_date": "2025-01-10", "email": "chetan.patil@ssc.example", "phone": "+91 98765 01003"},
    {"employee_id": "SSC-004", "name": "Divya Iyer", "designation": "HR Manager",
     "department": "HR", "hire_date": "2024-01-20", "email": "divya.iyer@ssc.example", "phone": "+91 98765 01004"},
    {"employee_id": "SSC-005", "name": "Eshan Rao", "designation": "Finance Officer",
     "department": "FIN", "hire_date": "2024-05-01", "email": "eshan.rao@ssc.example", "phone": "+91 98765 01005"},
    {"employee_id": "SSC-006", "name": "Fatima Khan", "designation": "Site Supervisor",
     "department": "OPS", "hire_date": "2024-08-12", "email": "fatima.khan@ssc.example", "phone": "+91 98765 01006"},
    # INFRA workspace sample
    {"employee_id": "INF-001", "name": "Gopal Mishra", "designation": "Site Engineer",
     "department": "ENG", "hire_date": "2024-02-01", "email": "gopal.mishra@infra.example", "phone": "+91 98765 02001"},
    {"employee_id": "INF-002", "name": "Hari Prasad", "designation": "Foreman",
     "department": "OPS", "hire_date": "2024-04-15", "email": "hari.prasad@infra.example", "phone": "+91 98765 02002"},
]

_DEMO_SITES = [
    {"name": "SSC-Kothi Site", "code": "SSC-SITE-01", "address": "Kothi, Singrauli, MP", "geofence_radius_m": 150.0, "field_policy_required": 1},
    {"name": "SSC-Mahuwa Site", "code": "SSC-SITE-02", "address": "Mahuwa, Singrauli, MP", "geofence_radius_m": 100.0, "field_policy_required": 1},
    {"name": "INFRA-Waidhan Site", "code": "INF-SITE-01", "address": "Waidhan, MP", "geofence_radius_m": 200.0, "field_policy_required": 1},
]

_DEMO_CLAIMS = [
    # (workspace, title, category, amount) - note: participant ids start at 1 here
    ("SSC", "Field travel - Mahuwa", "travel", 1250.0),
    ("SSC", "Lodging - survey camp", "food_lodging", 3400.0),
    ("SSC", "Fuel - survey team", "fuel", 2100.0),
    ("INFRA", "Site materials - Waidhan", "site_expense", 8700.0),
    ("INFRA", "Equipment maintenance", "equipment_maintenance", 5600.0),
]

_DEMO_LEAVES = [
    ("annual", "2026-11-02", "2026-11-03", 2.0, "approved"),
    ("annual", "2026-11-16", "2026-11-17", 2.0, "approved"),
    ("sick", "2026-12-10", "2026-12-10", 1.0, "approved"),
    ("casual", "2027-01-05", "2027-01-05", 1.0, "rejected"),
]

_DEMO_PAYROLL = [
    ("SSC", "2027-01", 10000.0, 800.0, 9200.0, "ready"),
    ("INFRA", "2027-01", 18000.0, 1500.0, 16500.0, "draft"),
]


def seed_domain_demo(conn, workspaces) -> None:
    """Seed synthetic HR/attendance/expense/payroll demo data.
    workspaces: list of workspace dicts from the store (for scoping seed rows).
    """
    ws_by_code = {w["code"]: w["id"] for w in workspaces}

    # departments per workspace
    for code, label in _DEMO_DEPARTMENTS:
        for w in workspaces:
            conn.execute(
                "INSERT OR IGNORE INTO departments (workspace_id, code, label) VALUES (?, ?, ?)",
                (w["id"], code, label))

    emp_rows = []
    # Demo employees carry a short namespace prefix ("SSC", "INF", ...).
    # Map each namespace prefix to its business workspace code.
    _EMP_PREFIX = [
        ("SSC", "SSC"),
        ("INF", "INFRA"),
    ]
    for e in _DEMO_EMPLOYEES:
        prefix = e["employee_id"].split("-")[0]
        target_code = None
        for ns, code in _EMP_PREFIX:
            if prefix == ns:
                target_code = code
                break
        if target_code is None:
            continue
        target_ws = next((w for w in workspaces if w["code"] == target_code), None)
        if target_ws is None:
            continue
        cur = conn.execute(
            "SELECT id FROM employees WHERE employee_id=?",
            (e["employee_id"],)).fetchone()
        if not cur:
            conn.execute(
                "INSERT INTO employees (workspace_id, employee_id, name, designation, "
                "department_id, hire_date, email, phone) VALUES (?,?,?,?,?,?,?,?)",
                (target_ws["id"], e["employee_id"], e["name"], e["designation"],
                 None, e["hire_date"], e["email"], e["phone"]))
            cur = conn.execute(
                "SELECT id FROM employees WHERE employee_id=?", (e["employee_id"],)).fetchone()
        emp_rows.append({"id": cur["id"], "code": target_code,
                         "name": e["name"], "workspace_id": target_ws["id"]})

    # leaves (synthetic)
    for emp in emp_rows:
        for etype, d0, d1, days, status in _DEMO_LEAVES:
            conn.execute(
                "INSERT INTO leaves (employee_id, type, start_date, end_date, days, status, reason) "
                "VALUES (?,?,?,?,?,?,?)",
                (emp["id"], etype, d0, d1, days, status, "synthetic demo"))

    # sites
    site_rows = []
    for s in _DEMO_SITES:
        for w in workspaces:
            if w["code"] == "SSC" and s["code"].startswith("INF"):
                continue
            if w["code"] == "INFRA" and not s["code"].startswith("INF"):
                continue
            cur = conn.execute(
                "SELECT id FROM sites WHERE code=?", (s["code"],)).fetchone()
            if not cur:
                conn.execute(
                    "INSERT INTO sites (workspace_id, name, code, address, geofence_radius_m, field_policy_required) "
                    "VALUES (?,?,?,?,?,?)",
                    (w["id"], s["name"], s["code"], s["address"],
                     s["geofence_radius_m"], s["field_policy_required"]))
                cur = conn.execute(
                    "SELECT id FROM sites WHERE code=?", (s["code"],)).fetchone()
            site_rows.append({"id": cur["id"], "code": s["code"], "workspace_id": w["id"],
                              "policy": bool(s["field_policy_required"])})

    # attendance (synthetic check-ins for the current week; geofencing + selfie)
    if site_rows:
        now = datetime.now()
        d0 = now.replace(hour=9, minute=0, second=0, microsecond=0) - timedelta(days=now.weekday())
        rows = []
        for s in site_rows:
            for emp in emp_rows:
                if s["code"] != "INF-SITE-01" and emp["code"] != "SSC":
                    continue
                if s["code"] == "INF-SITE-01" and emp["code"] != "INFRA":
                    continue
                ci = d0 + timedelta(days=site_rows.index(s) % 3, hours=site_rows.index(s) % 2)
                co = ci + timedelta(hours=8, minutes=30)
                rows.append((emp["workspace_id"], emp["id"], s["id"], ci.isoformat(), co.isoformat(),
                             24.98, 83.04, 1, 1, "present"))
        conn.executemany(
            "INSERT INTO attendance_logs (workspace_id, employee_id, site_id, check_in, check_out, gps_lat, gps_lng, geofence_passed, selfie_taken, status) "
            "VALUES (?,?,?,?,?,?,?,?,?,?)",
            rows)

    # expense claims
    for wcode, title, category, amount in _DEMO_CLAIMS:
        for w in workspaces:
            if w["code"] != wcode:
                continue
            emp = next((e for e in emp_rows if e["code"] == wcode), None)
            if not emp:
                continue
            cur = conn.execute(
                "SELECT id FROM expense_vendors ORDER BY id LIMIT 1").fetchone()
            vendor_id = cur["id"] if cur else None
            cur = conn.execute(
                "INSERT INTO expense_claims (workspace_id, employee_id, project_id, category, amount, currency, receipt_url, cash_advance_id, submitted_by, submitted_at) "
                "VALUES (?,?,?,?,?,?,?,?,?,?)",
                (w["id"], emp["id"], "PRJ-01", category, amount, "INR",
                 "receipt://synthetic/" + title, None, emp["id"], datetime.now().isoformat()))
            emp["last_claim"] = cur.lastrowid

    # payroll runs
    for wcode, month, gross, ded, in_hand, status in _DEMO_PAYROLL:
        for w in workspaces:
            if w["code"] != wcode:
                continue
            emp = next((e for e in emp_rows if e["code"] == wcode), None)
            if emp is None:
                continue
            cur = conn.execute(
                "INSERT INTO payroll_runs (workspace_id, run_month, period, run_by, status) "
                "VALUES (?,?,?,?,?)",
                (w["id"], month, "monthly", emp["id"], status))
            conn.execute(
                "INSERT INTO payslips (payroll_run_id, employee_id, name, month, gross, deductions, in_hand, report_url) "
                "VALUES (?,?,?,?,?,?,?,?)",
                (cur.lastrowid, emp["id"], emp["name"], month, gross, ded, in_hand,
                 "payslip://synthetic/" + month))

