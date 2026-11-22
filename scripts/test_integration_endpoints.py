import urllib.request, json

req = urllib.request.Request('http://127.0.0.1:8899/api/auth/login', data=json.dumps({'username':'owner', 'password':'ShahGroup_Owner_Secured_2026!#'}).encode('utf-8'), headers={'Content-Type': 'application/json'})
token = json.loads(urllib.request.urlopen(req).read().decode('utf-8'))['token']

endpoints = [
    '/api/integrations',
    '/api/integrations/center/health',
    '/api/social/accounts',
    '/api/integrations/google/status',
    '/api/integrations/sheets/mappings',
    '/api/integrations/drive/folders'
]

for ep in endpoints:
    url = f'http://127.0.0.1:8899{ep}?workspace=SSC'
    r = urllib.request.Request(url, headers={'Authorization': f'Bearer {token}'})
    try:
        with urllib.request.urlopen(r) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            print(f"[OK 200] {ep} -> {list(data.keys()) if isinstance(data, dict) else f'list[{len(data)}]'}")
    except urllib.error.HTTPError as e:
        print(f"[{e.code}] {ep}")
