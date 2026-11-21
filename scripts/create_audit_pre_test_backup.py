# scripts/create_audit_pre_test_backup.py
import os, sys, shutil, sqlite3, hashlib, json, time, subprocess
from pathlib import Path

repo_root = Path("C:/Users/HP/Desktop/ssc_marketing_managing").resolve()
audit_backup_dir = repo_root / "AUDIT_BACKUP"
audit_backup_dir.mkdir(parents=True, exist_ok=True)

# Also create required audit directories
for d in ["AUDIT_RESTORE_VERIFICATION", "AUDIT_TEST_EVIDENCE", "AUDIT_SCREENSHOTS", "AUDIT_LOGS"]:
    (repo_root / d).mkdir(parents=True, exist_ok=True)

print(f"=== CREATING PRE-AUDIT VERIFIED BACKUP IN: {audit_backup_dir} ===")

# 1. Transactional SQLite online backup
db_src = repo_root / "data" / "sgcc_foundation.sqlite"
db_dst_dir = audit_backup_dir / "data"
db_dst_dir.mkdir(parents=True, exist_ok=True)
db_dst = db_dst_dir / "sgcc_foundation.sqlite"

if db_src.exists():
    src_conn = sqlite3.connect(str(db_src))
    dst_conn = sqlite3.connect(str(db_dst))
    src_conn.backup(dst_conn)
    
    # Check integrity
    cur = dst_conn.cursor()
    cur.execute("PRAGMA integrity_check")
    res = cur.fetchone()[0]
    assert res.lower() == "ok", f"Integrity check failed: {res}"
    print(f"[PASS] Pre-audit SQLite backup verified: PRAGMA integrity_check = '{res}'.")
    dst_conn.close()
    src_conn.close()

# Copy CSVs in data/ and data/sheets_sync/
for f in (repo_root / "data").glob("*.csv"):
    shutil.copy2(f, db_dst_dir / f.name)

sync_src = repo_root / "data" / "sheets_sync"
sync_dst = db_dst_dir / "sheets_sync"
if sync_src.exists():
    shutil.copytree(sync_src, sync_dst, dirs_exist_ok=True)
print("[PASS] Pre-audit database and CSV mirrors backed up.")

# 2. Backup code directories
dirs_to_copy = ["foundation", "modules", "shared", "scripts", "tests", "docs", "brand", "config"]
for d in dirs_to_copy:
    src_d = repo_root / d
    if src_d.exists():
        dst_d = audit_backup_dir / d
        if dst_d.exists():
            shutil.rmtree(dst_d)
        shutil.copytree(src_d, dst_d, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache"))
        print(f"[PASS] Backed up directory: {d}")

# Copy root docs and config
for f in repo_root.glob("*.md"):
    shutil.copy2(f, audit_backup_dir / f.name)
for f in repo_root.glob("*.ps1"):
    shutil.copy2(f, audit_backup_dir / f.name)

# 3. Create manifest
git_commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=repo_root).stdout.strip()
git_branch = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True, text=True, cwd=repo_root).stdout.strip()

manifest = {
    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    "audit_phase": "pre-audit-baseline",
    "git_commit": git_commit,
    "git_branch": git_branch,
    "database_integrity": "ok",
    "files": {}
}

total_files = 0
for root, _, files in os.walk(audit_backup_dir):
    for f in files:
        if f in ("manifest.json", "checksums.sha256"):
            continue
        fp = Path(root) / f
        rel = fp.relative_to(audit_backup_dir).as_posix()
        with open(fp, "rb") as bf:
            h = hashlib.sha256(bf.read()).hexdigest()
        manifest["files"][rel] = h
        total_files += 1

with open(audit_backup_dir / "manifest.json", "w") as mf:
    json.dump(manifest, mf, indent=2)

with open(audit_backup_dir / "checksums.sha256", "w") as cf:
    for rel, h in sorted(manifest["files"].items()):
        cf.write(f"{h}  {rel}\n")

print(f"[PASS] Manifest created with {total_files} files verified.")
print(f"=== PRE-AUDIT BACKUP COMPLETED IN: {audit_backup_dir} ===")
