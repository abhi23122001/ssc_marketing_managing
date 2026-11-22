# scripts/migrate_enhancements.py
import sqlite3
import os

DB_PATHS = [
    r"C:\Users\HP\Desktop\ssc_marketing_managing\data\sgcc_foundation.sqlite",
    r"C:\Users\HP\Desktop\ssc_marketing_managing\data\business_os.db"
]

MIGRATIONS = {
    "sites": [
        ("client_name", "TEXT DEFAULT ''"),
        ("project_location", "TEXT DEFAULT ''"),
        ("complete_address", "TEXT DEFAULT ''"),
        ("coordinates", "TEXT DEFAULT ''"),
        ("survey_type", "TEXT DEFAULT 'Topographic Survey'"),
        ("scope_of_work", "TEXT DEFAULT ''"),
        ("start_date", "TEXT DEFAULT ''"),
        ("expected_completion_date", "TEXT DEFAULT ''"),
        ("assigned_team", "TEXT DEFAULT '[]'"),
        ("team_leader", "TEXT DEFAULT ''"),
        ("equipment_assigned", "TEXT DEFAULT '[]'"),
        ("transport_details", "TEXT DEFAULT ''"),
        ("estimated_expenses", "REAL DEFAULT 0.0"),
        ("special_instructions", "TEXT DEFAULT ''"),
        ("required_documents", "TEXT DEFAULT ''"),
        ("site_contact_person", "TEXT DEFAULT ''"),
        ("site_contact_phone", "TEXT DEFAULT ''"),
        ("survey_status", "TEXT DEFAULT 'Site Scheduled'"),
        ("status_history", "TEXT DEFAULT '[]'"),
        ("project_value", "REAL DEFAULT 0.0"),
        ("advance_received", "REAL DEFAULT 0.0"),
        ("invoice_generated", "TEXT DEFAULT ''"),
        ("total_billed", "REAL DEFAULT 0.0"),
        ("payment_received", "REAL DEFAULT 0.0"),
        ("balance_due", "REAL DEFAULT 0.0"),
        ("payment_due_date", "TEXT DEFAULT ''"),
        ("last_followup_date", "TEXT DEFAULT ''"),
        ("next_followup_date", "TEXT DEFAULT ''"),
        ("payment_status", "TEXT DEFAULT 'Not Invoiced'"),
        ("documents_json", "TEXT DEFAULT '[]'")
    ],
    "employees": [
        ("employment_status", "TEXT DEFAULT 'Active'"),
        ("exit_date", "TEXT DEFAULT ''"),
        ("last_working_date", "TEXT DEFAULT ''"),
        ("reason_for_leaving", "TEXT DEFAULT ''"),
        ("exit_type", "TEXT DEFAULT ''"),
        ("notice_period_details", "TEXT DEFAULT ''"),
        ("handover_status", "TEXT DEFAULT ''"),
        ("final_settlement_status", "TEXT DEFAULT ''"),
        ("exit_remarks", "TEXT DEFAULT ''"),
        ("status_history", "TEXT DEFAULT '[]'")
    ],
    "expense_vendors": [
        ("company_name", "TEXT DEFAULT ''"),
        ("contact_person", "TEXT DEFAULT ''"),
        ("mobile", "TEXT DEFAULT ''"),
        ("email", "TEXT DEFAULT ''"),
        ("address", "TEXT DEFAULT ''"),
        ("city", "TEXT DEFAULT ''"),
        ("state", "TEXT DEFAULT ''"),
        ("pincode", "TEXT DEFAULT ''"),
        ("gstin", "TEXT DEFAULT ''"),
        ("pan", "TEXT DEFAULT ''"),
        ("msme_udyam", "TEXT DEFAULT ''"),
        ("bank_name", "TEXT DEFAULT ''"),
        ("bank_account", "TEXT DEFAULT ''"),
        ("bank_ifsc", "TEXT DEFAULT ''"),
        ("bank_branch", "TEXT DEFAULT ''"),
        ("services_supplied", "TEXT DEFAULT ''"),
        ("registration_date", "TEXT DEFAULT ''"),
        ("documents_json", "TEXT DEFAULT '[]'"),
        ("status", "TEXT DEFAULT 'Approved'"),
        ("notes", "TEXT DEFAULT ''"),
        ("status_history", "TEXT DEFAULT '[]'")
    ],
    "business_invoices": [
        ("bill_type", "TEXT DEFAULT 'GST'"),
        ("bill_number", "TEXT DEFAULT ''"),
        ("client_name", "TEXT DEFAULT ''"),
        ("client_address", "TEXT DEFAULT ''"),
        ("client_contact", "TEXT DEFAULT ''"),
        ("description_of_work", "TEXT DEFAULT ''"),
        ("discount_amount", "REAL DEFAULT 0.0"),
        ("amount_in_words", "TEXT DEFAULT ''"),
        ("payment_mode", "TEXT DEFAULT ''"),
        ("notes", "TEXT DEFAULT ''"),
        ("authorized_signature", "TEXT DEFAULT ''")
    ],
    "business_quotations": [
        ("discount_total", "REAL DEFAULT 0.0"),
        ("taxable_amount", "REAL DEFAULT 0.0"),
        ("client_name", "TEXT DEFAULT ''"),
        ("client_address", "TEXT DEFAULT ''"),
        ("client_contact", "TEXT DEFAULT ''"),
        ("amount_in_words", "TEXT DEFAULT ''")
    ]
}

def migrate_db(db_path):
    print("=" * 60)
    print(f"Migrating: {db_path}")
    if not os.path.exists(db_path):
        print("  File not found!")
        return

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Ensure tables exist
    for table, cols in MIGRATIONS.items():
        # Check if table exists
        exists = cur.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'").fetchone()
        if not exists:
            print(f"  Table '{table}' does not exist, skipping column additions.")
            continue

        existing_cols = [r[1].lower() for r in cur.execute(f"PRAGMA table_info({table})").fetchall()]
        added = 0
        for col_name, col_def in cols:
            if col_name.lower() not in existing_cols:
                sql = f"ALTER TABLE {table} ADD COLUMN {col_name} {col_def}"
                try:
                    cur.execute(sql)
                    added += 1
                except Exception as e:
                    print(f"    Error adding {col_name} to {table}: {e}")
        print(f"  Table '{table}': added {added} new columns.")

    # Ensure reports table exists with rich structure
    cur.execute("""
        CREATE TABLE IF NOT EXISTS business_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            workspace_id TEXT DEFAULT 'SSC',
            report_type TEXT,
            title TEXT,
            period_label TEXT,
            date_range TEXT,
            generated_at TEXT,
            summary TEXT,
            executive_summary TEXT,
            detailed_tables_json TEXT DEFAULT '[]',
            charts_json TEXT DEFAULT '{}',
            key_metrics_json TEXT DEFAULT '{}',
            pending_actions_json TEXT DEFAULT '[]',
            status TEXT DEFAULT 'Completed',
            error_message TEXT DEFAULT '',
            author_id INTEGER DEFAULT 1
        );
    """)
    print("  Ensured 'business_reports' table exists.")

    conn.commit()
    conn.close()
    print("Migration successful.")

if __name__ == "__main__":
    for p in DB_PATHS:
        migrate_db(p)
