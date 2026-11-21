"""Automated test suite for Business Workflow integration in SHAH Group AI OS.

Tests:
  1. Owner authentication
  2. CSV leads sync (data/leads.csv -> social_leads)
  3. Query synced leads
  4. Lead status transition (new -> qualified)
  5. Lead conversion (social_leads -> social_client_profiles + sites)
  6. Query clients API (/api/clients)
  7. Query sites API (/api/sites)
  8. Create new survey site (/api/sites)
  9. Query vendors (/api/finance/vendors)
  10. Create new vendor (/api/finance/vendors)
  11. Submit expense claim (/api/finance/expenses)
  12. Query expense claims (/api/finance/expenses)
  13. Auto-approval check for expense claim
  14. Approval transition (/api/approvals/{id}/transition)
  15. AI Brain sensitive action gating (/api/ai-brain/action)
  16. Rich CRM dashboard endpoint (/api/dashboard/crm)
  17. Rich Projects dashboard endpoint (/api/dashboard/projects)
  18. Rich Finance dashboard endpoint (/api/dashboard/finance)
"""

import json
import urllib.request
import urllib.error
import sys

BASE = "http://127.0.0.1:8899"
TOKEN = None

def req(path, method="GET", body=None, token=None):
    headers = {"Content-Type": "application/json"}
    t = token or TOKEN
    if t:
        headers["Authorization"] = f"Bearer {t}"
    data = json.dumps(body).encode("utf-8") if body is not None else None
    r = urllib.request.Request(f"{BASE}{path}", data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(r) as resp:
            text = resp.read().decode("utf-8")
            return resp.status, json.loads(text) if text else {}
    except urllib.error.HTTPError as e:
        text = e.read().decode("utf-8")
        try:
            return e.code, json.loads(text)
        except Exception:
            return e.code, {"raw": text}

def run_tests():
    global TOKEN
    print("=== TESTING INTEGRATED BUSINESS WORKFLOWS ===")
    
    # 1. Login
    code, data = req("/api/auth/login", "POST", {"username": "owner", "password": "demo-owner-pass-0001"})
    assert code == 200, f"Login failed: {code} {data}"
    TOKEN = data["token"]
    print("[PASS] 1. Owner authenticated successfully")
    
    # 2. Sync leads from CSV
    code, data = req("/api/leads/sync-csv", "POST", {})
    assert code == 200 and data.get("ok"), f"CSV sync failed: {code} {data}"
    imported = data.get("imported", 0)
    print(f"[PASS] 2. CSV leads sync succeeded (imported {imported} leads, total {data.get('total_leads')})")
    
    # 3. Query leads
    code, data = req("/api/leads", "GET")
    assert code == 200 and "leads" in data, f"Get leads failed: {code} {data}"
    leads = data["leads"]
    assert len(leads) >= 4, f"Expected at least 4 leads, got {len(leads)}"
    target_lead = leads[0]
    lead_id = target_lead["id"]
    print(f"[PASS] 3. Verified leads count: {len(leads)} (Target Lead #{lead_id}: {target_lead.get('company')})")
    
    # 4. Update lead status
    code, data = req(f"/api/leads/{lead_id}/status", "POST", {"status": "qualified"})
    assert code == 200 and data.get("lead", {}).get("lead_status") == "qualified", f"Lead status update failed: {code} {data}"
    print(f"[PASS] 4. Lead #{lead_id} status updated to 'qualified'")
    
    # 5. Convert lead to client + site
    code, data = req(f"/api/leads/{lead_id}/convert", "POST", {"create_site": True})
    assert code == 200 and data.get("ok"), f"Lead conversion failed: {code} {data}"
    client = data.get("client")
    site = data.get("site")
    assert client is not None, "Client not returned from conversion"
    assert site is not None, "Site not returned from conversion"
    print(f"[PASS] 5. Lead #{lead_id} converted to Client '{client.get('company_name')}' and Site '{site.get('code')}'")
    
    # 6. Query clients
    code, data = req("/api/clients", "GET")
    assert code == 200 and len(data.get("clients", [])) >= 1, f"Clients query failed: {code} {data}"
    print(f"[PASS] 6. Query clients returned {len(data['clients'])} client record(s)")
    
    # 7. Query sites
    code, data = req("/api/sites", "GET")
    assert code == 200 and len(data.get("sites", [])) >= 4, f"Sites query failed: {code} {data}"
    print(f"[PASS] 7. Query sites returned {len(data['sites'])} active site(s)")
    
    # 8. Create new survey site
    import time
    ts = int(time.time() * 1000) % 10000
    site_payload = {
        "name": f"Singrauli Super Thermal Power Alignment {ts}",
        "code": f"SITE-SSTP-{ts}",
        "address": "Singrauli Energy Hub, MP",
        "geofence_radius_m": 250.0,
        "field_policy_required": True
    }
    code, data = req("/api/sites", "POST", site_payload)
    assert code in (200, 201) and data.get("site", {}).get("code") == site_payload["code"], f"Create site failed: {code} {data}"
    print(f"[PASS] 8. Registered new Survey Site '{site_payload['code']}'")
    
    # 9. Query vendors
    code, data = req("/api/finance/vendors", "GET")
    assert code == 200 and len(data.get("vendors", [])) >= 3, f"Query vendors failed: {code} {data}"
    print(f"[PASS] 9. Query vendors returned {len(data['vendors'])} vendor(s)")
    
    # 10. Create new vendor
    v_payload = {
        "name": f"Trimble Geospatial Spares & Repairs {ts}",
        "category": "Equipment Calibration & Spares",
        "contact": "support@trimble-central.in"
    }
    code, data = req("/api/finance/vendors", "POST", v_payload)
    assert code in (200, 201) and data.get("vendor", {}).get("name") == v_payload["name"], f"Create vendor failed: {code} {data}"
    print(f"[PASS] 10. Added new vendor '{v_payload['name']}'")
    
    # 11. Submit expense claim
    exp_payload = {
        "amount": 14500.0,
        "category": "Equipment Calibration",
        "notes": "DGPS Base & Rover annual calibration certificate fee",
        "project_id": "SITE-SSTP-05"
    }
    code, data = req("/api/finance/expenses", "POST", exp_payload)
    assert code == 201 and data.get("expense", {}).get("amount") == 14500.0, f"Submit expense failed: {code} {data}"
    exp_id = data["expense"]["id"]
    print(f"[PASS] 11. Submitted Expense Claim #{exp_id} for INR 14,500.00")
    
    # 12. Query expense claims
    code, data = req("/api/finance/expenses", "GET")
    assert code == 200 and len(data.get("expenses", [])) >= 1, f"Query expenses failed: {code} {data}"
    print(f"[PASS] 12. Query expense claims returned {len(data['expenses'])} claim(s)")
    
    # 13. Auto-approval check
    code, data = req("/api/approvals", "GET")
    assert code == 200, f"Query approvals failed: {code} {data}"
    apprs = [a for a in data.get("approvals", []) if "14,500" in a.get("title", "")]
    assert len(apprs) >= 1, f"Expected auto-created approval for expense claim, got {data.get('approvals')}"
    claim_appr = apprs[0]
    print(f"[PASS] 13. Verified auto-staged approval #{claim_appr['id']} for expense claim")
    
    # 14. Transition approval
    code, data = req(f"/api/approvals/{claim_appr['id']}/transition", "POST", {"status": "approved", "note": "Approved by Owner"})
    assert code == 200 and data.get("approval", {}).get("status") == "approved", f"Transition approval failed: {code} {data}"
    print(f"[PASS] 14. Approval #{claim_appr['id']} transitioned to 'approved'")
    
    # 15. AI Brain sensitive action gating
    ai_payload = {
        "action": "publish_post",
        "payload": {"platform": "linkedin", "post_id": 99, "caption": "New DGPS Project Announcement"}
    }
    code, data = req("/api/ai-brain/action", "POST", ai_payload)
    assert code == 200 and data.get("status") == "approval_required", f"AI action gating failed: {code} {data}"
    ai_appr_id = data.get("approval_id")
    print(f"[PASS] 15. AI Brain sensitive action successfully gated into Approval #{ai_appr_id}")
    
    # 16. Rich CRM Dashboard
    code, data = req("/api/dashboard/crm", "GET")
    assert code == 200 and "stats" in data and "leads" in data and "clients" in data, f"CRM dashboard failed: {code} {data}"
    stats = data["stats"]
    print(f"[PASS] 16. Rich CRM Dashboard verified (Total Leads: {stats['total_leads']}, Clients: {stats['clients_count']})")
    
    # 17. Rich Projects Dashboard
    code, data = req("/api/dashboard/projects", "GET")
    assert code == 200 and "sites" in data and "deliverables" in data, f"Projects dashboard failed: {code} {data}"
    print(f"[PASS] 17. Rich Projects Dashboard verified ({len(data['sites'])} sites, {len(data['deliverables'])} deliverables)")
    
    # 18. Rich Finance Dashboard
    code, data = req("/api/dashboard/finance", "GET")
    assert code == 200 and "summary" in data and "vendors" in data and "claims" in data, f"Finance dashboard failed: {code} {data}"
    f_sum = data["summary"]
    print(f"[PASS] 18. Rich Finance Dashboard verified (Total Claims INR: {f_sum['total_claims_inr']}, Vendors: {f_sum['vendor_count']})")

    print("\n" + "=" * 60)
    print("ALL 18 BUSINESS WORKFLOW CHECKS PASSED: 100% CLEAN RUN")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()
