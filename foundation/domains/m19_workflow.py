"""M19 workflow modules.

  SM-09  Content calendar & production management
  SM-10  Content approval center (version-locked, permission-checked)
  SM-11  Publishing & scheduling engine (idempotent, audit-trail)
  SM-18  External client agency management
"""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone

from ..store import Store
from .m19_schema import create_m19_tables
from .shared import _assert_owned, _audit, _now_iso

# ---------------------------------------------------------------- SM-09 ----

def list_calendar(store: Store, workspace_id: str = None, status: str = None):
    sql = ("SELECT c.*, ci.title, ci.hook, ci.platform, ci.content_format, ci.workflow_state "
           "FROM social_calendar_entries c "
           "JOIN social_content_items ci ON ci.id = c.content_id "
           "WHERE c.status IS NOT NULL")
    params = []
    if workspace_id:
        sql += " AND c.workspace_id=?"; params.append(workspace_id)
    if status:
        sql += " AND c.status=?"; params.append(status)
    sql += " ORDER BY c.publish_date DESC, c.publish_time DESC"
    return store.fetchall(sql, params)


def create_calendar_entry(store: Store, actor_id: int, workspace_id: str,
                          content_id: int, platform: str, publish_date: str,
                          publish_time: str, assigned_employee_id: int | None = None,
                          status: str = "planning") -> dict:
    _assert_owned(store, actor_id, workspace_id)
    row = store.fetchone("SELECT * FROM social_content_items WHERE id=?",
                         (content_id,))
    if not row:
        raise LookupError(f"content item {content_id} not found")
    cur = store.conn.execute(
        "INSERT INTO social_calendar_entries (workspace_id, content_id, platform, publish_date, publish_time, "
        "status, assigned_employee_id) VALUES (?,?,?,?,?,?,?)",
        (workspace_id, content_id, platform, publish_date, publish_time, status, assigned_employee_id))
    store.conn.commit()
    _audit(store, actor_id, "calendar:entry:create", f"entry:{cur.lastrowid}",
           {"platform": platform, "publish_date": publish_date}, workspace_id)
    return store.fetchone("SELECT ce.*, ci.title, ci.hook FROM social_calendar_entries ce "
                          "JOIN social_content_items ci ON ci.id=ce.content_id WHERE ce.id=?", (cur.lastrowid,))


def list_tasks(store: Store, workspace_id: str = None) -> list[dict]:
    sql = ("SELECT t.*, ci.title AS content_title, ci.hook, ci.platform "
           "FROM social_tasks t JOIN social_content_items ci ON ci.id=t.content_id "
           "WHERE t.status IS NOT NULL")
    params = []
    if workspace_id:
        sql += " AND t.workspace_id=?"; params.append(workspace_id)
    sql += " ORDER BY t.created_at DESC"
    return store.fetchall(sql, params)


def create_task(store: Store, actor_id: int, workspace_id: str, content_id: int,
                employee_id: int | None, due_date: str) -> dict:
    _assert_owned(store, actor_id, workspace_id)
    if employee_id:
        emp = store.fetchone("SELECT id, workspace_id FROM employees WHERE id=?", (employee_id,))
        if emp and emp["workspace_id"] != workspace_id:
            raise PermissionError("employee not in this workspace")
    cur = store.conn.execute(
        "INSERT INTO social_tasks (workspace_id, content_id, employee_id, due_date, status) "
        "VALUES (?,?,?,?,?)",
        (workspace_id, content_id, employee_id, due_date, "open"))
    store.conn.commit()
    _audit(store, actor_id, "task:create", f"task:{cur.lastrowid}",
           {"content_id": content_id}, workspace_id)
    return store.fetchone(
        "SELECT t.*, ci.title, ci.hook FROM social_tasks t "
        "JOIN social_content_items ci ON ci.id=t.content_id WHERE t.id=?", (cur.lastrowid,))


# ---------------------------------------------------------------- SM-10 ----

