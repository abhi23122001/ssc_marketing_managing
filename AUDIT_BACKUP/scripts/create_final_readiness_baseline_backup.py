import os, sys, shutil, sqlite3, hashlib, json, time, subprocess
from pathlib import Path

repo_root = Path("C:/Users/HP/Desktop/ssc_marketing_managing").resolve()
backup_dir = repo_root / "backups" / "antigravity_2026-11-21_final_readiness_baseline"
backup_dir.mkdir(parents=True, exist_ok=True)

print("Creating Final Readiness Baseline Milestone backup at:", backup_dir)

# 1. Backup SQLite database transactionally via online backup API
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
    "MANUAL_TESTING_GUIDE.md", "ANTIGRAVITY_FINAL_HANDOVER.md",
    "PROJECT_MASTER_INVENTORY.md", "IMPLEMENTATION_GAP_REPORT.md",
    "INSTALLATION_GUIDE.md", "FINAL_ACCEPTANCE_REPORT.md",
    "FINAL_PROJECT_HANDOVER.md", "NEXT_PHASE_ROADMAP.md",
    "POST_INTELLIGENCE_STUDIO_HANDOVER.md"
]
for f in files_to_copy:
    src_f = repo_root / f
    if src_f.exists():
        shutil.copy2(src_f, backup_dir / f)

# 3. Record git state and manifest
try:
    git_commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=repo_root).stdout.strip()
    git_branch = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True, text=True, cwd=repo_root).stdout.strip()
except Exception:
    git_commit = "unknown"
    git_branch = "unknown"

manifest = {
    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    "backup_name": "antigravity_2026-11-21_final_readiness_baseline",
    "git_commit": git_commit,
    "git_branch": git_branch,
    "files": {}
}

total_files = 0
for root, _, files in os.walk(backup_dir):
    for f in files:
        if f == "manifest.json" or f == "checksums.sha256":
            continue
        fp = Path(root) / f
        rel = fp.relative_to(backup_dir).as_posix()
        with open(fp, "rb") as bf:
            h = hashlib.sha256(bf.read()).hexdigest()
        manifest["files"][rel] = h
        total_files += 1

with open(backup_dir / "manifest.json", "w") as mf:
    json.dump(manifest, mf, indent=2)

with open(backup_dir / "checksums.sha256", "w") as cf:
    for rel, h in sorted(manifest["files"].items()):
        cf.write(f"{h}  {rel}\n")

print(f"Manifest created with {total_files} files verified.")
print("Final Readiness Baseline milestone backup completed successfully.")
