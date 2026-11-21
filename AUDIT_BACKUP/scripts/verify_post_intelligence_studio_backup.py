import os, sys, shutil, sqlite3, hashlib, json
from pathlib import Path

backup_dir = Path(r"C:\Users\HP\Desktop\ssc_marketing_managing\backups\antigravity_2026-11-21_pre_creative_studio")
restore_dir = Path(r"C:\temp\antigravity_restore_pre_studio")
if restore_dir.exists():
    shutil.rmtree(restore_dir)
restore_dir.mkdir(parents=True, exist_ok=True)

with open(backup_dir / "manifest.json") as f:
    manifest = json.load(f)

mismatches = 0
for rel, h in manifest["files"].items():
    src_f = backup_dir / rel
    dst_f = restore_dir / rel
    dst_f.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src_f, dst_f)
    with open(dst_f, "rb") as bf:
        if hashlib.sha256(bf.read()).hexdigest() != h:
            mismatches += 1

print(f"Restored {len(manifest['files'])} files, mismatches: {mismatches}")
db_p = restore_dir / "data" / "sgcc_foundation.sqlite"
conn = sqlite3.connect(str(db_p))
check = conn.execute("PRAGMA integrity_check").fetchone()[0]
table_count = conn.execute("SELECT count(tbl_name) FROM sqlite_master WHERE type='table'").fetchone()[0]
conn.close()
print(f"SQLite integrity_check: {check}, table count: {table_count}")
if mismatches == 0 and check == "ok":
    print("RESTORE VERIFICATION SUCCESS: 100% MATCH")
else:
    print("RESTORE VERIFICATION FAILED")
    sys.exit(1)
