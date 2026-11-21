#!/usr/bin/env python3
"""Debug the HTTP client test."""
import sys
sys.path.insert(0, '.')

from foundation.store import Store
from foundation.auth import issue_token

store = Store('data/sgcc_foundation.sqlite')
owner_token = issue_token(store, 'owner')
store.conn.commit()

print('Owner token:', owner_token)
print('Token length:', len(owner_token))

# Test the token with direct Python
from foundation.auth import authenticate
user = authenticate(store, owner_token)
print('Authenticate (Python):', user['username'] if user else None)

# Test with HTTP
import urllib.request, urllib.error
url = 'http://127.0.0.1:8899/api/auth/me'
req = urllib.request.Request(url, method='GET')
req.add_header('Authorization', 'Bearer ' + owner_token)
try:
    resp = urllib.request.urlopen(req)
    print('Auth me status:', resp.status)
    print('Auth me body:', resp.read().decode())
except urllib.error.HTTPError as e:
    print('Auth me status:', e.code)
    print('Auth me body:', e.read().decode())
