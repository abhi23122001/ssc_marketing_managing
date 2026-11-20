"""M18 Payroll & Salary Management.

Monthly payroll calculation, attendance-based salary, leave and overtime
adjustments, advances and deductions, payslip generation, payroll reports and
reconciliation. No real payments or bank transfers are initiated; payroll runs
are drafts until explicitly approved and produce payslips only.
"""
from __future__ import annotations

from ..store import Store
from datetime import datetime, timezone

from .attendance import compute_overtime, compute_worked_hours

ALLOWED_RUN_FIELDS = {"run_month", "period", "status", "ledger_snapshot"}
ALLOWED_PAYSLIP_FIELDS = {"name", "month", "gross", "deductions", "in_hand",
                          "report_url"}


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


def _week_days(year, month) -> int:
    import calendar
    return calendar.monthrange(year, month)[1]


def list_payroll_runs(store: Store, workspace_id: str | None = None) -> list[dict]:
    if workspace_id is None:
        rows = store.fetchall("SELECT * FROM payroll_runs ORDER BY run_month DESC")
    else:
        rows = store.fetchall(
            "SELECT * FROM payroll_runs WHERE workspace_id=? "
            "ORDER BY run_month DESC", (workspace_id,))
    return rows


def get_payroll_run(store: Store, run_id: int) -> dict | None:
    return dict(store.conn.execute(
        "SELECT * FROM payroll_runs WHERE id=?", (run_id,)).fetchone())


def create_payroll_run(store: Store, actor_id: int, workspace_id: str,
                       run_month: str, period: str = "monthly",
                       run_by: int | None = None, status: str = "draft") -> dict:
    if not _workspace_exists(store, workspace_id):
        raise LookupError(f"workspace {workspace_id!r} not found")
    _assert_owned(store, actor_id, workspace_id)
    if status not in ("draft", "ready", "approved"):
        raise ValueError(f"invalid status {status!r}")
    emp = None
    if run_by is not None:
        emp = dict(store.conn.execute(
            "SELECT id, workspace_id FROM employees WHERE id=?", (run_by,)).fetchone())
        if not emp:
            raise LookupError("run_by employee not found")
        _assert_owned(store, actor_id, emp["workspace_id"])
    cur = store.conn.execute(
        "INSERT INTO payroll_runs (workspace_id, run_month, period, run_by, status) "
        "VALUES (?,?,?,?,?)",
        (workspace_id, run_month, period, run_by or None, status))
    store.conn.commit()
    _audit(store, actor_id, "payroll:run:create",
           f"payroll_run:{cur.lastrowid}", {"run_month": run_month,
                                            "period": period,
                                            "status": status},
           workspace_id)
    return dict(store.conn.execute(
        "SELECT * FROM payroll_runs WHERE id=?", (cur.lastrowid,)).fetchone())


def approve_run(store: Store, actor_id: int, run_id: int) -> dict | None:
    run = get_payroll_run(store, run_id)
    if not run:
        raise LookupError(f"payroll run {run_id!r} not found")
    _assert_owned(store, actor_id, run["workspace_id"])
    if run["status"] not in ("draft", "ready"):
        raise PermissionError(f"run {run['status']} cannot be approved")
    store.conn.execute(
        "UPDATE payroll_runs SET status='approved', processed_at=? WHERE id=?",
        (_now_iso(), run_id))
    store.conn.commit()
    _audit(store, actor_id, "payroll:run:approve",
           f"payroll_run:{run_id}", {"old_status": run["status"]},
           run["workspace_id"])
    return get_payroll_run(store, run_id)


def _employee_list(store: Store, workspace_id: str) -> list[dict]:
    return store.fetchall(
        "SELECT id, employee_id, name, designation, department_id, status "
        "FROM employees WHERE workspace_id=? ORDER BY employee_id", (workspace_id,))


def calculate_payroll(stock: Store, workspace_id: str, run_month: str,
                      base_monthly_salary: float = 25000.0,
                      regular_hours: float = 8.0) -> dict:
    """Compute a monthly payroll summary from the synthetic data in the store.

    This is a deterministic calculation over the DB records:
      gross = salary + attendance_overtime + leave_adjustment
      deductions = approved leave days + any authorized deductions
      in_hand = gross - deductions
    It never touches the bank and does not create or alter payment records.
    """
    emp_rows = _employee_list(stock, workspace_id)
    total_gross = 0.0
    total_deductions = 0.0
    total_in_hand = 0.0
    ledger = []
    for e in emp_rows:
        emp = e["id"]
        salary = float(base_monthly_salary)
        # Overtime from attendance event rows for this employee.
        rows = stock.fetchall(
            "SELECT check_in, check_out FROM attendance_logs "
            "WHERE employee_id=? AND status NOT IN ('weekly_off','absent')",
            (emp,))
        ot_hours = 0.0
        hours = 0.0
        for r in rows:
            hours += compute_worked_hours(r["check_in"],
                                          r.get("check_out") or r["check_in"])
        ot_hours = compute_overtime(hours, regular_hours)
        ot = ot_hours * 200.0  # overtime rate assumption (200/unit)
        gross = salary + ot

        # Approved leave days as deductions.
        leaves = stock.fetchall(
            "SELECT COALESCE(SUM(days),0) AS c FROM leaves "
            "WHERE employee_id=? AND status='approved'",
            (emp,))
        leave_days = float(leaves[0]["c"] or 0.0)
        deductions = leave_days * (salary / 26.0)

        in_hand = gross - deductions
        total_gross += gross
        total_deductions += deductions
        total_in_hand += in_hand
        ledger.append({
            "employee_id": e["employee_id"], "name": e["name"],
            "salary": salary, "overtime_hours": round(ot_hours, 2),
            "overtime_amount": round(ot, 2), "leave_days": leave_days,
            "deductions": round(deductions, 2), "gross": round(gross, 2),
            "in_hand": round(in_hand, 2), "status": e["status"],
        })
    return {
        "run_month": run_month, "workspace_id": workspace_id,
        "period": "monthly",
        "total_employees": len(emp_rows),
        "total_gross": round(total_gross, 2),
        "total_deductions": round(total_deductions, 2),
        "total_in_hand": round(total_in_hand, 2),
        "ledger": ledger,
    }


