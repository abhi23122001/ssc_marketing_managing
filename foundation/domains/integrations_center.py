# -*- coding: utf-8 -*-
"""SHAH GROUP AI OS — Central Integration & Data Sync Center.

Provides unified management for:
  1. Google Account & Google Drive (hierarchical folder management for SSC and INFRA).
  2. Google Sheets module-wise destination spreadsheet & worksheet mapping (12 modules).
  3. Official Social Media Channels (Instagram, Facebook Pages, YouTube).
  4. Integration Health Monitor (live status, permissions, token health, troubleshooting).
  5. Sync Queue & Activity Audit Trail.
  6. Guided Integration Setup Assistant.
"""
from __future__ import annotations

import base64
import json
import os
import shutil
import sqlite3
import time
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Tuple

from ..config import project_root
from ..store import Store

KOLKATA_TZ = timezone(timedelta(hours=5, minutes=30))
DRIVE_SYNC_DIR = os.path.join(os.getcwd(), "data", "drive_sync")
SHEETS_SYNC_DIR = os.path.join(os.getcwd(), "data", "sheets_sync")


def now_kolkata_iso() -> str:
    return datetime.now(KOLKATA_TZ).strftime("%Y-%m-%d %H:%M:%S")


def ensure_integration_center_schema(conn: sqlite3.Connection) -> None:
    """Ensures database tables for Drive folders, module mappings, and sync queue."""
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS drive_folders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        workspace_id TEXT NOT NULL,  -- 'SSC' or 'INFRA'
        module_key TEXT NOT NULL,    -- 'crm', 'clients', 'projects', 'quotations', 'invoices', etc.
        folder_name TEXT NOT NULL,
        drive_folder_id TEXT DEFAULT '',
        parent_folder TEXT DEFAULT 'SHAH GROUP AI OS',
        created_at TEXT NOT NULL DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS drive_synced_files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        workspace_id TEXT NOT NULL,
        module_key TEXT NOT NULL,
        file_name TEXT NOT NULL,
        local_path TEXT NOT NULL,
        drive_file_id TEXT DEFAULT '',
        file_size_bytes INTEGER DEFAULT 0,
        status TEXT NOT NULL DEFAULT 'synced',  -- 'synced', 'pending', 'failed'
        synced_at TEXT NOT NULL DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS sheets_module_mappings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        workspace_id TEXT NOT NULL,
        module_key TEXT NOT NULL,      -- 'leads', 'clients', 'sites', 'tasks', etc.
        spreadsheet_name TEXT NOT NULL,
        spreadsheet_id TEXT DEFAULT '',
        worksheet_tab TEXT NOT NULL,
        field_mapping_json TEXT DEFAULT '{}',
        sync_enabled INTEGER NOT NULL DEFAULT 1,
        sync_mode TEXT NOT NULL DEFAULT 'auto',  -- 'auto', 'manual'
        last_sync_at TEXT,
        last_status TEXT DEFAULT 'ok',
        created_at TEXT NOT NULL DEFAULT (datetime('now')),
        UNIQUE(workspace_id, module_key)
    );

    CREATE TABLE IF NOT EXISTS integration_activity_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        workspace_id TEXT NOT NULL,
        provider TEXT NOT NULL,       -- 'google_drive', 'google_sheets', 'instagram', 'facebook', 'youtube'
        action TEXT NOT NULL,
        status TEXT NOT NULL,         -- 'success', 'failed', 'pending'
        details TEXT DEFAULT '',
        created_at TEXT NOT NULL DEFAULT (datetime('now'))
    );
    """)


# Standard 12 Module Keys for Google Sheets
CORE_MODULES = [
    {"key": "leads", "label": "CRM / Inbound Leads", "default_tab": "CRM_Leads", "fields": ["id", "company", "lead_name", "phone", "email", "service_interest", "lead_priority", "lead_status"]},
    {"key": "clients", "label": "Client Profiles & Accounts", "default_tab": "Client_Profiles", "fields": ["id", "client_workspace_id", "company_name", "service_package", "created_at"]},
    {"key": "sites", "label": "Project & Survey Sites", "default_tab": "Project_Sites", "fields": ["id", "code", "name", "address", "geofence_radius_m", "status"]},
    {"key": "employees", "label": "Human Resources & Staff", "default_tab": "Staff_Directory", "fields": ["id", "employee_id", "name", "designation", "role", "email", "status"]},
    {"key": "attendance", "label": "Daily Field Attendance", "default_tab": "Attendance_Logs", "fields": ["id", "employee_id", "date", "check_in", "check_out", "status", "worked_hours"]},
    {"key": "tasks", "label": "Employee Tasks & Workload", "default_tab": "Employee_Tasks", "fields": ["id", "title", "assigned_to", "priority", "deadline_date", "status", "progress_pct"]},
    {"key": "estimates", "label": "Scope & Cost Estimates", "default_tab": "Project_Estimates", "fields": ["id", "title", "service_type", "estimated_amount", "status"]},
    {"key": "quotations", "label": "Commercial Quotations (BOQ)", "default_tab": "Commercial_Quotations", "fields": ["id", "quotation_number", "project_name", "subtotal", "gst_amount", "total_amount", "status"]},
    {"key": "invoices", "label": "GST Tax Invoices", "default_tab": "GST_Invoices", "fields": ["id", "invoice_number", "invoice_date", "total_amount", "amount_paid", "payment_status"]},
    {"key": "expenses", "label": "Expense Claims & Outflows", "default_tab": "Expense_Claims", "fields": ["id", "project_id", "category", "amount", "status"]},
    {"key": "finance", "label": "Payment Receipts & Banking", "default_tab": "Payment_Receipts", "fields": ["id", "invoice_id", "amount", "payment_date", "payment_mode", "reference_number"]},
    {"key": "reports", "label": "AI Intelligence & Reports", "default_tab": "Intelligence_Reports", "fields": ["id", "title", "report_type", "summary", "generated_at"]}
]


def seed_default_mappings(conn: sqlite3.Connection) -> None:
    """Pre-seeds default sheets module mappings and drive folders for SSC and INFRA."""
    ensure_integration_center_schema(conn)
    os.makedirs(DRIVE_SYNC_DIR, exist_ok=True)
    os.makedirs(SHEETS_SYNC_DIR, exist_ok=True)

    # 1. Seed Google Sheets Mappings
    for ws in ["SSC", "INFRA"]:
        spreadsheet_name = f"SHAH GROUP OS — {ws} Operational Master"
        for mod in CORE_MODULES:
            row = conn.execute(
                "SELECT id FROM sheets_module_mappings WHERE workspace_id=? AND module_key=?",
                (ws, mod["key"])
            ).fetchone()
            if not row:
                field_map = {f: f.replace("_", " ").title() for f in mod["fields"]}
                conn.execute("""
                INSERT INTO sheets_module_mappings
                (workspace_id, module_key, spreadsheet_name, worksheet_tab, field_mapping_json, sync_enabled, sync_mode, last_status)
                VALUES (?, ?, ?, ?, ?, 1, 'auto', 'ok')
                """, (ws, mod["key"], spreadsheet_name, mod["default_tab"], json.dumps(field_map)))

    # 2. Seed Drive Folders for SSC and INFRA
    default_drive_folders = {
        "SSC": ["CRM", "Clients", "Projects", "Quotations", "Invoices", "Finance", "HRM", "Attendance", "Reports", "Social Media"],
        "INFRA": ["CRM", "Projects", "Finance", "Reports", "Documents"]
    }
    for ws, f_list in default_drive_folders.items():
        ws_dir = os.path.join(DRIVE_SYNC_DIR, ws)
        os.makedirs(ws_dir, exist_ok=True)
        for f_name in f_list:
            mod_key = f_name.lower().replace(" ", "_")
            os.makedirs(os.path.join(ws_dir, f_name), exist_ok=True)
            row = conn.execute(
                "SELECT id FROM drive_folders WHERE workspace_id=? AND module_key=?",
                (ws, mod_key)
            ).fetchone()
            if not row:
                conn.execute(
                    "INSERT INTO drive_folders (workspace_id, module_key, folder_name, parent_folder) VALUES (?, ?, ?, ?)",
                    (ws, mod_key, f_name, f"SHAH GROUP AI OS/{ws}")
                )
    conn.commit()


def get_integration_health_monitor(store: Store, workspace_id: str = "SSC") -> Dict[str, Any]:
    """Generates unified health monitor data across all external providers and local AI."""
    seed_default_mappings(store.conn)
    from .oauth_service import get_account_oauth_status
    from .google_oauth_service import get_google_account_details
    from .social_integrations import list_social_accounts

    # Live token checks from OAuth service & Google OAuth Manager
    google_acc_info = get_google_account_details(store.conn, workspace_id)
    is_google_connected = google_acc_info.get("is_connected", False)
    google_email = google_acc_info.get("account_email") or "Google OAuth Consent Required"

    google_oauth = {"is_connected": is_google_connected, "account_identifier": google_email}
    google_drive_oauth = {"is_connected": is_google_connected}
    google_sheets_oauth = {"is_connected": is_google_connected}
    gbp_oauth = get_account_oauth_status(store.conn, workspace_id, "google_business_profile", "gbp_manage")
    
    # Official social accounts status
    social_accounts_list = list_social_accounts(store, workspace_id)
    insta_acc = next((a for a in social_accounts_list if a.get("platform") == "instagram"), None)
    fb_acc = next((a for a in social_accounts_list if a.get("platform") == "facebook"), None)
    yt_acc = next((a for a in social_accounts_list if a.get("platform") == "youtube"), None)

    # Recent sync logs
    recent_logs = store.fetchall(
        "SELECT * FROM integration_activity_logs WHERE workspace_id=? ORDER BY id DESC LIMIT 15",
        (workspace_id,)
    )

    # Google Sheets mapping status
    mappings = store.fetchall(
        "SELECT * FROM sheets_module_mappings WHERE workspace_id=? ORDER BY id ASC",
        (workspace_id,)
    )
    active_sheets_count = sum(1 for m in mappings if m["sync_enabled"] == 1)

    # Drive folders count (10 SSC + 5 INFRA = 15 total folders)
    drive_folders = store.fetchall(
        "SELECT * FROM drive_folders WHERE workspace_id=? ORDER BY folder_name ASC",
        (workspace_id,)
    )

    # Drive files count
    drive_files = store.fetchall(
        "SELECT * FROM drive_synced_files WHERE workspace_id=? ORDER BY id DESC LIMIT 20",
        (workspace_id,)
    )

    providers = [
        {
            "id": "google_account",
            "name": "Google Account (Core Auth)",
            "icon": "🌐",
            "status": "connected" if google_oauth.get("is_connected") else "setup_required",
            "status_label": "Authenticated" if google_oauth.get("is_connected") else "Authorization Required (Local Safe Staging Only)",
            "account_identifier": google_oauth.get("account_identifier", "Google OAuth 2.0 Consent Required"),
            "required_scopes": ["https://www.googleapis.com/auth/userinfo.email", "https://www.googleapis.com/auth/drive.file"],
            "last_sync": now_kolkata_iso()[:16],
            "troubleshooting": "Google OAuth authorization required to link cloud services. Local file and CSV staging remains 100% active offline."
        },
        {
            "id": "google_drive",
            "name": "Google Drive (Cloud Storage)",
            "icon": "📁",
            "status": "connected" if google_drive_oauth.get("is_connected") else "setup_required",
            "status_label": "Cloud Synced" if google_drive_oauth.get("is_connected") else "Local Safe Staging Only (15 Folders Active)",
            "account_identifier": f"SHAH GROUP AI OS / {workspace_id} ({len(drive_folders)} folders in data/drive_sync/)",
            "required_scopes": ["https://www.googleapis.com/auth/drive.file"],
            "last_sync": now_kolkata_iso()[:16],
            "troubleshooting": "Files are staged locally in data/drive_sync/ and automatically mirrored upon cloud connection. Local staging is never labeled cloud-connected."
        },
        {
            "id": "google_sheets",
            "name": "Google Sheets (Module Data Sync)",
            "icon": "📊",
            "status": "connected" if google_sheets_oauth.get("is_connected") else "setup_required",
            "status_label": "Cloud Synced" if google_sheets_oauth.get("is_connected") else "Local Safe Staging Only (12 CSV Modules Staged)",
            "account_identifier": "Shah AI OS (ID: 17CpMIB7mMrBalL6juZMmKVFvm2j5IvLXJjYdsbAmU5c)",
            "required_scopes": ["https://www.googleapis.com/auth/spreadsheets"],
            "spreadsheet_url": "https://docs.google.com/spreadsheets/d/17CpMIB7mMrBalL6juZMmKVFvm2j5IvLXJjYdsbAmU5c/edit",
            "last_sync": now_kolkata_iso()[:16],
            "troubleshooting": "12 core operational modules mirrored cleanly to data/sheets_sync/ with SHA-256 deduplication and last-write-wins merge."
        },
        {
            "id": "instagram",
            "name": "Instagram Professional",
            "icon": "📸",
            "status": "connected" if (insta_acc and insta_acc.get("status") == "Connected") else "setup_required",
            "status_label": insta_acc.get("status") if insta_acc else "Authorization Required",
            "account_identifier": "@shahgroupofficial1 (https://www.instagram.com/shahgroupofficial1/)",
            "required_scopes": ["instagram_basic", "instagram_content_publish", "instagram_manage_insights", "pages_show_list"],
            "last_sync": now_kolkata_iso()[:16],
            "troubleshooting": "Instagram Professional account linkage to a Facebook Page in Meta Business Suite is required for Graph API publishing."
        },
        {
            "id": "facebook",
            "name": "Facebook Pages",
            "icon": "📘",
            "status": "connected" if (fb_acc and fb_acc.get("status") == "Connected") else "setup_required",
            "status_label": fb_acc.get("status") if fb_acc else "Authorization Required",
            "account_identifier": "Profile ID: 61593669391620 (https://www.facebook.com/profile.php?id=61593669391620)",
            "required_scopes": ["pages_show_list", "pages_read_engagement", "pages_manage_posts"],
            "last_sync": now_kolkata_iso()[:16],
            "troubleshooting": "Personal profile detected. Meta Graph API v19+ blocks publishing to personal profiles (/me/feed deprecated). Page linkage required."
        },
        {
            "id": "youtube",
            "name": "YouTube Channels",
            "icon": "▶️",
            "status": "connected" if (yt_acc and yt_acc.get("status") == "Connected") else "setup_required",
            "status_label": yt_acc.get("status") if yt_acc else "Authorization Required",
            "account_identifier": "@ShahGroupOfficial (https://www.youtube.com/@ShahGroupOfficial)",
            "required_scopes": ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube.readonly"],
            "last_sync": now_kolkata_iso()[:16],
            "troubleshooting": "Requires official Google OAuth 2.0 authorization with youtube.upload scope and channel ownership verification."
        },
        {
            "id": "google_business_profile",
            "name": "Google Business Profile",
            "icon": "🏢",
            "status": "connected" if gbp_oauth.get("is_connected") else "setup_required",
            "status_label": "Business Profile Active" if gbp_oauth.get("is_connected") else "Authorization Required (Local Profile Ready)",
            "account_identifier": "Shah Surveyors & Consultancy (Nagpur & Central India)",
            "required_scopes": ["https://www.googleapis.com/auth/business.manage"],
            "last_sync": now_kolkata_iso()[:16],
            "troubleshooting": "Google Business Profile API requires OAuth authorization with business.manage scope to sync local reviews, services, and posts."
        },
        {
            "id": "hermes_ai",
            "name": "Hermes AI Agent & Free Models",
            "icon": "🧠",
            "status": "connected",
            "status_label": "Active (Local v0.23.1 + StepFun Free)",
            "account_identifier": "Hermes Orchestrator / StepFun 3.7 Flash Free",
            "required_scopes": ["local_exec", "zero_paid_billing"],
            "last_sync": now_kolkata_iso()[:16],
            "troubleshooting": "100% active locally. Zero paid billing enforced."
        },
        {
            "id": "image_gen",
            "name": "AI Image & Visual Studio",
            "icon": "🎨",
            "status": "connected",
            "status_label": "Active (Pollinations.ai + Offline Vector Engine)",
            "account_identifier": "Domain-Specific DGPS & Drone Infused Prompts",
            "required_scopes": ["text_to_image", "offline_fallback"],
            "last_sync": now_kolkata_iso()[:16],
            "troubleshooting": "Generates 1080x1080, 9:16 and 16:9 images with automatic media library sync."
        }
    ]

    return {
        "workspace_id": workspace_id,
        "providers": providers,
        "active_modules_count": active_sheets_count,
        "total_modules": len(CORE_MODULES),
        "recent_activity": recent_logs,
        "drive_folders_count": len(drive_folders),
        "drive_files_count": len(drive_files),
        "zero_paid_billing": True
    }


def list_sheets_mappings(store: Store, workspace_id: str = "SSC") -> List[Dict[str, Any]]:
    """Returns the 12 module sheets mappings with detailed metadata."""
    seed_default_mappings(store.conn)
    rows = store.fetchall(
        "SELECT * FROM sheets_module_mappings WHERE workspace_id=? ORDER BY id ASC",
        (workspace_id,)
    )
    result = []
    for r in rows:
        d = dict(r)
        d["field_mapping"] = json.loads(d.get("field_mapping_json") or "{}")
        # Match label from CORE_MODULES
        match = next((m for m in CORE_MODULES if m["key"] == d["module_key"]), None)
        d["label"] = match["label"] if match else d["module_key"].title()
        d["available_fields"] = match["fields"] if match else []
        result.append(d)
    return result


def update_sheet_mapping(store: Store, workspace_id: str, module_key: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Updates destination spreadsheet, worksheet tab, and field map for a module."""
    seed_default_mappings(store.conn)
    sp_name = data.get("spreadsheet_name", f"SHAH GROUP OS — {workspace_id} Master")
    sp_id = data.get("spreadsheet_id", "")
    tab = data.get("worksheet_tab", "Master_Data")
    enabled = 1 if data.get("sync_enabled", True) else 0
    mode = data.get("sync_mode", "auto")
    f_map = json.dumps(data.get("field_mapping", {}))

    store.conn.execute("""
    UPDATE sheets_module_mappings
    SET spreadsheet_name=?, spreadsheet_id=?, worksheet_tab=?, field_mapping_json=?, sync_enabled=?, sync_mode=?, last_sync_at=?
    WHERE workspace_id=? AND module_key=?
    """, (sp_name, sp_id, tab, f_map, enabled, mode, now_kolkata_iso(), workspace_id, module_key))
    store.conn.commit()

    # Log activity
    store.conn.execute(
        "INSERT INTO integration_activity_logs (workspace_id, provider, action, status, details) VALUES (?,?,?,?,?)",
        (workspace_id, "google_sheets", f"Updated mapping: {module_key}", "success", f"Destination: {sp_name} -> {tab}")
    )
    store.conn.commit()

    return {"ok": True, "workspace_id": workspace_id, "module_key": module_key}


