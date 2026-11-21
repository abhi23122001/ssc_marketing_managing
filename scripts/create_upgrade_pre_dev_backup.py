# scripts/create_upgrade_pre_dev_backup.py
import os, sys, shutil, sqlite3, hashlib, json, time, subprocess
from pathlib import Path

repo_root = Path("C:/Users/HP/Desktop/ssc_marketing_managing").resolve()
backup_dir = repo_root / "backups" / "antigravity_2026-11-21_upgrade_baseline"
backup_dir.mkdir(parents=True, exist_ok=True)

print(f"=== CREATING PRE-UPGRADE VERIFIED BACKUP IN: {backup_dir} ===")

# 1. Transactional SQLite online backup
db_src = repo_root / "data" / "sgcc_foundation.sqlite"
db_dst_dir = backup_dir / "data"
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
    print(f"[PASS] Pre-upgrade SQLite backup verified: PRAGMA integrity_check = '{res}'.")
    dst_conn.close()
    src_conn.close()

# Copy CSVs in data/ and data/sheets_sync/
for f in (repo_root / "data").glob("*.csv"):
    shutil.copy2(f, db_dst_dir / f.name)

sync_src = repo_root / "data" / "sheets_sync"
sync_dst = db_dst_dir / "sheets_sync"
if sync_src.exists():
    shutil.copytree(sync_src, sync_dst, dirs_exist_ok=True)
print("[PASS] Pre-upgrade database and CSV mirrors backed up.")

# 2. Backup code directories
dirs_to_copy = ["foundation", "modules", "shared", "scripts", "tests", "docs", "brand", "config"]
for d in dirs_to_copy:
    src_d = repo_root / d
    if src_d.exists():
        dst_d = backup_dir / d
        shutil.copytree(src_d, dst_d, dirs_exist_ok=True)

# Copy root md and ps1 files
for f in repo_root.glob("*.md"):
    shutil.copy2(f, backup_dir / f.name)
for f in repo_root.glob("*.ps1"):
    shutil.copy2(f, backup_dir / f.name)

# 3. Generate SHA-256 Manifest
manifest = {
    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    "upgrade_phase": "pre-upgrade-baseline",
    "git_commit": "bd05bde4dac6e887c7f4f76cf65ec7feadf06d87",
    "git_branch": "main",
    "database_integrity": "ok",
    "files": {}
}

checksum_lines = []
for root, _, files in os.walk(backup_dir):
    for fn in files:
        if fn in ["MANIFEST.json", "checksums.sha256"]:
            continue
        fp = Path(root) / fn
        rel = fp.relative_to(backup_dir).as_posix()
        h = hashlib.sha256()
        with open(fp, "rb") as bf:
            while chunk := bf.read(65536):
                h.update(chunk)
        digest = h.hexdigest()
        manifest["files"][rel] = digest
        checksum_lines.append(f"{digest}  {rel}")

with open(backup_dir / "MANIFEST.json", "w", encoding="utf-8") as mf:
    json.dump(manifest, mf, indent=2)

with open(backup_dir / "checksums.sha256", "w", encoding="utf-8") as cf:
    cf.write("\n".join(sorted(checksum_lines)) + "\n")

print(f"[PASS] Pre-upgrade backup created successfully: {len(manifest['files'])} files indexed with SHA-256.")
