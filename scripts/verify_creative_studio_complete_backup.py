import os, sys, shutil, sqlite3, hashlib, json
from pathlib import Path

repo_root = Path("C:/Users/HP/Desktop/ssc_marketing_managing").resolve()
backup_dir = repo_root / "backups" / "antigravity_2026-11-21_creative_studio_complete"
restore_temp_dir = Path("C:/temp/antigravity_restore_creative_studio_complete")

print("=== STARTING ISOLATED OUT-OF-PLACE RESTORE VERIFICATION ===")
print("Backup source:", backup_dir)
print("Restore target:", restore_temp_dir)

if restore_temp_dir.exists():
    shutil.rmtree(restore_temp_dir)
restore_temp_dir.mkdir(parents=True, exist_ok=True)

# 1. Read manifest and checksums
with open(backup_dir / "manifest.json", "r") as f:
    manifest = json.load(f)

expected_files = manifest["files"]
print(f"Manifest loaded: {len(expected_files)} files recorded.")

# 2. Copy files to restore temp directory
for rel_path in expected_files:
    src_file = backup_dir / rel_path
    dst_file = restore_temp_dir / rel_path
    dst_file.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src_file, dst_file)

print("All files restored out-of-place.")

# 3. Checksum verification
mismatches = 0
for rel_path, expected_hash in expected_files.items():
    restored_file = restore_temp_dir / rel_path
    if not restored_file.exists():
        print(f"MISSING: {rel_path}")
        mismatches += 1
        continue
    with open(restored_file, "rb") as f:
        actual_hash = hashlib.sha256(f.read()).hexdigest()
    if actual_hash != expected_hash:
        print(f"HASH MISMATCH: {rel_path}")
        mismatches += 1

if mismatches == 0:
    print(f"[PASS] 100% Checksum Verification ({len(expected_files)} files match SHA-256).")
else:
    print(f"[FAIL] {mismatches} file mismatches detected.")
    sys.exit(1)

# 4. SQLite integrity check
restored_db = restore_temp_dir / "data" / "sgcc_foundation.sqlite"
if restored_db.exists():
    conn = sqlite3.connect(str(restored_db))
    cursor = conn.cursor()
    cursor.execute("PRAGMA integrity_check;")
    res = cursor.fetchone()
    print("SQLite integrity check result:", res)
    cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='table';")
    table_count = cursor.fetchone()[0]
    print(f"Restored SQLite contains {table_count} tables.")
    conn.close()
    if res and res[0] == "ok":
        print("[PASS] SQLite integrity verified: OK")
    else:
        print("[FAIL] SQLite integrity check failed")
        sys.exit(1)

print("\n=== ISOLATED RESTORE VERIFICATION SUCCESS: 100% PASS ===")
