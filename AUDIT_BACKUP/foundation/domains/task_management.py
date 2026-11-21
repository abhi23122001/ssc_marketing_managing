# -*- coding: utf-8 -*-
"""SHAH GROUP AI OS — Employee Task Management & Workload Dashboard.

Full Lifecycle Workflow:
  Admin / Manager creates task -> Assigns Employee -> Employee sees in My Tasks ->
  Accepts Task -> Updates Progress (0-100%) -> Submits Work Proof -> Manager Reviews ->
  Approves (Closed) OR Requests Rework (Rework Notes).

Features:
  - My Tasks, Today's Tasks, Upcoming & Overdue Tasks, Project-Linked Tasks.
  - Priority (urgent/high/medium/low) & Deadlines.
  - Work proof submission (text + deliverable attachment link).
  - Comments & Activity Audit.
  - In-app notification queue (`task_notifications`).
  - Admin Workload Dashboard & Employee-wise performance metrics.
  - Multi-tenant workspace isolation & RBAC enforcement.
"""
from __future__ import annotations

import json
import sqlite3
import time
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Tuple

from ..store import Store

KOLKATA_TZ = timezone(timedelta(hours=5, minutes=30))


def now_kolkata_iso() -> str:
    return datetime.now(KOLKATA_TZ).strftime("%Y-%m-%dT%H:%M:%S%z")


def now_kolkata_date() -> str:
    return datetime.now(KOLKATA_TZ).strftime("%Y-%m-%d")


