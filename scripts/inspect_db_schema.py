import sqlite3

for db_path in ['data/sgcc_foundation.sqlite', 'data/business_os.db']:
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [r[0] for r in cur.fetchall()]
        print(f"\n--- {db_path} ({len(tables)} tables) ---")
        print(tables)
        if 'users' in tables:
            cur.execute("SELECT id, username, role_id, workspace_id, active FROM users")
            users = cur.fetchall()
            print("Users:", users)
    except Exception as e:
        print(f"Error {db_path}: {e}")
