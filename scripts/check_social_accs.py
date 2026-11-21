import sqlite3
conn = sqlite3.connect('C:/Users/HP/Desktop/ssc_marketing_managing/data/sgcc_foundation.sqlite')
cur = conn.cursor()
cur.execute("PRAGMA table_info(social_accounts)")
print("social_accounts:", [r[1] for r in cur.fetchall()])
cur.execute("SELECT * FROM social_accounts")
print("rows:", cur.fetchall())
