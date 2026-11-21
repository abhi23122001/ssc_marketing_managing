import sqlite3
conn = sqlite3.connect('data/sgcc_foundation.sqlite')
c = conn.cursor()
c.execute('PRAGMA integrity_check')
print('INTEGRITY:', c.fetchone())
c.execute("SELECT count(*) FROM sqlite_master WHERE type='table'")
print('TABLES:', c.fetchone()[0])
conn.close()
