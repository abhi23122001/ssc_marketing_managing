"""SHAH AI Brain foundation.

Central AI orchestration layer for the shared owner dashboard and the
business workspaces (SSC, INFRA, OTHER). Responsibilities:

  * Understand owner commands and route them to the correct workspace.
  * Coordinate specialist agents (owner assistant, survey ops, project mgmt,
    HR, attendance, finance, expense, payroll, marketing, SEO, contractor
    intelligence, email drafting, reporting).
  * Read only authorized business data.
  * Generate reports, attendance anomalies, expense alerts and payroll alerts.
  * Track task status and maintain audit logs.

Permission-aware tool execution: a tool executes only when the authenticated
role explicitly allows it (store + RBAC). Sensitive operations require owner
approval via the approval engine. No external or payment action is ever
performed without explicit human approval.
"""
from __future__ import annotations

import json
import time

from ..store import Store

from . import employee, attendance, expense, payroll
from . import m19_core
from .shared import _assert_owned, _audit, _json_dumps, _now_iso, _workspace_exists
from .. import rbac

ALLOWED_TOOLS = {
    "workspace:list", "workspace:read", "resource:list", "resource:read",
    "employees:read", "departments:read", "attendance:read", "expense:read",
    "payroll:read", "reports:read", "ai:brain:query",
}


# ---------------------------------------------------------------------------
# Agents
# ---------------------------------------------------------------------------
def list_agents(store: Store, workspace_id: str | None = None) -> list[dict]:
    if workspace_id is None:
        rows = store.fetchall("SELECT * FROM ai_agents ORDER BY code")
    else:
        rows = store.fetchall(
            "SELECT * FROM ai_agents WHERE workspace_id=? ORDER BY code",
            (workspace_id,))
    for r in rows:
        r["tool_access"] = r.get("tool_access") or "{}"
    return rows


def create_agent(store: Store, actor_id: int, workspace_id: str,
                 code: str, name: str, description: str = "", agent_type: str = "general",
                 tool_access: dict | None = None) -> dict:
    if not store.conn.execute(
            "SELECT 1 FROM workspaces WHERE id=? OR code=?", (workspace_id, workspace_id)
    ).fetchone():
        raise LookupError(f"workspace {workspace_id!r} not found")
    _assert_owned(store, actor_id, workspace_id)
    if tool_access is None:
        tool_access = {}
    cur = store.conn.execute(
        "INSERT INTO ai_agents (workspace_id, code, name, description, agent_type, tool_access) "
        "VALUES (?,?,?,?,?,?)",
        (workspace_id, code, name, description, agent_type, _json_dumps(tool_access)))
    store.conn.commit()
    _audit(store, actor_id, "ai:agent:create",
           f"ai_agent:{cur.lastrowid}", {"code": code, "name": name}, workspace_id)
    return dict(store.conn.execute(
        "SELECT * FROM ai_agents WHERE id=?", (cur.lastrowid,)).fetchone())


# ---------------------------------------------------------------------------
# Tasks
# ---------------------------------------------------------------------------
def list_tasks(store: Store, workspace_id: str | None = None,
               status: str = "") -> list[dict]:
    sql = ("SELECT t.*, a.name AS agent_name FROM ai_tasks t "
           "LEFT JOIN ai_agents a ON a.id = t.agent_id "
           "WHERE t.workspace_id IS NOT NULL")
    params: list = []
    if workspace_id is not None:
        sql += " AND t.workspace_id=?"; params.append(workspace_id)
    if status:
        sql += " AND t.status=?"; params.append(status)
    sql += " ORDER BY t.priority DESC, t.created_at DESC"
    rows = store.fetchall(sql, params)
    for r in rows:
        r["status"] = r.get("status") or "open"
    return rows


