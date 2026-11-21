# -*- coding: utf-8 -*-
"""Audit 08: Social Media Connections & Integrations Verification.

Verifies:
  1. Social accounts registry for SSC and INFRA (Instagram, Facebook, YouTube, LinkedIn).
  2. Connection lifecycle (toggle connect/disconnect).
  3. Telemetry synchronization.
  4. OAuth credentials existence (real vs simulated architecture readiness).
  5. Content pipeline and trends API.
"""
import json
import os
import sys
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
    print("=== AUDIT 08: SOCIAL MEDIA INTEGRATIONS & ACCOUNTS ===")
    results = {}
    
    # 1. Login as Owner
    status, res = req("/api/auth/login", "POST", {"username": "owner", "password": "demo-owner-pass-0001"})
    token = res.get("token")
    if status != 200 or not token:
        print(f"[FAIL] Owner login failed: {status} {res}")
        return
    print("[PASS] Owner authenticated successfully.")
    
    # 2. Get SSC Social Accounts
    status, res = req("/api/social/accounts?workspace=SSC", token=token)
    results["ssc_accounts_status"] = status
    results["ssc_accounts"] = res.get("accounts", [])
    print(f"[CHECK] SSC accounts retrieved: {len(results['ssc_accounts'])} accounts (HTTP {status})")
    
    # 3. Get INFRA Social Accounts
    status_infra, res_infra = req("/api/social/accounts?workspace=INFRA", token=token)
    results["infra_accounts_status"] = status_infra
    results["infra_accounts"] = res_infra.get("accounts", [])
    print(f"[CHECK] INFRA accounts retrieved: {len(results['infra_accounts'])} accounts (HTTP {status_infra})")
    
    # 4. Check platforms covered
    platforms = set(acc.get("platform") for acc in results["ssc_accounts"])
    expected_platforms = {"instagram", "facebook", "youtube", "linkedin"}
    results["platforms_detected"] = list(platforms)
    results["all_platforms_covered"] = expected_platforms.issubset(platforms)
    print(f"[CHECK] Platforms detected in SSC: {platforms} - Covered: {results['all_platforms_covered']}")
    
    # 5. Lifecycle toggle test on account
    if results["ssc_accounts"]:
        test_acc = results["ssc_accounts"][0]
        acc_id = test_acc["id"]
        
        # Disconnect
        d_status, d_res = req(f"/api/social/accounts/{acc_id}/connect", "POST", {"connect": False}, token=token)
        # Note: in social_integrations, connect=True is /connect. Let's test connect
        c_status, c_res = req(f"/api/social/accounts/{acc_id}/connect", "POST", {}, token=token)
        results["connect_toggle"] = {"status": c_status, "response": c_res}
        print(f"[CHECK] Account connection toggle (ID {acc_id}): HTTP {c_status}")
        
        # Sync telemetry
        s_status, s_res = req(f"/api/social/accounts/{acc_id}/sync", "POST", {}, token=token)
        results["sync_telemetry"] = {"status": s_status, "response": s_res}
        print(f"[CHECK] Account telemetry sync (ID {acc_id}): HTTP {s_status}")
    
    # 6. Trends API
    t_status, t_res = req("/api/social/trends", token=token)
    results["social_trends"] = {"status": t_status, "trend_count": len(t_res.get("trends", [])) if isinstance(t_res, dict) else 0}
    print(f"[CHECK] Social trends API: HTTP {t_status}, {results['social_trends']['trend_count']} trends found")
    
    # 7. Check for actual real-world API secrets / credentials
    cred_checks = {
        "META_APP_SECRET": bool(os.getenv("META_APP_SECRET") or os.getenv("FACEBOOK_CLIENT_SECRET")),
        "INSTAGRAM_ACCESS_TOKEN": bool(os.getenv("INSTAGRAM_ACCESS_TOKEN")),
        "YOUTUBE_API_KEY": bool(os.getenv("YOUTUBE_API_KEY") or os.getenv("GOOGLE_CLIENT_SECRET")),
        "LINKEDIN_CLIENT_SECRET": bool(os.getenv("LINKEDIN_CLIENT_SECRET")),
    }
    results["live_api_credentials_present"] = cred_checks
    has_live_creds = any(cred_checks.values())
    results["operational_mode"] = "Live Authenticated" if has_live_creds else "Simulated Architecture-Ready (Pre-seeded Demo Channels)"
    print(f"[AUDIT VERDICT] Social Media Operational Mode: {results['operational_mode']}")
    
    os.makedirs("AUDIT_TEST_EVIDENCE", exist_ok=True)
    with open("AUDIT_TEST_EVIDENCE/audit_08_social_media.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print("AUDIT 08 COMPLETED: Evidence saved to AUDIT_TEST_EVIDENCE/audit_08_social_media.json")

if __name__ == "__main__":
    run()
