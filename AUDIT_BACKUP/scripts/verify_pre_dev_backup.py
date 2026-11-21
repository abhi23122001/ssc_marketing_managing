import os, sys, shutil, sqlite3, hashlib, json
from pathlib import Path

backup_dir = Path("C:/Users/HP/Desktop/ssc_marketing_managing/backups/antigravity_2026-11-20_pre_dev")
restore_dir = Path("C:/temp/antigravity_restore_test_20261120")

if restore_dir.exists():
    shutil.rmtree(restore_dir)
restore_dir.mkdir(parents=True, exist_ok=True)

manifest = json.loads((backup_dir / "backup_manifest.json").read_text(encoding="utf-8"))
failures = 0

for rel, info in manifest["files"].items():
    src_f = backup_dir / rel
    dst_f = restore_dir / rel
    dst_f.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src_f, dst_f)
    
    # verify sha
    calc_sha = hashlib.sha256(dst_f.read_bytes()).hexdigest()
    if calc_sha != info["sha256"]:
        print(f"CORRUPTION in {rel}")
        failures += 1

# Verify restored database opens and queries cleanly
restored_db = restore_dir / "data" / "sgcc_foundation.sqlite"
conn = sqlite3.connect(str(restored_db))
cur = conn.cursor()
tbl_count = cur.execute("SELECT count(*) FROM sqlite_master WHERE type='table'").fetchone()[0]
user_count = cur.execute("SELECT count(*) FROM users").fetchone()[0]
conn.close()

print(f"Restore verification complete: {len(manifest['files'])} files restored.")
print(f"Checksum mismatches: {failures}")
print(f"Restored DB check: {tbl_count} tables, {user_count} users verified.")

if failures == 0 and tbl_count > 0:
    print("RESTORE TEST RESULT: PASS")
    # Clean up temp restore directory
    shutil.rmtree(restore_dir)
else:
    print("RESTORE TEST RESULT: FAIL")
    sys.exit(1)
