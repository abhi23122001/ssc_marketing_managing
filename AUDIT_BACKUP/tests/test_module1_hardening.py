import json, urllib.request, urllib.error, sys

BASE = "http://127.0.0.1:8899"

def req(method, path, body=None, token=None):
    data = json.dumps(body).encode() if body is not None else None
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = "Bearer " + token
    r = urllib.request.Request(BASE + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(r, timeout=10) as resp:
            raw = resp.read().decode()
            return resp.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        try:
            return e.code, json.loads(raw) if raw else {}
        except Exception:
            return e.code, {"raw": raw}

def test_module1():
    print("=== TESTING MODULE 1 AUTHENTICATION & USER MANAGEMENT ===")
    
    # 1. Login owner
    st, j = req("POST", "/api/auth/login", {"username": "owner", "password": "demo-owner-pass-0001"})
    assert st == 200, f"Owner login failed: {st} {j}"
    owner_token = j["token"]
    print("[PASS] 1. Owner login succeeded, token issued")

    # 2. Wrong password rejected
    st, j = req("POST", "/api/auth/login", {"username": "owner", "password": "wrong-password"})
    assert st == 401, f"Expected 401 for wrong password, got {st}"
    print("[PASS] 2. Invalid password rejected with 401")

    # 3. Create test user for lifecycle test
    import time
    test_user = f"test_lifecycle_{int(time.time())}"
    st, j = req("POST", "/api/users", {
        "username": test_user,
        "password": "initial_password_123",
        "name": "Lifecycle Test User",
        "role": "Viewer",
        "workspace_id": "SSC"
    }, token=owner_token)
    assert st == 201, f"User creation failed: {st} {j}"
    uid = j["user"]["id"]
    print(f"[PASS] 3. Test user created with ID {uid}")

    # 4. Login with newly created user
    st, j = req("POST", "/api/auth/login", {"username": test_user, "password": "initial_password_123"})
    assert st == 200, f"New user login failed: {st} {j}"
    user_token = j["token"]
    print("[PASS] 4. New user authenticated successfully")

    # 5. RESTful PUT /api/users/{id} to edit user name and role
    st, j = req("PUT", f"/api/users/{uid}", {
        "name": "Updated Lifecycle User",
        "role": "Employee",
        "workspace_id": "SSC"
    }, token=owner_token)
    assert st == 200, f"PUT /api/users/{uid} failed: {st} {j}"
    assert j["user"]["name"] == "Updated Lifecycle User", "Name not updated"
    assert j["user"]["role"] == "Employee", "Role not updated"
    print(f"[PASS] 5. RESTful PUT /api/users/{uid} updated name and role")

    # 6. Self-service password change
    st, j = req("POST", "/api/auth/password", {
        "old_password": "initial_password_123",
        "new_password": "new_secure_password_456"
    }, token=user_token)
    assert st == 200, f"Password change failed: {st} {j}"
    print("[PASS] 6. Self-service password change succeeded")

    # 7. Old password fails, new password succeeds
    st, _ = req("POST", "/api/auth/login", {"username": test_user, "password": "initial_password_123"})
    assert st == 401, f"Old password should fail: {st}"
    st, j = req("POST", "/api/auth/login", {"username": test_user, "password": "new_secure_password_456"})
    assert st == 200, f"New password login failed: {st}"
    active_token = j["token"]
    print("[PASS] 7. New password verified, old password rejected")

    # 8. User deactivation & session purge test
    st, j = req("POST", f"/api/users/{uid}/deactivate", {}, token=owner_token)
    assert st == 200, f"Deactivation failed: {st} {j}"
    print(f"[PASS] 8. User {uid} deactivated by Owner")

    # 9. Deactivated user token immediately fails
    st, j = req("GET", "/api/auth/me", token=active_token)
    assert st == 401, f"Deactivated user session should return 401, got {st}"
    print("[PASS] 9. Active session for deactivated user was immediately invalidated")

    # 10. Deactivated user cannot log in
    st, j = req("POST", "/api/auth/login", {"username": test_user, "password": "new_secure_password_456"})
    assert st == 401, f"Deactivated user login should return 401, got {st}"
    print("[PASS] 10. Deactivated user login rejected")

    # 11. Reactivate user
    st, j = req("POST", f"/api/users/{uid}/activate", {}, token=owner_token)
    assert st == 200, f"Activation failed: {st} {j}"
    st, j = req("POST", "/api/auth/login", {"username": test_user, "password": "new_secure_password_456"})
    assert st == 200, f"Reactivated user login failed: {st}"
    fresh_token = j["token"]
    print("[PASS] 11. Reactivated user login succeeds")

    # 12. Logout invalidates session
    st, _ = req("POST", "/api/auth/logout", {}, token=fresh_token)
    assert st == 200, "Logout call failed"
    st, _ = req("GET", "/api/auth/me", token=fresh_token)
    assert st == 401, "Logged out token should return 401"
    print("[PASS] 12. Logout successfully deleted session token from DB")

    # 13. Search and filtering
    st, j = req("GET", f"/api/users?q={test_user}", token=owner_token)
    assert st == 200, f"Search failed: {st}"
    assert any(u["username"] == test_user for u in j["users"]), "Search did not find user"
    st, j = req("GET", "/api/users?workspace=INFRA", token=owner_token)
    assert st == 200
    assert all(u["workspace_id"] == "INFRA" for u in j["users"]), "Workspace filter failed"
    print("[PASS] 13. User search (?q=...) and workspace filtering (?workspace=...) verified")

    print("\n============================================================")
    print("ALL 13 MODULE 1 HARDENING CHECKS PASSED")
    print("============================================================")

if __name__ == "__main__":
    test_module1()
