import sqlite3

for db_path in ['data/sgcc_foundation.sqlite', 'data/business_os.db']:
    print('='*50)
    print(f'DB: {db_path}')
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    tables = cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;").fetchall()
    for t in tables:
        tname = t[0]
        cnt = cur.execute(f'SELECT COUNT(*) FROM "{tname}"').fetchone()[0]
        print(f'  {tname}: {cnt} rows')
    conn.close()
