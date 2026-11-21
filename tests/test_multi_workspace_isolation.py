import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from foundation.store import Store
from foundation.auth import authenticate, issue_token
from foundation.domains import filter_system


class TestMultiWorkspaceIsolation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "sgcc_foundation.sqlite"))
        cls.store = Store(db_path)

    def test_sites_workspace_isolation(self):
        ssc_sites = self.store.list_sites("SSC")
        infra_sites = self.store.list_sites("INFRA")
        self.assertTrue(len(ssc_sites) > 0, "SSC should have sites")
        self.assertTrue(len(infra_sites) > 0, "INFRA should have sites")

        ssc_codes = {s["code"] for s in ssc_sites}
        infra_codes = {s["code"] for s in infra_sites}
        self.assertTrue(ssc_codes.isdisjoint(infra_codes), "Sites must be strictly isolated between workspaces")
        self.assertIn("SITE-INF-01", infra_codes)

    def test_clients_workspace_isolation(self):
        ssc_clients = self.store.list_clients("SSC")
        infra_clients = self.store.list_clients("INFRA")
        self.assertTrue(len(ssc_clients) > 0, "SSC should have clients")
        self.assertTrue(len(infra_clients) > 0, "INFRA should have clients")

        ssc_ids = {c["client_workspace_id"] for c in ssc_clients}
        infra_ids = {c["client_workspace_id"] for c in infra_clients}
        self.assertTrue(ssc_ids.isdisjoint(infra_ids), "Clients must be strictly isolated between workspaces")
        self.assertIn("CLT-INF-01", infra_ids)

    def test_leads_workspace_isolation(self):
        ssc_leads = self.store.fetchall("SELECT * FROM social_leads WHERE workspace_id='SSC'")
        infra_leads = self.store.fetchall("SELECT * FROM social_leads WHERE workspace_id='INFRA'")
        self.assertTrue(len(ssc_leads) > 0, "SSC should have leads")
        self.assertTrue(len(infra_leads) > 0, "INFRA should have leads")

        ssc_comps = {l["company"] for l in ssc_leads}
        infra_comps = {l["company"] for l in infra_leads}
        self.assertTrue(ssc_comps.isdisjoint(infra_comps), "Leads must be strictly isolated between workspaces")

    def test_business_ops_workspace_isolation(self):
        ssc_ests = self.store.list_estimates("SSC")
        infra_ests = self.store.list_estimates("INFRA")
        self.assertTrue(len(ssc_ests) > 0)
        self.assertTrue(len(infra_ests) > 0)

        ssc_quots = self.store.list_quotations("SSC")
        infra_quots = self.store.list_quotations("INFRA")
        self.assertTrue(len(ssc_quots) > 0)
        self.assertTrue(len(infra_quots) > 0)

        ssc_wos = self.store.list_work_orders("SSC")
        infra_wos = self.store.list_work_orders("INFRA")
        self.assertTrue(len(ssc_wos) > 0)
        self.assertTrue(len(infra_wos) > 0)

        ssc_invs = self.store.list_invoices("SSC")
        infra_invs = self.store.list_invoices("INFRA")
        self.assertTrue(len(ssc_invs) > 0)
        self.assertTrue(len(infra_invs) > 0)

    def test_filter_system_workspace_isolation(self):
        # Universal filter scoped to SSC
        ssc_res = filter_system.query_filtered_records(self.store, "sites", "SSC", {})
        # Universal filter scoped to INFRA
        infra_res = filter_system.query_filtered_records(self.store, "sites", "INFRA", {})

        ssc_codes = {r["code"] for r in ssc_res["records"]}
        infra_codes = {r["code"] for r in infra_res["records"]}
        self.assertTrue(ssc_codes.isdisjoint(infra_codes))
        self.assertIn("SITE-INF-01", infra_codes)


if __name__ == "__main__":
    unittest.main()