def list_payslips(store: Store, payroll_run_id: int) -> list[dict]:
    return store.fetchall(
        "SELECT * FROM payslips WHERE payroll_run_id=? ORDER BY employee_id",
        (payroll_run_id,))


def add_payslip(store: Store, actor_id: int, payroll_run_id: int,
                employee_id: int, name: str, month: str,
                gross: float, deductions: float, in_hand: float,
                report_url: str = "") -> dict:
    run = get_payroll_run(store, payroll_run_id)
    if not run:
        raise LookupError(f"payroll run {payroll_run_id!r} not found")
    _assert_owned(store, actor_id, run["workspace_id"])
    if in_hand < 0:
        raise ValueError("in_hand cannot be negative")
    cur = store.conn.execute(
        "INSERT INTO payslips (payroll_run_id, employee_id, name, month, "
        "gross, deductions, in_hand, report_url) VALUES (?,?,?,?,?,?,?,?)",
        (payroll_run_id, employee_id, name, month, gross, deductions,
         in_hand, report_url))
    store.conn.commit()
    _audit(store, actor_id, "payroll:payslip:add",
           f"payslip:{cur.lastrowid}", {"month": month, "gross": gross,
                                        "deductions": deductions,
                                        "in_hand": in_hand},
           run["workspace_id"])
    return dict(store.conn.execute(
        "SELECT * FROM payslips WHERE id=?", (cur.lastrowid,)).fetchone())


def execute_payroll_run(store: Store, actor_id: int, workspace_id: str,
                        run_month: str, run_by: int | None = None,
                        base_monthly_salary: float = 25000.0) -> dict:
    """Execute end-to-end payroll calculation, persist run, generate payslips, and stage approval."""
    import json
    calc = calculate_payroll(store, workspace_id, run_month, base_monthly_salary)
    _assert_owned(store, actor_id, workspace_id)

    # Resolve run_by employee id
    if run_by is None:
        first_emp = store.fetchone("SELECT id FROM employees WHERE workspace_id=? ORDER BY id ASC", (workspace_id,))
        if first_emp:
            run_by = first_emp["id"]
        else:
            first_any = store.fetchone("SELECT id FROM employees ORDER BY id ASC")
            run_by = first_any["id"] if first_any else 1

    ledger_json = json.dumps(calc["ledger"])
    cur = store.conn.execute(
        "INSERT INTO payroll_runs (workspace_id, run_month, period, run_by, status, "
        "total_gross, total_deductions, total_in_hand, ledger_snapshot, created_at) "
        "VALUES (?,?,'monthly',?,'draft',?,?,?,?,?)",
        (workspace_id, run_month, run_by, calc["total_gross"],
         calc["total_deductions"], calc["total_in_hand"], ledger_json, _now_iso())
    )
    run_id = cur.lastrowid
    store.conn.commit()

    # Generate payslips for each employee in ledger
    created_slips = []
    for item in calc["ledger"]:
        emp_row = store.fetchone("SELECT id FROM employees WHERE employee_id=? AND workspace_id=?",
                                 (item["employee_id"], workspace_id))
        db_emp_id = emp_row["id"] if emp_row else 1
        slip_cur = store.conn.execute(
            "INSERT INTO payslips (payroll_run_id, employee_id, name, month, gross, deductions, in_hand, report_url, generated_at) "
            "VALUES (?,?,?,?,?,?,?,?,?)",
            (run_id, db_emp_id, item["name"], run_month, item["gross"], item["deductions"],
             item["in_hand"], f"/api/payroll/payslips/{run_id}/{db_emp_id}", _now_iso())
        )
        created_slips.append(dict(store.conn.execute("SELECT * FROM payslips WHERE id=?", (slip_cur.lastrowid,)).fetchone()))
    store.conn.commit()

    # Auto-stage approval request
    try:
        res_key = "payroll_runs"
        res = store.fetchone("SELECT id FROM resources WHERE workspace_id=? AND key=?", (workspace_id, res_key))
        if not res:
            store.create_resource(workspace_id, res_key, "Payroll Run Register", "Monthly staff salary and payroll records")
        store.create_approval(
            workspace_id,
            f"Payroll Run: {run_month} ({workspace_id}) - INR {calc['total_gross']:,.2f}",
            f"Payroll generated for {calc['total_employees']} staff. Total Net: INR {calc['total_in_hand']:,.2f}",
            actor_id,
            res_key
        )
    except Exception:
        pass

    _audit(store, actor_id, "payroll:run:execute", f"payroll_run:{run_id}",
           {"run_month": run_month, "total_gross": calc["total_gross"]}, workspace_id)

    run_record = get_payroll_run(store, run_id)
    run_record["payslips"] = created_slips
    run_record["summary"] = calc
    return run_record


def _now_iso() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
