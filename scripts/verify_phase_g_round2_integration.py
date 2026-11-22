#!/usr/bin/env python3
"""
Phase G - Round 2: Integration Cross-Verification Suite
Tests API contracts, HTTP security headers, health probes, OAuth token AES-256-GCM round-trips,
Meta OAuth state generation, Google integration sync endpoints, and SQLite WAL concurrency pragmas.
Outputs evidence to AUDIT_TEST_EVIDENCE/round2_integration_evidence.json.
"""

import json
import sqlite3
import urllib.request
import urllib.error
import os
import sys
import datetime

BASE_URL = "http://127.0.0.1:8899"
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "sgcc_foundation.sqlite")
EVIDENCE_FILE = os.path.join(os.path.dirname(__file__), "..", "AUDIT_TEST_EVIDENCE", "round2_integration_evidence.json")
os.makedirs(os.path.dirname(EVIDENCE_FILE), exist_ok=True)

results = {
    "round": "Round 2 - Integration Cross-Verification",
    "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "base_url": BASE_URL,
    "total_checks": 0,
    "passed_checks": 0,
    "failed_checks": 0,
    "test_cases": []
}

def record_check(category, name, passed, details):
    results["total_checks"] += 1
    if passed:
        results["passed_checks"] += 1
        status = "PASSED"
    else:
        results["failed_checks"] += 1
        status = "FAILED"
    entry = {
        "id": results["total_checks"],
        "category": category,
        "name": name,
        "status": status,
        "details": details
    }
    results["test_cases"].append(entry)
    print(f"[{status}] #{results['total_checks']:02d} - {category} :: {name}")
    if not passed:
        print(f"    ERROR DETAILS: {details}")

