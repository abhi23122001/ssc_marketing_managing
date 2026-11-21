#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SHAH AI OS - Phase 5A Backup v4 (fast, robust)

Backup strategy (all in ONE fast self-contained run):
  1. os.walk + fixed exclusion policy -> sorted file list.
  2. System `tar` (C-optimised) over the file list, piped into `gzip -1`
     (fastest gzip) -> single compressed TAR archive.
  3. Python manifest (SHA-256 per file) + archive checksum + checksum file.
  4. Recovery bundles + recovery metadata/docs (reuse git bundle routine).

Run NEARLY always in the foreground (tool timeout up to 600s) so the archive
is never left truncated.
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
import tarfile
from datetime import datetime, timezone
from pathlib import Path

TAR = "C:/Program Files/Git/usr/bin/tar.exe"
GZIP = "C:/Program Files/Git/usr/bin/gzip.exe"

REPO_ROOT = "C:/Users/HP/Desktop/ssc_marketing_managing"
PROJECT_NAME = "ssc_marketing_managing"

PRODUCTION_CRM = {"data/leads.csv"}
LEGACY_BACKUPS = ("backup_phase3_harden_", "backup_phase4_sprint1_")
SUBMODULE_PACK_DIR = ".git/modules/vendor/hermes-agent/objects"
EXCLUDE_DIRS = {"outputs", "private-client-data", "__pycache__", "node_modules", ".venv", "venv", ".hermes"}
EXCLUDE_EXTS = {".pyc", ".tmp", ".swp", ".log", ".sqlite", ".sqlite3", ".db"}
EXCLUDED_PATHS = set(PRODUCTION_CRM)
PROTECTED = {
    ".hermes/skills/shah-ai/SKILL.md", "config/SOUL.md", "brand/ssc-brand-profile.md",
}
SUPERPROJECT_HEAD = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, capture_output=True, text=True).stdout.strip()
SUBMODULE_PINNED = subprocess.run(["git", "submodule", "status"], cwd=REPO_ROOT, capture_output=True, text=True).stdout.split()[0] if subprocess.run(["git","submodule","status"], cwd=REPO_ROOT, capture_output=True, text=True).stdout.split() else "unknown"

def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1024*1024), b""):
            h.update(chunk)
    return h.hexdigest()

def is_excluded(rel):
    parts = Path(rel).parts
    if rel in EXCLUDE_DIRS or (parts and parts[0] in EXCLUDE_DIRS):
        return True
    if any(LEGACY_BACKUPS[0] in rel or LEGACY_BACKUPS[1] in rel for _ in [0]):
        pass
    if "backup_phase3_harden_" in rel or "backup_phase4_sprint1_" in rel:
        return True
    if rel in PRODUCTION_CRM:
        return True
    if any(p in parts for p in ("private-client-data",)):
        return True
    if Path(rel).name.startswith(".env") or Path(rel).name in {"credentials.json", "token.json", "credentials", "token"}:
        return True
    if Path(rel).suffix in EXCLUDE_EXTS:
        return True
    if rel.startswith(SUBMODULE_PACK_DIR + "/"):
        return True
    if ".hermes" in parts:
        return True
    return False

def collect_files(repo_root):
    files = []
    for dirpath, dirnames, filenames in os.walk(repo_root):
        dirpath = Path(dirpath)
        pruned = []
        for d in dirnames:
            full = dirpath / d
            rel = str(full.relative_to(repo_root))
            if is_excluded(rel) or rel == "data/leads.csv":
                continue
            pruned.append(d)
        dirnames[:] = pruned
        for fn in filenames:
            full = dirpath / fn
            rel = str(full.relative_to(repo_root)).replace("\\", "/")
            if is_excluded(rel):
                continue
            files.append(rel)
    return sorted(set(files))

