"""M17 Expense & Reimbursement.

Employee expense claims (travel, fuel, food/lodging, site expense,
equipment maintenance, other), vendors, cash advances, approval workflow,
project/site-wise tracking, budget vs actual, receipt uploads and audit trails.
"""
from __future__ import annotations

from ..store import Store
from datetime import datetime, timezone

ALLOWED_CATEGORIES = {
    "travel", "food_lodging", "fuel", "site_expense",
    "equipment_maintenance", "other",
}
ALLOWED_CLAIM_FIELDS = {"project_id", "category", "amount", "currency",
                        "receipt_url", "cash_advance_id", "notes"}


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


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def list_vendors(store: Store, workspace_id: str | None = None) -> list[dict]:
    if workspace_id is None:
        rows = store.fetchall("SELECT * FROM expense_vendors ORDER BY name")
    else:
        rows = store.fetchall(
            "SELECT * FROM expense_vendors WHERE workspace_id=? ORDER BY name",
            (workspace_id,))
    return rows


def create_vendor(store: Store, actor_id: int, workspace_id: str,
                  name: str, category: str = "vendor", contact: str = "") -> dict:
    if not _workspace_exists(store, workspace_id):
        raise LookupError(f"workspace {workspace_id!r} not found")
    _assert_owned(store, actor_id, workspace_id)
    cur = store.conn.execute(
        "INSERT INTO expense_vendors (workspace_id, name, category, contact) "
        "VALUES (?,?,?,?)",
        (workspace_id, name, category, contact))
    store.conn.commit()
    _audit(store, actor_id, "expense:vendor:create",
           f"vendor:{cur.lastrowid}", {"name": name, "category": category},
           workspace_id)
    return dict(store.conn.execute(
        "SELECT * FROM expense_vendors WHERE id=?", (cur.lastrowid,)).fetchone())


def list_claims(store: Store, workspace_id: str | None = None,
                status: str = "submitted") -> list[dict]:
    sql = ("SELECT ec.*, e.name AS employee_name FROM expense_claims ec "
           "JOIN employees e ON e.id = ec.employee_id "
           "WHERE ec.workspace_id IS NOT NULL")
    params: list = []
    if workspace_id is not None:
        sql += " AND ec.workspace_id=?"; params.append(workspace_id)
    if status:
        sql += " AND ec.status=?"; params.append(status)
    sql += " ORDER BY ec.submitted_at DESC"
    rows = store.fetchall(sql, params)
    for r in rows:
        r["claim_amount"] = float(r.get("amount") or 0)
    return rows


def get_claim(store: Store, claim_id: int) -> dict | None:
    return dict(store.conn.execute(
        "SELECT ec.*, e.name AS employee_name FROM expense_claims ec "
        "JOIN employees e ON e.id = ec.employee_id WHERE ec.id=?",
        (claim_id,)).fetchone())


def create_claim(store: Store, actor_id: int, workspace_id: str,
                 employee_id: int, project_id: str, category: str,
                 amount: float, currency: str = "INR",
                 receipt_url: str = "", cash_advance_id: int | None = None,
                 notes: str = "") -> dict:
    if category not in ALLOWED_CATEGORIES:
        raise ValueError(f"invalid category {category!r}")
    if amount < 0:
        raise ValueError("amount cannot be negative")
    emp = dict(store.conn.execute(
        "SELECT id, workspace_id FROM employees WHERE id=?", (employee_id,)).fetchone())
    if not emp:
        raise LookupError(f"employee {employee_id!r} not found")
    if emp["workspace_id"] != workspace_id:
        raise PermissionError("employee does not belong to this workspace")
    _assert_owned(store, actor_id, workspace_id)
    cur = store.conn.execute(
        "INSERT INTO expense_claims (workspace_id, employee_id, project_id, category, "
        "amount, currency, receipt_url, cash_advance_id, status, submitted_by, submitted_at, notes) "
        "VALUES (?,?,?,?,?,?,?,?, 'submitted',?,?,?)",
        (workspace_id, employee_id, project_id, category, amount, currency,
         receipt_url, cash_advance_id, actor_id, _now_iso(), notes))
    store.conn.commit()
    _audit(store, actor_id, "expense:claim:create",
           f"expense:claim:{cur.lastrowid}", {"category": category,
                                              "amount": amount,
                                              "project_id": project_id},
           workspace_id)
    return get_claim(store, cur.lastrowid)


