"""Comprehensive verification of the full Business Operations pipeline:

Lead -> Client -> Enquiry -> Site Visit -> Estimate -> Quotation (BOQ) ->
Work Order -> Team Allocation -> Field Work -> QC -> Report ->
Invoice (GST) -> Payment -> Expense -> Profit -> Closure.
"""
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from foundation.store import Store
from foundation.domains import business_ops


class TestBusinessOperationsPipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.store = Store()
        cls.ws = "SSC"
        # Ensure schema tables
        business_ops.ensure_business_ops_schema(cls.store.conn)

    def test_01_lead_to_client_conversion(self):
        """Step 1 & 2: Lead creation and conversion to client + site."""
        lead = self.store.create_lead(
            self.ws,
            lead_name="Vikramaditya Infrastructure Corp",
            service_interest="DGPS & Topographical Survey",
            location="Bhopal Industrial Zone",
            phone="+91 98260 99999",
            priority="high",
            notes="Need comprehensive contour and boundary survey for 500-acre logistics park."
        )
        self.assertIsNotNone(lead)
        self.assertEqual(lead["lead_priority"], "high")

        # Convert lead to client + site
        conv = self.store.convert_lead(lead["id"], self.ws, 1, create_site=True)
        self.assertIsNotNone(conv)
        self.assertEqual(conv["lead"]["lead_status"], "won")
        self.assertEqual(conv["client"]["company_name"], "Vikramaditya Infrastructure Corp")
        self.assertIsNotNone(conv.get("site"))
        self.assertTrue(conv["site"]["code"].startswith("SITE-CLT-"))

        TestBusinessOperationsPipeline.client_id = conv["client"]["id"]
        TestBusinessOperationsPipeline.site_id = conv["site"]["id"]
        TestBusinessOperationsPipeline.lead_id = lead["id"]

    def test_02_site_visit_and_estimate_creation(self):
        """Step 3 & 4: Site visit estimation."""
        est = self.store.create_estimate(
            self.ws,
            {
                "lead_id": self.lead_id,
                "client_id": self.client_id,
                "title": "Bhopal Logistics Hub 500-Acre DGPS Survey Estimate",
                "service_type": "DGPS & Topographical Survey",
                "site_location": "Bhopal Industrial Corridor",
                "estimated_amount": 250000.0,
                "scope_of_work": "DGPS boundary fixing with 4 static base stations, 0.5m interval contour mapping, and KML delivery.",
                "status": "draft",
            }
        )
        self.assertIsNotNone(est)
        self.assertEqual(est["estimated_amount"], 250000.0)
        self.assertEqual(est["status"], "draft")

        # Approve estimate
        updated_est = self.store.update_estimate_status(est["id"], "approved")
        self.assertEqual(updated_est["status"], "approved")
        TestBusinessOperationsPipeline.estimate_id = est["id"]

    def test_03_quotation_and_boq_with_gst(self):
        """Step 5 & 6: Formal Quotation with BOQ line items and 18% GST."""
        boq_items = [
            {"description": "DGPS Static & RTK Boundary Survey (Per Acre)", "unit": "Acre", "quantity": 500, "rate": 350.0, "amount": 175000.0},
            {"description": "Topographical Contour Survey (0.5m interval)", "unit": "Acre", "quantity": 500, "rate": 150.0, "amount": 75000.0},
            {"description": "KML, DWG & Deliverable CAD Processing", "unit": "Lump Sum", "quantity": 1, "rate": 20000.0, "amount": 20000.0},
        ]
        q = self.store.create_quotation(
            self.ws,
            {
                "client_id": self.client_id,
                "estimate_id": self.estimate_id,
                "project_name": "Bhopal Logistics Hub Survey",
                "items": boq_items,
                "gst_rate": 18.0,
                "validity_days": 45,
                "terms": "50% Advance with Work Order, 50% upon final drawing submission.",
            }
        )
        self.assertIsNotNone(q)
        self.assertEqual(q["subtotal"], 270000.0)  # 175k + 75k + 20k
        self.assertEqual(q["gst_rate"], 18.0)
        self.assertEqual(q["gst_amount"], 48600.0)  # 18% of 270,000
        self.assertEqual(q["total_amount"], 318600.0)
        self.assertTrue(q["quotation_number"].startswith("SSC-QT-"))
        self.assertEqual(len(q["items"]), 3)

        # Accept quotation
        accepted_q = self.store.update_quotation_status(q["id"], "accepted")
        self.assertEqual(accepted_q["status"], "accepted")
        TestBusinessOperationsPipeline.quotation_id = q["id"]
        TestBusinessOperationsPipeline.total_contract_value = q["total_amount"]

    def test_04_work_order_and_team_allocation(self):
        """Step 7: Issue Work Order and allocate Survey Team Leader."""
        # Find or create a team leader employee
        emp = self.store.fetchone("SELECT id FROM employees WHERE workspace_id=?", (self.ws,))
        if not emp:
            emp = self.store.create_employee(self.ws, "Raghav Verma", role="Survey Team Lead", department="Engineering", salary=45000.0)
        emp_id = emp["id"]

        wo = self.store.create_work_order(
            self.ws,
            {
                "quotation_id": self.quotation_id,
                "client_id": self.client_id,
                "site_id": self.site_id,
                "title": "Bhopal Logistics Hub DGPS Field Contract",
                "total_contract_value": self.total_contract_value,
                "assigned_team_leader_id": emp_id,
                "field_qc_status": "in_progress",
                "deliverables_status": "drafting",
                "notes": "Ensure high-precision dual-frequency DGPS instruments calibrated with Leica base.",
            }
        )
        self.assertIsNotNone(wo)
        self.assertTrue(wo["work_order_number"].startswith("SSC-WO-"))
        self.assertEqual(wo["total_contract_value"], 318600.0)
        self.assertEqual(wo["field_qc_status"], "in_progress")
        self.assertEqual(wo["assigned_team_leader_id"], emp_id)

        # Verify quotation status transitioned to converted_to_wo
        q_check = self.store.get_quotation(self.quotation_id)
        self.assertEqual(q_check["status"], "converted_to_wo")

        TestBusinessOperationsPipeline.work_order_id = wo["id"]
        TestBusinessOperationsPipeline.team_leader_id = emp_id

    def test_05_field_work_and_attendance(self):
        """Step 8: Field work execution and GPS attendance check-in/out."""
        att_in = self.store.log_attendance(
            self.ws,
            self.team_leader_id,
            event="check_in",
            lat=23.2599,
            lng=77.4126,
            notes="DGPS Base Station 01 Setup & Observation Commenced"
        )
        self.assertIsNotNone(att_in)
        self.assertEqual(att_in["gps_lat"], 23.2599)

        att_out = self.store.log_attendance(
            self.ws,
            self.team_leader_id,
            event="check_out",
            lat=23.2599,
            lng=77.4126,
            notes="Field observation completed; 1,420 coordinate points logged."
        )
        self.assertIsNotNone(att_out)

    def test_06_field_qc_and_deliverables_signoff(self):
        """Step 9 & 10: Quality Control inspection and deliverables approval."""
        updated_wo = self.store.update_work_order_status(
            self.work_order_id,
            status="qc_approved",
            field_qc_status="qc_passed",
            deliverables_status="accepted"
        )
        self.assertIsNotNone(updated_wo)
        self.assertEqual(updated_wo["status"], "qc_approved")
        self.assertEqual(updated_wo["field_qc_status"], "qc_passed")
        self.assertEqual(updated_wo["deliverables_status"], "accepted")

    def test_07_invoice_generation_with_gst(self):
        """Step 11: Tax invoice generation with CGST & SGST."""
        inv_items = [
            {"item": "DGPS & Topographical Survey as per WO", "hsn_sac": "998315", "quantity": 1, "rate": 270000.0, "amount": 270000.0}
        ]
        inv = self.store.create_invoice(
            self.ws,
            {
                "work_order_id": self.work_order_id,
                "client_id": self.client_id,
                "items": inv_items,
                "is_interstate": False,  # Intra-state MP: CGST 9% + SGST 9%
                "gst_rate": 18.0,
            }
        )
        self.assertIsNotNone(inv)
        self.assertTrue(inv["invoice_number"].startswith("SSC-INV-"))
        self.assertEqual(inv["subtotal"], 270000.0)
        self.assertEqual(inv["cgst_amount"], 24300.0)  # 9% of 270k
        self.assertEqual(inv["sgst_amount"], 24300.0)  # 9% of 270k
        self.assertEqual(inv["igst_amount"], 0.0)
        self.assertEqual(inv["total_tax"], 48600.0)
        self.assertEqual(inv["total_amount"], 318600.0)
        self.assertEqual(inv["payment_status"], "unpaid")
        self.assertEqual(inv["balance_due"], 318600.0)

        TestBusinessOperationsPipeline.invoice_id = inv["id"]

    def test_08_expense_claims_against_project(self):
        """Step 12 & 13: Operational field expenses and approval."""
        expense = self.store.create_expense_claim(
            self.ws,
            self.team_leader_id,
            f"WO-{self.work_order_id}",
            "fuel",
            14500.0,
            notes="Diesel for site survey vehicles and DGPS generator",
            receipt_url="/receipts/fuel_nov20.pdf"
        )
        self.assertIsNotNone(expense)
        self.assertEqual(expense["amount"], 14500.0)

        # Auto-approve for financial calculation testing
        self.store.conn.execute("UPDATE expense_claims SET status='approved' WHERE id=?", (expense["id"],))
        self.store.conn.commit()

    def test_09_payment_collection_and_reconciliation(self):
        """Step 14: Payment receipt against invoice."""
        # Partial payment 1: Advance INR 150,000
        p1 = self.store.record_payment(
            self.ws,
            self.invoice_id,
            {
                "amount": 150000.0,
                "payment_mode": "NEFT/RTGS",
                "reference_number": "HDFC-NEFT-2026112001",
                "notes": "50% project advance receipt"
            }
        )
        self.assertEqual(p1["payment_status"], "partially_paid")
        self.assertEqual(p1["amount_paid"], 150000.0)
        self.assertEqual(p1["balance_due"], 168600.0)

        # Final payment 2: Remaining INR 168,600
        p2 = self.store.record_payment(
            self.ws,
            self.invoice_id,
            {
                "amount": 168600.0,
                "payment_mode": "NEFT/RTGS",
                "reference_number": "HDFC-NEFT-2026112002",
                "notes": "Final settlement upon KML/DWG delivery signoff"
            }
        )
        self.assertEqual(p2["payment_status"], "paid")
        self.assertEqual(p2["amount_paid"], 318600.0)
        self.assertEqual(p2["balance_due"], 0.0)

    def test_10_profit_and_loss_analytics(self):
        """Step 15: P&L revenue, expenses, and operating profit verification."""
        pnl = self.store.get_profit_loss_summary(self.ws)
        self.assertIsNotNone(pnl)
        self.assertGreaterEqual(pnl["total_invoiced_inr"], 318600.0)
        self.assertGreaterEqual(pnl["total_collected_inr"], 318600.0)
        self.assertGreaterEqual(pnl["total_expenses_inr"], 14500.0)
        self.assertIsInstance(pnl["cash_operating_profit_inr"], float)
        self.assertIsInstance(pnl["accrual_operating_profit_inr"], float)
        self.assertIn("metrics", pnl)

    def test_11_project_closure(self):
        """Step 16: Complete project closure."""
        closed_wo = self.store.update_work_order_status(self.work_order_id, status="closed")
        self.assertEqual(closed_wo["status"], "closed")


if __name__ == "__main__":
    unittest.main()
