import sys, os
sys.path.insert(0, r'C:\Users\HP\Desktop\ssc_marketing_managing')
from foundation.store import Store, now_iso

st = Store(r'C:\Users\HP\Desktop\ssc_marketing_managing\data\sgcc_foundation.sqlite')

# 1. Seed INFRA Sites
infra_sites = [
    ("SITE-INF-01", "Rewa Ring Road Civil Earthworks & Embankment", "NH-7 Bypass, Rewa, MP", 250.0),
    ("SITE-INF-02", "Shah Heights Commercial Complex Foundation", "Plot 14, Commercial Zone, Singrauli, MP", 150.0),
    ("SITE-INF-03", "Anuppur Logistics Park Pavement & Drainage", "Industrial Area, Anuppur, MP", 200.0)
]
for code, name, addr, rad in infra_sites:
    existing = st.fetchone("SELECT id FROM sites WHERE code=? AND workspace_id='INFRA'", (code,))
    if not existing:
        st.conn.execute(
            "INSERT INTO sites (workspace_id, name, code, address, geofence_radius_m, field_policy_required, status, created_at) "
            "VALUES ('INFRA', ?, ?, ?, ?, 1, 'active', ?)",
            (name, code, addr, rad, now_iso())
        )

# 2. Seed INFRA Clients
infra_clients = [
    ("CLT-INF-01", "MP State Road Development Corporation (MPSRDC)", "Highway Civil Contracting"),
    ("CLT-INF-02", "Vindhya Commercial Developers LLP", "Structural & Piling Works"),
    ("CLT-INF-03", "Rewa Urban Infrastructure Trust", "Municipal Drainage & Pavement")
]
for code, name, pkg in infra_clients:
    existing = st.fetchone("SELECT id FROM social_client_profiles WHERE client_workspace_id=?", (code,))
    if not existing:
        st.conn.execute(
            "INSERT INTO social_client_profiles (client_workspace_id, company_name, service_package, workspace_id, created_at) "
            "VALUES (?, ?, ?, 'INFRA', ?)",
            (code, name, pkg, now_iso())
        )

# 3. Seed INFRA Leads
infra_leads = [
    ("Bhopal Metro Viaduct Section 3", "Bhopal Metro Rail Corp", "9826110011", "Sub-base Earthworks", "high", "qualified"),
    ("Katni Bypass Flyover Retaining Wall", "Katni Infra Projects", "9826110022", "Piling & Concrete", "medium", "new"),
    ("Singrauli Industrial Corridor Road Extension", "Singrauli Development Authority", "9826110033", "Bituminous Paving", "high", "new")
]
for comp, lead_name, phone, interest, prio, status in infra_leads:
    existing = st.fetchone("SELECT id FROM social_leads WHERE company=? AND workspace_id='INFRA'", (comp,))
    if not existing:
        st.conn.execute(
            "INSERT INTO social_leads (workspace_id, company, lead_name, phone, service_interest, lead_priority, lead_status, created_at, updated_at) "
            "VALUES ('INFRA', ?, ?, ?, ?, ?, ?, ?, ?)",
            (comp, lead_name, phone, interest, prio, status, now_iso(), now_iso())
        )

# 4. Seed INFRA Estimates & Quotations
est_existing = st.fetchone("SELECT id FROM business_estimates WHERE workspace_id='INFRA'")
if not est_existing:
    st.conn.execute(
        "INSERT INTO business_estimates (workspace_id, title, service_type, site_location, estimated_amount, scope_of_work, status, created_at) "
        "VALUES ('INFRA', 'Rewa Bypass 12km Embankment Construction', 'Civil Earthworks', 'Rewa, MP', 4850000.0, 'Embankment compaction, sub-base preparation', 'approved', ?)",
        (now_iso(),)
    )

