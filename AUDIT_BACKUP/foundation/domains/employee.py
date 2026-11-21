"""M15 Employee Management.

Employee profiles with unique employee IDs, departments/designations, joining
and resignation records, employment document metadata, salary structure, leave
records. All operations are workspace-scoped; the workspace_id comes from the
authenticated request.
"""
from __future__ import annotations

from ..store import Store

ALLOWED_EMPLOYEE_FIELDS = {
    "designation", "department_id", "hire_date", "resignation_date",
    "status", "email", "phone", "manager_id",
}


def _workspace_exists(store: Store, workspace_id: str) -> bool:
    return store.conn.execute(
        "SELECT 1 FROM workspaces WHERE id=? OR code=?", (workspace_id, workspace_id)
    ).fetchone() is not None


def _assert_owned(store: Store, actor_id: int, workspace_id: str) -> None:
    row = store.conn.execute(
        "SELECT u.workspace_id, r.code AS code FROM users u "
        "JOIN roles r ON r.id = u.role_id WHERE u.id=?",
        (actor_id,),).fetchone()
    if not row:
        raise PermissionError("unknown actor")
    if row["code"] != "Owner" and row["workspace_id"] != workspace_id:
        raise PermissionError(
            f"workspace isolation: actor {actor_id} belongs to "
            f"{row['workspace_id']!r}, not {workspace_id!r}")


def _audit(store: Store, actor_id: int, action: str, target: str,
           details: dict, workspace_id: str | None) -> int:
    return store.add_audit(actor_id, action, target, details, workspace_id)


# ---------------------------------------------------------------------------
# Departments
# ---------------------------------------------------------------------------
def list_departments(store: Store, workspace_id: str | None = None) -> list[dict]:
    if workspace_id is None:
        rows = store.fetchall("SELECT * FROM departments ORDER BY code")
    else:
        rows = store.fetchall(
            "SELECT * FROM departments WHERE workspace_id=? ORDER BY code",
            (workspace_id,))
    return rows


def create_department(store: Store, actor_id: int, workspace_id: str,
                      code: str, label: str) -> dict:
    if not _workspace_exists(store, workspace_id):
        raise LookupError(f"workspace {workspace_id!r} not found")
    _assert_owned(store, actor_id, workspace_id)
    cur = store.conn.execute(
        "INSERT INTO departments (workspace_id, code, label) VALUES (?,?,?)",
        (workspace_id, code, label))
    store.conn.commit()
    _audit(store, actor_id, "employee:department:create",
           f"department:{cur.lastrowid}", {"code": code, "label": label}, workspace_id)
    return dict(store.conn.execute(
        "SELECT * FROM departments WHERE id=?", (cur.lastrowid,)).fetchone())


# ---------------------------------------------------------------------------
# Employees
# ---------------------------------------------------------------------------
def list_employees(store: Store, workspace_id: str | None = None,
                   status: str = "active") -> list[dict]:
    sql = ("SELECT e.*, d.label AS department FROM employees e "
           "LEFT JOIN departments d ON d.id = e.department_id")
    params: list = []
    if workspace_id is not None:
        sql += " WHERE e.workspace_id=?"; params.append(workspace_id)
    if status:
        sql += " AND e.status=?"; params.append(status)
    sql += " ORDER BY e.employee_id"
    rows = store.fetchall(sql, params)
    for r in rows:
        if r.get("manager_id"):
            m = store.conn.execute(
                "SELECT employee_id, name FROM employees WHERE id=?",
                (r["manager_id"],)).fetchone()
            r["manager_id"] = m["employee_id"] if m else None
            r["manager_name"] = m["name"] if m else None
    return rows


def get_employee(store: Store, emp_id: int) -> dict | None:
    return dict(store.conn.execute(
        "SELECT e.*, d.label AS department FROM employees e "
        "LEFT JOIN departments d ON d.id = e.department_id WHERE e.id=?",
        (emp_id,)).fetchone())


def get_employee_by_id(store: Store, employee_id: str) -> dict | None:
    return dict(store.conn.execute(
        "SELECT e.*, d.label AS department FROM employees e "
        "LEFT JOIN departments d ON d.id = e.department_id WHERE e.employee_id=?",
        (employee_id,)).fetchone())


