import os, sys, shutil, sqlite3, hashlib, json, time, subprocess
from pathlib import Path

repo_root = Path("C:/Users/HP/Desktop/ssc_marketing_managing").resolve()
backup_dir = repo_root / "backups" / "antigravity_2026-11-20_post_hardening"
backup_dir.mkdir(parents=True, exist_ok=True)

print("Creating post-hardening backup at:", backup_dir)

# 1. Backup SQLite database transactionally
db_src = repo_root / "data" / "sgcc_foundation.sqlite"
db_dst_dir = backup_dir / "data"
db_dst_dir.mkdir(parents=True, exist_ok=True)
db_dst = db_dst_dir / "sgcc_foundation.sqlite"

if db_src.exists():
    src_conn = sqlite3.connect(str(db_src))
    dst_conn = sqlite3.connect(str(db_dst))
    src_conn.backup(dst_conn)
    dst_conn.close()
    src_conn.close()
    print("SQLite database backed up via online backup API.")

# Copy CSVs in data/
for f in (repo_root / "data").glob("*.csv"):
    shutil.copy2(f, db_dst_dir / f.name)
print("Data CSVs backed up.")

# 2. Backup code directories
dirs_to_copy = ["foundation", "modules", "shared", "scripts", "tests", "docs", "brand", "config"]
for d in dirs_to_copy:
    src_d = repo_root / d
    if src_d.exists():
        dst_d = backup_dir / d
        if dst_d.exists():
            shutil.rmtree(dst_d)
        shutil.copytree(src_d, dst_d, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache"))
        print(f"Backed up directory: {d}")

# Copy root documentation and script files
files_to_copy = [
    "Start-SHAI-Center.ps1", "Start-SHAI-Backup.ps1", "Start-SHAI-Restore-Test.ps1",
    "COMMAND-CENTER.md", "AGENTS.md", ".gitignore",
    "PROJECT_ARCHITECTURE.md", "MODULE_STATUS.md", "DEVELOPMENT_LOG.md",
    "KNOWN_ISSUES.md", "TEST_RESULTS.md", "API_ENDPOINTS.md",
    "DATABASE_SCHEMA.md", "SECURITY_AUDIT.md", "BACKUP_LOG.md",
    "MANUAL_TESTING_GUIDE.md"
]
for f in files_to_copy:
    src_f = repo_root / f
    if src_f.exists():
        shutil.copy2(src_f, backup_dir / f)

# 3. Record git state and manifest
git_commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=repo_root).stdout.strip()
git_branch = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True, text=True, cwd=repo_root).stdout.strip()

manifest = {
    "backup_name": "antigravity_2026-11-20_post_hardening",
    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "git_commit": git_commit,
    "git_branch": git_branch,
    "files": {}
}

for root, _, files in os.walk(backup_dir):
    for f in files:
        if f == "backup_manifest.json":
            continue
        fp = Path(root) / f
        rel = fp.relative_to(backup_dir).as_posix()
        sha = hashlib.sha256(fp.read_bytes()).hexdigest()
        manifest["files"][rel] = {
            "size": fp.stat().st_size,
            "sha256": sha
        }

with open(backup_dir / "backup_manifest.json", "w", encoding="utf-8") as mf:
    json.dump(manifest, mf, indent=2)

print("Backup complete:", len(manifest["files"]), "files indexed.")

# 4. Out-of-place restore verification
restore_dir = Path("C:/temp/antigravity_restore_test_post_hardening")
if restore_dir.exists():
    shutil.rmtree(restore_dir)
restore_dir.mkdir(parents=True, exist_ok=True)

failures = 0
for rel, info in manifest["files"].items():
    src_f = backup_dir / rel
    dst_f = restore_dir / rel
    dst_f.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src_f, dst_f)
    if hashlib.sha256(dst_f.read_bytes()).hexdigest() != info["sha256"]:
        failures += 1

restored_db = restore_dir / "data" / "sgcc_foundation.sqlite"
conn = sqlite3.connect(str(restored_db))
cur = conn.cursor()
tbl_count = cur.execute("SELECT count(*) FROM sqlite_master WHERE type='table'").fetchone()[0]
user_count = cur.execute("SELECT count(*) FROM users").fetchone()[0]
conn.close()

if failures == 0 and tbl_count > 0:
    print("RESTORE VERIFICATION: PASS (0 mismatches,", tbl_count, "tables,", user_count, "users)")
    shutil.rmtree(restore_dir)
else:
    print("RESTORE VERIFICATION: FAIL")
    sys.exit(1)
