import sqlite3

conn = sqlite3.connect('data/sgcc_foundation.sqlite')
cur = conn.cursor()

tables = [
    'sites', 'employees', 'business_invoices', 'business_quotations',
    'business_estimates', 'business_payments', 'business_work_orders',
    'social_client_profiles', 'social_leads', 'expense_claims',
    'expense_vendors', 'leaves', 'attendance_logs', 'payroll_runs',
    'payslips', 'employee_tasks', 'ai_research_items', 'ai_marketing_briefs',
    'ai_tasks', 'approvals', 'social_content_items', 'social_campaigns',
    'studio_projects', 'task_comments', 'task_notifications'
]

for t in tables:
    cols = [c[1] for c in cur.execute(f'PRAGMA table_info("{t}")').fetchall()]
    count = cur.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0]
    sample = cur.execute(f'SELECT * FROM "{t}" LIMIT 2').fetchall()
    print(f"=== {t} ({count} rows) ===")
    print(f"  Cols: {cols}")
    if sample:
        print(f"  Sample: {sample[0]}")

conn.close()
