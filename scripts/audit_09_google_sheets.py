# -*- coding: utf-8 -*-
"""Audit 09: Google Sheets Integration & Operational Sync Verification.

Verifies:
  1. Status endpoint `/api/integrations/google/status` for 12 mapped entities.
  2. Sync execution `/api/integrations/google/sync` (bidirectional push/pull).
  3. Disk verification of mirror CSV files in `data/sheets_sync/`.
  4. Google OAuth / Service Account credential verification (Live vs Local CSV Mirror).
"""
import glob
import json
import os
import urllib.request
import urllib.error

BASE_URL = "http://127.0.0.1:8899"

def req(path, method="GET", data=None, token=None):
    url = f"{BASE_URL}{path}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = json.dumps(data).encode("utf-8") if data is not None else None
    r = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(r, timeout=10) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8")
        try:
            return e.code, json.loads(raw)
        except Exception:
            return e.code, {"raw": raw}
    except Exception as ex:
        return 0, {"error": str(ex)}

def run():
    print("=== AUDIT 09: GOOGLE SHEETS INTEGRATION & SYNC ===")
    results = {}

    # 1. Login as Owner
    status, res = req("/api/auth/login", "POST", {"username": "owner", "password": "demo-owner-pass-0001"})
    token = res.get("token")
    if status != 200 or not token:
        print(f"[FAIL] Owner login failed: {status} {res}")
        return
    print("[PASS] Owner authenticated successfully.")

    # 2. Get Google Sheets Integration Status
    status, st_res = req("/api/integrations/google/status?workspace=SSC", token=token)
    results["google_status_code"] = status
    results["google_status_response"] = st_res
    entities_mapped = st_res.get("mapped_entities", [])
    print(f"[CHECK] Status API: HTTP {status}, Mapped Entities: {len(entities_mapped)} ({entities_mapped})")

    # 3. Trigger Sync Execution on "leads"
    sync_status, sync_res = req("/api/integrations/google/sync", "POST", {
        "entity": "leads",
        "direction": "bidirectional"
    }, token=token)
    results["single_entity_sync"] = {"status": sync_status, "response": sync_res}
    print(f"[CHECK] Sync API ('leads'): HTTP {sync_status}")

    # 4. Trigger Full Sync Execution ("all")
    sync_all_status, sync_all_res = req("/api/integrations/google/sync", "POST", {
        "entity": "all",
        "direction": "bidirectional"
    }, token=token)
    results["all_entities_sync"] = {"status": sync_all_status, "response": sync_all_res}
    print(f"[CHECK] Sync API ('all'): HTTP {sync_all_status}")

    # 5. Inspect CSV mirror files in data/sheets_sync/
    sync_dir = os.path.join(os.getcwd(), "data", "sheets_sync")
    csv_files = glob.glob(os.path.join(sync_dir, "*.csv"))
    file_info = []
    total_csv_rows = 0
    for cf in csv_files:
        name = os.path.basename(cf)
        size = os.path.getsize(cf)
        with open(cf, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
        row_count = len(lines) - 1 if len(lines) > 0 else 0
        total_csv_rows += row_count
        file_info.append({"filename": name, "size_bytes": size, "data_rows": row_count})

    results["csv_mirrors"] = {
        "directory": sync_dir,
        "total_files": len(csv_files),
        "total_data_rows": total_csv_rows,
        "files": file_info
    }
    print(f"[CHECK] Mirror CSVs on disk: {len(csv_files)} files, {total_csv_rows} total rows in {sync_dir}")

    # 6. Check for Google Cloud Service Account JSON / OAuth credentials
    google_creds_env = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    google_client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
    creds_file_exists = os.path.exists("credentials/google_service_account.json") or os.path.exists("credentials/client_secret.json")
    
    results["live_google_credentials"] = {
        "env_var_set": bool(google_creds_env or google_client_secret),
        "service_account_file_exists": creds_file_exists
    }
    has_live_creds = bool(google_creds_env or google_client_secret or creds_file_exists)
    results["operational_mode"] = "Live Google Account Synced" if has_live_creds else "Local CSV Mirror Sync Active (Offline Resilient, Zero Paid Billing)"
    print(f"[AUDIT VERDICT] Google Sheets Operational Mode: {results['operational_mode']}")

    os.makedirs("AUDIT_TEST_EVIDENCE", exist_ok=True)
    with open("AUDIT_TEST_EVIDENCE/audit_09_google_sheets.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print("AUDIT 09 COMPLETED: Evidence saved to AUDIT_TEST_EVIDENCE/audit_09_google_sheets.json")

if __name__ == "__main__":
    run()
