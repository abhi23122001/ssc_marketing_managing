# -*- coding: utf-8 -*-
"""Audit script for existing Google Sheets, Google Drive, and OAuth integrations."""
import sqlite3
import os
import json

def audit():
    db_path = "data/sgcc_foundation.sqlite"
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    print("=== DATABASE TABLES ===")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [r[0] for r in cursor.fetchall()]
    
    target_tables = [t for t in tables if any(k in t.lower() for k in ['sheet', 'drive', 'oauth', 'sync', 'integrat'])]
    for t in sorted(target_tables):
        count = conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        cols = [c[1] for c in conn.execute(f"PRAGMA table_info({t})").fetchall()]
        print(f"  {t} ({count} rows) -> cols: {cols}")

    print("\n=== GOOGLE SHEETS CONFIG ===")
    rows = conn.execute("SELECT * FROM google_sheets_config").fetchall()
    for r in rows:
        print(" ", dict(r))

    print("\n=== GOOGLE SHEETS MAPPINGS (Sample 3) ===")
    rows = conn.execute("SELECT * FROM sheets_module_mappings LIMIT 3").fetchall()
    for r in rows:
        print(" ", dict(r))

    print("\n=== DRIVE FOLDERS ===")
    rows = conn.execute("SELECT workspace_id, COUNT(*) as cnt FROM drive_folders GROUP BY workspace_id").fetchall()
    for r in rows:
        print(" ", dict(r))
    folders = conn.execute("SELECT * FROM drive_folders").fetchall()
    for f in folders:
        print(f"    [{f['workspace_id']}] {f['folder_name']} (module: {f['module_key']}, drive_id: '{f['drive_folder_id']}')")

    print("\n=== OAUTH TOKENS ===")
    rows = conn.execute("SELECT * FROM oauth_tokens").fetchall()
    print(f"  Total tokens: {len(rows)}")
    for r in rows:
        print(f"    [{r['workspace_id']}] provider: {r['provider']}, account: {r['account_identifier']}, expires_at: {r['expires_at']}")

    print("\n=== INTEGRATION ACTIVITY LOGS (Last 5) ===")
    rows = conn.execute("SELECT * FROM integration_activity_logs ORDER BY id DESC LIMIT 5").fetchall()
    for r in rows:
        print(" ", dict(r))

if __name__ == '__main__':
    audit()