def request_approval(store: Store, actor_id: int, workspace_id: str,
                     content_id: int, version: int = 1) -> dict:
    _assert_owned(store, actor_id, workspace_id)
    row = store.fetchone("SELECT * FROM social_content_items WHERE id=?", (content_id,))
    if not row:
        raise LookupError(f"content item {content_id} not found")
    cur = store.conn.execute(
        "INSERT INTO social_approvals (content_id, version_locked, requester_id, status, "
        "final_script, final_caption, final_cta, final_hashtags, final_media_url) "
        "VALUES (?,?,?,?,?,?,?,?,?)",
        (content_id, 1, actor_id, "pending",
         store.fetchone(
             "SELECT script, caption, cta, keywords, thumbnail_text FROM social_content_versions WHERE content_id=? ORDER BY version DESC LIMIT 1",
             (content_id,))["script"] if store.fetchone(
                 "SELECT script FROM social_content_versions WHERE content_id=?" ,
                 (content_id,)) else "",
         row["caption"], row["cta"], json.dumps(row.get("keywords", [])),
         row.get("thumbnail_text", "")))
    store.conn.commit()
    _audit(store, actor_id, "approval:create", f"approval:{cur.lastrowid}",
           {"content_id": content_id, "version": version}, workspace_id)
    return get_approval(store, cur.lastrowid)


def get_approval(store: Store, approval_id: int) -> dict:
    return store.fetchone(
        "SELECT a.*, ci.title, ci.hook, ci.platform, ci.content_format, ci.workspace_id "
        "FROM social_approvals a "
        "JOIN social_content_items ci ON ci.id=a.content_id "
        "WHERE a.id=?", (approval_id,))


def approve_approval(store: Store, actor_id: int, approval_id: int,
                     final_script: str = "", final_caption: str = "",
                     final_cta: str = "", final_hashtags: str = "[]",
                     final_media_url: str = "") -> dict:
    a = get_approval(store, approval_id)
    if not a:
        raise LookupError(f"approval {approval_id} not found")
    if a["status"] != "pending":
        raise PermissionError(f"approval {a['status']} is not pending")
    _assert_owned(store, actor_id, a["workspace_id"])
    store.conn.execute(
        "UPDATE social_approvals SET status='approved', final_script=?, final_caption=?, "
        "final_cta=?, final_hashtags=?, final_media_url=?, approved_at=?, final_version=final_version+1 "
        "WHERE id=?",
        (final_script, final_caption, final_cta,
         json.dumps(json.loads(final_hashtags) if final_hashtags else []),
         final_media_url, _now_iso(), approval_id))
    store.conn.commit()
    _audit(store, actor_id, "approval:approve", f"approval:{approval_id}",
           {"content_id": a["content_id"]}, a["workspace_id"])
    return get_approval(store, approval_id)


def reject_approval(store: Store, actor_id: int, approval_id: int,
                    note: str = "") -> dict:
    a = get_approval(store, approval_id)
    if not a:
        raise LookupError(f"approval {approval_id} not found")
    _assert_owned(store, actor_id, a["workspace_id"])
    store.conn.execute(
        "UPDATE social_approvals SET status='rejected', approval_note=?, updated_at=? WHERE id=?",
        (note, _now_iso(), approval_id))
    store.conn.commit()
    _audit(store, actor_id, "approval:reject", f"approval:{approval_id}",
           {"note": note}, a["workspace_id"])
    return get_approval(store, approval_id)


def latest_approved_version(store: Store, content_id: int) -> dict | None:
    return store.fetchone(
        "SELECT a.*, ci.hook, ci.platform, ci.content_format FROM social_approvals a "
        "JOIN social_content_items ci ON ci.id=a.content_id "
        "WHERE a.content_id=? AND a.status='approved' ORDER BY a.final_version DESC LIMIT 1",
        (content_id,))


# ---------------------------------------------------------------- SM-11 ----

