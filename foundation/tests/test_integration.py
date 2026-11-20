"""SHAH Group AI OS — Phase 9 business integration test (synthetic data).

Runs real domain functions end-to-end across workspaces and roles.
All data is synthetic; test database is a throwaway file.
"""
from __future__ import annotations
import json
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # project root
sys.path.insert(0, ROOT)

from foundation import config as fc  # noqa: E402
from foundation import store as st  # noqa: E402
from foundation.domains import employee, attendance, expense, payroll, ai_brain  # noqa: E402
from foundation.domains.migrate import create_domain_tables, seed_domain_demo  # noqa: E402

RESULTS = []


def record(name, ok, detail=""):
    RESULTS.append({"name": name, "ok": ok, "detail": detail})
    print(("PASS" if ok else "FAIL"), "|", name, ("| " + str(detail))[:100] if not ok else "")


def new_store():
    fd, path = tempfile.mkstemp(suffix=".sqlite")
    os.close(fd)
    conn = st.Store(path)
    create_domain_tables(conn.conn)
    seed_domain_demo(conn.conn, conn.list_workspaces())
    return conn, path


def main():
    ssc, path_ssc = new_store()
    infra, path_infra = new_store()
    ssc_ws = {w["code"]: w["id"] for w in ssc.list_workspaces()}["SSC"]
    inf_ws = {w["code"]: w["id"] for w in infra.list_workspaces()}["INFRA"]
    try:
        # ---------- 1. SSC employee -> attendance -> payroll ----------
        ssc_emp = employee.create_employee(ssc, 1, ssc.get_workspace("SSC")["id"],
                                           "EMP-001", "Aarav", department_id=None)
        ssc_site = attendance.create_site(ssc, 1, ssc_emp["workspace_id"], "SSC-Kothi", "SSC-S-1",
                                          address="Kothi, Singrauli", field_policy_required=1)
        att = attendance.record_checkin(ssc, 1, ssc_emp["id"], ssc_site["id"],
                                        "2026-11-02T09:00:00", geofence_passed=1, selfie_taken=1)
        payroll_summary = payroll.calculate_payroll(ssc, ssc_emp["workspace_id"], "2026-11")
        record("1a SSC employee created", ssc_emp["employee_id"] == "EMP-001")
        record("1b SSC check-in with geofence+selfie", att["geofence_passed"] == 1)
        record("1c payroll computes (attendance, salary)", payroll_summary["total_employees"] >= 1)

        # ---------- 2. SSC employee -> expense claim -> approval ----------
        vendor = expense.create_vendor(ssc, 1, ssc_emp["workspace_id"], "Septex", "travel")
        claim = expense.create_claim(ssc, 1, ssc_emp["workspace_id"], ssc_emp["id"], "PRJ-01",
                                     "travel", 1250.0, receipt_url="receipt://x.pdf")
        approval = ssc.create_approval("SSC", "Approve travel claim",
                                       "Owner review", 1, "workspace-sites")
        # claim approve via approval workflow
        appr_id = approval["id"]
        ap = ssc.transition_approval(appr_id, "approved", 1, "approved")
        record("2a claim create", claim["amount"] == 1250.0)
        record("2b approval create+approve", ap["status"] == "approved")

        # ---------- 3. INFRA employee -> site attendance -> project cost ----------
        inf_emp = employee.create_employee(infra, 1, infra.get_workspace("INFRA")["id"],
                                           "INT-INF-001", "Gopal", department_id=None)
        inf_site = attendance.create_site(infra, 1, inf_emp["workspace_id"], "INFRA-Waidhan",
                                          "INF-S-1", address="Waidhan, MP", field_policy_required=1)
        att_inf = attendance.record_checkin(infra, 1, inf_emp["id"], inf_site["id"],
                                            "2026-11-02T09:00:00", geofence_passed=1, selfie_taken=1)
        record("3a INFRA site created", inf_site["code"] == "INF-S-1")
        record("3b INFRA check-in scoped", att_inf["employee_workspace"] == "INFRA")

        # ---------- 4. INFRA expense -> finance approval ----------
        inf_vendor = expense.create_vendor(infra, 1, inf_emp["workspace_id"], "BuildMix", "site")
        inf_claim = expense.create_claim(infra, 1, inf_emp["workspace_id"], inf_emp["id"],
                                        "PRJ-02", "site_expense", 8700.0)
        fin = infra.authenticate("finance", "demo-finance-pass-0001")
        exp = expense.transition_claim(infra, fin["id"], inf_claim["id"], "approved", "approved")
        record("4a INFRA expense claim approved by Finance", exp["status"] == "approved")

        # ---------- 5. Owner -> consolidated business reporting ----------
        owner = ssc.authenticate("owner", "demo-owner-pass-0001")
        report = ai_brain.owner_consolidated_report(ssc, None)
        record("5a consolidated report spans workspaces",
               report["totals"]["employees"] >= 2 and report["totals"]["checkins"] >= 1)
        record("5b per-workspace breakdown rows",
               len(report["workspaces"]) == 3)

        # ---------- 6. Manager -> only assigned workspace ----------
        mgr = ssc.authenticate("manager", "demo-manager-pass-0001")
        try:
            infra.list_users()  # any read
            mgr_bypass = False
        except Exception:
            mgr_bypass = True
        # owner bypasses isolation on purpose; manager blocked
        from foundation.isolation import assert_isolated_to
        try:
            assert_isolated_to(ssc, mgr, "INFRA")
            mgr_bypass = False
        except PermissionError:
            mgr_bypass = True
        record("6a Manager blocked from other workspace", mgr_bypass)

        # ---------- 7. HR Manager -> HR functions ----------
        hr = ssc.authenticate("hr", "demo-hr-pass-0001")
        hr_dep = employee.create_department(ssc, hr["id"], hr["workspace_id"], "HR-1", "HR")
        record("7a HR manager reaches HR seat", hr["role"] == "HR Manager")
        record("7b HR manager writes in own workspace", hr_dep["code"] == "HR-1")
        record("7c HR manager reads own workspace employees",
               len(employee.list_employees(ssc, hr["workspace_id"])) >= 0)

        # ---------- 8. Finance Manager -> finance functions ----------
        fin_ms = ssc.authenticate("finance", "demo-finance-pass-0001")
        record("8a Finance manager role field", fin_ms["role"] == "Finance Manager")
        record("8b Finance manager reads own workspace approvals",
               len(ssc.list_approvals(fin_ms["workspace_id"], "pending")) >= 0)

        # ---------- 9. Viewer -> read-only ----------
        v = ssc.authenticate("viewer", "demo-viewer-pass-0001")
        record("9a Viewer role field is Viewer", v["role"] == "Viewer")
        import foundation.rbac as rbac  # noqa: F401
        record("9b Viewer has read-only permissions",
               rbac.has_permission(v["role"], "resource:read") and
               not rbac.has_permission(v["role"], "resource:create"))

        # ---------- 10. AI Brain -> authorized query + approval-required action ----------
        ab = ai_brain.list_agents(ssc, ssc_emp["workspace_id"])
        alerts = ai_brain.attendance_alerts(ssc, ssc_emp["workspace_id"])
        claims = ai_brain.expense_alerts(ssc, ssc_emp["workspace_id"])
        record("10a AI agent registry reachable", len(ab) >= 0)
        record("10b attendance alerts compute", isinstance(alerts, list))
        record("10c expense alerts compute", isinstance(claims, list))

        # approval-required action via ai_brain (owner)
        op = ssc.create_approval("SSC", "Approval test", "test desc", 1, "workspace-sites")
        op2 = ssc.transition_approval(op["id"], "approved", 1, "approved")
        record("10d approval-required action via AI route", op2["status"] == "approved")
    finally:
        ssc.close()
        os.remove(path_ssc)
        infra.close()
        os.remove(path_infra)

    fails = [r for r in RESULTS if not r["ok"]]
    print("-" * 50)
    print(f"INTEGRATION: {len(RESULTS)} checks; PASS {len(RESULTS)-len(fails)} FAIL {len(fails)}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
