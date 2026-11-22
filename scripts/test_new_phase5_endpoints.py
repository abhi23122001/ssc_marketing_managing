import urllib.request, json

req = urllib.request.Request(
    'http://127.0.0.1:8899/api/auth/login',
    data=json.dumps({'username':'owner', 'password':'ShahGroup_Owner_Secured_2026!#'}).encode('utf-8'),
    headers={'Content-Type': 'application/json'}
)
token = json.loads(urllib.request.urlopen(req).read().decode('utf-8'))['token']
print("Owner login success.")

def test_api(name, url, method="GET", data=None):
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    body = json.dumps(data).encode('utf-8') if data else None
    r = urllib.request.Request(f'http://127.0.0.1:8899{url}', data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(r) as resp:
            res = json.loads(resp.read().decode('utf-8'))
            print(f"[PASS] {name} ({resp.status}) -> Keys: {list(res.keys()) if isinstance(res, dict) else len(res)}")
            return res
    except urllib.error.HTTPError as e:
        print(f"[FAIL] {name} -> HTTP {e.code}: {e.read().decode('utf-8')}")
        return None

# 1. GBP Profile
gbp = test_api("GBP Profile Status", "/api/gbp/profile?workspace=SSC")
print("  GBP Business:", gbp['config']['business_name'], "| Status:", gbp['status'])

# 2. GBP Post Draft
gbp_post = test_api("GBP Create Post", "/api/gbp/posts?workspace=SSC", "POST", {
    "summary": "High-Precision DGPS RTK boundary survey services across Nagpur and Central India.",
    "call_to_action_type": "CALL"
})

# 3. Owner Setup Status
setup_status = test_api("Owner Setup Status", "/api/owner-setup/status?workspace=SSC")
print(f"  Setup Tasks: {setup_status['completed_or_ready_count']}/{setup_status['total_tasks']} ready/completed, {setup_status['action_required_count']} owner actions pending.")

# 4. Owner Credentials Save
saved_creds = test_api("Owner Credentials Save", "/api/owner-setup/credentials", "POST", {
    "GOOGLE_REDIRECT_URI": "http://127.0.0.1:8899/api/oauth/callback",
    "OWNER_BUSINESS_GSTIN": "27AABCS1234F1Z5"
})

# 5. Marketing Brief (Non-repeating)
brief = test_api("Marketing Brief Fetch", "/api/intelligence/briefs?workspace=SSC")
print("  Brief Pillar:", brief['brief']['service_pillar'], "| Title:", brief['brief']['hook_text'])

# 6. Save Brief to Content Calendar
saved_cal = test_api("Save Brief to Calendar", "/api/intelligence/briefs/save-to-calendar?workspace=SSC", "POST", {
    "brief_id": brief['brief']['id'],
    "platform": "instagram"
})
print("  Calendar Save:", saved_cal)

# 7. Integrations Summary
integrations = test_api("Integrations Summary", "/api/integrations/summary?workspace=SSC")
print("  Providers in Integration Center:", len(integrations['providers']))
for p in integrations['providers']:
    print(f"    - {p['name']}: {p['status_label']}")
