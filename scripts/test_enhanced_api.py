# scripts/test_enhanced_api.py
import urllib.request
import json

BASE_URL = "http://127.0.0.1:8899"
LOGIN_DATA = {"username": "owner", "password": "ShahGroup_Owner_Secured_2026!#"}

# 1. Login
req = urllib.request.Request(f"{BASE_URL}/api/auth/login", data=json.dumps(LOGIN_DATA).encode(), headers={"Content-Type": "application/json"})
res = urllib.request.urlopen(req)
token = json.loads(res.read().decode())["token"]

def api_call(path, method="GET", body=None):
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(f"{BASE_URL}{path}", data=data, headers=headers, method=method)
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read().decode())

print("Testing Dynamic Quotation (10 items)...")
items_10 = [{"item_name": f"Topographic Feature {i}", "quantity": i*2, "unit": "Km", "rate": 1500, "discount": 100, "gst_rate": 18} for i in range(1, 11)]
quot_res = api_call("/api/quotations?workspace=SSC", method="POST", body={
    "project_name": "NH-44 10-Item Package",
    "client_name": "National Highways Authority of India",
    "validity_days": 45,
    "items": items_10
})
q = quot_res["quotation"]
print(f"  Quotation: {q['quotation_number']} | Items: {len(q['items'])} | Subtotal: {q['subtotal']} | Total: {q['total_amount']}")
assert len(q["items"]) == 10, "Expected 10 items"

print("Testing Survey Site Full Lifecycle & Reminders...")
site_res = api_call("/api/sites?workspace=SSC", method="POST", body={
    "name": "Bhopal Smart City GIS Survey",
    "code": "SITE-BPL-001",
    "client_name": "Bhopal Municipal Corporation",
    "project_location": "Bhopal, MP",
    "complete_address": "Zone 1, MP Nagar, Bhopal",
    "survey_type": "DGPS RTK & Drone LiDAR",
    "scope_of_work": "Sub-surface utility mapping and GIS digitization",
    "start_date": "2026-11-24", # Tomorrow
    "expected_completion_date": "2026-12-15",
    "project_value": 450000.0,
    "advance_received": 100000.0,
    "assigned_team": ["Vikram Singh", "Rahul Verma"],
    "team_leader": "Vikram Singh",
    "equipment_assigned": ["CHCNav i90 DGPS", "DJI Matrice 350 RTK"],
    "transport_details": "Bolero Camper (MH-31-CB-4040)",
    "estimated_expenses": 25000.0
})
s = site_res["site"]
print(f"  Site: {s['code']} | Status: {s['survey_status']} | Schedule Cat: {s['schedule_category']} | Bal: {s['balance_due']}")
assert s["schedule_category"] == "Tomorrow's Site", f"Expected Tomorrow's Site, got {s['schedule_category']}"

# Update Survey Status
s_status = api_call(f"/api/sites/{s['id']}/status", method="POST", body={
    "survey_status": "Field Survey Completed",
    "remarks": "LiDAR point cloud acquisition 100% complete"
})
print(f"  Site Status Updated: {s_status['site']['survey_status']}")

# Update Site Payment
s_pay = api_call(f"/api/sites/{s['id']}/payment", method="POST", body={
    "payment_received": 150000.0,
    "invoice_generated": "INV-SSC-2026-0001",
    "payment_due_date": "2026-12-05"
})
print(f"  Site Payment Updated: Status {s_pay['site']['payment_status']} | Bal: {s_pay['site']['balance_due']}")

print("Testing Non-GST Commercial Bill vs GST Invoice...")
nongst_res = api_call("/api/bills?workspace=SSC", method="POST", body={
    "bill_type": "NON_GST",
    "client_name": "Siddharth Infra Pvt Ltd",
    "description_of_work": "Topographic Consultancy & Project Advisory",
    "items": [
        {"item": "Site Alignment Advisory", "quantity": 1, "unit": "Lump Sum", "rate": 60000}
    ],
    "discount_amount": 5000
})
b = nongst_res["bill"]
print(f"  Non-GST Bill: {b['invoice_number']} | Total: {b['total_amount']} | Tax: {b['total_tax']}")
assert b["total_tax"] == 0.0, "Non-GST bill must have 0 tax!"
assert b["total_amount"] == 55000.0, "Expected 55000.0"

print("Testing Registered Vendor Workflow...")
vendor_res = api_call("/api/vendors?workspace=SSC", method="POST", body={
    "company_name": "Trimble Navigation India",
    "category": "Survey Equipment",
    "contact_person": "Amit Roy",
    "mobile": "+91 98230 11223",
    "city": "Pune",
    "state": "Maharashtra",
    "gstin": "27AAACT0000A1Z5",
    "services_supplied": "Trimble R12i GNSS Receivers & Total Stations"
})
v = vendor_res["vendor"]
print(f"  Vendor: {v['name']} | Status: {v['status']}")

# Update vendor status
v_stat = api_call(f"/api/vendors/{v['id']}/status", method="POST", body={
    "status": "Active",
    "remarks": "Vendor KYC and GSTIN verified"
})
print(f"  Vendor Status Updated: {v_stat['vendor']['status']}")

print("Testing Automated Business Report Generation...")
rep_res = api_call("/api/reports/generate?workspace=SSC", method="POST", body={
    "report_type": "EXECUTIVE_MONTHLY_PERFORMANCE",
    "date_range": "November 2026"
})
rep = rep_res["report"]
print(f"  Report Generated: {rep['title']} | Tables: {len(rep['detailed_tables_json'])}")

print("\nALL ENHANCED BACKEND ENDPOINTS TESTED AND VERIFIED SUCCESSFULLY!")
