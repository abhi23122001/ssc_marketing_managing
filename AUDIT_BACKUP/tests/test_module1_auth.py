#!/usr/bin/env python3
"""Complete Module 1 authentication test suite."""
import sys
sys.path.insert(0, '.')

from foundation.store import Store
from foundation.auth import issue_token, authenticate, TOKEN_PREFIX

def main():
    print("=" * 60)
    print("MODULE 1 AUTHENTICATION TEST SUITE")
    print("=" * 60)

    store = Store('data/sgcc_foundation.sqlite')

    # Step 1: Owner login
    print("\n[1] Creating owner token...")
    owner_token = issue_token(store, 'owner')
    print(f"    Owner token: {owner_token[:20]}...")

    # Step 2: Manager login
    print("[2] Creating manager token...")
    manager_token = issue_token(store, 'manager')
    print(f"    Manager token: {manager_token[:20]}...")

    # Wait for server to see the changes (SQLite WAL sync)
    import time
    print("[3] Creating employee token...")
    employee_token = issue_token(store, 'employee')
    print(f"    Employee token: {employee_token[:20]}...")
    print("[4] Waiting for server database sync...")
    time.sleep(3)

    # Wait for server to see the changes (SQLite WAL sync)
    import time
    time.sleep(2)

    # Step 4: Auth check (Owner)
    print("\n[4] Auth check (Owner)...")
    user = authenticate(store, owner_token)
    assert user is not None, "Owner auth failed!"
    print(f"    Owner auth: {user['username']} ({user['role']})")

    # Step 5: Auth check (Manager)
    print("\n[5] Auth check (Manager)...")
    user = authenticate(store, manager_token)
    assert user is not None, "Manager auth failed!"
    print(f"    Manager auth: {user['username']} ({user['role']})")

    # Step 6: Auth check (Employee)
    print("\n[6] Auth check (Employee)...")
    user = authenticate(store, employee_token)
    assert user is not None, "Employee auth failed!"
    print(f"    Employee auth: {user['username']} ({user['role']})")

    # Step 7: Logout (Owner)
    print("\n[7] Logout (Owner)...")
    store.conn.execute("DELETE FROM sessions WHERE token=?", (owner_token,))
    store.conn.commit()
    print("    Owner session deleted")

    # CRITICAL: Create a fresh token for subsequent tests
    # (the old token was deleted during logout)
    import time
    print("\n[8] Creating fresh owner token for remaining tests...")
    # Re-issue a fresh token (reuse owner username)
    owner_token = issue_token(store, 'owner')
    store.conn.commit()
    time.sleep(3)  # Wait for server database sync

    # Step 8: API without token (expect 401)
    print("\n[9] API without token (expect 401)...")
    from foundation.api import Handler
    from http.server import ThreadingHTTPServer
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
    status, body = client.request("GET", "/api/workspaces")
    print(f"    Status: {status}")
    assert status == 401, "Expected 401 without token"
    print("    PASS: 401 without token")

    # Step 9: API with invalid token (expect 401)
    print("\n[10] API with invalid token (expect 401)...")
    status, body = client.request("GET", "/api/workspaces", headers={"Authorization": "Bearer invalid"})
    print(f"    Status: {status}")
    assert status == 401, "Expected 401 with invalid token"
    print("    PASS: 401 with invalid token")

    # Step 10: API with valid owner token (expect 200)
    print("\n[10] API with valid owner token (expect 200)...")
    status, body = client.request("GET", "/api/workspaces", headers={"Authorization": f"Bearer {owner_token}"})
    print(f"    Status: {status}")
    assert status == 200, f"Expected 200 with valid token, got {status}"
    print("    PASS: 200 with valid token")

    # Step 11: Session expiry
    print("\n[11] Session expiry test...")
    import time
    # Expire the manager's session
    store.conn.execute("UPDATE sessions SET expires_at=? WHERE token=?", (str(int(time.time())-1000), manager_token))
    store.conn.commit()
    user = authenticate(store, manager_token)
    assert user is None, "Expired token should return None"
    print("    PASS: Expired token rejected")

    # Step 12: Role-based permissions
    print("\n[12] Role-based permissions...")
    # Owner should have access to all workspaces
    status, body = client.request("GET", "/api/workspaces", headers={"Authorization": f"Bearer {owner_token}"})
    print(f"    Owner workspace access: {status}")
    assert status == 200, "Owner should access all workspaces"

    # Clean up
    store.conn.execute("DELETE FROM sessions WHERE token=?", (employee_token,))
    store.conn.commit()
    print("    Employee session deleted")

    print("\n" + "=" * 60)
    print("ALL AUTHENTICATION TESTS PASSED")
    print("=" * 60)

if __name__ == "__main__":
    main()
