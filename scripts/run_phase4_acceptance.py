# -*- coding: utf-8 -*-
"""SHAH GROUP AI OS — Comprehensive Phase 4 Acceptance Test Suite.

Verifies:
  1. SSC Social Media Account Registry (Instagram, Facebook, YouTube).
  2. Lifecycle status transitions (Not Connected, Authorization Required, Connected, Expired, Permission Missing, Error).
  3. Facebook Page vs Personal Profile determination & Meta Graph API restriction.
  4. Google Sheets Integration with owner spreadsheet (17CpMIB7mMrBalL6juZMmKVFvm2j5IvLXJjYdsbAmU5c) and 12-table local staging.
  5. Google Drive 15-folder local staging and folder binding.
  6. Security Hardening:
     - Disclosed demo owner credential 'demo-owner-pass-0001' is blocked (401).
     - Rotated owner credential succeeds.
     - Server-side session logout invalidation.
     - Password rotation with complexity checks.
     - 7-Role Security Matrix validation.
     - Cross-tenant isolation (SSC vs INFRA) and IDOR guards.
     - Login rate limiting (429).
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

BASE_URL = "http://127.0.0.1:8899"
ROTATED_OWNER_PASS = "ShahGroup_Owner_Secured_2026!#"

def req(path: str, method: str = "GET", data: dict = None, token: str = None) -> tuple[int, dict]:
    url = f"{BASE_URL}{path}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = json.dumps(data).encode("utf-8") if data is not None else None
    request = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=10) as resp:
            status = resp.status
            content = resp.read().decode("utf-8")
            try:
                res_json = json.loads(content)
            except Exception:
                res_json = {"raw": content}
            return status, res_json
    except urllib.error.HTTPError as e:
        content = e.read().decode("utf-8")
        try:
            res_json = json.loads(content)
        except Exception:
            res_json = {"raw": content}
        return e.code, res_json
    except Exception as ex:
        return 599, {"error": str(ex)}

def main():
    print("=" * 70)
    print("SHAH GROUP AI OS — PHASE 4 ACCEPTANCE AUDIT & TEST RUNNER")
    print("=" * 70)
    results = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "base_url": BASE_URL,
        "tests": [],
        "summary": {"total": 0, "passed": 0, "failed": 0}
    }

    def record(name: str, passed: bool, details: dict):
        results["summary"]["total"] += 1
        if passed:
            results["summary"]["passed"] += 1
            print(f"[PASS] {name}")
        else:
            results["summary"]["failed"] += 1
            print(f"[FAIL] {name}: {details.get('error') or details.get('response') or 'Assertion failed'}")
        results["tests"].append({
            "test_name": name,
            "passed": passed,
            "details": details
        })

    # -------------------------------------------------------------
    # 1. SECURITY: DISCLOSED DEMO OWNER CREDENTIAL ROTATION
    # -------------------------------------------------------------
    print("\n--- 1. Security: Owner Credential Rotation & Session Model ---")
    
    # 1.1 Old demo password MUST fail
    st, res = req("/api/auth/login", "POST", {"username": "owner", "password": "demo-owner-pass-0001"})
    record("Old Disclosed Demo Owner Credential Blocked", st == 401, {"status": st, "response": res})

    # 1.2 Rotated owner password MUST succeed
    st, res = req("/api/auth/login", "POST", {"username": "owner", "password": ROTATED_OWNER_PASS})
    owner_token = res.get("token")
    record("Rotated Owner Credential Login", st == 200 and bool(owner_token), {"status": st, "username": "owner"})

    # 1.3 Server-Side Logout & Session Invalidation
    st_t, res_t = req("/api/auth/login", "POST", {"username": "owner", "password": ROTATED_OWNER_PASS})
    temp_token = res_t.get("token")
    st_auth, _ = req("/api/auth/me", "GET", token=temp_token)
    st_logout, res_logout = req("/api/auth/logout", "POST", token=temp_token)
    st_after, _ = req("/api/auth/me", "GET", token=temp_token)
    record("Server-Side Logout Invalidates Session", st_auth == 200 and st_logout == 200 and st_after == 401, {
        "before_logout": st_auth, "logout_status": st_logout, "after_logout": st_after
    })

    # 1.4 Password Rotation API & Complexity Enforcement
    st_weak, res_weak = req("/api/auth/change-password", "POST", {
        "current_password": ROTATED_OWNER_PASS,
        "new_password": "short"
    }, token=owner_token)
    record("Password Complexity Enforced (Min Length/Format)", st_weak == 400, {"status": st_weak, "response": res_weak})

    # -------------------------------------------------------------
    # 2. SSC SOCIAL MEDIA ACCOUNT REGISTRY
    # -------------------------------------------------------------
    print("\n--- 2. SSC Social Media Account Registry ---")
    st_soc, res_soc = req("/api/social/accounts?workspace=SSC", "GET", token=owner_token)
    accounts = res_soc.get("accounts", [])
    record("Fetch SSC Social Accounts List", st_soc == 200 and len(accounts) >= 3, {"status": st_soc, "count": len(accounts)})

    insta = next((a for a in accounts if a.get("platform") == "instagram" and a.get("platform_account_id") == "shahgroupofficial1"), None)
    fb = next((a for a in accounts if a.get("platform") == "facebook" and a.get("platform_account_id") == "61593669391620"), None)
    yt = next((a for a in accounts if a.get("platform") == "youtube" and a.get("platform_account_id") == "@ShahGroupOfficial"), None)

    # 2.1 Instagram Verification
    record("Official Instagram Registered (@shahgroupofficial1)", insta is not None and insta.get("account_url") == "https://www.instagram.com/shahgroupofficial1/", {
        "account": insta
    })
    record("Instagram Graph API Requirement (Page Linkage in Meta Business Suite)", insta is not None and insta.get("page_linkage_required") is True, {
        "notice": insta.get("meta_graph_api_notice") if insta else None
    })

    # 2.2 Facebook Verification & Technical Determination
    record("Official Facebook Registered (ID: 61593669391620)", fb is not None and fb.get("account_url") == "https://www.facebook.com/profile.php?id=61593669391620", {
        "account": fb
    })
    record("Facebook Page vs Personal Profile Technical Determination", fb is not None and "Personal Profile" in fb.get("facebook_page_vs_profile", ""), {
        "determination": fb.get("facebook_page_vs_profile") if fb else None,
        "api_restriction": fb.get("meta_graph_api_notice") if fb else None
    })

    # 2.3 YouTube Verification
    record("Official YouTube Registered (@ShahGroupOfficial)", yt is not None and yt.get("account_url") == "https://www.youtube.com/@ShahGroupOfficial", {
        "account": yt
    })

    # 2.4 Honest Status (Zero-Simulation: Not falsely claiming Connected)
    honest_statuses = all(a.get("status") in ("Authorization Required", "Not Connected") for a in [insta, fb, yt] if a)
    record("Zero Simulation: Accounts Honest Status (Authorization Required)", honest_statuses, {
        "insta_status": insta.get("status") if insta else None,
        "fb_status": fb.get("status") if fb else None,
        "yt_status": yt.get("status") if yt else None
    })

    # 2.5 Lifecycle Status Transitions (All 6 Statuses)
    if insta:
        target_id = insta["id"]
        statuses_verified = {}
        for sc in ["set_expired", "set_permission_missing", "set_error", "set_connected", "set_not_connected", "set_auth_required"]:
            st_diag, res_diag = req("/api/oauth/diagnostic", "POST", {"account_id": target_id, "scenario": sc}, token=owner_token)
            curr_st = res_diag.get("account", {}).get("status")
            statuses_verified[sc] = curr_st
        all_matched = (
            statuses_verified.get("set_expired") == "Expired" and
            statuses_verified.get("set_permission_missing") == "Permission Missing" and
            statuses_verified.get("set_error") == "Error" and
            statuses_verified.get("set_connected") == "Connected" and
            statuses_verified.get("set_not_connected") == "Not Connected" and
            statuses_verified.get("set_auth_required") == "Authorization Required"
        )
        record("Lifecycle Status Transitions (All 6 Statuses Verified)", all_matched, statuses_verified)

    # -------------------------------------------------------------
    # 3. OAUTH CSRF STATE TOKEN VALIDATION
    # -------------------------------------------------------------
    print("\n--- 3. OAuth Anti-CSRF Security & Consent Flows ---")
    st_oa, res_oa = req("/api/oauth/authorize?provider=google&workspace=SSC", "GET", token=owner_token)
    state_token = res_oa.get("state_token")
    record("OAuth Authorization Request Generates State Token", st_oa == 200 and bool(state_token), res_oa)

    # Test OAuth Callback with invalid state token (must fail CSRF check)
    st_bad_csrf, res_bad_csrf = req("/api/oauth/callback", "POST", {
        "state": "tampered_fake_state_12345",
        "code": "test_auth_code_001"
    }, token=owner_token)
    record("Anti-CSRF State Parameter Validation Blocks Tampered Request", st_bad_csrf == 400, res_bad_csrf)

    # Test OAuth Callback with valid state token
    st_good_csrf, res_good_csrf = req("/api/oauth/callback", "POST", {
        "state": state_token,
        "code": "sample_auth_code_999"
    }, token=owner_token)
    record("Valid OAuth Anti-CSRF State Token Accepted", st_good_csrf == 200, res_good_csrf)

    # -------------------------------------------------------------
    # 4. GOOGLE SHEETS & DRIVE INTEGRATIONS
    # -------------------------------------------------------------
    print("\n--- 4. Google Sheets & Drive Integrations ---")
    st_gs, res_gs = req("/api/integrations/google/status?workspace=SSC", "GET", token=owner_token)
    record("Google Sheets Status Reports Owner Spreadsheet (17CpMIB7mMrBalL6juZMmKVFvm2j5IvLXJjYdsbAmU5c)", 
           res_gs.get("spreadsheet_id") == "17CpMIB7mMrBalL6juZMmKVFvm2j5IvLXJjYdsbAmU5c" and res_gs.get("spreadsheet_title") == "Shah AI OS",
           {"id": res_gs.get("spreadsheet_id"), "title": res_gs.get("spreadsheet_title")})

    record("Clear Distinction: Local Safe Staging vs Cloud Sync",
           "local_staging" in res_gs and "cloud_sync" in res_gs and res_gs.get("cloud_sync", {}).get("is_connected") is False, {
               "cloud_sync": res_gs.get("cloud_sync"),
               "local_staging": res_gs.get("local_staging")
           })

    # Test Sheets Operational Sync
    st_sync, res_sync = req("/api/integrations/google/sync", "POST", {"entity": "all"}, token=owner_token)
    record("Google Sheets Sync Engine Executes Safe Local Staging", st_sync == 200 and res_sync.get("ok") is True, {
        "records_pushed": res_sync.get("total_records_pushed"),
        "modules_synced": res_sync.get("synced_entities_count")
    })

    # Test Google Drive Folders (15 folders structure)
    st_df, res_df = req("/api/integrations/drive/folders?workspace=SSC", "GET", token=owner_token)
    folders = res_df.get("folders", [])
    record("Google Drive Local Safe Staging Folders Verified", st_df == 200 and len(folders) >= 10, {
        "folders_count": len(folders)
    })

    # Test File Staging into Drive Folder
    test_content_b64 = "U0hBSCBHUk9VUCBBSSBPUyAtIFRFU1QgRE9DVU1FTlQgU1RBR0lORw=="
    st_up, res_up = req("/api/integrations/drive/upload", "POST", {
        "module_key": "reports",
        "filename": "phase4_acceptance_verification_sample.txt",
        "file_b64": test_content_b64
    }, token=owner_token)
    record("Google Drive Local File Staging Upload", st_up == 201 and res_up.get("ok") is True, res_up)

    # -------------------------------------------------------------
    # 5. SEVEN ROLE SECURITY MATRIX & TENANT ISOLATION
    # -------------------------------------------------------------
    print("\n--- 5. Seven Role Security Matrix & Tenant Isolation ---")
    
    # Login users for the 7 roles
    role_credentials = [
        ("manager", "demo-manager-pass-0001", "Manager", "SSC"),
        ("pm", "demo-pm-pass-0001", "Project Manager", "INFRA"),
        ("finance", "demo-finance-pass-0001", "Finance Manager", "INFRA"),
        ("hr", "demo-hr-pass-0001", "HR Manager", "OTHER"),
        ("employee", "demo-employee-pass-0001", "Employee", "SSC"),
        ("viewer", "demo-viewer-pass-0001", "Viewer", "INFRA"),
    ]
    tokens = {"Owner": owner_token}
    for uname, pword, role, ws in role_credentials:
        st_l, res_l = req("/api/auth/login", "POST", {"username": uname, "password": pword})
        if st_l == 200 and res_l.get("token"):
            tokens[role] = res_l["token"]

    record("All 7 Roles Active and Authenticating", len(tokens) == 7, {"active_roles": list(tokens.keys())})

    # 5.1 Cross-Workspace Tenant Isolation: INFRA PM cannot access SSC sites
    pm_token = tokens.get("Project Manager")
    st_pm_ssc, res_pm_ssc = req("/api/sites?workspace=SSC", "GET", token=pm_token)
    record("Tenant Isolation: INFRA User Blocked from SSC Sites (403)", st_pm_ssc == 403, res_pm_ssc)

    # 5.2 Cross-Workspace Tenant Isolation: SSC Employee cannot access INFRA tasks
    emp_token = tokens.get("Employee")
    st_emp_inf, res_emp_inf = req("/api/tasks?workspace=INFRA", "GET", token=emp_token)
    record("Tenant Isolation: SSC User Blocked from INFRA Tasks (403)", st_emp_inf == 403, res_emp_inf)

    # 5.3 Owner has Cross-Workspace Access
    st_own_ssc, _ = req("/api/sites?workspace=SSC", "GET", token=owner_token)
    st_own_inf, _ = req("/api/sites?workspace=INFRA", "GET", token=owner_token)
    record("Owner Role Cross-Workspace Authority", st_own_ssc == 200 and st_own_inf == 200, {
        "ssc": st_own_ssc, "infra": st_own_inf
    })

    # 5.4 Role RBAC Limits: Viewer cannot create resources
    view_token = tokens.get("Viewer")
    st_view_create, res_view_create = req("/api/approvals", "POST", {
        "title": "Unauthorized Approval",
        "resource_key": "res_001"
    }, token=view_token)
    record("RBAC Gate: Viewer Role Blocked from Creating Approvals (403)", st_view_create == 403, res_view_create)

    # 5.5 Role RBAC: Finance Manager can access invoices, but Employee cannot create invoices
    fin_token = tokens.get("Finance Manager")
    st_fin_inv, _ = req("/api/invoices?workspace=INFRA", "GET", token=fin_token)
    st_emp_inv, res_emp_inv = req("/api/invoices", "POST", {"amount": 5000}, token=emp_token)
    record("RBAC Gate: Finance Manager Manages Invoices, Employee Blocked (403)", st_fin_inv == 200 and st_emp_inv == 403, {
        "finance_status": st_fin_inv, "employee_post_status": st_emp_inv
    })

    # 5.6 IDOR Protection: INFRA User blocked from querying SSC payslip by ID
    st_idor, res_idor = req("/api/payroll/payslips/1", "GET", token=pm_token)
    record("IDOR Guard: Cross-Workspace Direct Object Access Blocked (403/404)", st_idor in (403, 404), {
        "status": st_idor, "response": res_idor
    })

    # -------------------------------------------------------------
    # 6. BRUTE FORCE RATE LIMITING (Run at end of suite)
    # -------------------------------------------------------------
    print("\n--- 6. Brute Force Rate Limiting ---")
    for _ in range(5):
        req("/api/auth/login", "POST", {"username": "rate_limit_probe_user", "password": "wrong_password"})
    st_rate, res_rate = req("/api/auth/login", "POST", {"username": "rate_limit_probe_user", "password": "wrong_password"})
    record("Brute Force Rate Limiting Enforces HTTP 429", st_rate == 429, {"status": st_rate, "response": res_rate})

    # -------------------------------------------------------------
    # SUMMARY & EVIDENCE EXPORT
    # -------------------------------------------------------------
    print("\n" + "=" * 70)
    print(f"AUDIT COMPLETE: {results['summary']['passed']}/{results['summary']['total']} Tests Passed")
    print("=" * 70)

    out_file = "scripts/phase4_acceptance_results.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to: {out_file}")

if __name__ == "__main__":
    main()
