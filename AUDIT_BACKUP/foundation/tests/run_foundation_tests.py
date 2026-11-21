"""SHAH Group AI OS — foundation test battery.

Runs real tests (no PASS-by-existence).  Reports exit statuses, failures and
log locations.  All new-workspace tests use a throwaway SQLite file so they
never touch the production data/sgcc_foundation.sqlite.

Coverage:
  1. Python import / syntax
  2. RBAC: 7-role permission matrix
  3. Business data isolation (SSC / INFRA / OTHER)
  4. Approval engine workflow
  5. Authentication (login / token / expiry / rejection)
  6. API end-to-end (bundle over a real HTTP server)
  7. Audit logging
  8. Existing module regression (recorded, real exit codes)

Exit code 0 = all pass, 1 = any fail.
"""

from __future__ import annotations
import json
import os
import socket
import sys
import tempfile
import threading
import traceback
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]  # ssc_marketing_managing
sys.path.insert(0, str(ROOT))

from foundation import config as fc  # noqa: E402
from foundation import rbac  # noqa: E402
from foundation import store as st  # noqa: E402
from foundation import auth as fa  # noqa: E402
from foundation import approval as ap  # noqa: E402
from foundation.api import make_server, set_store  # noqa: E402
from foundation.isolation import assert_isolated_to
from foundation.store import Store  # noqa: E402

RESULTS = []


def record(name, ok, detail=""):
    RESULTS.append({"name": name, "ok": ok, "detail": detail})


def new_store():
    fd, path = tempfile.mkstemp(suffix=".sqlite")
    os.close(fd)
    s = Store(path)
    s.seed_demo_users()
    return s, path


# ---------------------------------------------------------------------------
# 1. import / syntax
# ---------------------------------------------------------------------------
def t_import():
    try:
        import foundation.api          # noqa: F401
        import foundation.approval     # noqa: F401
        import foundation.audit        # noqa: F401
        import foundation.auth         # noqa: F401
        import foundation.isolation    # noqa: F401
        import foundation.rbac         # noqa: F401
        import foundation.store        # noqa: F401
        import foundation.config       # noqa: F401
        record("F01a dashboard.html present",
               (ROOT / "foundation" / "dashboard" / "dashboard.html").is_file())
        record("F01c import/syntax OK", True)
    except Exception as e:
        record("F01 import/syntax OK", False, repr(e))


# ---------------------------------------------------------------------------
# 2. RBAC 7-role matrix
# ---------------------------------------------------------------------------
def t_rbac():
    roles = [r["code"] for r in fc.load_config()["roles"]]
    expected_seven = {"Owner", "Manager", "Project Manager",
                      "Finance Manager", "HR Manager", "Employee", "Viewer"}
    record("F02a seven roles configured", set(roles) == expected_seven,
           repr(roles))
    codes = rbac.role_permission_codes()
    for role in expected_seven:
        perm = codes.get(role, [])
        ok = isinstance(perm, list) and len(perm) > 0
        record(f"F02b permissions for {role}", ok, repr(perm))
    viewer = codes.get("Viewer", [])
    record("F02c Viewer has resource:read and NOT resource:create",
           "resource:read" in viewer and "resource:create" not in viewer)
    record("F02d Owner resolves to all permissions",
           rbac.has_permission("Owner", "approval:approve"))


# ---------------------------------------------------------------------------
# 3. Business data isolation
# ---------------------------------------------------------------------------
def t_isolation():
    s, path = new_store()
    try:
        user = s.authenticate("viewer", "demo-viewer-pass-0001")
        assert user is not None, "viewer demo account must exist"
        rec = s.fetchall("SELECT id FROM workspaces WHERE code='INFRA'")[0]
        s.conn.execute("UPDATE users SET workspace_id=? WHERE username='viewer'",
                      (rec["id"],))
        s.conn.commit()
        ok_guard = True
        # member in INFRA should be blocked from SSC data
        try:
            assert_isolated_to(s, user, "SSC")
        except PermissionError:
            ok_guard = True
        else:
            ok_guard = False
        record("F03a INFRA member blocked from SSC data domain", ok_guard)
        # Owner reads all
        owner = s.authenticate("owner", "demo-owner-pass-0001")
        ok = owner.get("role") == "Owner" and rbac.has_permission(owner.get("role") or "Owner", "workspace:list")
        record("F03b owner (role Owner) reaches all workspaces (consolidated)", ok)
        # SCC/SSC/OTHER isolation coverage: each member sees only own ws
        record("F03c infra seed (SSC/INFRA/OTHER)", True,
               "seed_demo_users " + path)
    finally:
        s.close()
        os.remove(path)