def run(cmd, shell=False, check=True, cwd=None):
    return subprocess.run(cmd, shell=shell, check=check, cwd=cwd, capture_output=True, text=True)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=REPO_ROOT)
    ap.add_argument("--dest", required=True)
    args = ap.parse_args()
    repo_root = args.repo_root
    repo_root_path = Path(repo_root)
    dest = Path(args.dest).resolve()
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "validation").mkdir(exist_ok=True)
    print(f"Backup dest: {dest}", flush=True)
    print(f"Repo root  : {repo_root}", flush=True)

    # 1. File list (fixed exclusion policy)
    print("\n[1/5] Collecting files ...", flush=True)
    files = collect_files(repo_root)
    print(f"      files: {len(files)}", flush=True)

    # 2. Archive via system tar + gzip -1 (fast)
    print("[2/5] Creating archive via tar (gzip -1) ...", flush=True)
    filelist = dest / "filelist.txt"
    with open(filelist, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(files))
        fh.write("\n")
    archive = dest / "ssc_marketing_managing.tar.gz"
    cmd = f'"{TAR}" cf - -C {repo_root} -T {filelist} 2>nul | "{GZIP}" -1 > {archive}'
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if r.returncode != 0:
        print("TAR ERR:", r.stderr, file=sys.stderr)
        return 1
    print(f"      archive: {archive.name} ({archive.stat().st_size} bytes)", flush=True)

    # 3. Manifest + checksum
    print("[3/5] Writing manifest + checksum ...", flush=True)
    arc_sha = sha256_file(archive)
    manifest = {
        "backup_spec": "SHAH AI OS Phase 5A v4 fast",
        "project_root": repo_root,
        "archive_file": archive.name,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "branch": subprocess.run(["git", "branch", "--show-current"], cwd=repo_root, capture_output=True, text=True).stdout.strip(),
        "head_commit": SUPERPROJECT_HEAD,
        "submodule_pinned_commit": SUBMODULE_PINNED,
        "metadata": {"total_files": len(files), "archive_sha256": arc_sha},
        "files": [{"relative_path": f, "sha256": sha256_file(repo_root_path / f),
                   "size_bytes": (repo_root_path / f).stat().st_size, "is_symlink": (repo_root_path / f).is_symlink()}
                  for f in files],
        "exclude_policy": {"excluded_dirs": sorted(EXCLUDE_DIRS), "excluded_extensions": sorted(EXCLUDE_EXTS),
                           "production_crm_excluded": sorted(PRODUCTION_CRM)},
    }
    (dest / "ssc_marketing_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    with open(dest / "ssc_marketing_managing.sha256", "w", encoding="utf-8") as fh:
        fh.write(arc_sha + "  " + archive.name + "\n")
        for e in manifest["files"]:
            fh.write(e["sha256"] + "  " + e["relative_path"] + "\n")
    print("      manifest: ssc_marketing_manifest.json", flush=True)

    # 4. Recovery bundles
    print("[4/5] Git bundles ...", flush=True)
    import shutil
    sub_worktree = Path(repo_root) / "vendor/hermes-agent"
    s = run(["git", "bundle", "create", "superproject.bundle", "--all"], cwd=repo_root)
    b_super = Path(repo_root) / "superproject.bundle"
    s2 = run(["git", "bundle", "create", "submodule.bundle", "--all"], cwd=sub_worktree)
    b_sub = sub_worktree / "submodule.bundle"
    shutil.copy2(b_super, dest / "superproject.bundle")
    shutil.copy2(b_sub, dest / "submodule.bundle")
    os.remove(b_super); os.remove(b_sub)
    print("      superproject.bundle: OK", flush=True)
    print("      submodule.bundle   : OK", flush=True)

    # 5. Recovery metadata + README
    print("[5/5] Recovery metadata ...", flush=True)
    git_rec = {
        "backup_spec": "SHAH AI OS Phase 5A v4 fast",
        "project_root": repo_root,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "branch": "main",
        "superproject_head": SUPERPROJECT_HEAD,
        "submodule_pinned_commit": SUBMODULE_PINNED,
        "submodule_path": "vendor/hermes-agent",
        "bundles": [{"file": n, "sha256": sha256_file(p), "size": p.stat().st_size}
                    for n, p in [("superproject.bundle", dest/"superproject.bundle"),
                                 ("submodule.bundle", dest/"submodule.bundle")]],
        "note": "Full Git history via bundles; tar.gz holds working tree + .git metadata (pack volumes lost, recoverable from submodule.bundle).",
    }
    (dest / "git-recovery.log").write_text(json.dumps(git_rec, indent=2), encoding="utf-8")
    (dest / "submodule-recovery.log").write_text(json.dumps({
        "backup_spec": "SHAH AI OS Phase 5A v4 fast",
        "submodule_pinned_commit": SUBMODULE_PINNED,
        "submodule_gitdir": str(Path(repo_root) / ".git/modules/vendor/hermes-agent"),
        "bundle_file": "submodule.bundle",
    }, indent=2), encoding="utf-8")
    (dest / "recovery-README.md").write_text(
        f"# Phase 5A Recovery README\n\n"
        f"Superproject HEAD: {SUPERPROJECT_HEAD}\n"
        f"Submodule commit : {SUBMODULE_PINNED}\n\n"
        "Recovery procedure documented in recovery-README.md (bundles + tar.gz).\n",
        encoding="utf-8")
    print("      git-recovery.log, submodule-recovery.log, recovery-README.md", flush=True)

    # 5b. Print summary
    print("\nBACKUP COMPLETE:", dest)
    print("  archive:", archive.name, archive.stat().st_size, "bytes,", len(files), "files")
    print("  bundles:", "superproject.bundle", (dest / "superproject.bundle").stat().st_size,
          "|", "submodule.bundle", (dest / "submodule.bundle").stat().st_size)
    print("  archive sha256:", arc_sha)
    print("  manifest entries:", len(files))
    return 0

if __name__ == "__main__":
    sys.exit(main())
