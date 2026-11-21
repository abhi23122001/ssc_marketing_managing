import urllib.request, json

def login():
    data = json.dumps({"username": "owner", "password": "demo-owner-pass-0001"}).encode()
    req = urllib.request.Request("http://127.0.0.1:8899/api/auth/login", data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())["token"]

token = login()

def get_json(url):
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())

# 1. Projects isolation
p_ssc = get_json("http://127.0.0.1:8899/api/dashboard/projects?workspace=SSC")
p_infra = get_json("http://127.0.0.1:8899/api/dashboard/projects?workspace=INFRA")

ssc_codes = {s["code"] for s in p_ssc.get("sites", [])}
infra_codes = {s["code"] for s in p_infra.get("sites", [])}

print(f"SSC Sites count: {len(ssc_codes)}, sample: {list(ssc_codes)[:3]}")
print(f"INFRA Sites count: {len(infra_codes)}, sample: {list(infra_codes)[:3]}")
assert ssc_codes.isdisjoint(infra_codes), "Sites must be disjoint between SSC and INFRA!"
assert "SITE-INF-01" in infra_codes, "SITE-INF-01 must be in INFRA sites!"

# 2. CRM isolation
crm_ssc = get_json("http://127.0.0.1:8899/api/dashboard/crm?workspace=SSC")
crm_infra = get_json("http://127.0.0.1:8899/api/dashboard/crm?workspace=INFRA")

ssc_leads = {l["company"] for l in crm_ssc.get("leads", [])}
infra_leads = {l["company"] for l in crm_infra.get("leads", [])}

print(f"SSC Leads count: {len(ssc_leads)}, sample: {list(ssc_leads)[:3]}")
print(f"INFRA Leads count: {len(infra_leads)}, sample: {list(infra_leads)[:3]}")
assert ssc_leads.isdisjoint(infra_leads), "Leads must be disjoint between SSC and INFRA!"
assert "Bhopal Metro Viaduct Section 3" in infra_leads

# 3. Universal filter API isolation
f_ssc = get_json("http://127.0.0.1:8899/api/filter/sites?workspace=SSC")
f_infra = get_json("http://127.0.0.1:8899/api/filter/sites?workspace=INFRA")

f_ssc_codes = {r["code"] for r in f_ssc["records"]}
f_infra_codes = {r["code"] for r in f_infra["records"]}
assert f_ssc_codes.isdisjoint(f_infra_codes), "Universal filter must respect workspace isolation!"
assert "SITE-INF-01" in f_infra_codes

print("ALL LIVE HTTP MULTI-WORKSPACE ISOLATION CHECKS PASSED PERFECTLY!")