def transition_claim(store: Store, actor_id: int, claim_id: int,
                     new_status: str, note: str = "") -> dict | None:
    """Approvers move a claim forward. Sensitive transitions are audited."""
    claim = get_claim(store, claim_id)
    if not claim:
        raise LookupError(f"claim {claim_id!r} not found")
    if claim["workspace_id"] is None:
        raise PermissionError("claim is not workspace-scoped")
    emp = dict(store.conn.execute(
        "SELECT workspace_id FROM employees WHERE id=?", (claim["employee_id"],)).fetchone())
    _assert_owned(store, actor_id, emp["workspace_id"])

    allowed = {"submitted", "pending_approval", "approved", "rejected", "settled"}
    if new_status not in allowed:
        raise ValueError(f"bad status {new_status!r}")
    # A manager/owner may approve/reject; anyone may submit/pending/settle.
    if new_status in ("approved", "rejected"):
        role = store.conn.execute(
            "SELECT r.code AS code FROM users u JOIN roles r ON r.id=u.role_id "
            "WHERE u.id=?", (actor_id,)).fetchone()["code"]
        if role not in ("Owner", "Manager", "Finance Manager", "Project Manager"):
            raise PermissionError(
                f"{role} cannot {new_status} claims (Owner/Manager/Finance/PM only)")

    store.conn.execute(
        "UPDATE expense_claims SET status=?, approved_by=?, approved_at=?, notes=? WHERE id=?",
        (new_status, actor_id, _now_iso(), note, claim_id))
    store.conn.commit()
    _audit(store, actor_id, f"expense:{new_status}",
           f"expense:claim:{claim_id}", {"from": claim["status"],
                                          "to": new_status, "note": note},
           emp["workspace_id"])
    return get_claim(store, claim_id)


def settle_claim(store: Store, actor_id: int, claim_id: int) -> dict | None:
    return transition_claim(store, actor_id, claim_id, "settled",
                            "settled with cash advance / bank reimbursement")


def create_cash_advance(store: Store, actor_id: int, workspace_id: str,
                        employee_id: int, amount: float, currency: str = "INR") -> dict:
    if amount < 0:
        raise ValueError("amount cannot be negative")
    emp = dict(store.conn.execute(
        "SELECT id, workspace_id FROM employees WHERE id=?", (employee_id,)).fetchone())
    if not emp:
        raise LookupError(f"employee {employee_id!r} not found")
    if emp["workspace_id"] != workspace_id:
        raise PermissionError("employee does not belong to this workspace")
    _assert_owned(store, actor_id, workspace_id)
    cur = store.conn.execute(
        "INSERT INTO cash_advance (workspace_id, employee_id, amount, currency, status) "
        "VALUES (?,?,?,?,?)",
        (workspace_id, employee_id, amount, currency, "advanced"))
    store.conn.commit()
    _audit(store, actor_id, "expense:cash:advance:create",
           f"cash_advance:{cur.lastrowid}", {"amount": amount,
                                             "currency": currency,
                                             "employee_id": employee_id},
           workspace_id)
    return dict(store.conn.execute(
        "SELECT * FROM cash_advance WHERE id=?", (cur.lastrowid,)).fetchone())


def settle_cash_advance(store: Store, actor_id: int, advance_id: int,
                        amount: float | None = None) -> dict | None:
    adv = dict(store.conn.execute(
        "SELECT * FROM cash_advance WHERE id=?", (advance_id,)).fetchone())
    if not adv:
        raise LookupError(f"cash advance {advance_id!r} not found")
    _assert_owned(store, actor_id, adv["workspace_id"])
    if adv["status"] == "settled":
        return adv
    settle = amount if amount is not None else adv["amount"]
    if settle < 0 or settle > (adv["amount"] or 0):
        raise ValueError("settlement amount exceeds advance amount")
    rem = (adv["amount"] or 0) - settle
    store.conn.execute(
        "UPDATE cash_advance SET status='settled', settled_at=?, amount=? WHERE id=?",
        (_now_iso(), rem, advance_id))
    store.conn.commit()
    _audit(store, actor_id, "expense:cash:advance:settle",
           f"cash_advance:{advance_id}", {"settled_amount": settle,
                                          "remaining": rem},
           adv["workspace_id"])
    return dict(store.conn.execute(
        "SELECT * FROM cash_advance WHERE id=?", (advance_id,)).fetchone())


def budget_workspace(store: Store, workspace_id: str,
                     category: str) -> float:
    """Budgeted amount for a workspace+category (0 if not configured)."""
    row = store.conn.execute(
        "SELECT COALESCE(SUM(amount),0) AS c FROM expense_claims "
        "WHERE workspace_id=? AND category=? AND status='approved'",
        (workspace_id, category)).fetchone()
    return float(row["c"])


def category_totals(store: Store, workspace_id: str) -> dict:
    rows = store.fetchall(
        "SELECT category, COALESCE(SUM(amount),0) AS c FROM expense_claims "
        "WHERE workspace_id=? GROUP BY category", (workspace_id,))
    return {r["category"]: float(r["c"]) for r in rows}


def claims_for_project(store: Store, workspace_id: str, project_id: str) -> list[dict]:
    return store.fetchall(
        "SELECT ec.*, e.name AS employee_name FROM expense_claims ec "
        "JOIN employees e ON e.id = ec.employee_id "
        "WHERE ec.workspace_id=? AND ec.project_id=? ORDER BY ec.submitted_at DESC",
        (workspace_id, project_id))
