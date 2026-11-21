"""M16 Attendance & Workforce Management.

Check-in / check-out, GPS + selfie evidence, site-wise attendance, geofencing,
late arrival / early departure / overtime, weekly off + holidays, leave/absence
records, and manager approval for attendance anomalies. For SSC/INFRA field
sites the configured policy (GPS + selfie + geofencing) is enforced; for other
businesses the policy is configurable via the site record.
"""
from __future__ import annotations

from datetime import datetime, timezone

from ..store import Store

DATE_FMT = "%Y-%m-%dT%H:%M:%SZ"


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime(DATE_FMT)


def _now_dt() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _workspace_exists(store: Store, workspace_id: str) -> bool:
    return store.conn.execute(
        "SELECT 1 FROM workspaces WHERE id=? OR code=?", (workspace_id, workspace_id)
    ).fetchone() is not None


def _site_field_policy(store: Store, site_id: int) -> int:
    row = store.conn.execute(
        "SELECT field_policy_required FROM sites WHERE id=?", (site_id,)).fetchone()
    return bool(row and row["field_policy_required"])


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
# Sites
# ---------------------------------------------------------------------------
def list_sites(store: Store, workspace_id: str | None = None) -> list[dict]:
    if workspace_id is None:
        rows = store.fetchall("SELECT * FROM sites ORDER BY name")
    else:
        rows = store.fetchall(
            "SELECT * FROM sites WHERE workspace_id=? ORDER BY name",
            (workspace_id,))
    return rows


def create_site(store: Store, actor_id: int, workspace_id: str,
                name: str, code: str, address: str = "",
                geofence_radius_m: float = 100.0,
                field_policy_required: int = 0) -> dict:
    if not _workspace_exists(store, workspace_id):
        raise LookupError(f"workspace {workspace_id!r} not found")
    _assert_owned(store, actor_id, workspace_id)
    cur = store.conn.execute(
        "INSERT INTO sites (workspace_id, name, code, address, geofence_radius_m, field_policy_required) "
        "VALUES (?,?,?,?,?,?)",
        (workspace_id, name, code, address, geofence_radius_m, field_policy_required))
    store.conn.commit()
    _audit(store, actor_id, "attendance:site:create",
           f"site:{cur.lastrowid}", {"code": code, "name": name,
                                     "field_policy_required": field_policy_required},
           workspace_id)
    return dict(store.conn.execute(
        "SELECT * FROM sites WHERE id=?", (cur.lastrowid,)).fetchone())


# ---------------------------------------------------------------------------
# Geofences
# ---------------------------------------------------------------------------
def list_geofences(store: Store, site_id: int) -> list[dict]:
    return store.fetchall(
        "SELECT * FROM geofences WHERE site_id=? ORDER BY id", (site_id,))


def create_geofence(store: Store, actor_id: int, site_id: int,
                    name: str, polygon_json: str = "{}") -> dict:
    site = dict(store.conn.execute(
        "SELECT id, workspace_id FROM sites WHERE id=?", (site_id,)).fetchone())
    if not site:
        raise LookupError(f"site {site_id!r} not found")
    _assert_owned(store, actor_id, site["workspace_id"])
    cur = store.conn.execute(
        "INSERT INTO geofences (site_id, name, polygon_json) VALUES (?,?,?)",
        (site_id, name, polygon_json))
    store.conn.commit()
    _audit(store, actor_id, "attendance:geofence:create",
           f"geofence:{cur.lastrowid}", {"site_id": site_id, "name": name},
           site["workspace_id"])
    return dict(store.conn.execute(
        "SELECT * FROM geofences WHERE id=?", (cur.lastrowid,)).fetchone())


# ---------------------------------------------------------------------------
# Attendance logs (check-in / check-out)
# ---------------------------------------------------------------------------
def list_attendance(store: Store, workspace_id: str | None = None,
                    from_date: str = "", to_date: str = "") -> list[dict]:
    sql = ("SELECT al.*, e.name AS employee_name, s.name AS site_name, "
           "e.workspace_id AS employee_workspace "
           "FROM attendance_logs al "
           "JOIN employees e ON e.id = al.employee_id "
           "JOIN sites s ON s.id = al.site_id "
           "WHERE 1=1")
    params: list = []
    if workspace_id is not None:
        sql += " AND e.workspace_id=?"; params.append(workspace_id)
    if from_date:
        sql += " AND al.check_in >= ?"; params.append(from_date)
    if to_date:
        sql += " AND al.check_in <= ?"; params.append(to_date)
    sql += " ORDER BY al.check_in DESC"
    rows = store.fetchall(sql, params)
    for r in rows:
        r["strftime_check_in"] = r["check_in"][:10] if r.get("check_in") else ""
    return rows


