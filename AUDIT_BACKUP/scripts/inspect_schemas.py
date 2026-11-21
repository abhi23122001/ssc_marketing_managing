import sqlite3

conn = sqlite3.connect('C:/Users/HP/Desktop/ssc_marketing_managing/data/sgcc_foundation.sqlite')
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
all_tables = [r[0] for r in cur.fetchall()]
print("All tables:", all_tables)

for t in all_tables:
    if 'client' in t:
        cur.execute(f"PRAGMA table_info({t})")
        cols = [r[1] for r in cur.fetchall()]
        print(f"Match '{t}': {', '.join(cols)}")