def create_employee(store: Store, actor_id: int, workspace_id: str,
                    employee_id: str, name: str, designation: str = "",
                    department_id: int | None = None,
                    hire_date: str = "", email: str = "", phone: str = "",
                    manager_id: int | None = None) -> dict:
    if not _workspace_exists(store, workspace_id):
        raise LookupError(f"workspace {workspace_id!r} not found")
    _assert_owned(store, actor_id, workspace_id)
    # Validate department_id belongs to the same workspace.
    if department_id is not None:
        dept = store.conn.execute(
            "SELECT 1 FROM departments WHERE id=? AND workspace_id=?",
            (department_id, workspace_id)).fetchone()
        if not dept:
            raise LookupError("department does not belong to this workspace")
    if manager_id is not None:
        mgr = store.conn.execute(
            "SELECT 1 FROM employees WHERE id=? AND workspace_id=?",
            (manager_id, workspace_id)).fetchone()
        if not mgr:
            raise LookupError("manager does not belong to this workspace")
    try:
        cur = store.conn.execute(
            "INSERT INTO employees (workspace_id, employee_id, name, designation, "
            "department_id, hire_date, email, phone, manager_id) VALUES (?,?,?,?,?,?,?,?,?)",
            (workspace_id, employee_id, name, designation, department_id,
             hire_date, email, phone, manager_id))
    except Exception as exc:  # unique constraint on employee_id
        raise ValueError(f"employee_id {employee_id!r} already exists") from exc
    store.conn.commit()
    _audit(store, actor_id, "employee:create", f"employee:{cur.lastrowid}",
           {"employee_id": employee_id, "name": name,
            "workspace_id": workspace_id}, workspace_id)
    return get_employee(store, cur.lastrowid)


def update_employee(store: Store, actor_id: int, emp_id: int,
                    **fields) -> dict | None:
    """Update only fixed allowlisted fields (no user-supplied column names)."""
    _allowed = {k: v for k, v in fields.items() if k in ALLOWED_EMPLOYEE_FIELDS}
    if not _allowed:
        return get_employee(store, emp_id)
    sets = ", ".join(f"{k}=?" for k in _allowed)
    store.conn.execute(
        f"UPDATE employees SET {sets} WHERE id=?", (*_allowed.values(), emp_id))
    store.conn.commit()
    # Refresh the row so caller sees latest values.
    return get_employee(store, emp_id)


def list_active_employees(store: Store, workspace_id: str | None = None) -> list[dict]:
    return list_employees(store, workspace_id, "active")


def list_resignations(store: Store, workspace_id: str | None = None) -> list[dict]:
    return list_employees(store, workspace_id, "resigned")


# ---------------------------------------------------------------------------
# Employment documents
# ---------------------------------------------------------------------------
def list_documents(store: Store, employee_id: int) -> list[dict]:
    return store.fetchall(
        "SELECT * FROM employee_documents WHERE employee_id=? ORDER BY id",
        (employee_id,))


def add_document(store: Store, actor_id: int, employee_id: int,
                 doc_type: str, doc_url: str, uploaded_by: int) -> dict:
    emp = get_employee(store, employee_id)
    if not emp:
        raise LookupError(f"employee {employee_id!r} not found")
    _assert_owned(store, actor_id, emp["workspace_id"])
    cur = store.conn.execute(
        "INSERT INTO employee_documents (employee_id, doc_type, doc_url, uploaded_by) "
        "VALUES (?,?,?,?)",
        (employee_id, doc_type, doc_url, uploaded_by))
    store.conn.commit()
    _audit(store, actor_id, "employee:document:add",
           f"document:{cur.lastrowid}", {"employee_id": employee_id,
                                         "doc_type": doc_type}, emp["workspace_id"])
    return dict(store.conn.execute(
        "SELECT * FROM employee_documents WHERE id=?", (cur.lastrowid,)).fetchone())


# ---------------------------------------------------------------------------
# Leave records
# ---------------------------------------------------------------------------
def list_leaves(store: Store, workspace_id: str | None = None) -> list[dict]:
    rows = store.fetchall(
        "SELECT l.*, e.name AS employee_name, e.workspace_id AS employee_workspace "
        "FROM leaves l JOIN employees e ON e.id = l.employee_id "
        "WHERE e.workspace_id IS NOT NULL")
    if workspace_id is not None:
        rows = [r for r in rows if r["employee_workspace"] == workspace_id]
    for r in rows:
        r["leave_days"] = float(r.get("days") or 0)
    return rows


def create_leave(store: Store, actor_id: int, employee_id: int,
                 type: str, start_date: str, end_date: str,
                 days: float, status: str = "applied", reason: str = "") -> dict:
    emp = get_employee(store, employee_id)
    if not emp:
        raise LookupError(f"employee {employee_id!r} not found")
    _assert_owned(store, actor_id, emp["workspace_id"])
    if type not in ("annual", "sick", "casual", "leave_without_pay"):
        raise ValueError(f"invalid leave type {type!r}")
    if status not in ("applied", "approved", "rejected", "carried"):
        raise ValueError(f"invalid leave status {status!r}")
    cur = store.conn.execute(
        "INSERT INTO leaves (employee_id, type, start_date, end_date, days, status, reason) "
        "VALUES (?,?,?,?,?,?,?)",
        (employee_id, type, start_date, end_date, days, status, reason))
    store.conn.commit()
    _audit(store, actor_id, "leave:create", f"leave:{cur.lastrowid}",
           {"type": type, "days": days, "status": status,
            "employee_id": employee_id}, emp["workspace_id"])
    return dict(store.conn.execute(
        "SELECT l.*, e.name AS employee_name FROM leaves l "
        "JOIN employees e ON e.id = l.employee_id WHERE l.id=?",
        (cur.lastrowid,)).fetchone())