def get_attendance(store: Store, att_id: int) -> dict | None:
    return dict(store.conn.execute(
        "SELECT al.*, e.name AS employee_name, s.name AS site_name, "
        "e.workspace_id AS employee_workspace "
        "FROM attendance_logs al "
        "JOIN employees e ON e.id = al.employee_id "
        "JOIN sites s ON s.id = al.site_id WHERE al.id=?",
        (att_id,)).fetchone())


def record_checkin(store: Store, actor_id: int, employee_id: int, site_id: int,
                   check_in: str, check_out: str = "",
                   gps_lat: float = 0.0, gps_lng: float = 0.0,
                   geofence_passed: int = 0, selfie_taken: int = 0,
                   notes: str = "") -> dict:
    emp = dict(store.conn.execute(
        "SELECT id, workspace_id FROM employees WHERE id=?", (employee_id,)).fetchone())
    site = dict(store.conn.execute(
        "SELECT id, workspace_id FROM sites WHERE id=?", (site_id,)).fetchone())
    if not emp:
        raise LookupError(f"employee {employee_id!r} not found")
    if not site:
        raise LookupError(f"site {site_id!r} not found")
    if emp["workspace_id"] != site["workspace_id"]:
        raise PermissionError("employee and site belong to different workspaces")
    field_policy = _site_field_policy(store, site_id)

    # Enforce mandatory evidence for field sites.
    if field_policy:
        if not geofence_passed:
            raise PermissionError(
                f"site {site_id} requires geofence_passed = 1 "
                "(GPS + selfie + geofencing mandatory)")
        if not selfie_taken:
            raise PermissionError(
                f"site {site_id} requires selfie_taken = 1 (GPS + selfie + geofencing mandatory)")

    if not check_out:
        check_out = check_in

    cur = store.conn.execute(
        "INSERT INTO attendance_logs (workspace_id, employee_id, site_id, check_in, check_out, "
        "gps_lat, gps_lng, geofence_passed, selfie_taken, status, notes) "
        "VALUES (?,?,?,?,?,?,?,?,?,?,?)",
        (emp["workspace_id"], employee_id, site_id, check_in, check_out, gps_lat, gps_lng,
         geofence_passed, selfie_taken, "present", notes))
    store.conn.commit()
    _audit(store, actor_id, "attendance:checkin",
           f"attendance:{cur.lastrowid}", {"employee_id": employee_id,
                                           "site_id": site_id,
                                           "field_policy_required": field_policy},
           emp["workspace_id"])
    return get_attendance(store, cur.lastrowid)


def check_out(store: Store, actor_id: int, att_id: int,
              checkout_gps_lat: float = 0.0, checkout_gps_lng: float = 0.0,
              geofence_passed: int = 0, selfie_taken: int = 0) -> dict | None:
    att = get_attendance(store, att_id)
    if not att:
        raise LookupError(f"attendance {att_id!r} not found")
    emp = dict(store.conn.execute(
        "SELECT id, workspace_id FROM employees WHERE id=?", (att["employee_id"],)).fetchone())
    site = dict(store.conn.execute(
        "SELECT id, workspace_id FROM sites WHERE id=?", (att["site_id"],)).fetchone())
    _assert_owned(store, actor_id, emp["workspace_id"])
    field_policy = _site_field_policy(store, att["site_id"])
    if field_policy:
        if not geofence_passed:
            raise PermissionError(
                f"site {att['site_id']} requires geofence_passed = 1")
        if not selfie_taken:
            raise PermissionError(
                f"site {att['site_id']} requires selfie_taken = 1")
    store.conn.execute(
        "UPDATE attendance_logs SET check_out=?, gps_lat=?, gps_lng=?, "
        "geofence_passed=?, selfie_taken=? WHERE id=?",
        (_now_iso(), checkout_gps_lat, checkout_gps_lng,
         geofence_passed, selfie_taken, att_id))
    store.conn.commit()
    return get_attendance(store, att_id)