quot_existing = st.fetchone("SELECT id FROM business_quotations WHERE workspace_id='INFRA'")
if not quot_existing:
    st.conn.execute(
        "INSERT INTO business_quotations (workspace_id, quotation_number, project_name, subtotal, gst_rate, gst_amount, total_amount, terms, status, created_at) "
        "VALUES ('INFRA', 'Q-INF-2026-001', 'Rewa Ring Road Civil Works', 4850000.0, 18.0, 873000.0, 5723000.0, 'Standard 30-day payment milestone', 'accepted', ?)",
        (now_iso(),)
    )

# 5. Seed INFRA Work Orders & Invoices
wo_existing = st.fetchone("SELECT id FROM business_work_orders WHERE workspace_id='INFRA'")
if not wo_existing:
    st.conn.execute(
        "INSERT INTO business_work_orders (workspace_id, work_order_number, title, total_contract_value, status, field_qc_status, deliverables_status, created_at) "
        "VALUES ('INFRA', 'WO-INF-2026-001', 'Rewa Ring Road Civil Earthworks Package', 5723000.0, 'active', 'qc_passed', 'in_progress', ?)",
        (now_iso(),)
    )

inv_existing = st.fetchone("SELECT id FROM business_invoices WHERE workspace_id='INFRA'")
if not inv_existing:
    st.conn.execute(
        "INSERT INTO business_invoices (workspace_id, invoice_number, invoice_date, due_date, subtotal, total_tax, total_amount, amount_paid, payment_status, status, created_at) "
        "VALUES ('INFRA', 'INV-INF-2026-001', '2026-11-15', '2026-12-15', 2425000.0, 436500.0, 2861500.0, 1500000.0, 'partially_paid', 'issued', ?)",
        (now_iso(),)
    )

# 6. Seed INFRA Expenses & Vendors
exp_existing = st.fetchone("SELECT id FROM expense_claims WHERE workspace_id='INFRA'")
if not exp_existing:
    st.conn.execute(
        "INSERT INTO expense_claims (workspace_id, employee_id, submitted_by, category, amount, currency, status, notes, submitted_at, created_at) "
        "VALUES ('INFRA', 1, 1, 'machinery_fuel', 145000.0, 'INR', 'approved', 'Excavator & Tipper diesel fuel for Rewa Ring Road', ?, ?)",
        (now_iso(), now_iso())
    )

vend_existing = st.fetchone("SELECT id FROM expense_vendors WHERE workspace_id='INFRA'")
if not vend_existing:
    st.conn.execute(
        "INSERT INTO expense_vendors (workspace_id, name, category, status, contact_person, mobile, city, state, gstin, created_at) "
        "VALUES ('INFRA', 'Vindhya Heavy Earthmovers LLP', 'Earthmoving Machinery', 'Active', 'Rajesh Patel', '+91 94251 22334', 'Rewa', 'MP', '23AAAFV1234D1Z2', ?)",
        (now_iso(),)
    )

nongst_existing = st.fetchone("SELECT id FROM business_invoices WHERE workspace_id='INFRA' AND bill_type='NON_GST'")
if not nongst_existing:
    st.conn.execute(
        "INSERT INTO business_invoices (workspace_id, invoice_number, invoice_date, due_date, subtotal, total_tax, total_amount, amount_paid, payment_status, status, bill_type, client_name, created_at) "
        "VALUES ('INFRA', 'BILL-INF-2026-0001', '2026-11-20', '2026-12-20', 125000.0, 0.0, 125000.0, 0.0, 'unpaid', 'issued', 'NON_GST', 'Vindhya Commercial Developers LLP', ?)",
        (now_iso(),)
    )

# 7. Seed OTHER workspace records
other_sites = [("SITE-OTH-01", "Shah Ventures Agrotech Facility", "Satna Road, Maihar, MP", 300.0)]
for code, name, addr, rad in other_sites:
    existing = st.fetchone("SELECT id FROM sites WHERE code=? AND workspace_id='OTHER'", (code,))
    if not existing:
        st.conn.execute(
            "INSERT INTO sites (workspace_id, name, code, address, geofence_radius_m, status, created_at) "
            "VALUES ('OTHER', ?, ?, ?, ?, 'active', ?)",
            (name, code, addr, rad, now_iso())
        )

st.conn.commit()
print("Multi-workspace data seeded successfully.")
