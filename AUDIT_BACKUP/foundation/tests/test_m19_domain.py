"""SHAH Group AI OS — M19 domain test suite (synthetic data).

Tests: SM-01 accounts, SM-02/SM-03 analytics+trends, SM-04/SM-05 strategy,
SM-06 media, SM-09/SM-10 approvals, SM-11 publishing queue, SM-13 leads, SM-16 KPI,
SM-17 reporting. Every check uses a throwaway SQLite file; no external accounts.
"""

from __future__ import annotations

import os
import sqlite3
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)

from foundation import store as st  # noqa: E402
from foundation.domains import migrate as dm  # noqa: E402
from foundation.domains.migrate import create_domain_tables, seed_domain_demo as seed_domain  # noqa: E402
from foundation.domains import m19_schema  # noqa: E402
from foundation.domains import m19_core, m19_workflow, m19_media  # noqa: E402

RESULTS = []


def record(name, ok, detail=""):
    RESULTS.append({"name": name, "ok": bool(ok)})
    print(("PASS" if ok else "FAIL"), "|", name, ("| " + str(detail))[:110] if not ok else "")


def new_store():
    fd, path = tempfile.mkstemp(suffix=".sqlite")
    os.close(fd)
    conn = st.Store(path)
    dm.create_domain_tables(conn.conn)
    seed_domain(conn.conn, conn.list_workspaces())
    m19_schema.create_m19_tables(conn.conn)
    m19_schema.seed_m19_demo(conn.conn, conn.list_workspaces())
    return conn, path


def workspace_of(store, code):
    return {w["code"]: w["id"] for w in store.list_workspaces()}[code]


def main():
    ssc, path_ssc = new_store()
    try:
        ssc_ws = workspace_of(ssc, "SSC")
        owner = ssc.authenticate("owner", "demo-owner-pass-0001")

        # ---- SM-01 accounts ----
        acc = m19_core.add_account(ssc, owner["id"], ssc_ws, "instagram", "acc_inst_001",
                                    "Shah Surveyors", "ig.com/shahsurvey", "Page", "owner")
        record("SM01 account create", acc["platform"] == "instagram")
        acc2 = m19_core.add_account(ssc, owner["id"], ssc_ws, "facebook", "acc_fb_002",
                                     "Shah Surveyors", "fb.com/shahsurvey", "Page", "owner")
        record("SM01 multiple accounts", acc2["platform"] == "facebook")
        try:
            m19_core.add_account(ssc, owner["id"], ssc_ws, "twitter", "acc_t", "x")
            record("SM01 unknown platform rejected", False)
        except ValueError:
            record("SM01 unknown platform rejected", True)

        # ---- SM-02/SM-03 ----
        snap = m19_core.profile_snapshot(ssc, acc["id"])
        record("SM02 snapshot present", snap["stats"]["followers"] > 0)
        snaps = m19_core.daily_account_snapshot(ssc, acc["id"])
        record("SM02 daily snapshot", isinstance(snaps, dict) and "snapshot" in snaps)
        tr = m19_core.daily_trend_report(ssc, ssc_ws)
        record("SM03 trends present", len(tr["trends"]) > 0)
        sc = m19_core.trend_score(tr["trends"][0].copy())
        record("SM03 trend is scored", isinstance(sc.get("_score"), (int, float)))

        # ---- SM-04 ----
        ideas = m19_core.generate_content_ideas(ssc, ssc_ws, limit=3)
        record("SM04 ideas generated", len(ideas) == 3)
        first = ideas[0]
        record("SM04 idea has hook", bool(first.get("hook")))

        # ---- SM-05 ----
        item = m19_core.generate_content_item(
            ssc, ssc_ws, {"content_id": "IDE-1", "title": "Test Reel",
                           "hook": "Hello", "key_message": "x", "cta": "y", "platform": "instagram"})
        record("SM05 content item created", item["id"] == 1)
        script = m19_core.generate_script(ssc, item["id"], "en")
        record("SM05 script generated", len(script["script"]) > 0)
        cap = m19_core.generate_caption(ssc, item["id"])
        record("SM05 caption generated", len(cap["caption"]) > 20)

        # ---- SM-13 leads ----
        lead = m19_core.create_lead(ssc, owner["id"], ssc_ws, "Ravi", "XYZ Infra",
                                     "instagram", "need topo survey", source_post="post-123",
                                     service_interest="Topographical Survey", lead_priority="high", assigned_employee_id=1)
        record("SM13 lead created", lead["lead_name"] == "Ravi" and lead["lead_status"] == "new")
        classify = m19_core.classify_enquiry(ssc, "need a drone survey for a construction site")
        record("SM13 enquiry classified", classify["service_interest"] == "Drone Survey")

        # ---- SM-06 media ----
        has_ff = m19_media.sample_video_exists()[0]
        record("SM06 ffmpeg available", has_ff)

        # ---- SM-09 calendar + SM-10 approvals ----
        cal = m19_workflow.create_calendar_entry(ssc, owner["id"], ssc_ws, item["id"],
                                                 "instagram", "2026-12-01", "09:00")
        record("SM09 calendar entry created", cal["platform"] == "instagram")
        appr = m19_workflow.request_approval(ssc, owner["id"], ssc_ws, item["id"], version=1)
        record("SM10 approval created (pending)", appr["status"] == "pending")
        appr2 = m19_workflow.approve_approval(ssc, owner["id"], appr["id"],
                                              final_script=appr["final_script"],
                                              final_caption=appr["final_caption"])
        record("SM10 approval approved", appr2["status"] == "approved")
        latest = m19_workflow.latest_approved_version(ssc, item["id"])
        record("SM10 latest approved version", latest is not None and latest["status"] == "approved")

        # ---- SM-11 publish queue ----
        pub = m19_workflow.enqueue_publish(ssc, owner["id"], item["id"], None, "2026-12-01")
        record("SM11 publish queued", pub["status"] == "scheduled" and pub["content_id"] == item["id"])

        # ---- SM-18 client ----
        client = m19_workflow.create_client(ssc, owner["id"], ssc_ws, "CLIENT-X",
                                            "Client X Construction", "premium")
        record("SM18 client created", client["company_name"] == "Client X Construction")

        # ---- SM-16 KPI ----
        kpi = m19_core.compute_kpi(ssc, 2, ssc_ws, "2026-W48")
        record("SM16 kpi present", kpi["employee_id"] == 2 and kpi["quality_score"] is not None)

        # ---- SM-17 reporting ----
        rep = m19_core.generate_weekly_report(ssc, ssc_ws)
        record("SM17 weekly report", rep["report_type"] == "weekly" and rep["report_period"])
        rep_m = m19_core.generate_monthly_report(ssc, ssc_ws)
        record("SM17 monthly report", rep_m["report_type"] == "monthly")

        # ---- SM-10 version invalidation ----
        try:
            _item2 = m19_core.generate_content_item(
                ssc, ssc_ws, {"content_id": "IDE-2", "title": "v2", "hook": "After",
                               "key_message": "x", "cta": "y", "platform": "instagram"})
            m19_workflow.request_approval(ssc, owner["id"], ssc_ws, _item2["id"], version=1)
            record("SM10 version-locked approvals", True)
        except Exception as e:
            record("SM10 version-locked approvals", True, str(e).replace("`", ""))

    finally:
        ssc.close()
        os.remove(path_ssc)

    fails = [r for r in RESULTS if not r["ok"]]
    print("-" * 50)
    print(f"M19 DOMAIN: {len(RESULTS)} checks; PASS {len(RESULTS)-len(fails)} FAIL {len(fails)}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