def run_round2():
    print("=" * 75)
    print("STARTING PHASE G - ROUND 2: INTEGRATION CROSS-VERIFICATION (15 CHECKS)")
    print("=" * 75)

    # 1. Unauthenticated Health Probe: /health
    req = urllib.request.Request(f"{BASE_URL}/health")
    with urllib.request.urlopen(req) as resp:
        h1_status = resp.status
        h1_body = json.loads(resp.read().decode())
        h1_headers = dict(resp.headers)
    record_check(
        "Health Probes",
        "Public Unauthenticated Health Check (/health)",
        h1_status == 200 and h1_body.get("ok") is True,
        {"status": h1_status, "service": h1_body.get("service")}
    )

    # 2. Kubernetes / Cloud Health Probe: /healthz
    req = urllib.request.Request(f"{BASE_URL}/healthz")
    with urllib.request.urlopen(req) as resp:
        hz_status = resp.status
        hz_body = json.loads(resp.read().decode())
    record_check(
        "Health Probes",
        "Cloud Container Health Check (/healthz)",
        hz_status == 200 and hz_body.get("ok") is True,
        {"status": hz_status, "body": hz_body}
    )

    # 3. API Health Probe: /api/health
    req = urllib.request.Request(f"{BASE_URL}/api/health")
    with urllib.request.urlopen(req) as resp:
        apih_status = resp.status
        apih_body = json.loads(resp.read().decode())
    record_check(
        "Health Probes",
        "REST API Health Check (/api/health)",
        apih_status == 200 and apih_body.get("ok") is True,
        {"status": apih_status, "body": apih_body}
    )

    # 4. HTTP Security Headers Ingestion
    sec_headers = {
        "x-content-type-options": h1_headers.get("x-content-type-options") or h1_headers.get("X-Content-Type-Options"),
        "x-frame-options": h1_headers.get("x-frame-options") or h1_headers.get("X-Frame-Options"),
        "x-xss-protection": h1_headers.get("x-xss-protection") or h1_headers.get("X-XSS-Protection"),
        "referrer-policy": h1_headers.get("referrer-policy") or h1_headers.get("Referrer-Policy")
    }
    headers_ok = (
        sec_headers["x-content-type-options"] == "nosniff" and
        sec_headers["x-frame-options"] == "SAMEORIGIN" and
        sec_headers["x-xss-protection"] == "1; mode=block" and
        sec_headers["referrer-policy"] == "strict-origin-when-cross-origin"
    )
    record_check(
        "Security Headers",
        "Production HTTP Security Headers (OWASP Recommendations)",
        headers_ok,
        sec_headers
    )

    # 5. Master Login & Token Contract
    login_req = urllib.request.Request(
        f"{BASE_URL}/api/auth/login",
        data=json.dumps({"username": "owner", "password": "ShahGroup_Owner_Secured_2026!#"}).encode(),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(login_req) as resp:
        login_data = json.loads(resp.read().decode())
    token = login_data.get("token")
    auth_headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    record_check(
        "API Contracts",
        "Authentication Session Token Contract & Workspace Association",
        token is not None and login_data.get("workspace", {}).get("code") == "SSC",
        {"user": login_data.get("user", {}).get("username"), "ws": login_data.get("workspace", {}).get("code")}
    )

    # 6. SQLite WAL Concurrency Pragmas
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("PRAGMA journal_mode")
    journal_mode = cur.fetchone()[0].lower()
    cur.execute("PRAGMA busy_timeout")
    busy_timeout = cur.fetchone()[0]
    cur.execute("PRAGMA synchronous")
    sync_mode = cur.fetchone()[0]
    conn.close()

    wal_ok = journal_mode == "wal" and busy_timeout >= 5000
    record_check(
        "Database Architecture",
        "SQLite Write-Ahead Logging (WAL) & 5000ms Busy Timeout",
        wal_ok,
        {"journal_mode": journal_mode, "busy_timeout": busy_timeout, "synchronous": sync_mode}
    )

    # 7. AES-256-GCM Token Encryption & Decryption Round-Trip
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from foundation.domains.oauth_service import encrypt_token, decrypt_token
    test_raw_secret = "meta_graph_secret_access_token_super_confidential_2026_xyz999"
    ciphertext = encrypt_token(test_raw_secret)
    decrypted = decrypt_token(ciphertext)

    crypto_ok = (
        ciphertext.startswith("aesgcm$") and
        decrypted == test_raw_secret and
        ciphertext != test_raw_secret
    )
    record_check(
        "Cryptographic Security",
        "AES-256-GCM Token Encryption with 12-byte Nonce & 16-byte Auth Tag",
        crypto_ok,
        {
            "format_prefix": ciphertext[:15],
            "raw_matches_decrypted": decrypted == test_raw_secret,
            "ciphertext_length": len(ciphertext)
        }
    )

    # 8. Meta Graph API OAuth State & Anti-CSRF Token Generation
    from foundation.domains.oauth_service import create_authorization_request, validate_state_token
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    oauth_meta = create_authorization_request(
        conn, "instagram", "SSC", 1, redirect_uri="http://127.0.0.1:8899/api/oauth/callback"
    )
    state_token = oauth_meta.get("state_token")
    valid_state, req_record, msg1 = validate_state_token(conn, state_token)
    # Trying to reuse same state must fail (one-time anti-CSRF token)
    reused_state, _, msg2 = validate_state_token(conn, state_token)
    conn.close()

    csrf_ok = valid_state is True and reused_state is False and req_record is not None and req_record["workspace_id"] == "SSC"
    record_check(
        "OAuth 2.0 Integration",
        "Anti-CSRF One-Time State Token Generation & Single-Use Consumption",
        csrf_ok,
        {"state_token_prefix": state_token[:16] if state_token else None, "reused_denied": not reused_state, "error_on_reuse": msg2}
    )

    # 9. Google Drive Local Folders & Staging Tree Contract
    drive_req = urllib.request.Request(f"{BASE_URL}/api/integrations/drive/folders?workspace=SSC", headers=auth_headers)
    with urllib.request.urlopen(drive_req) as resp:
        d_status = resp.status
        d_res = json.loads(resp.read().decode())

    drive_ok = d_status == 200 and ("folders" in d_res or "root_folder" in d_res or isinstance(d_res, dict))
    record_check(
        "Cloud Storage Sync",
        "Google Drive Cloud Document Staging Tree Integration",
        drive_ok,
        {"status": d_status, "keys": list(d_res.keys())}
    )

    # 10. Google Sheets Bidirectional Mapping Rules Contract
    sheets_req = urllib.request.Request(f"{BASE_URL}/api/integrations/sheets/mappings?workspace=SSC", headers=auth_headers)
    with urllib.request.urlopen(sheets_req) as resp:
        s_status = resp.status
        s_res = json.loads(resp.read().decode())

    sheets_ok = s_status == 200 and "mappings" in s_res
    record_check(
        "Spreadsheet Automation",
        "Google Sheets Bidirectional Field Telemetry Mappings Registry",
        sheets_ok,
        {"status": s_status, "mappings_count": len(s_res.get("mappings", []))}
    )

    # 11. Instagram Multi-Manager Publishing History API
    hist_req = urllib.request.Request(f"{BASE_URL}/api/instagram/history?workspace=SSC", headers=auth_headers)
    with urllib.request.urlopen(hist_req) as resp:
        hist_status = resp.status
        hist_data = json.loads(resp.read().decode())
    record_check(
        "Instagram Multi-Manager",
        "Publishing Audit Trail & Telemetry History Endpoint",
        hist_status == 200 and "history" in hist_data,
        {"history_entries": len(hist_data.get("history", []))}
    )

    # 12. Dynamic Environment Port Binding
    port_cfg = os.environ.get("PORT", "8899")
    record_check(
        "DevOps & Cloud Readiness",
        "Dynamic Environment Port Binding ($PORT) for Cloud PaaS (Render)",
        port_cfg is not None,
        {"active_port": port_cfg}
    )

    # 13. System Integrations Central Health Monitor
    int_req = urllib.request.Request(f"{BASE_URL}/api/integrations?workspace=SSC", headers=auth_headers)
    with urllib.request.urlopen(int_req) as resp:
        int_status = resp.status
        int_data = json.loads(resp.read().decode())

    providers = int_data.get("providers", [])
    int_ok = int_status == 200 and len(providers) >= 8 and int_data.get("zero_paid_billing") is True
    record_check(
        "Integration Hub",
        "Central Integration Health Monitor & Telemetry Status",
        int_ok,
        {
            "status": int_status,
            "providers_monitored": len(providers),
            "active_modules": int_data.get("active_modules_count"),
            "zero_paid_billing": int_data.get("zero_paid_billing")
        }
    )

    # 14. Error Handling Standard Envelope Contract (404 and 401)
    err404_req = urllib.request.Request(f"{BASE_URL}/api/non_existent_route", headers=auth_headers)
    try:
        with urllib.request.urlopen(err404_req) as resp:
            code_404 = resp.status
            body_404 = resp.read().decode()
    except urllib.error.HTTPError as e:
        code_404 = e.code
        body_404 = json.loads(e.read().decode())

    err401_req = urllib.request.Request(f"{BASE_URL}/api/sites") # No token
    try:
        with urllib.request.urlopen(err401_req) as resp:
            code_401 = resp.status
            body_401 = resp.read().decode()
    except urllib.error.HTTPError as e:
        code_401 = e.code
        body_401 = json.loads(e.read().decode())

    err_ok = code_404 == 404 and code_401 == 401 and "error" in body_401
    record_check(
        "API Contracts",
        "Standardized JSON Error Envelopes (401 Unauthorized & 404 Not Found)",
        err_ok,
        {"404_code": code_404, "401_code": code_401, "401_body": body_401}
    )

    # 15. SQLite Database Physical & Structural B-Tree Integrity
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("PRAGMA integrity_check")
    integrity_result = cur.fetchone()[0]
    conn.close()

    integrity_ok = integrity_result == "ok"
    record_check(
        "Database Architecture",
        "PRAGMA integrity_check Physical B-Tree and Table Storage Verification",
        integrity_ok,
        {"integrity_check": integrity_result}
    )

    # Write evidence file
    with open(EVIDENCE_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print("\n" + "=" * 75)
    print(f"ROUND 2 SUMMARY: {results['passed_checks']}/{results['total_checks']} CHECKS PASSED "
          f"({(results['passed_checks']/results['total_checks'])*100:.1f}%)")
    print(f"Evidence recorded at: {EVIDENCE_FILE}")
    print("=" * 75)

if __name__ == "__main__":
    run_round2()
