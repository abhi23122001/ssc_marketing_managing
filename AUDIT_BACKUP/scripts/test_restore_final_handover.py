# scripts/test_restore_final_handover.py
import os, sys, shutil, sqlite3, hashlib, json
from pathlib import Path

repo_root = Path("C:/Users/HP/Desktop/ssc_marketing_managing").resolve()
backup_dir = repo_root / "backups" / "antigravity_2026-11-21_final_production_handover"
restore_dir = repo_root / "test_restore_final"

print(f"=== TESTING OUT-OF-PLACE RESTORE TO: {restore_dir} ===")

if not backup_dir.exists():
    print(f"FAIL: Backup directory does not exist: {backup_dir}")
    sys.exit(1)

# Clean restore dir
if restore_dir.exists():
    shutil.rmtree(restore_dir)
restore_dir.mkdir(parents=True, exist_ok=True)

# 1. Read manifest
manifest_path = backup_dir / "manifest.json"
with open(manifest_path, "r", encoding="utf-8") as f:
    manifest = json.load(f)

print(f"Manifest loaded: {len(manifest['files'])} files recorded.")

# 2. Copy files out-of-place
for rel_path in manifest["files"]:
    src_file = backup_dir / rel_path
    dst_file = restore_dir / rel_path
    dst_file.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src_file, dst_file)

# 3. Verify SHA-256 checksums
print("Verifying SHA-256 checksums on all restored files...")
mismatch_count = 0
verified_count = 0

for rel_path, expected_hash in manifest["files"].items():
    restored_file = restore_dir / rel_path
    if not restored_file.exists():
        print(f"FAIL: Missing restored file: {rel_path}")
        mismatch_count += 1
        continue
    with open(restored_file, "rb") as bf:
        actual_hash = hashlib.sha256(bf.read()).hexdigest()
    if actual_hash != expected_hash:
        print(f"FAIL: Hash mismatch on {rel_path}: expected {expected_hash}, got {actual_hash}")
        mismatch_count += 1
    else:
        verified_count += 1

print(f"[PASS] {verified_count}/{len(manifest['files'])} file checksums matched perfectly.")
assert mismatch_count == 0, f"Total checksum mismatches: {mismatch_count}"

# 4. Verify SQLite database integrity in restored location
restored_db = restore_dir / "data" / "sgcc_foundation.sqlite"
assert restored_db.exists(), "Restored SQLite database not found!"

conn = sqlite3.connect(str(restored_db))
cur = conn.cursor()
cur.execute("PRAGMA integrity_check")
res = cur.fetchone()[0]
assert res.lower() == "ok", f"Restored DB integrity check failed: {res}"
print(f"[PASS] Restored SQLite database verified: PRAGMA integrity_check = '{res}'.")

# 5. Check row counts on critical tables in restored database
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in cur.fetchall()]
print(f"[PASS] Restored database contains {len(tables)} tables.")

for t in ["users", "sites", "social_leads", "social_client_profiles", "employee_tasks", "attendance_logs"]:
    if t in tables:
        cur.execute(f"SELECT COUNT(*) FROM {t}")
        cnt = cur.fetchone()[0]
        print(f"  Table [{t}]: {cnt} records")

conn.close()

# Cleanup test restore directory after verified success
shutil.rmtree(restore_dir)
print("[PASS] Test restore directory cleaned up.")

print("\n============================================================")
print("OUT-OF-PLACE RESTORE TEST COMPLETED: 100% PASS")
print("============================================================")
