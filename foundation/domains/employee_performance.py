# -*- coding: utf-8 -*-
"""SHAH GROUP AI OS — Employee Performance & Field Productivity Analytics Engine.

Provides:
  1. Individual Employee Performance Scorecards (Attendance, Task Delivery, Geofenced Accuracy).
  2. Performance Grades: A+ (Star Performer), A (Consistent), B (Average), C (Needs Attention).
  3. Actionable AI Recommendations for each staff member.
  4. Team Leaderboard, Attendance Reliability Index, and Project Delivery Metrics.
"""
from __future__ import annotations

import sqlite3
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List

KOLKATA_TZ = timezone(timedelta(hours=5, minutes=30))


def now_kolkata() -> datetime:
    return datetime.now(KOLKATA_TZ)


def now_kolkata_iso() -> str:
    return now_kolkata().strftime("%Y-%m-%d %H:%M:%S")


def get_employee_performance_analytics(conn: sqlite3.Connection, workspace_id: str = "SSC") -> Dict[str, Any]:
    """Computes comprehensive performance scorecards for all employees in the workspace."""
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # 1. Fetch all active employees
    cur.execute(
        """
        SELECT id, employee_id, name, designation, department_id, email, phone, hire_date, status
        FROM employees
        WHERE workspace_id = ?
        ORDER BY name ASC
        """,
        (workspace_id,)
    )
    emp_rows = [dict(r) for r in cur.fetchall()]

    # Date boundary: Last 30 days
    last_30_days = (now_kolkata() - timedelta(days=30)).strftime("%Y-%m-%d")

    scorecards = []

    for emp in emp_rows:
        eid = emp["id"]
        emp_name = emp["name"]

        # Attendance Metrics (last 30 days)
        cur.execute(
            """
            SELECT COUNT(id) AS total_punches,
                   COALESCE(SUM(CASE WHEN geofence_passed = 1 THEN 1 ELSE 0 END), 0) AS geofence_valid,
                   COALESCE(SUM(CASE WHEN check_out IS NOT NULL AND check_out != '' THEN 1 ELSE 0 END), 0) AS completed_shifts
            FROM attendance_logs
            WHERE workspace_id = ? AND employee_id = ? AND date(created_at) >= date(?)
            """,
            (workspace_id, eid, last_30_days)
        )
        att_row = cur.fetchone()
        total_punches = int(att_row["total_punches"]) if att_row else 0
        geofence_valid = int(att_row["geofence_valid"]) if att_row else 0
        geofence_accuracy_pct = round((geofence_valid / total_punches * 100), 1) if total_punches > 0 else 100.0

        # Estimated total hours worked (assuming 8 hours per full shift as baseline or real duration)
        hours_worked = round(total_punches * 8.0, 1)

        # Leave Metrics (last 30 days)
        cur.execute(
            """
            SELECT COUNT(id)
            FROM leaves
            WHERE employee_id = ? AND status = 'approved' AND date(start_date) >= date(?)
            """,
            (eid, last_30_days)
        )
        leave_days = int(cur.fetchone()[0] or 0)

        # Task Execution Metrics
        cur.execute(
            """
            SELECT COUNT(id) AS total_tasks,
                   COALESCE(SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END), 0) AS completed_tasks,
                   COALESCE(SUM(CASE WHEN status = 'in_progress' THEN 1 ELSE 0 END), 0) AS in_progress_tasks,
                   COALESCE(SUM(CASE WHEN status IN ('pending', 'open') THEN 1 ELSE 0 END), 0) AS pending_tasks,
                   COALESCE(AVG(progress_pct), 0) AS avg_progress
            FROM employee_tasks
            WHERE workspace_id = ? AND (assigned_to = ? OR assigned_to = ?)
            """,
            (workspace_id, eid, emp_name)
        )
        task_row = cur.fetchone()
        total_tasks = int(task_row["total_tasks"]) if task_row else 0
        completed_tasks = int(task_row["completed_tasks"]) if task_row else 0
        in_progress_tasks = int(task_row["in_progress_tasks"]) if task_row else 0
        pending_tasks = int(task_row["pending_tasks"]) if task_row else 0
        avg_progress = round(float(task_row["avg_progress"] or 0.0), 1)
        task_completion_rate = round((completed_tasks / total_tasks * 100), 1) if total_tasks > 0 else 85.0

        # Compute Composite Performance Score (0 to 100)
        # Weights: Attendance presence (35%), Geofence accuracy (25%), Task completion rate (40%)
        # Attendance presence score out of 35 (baseline 22 working days in a month)
        working_days_target = 22
        presence_ratio = min(total_punches / working_days_target, 1.0) if total_punches > 0 else 0.8
        att_score = presence_ratio * 35.0

        geo_score = (geofence_accuracy_pct / 100.0) * 25.0
        task_score = (task_completion_rate / 100.0) * 40.0

        raw_score = round(att_score + geo_score + task_score)
        perf_score = max(50, min(raw_score, 99))  # normalize to 50-99 range

        # Assign Grade and Label
        if perf_score >= 90:
            grade = "A+"
            grade_label = "Star Performer (Excellent)"
            status_color = "#10b981"
            ai_recommendation = (
                f"{emp_name} exhibits outstanding punctuality ({total_punches} shifts) with {geofence_accuracy_pct}% "
                f"geofence compliance. Task completion is high ({task_completion_rate}%). Ideal candidate for site lead "
                "or handling high-value highway DPR survey assignments."
            )
        elif perf_score >= 78:
            grade = "A"
            grade_label = "Consistent & Reliable"
            status_color = "#38bdf8"
            ai_recommendation = (
                f"{emp_name} maintains steady field attendance ({total_punches} shifts) and solid delivery ({completed_tasks} completed tasks). "
                "Maintain current project allocation and monitor on-time submission."
            )
        elif perf_score >= 65:
            grade = "B"
            grade_label = "Average (Steady Progress)"
            status_color = "#f59e0b"
            ai_recommendation = (
                f"{emp_name} has {pending_tasks} pending tasks. Site geofence accuracy is {geofence_accuracy_pct}%. "
                "Recommend weekly review meeting with Project Manager to unblock active field tasks."
            )
        else:
            grade = "C"
            grade_label = "Needs Attention"
            status_color = "#ef4444"
            ai_recommendation = (
                f"Attendance or task delivery is lower than team average ({total_punches} shifts logged, {pending_tasks} pending). "
                "Check for site transport issues or reassign to pairing with a senior surveyor."
            )

        scorecards.append({
            "employee_id": eid,
            "emp_code": emp.get("employee_id") or f"EMP-{eid:03d}",
            "name": emp_name,
            "designation": emp.get("designation") or "Field Engineer",
            "department": emp.get("department_id") or "Operations",
            "phone": emp.get("phone") or "",
            "performance_score": perf_score,
            "grade": grade,
            "grade_label": grade_label,
            "status_color": status_color,
            "attendance": {
                "total_shifts_30d": total_punches,
                "geofence_accuracy_pct": geofence_accuracy_pct,
                "hours_worked": hours_worked,
                "leaves_taken": leave_days
            },
            "tasks": {
                "total": total_tasks,
                "completed": completed_tasks,
                "in_progress": in_progress_tasks,
                "pending": pending_tasks,
                "completion_rate_pct": task_completion_rate,
                "avg_progress_pct": avg_progress
            },
            "ai_recommendation": ai_recommendation
        })

    # Sort scorecards by performance_score descending (Leaderboard)
    scorecards.sort(key=lambda x: x["performance_score"], reverse=True)

    # Team Summary Analytics
    total_staff = len(scorecards)
    avg_score = round(sum(s["performance_score"] for s in scorecards) / total_staff, 1) if total_staff > 0 else 82.0
    top_performers = scorecards[:3] if total_staff >= 3 else scorecards
    total_completed_tasks_team = sum(s["tasks"]["completed"] for s in scorecards)
    avg_attendance_reliability = round(sum(s["attendance"]["geofence_accuracy_pct"] for s in scorecards) / total_staff, 1) if total_staff > 0 else 95.0

    return {
        "ok": True,
        "workspace_id": workspace_id,
        "generated_at": now_kolkata_iso(),
        "team_summary": {
            "total_staff_analyzed": total_staff,
            "team_average_performance_score": avg_score,
            "team_attendance_reliability_pct": avg_attendance_reliability,
            "total_completed_tasks_30d": total_completed_tasks_team,
            "top_performer": top_performers[0]["name"] if top_performers else "N/A"
        },
        "scorecards": scorecards,
        "leaderboard": [
            {
                "rank": idx + 1,
                "name": s["name"],
                "designation": s["designation"],
                "score": s["performance_score"],
                "grade": s["grade"],
                "shifts": s["attendance"]["total_shifts_30d"],
                "tasks_completed": s["tasks"]["completed"]
            }
            for idx, s in enumerate(scorecards)
        ]
    }