def ensure_tasks_schema(conn: sqlite3.Connection) -> None:
    """Creates persistent tables for tasks, comments, and task notifications."""
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS employee_tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        workspace_id TEXT NOT NULL,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        category TEXT NOT NULL DEFAULT 'general',
        project_id TEXT,
        assigned_to INTEGER NOT NULL,  -- user_id / employee_id
        assigned_by INTEGER NOT NULL,  -- manager user_id
        priority TEXT NOT NULL DEFAULT 'medium',  -- 'urgent', 'high', 'medium', 'low'
        deadline_date TEXT NOT NULL,              -- YYYY-MM-DD
        status TEXT NOT NULL DEFAULT 'assigned',  -- 'assigned', 'accepted', 'in_progress', 'submitted', 'approved', 'rework_requested', 'closed'
        progress_pct INTEGER NOT NULL DEFAULT 0,
        work_proof_text TEXT,
        work_proof_url TEXT,
        rework_notes TEXT,
        created_at TEXT NOT NULL DEFAULT (datetime('now')),
        updated_at TEXT NOT NULL DEFAULT (datetime('now')),
        closed_at TEXT
    );

    CREATE TABLE IF NOT EXISTS task_comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        author_name TEXT NOT NULL,
        comment_text TEXT NOT NULL,
        created_at TEXT NOT NULL DEFAULT (datetime('now')),
        FOREIGN KEY (task_id) REFERENCES employee_tasks(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS task_notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        task_id INTEGER,
        title TEXT NOT NULL,
        message TEXT NOT NULL,
        is_read INTEGER NOT NULL DEFAULT 0,
        created_at TEXT NOT NULL DEFAULT (datetime('now'))
    );

    CREATE INDEX IF NOT EXISTS idx_employee_tasks_assignee ON employee_tasks(assigned_to);
    CREATE INDEX IF NOT EXISTS idx_employee_tasks_workspace ON employee_tasks(workspace_id);
    CREATE INDEX IF NOT EXISTS idx_employee_tasks_deadline ON employee_tasks(deadline_date);
    CREATE INDEX IF NOT EXISTS idx_task_notifications_user ON task_notifications(user_id);
    """)
    conn.commit()


# -----------------------------------------------------------------------------
# Task Creation & Assignment
# -----------------------------------------------------------------------------

def create_employee_task(store: Store, workspace_id: str, actor_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
    """Creates a new assigned task and notifies the employee."""
    ensure_tasks_schema(store.conn)
    title = data.get("title", "").strip()
    if not title:
        raise ValueError("Task title is required.")
    
    desc = data.get("description", "").strip()
    assigned_to = int(data.get("assigned_to", actor_id))
    category = data.get("category", "field_survey")
    project_id = data.get("project_id")
    priority = data.get("priority", "medium").lower()
    if priority not in ["urgent", "high", "medium", "low"]:
        priority = "medium"
    
    deadline = data.get("deadline_date") or now_kolkata_date()
    now_str = now_kolkata_iso()

    cur = store.conn.execute(
        "INSERT INTO employee_tasks (workspace_id, title, description, category, project_id, "
        "assigned_to, assigned_by, priority, deadline_date, status, progress_pct, created_at, updated_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'assigned', 0, ?, ?)",
        (workspace_id, title, desc, category, project_id, assigned_to, actor_id, priority, deadline, now_str, now_str)
    )
    task_id = cur.lastrowid

    # Create notification for assignee
    assigner_row = store.fetchone("SELECT name, username FROM users WHERE id=?", (actor_id,))
    assigner_name = assigner_row["name"] if assigner_row else "Management"
    store.conn.execute(
        "INSERT INTO task_notifications (user_id, task_id, title, message, is_read, created_at) "
        "VALUES (?, ?, ?, ?, 0, ?)",
        (assigned_to, task_id, f"New Task Assigned ({priority.upper()})",
         f"{assigner_name} assigned task: '{title}' due on {deadline}.", now_str)
    )
    store.conn.commit()

    return get_employee_task(store, task_id)


def get_employee_task(store: Store, task_id: int) -> Optional[Dict[str, Any]]:
    """Retrieves full details of a single task including assignee and assigner names."""
    ensure_tasks_schema(store.conn)
    row = store.fetchone("""
    SELECT t.*,
           u1.name AS assignee_name, u1.username AS assignee_username,
           u2.name AS assigner_name, u2.username AS assigner_username
    FROM employee_tasks t
    LEFT JOIN users u1 ON u1.id = t.assigned_to
    LEFT JOIN users u2 ON u2.id = t.assigned_by
    WHERE t.id = ?
    """, (task_id,))
    if not row:
        return None
    d = dict(row)
    d["comments"] = list_task_comments(store, task_id)
    return d


# -----------------------------------------------------------------------------
# Task Workflow State Transitions
# -----------------------------------------------------------------------------

def accept_task(store: Store, task_id: int, actor_id: int) -> Dict[str, Any]:
    """Employee accepts the task."""
    ensure_tasks_schema(store.conn)
    task = get_employee_task(store, task_id)
    if not task:
        raise LookupError(f"Task {task_id} not found.")
    
    store.conn.execute(
        "UPDATE employee_tasks SET status='accepted', updated_at=? WHERE id=?",
        (now_kolkata_iso(), task_id)
    )
    # Add auto-comment
    add_task_comment(store, task_id, actor_id, "Accepted the task and scheduled execution.")
    store.conn.commit()
    return get_employee_task(store, task_id)


def update_task_progress(store: Store, task_id: int, actor_id: int, progress_pct: int, note: str = "") -> Dict[str, Any]:
    """Employee updates work progress (0-100%)."""
    ensure_tasks_schema(store.conn)
    task = get_employee_task(store, task_id)
    if not task:
        raise LookupError(f"Task {task_id} not found.")

    progress_pct = max(0, min(100, int(progress_pct)))
    new_status = "in_progress" if progress_pct < 100 else task["status"]

    store.conn.execute(
        "UPDATE employee_tasks SET progress_pct=?, status=?, updated_at=? WHERE id=?",
        (progress_pct, new_status, now_kolkata_iso(), task_id)
    )
    if note:
        add_task_comment(store, task_id, actor_id, f"Progress updated to {progress_pct}%: {note}")
    store.conn.commit()
    return get_employee_task(store, task_id)


def submit_task_work_proof(store: Store, task_id: int, actor_id: int, proof_text: str, proof_url: str = "") -> Dict[str, Any]:
    """Employee submits deliverable work proof for manager review."""
    ensure_tasks_schema(store.conn)
    task = get_employee_task(store, task_id)
    if not task:
        raise LookupError(f"Task {task_id} not found.")

    now_str = now_kolkata_iso()
    store.conn.execute(
        "UPDATE employee_tasks SET status='submitted', progress_pct=100, work_proof_text=?, "
        "work_proof_url=?, updated_at=? WHERE id=?",
        (proof_text, proof_url, now_str, task_id)
    )
    # Notify manager
    store.conn.execute(
        "INSERT INTO task_notifications (user_id, task_id, title, message, is_read, created_at) "
        "VALUES (?, ?, 'Work Proof Submitted', ?, 0, ?)",
        (task["assigned_by"], task_id, f"Work proof submitted for '{task['title']}' by {task.get('assignee_name','staff')}.", now_str)
    )
    add_task_comment(store, task_id, actor_id, f"Submitted work proof: {proof_text} (Deliverable: {proof_url or 'Attached in project'})")
    store.conn.commit()
    return get_employee_task(store, task_id)


def review_task(store: Store, task_id: int, actor_id: int, decision: str, notes: str = "") -> Dict[str, Any]:
    """Manager reviews submitted task: 'approve' or 'rework'."""
    ensure_tasks_schema(store.conn)
    task = get_employee_task(store, task_id)
    if not task:
        raise LookupError(f"Task {task_id} not found.")

    now_str = now_kolkata_iso()
    decision = decision.lower()
    
    if decision == "approve":
        store.conn.execute(
            "UPDATE employee_tasks SET status='approved', closed_at=?, updated_at=? WHERE id=?",
            (now_str, now_str, task_id)
        )
        store.conn.execute(
            "INSERT INTO task_notifications (user_id, task_id, title, message, is_read, created_at) "
            "VALUES (?, ?, 'Task Approved', ?, 0, ?)",
            (task["assigned_to"], task_id, f"Your deliverable for '{task['title']}' has been APPROVED by management.", now_str)
        )
        add_task_comment(store, task_id, actor_id, f"Quality review PASSED: Task approved and marked complete. {notes}")
    elif decision == "rework":
        store.conn.execute(
            "UPDATE employee_tasks SET status='rework_requested', rework_notes=?, progress_pct=60, updated_at=? WHERE id=?",
            (notes, now_str, task_id)
        )
        store.conn.execute(
            "INSERT INTO task_notifications (user_id, task_id, title, message, is_read, created_at) "
            "VALUES (?, ?, 'Task Rework Requested', ?, 0, ?)",
            (task["assigned_to"], task_id, f"Rework requested on '{task['title']}': {notes}", now_str)
        )
        add_task_comment(store, task_id, actor_id, f"Review feedback - REWORK REQUIRED: {notes}")
    else:
        raise ValueError("Review decision must be 'approve' or 'rework'.")

    store.conn.commit()
    return get_employee_task(store, task_id)


# -----------------------------------------------------------------------------
# Comments & Activity
# -----------------------------------------------------------------------------

def add_task_comment(store: Store, task_id: int, actor_id: int, text: str) -> Dict[str, Any]:
    """Appends an activity comment to a task."""
    ensure_tasks_schema(store.conn)
    user = store.fetchone("SELECT name, username FROM users WHERE id=?", (actor_id,))
    author_name = user["name"] if user else f"User {actor_id}"

    cur = store.conn.execute(
        "INSERT INTO task_comments (task_id, user_id, author_name, comment_text, created_at) "
        "VALUES (?, ?, ?, ?, ?)",
        (task_id, actor_id, author_name, text, now_kolkata_iso())
    )
    store.conn.commit()
    return {
        "id": cur.lastrowid,
        "task_id": task_id,
        "user_id": actor_id,
        "author_name": author_name,
        "comment_text": text,
        "created_at": now_kolkata_iso()
    }


def list_task_comments(store: Store, task_id: int) -> List[Dict[str, Any]]:
    ensure_tasks_schema(store.conn)
    return store.fetchall("SELECT * FROM task_comments WHERE task_id=? ORDER BY id ASC", (task_id,))


# -----------------------------------------------------------------------------
# Filtered Queries (My Tasks, Today, Upcoming, Overdue, Project)
# -----------------------------------------------------------------------------

def list_employee_tasks(
    store: Store,
    workspace_id: str,
    user_id: Optional[int] = None,
    user_role: str = "Owner",
    filter_type: str = "all",
    status: Optional[str] = None,
    priority: Optional[str] = None,
    project_id: Optional[str] = None,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """Retrieves tasks with comprehensive role-based visibility and filters."""
    ensure_tasks_schema(store.conn)
    today = now_kolkata_date()

    sql = """
    SELECT t.*,
           u1.name AS assignee_name, u1.username AS assignee_username,
           u2.name AS assigner_name, u2.username AS assigner_username
    FROM employee_tasks t
    LEFT JOIN users u1 ON u1.id = t.assigned_to
    LEFT JOIN users u2 ON u2.id = t.assigned_by
    WHERE t.workspace_id = ?
    """
    params: List[Any] = [workspace_id]

    # Non-managers see only their assigned tasks
    is_manager = user_role in ["Owner", "Manager", "Project Manager"]
    if not is_manager and user_id:
        sql += " AND t.assigned_to = ?"
        params.append(user_id)

    # Views
    if filter_type == "my_tasks" and user_id:
        sql += " AND t.assigned_to = ?"
        params.append(user_id)
    elif filter_type == "today_tasks":
        sql += " AND t.deadline_date = ?"
        params.append(today)
    elif filter_type == "upcoming_tasks":
        sql += " AND t.deadline_date > ? AND t.status NOT IN ('approved', 'closed')"
        params.append(today)
    elif filter_type == "overdue_tasks":
        sql += " AND t.deadline_date < ? AND t.status NOT IN ('approved', 'closed')"
        params.append(today)
    elif filter_type == "project_tasks" or project_id:
        if project_id:
            sql += " AND t.project_id = ?"
            params.append(project_id)
        else:
            sql += " AND t.project_id IS NOT NULL AND t.project_id != ''"

    if status:
        sql += " AND t.status = ?"
        params.append(status)
    if priority:
        sql += " AND t.priority = ?"
        params.append(priority)

    sql += " ORDER BY CASE t.priority WHEN 'urgent' THEN 1 WHEN 'high' THEN 2 WHEN 'medium' THEN 3 ELSE 4 END, t.deadline_date ASC LIMIT ?"
    params.append(limit)

    return store.fetchall(sql, params)


# -----------------------------------------------------------------------------
# Admin Workload Dashboard & Performance Metrics
# -----------------------------------------------------------------------------

def get_admin_workload_summary(store: Store, workspace_id: str) -> Dict[str, Any]:
    """Generates an executive workload and employee performance summary."""
    ensure_tasks_schema(store.conn)
    today = now_kolkata_date()

    all_tasks = store.fetchall("SELECT * FROM employee_tasks WHERE workspace_id=?", (workspace_id,))
    total = len(all_tasks)
    active = len([t for t in all_tasks if t["status"] not in ["approved", "closed"]])
    submitted = len([t for t in all_tasks if t["status"] == "submitted"])
    overdue = len([t for t in all_tasks if t["deadline_date"] < today and t["status"] not in ["approved", "closed"]])
    completed = len([t for t in all_tasks if t["status"] in ["approved", "closed"]])

    # Employee-wise breakdown
    employees = store.fetchall("SELECT id, name, username, role_id FROM users WHERE workspace_id=? OR workspace_id='ALL'", (workspace_id,))
    emp_stats = []
    for emp in employees:
        emp_id = emp["id"]
        e_tasks = [t for t in all_tasks if t["assigned_to"] == emp_id]
        if not e_tasks:
            continue
        e_total = len(e_tasks)
        e_done = len([t for t in e_tasks if t["status"] in ["approved", "closed"]])
        e_active = len([t for t in e_tasks if t["status"] not in ["approved", "closed"]])
        e_overdue = len([t for t in e_tasks if t["deadline_date"] < today and t["status"] not in ["approved", "closed"]])
        rate = round((e_done / e_total) * 100, 1) if e_total > 0 else 100.0

        emp_stats.append({
            "user_id": emp_id,
            "name": emp["name"],
            "username": emp["username"],
            "total_tasks": e_total,
            "active_tasks": e_active,
            "completed_tasks": e_done,
            "overdue_tasks": e_overdue,
            "completion_rate_pct": rate
        })

    emp_stats.sort(key=lambda x: x["active_tasks"], reverse=True)

    return {
        "workspace_id": workspace_id,
        "date": today,
        "total_tasks": total,
        "active_tasks": active,
        "pending_review_count": submitted,
        "overdue_count": overdue,
        "completed_count": completed,
        "overall_completion_rate": round((completed / total) * 100, 1) if total > 0 else 100.0,
        "employee_performance": emp_stats
    }


# -----------------------------------------------------------------------------
# Notifications
# -----------------------------------------------------------------------------

def list_user_notifications(store: Store, user_id: int, unread_only: bool = False) -> List[Dict[str, Any]]:
    ensure_tasks_schema(store.conn)
    sql = "SELECT * FROM task_notifications WHERE user_id=?"
    params: List[Any] = [user_id]
    if unread_only:
        sql += " AND is_read=0"
    sql += " ORDER BY id DESC LIMIT 20"
    return store.fetchall(sql, params)


def mark_notification_read(store: Store, notif_id: int, user_id: int) -> bool:
    ensure_tasks_schema(store.conn)
    store.conn.execute("UPDATE task_notifications SET is_read=1 WHERE id=? AND user_id=?", (notif_id, user_id))
    store.conn.commit()
    return True