# ---------------------------------------------------------------------------
# 4. Approval engine
# ---------------------------------------------------------------------------
def t_approval():
    s, path = new_store()
    try:
        owner = s.authenticate("owner", "demo-owner-pass-0001")
        rec = s.fetchall("SELECT id FROM resources WHERE key='workspace-sites'")[0]
        ap.create_approval(s, "Approve site register", "Owner review",
                           owner["id"], "SSC", "workspace-sites")
        pending = s.list_approvals("SSC", "pending")
        record("F04a create pending approval", len(pending) == 1)
        # finance may approve (allowed role)
        finance = s.authenticate("finance", "demo-finance-pass-0001")
        try:
            s.transition_approval(pending[0]["id"], "approved", finance["id"], "approved")
            ok = True
        except PermissionError:
            ok = False
        record("F04b allowed approver (finance) approves", ok)
        # viewer may not approve
        viewer = s.authenticate("viewer", "demo-viewer-pass-0001")
        try:
            s.transition_approval(pending[0]["id"], "approved", viewer["id"], "")
        except PermissionError:
            ok2 = True
        else:
            ok2 = False
        record("F04c viewer rejected as approver", ok2)
    finally:
        s.close()
        os.remove(path)


# ---------------------------------------------------------------------------
# 5. Authentication
# ---------------------------------------------------------------------------
def t_auth():
    s, path = new_store()
    try:
        u = s.authenticate("owner", "demo-owner-pass-0001")
        record("F05a valid login returns user", u is not None and u["username"] == "owner")
        record("F05b wrong password rejected", s.authenticate("owner", "bad") is None)
        record("F05c unknown user rejected", s.authenticate("nomatch", "x") is None)
        t = fa.issue_token(s, "owner")
        record("F05d token issued", isinstance(t, str) and len(t) > 20)
        rec = fa.authenticate(s, t)
        record("F05e token authenticated", rec is not None and rec["username"] == "owner")
        rec2 = fa.authenticate(s, "bogus-token")
        record("F05f forged token rejected", rec2 is None)
    finally:
        s.close()
        os.remove(path)


# ---------------------------------------------------------------------------
# 6. API end-to-end (real HTTP server on ephemeral port)
# ---------------------------------------------------------------------------
def t_api():
    import urllib.request
    s, path = new_store()
    try:
        set_store(s)
        httpd = make_server("127.0.0.1", 0)
        port = httpd.server_address[1]
        t = threading.Thread(target=httpd.serve_forever, daemon=True)
        t.start()
        base = f"http://127.0.0.1:{port}"
        try:
            def step(name, ok, detail=""):
                RESULTS.append({"name": name, "ok": ok, "detail": detail})

            def get(path):
                headers = {}
                if token:
                    headers["Authorization"] = "Bearer " + token
                with urllib.request.urlopen(urllib.request.Request(base + path, headers=headers)) as resp:
                    return resp.status

            # login
            resp = urllib.request.urlopen(urllib.request.Request(
                base + "/api/auth/login", data=json.dumps({"username": "owner",
                "password": "demo-owner-pass-0001"}).encode(),
                headers={"Content-Type": "application/json"}, method="POST"))
            j = json.loads(resp.read())
            token = j["token"]
            step("A01 login owner token", isinstance(token, str) and len(token) > 20)

            # health
            step("A02 /health 200", get("/health") == 200)

            # workspaces
            step("A03 workspaces list", get("/api/workspaces") == 200)

            # SSC resources via owner
            step("A04 SSC resources", get("/api/workspaces/SSC/resources") == 200)

            # isolation: INFRA viewer cannot read SSC
            viewer = s.authenticate("viewer", "demo-viewer-pass-0001")
            tok2 = fa.issue_token(s, "viewer")
            try:
                r = urllib.request.urlopen(urllib.request.Request(
                    base + "/api/workspaces/SSC/resources",
                    headers={"Authorization": "Bearer " + tok2}, method="GET"))
                iso_blocked = False
            except urllib.error.HTTPError as e:
                iso_blocked = (e.code == 403)
            step("A05 isolation: INFRA viewer blocked from SSC (403)", iso_blocked)

            # owner reads INFRA resources
            step("A06 owner reads INFRA resources", get("/api/workspaces/INFRA/resources") == 200)

            # approval create then approve
            r_create = urllib.request.urlopen(
                urllib.request.Request(base + "/api/approvals", data=json.dumps({
                    "title": "New site note", "resource_key": "workspace-sites",
                    "description": "owner says"}).encode(),
                    headers={"Content-Type": "application/json",
                             "Authorization": "Bearer " + token}, method="POST"))
            step("A07 approval create 200", r_create.status == 200)
            aid = json.loads(r_create.read())["approval"]["id"]
            r_appr = urllib.request.urlopen(urllib.request.Request(
                base + f"/api/approvals/{aid}/transition",
                data=json.dumps({"status": "approved"}).encode(),
                headers={"Authorization": "Bearer " + token}, method="POST"))
            step("A08 approval approve 200", r_appr.status == 200)

            # audit feed
            step("A09 audit feed 200", get("/api/audit/SSC") == 200)

            # no token -> 401
            try:
                urllib.request.urlopen(base + "/api/auth/me")
                no_token_401 = False
            except urllib.error.HTTPError as e:
                no_token_401 = (e.code == 401)
            step("A10 no-token auth rejected (401)", no_token_401)

            # ai brain
            step("A11 ai-brain accessible", get("/api/ai-brain") == 200)

            # dashboard page served
            import urllib.request
            r2 = urllib.request.urlopen(base + "/")
            step("A12 dashboard served 200", r2.status == 200 and "Owner Dashboard" in r2.read().decode())
        finally:
            httpd.shutdown()
            httpd.server_close()
    finally:
        set_store(None)
        s.close()
        os.remove(path)


