import sqlite3

conn = sqlite3.connect('data/sgcc_foundation.sqlite')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

print("--- USERS ---")
for r in cur.execute("SELECT u.id, u.username, u.name, r.label as role_name, u.workspace_id FROM users u LEFT JOIN roles r ON u.role_id = r.id").fetchall():
    print(f"User {r['id']}: {r['username']} ({r['name']}, {r['role_name']}, {r['workspace_id']})")

print("\n--- SITES / PROJECTS ---")
for r in cur.execute("SELECT id, name, client_name, workspace_id FROM sites LIMIT 10").fetchall():
    print(f"Site {r['id']}: {r['name']} | Client: {r['client_name']} ({r['workspace_id']})")

print("\n--- EMPLOYEES ---")
for r in cur.execute("SELECT id, name, designation, workspace_id FROM employees LIMIT 10").fetchall():
    print(f"Employee {r['id']}: {r['name']} ({r['designation']}, {r['workspace_id']})")

print("\n--- INVOICES ---")
for r in cur.execute("SELECT id, invoice_number, total_amount, workspace_id FROM business_invoices LIMIT 10").fetchall():
    print(f"Invoice {r['id']}: {r['invoice_number']} | Amount: {r['total_amount']} ({r['workspace_id']})")

print("\n--- CLIENTS (social_client_profiles) ---")
for r in cur.execute("SELECT id, company_name, industry, workspace_id FROM social_client_profiles LIMIT 10").fetchall():
    print(f"Client {r['id']}: {r['company_name']} ({r['industry']}, {r['workspace_id']})")

print("\n--- LEADS (social_leads) ---")
for r in cur.execute("SELECT id, contact_name, company, status, workspace_id FROM social_leads LIMIT 10").fetchall():
    print(f"Lead {r['id']}: {r['contact_name']} @ {r['company']} ({r['status']}, {r['workspace_id']})")

print("\n--- EXPENSE CLAIMS & VENDORS ---")
for r in cur.execute("SELECT id, vendor_name, category, workspace_id FROM expense_vendors LIMIT 5").fetchall():
    print(f"Vendor {r['id']}: {r['vendor_name']} ({r['category']}, {r['workspace_id']})")
for r in cur.execute("SELECT id, category, amount, status, workspace_id FROM expense_claims LIMIT 5").fetchall():
    print(f"Claim {r['id']}: {r['category']} Rs.{r['amount']} ({r['status']}, {r['workspace_id']})")

print("\n--- AI RESEARCH ITEMS ---")
for r in cur.execute("SELECT id, title, source_name, created_at FROM ai_research_items LIMIT 5").fetchall():
    print(f"Research {r['id']}: {r['title']} | Source: {r['source_name']}")

conn.close()
