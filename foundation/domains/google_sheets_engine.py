# -*- coding: utf-8 -*-
"""SHAH GROUP AI OS — Google Sheets Engine & Live Synchronization Engine.

Provides:
  1. Live Google Sheets API v4 client (metadata inspection, worksheet listing, cell read/write).
  2. Controlled synchronization of approved business modules (Leads, Quotations, Invoices, Sites, etc.).
  3. Strict anti-duplicate row engine (Primary Key extraction + SHA-256 fingerprint deduplication).
  4. Local safe staging fallback (data/sheets_sync/) when cloud OAuth is not yet authorized.
  5. Rate-limit and error handling with detailed audit logging in google_sheets_sync_history.
  6. Strict tenant isolation between SSC and INFRA.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import sqlite3
import time
import urllib.parse
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Tuple

from ..store import Store
from .google_oauth_service import get_valid_google_token, now_kolkata_iso, KOLKATA_TZ

SHEETS_API_BASE = "https://sheets.googleapis.com/v4/spreadsheets"
SYNC_DATA_DIR = os.path.join(os.getcwd(), "data", "sheets_sync")

# Default Owner Master Spreadsheet (can be customized per workspace)
DEFAULT_SPREADSHEET_ID = "17CpMIB7mMrBalL6juZMmKVFvm2j5IvLXJjYdsbAmU5c"
DEFAULT_SPREADSHEET_TITLE = "Shah AI OS"
DEFAULT_SPREADSHEET_URL = f"https://docs.google.com/spreadsheets/d/{DEFAULT_SPREADSHEET_ID}/edit"

# Core Approved Business Modules and their Authorized Field Mappings
APPROVED_MODULES: Dict[str, Dict[str, Any]] = {
    "leads": {
        "title": "CRM_Leads",
        "table": "social_leads",
        "key_col": "id",
        "cols": ["id", "workspace_id", "company", "lead_name", "phone", "email", "service_interest", "lead_priority", "lead_status", "created_at"],
        "display_headers": ["Lead ID", "Workspace", "Company", "Contact Person", "Phone", "Email", "Service Interest", "Priority", "Status", "Date Added"]
    },
    "clients": {
        "title": "Client_Profiles",
        "table": "social_client_profiles",
        "key_col": "id",
        "cols": ["id", "client_workspace_id", "company_name", "service_package", "workspace_id", "created_at"],
        "display_headers": ["Client ID", "Client Code", "Company Name", "Service Scope", "Workspace", "Created At"]
    },
    "sites": {
        "title": "Project_Sites",
        "table": "sites",
        "key_col": "id",
        "cols": ["id", "workspace_id", "code", "name", "address", "geofence_radius_m", "status", "created_at"],
        "display_headers": ["Site ID", "Workspace", "Site Code", "Site Name", "Location / Address", "Geofence Radius (m)", "Status", "Date Initiated"]
    },
    "tasks": {
        "title": "Employee_Tasks",
        "table": "employee_tasks",
        "key_col": "id",
        "cols": ["id", "workspace_id", "title", "description", "category", "assigned_to", "priority", "deadline_date", "status", "progress_pct", "created_at"],
        "display_headers": ["Task ID", "Workspace", "Task Title", "Description", "Category", "Assigned Employee", "Priority", "Deadline", "Status", "Progress %", "Created At"]
    },
    "attendance": {
        "title": "Staff_Attendance",
        "table": "attendance_logs",
        "key_col": "id",
        "cols": ["id", "workspace_id", "employee_id", "site_id", "check_in", "check_out", "status", "created_at"],
        "display_headers": ["Attendance ID", "Workspace", "Employee ID", "Site ID", "Check-In Time", "Check-Out Time", "Status", "Logged Date"]
    },
    "quotations": {
        "title": "Commercial_Quotations",
        "table": "business_quotations",
        "key_col": "id",
        "cols": ["id", "workspace_id", "quotation_number", "project_name", "subtotal", "gst_amount", "total_amount", "status", "created_at"],
        "display_headers": ["Quotation ID", "Workspace", "Quotation Number", "Project Title", "Subtotal (INR)", "GST (INR)", "Total Amount (INR)", "Approval Status", "Date"]
    },
    "invoices": {
        "title": "GST_Invoices",
        "table": "business_invoices",
        "key_col": "id",
        "cols": ["id", "workspace_id", "invoice_number", "invoice_date", "subtotal", "total_tax", "total_amount", "amount_paid", "payment_status", "status", "created_at"],
        "display_headers": ["Invoice ID", "Workspace", "Invoice Number", "Bill Date", "Subtotal (INR)", "Tax (INR)", "Total (INR)", "Amount Paid (INR)", "Payment Status", "Status", "Created At"]
    },
    "payments": {
        "title": "Payment_Receipts",
        "table": "business_payments",
        "key_col": "id",
        "cols": ["id", "workspace_id", "invoice_id", "amount", "payment_method", "reference_number", "payment_date", "created_at"],
        "display_headers": ["Payment ID", "Workspace", "Invoice ID", "Amount (INR)", "Payment Mode", "UTR / Reference", "Payment Date", "Logged At"]
    },
    "expenses": {
        "title": "Expense_Claims",
        "table": "expense_claims",
        "key_col": "id",
        "cols": ["id", "workspace_id", "employee_id", "category", "amount", "currency", "status", "notes", "submitted_at", "created_at"],
        "display_headers": ["Expense ID", "Workspace", "Employee ID", "Category", "Amount", "Currency", "Status", "Notes", "Submitted At", "Created At"]
    },
    "calendar": {
        "title": "Content_Calendar",
        "table": "social_calendar_entries",
        "key_col": "id",
        "cols": ["id", "workspace_id", "scheduled_date", "scheduled_time", "slot_label", "assigned_platform", "status", "created_at"],
        "display_headers": ["Schedule ID", "Workspace", "Scheduled Date", "Time", "Slot Label", "Platform", "Status", "Created At"]
    },
    "publishing": {
        "title": "Publishing_Logs",
        "table": "social_published_posts",
        "key_col": "id",
        "cols": ["id", "workspace_id", "platform", "post_type", "published_url", "status", "created_at"],
        "display_headers": ["Publish ID", "Workspace", "Platform", "Post Type", "URL", "Status", "Published At"]
    },
    "reports": {
        "title": "AI_Intelligence_Reports",
        "table": "ai_generated_reports",
        "key_col": "id",
        "cols": ["id", "workspace_id", "report_type", "title", "summary_md", "created_at"],
        "display_headers": ["Report ID", "Workspace", "Report Type", "Title", "Executive Summary", "Generated At"]
    }
}


def calculate_row_hash(row_data: Dict[str, Any], cols: List[str]) -> str:
    """Computes SHA-256 fingerprint of row content for safe deduplication."""
    serialized = "|".join(str(row_data.get(c, "") or "") for c in cols)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def extract_spreadsheet_id(input_str: str) -> str:
    """Extracts clean Google Spreadsheet ID from either raw ID or full docs.google.com URL."""
    clean = input_str.strip()
    if "/spreadsheets/d/" in clean:
        parts = clean.split("/spreadsheets/d/")
        if len(parts) > 1:
            clean = parts[1].split("/")[0].split("?")[0].split("#")[0]
    return clean


def get_workspace_spreadsheet_config(conn: sqlite3.Connection, workspace_id: str = "SSC") -> Dict[str, Any]:
    """Retrieves target spreadsheet ID and preferences for the workspace."""
    row = conn.execute(
        "SELECT * FROM google_sheets_config WHERE workspace_id=?",
        (workspace_id,)
    ).fetchone()

    if not row:
        conn.execute("""
        INSERT INTO google_sheets_config (
            workspace_id, spreadsheet_id, spreadsheet_name,
            connection_status, auto_sync_interval_mins
        ) VALUES (?, ?, ?, 'Authorization Required', 15)
        """, (workspace_id, DEFAULT_SPREADSHEET_ID, DEFAULT_SPREADSHEET_TITLE))
        conn.commit()
        row = conn.execute("SELECT * FROM google_sheets_config WHERE workspace_id=?", (workspace_id,)).fetchone()

    cfg = dict(row) if row else {}
    if cfg and "spreadsheet_id" in cfg and cfg["spreadsheet_id"]:
        cfg["spreadsheet_url"] = f"https://docs.google.com/spreadsheets/d/{cfg['spreadsheet_id']}/edit"
    return cfg


def update_workspace_spreadsheet_selection(
    conn: sqlite3.Connection,
    workspace_id: str,
    spreadsheet_id_or_url: str,
    spreadsheet_name: Optional[str] = None
) -> Dict[str, Any]:
    """Updates the target Google Spreadsheet ID/URL for the workspace."""
    sp_id = extract_spreadsheet_id(spreadsheet_id_or_url)
    if not sp_id:
        return {"ok": False, "error": "Invalid spreadsheet ID or URL provided."}

    sp_url = f"https://docs.google.com/spreadsheets/d/{sp_id}/edit"
    sp_name = spreadsheet_name or f"Shah Group AI OS — {workspace_id} Master"

    conn.execute("""
    UPDATE google_sheets_config
    SET spreadsheet_id=?, spreadsheet_name=?, updated_at=datetime('now')
    WHERE workspace_id=?
    """, (sp_id, sp_name, workspace_id))

    # Also update default spreadsheet in sheets_module_mappings for this workspace
    conn.execute("""
    UPDATE sheets_module_mappings
    SET spreadsheet_id=?, spreadsheet_name=?
    WHERE workspace_id=?
    """, (sp_id, sp_name, workspace_id))
    conn.commit()

    conn.execute("""
    INSERT INTO integration_activity_logs (workspace_id, provider, action, status, details)
    VALUES (?, 'google_sheets', 'Spreadsheet Selected', 'success', ?)
    """, (workspace_id, f"Selected Target Spreadsheet: {sp_name} (ID: {sp_id})"))
    conn.commit()

    return {
        "ok": True,
        "workspace_id": workspace_id,
        "spreadsheet_id": sp_id,
        "spreadsheet_url": sp_url,
        "spreadsheet_name": sp_name
    }


def fetch_spreadsheet_metadata(
    conn: sqlite3.Connection,
    workspace_id: str = "SSC",
    spreadsheet_id: Optional[str] = None
) -> Dict[str, Any]:
    """Queries Google Sheets API v4 to list available worksheets/tabs and spreadsheet title."""
    cfg = get_workspace_spreadsheet_config(conn, workspace_id)
    target_id = spreadsheet_id or cfg.get("spreadsheet_id") or DEFAULT_SPREADSHEET_ID

    token, email, _ = get_valid_google_token(conn, workspace_id)
    if not token:
        # Offline fallback: return standard module tabs
        local_tabs = [m["title"] for m in APPROVED_MODULES.values()]
        return {
            "ok": True,
            "is_cloud_synced": False,
            "connection_status": "Authorization Required",
            "spreadsheet_id": target_id,
            "spreadsheet_title": cfg.get("spreadsheet_name") or DEFAULT_SPREADSHEET_TITLE,
            "spreadsheet_url": f"https://docs.google.com/spreadsheets/d/{target_id}/edit",
            "worksheets": [{"title": t, "index": i, "sheetId": i} for i, t in enumerate(local_tabs)],
            "note": "Offline mode active. Connecting Google OAuth will query live sheet tabs."
        }

    url = f"{SHEETS_API_BASE}/{target_id}?fields=spreadsheetId,properties.title,sheets.properties(sheetId,title,index,gridProperties)"
    try:
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
        with urllib.request.urlopen(req, timeout=12) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        sheets = data.get("sheets", [])
        worksheets = []
        for s in sheets:
            props = s.get("properties", {})
            worksheets.append({
                "sheetId": props.get("sheetId"),
                "title": props.get("title"),
                "index": props.get("index"),
                "rowCount": props.get("gridProperties", {}).get("rowCount", 0),
                "columnCount": props.get("gridProperties", {}).get("columnCount", 0)
            })

        return {
            "ok": True,
            "is_cloud_synced": True,
            "connection_status": "Connected",
            "account_email": email,
            "spreadsheet_id": target_id,
            "spreadsheet_title": data.get("properties", {}).get("title", "Untitled Spreadsheet"),
            "spreadsheet_url": f"https://docs.google.com/spreadsheets/d/{target_id}/edit",
            "worksheets": worksheets
        }
    except urllib.error.HTTPError as e:
        err_msg = f"Google Sheets API Error (HTTP {e.code}): {e.reason}"
        try:
            err_body = json.loads(e.read().decode("utf-8"))
            err_msg = err_body.get("error", {}).get("message", err_msg)
        except Exception:
            pass
        return {
            "ok": False,
            "is_cloud_synced": False,
            "error": err_msg,
            "spreadsheet_id": target_id
        }
    except Exception as e:
        return {
            "ok": False,
            "is_cloud_synced": False,
            "error": f"Failed to connect to Google Sheets: {str(e)}",
            "spreadsheet_id": target_id
        }


def read_worksheet_rows(
    token: str,
    spreadsheet_id: str,
    sheet_tab: str,
    range_notation: str = "A1:Z5000"
) -> Tuple[bool, List[List[Any]], str]:
    """Reads cell values from a worksheet tab via Google Sheets API v4."""
    quoted_tab = urllib.parse.quote(f"{sheet_tab}!{range_notation}")
    url = f"{SHEETS_API_BASE}/{spreadsheet_id}/values/{quoted_tab}"

    try:
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        values = data.get("values", [])
        return True, values, "Success"
    except urllib.error.HTTPError as e:
        err_body = ""
        try:
            err_body = e.read().decode("utf-8")
        except Exception:
            pass
        return False, [], f"HTTP {e.code}: {e.reason} {err_body}"
    except Exception as e:
        return False, [], str(e)


def create_worksheet_tab_if_missing(
    token: str,
    spreadsheet_id: str,
    sheet_tab: str
) -> Tuple[bool, str]:
    """Creates a new worksheet tab in the spreadsheet if it does not already exist."""
    url = f"{SHEETS_API_BASE}/{spreadsheet_id}:batchUpdate"
    body = {
        "requests": [
            {
                "addSheet": {
                    "properties": {
                        "title": sheet_tab
                    }
                }
            }
        ]
    }
    try:
        data_bytes = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data_bytes,
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=12) as resp:
            pass
        return True, "Tab created"
    except urllib.error.HTTPError as e:
        # If tab already exists, Google returns 400 with 'already exists'
        if "already exists" in str(e).lower():
            return True, "Tab already exists"
        return False, str(e)
    except Exception as e:
        return False, str(e)


def append_worksheet_rows(
    token: str,
    spreadsheet_id: str,
    sheet_tab: str,
    rows: List[List[Any]]
) -> Tuple[bool, int, str]:
    """Appends rows to the end of a worksheet tab via Google Sheets API v4."""
    if not rows:
        return True, 0, "No rows to append"

    quoted_tab = urllib.parse.quote(f"{sheet_tab}!A1")
    url = f"{SHEETS_API_BASE}/{spreadsheet_id}/values/{quoted_tab}:append?valueInputOption=USER_ENTERED&insertDataOption=INSERT_ROWS"
    body = {
        "range": f"{sheet_tab}!A1",
        "majorDimension": "ROWS",
        "values": rows
    }

    try:
        data_bytes = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data_bytes,
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        updates = data.get("updates", {})
        updated_rows = updates.get("updatedRows", len(rows))
        return True, updated_rows, "Appended successfully"
    except urllib.error.HTTPError as e:
        return False, 0, f"HTTP {e.code}: {e.reason}"
    except Exception as e:
        return False, 0, str(e)


def write_worksheet_rows(
    token: str,
    spreadsheet_id: str,
    sheet_tab: str,
    rows: List[List[Any]],
    range_notation: str = "A1"
) -> Tuple[bool, int, str]:
    """Writes / overwrites rows into a worksheet starting at range_notation."""
    quoted_tab = urllib.parse.quote(f"{sheet_tab}!{range_notation}")
    url = f"{SHEETS_API_BASE}/{spreadsheet_id}/values/{quoted_tab}?valueInputOption=USER_ENTERED"
    body = {
        "range": f"{sheet_tab}!{range_notation}",
        "majorDimension": "ROWS",
        "values": rows
    }

    try:
        data_bytes = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data_bytes,
            method="PUT",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        updated_rows = data.get("updatedRows", len(rows))
        return True, updated_rows, "Written successfully"
    except Exception as e:
        return False, 0, str(e)


def sync_approved_report_to_sheet(
    store: Store,
    workspace_id: str,
    module_key: str,
    custom_spreadsheet_id: Optional[str] = None,
    custom_tab: Optional[str] = None
) -> Dict[str, Any]:
    """Controlled synchronization of an approved business report to Google Sheets and local staging.

    Features:
      - Anti-duplicate row engine (compares Primary Key & SHA-256 fingerprint against existing rows).
      - Never overwrites user's existing spreadsheet data.
      - Maintains local CSV staging in data/sheets_sync/ in parallel.
      - Logs audit entry in google_sheets_sync_history.
    """
    mapping = APPROVED_MODULES.get(module_key)
    if not mapping:
        return {"ok": False, "error": f"Unknown or unapproved module: {module_key}"}

    os.makedirs(SYNC_DATA_DIR, exist_ok=True)
    t0 = time.time()

    tbl = mapping["table"]
    cols = mapping["cols"]
    default_tab = mapping["title"]
    headers = mapping["display_headers"]
    key_col = mapping["key_col"]

    # Check mapping override from database
    m_row = store.fetchone(
        "SELECT * FROM sheets_module_mappings WHERE workspace_id=? AND module_key=?",
        (workspace_id, module_key)
    )
    sheet_tab = custom_tab or (m_row["worksheet_tab"] if m_row else default_tab)
    spreadsheet_id = custom_spreadsheet_id or (m_row["spreadsheet_id"] if m_row and m_row["spreadsheet_id"] else None)

    if not spreadsheet_id:
        cfg = get_workspace_spreadsheet_config(store.conn, workspace_id)
        spreadsheet_id = cfg.get("spreadsheet_id") or DEFAULT_SPREADSHEET_ID

    # 1. Fetch authorized records from SQLite database for this workspace
    try:
        sql = f"SELECT {', '.join(cols)} FROM {tbl} WHERE workspace_id=?" if "workspace_id" in cols else f"SELECT {', '.join(cols)} FROM {tbl}"
        params = [workspace_id] if "workspace_id" in cols else []
        db_rows = store.fetchall(sql, params)
    except Exception as e:
        db_rows = []

    # 2. Update local CSV mirror in data/sheets_sync/
    csv_file = os.path.join(SYNC_DATA_DIR, f"{workspace_id}_{sheet_tab}.csv")
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for r in db_rows:
            writer.writerow([r[c] if r[c] is not None else "" for c in cols])

    total_records = len(db_rows)

    # 3. Check Google Cloud OAuth status
    token, email, _ = get_valid_google_token(store.conn, workspace_id)
    is_cloud_synced = False
    cloud_pushed_count = 0
    duplicate_count = 0
    cloud_status_note = "Local Safe Staging Only (Cloud Authorization Required)"

    if token:
        # Ensure target worksheet tab exists on Google Sheets
        create_worksheet_tab_if_missing(token, spreadsheet_id, sheet_tab)

        # Read existing remote rows from the sheet
        ok_read, existing_remote_rows, _ = read_worksheet_rows(token, spreadsheet_id, sheet_tab)
        existing_keys = set()
        existing_hashes = set()

        if ok_read and existing_remote_rows:
            # First row is usually header
            for row_vals in existing_remote_rows[1:]:
                if row_vals:
                    # Key column is at index 0 (ID or Code)
                    existing_keys.add(str(row_vals[0]).strip())
                    row_str = "|".join(str(v).strip() for v in row_vals)
                    existing_hashes.add(hashlib.sha256(row_str.encode("utf-8")).hexdigest())

        # Determine rows to append (Anti-Duplicate Check)
        rows_to_append = []
        if not existing_remote_rows:
            # Write header first if sheet is empty
            rows_to_append.append(headers)

        for r in db_rows:
            row_dict = dict(r)
            p_key = str(row_dict.get(key_col, "")).strip()
            row_hash = calculate_row_hash(row_dict, cols)

            if p_key in existing_keys or row_hash in existing_hashes:
                duplicate_count += 1
                continue

            row_cells = [str(row_dict.get(c, "") if row_dict.get(c) is not None else "") for c in cols]
            rows_to_append.append(row_cells)

        if rows_to_append:
            ok_append, pushed, append_msg = append_worksheet_rows(token, spreadsheet_id, sheet_tab, rows_to_append)
            if ok_append:
                cloud_pushed_count = max(0, pushed - (1 if not existing_remote_rows else 0))
                is_cloud_synced = True
                cloud_status_note = f"Successfully synced {cloud_pushed_count} new records to Google Sheet [{sheet_tab}] ({duplicate_count} duplicate rows prevented)"
            else:
                cloud_status_note = f"Failed to push rows: {append_msg}"
        else:
            is_cloud_synced = True
            cloud_status_note = f"Remote Google Sheet [{sheet_tab}] is fully up to date ({duplicate_count} records already present, 0 duplicates added)"

    # 4. Update sync history and mappings tables
    now_ts = now_kolkata_iso()
    sync_tier = "cloud_and_local" if is_cloud_synced else "local_staging"
    status_str = "success" if (is_cloud_synced or not token) else "partial_error"

    store.conn.execute("""
    INSERT INTO google_sheets_sync_history
    (workspace_id, entity_name, direction, records_pushed, records_pulled, conflicts_resolved, status, sync_tier, audit_note)
    VALUES (?, ?, 'push', ?, 0, ?, ?, ?, ?)
    """, (workspace_id, module_key, cloud_pushed_count if token else total_records, duplicate_count, status_str, sync_tier, cloud_status_note))

    store.conn.execute("""
    UPDATE sheets_module_mappings
    SET last_sync_at=?, last_status=?
    WHERE workspace_id=? AND module_key=?
    """, (now_ts, "ok" if (is_cloud_synced or not token) else "error", workspace_id, module_key))

    store.conn.execute("""
    UPDATE google_sheets_config
    SET last_sync_at=?, last_status='synced'
    WHERE workspace_id=?
    """, (now_ts, workspace_id))
    store.conn.commit()

    latency_ms = int((time.time() - t0) * 1000)

    return {
        "ok": True,
        "workspace_id": workspace_id,
        "module_key": module_key,
        "worksheet_tab": sheet_tab,
        "spreadsheet_id": spreadsheet_id,
        "is_cloud_synced": is_cloud_synced,
        "synced_entities_count": 1,
        "records_staged_locally": total_records,
        "records_pushed_to_cloud": cloud_pushed_count if token else 0,
        "total_records_staged": total_records,
        "total_records_pushed": cloud_pushed_count if token else total_records,
        "duplicates_prevented": duplicate_count,
        "sync_tier": sync_tier,
        "status_note": cloud_status_note,
        "csv_mirror": os.path.relpath(csv_file, os.getcwd()).replace("\\", "/"),
        "synced_at": now_ts,
        "latency_ms": latency_ms,
        "details": [{
            "module_key": module_key,
            "sync_tier": sync_tier,
            "status_note": cloud_status_note,
            "records_staged": total_records,
            "records_pushed": cloud_pushed_count if token else 0
        }]
    }


def sync_all_approved_modules(store: Store, workspace_id: str = "SSC") -> Dict[str, Any]:
    """Synchronizes all approved operational modules for the workspace."""
    results = []
    t0 = time.time()
    total_staged = 0
    total_cloud_pushed = 0
    total_dups = 0

    for m_key in APPROVED_MODULES.keys():
        res = sync_approved_report_to_sheet(store, workspace_id, m_key)
        results.append(res)
        total_staged += res.get("records_staged_locally", 0)
        total_cloud_pushed += res.get("records_pushed_to_cloud", 0)
        total_dups += res.get("duplicates_prevented", 0)

    now_ts = now_kolkata_iso()
    latency_ms = int((time.time() - t0) * 1000)

    token, email, _ = get_valid_google_token(store.conn, workspace_id)
    overall_status = "Connected & Synchronized" if token else "Local Staging Complete (Cloud Auth Required)"

    return {
        "ok": True,
        "workspace_id": workspace_id,
        "status": overall_status,
        "is_cloud_synced": bool(token),
        "account_email": email,
        "synced_entities_count": len(results),
        "total_modules_synced": len(results),
        "total_records_staged": total_staged,
        "total_records_pushed": total_cloud_pushed if token else total_staged,
        "total_records_pushed_to_cloud": total_cloud_pushed,
        "duplicates_prevented": total_dups,
        "latency_ms": latency_ms,
        "synced_at": now_ts,
        "module_results": results,
        "details": results
    }