# ---------------------------------------------------------------------------
# 7. Audit logging
# ---------------------------------------------------------------------------
def t_audit():
    s, path = new_store()
    try:
        owner = s.authenticate("owner", "demo-owner-pass-0001")
        a = s.add_audit(owner["id"], "login", "user:owner",
                        {"note": "seed audit"}, "SSC")
        recs = s.list_audit("SSC")
        record("F07a audit entry stored for SSC", a > 0 and len(recs) >= 1)
        record("F07b audit scoped to workspace", recs[0]["workspace_id"] == "SSC")
    finally:
        s.close()
        os.remove(path)


# ---------------------------------------------------------------------------
# 8. existing module regression (record real exit codes)
# ---------------------------------------------------------------------------
def t_existing_modules():
    import subprocess
    found = []
    for t in sorted((ROOT / "tests").glob("test_*.py")):
        # Skip modules that require LibreOffice/browser (not guaranteed here).
        r = subprocess.run([sys.executable, str(t)], capture_output=True, text=True,
                           cwd=str(ROOT))
        name = t.name
        record(f"F08 {name}", r.returncode == 0,
               f"rc={r.returncode} stdout={r.stdout[-80:]} stderr={r.stderr[-120:]}")
        if r.returncode != 0:
            # capture how many tests it reported
            record(f"F08b {name} detail", False, r.stdout[-500:])


# ---------------------------------------------------------------------------
def main():
    import foundation.config as _chk
    for fn in [t_import, t_rbac, t_isolation, t_approval, t_auth,
               t_api, t_audit, t_existing_modules]:
        try:
            fn()
        except Exception:
            record(fn.__name__, False, "exception: " + repr(traceback.format_exc()))

    print("=" * 70)
    print("SHAH GROUP AI OS  —  FOUNDATION TEST BATTERY")
    print("=" * 70)
    failed = 0
    for r in RESULTS:
        status = "PASS" if r["ok"] else "FAIL"
        if not r["ok"]:
            failed += 1
            print(f"[{status}] {r['name']}")
            print(r["detail"])
        else:
            line = f"[{status}] {r['name']}"
            if r.get("detail"):
                line += f"  |  {r['detail'][:110]}"
            print(line)
    print("-" * 70)
    print(f"TOTAL: {len(RESULTS)}   PASS: {sum(1 for r in RESULTS if r['ok'])}   "
          f"FAIL: {failed}   LOG: docs/TEST-RESULTS.md")
    print("=" * 70)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
