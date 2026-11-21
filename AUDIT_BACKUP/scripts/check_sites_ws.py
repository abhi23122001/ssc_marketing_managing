import sqlite3
conn = sqlite3.connect('C:/Users/HP/Desktop/ssc_marketing_managing/data/sgcc_foundation.sqlite')
cur = conn.cursor()
cur.execute("SELECT id, workspace_id, code, name FROM sites WHERE code LIKE '%INF%'")
print(cur.fetchall())