def create_task(store: Store, actor_id: int, workspace_id: str, agent_id: int | None,
                title: str, description: str = "", priority: str = "medium",
                assigned_to: int | None = None,
                tool_requests: list[str] | None = None) -> dict:
    _assert_owned(store, actor_id, workspace_id)
    agent = None
    if agent_id is not None:
        row = store.conn.execute("SELECT id, workspace_id FROM ai_agents WHERE id=?", (agent_id,)).fetchone()
        if not row and isinstance(agent_id, str):
            row = store.conn.execute("SELECT id, workspace_id FROM ai_agents WHERE code=? OR code LIKE ? LIMIT 1", (agent_id, f"%{agent_id}%")).fetchone()
        if not row:
            row = store.conn.execute("SELECT id, workspace_id FROM ai_agents WHERE workspace_id=? LIMIT 1", (workspace_id,)).fetchone()
        if row:
            agent = dict(row)
            agent_id = agent["id"]
            _assert_owned(store, actor_id, agent["workspace_id"])
    # Ensure tool_requests column exists (backward compatibility for older DBs)
    cols = store.conn.execute(
        "PRAGMA table_info(ai_tasks)").fetchall()
    col_names = [c["name"] for c in cols]
    if "tool_requests" not in col_names:
        store.conn.execute(
            "ALTER TABLE ai_tasks ADD COLUMN tool_requests TEXT NOT NULL DEFAULT '{}'")
        store.conn.commit()
    cur = store.conn.execute(
        "INSERT INTO ai_tasks (workspace_id, agent_id, title, description, priority, assigned_to, tool_requests) "
        "VALUES (?,?,?,?,?,?,?)",
        (workspace_id, agent_id, title, description, priority, assigned_to,
         _json_dumps(tool_requests or [])))
    store.conn.commit()
    _audit(store, actor_id, "ai:task:create",
           f"ai_task:{cur.lastrowid}", {"agent_id": agent_id, "title": title}, workspace_id)
    return dict(store.conn.execute(
        "SELECT t.*, a.name AS agent_name FROM ai_tasks t "
        "LEFT JOIN ai_agents a ON a.id = t.agent_id WHERE t.id=?",
        (cur.lastrowid,)).fetchone())


def update_task_status(store: Store, actor_id: int, task_id: int,
                       new_status: str, result_summary: str = "",
                       audit_note: str = "") -> dict | None:
    task = dict(store.conn.execute(
        "SELECT * FROM ai_tasks WHERE id=?", (task_id,)).fetchone())
    if not task:
        raise LookupError(f"task {task_id!r} not found")
    _assert_owned(store, actor_id, task["workspace_id"])
    allowed = {"open", "in_progress", "completed", "blocked", "cancelled"}
    if new_status not in allowed:
        raise ValueError(f"bad status {new_status!r}")
    store.conn.execute(
        "UPDATE ai_tasks SET status=?, result_summary=?, audit_note=?, "
        "updated_at=? WHERE id=?",
        (new_status, result_summary, audit_note, _now_iso(), task_id))
    store.conn.commit()
    _audit(store, actor_id, f"ai:task:{new_status}",
           f"ai:task:{task_id}", {"from": task["status"], "note": audit_note},
           task["workspace_id"])
    return dict(store.conn.execute(
        "SELECT t.*, a.name AS agent_name FROM ai_tasks t "
        "LEFT JOIN ai_agents a ON a.id = t.agent_id WHERE t.id=?",
        (task_id,)).fetchone())


# ---------------------------------------------------------------------------
# Tool executions (permission-aware audit)
# ---------------------------------------------------------------------------
def list_tool_executions(store: Store, task_id: int) -> list[dict]:
    return store.fetchall(
        "SELECT * FROM ai_tool_executions WHERE ai_task_id=? ORDER BY id",
        (task_id,))


def record_tool_execution(store: Store, actor_id: int, task_id: int,
                          tool_name: str, args: dict, allowed: int,
                          result: dict, executed_by: int) -> dict:
    _agent = store.conn.execute(
        "SELECT workspace_id FROM ai_tasks WHERE id=?",
        (task_id,)).fetchone()
    workspace_id = _agent["workspace_id"] if _agent else None
    _assert_owned(store, actor_id, workspace_id or "")
    cur = store.conn.execute(
        "INSERT INTO ai_tool_executions (ai_task_id, tool_name, args, allowed, result, executed_by) "
        "VALUES (?,?,?,?,?,?)",
        (task_id, tool_name, _json_dumps(args), allowed,
         _json_dumps(result), executed_by))
    store.conn.commit()
    _audit(store, actor_id, "ai:tool:execution",
           f"ai_tool_execution:{cur.lastrowid}",
           {"tool": tool_name, "allowed": bool(allowed), "actor": actor_id},
           workspace_id)
    return dict(store.conn.execute(
        "SELECT * FROM ai_tool_executions WHERE id=?", (cur.lastrowid,)).fetchone())


