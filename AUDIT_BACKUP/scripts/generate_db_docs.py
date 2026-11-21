import sqlite3
from pathlib import Path

repo_root = Path("C:/Users/HP/Desktop/ssc_marketing_managing")
db_path = repo_root / "data" / "sgcc_foundation.sqlite"
conn = sqlite3.connect(str(db_path))
cur = conn.cursor()

tables = cur.execute("SELECT name, sql FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()

doc = ["# SHAH Group AI OS — Database Schema Reference", ""]
doc.append(f"**Database File**: `data/sgcc_foundation.sqlite`")
doc.append(f"**Total Tables**: {len(tables)}")
doc.append("")
doc.append("## Table Summary")
doc.append("| Table Name | Row Count | Primary Purpose |")
doc.append("|------------|-----------|-----------------|")

for name, sql in tables:
    if name == "sqlite_sequence":
        continue
    try:
        cnt = cur.execute(f"SELECT COUNT(*) FROM [{name}]").fetchone()[0]
    except Exception:
        cnt = "?"
    doc.append(f"| `{name}` | {cnt} | System / Domain table |")

doc.append("")
doc.append("## Detailed Table Schemas")

for name, sql in tables:
    doc.append(f"### `{name}`")
    try:
        cols = cur.execute(f"PRAGMA table_info([{name}])").fetchall()
        doc.append("| cid | Column Name | Type | Not Null | Default Value | Primary Key |")
        doc.append("|-----|-------------|------|----------|---------------|-------------|")
        for col in cols:
            doc.append(f"| {col[0]} | `{col[1]}` | {col[2]} | {col[3]} | {col[4]} | {col[5]} |")
    except Exception as e:
        doc.append(f"Error fetching columns: {e}")
    doc.append("")
    doc.append("```sql")
    doc.append(sql or "")
    doc.append("```")
    doc.append("")

conn.close()

(repo_root / "DATABASE_SCHEMA.md").write_text("\n".join(doc), encoding="utf-8")
print("DATABASE_SCHEMA.md generated successfully.")
