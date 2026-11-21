#!/usr/bin/env python3
"""Debug the test script's HTTP client."""
import sys
sys.path.insert(0, '.')

from foundation.store import Store
from foundation.auth import issue_token, authenticate

# Create store
store = Store('data/sgcc_foundation.sqlite')
owner_token = issue_token(store, 'owner')
store.conn.commit()
print('owner_token:', owner_token)

# Test authenticate directly
user = authenticate(store, owner_token)
print('Authenticate (Python):', user['username'] if user else None)

# Test with HTTP using the same method as the test script
import urllib.request, urllib.error

class TestClient:
    def __init__(self, base_url):
        self.base_url = base_url

    def request(self, method, path, headers=None, body=None):
        url = self.base_url + path
        data = None
        if body:
            data = body.encode()
        req = urllib.request.Request(url, data=data, method=method)
        if headers:
            for k, v in headers.items():
                req.add_header(k, v)
        try:
            resp = urllib.request.urlopen(req)
            return resp.status, resp.read().decode()
        except urllib.error.HTTPError as e:
            return e.code, e.read().decode()

client = TestClient("http://127.0.0.1:8899")
status, body = client.request("GET", "/api/auth/me", headers={"Authorization": f"Bearer {owner_token}"})
print('Status:', status)
print('Body:', body[:100])
print('PASS:', '200' if status == 200 else 'FAIL')