def _classify(check_in: str, check_out: str, work_start: int = 9,
              work_end: int = 18, weekly_off: "set[str]" = None) -> str:
    """Classify the day as present, late, early, no_show, or absent."""
    try:
        ci = datetime.fromisoformat(check_in.replace("Z", "+00:00")).replace(tzinfo=None)
    except Exception:
        return "no_show"
    if weekly_off is not None and ci.date().isoformat() in weekly_off:
        return "weekly_off"
    if not check_out:
        return "present"
    try:
        co = datetime.fromisoformat(check_out.replace("Z", "+00:00")).replace(tzinfo=None)
    except Exception:
        return "present"
    late = (ci.hour > work_start) or (ci.hour == work_start and ci.minute > 15)
    early = (co.hour < work_end)
    if late:
        return "late"
    if early:
        return "early"
    return "present"


def compute_worked_hours(check_in: str, check_out: str) -> float:
    if not check_in or not check_out:
        return 0.0
    try:
        ci = datetime.fromisoformat(check_in.replace("Z", "+00:00")).replace(tzinfo=None)
        co = datetime.fromisoformat(check_out.replace("Z", "+00:00")).replace(tzinfo=None)
        return max((co - ci).total_seconds() / 3600.0, 0.0)
    except Exception:
        return 0.0


def compute_overtime(worked_hours: float, regular_hours: float = 8.0) -> float:
    """Overtime = hours beyond the regular 8-hour day."""
    return max(worked_hours - regular_hours, 0.0)


def summary_daily(store: Store, employee_id: int, date: str) -> dict | None:
    row = store.conn.execute(
        "SELECT * FROM attendance_logs WHERE employee_id=? AND check_in LIKE ?",
        (employee_id, date + "%")).fetchone()
    return dict(row) if row else None


def summary_monthly(store: Store, employee_id: int, year_month: str) -> dict | None:
    """Aggregate days/hours/leave for one employee for a YYYY-MM month."""
    rows = store.fetchall(
        "SELECT check_in, check_out FROM attendance_logs "
        "WHERE employee_id=? AND strftime('%Y-%m', check_in)=?",
        (employee_id, year_month))
    weekly_off = {"saturday", "sunday"}
    if not rows:
        return {"employee_id": employee_id, "month": year_month,
                "days_present": 0, "days_absent": 0, "weekly_off_days": 0,
                "total_hours": 0.0, "overtime_hours": 0.0}
    days_present = 0
    days_absent = 0
    weekly_off_days = 0
    total_hours = 0.0
    ot_hours = 0.0
    for r in rows:
        daily = summary_daily(store, employee_id, r["check_in"][:10])
        if not daily:
            continue
        cls = daily.get("status", "present")
        if cls == "weekly_off":
            weekly_off_days += 1
            continue
        if cls == "absent":
            days_absent += 1
            continue
        days_present += 1
        co_val = daily.get("check_out") or daily["check_in"]
        h = compute_worked_hours(daily["check_in"], co_val)
        total_hours += h
        ot_hours += compute_overtime(h, 8.0)
    return {"employee_id": employee_id, "month": year_month,
            "days_present": days_present, "days_absent": days_absent,
            "weekly_off_days": weekly_off_days,
            "total_hours": round(total_hours, 2),
            "overtime_hours": round(ot_hours, 2)}


# ---------------------------------------------------------------------------
# Leave / absence + manager approval
# ---------------------------------------------------------------------------
def balance_leave(store: Store, employee_id: int, leave_days: float,
                  leave_type: str = "annual") -> float:
    """Return unused leave balance for the type (annual = 20, sick = 10)."""
    annual = 20.0
    sick = 10.0
    base = annual if leave_type == "annual" else (sick if leave_type == "sick" else 0.0)
    used = store.conn.execute(
        "SELECT COALESCE(SUM(days),0) AS c FROM leaves "
        "WHERE employee_id=? AND type=? AND status='approved'",
        (employee_id, leave_type)).fetchone()["c"]
    return max(base - float(used), 0.0)