# ---------------------------------------------------------------------------
# Consolidated owner report (business-wise, not per-business cross-read)
# ---------------------------------------------------------------------------
def owner_consolidated_report(store: Store, workspace_id: str | None = None) -> dict:
    """Owner-facing consolidated view, business-scoped per workspace."""
    if workspace_id is None:
        # Owner reads all workspaces for the consolidated dashboard.
        sql = ("SELECT w.code AS workspace_code, "
               "(SELECT COUNT(*) FROM employees e WHERE e.workspace_id=w.id) AS employees, "
               "(SELECT COUNT(*) FROM sites s WHERE s.workspace_id=w.id) AS sites, "
               "(SELECT COUNT(*) FROM attendance_logs al WHERE al.site_id IN (SELECT id FROM sites s2 WHERE s2.workspace_id=w.id)) AS checkins, "
               "(SELECT COUNT(*) FROM expense_claims ec WHERE ec.workspace_id=w.id) AS claims "
               "FROM workspaces w ORDER BY w.code")
        rows = store.fetchall(sql)
        total_employees = total_sites = total_checkins = total_claims = 0
        for r in rows:
            total_employees += r["employees"]
            total_sites += r["sites"]
            total_checkins += r["checkins"]
            total_claims += r["claims"]
        return {
            "generated_at": _now_iso(),
            "workspaces": rows,
            "totals": {
                "employees": total_employees, "sites": total_sites,
                "checkins": total_checkins, "claims": total_claims,
            },
        }
    # Single-workspace breakdown.
    return {
        "generated_at": _now_iso(),
        "workspace_code": workspace_id,
        "employees": _count(store, "employees", workspace_id),
        "sites": _count(store, "sites", workspace_id),
        "checkins": _count(store, "attendance_logs", workspace_id),
        "claims": _count(store, "expense_claims", workspace_id),
        "payroll_runs": _count(store, "payroll_runs", workspace_id),
        "leave_days_approved": _count_approved_leave(store, workspace_id),
    }


def _count(store: Store, table: str, workspace_id: str) -> int:
    row = store.conn.execute(
        f"SELECT COUNT(*) AS c FROM {table} WHERE workspace_id=?", (workspace_id,)).fetchone()
    return int(row["c"])


def _count_approved_leave(store: Store, workspace_id: str) -> float:
    row = store.conn.execute(
        "SELECT COALESCE(SUM(l.days),0) AS c FROM leaves l "
        "JOIN employees e ON e.id=l.employee_id WHERE e.workspace_id=? AND l.status='approved'",
        (workspace_id,)).fetchone()
    return float(row["c"] or 0)

# ---------------------------------------------------------------------------
# Alerts
# ---------------------------------------------------------------------------
def attendance_alerts(store: Store, workspace_id: str | None = None) -> list[dict]:
    """Attendance anomalies: late arrivals, no_shows, unapproved absences."""
    sql = ("SELECT al.*, e.name AS employee_name, s.name AS site_name, "
           "e.workspace_id AS emp_ws FROM attendance_logs al "
           "JOIN employees e ON e.id = al.employee_id "
           "JOIN sites s ON s.id = al.site_id "
           "WHERE (al.status IN ('late','no_show') OR al.geofence_passed = 0)")
    params: list = []
    if workspace_id is not None:
        sql += " AND e.workspace_id=?"; params.append(workspace_id)
    sql += " ORDER BY al.check_in DESC"
    rows = store.fetchall(sql, params)
    return rows


def expense_alerts(store: Store, workspace_id: str | None = None) -> list[dict]:
    """Approved expense totals that exceed a configurable threshold."""
    if workspace_id is None:
        sql = ("SELECT ec.*, e.name AS employee_name FROM expense_claims ec "
               "JOIN employees e ON e.id = ec.employee_id "
               "WHERE ec.status='approved' ORDER BY ec.amount DESC")
        rows = store.fetchall(sql)
    else:
        rows = store.fetchall(
            "SELECT ec.*, e.name AS employee_name FROM expense_claims ec "
            "JOIN employees e ON e.id = ec.employee_id "
            "WHERE ec.workspace_id=? AND ec.status='approved' "
            "ORDER BY ec.amount DESC", (workspace_id,))
    return rows


def payroll_review_alerts(store: Store, workspace_id: str | None = None) -> list[dict]:
    """Payroll runs awaiting review."""
    sql = ("SELECT pr.*, u.username AS run_by_username FROM payroll_runs pr "
           "JOIN users u ON u.id = pr.run_by "
           "WHERE pr.status='draft'")
    params: list = []
    if workspace_id is not None:
        sql += " AND pr.workspace_id=?"; params.append(workspace_id)
    sql += " ORDER BY pr.run_month DESC"
    rows = store.fetchall(sql, params)
    return rows