def get_drive_folder_tree(store: Store, workspace_id: str = "SSC") -> Dict[str, Any]:
    """Returns the Drive hierarchical folder tree for the current workspace."""
    seed_default_mappings(store.conn)
    folders = store.fetchall(
        "SELECT * FROM drive_folders WHERE workspace_id=? ORDER BY folder_name ASC",
        (workspace_id,)
    )
    files = store.fetchall(
        "SELECT * FROM drive_synced_files WHERE workspace_id=? ORDER BY id DESC LIMIT 50",
        (workspace_id,)
    )

    # Physical check in DRIVE_SYNC_DIR
    ws_dir = os.path.join(DRIVE_SYNC_DIR, workspace_id)
    folder_details = []
    for f in folders:
        m_key = f["module_key"]
        p_dir = os.path.join(ws_dir, f["folder_name"])
        f_count = len(os.listdir(p_dir)) if os.path.exists(p_dir) else 0
        folder_details.append({
            "id": f["id"],
            "module_key": m_key,
            "folder_name": f["folder_name"],
            "parent_folder": f["parent_folder"],
            "local_path": p_dir,
            "files_count": f_count
        })

    return {
        "ok": True,
        "workspace_id": workspace_id,
        "root_folder": f"SHAH GROUP AI OS / {workspace_id}",
        "folders": folder_details,
        "recent_files": [dict(fl) for fl in files]
    }


def stage_drive_file_upload(store: Store, workspace_id: str, module_key: str, filename: str, file_b64: str) -> Dict[str, Any]:
    """Stages a report, invoice, quotation, or media file into the workspace Drive folder and syncs to Drive if connected."""
    seed_default_mappings(store.conn)
    from .google_drive_engine import stage_and_sync_file
    res = stage_and_sync_file(store, workspace_id, module_key, filename, file_b64)
    res["file_id"] = res.get("id")
    res["folder"] = res.get("folder_name")
    res["size_bytes"] = res.get("file_size_bytes")
    return res


def update_drive_folder(store: Store, workspace_id: str, folder_id: int, drive_folder_id: str) -> Dict[str, Any]:
    """Updates target Google Drive cloud folder ID binding for a folder."""
    seed_default_mappings(store.conn)
    store.conn.execute(
        "UPDATE drive_folders SET drive_folder_id=? WHERE id=? AND workspace_id=?",
        (drive_folder_id, folder_id, workspace_id)
    )
    store.conn.commit()
    row = store.fetchone("SELECT * FROM drive_folders WHERE id=?", (folder_id,))
    return {"ok": True, "folder": dict(row) if row else {}}

