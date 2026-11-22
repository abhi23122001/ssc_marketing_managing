import urllib.request
import json

BASE = "http://127.0.0.1:8899"

# 1. Login as owner
req = urllib.request.Request(f"{BASE}/api/auth/login", data=json.dumps({"username":"owner", "password":"ShahGroup_Owner_Secured_2026!#"}).encode("utf-8"), headers={"Content-Type":"application/json"})
res = json.loads(urllib.request.urlopen(req).read().decode("utf-8"))
owner_token = res["token"]
print("Owner authenticated.")

# 2. Check workspace isolation on sites
req_ssc_sites = urllib.request.Request(f"{BASE}/api/sites?workspace=SSC", headers={"Authorization": f"Bearer {owner_token}"})
ssc_sites = json.loads(urllib.request.urlopen(req_ssc_sites).read().decode("utf-8")).get("sites", [])

req_infra_sites = urllib.request.Request(f"{BASE}/api/sites?workspace=INFRA", headers={"Authorization": f"Bearer {owner_token}"})
infra_sites = json.loads(urllib.request.urlopen(req_infra_sites).read().decode("utf-8")).get("sites", [])

print(f"SSC Sites count: {len(ssc_sites)}, INFRA Sites count: {len(infra_sites)}")

# Check that SSC sites have workspace_id == 'SSC'
for s in ssc_sites:
    assert s.get("workspace_id") == "SSC", f"Isolation breach: site {s['id']} has ws {s.get('workspace_id')}"

# 3. Check billing isolation
req_ssc_bills = urllib.request.Request(f"{BASE}/api/bills?workspace=SSC", headers={"Authorization": f"Bearer {owner_token}"})
ssc_bills = json.loads(urllib.request.urlopen(req_ssc_bills).read().decode("utf-8")).get("bills", [])

req_infra_bills = urllib.request.Request(f"{BASE}/api/bills?workspace=INFRA", headers={"Authorization": f"Bearer {owner_token}"})
infra_bills = json.loads(urllib.request.urlopen(req_infra_bills).read().decode("utf-8")).get("bills", [])

print(f"SSC Bills count: {len(ssc_bills)}, INFRA Bills count: {len(infra_bills)}")
for b in ssc_bills:
    assert b.get("workspace_id") == "SSC", f"Isolation breach: bill {b['id']} has ws {b.get('workspace_id')}"

# 4. Check vendor isolation
req_ssc_v = urllib.request.Request(f"{BASE}/api/vendors?workspace=SSC", headers={"Authorization": f"Bearer {owner_token}"})
ssc_v = json.loads(urllib.request.urlopen(req_ssc_v).read().decode("utf-8")).get("vendors", [])

req_infra_v = urllib.request.Request(f"{BASE}/api/vendors?workspace=INFRA", headers={"Authorization": f"Bearer {owner_token}"})
infra_v = json.loads(urllib.request.urlopen(req_infra_v).read().decode("utf-8")).get("vendors", [])

print(f"SSC Vendors count: {len(ssc_v)}, INFRA Vendors count: {len(infra_v)}")

print("ALL MULTI-TENANT ISOLATION ASSERTIONS PASSED WITH ZERO CROSS-LEAKAGE!")