# ---------------------------------------------------------------------------
# Real, permission-checked task execution
# ---------------------------------------------------------------------------
def _execute_read_report(store: Store, workspace_id: str, args: dict) -> dict:
    """Read-only report: weekly/monthly synthesis over authorized workspace data."""
    from . import m19_core
    rtype = args.get("report_type", "weekly")
    if rtype == "weekly":
        rep = m19_core.generate_weekly_report(store, workspace_id, args.get("report_period", ""))  # type: ignore[arg-type]
    else:
        rep = m19_core.generate_monthly_report(store, workspace_id)
    return {"report": rep}


def execute_task(store: Store, actor_id: int, task_id: int,
                 max_retries: int = 3) -> dict:
    """Run an AI Brain task with real permission-checked tool execution.

    Steps:
      1. Recover the task + its assigned agent and workspace context.
      2. Parse the agent's tool_access allowlist.
      3. For each tool request: check RBAC + agent allowlist, then run the
         real domain function against the authorized workspace.
      4. Record every tool execution (allowed/disallowed, args, result).
      5. Update task status with the recorded results.

    Returns the task record with a result_summary and tool executions.
    Sensitive writes (e.g. payroll approvals, expense settlements) stay gated
    behind the owner-approval approval engine and are never auto-executed.
    """
    task = dict(store.conn.execute(
        "SELECT t.*, a.code AS agent_code, a.tool_access FROM ai_tasks t "
        "LEFT JOIN ai_agents a ON a.id=t.agent_id WHERE t.id=?", (task_id,)).fetchone())
    if not task:
        raise LookupError(f"task {task_id!r} not found")

    _assert_owned(store, actor_id, task["workspace_id"])

    # Sanity guard: only read/execute tools with explicit RBAC permission.
    agent_code = task.get("agent_code") or "general"
    agent_access = task.get("tool_access") or "{}"
    try:
        allowed_tools = json.loads(agent_access)
    except Exception:
        allowed_tools = []

    # Resolve the actor's role from the store (task dict has no actor_role).
    actor_row = store.conn.execute(
        "SELECT r.code AS code FROM users u "
        "JOIN roles r ON r.id = u.role_id WHERE u.id=?", (actor_id,)).fetchone()
    actor_role = actor_row["code"] if actor_row else "Employee"

    results = []
    executions = []
    attempts = 0
    error = None

    while attempts < max_retries:
        attempts += 1
        try:
            # Stop on a hard failure so we do not retry a doomed run.
            if error and "permanent" in error.lower():
                break

            # Parse tool_requests (stored as JSON string in DB)
            tool_requests = task.get("tool_requests") or "[]"
            if isinstance(tool_requests, str):
                try:
                    tool_requests = json.loads(tool_requests)
                except Exception:
                    tool_requests = []
            for tool_req in tool_requests or []:
                if isinstance(tool_req, (list, tuple)):
                    tool_name = tool_req[0]
                    arg = tool_req[1] if len(tool_req) > 1 and isinstance(tool_req[1], dict) else {}
                elif isinstance(tool_req, dict):
                    tool_name = tool_req.get("tool") or tool_req.get("name")
                    arg = tool_req.get("args") or {}
                else:
                    tool_name = str(tool_req)
                    arg = {}

                if tool_name not in _BRAIN_TOOLS:
                    executions.append(record_tool_execution(
                        store, actor_id, task_id, tool_name, arg,
                        0, {"error": f"unknown tool {tool_name}"}, actor_id))
                    results.append({"tool": tool_name, "status": "failed",
                                    "error": f"unknown tool {tool_name}"})
                    continue

                # 1) RBAC gate (role permission) — required permission from tool def
                required_perm = _BRAIN_TOOLS[tool_name][0]
                if not rbac.has_permission(actor_role, required_perm):
                    executions.append(record_tool_execution(
                        store, actor_id, task_id, tool_name, arg,
                        0, {"error": f"permission denied for {tool_name}"}, actor_id))
                    results.append({"tool": tool_name, "status": "blocked",
                                    "error": f"role {actor_role} lacks permission {required_perm}"})
                    continue
                # 2) Agent allowlist gate (agent-specific tool_access)
                if allowed_tools and tool_name not in allowed_tools:
                    executions.append(record_tool_execution(
                        store, actor_id, task_id, tool_name, arg,
                        0, {"error": "tool not in agent allowlist"}, actor_id))
                    results.append({"tool": tool_name, "status": "blocked",
                                    "error": "not in agent allowlist"})
                    continue
                # 3) Execute the real domain function
                try:
                    fn = _BRAIN_TOOLS[tool_name][1]
                    import inspect
                    sig = inspect.signature(fn)
                    params = list(sig.parameters.values())
                    accepts_kwargs = any(p.kind == inspect.Parameter.VAR_KEYWORD for p in params)
                    named_params = {p.name for p in params if p.kind in (inspect.Parameter.POSITIONAL_OR_KEYWORD, inspect.Parameter.KEYWORD_ONLY)}

                    if accepts_kwargs:
                        res = fn(store, task["workspace_id"], **arg)
                    elif len(params) <= 2:
                        res = fn(store, task["workspace_id"])
                    else:
                        filtered = {k: v for k, v in arg.items() if k in named_params and k not in ("s", "store", "w", "workspace_id")}
                        res = fn(store, task["workspace_id"], **filtered)

                    executions.append(record_tool_execution(
                        store, actor_id, task_id, tool_name, arg, 1, res, actor_id))
                    results.append({"tool": tool_name, "status": "completed",
                                    "result": res})
                except Exception as e:
                    executions.append(record_tool_execution(
                        store, actor_id, task_id, tool_name, arg,
                        0, {"error": str(e)}, actor_id))
                    results.append({"tool": tool_name, "status": "failed",
                                    "error": str(e)})
                    if isinstance(e, PermissionError):
                        error = f"permanent: {e}"
            break
        except Exception as e:
            error = str(e)
            if attempts >= max_retries:
                break
            time.sleep(min(2 ** attempts, 5))

    final_status = task["status"]
    if error:
        final_status = "blocked"
    elif task["status"] == "open":
        final_status = "completed"

    store.conn.execute(
        "UPDATE ai_tasks SET status=?, result_summary=?, audit_note=?, "
        "updated_at=? WHERE id=?",  # noqa: F821
        (final_status,
         json.dumps({"task_id": task_id, "status": final_status,
                     "tool_executions": len(executions), "error": error or "none"}),
         json.dumps({"record_count": len(executions), "retries": attempts}),
         _now_iso(), task_id))
    store.conn.commit()
    _audit(store, actor_id, f"ai:task:execute:{final_status}",
           f"ai:task:{task_id}", {"error": error or "none"},
           task["workspace_id"])

    return dict(store.conn.execute(
        "SELECT t.*, a.name AS agent_name FROM ai_tasks t "
        "LEFT JOIN ai_agents a ON a.id=t.agent_id WHERE t.id=?", (task_id,)).fetchone())

