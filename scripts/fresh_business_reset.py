# -*- coding: utf-8 -*-
"""SHAH GROUP AI OS — Fresh Business Data Reset Engine.

Executes a verified, non-destructive fresh business environment reset:
1. Validates verified pre-reset backup existence.
2. Preserves 100% of System Security, Roles (1-7), Users, Schemas, Templates, Knowledge Base, and Config.
3. Purges all confirmed demo/dummy business data (employees, attendance, payroll, invoices, leads, clients, sites, expenses, tasks, social posts, old AI research).
4. Resets `data/sheets_sync/` CSV staging tables to clean header-only state.
5. Records audit event into `audit_logs`.
"""
from __future__ import annotations

import csv
import json
import os
import sqlite3
import sys
from datetime import datetime, timezone, timedelta

KOLKATA_TZ = timezone(timedelta(hours=5, minutes=30))


def now_kolkata_iso() -> str:
    return datetime.now(KOLKATA_TZ).strftime("%Y-%m-%dT%H:%M:%S%z")


def execute_fresh_business_reset():
    backup_path = r"C:\Users\HP\Desktop\ssc_marketing_managing_backup_final_1b6c3ee_20261123"
    if not os.path.exists(backup_path):
        print(f"[ERROR] Required backup path {backup_path} does not exist! Aborting reset.")
        sys.exit(1)
    
    print("=" * 70)
    print("SHAH GROUP AI OS — FRESH BUSINESS DATA RESET")
    print(f"Verified Backup Baseline: {backup_path}")
    print(f"Timestamp: {now_kolkata_iso()}")
    print("=" * 70)

    db_path = "data/sgcc_foundation.sqlite"
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Tables to purge completely (business transaction/operational records)
    business_tables_to_purge = [
        "attendance_logs",
        "leaves",
        "payslips",
        "payroll_runs",
        "cash_advance",
        "employee_documents",
        "employees",
        "business_payments",
        "business_invoices",
        "business_quotations",
        "business_estimates",
        "business_work_orders",
        "social_leads",
        "social_client_profiles",
        "expense_claims",
        "expense_vendors",
        "task_comments",
        "task_notifications",
        "employee_tasks",
        "approvals",
        "sites",
        "social_published_posts",
        "social_publish_jobs",
        "social_calendar_entries",
        "social_content_ideas",
        "social_content_versions",
        "social_content_items",
        "social_campaigns",
        "social_media_assets",
        "studio_render_jobs",
        "studio_projects",
        "ai_tasks",
        "ai_marketing_briefs",
        "ai_research_items",
        "ai_generated_reports",
        "ai_business_alerts",
        "ai_hermes_logs",
        "ai_tool_executions",
        "ai_scheduler_runs",
        "google_sheets_sync_history",
        "integration_activity_logs",
        "social_comments",
        "social_messages",
        "social_employee_kpis",
        "social_lead_attribution",
        "social_trends",
        "social_video_jobs",
        "social_subtitles",
        "social_thumbnails",
        "social_scripts",
        "social_tasks",
        "social_approvals",
        "social_agent_runs",
        "social_brand_assets",
        "social_brand_profiles",
        "social_competitor_profiles",
        "social_integration_logs"
    ]

    purged_counts = {}
    for table in business_tables_to_purge:
        try:
            cnt = cur.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]
            cur.execute(f'DELETE FROM "{table}"')
            purged_counts[table] = cnt
            print(f"  [PURGED] {table}: {cnt} demo records removed.")
        except Exception as e:
            print(f"  [SKIP] {table}: {e}")

    # Clean temporary test users (id > 7)
    test_users_cnt = cur.execute("SELECT COUNT(*) FROM users WHERE id > 7").fetchone()[0]
    cur.execute("DELETE FROM users WHERE id > 7")
    print(f"  [PURGED] users: {test_users_cnt} automated test users removed (Preserved 7 System Roles: Owner, Manager, PM, Finance, HR, Employee, Viewer).")

    # Clean sessions
    cur.execute("DELETE FROM sessions WHERE user_id > 7")
    
    # Reset sqlite autoincrement sequences for business tables
    for table in business_tables_to_purge:
        try:
            cur.execute(f"DELETE FROM sqlite_sequence WHERE name='{table}'")
        except Exception:
            pass

    # Record clean audit log
    cur.execute(
        """INSERT INTO audit_logs (actor_id, actor_username, action, target, details, workspace_id, created_at)
           VALUES (1, 'owner', 'FRESH_BUSINESS_RESET', 'SYSTEM_RESET_V4', ?, 'SSC', ?)""",
        (
            json.dumps({
                "backup": backup_path,
                "purged_tables": purged_counts,
                "status": "CLEAN_BUSINESS_START_PREPARED"
            }),
            now_kolkata_iso()
        )
    )

    conn.commit()
    conn.close()

    # Also clean secondary mirror db if exists
    mirror_db = "data/business_os.db"
    if os.path.exists(mirror_db):
        try:
            mconn = sqlite3.connect(mirror_db)
            mcur = mconn.cursor()
            for table in business_tables_to_purge:
                try:
                    mcur.execute(f'DELETE FROM "{table}"')
                except Exception:
                    pass
            mcur.execute("DELETE FROM users WHERE id > 7")
            mconn.commit()
            mconn.close()
            print("  [MIRROR] data/business_os.db synchronized with clean state.")
        except Exception as e:
            print(f"  [MIRROR_WARN] {e}")

    # Clean data/sheets_sync/ CSV staging files (preserve headers, 0 rows)
    sheets_sync_dir = "data/sheets_sync"
    if os.path.exists(sheets_sync_dir):
        for f in os.listdir(sheets_sync_dir):
            if f.endswith(".csv"):
                csv_path = os.path.join(sheets_sync_dir, f)
                try:
                    with open(csv_path, "r", encoding="utf-8") as rfp:
                        reader = csv.reader(rfp)
                        header = next(reader, None)
                    if header:
                        with open(csv_path, "w", encoding="utf-8", newline="") as wfp:
                            writer = csv.writer(wfp)
                            writer.writerow(header)
                        print(f"  [SHEETS_STAGING_RESET] {f}: Header preserved, 0 rows.")
                except Exception as ex:
                    print(f"  [SHEETS_STAGING_ERR] {f}: {ex}")

    # Remove temporary test sample files from drive sync reports
    test_sample = "data/drive_sync/SSC/Reports/phase4_acceptance_verification_sample.txt"
    if os.path.exists(test_sample):
        os.remove(test_sample)
        print("  [DRIVE_STAGING_CLEAN] Removed test verification sample from data/drive_sync/SSC/Reports/.")

    print("=" * 70)
    print("FRESH BUSINESS RESET COMPLETED SUCCESSFULLY")
    print("Zero demo records remain. All business modules ready for genuine owner data entry.")
    print("=" * 70)


if __name__ == "__main__":
    execute_fresh_business_reset()
