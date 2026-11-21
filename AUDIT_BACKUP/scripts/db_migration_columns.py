import sqlite3

conn = sqlite3.connect('C:/Users/HP/Desktop/ssc_marketing_managing/data/sgcc_foundation.sqlite')
cur = conn.cursor()

def add_col_if_missing(table, col, defn):
    cur.execute(f"PRAGMA table_info({table})")
    cols = [r[1] for r in cur.fetchall()]
    if col not in cols:
        print(f"Adding {col} to {table}...")
        cur.execute(f"ALTER TABLE {table} ADD COLUMN {col} {defn}")
        conn.commit()
    else:
        print(f"{table}.{col} already exists.")

add_col_if_missing('sites', 'status', "TEXT DEFAULT 'active'")
add_col_if_missing('social_client_profiles', 'workspace_id', "TEXT DEFAULT 'SSC'")

print("Migration completed.")