# Permitted tools + their real implementations (read-only domain functions).
# Each entry: (required_permission, callable, result_key)
_BRAIN_TOOLS: dict[str, tuple[str, callable, str]] = {
    "workspace:list": ("workspace:list", lambda s, w: {"workspaces": s.list_workspaces()}, "workspaces"),
    "workspace:read": ("workspace:read", lambda s, w: {"workspace": s.get_workspace(w)}, "workspace"),
    "resource:list": ("resource:list", lambda s, w: {"resources": s.list_resources(w)}, "resources"),
    "resource:read": ("resource:read", lambda s, w, rid=0: {"resource": s.get_resource(int(rid))}, "resource"),
    "employees:read": ("resource:read", lambda s, w: {"employees": s.list_employees(w)}, "employees"),
    "departments:read": ("resource:read", lambda s, w: {"departments": employee.list_departments(s, w)}, "departments"),
    "attendance:read": ("resource:read", lambda s, w: {"attendance": s.list_attendance(w)}, "attendance"),
    "expense:read": ("resource:read", lambda s, w: {"expense_claims": s.list_expense_claims(w)}, "expense_claims"),
    "payroll:read": ("resource:read", lambda s, w: {"payroll_runs": payroll.list_payroll_runs(s, w)}, "payroll_runs"),
    "reports:read": ("report:read", _execute_read_report, "report"),
    "leads:read": ("resource:read", lambda s, w: {"leads": s.fetchall("SELECT * FROM social_leads WHERE workspace_id=?", (w,))}, "leads"),
    "sites:read": ("resource:read", lambda s, w: {"sites": s.list_sites(w)}, "sites"),
    "vendors:read": ("resource:read", lambda s, w: {"vendors": s.list_vendors(w)}, "vendors"),
    "clients:read": ("resource:read", lambda s, w: {"clients": s.list_clients()}, "clients"),
    "alerts:attendance": ("resource:read", lambda s, w: {"alerts": attendance_alerts(s, w)}, "alerts"),
    "alerts:expense": ("resource:read", lambda s, w: {"alerts": expense_alerts(s, w)}, "alerts"),
}



