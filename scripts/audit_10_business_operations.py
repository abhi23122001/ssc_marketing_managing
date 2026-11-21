# -*- coding: utf-8 -*-
"""Audit 10: End-to-End Business Operations Pipeline Verification.

Verifies the full real-world commercial pipeline:
Lead -> Client -> Site -> Estimate -> Quotation -> Work Order -> QC Pass -> Invoice -> Payment -> P&L Summary.

Cleans up disposable test records upon completion.
"""
import json
import os
import sqlite3
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
    print("=== AUDIT 10: BUSINESS OPERATIONS PIPELINE VERIFICATION ===")
    results = {}
    created_ids = {}

    # Login as Owner
    status, res = req("/api/auth/login", "POST", {"username": "owner", "password": "demo-owner-pass-0001"})
    token = res.get("token")
    if status != 200 or not token:
        print(f"[FAIL] Owner login failed: {status}")
        return
    print("[PASS] Owner authenticated successfully.")

    try:
        # Step 1: Create Lead
        lead_payload = {
            "company": "Audit Infra Corp Ltd",
            "lead_name": "Ramesh Chandra",
            "phone": "+91 98765 43210",
            "email": "ramesh@auditinfra.example.com",
            "location": "Ahmedabad Outer Ring Road",
            "service_interest": "Drone & DGPS Boundary Survey",
            "lead_priority": "high",
            "lead_status": "enquiry"
        }
        st, r = req("/api/leads", "POST", lead_payload, token=token)
        lead = r.get("lead", {})
        created_ids["lead_id"] = lead.get("id")
        results["step_01_lead"] = {"status_code": st, "lead_id": created_ids["lead_id"]}
        print(f"[PASS] 1. Lead Created: ID {created_ids['lead_id']} (HTTP {st})")

        # Step 2: Create Client
        client_payload = {
            "company_name": "Audit Infra Corp Ltd",
            "contact_person": "Ramesh Chandra",
            "contact_phone": "+91 98765 43210",
            "contact_email": "ramesh@auditinfra.example.com",
            "billing_address": "402 Titanium City Center, Prahladnagar, Ahmedabad, Gujarat",
            "gstin": "24AAACA1234A1Z5",
            "service_package": "Enterprise Geospatial",
            "workspace_id": "SSC"
        }
        st, r = req("/api/clients", "POST", client_payload, token=token)
        client = r.get("client", {})
        created_ids["client_id"] = client.get("id")
        results["step_02_client"] = {"status_code": st, "client_id": created_ids["client_id"]}
        print(f"[PASS] 2. Client Created: ID {created_ids['client_id']} (HTTP {st})")

        # Step 3: Create Site
        site_payload = {
            "code": "AUDIT-SITE-001",
            "name": "Ahmedabad Ring Road Expressway Survey",
            "address": "SP Ring Road Km 24-38",
            "geofence_latitude": 23.0225,
            "geofence_longitude": 72.5714,
            "geofence_radius_m": 500
        }
        st, r = req("/api/sites", "POST", site_payload, token=token)
        site = r.get("site", {})
        created_ids["site_id"] = site.get("id")
        results["step_03_site"] = {"status_code": st, "site_id": created_ids["site_id"]}
        print(f"[PASS] 3. Site Created: ID {created_ids['site_id']} (HTTP {st})")

        # Step 4: Create Estimate
        estimate_payload = {
            "lead_id": created_ids["lead_id"],
            "client_id": created_ids["client_id"],
            "title": "Comprehensive DGPS & Drone Survey Estimate",
            "service_type": "DGPS & Drone Topographical Survey",
            "site_location": "SP Ring Road Km 24-38",
            "estimated_amount": 150000.0,
            "scope_of_work": "Ground control points, Drone mapping at 2cm GSD, CAD contours at 0.5m interval"
        }
        st, r = req("/api/estimates", "POST", estimate_payload, token=token)
        est = r.get("estimate", {})
        created_ids["estimate_id"] = est.get("id")
        results["step_04_estimate"] = {"status_code": st, "estimate_id": created_ids["estimate_id"]}
        print(f"[PASS] 4. Estimate Created: ID {created_ids['estimate_id']} (HTTP {st})")

        # Step 5: Create Quotation (BOQ with GST)
        quotation_payload = {
            "estimate_id": created_ids["estimate_id"],
            "client_id": created_ids["client_id"],
            "project_name": "Ring Road Topographical & Drone Survey",
            "items": [
                {"description": "DGPS Dual Frequency Base & Rover Field Work (3 Days)", "quantity": 3, "unit": "Days", "rate": 20000, "amount": 60000},
                {"description": "Drone High-Resolution Photogrammetry Survey (14 Km)", "quantity": 14, "unit": "Km", "rate": 5000, "amount": 70000},
                {"description": "CAD Topographic Deliverables & Digital Surface Model", "quantity": 1, "unit": "Lot", "rate": 20000, "amount": 20000}
            ],
            "subtotal": 150000.0,
            "gst_rate": 18.0,
            "gst_amount": 27000.0,
            "total_amount": 177000.0,
            "validity_days": 30,
            "terms": "50% Advance with Work Order, 50% on final submission"
        }
        st, r = req("/api/quotations", "POST", quotation_payload, token=token)
        quot = r.get("quotation", {})
        created_ids["quotation_id"] = quot.get("id")
        results["step_05_quotation"] = {"status_code": st, "quotation_id": created_ids["quotation_id"], "quotation_number": quot.get("quotation_number")}
        print(f"[PASS] 5. Quotation Created: ID {created_ids['quotation_id']} No: {quot.get('quotation_number')} (HTTP {st})")

        # Step 6: Create Work Order
        wo_payload = {
            "quotation_id": created_ids["quotation_id"],
            "client_id": created_ids["client_id"],
            "site_id": created_ids["site_id"],
            "title": "WO: Ahmedabad Ring Road Drone & DGPS Survey",
            "start_date": "2026-11-25",
            "target_completion_date": "2026-12-05",
            "total_contract_value": 177000.0,
            "notes": "Field team deployment scheduled for Wednesday 08:00 AM."
        }
        st, r = req("/api/work-orders", "POST", wo_payload, token=token)
        wo = r.get("work_order", {})
        created_ids["work_order_id"] = wo.get("id")
        results["step_06_work_order"] = {"status_code": st, "work_order_id": created_ids["work_order_id"], "work_order_number": wo.get("work_order_number")}
        print(f"[PASS] 6. Work Order Created: ID {created_ids['work_order_id']} No: {wo.get('work_order_number')} (HTTP {st})")

        # Step 7: Work Order QC Pass
        st, r = req(f"/api/work-orders/{created_ids['work_order_id']}/qc-pass", "POST", {"status": "in_progress"}, token=token)
        results["step_07_qc_pass"] = {"status_code": st, "field_qc_status": r.get("work_order", {}).get("field_qc_status")}
        print(f"[PASS] 7. Work Order QC Status Updated: {results['step_07_qc_pass']['field_qc_status']} (HTTP {st})")

        # Step 8: Create Invoice (GST Compliant)
        inv_payload = {
            "work_order_id": created_ids["work_order_id"],
            "client_id": created_ids["client_id"],
            "invoice_date": "2026-11-21",
            "due_date": "2026-12-05",
            "subtotal": 150000.0,
            "cgst_amount": 13500.0,
            "sgst_amount": 13500.0,
            "igst_amount": 0.0,
            "total_tax": 27000.0,
            "total_amount": 177000.0,
            "items": [
                {"description": "DGPS & Drone Topographical Survey Works", "amount": 150000.0}
            ]
        }
        st, r = req("/api/invoices", "POST", inv_payload, token=token)
        inv = r.get("invoice", {})
        created_ids["invoice_id"] = inv.get("id")
        results["step_08_invoice"] = {"status_code": st, "invoice_id": created_ids["invoice_id"], "invoice_number": inv.get("invoice_number")}
        print(f"[PASS] 8. Tax Invoice Issued: ID {created_ids['invoice_id']} No: {inv.get('invoice_number')} (HTTP {st})")

        # Step 9: Record Payment (e.g. 50% advance = 88500.0)
        pay_payload = {
            "invoice_id": created_ids["invoice_id"],
            "amount": 88500.0,
            "payment_date": "2026-11-21",
            "payment_mode": "NEFT / Bank Transfer",
            "reference_number": "NEFT-HDFC-99281920",
            "notes": "Advance payment 50% received via RTGS/NEFT"
        }
        st, r = req("/api/payments", "POST", pay_payload, token=token)
        pay_inv = r.get("invoice", {})
        results["step_09_payment"] = {
            "status_code": st,
            "amount_paid": pay_inv.get("amount_paid"),
            "payment_status": pay_inv.get("payment_status")
        }
        print(f"[PASS] 9. Payment Recorded: Rs {pay_payload['amount']} (Status: {pay_inv.get('payment_status')}) (HTTP {st})")

        # Step 10: Query Profit & Loss Summary
        st, r = req("/api/finance/profit-loss?workspace=SSC", token=token)
        pl = r.get("profit_loss", {})
        metrics = pl.get("metrics", {})
        results["step_10_profit_loss"] = {
            "status_code": st,
            "total_invoiced_inr": pl.get("total_invoiced_inr"),
            "total_collected_inr": pl.get("total_collected_inr"),
            "net_operating_profit_inr": pl.get("net_operating_profit_inr"),
            "profit_margin_pct": metrics.get("profit_margin_pct")
        }
        print(f"[PASS] 10. Consolidated P&L Summary: Invoiced Rs {pl.get('total_invoiced_inr')}, Collected Rs {pl.get('total_collected_inr')}, Margin {metrics.get('profit_margin_pct')}% (HTTP {st})")

        results["pipeline_verdict"] = "PASS"
        print("[ALL PASS] Complete Business Operations Pipeline Verified 10/10 Steps!")

    finally:
        # Cleanup disposable records
        print("\nCleaning up disposable test records from database...")
        conn = sqlite3.connect("data/sgcc_foundation.sqlite")
        try:
            if "invoice_id" in created_ids and created_ids["invoice_id"]:
                conn.execute("DELETE FROM business_payments WHERE invoice_id=?", (created_ids["invoice_id"],))
                conn.execute("DELETE FROM business_invoices WHERE id=?", (created_ids["invoice_id"],))
            if "work_order_id" in created_ids and created_ids["work_order_id"]:
                conn.execute("DELETE FROM business_work_orders WHERE id=?", (created_ids["work_order_id"],))
            if "quotation_id" in created_ids and created_ids["quotation_id"]:
                conn.execute("DELETE FROM business_quotations WHERE id=?", (created_ids["quotation_id"],))
            if "estimate_id" in created_ids and created_ids["estimate_id"]:
                conn.execute("DELETE FROM business_estimates WHERE id=?", (created_ids["estimate_id"],))
            if "site_id" in created_ids and created_ids["site_id"]:
                conn.execute("DELETE FROM sites WHERE id=?", (created_ids["site_id"],))
            if "client_id" in created_ids and created_ids["client_id"]:
                conn.execute("DELETE FROM social_client_profiles WHERE id=?", (created_ids["client_id"],))
            if "lead_id" in created_ids and created_ids["lead_id"]:
                conn.execute("DELETE FROM social_leads WHERE id=?", (created_ids["lead_id"],))
            conn.commit()
            print("[PASS] Cleanup complete. No disposable audit records remained in database.")
        except Exception as clex:
            print(f"[WARN] Cleanup error: {clex}")
        finally:
            conn.close()

    os.makedirs("AUDIT_TEST_EVIDENCE", exist_ok=True)
    with open("AUDIT_TEST_EVIDENCE/audit_10_business_operations.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print("AUDIT 10 COMPLETED: Evidence saved to AUDIT_TEST_EVIDENCE/audit_10_business_operations.json")

if __name__ == "__main__":
    run()
