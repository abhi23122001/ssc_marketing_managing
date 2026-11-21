# scripts/audit_database.py
import sqlite3, json, os
from pathlib import Path

repo_root = Path("C:/Users/HP/Desktop/ssc_marketing_managing").resolve()
db_path = repo_root / "data" / "sgcc_foundation.sqlite"
evidence_dir = repo_root / "AUDIT_TEST_EVIDENCE"
evidence_dir.mkdir(parents=True, exist_ok=True)

print(f"Auditing Database: {db_path}")

conn = sqlite3.connect(str(db_path))
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# 1. Integrity check
cur.execute("PRAGMA integrity_check")
integrity = cur.fetchone()[0]

# 2. Journal mode
cur.execute("PRAGMA journal_mode")
journal_mode = cur.fetchone()[0]

# 3. Foreign keys
cur.execute("PRAGMA foreign_keys")
fk_status = cur.fetchone()[0]

# 4. Tables list
cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = [r[0] for r in cur.fetchall()]

table_counts = {}
for t in tables:
    try:
        cur.execute(f"SELECT COUNT(*) FROM [{t}]")
        table_counts[t] = cur.fetchone()[0]
    except Exception as e:
        table_counts[t] = f"Error: {e}"

# 5. Users audit (without passwords)
cur.execute("""
    SELECT u.id, u.username, u.name, r.code as role, u.workspace_id, u.active, u.created_at 
    FROM users u 
    LEFT JOIN roles r ON u.role_id = r.id 
    ORDER BY u.id
""")
users = [dict(r) for r in cur.fetchall()]

# 6. Roles audit
cur.execute("SELECT * FROM roles ORDER BY id")
roles = [dict(r) for r in cur.fetchall()]

# 7. Workspaces audit
cur.execute("SELECT * FROM workspaces ORDER BY id")
workspaces = [dict(r) for r in cur.fetchall()]

conn.close()

audit_result = {
    "database_path": str(db_path),
    "size_bytes": os.path.getsize(db_path),
    "integrity_check": integrity,
    "journal_mode": journal_mode,
    "foreign_keys": fk_status,
    "total_tables": len(tables),
    "tables": tables,
    "table_counts": table_counts,
    "users_count": len(users),
    "users": users,
    "roles": roles,
    "workspaces": workspaces
}

with open(evidence_dir / "database_audit.json", "w", encoding="utf-8") as f:
    json.dump(audit_result, f, indent=2)

print(f"[PASS] Database audit complete: {len(tables)} tables, integrity={integrity}, journal_mode={journal_mode}, users={len(users)}")