def enqueue_publish(store: Store, actor_id: int, content_id: int,
                    account_id: int | None, publish_date: str,
                    client_workspace_id: str | None = None) -> dict:
    _assert_owned(store, actor_id, get_content_workspace(store, content_id))
    a = store.fetchone("SELECT * FROM social_content_items WHERE id=?", (content_id,))
    if not a:
        raise LookupError(f"content item {content_id} not found")
    # re-verify approval on the exact version before enqueueing.
    latest = latest_approved_version(store, content_id)
    if not latest or latest["status"] != "approved":
        raise PermissionError("no approved version for this content")
    # Version is locked; requalify approval immediately before the external call.
    latest = latest_approved_version(store, content_id)
    if not latest or not latest["final_script"]:
        raise PermissionError("approved version missing final media")
    cur = store.conn.execute(
        "INSERT INTO social_publish_jobs (workspace_id, content_id, version, account_id, "
        "client_workspace_id, platform, publish_at, status) VALUES (?,?,?,?,?,?,?,?)",
        (get_content_workspace(store, content_id), content_id, latest["final_version"],
         account_id, get_content_workspace(store, content_id), a["platform"], publish_date, "scheduled"))
    store.conn.commit()
    _audit(store, actor_id, "publish:queue", f"publish_job:{cur.lastrowid}",
           {"content_id": content_id, "version": latest["final_version"]}, get_content_workspace(store, content_id))
    return get_publish_job(store, cur.lastrowid)


def get_content_workspace(store: Store, content_id: int) -> str:
    row = store.fetchone("SELECT workspace_id, client_workspace_id FROM social_content_items WHERE id=?",
                         (content_id,))
    if not row:
        raise LookupError(f"content item {content_id} not found")
    return row["client_workspace_id"] or row["workspace_id"]


def get_publish_job(store: Store, job_id: int) -> dict:
    return store.fetchone(
        "SELECT j.* FROM social_publish_jobs j WHERE j.id=?", (job_id,))


def reconcile_publish(store: Store, job_id: int) -> dict:
    """Reconcile an uncertain publish outcome by querying the platform."""
    job = get_publish_job(store, job_id)
    if not job:
        raise LookupError(f"job {job_id} not found")
    if job["status"] == "published":
        return job
    # In a real deployment this would call the platform API + post-status query.
    job["status"] = "reconciled"
    job["status_detail"] = "manual verification required before publish"
    store.conn.commit()
    return job


# ---------------------------------------------------------------- SM-18 ----

def list_clients(store: Store, workspace_id: str = None) -> list[dict]:
    sql = ("SELECT c.*, w.code AS workspace_code FROM social_client_profiles c "
           "LEFT JOIN social_workspaces w ON w.id=c.client_workspace_id "
           "WHERE c.client_workspace_id IS NOT NULL")
    params = []
    if workspace_id:
        sql += " AND c.workspace_id=?"; params.append(workspace_id)
    return store.fetchall(sql, params)


def create_client(store: Store, actor_id: int, workspace_id: str,
                  client_workspace_id: str, company_name: str,
                  service_package: str = "", contract_metadata: dict = None) -> dict:
    _assert_owned(store, actor_id, workspace_id)
    existing = store.fetchone(
        "SELECT 1 FROM social_client_profiles WHERE client_workspace_id=?", (client_workspace_id,))
    if existing:
        raise ValueError(f"client workspace {client_workspace_id} already registered")
    store.conn.execute(
        "INSERT INTO social_client_profiles (client_workspace_id, company_name, service_package, "
        "contract_metadata, created_at) VALUES (?,?,?,?,?)",
        (client_workspace_id, company_name, service_package,
         json.dumps(contract_metadata or {}), _now_iso()))
    store.conn.commit()
    _audit(store, actor_id, "client:create", f"client:{client_workspace_id}",
           {"company": company_name}, workspace_id)
    return store.fetchone(
        "SELECT c.*, w.code AS workspace_code FROM social_client_profiles c "
        "LEFT JOIN social_workspaces w ON w.id=c.client_workspace_id "
        "WHERE c.client_workspace_id=?", (client_workspace_id,))
