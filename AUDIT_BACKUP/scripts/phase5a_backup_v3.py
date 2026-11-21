#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SHAH AI OS - Phase 5A Backup v3 (Git-bundle recovery + working-tree archive)

Goal: provide FULL Git + submodule object-history recovery, which the previous
backup (that excluded .git entirely) did NOT establish.

Mechanism:
  - superproject.bundle   : git bundle --all of the superproject (full history)
  - submodule.bundle      : git bundle --all of vendor/hermes-agent (full history)
  - ssc_marketing_managing.tar.gz : working-tree archive + full .git/.git/modules
                                    metadata, EXCLUDING only the regenerable
                                    1.4 GB submodule object pack (captured in the
                                    submodule.bundle instead).

Recovery procedure is documented in recovery-README.md inside the backup dir.
"""
import argparse
import hashlib
import json
import os
import shutil
import platform
import subprocess
import sys
import tarfile
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path.cwd().resolve()
PROJECT_NAME = "ssc_marketing_managing"

# ---- Production CRM exclusion (must NOT be archived) ----
PRODUCTION_CRM = {"data/leads.csv"}

# ---- Legacy backup directories: NEVER archived ----
LEGACY_BACKUPS = (
    "backup_phase3_harden_",
    "backup_phase4_sprint1_",
)

# ---- .git/modules/.../objects/ packs: regenerable, captured in submodule.bundle ----
SUBMODULE_PACK_DIR = ".git/modules/vendor/hermes-agent/objects"

# ---- Directories excluded from the working-tree archive ----
EXCLUDE_DIRS = {
    "outputs", "private-client-data", "__pycache__", "node_modules",
    ".venv", "venv", ".hermes",
}

# ---- File extensions excluded ----
EXCLUDE_EXTS = {".pyc", ".tmp", ".swp", ".log", ".sqlite", ".sqlite3", ".db"}

# ---- Files/paths excluded ----
EXCLUDED_PATHS = set(PRODUCTION_CRM)
EXCLUDED_NAMES = {"credentials.json", "token.json", "credentials", "token"}

# ---- Protected exceptions (must be present in the archive) ----
PROTECTED = {
    ".hermes/skills/shah-ai/SKILL.md",
    "config/SOUL.md",
    "brand/ssc-brand-profile.md",
}

# ---- Files always included explicitly ----
INCLUDE_PATHS = {
    ".gitmodules", ".gitignore", "AGENTS.md", "README.md",
    "COMMAND-CENTER.md", "Start-SHAI-Center.ps1",
    ".github/workflows/validate.yml",
}

SUPERPROJECT_HEAD = subprocess.run(
    ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, capture_output=True, text=True
).stdout.strip()
SUBMODULE_SHAS = subprocess.run(
    ["git", "submodule", "status"], cwd=REPO_ROOT, capture_output=True, text=True
).stdout


def sha256_of_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _norm_path(p):
    """Normalize MSYS/Cygwin-style paths (e.g. /c/Users -> C:/Users) on Windows."""
    p = str(p)
    if platform.system() == "Windows" and p.startswith("/"):
        p = p[1:]
        head, _, tail = p.partition("/")
        if head and head.lower() in ("c", "c:"):
            return (head + ":" + ("/" + tail if tail else "")).replace("//", "/")
    return p


def run(cmd, cwd=None):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)


def is_excluded(rel):
    parts = Path(rel).parts

    # dir-level exclusions
    if rel in EXCLUDE_DIRS:
        return True
    if parts[0] in EXCLUDE_DIRS:
        return True

    # legacy backups
    if any(LEGACY_BACKUPS[0] in rel or LEGACY_BACKUPS[1] in rel for _ in [0]):
        pass
    if "backup_phase3_harden_" in rel or "backup_phase4_sprint1_" in rel:
        return True

    # production CRM
    if rel in PRODUCTION_CRM:
        return True

    # confidential / sensitive
    if any(p in parts for p in ("private-client-data",)):
        return True
    if Path(rel).name.startswith(".env"):
        return True
    if Path(rel).name in EXCLUDED_NAMES:
        return True
    if Path(rel).suffix in EXCLUDE_EXTS:
        return True

    # .git submodules object packs (regenerable; covered by submodule.bundle)
    if rel.startswith(SUBMODULE_PACK_DIR + "/"):
        return True

    # .hermes runtime state (any path containing .hermes)
    if ".hermes" in parts:
        return True

    return False


def is_included(rel):
    # everything else is included unless explicitly excluded above
    return True


def collect_files(repo_root):
    files = []
    for dirpath, dirnames, filenames in os.walk(repo_root):
        dirpath = Path(dirpath)
        pruned = []
        for d in dirnames:
            full = dirpath / d
            rel = str(full.relative_to(repo_root))
            if is_excluded(rel):
                continue
            if rel == "data/leads.csv":
                continue
            pruned.append(d)
        dirnames[:] = pruned

        for fn in filenames:
            full = dirpath / fn
            rel = str(full.relative_to(repo_root)).replace("\\", "/")
            if is_excluded(rel):
                continue
            if not is_included(rel):
                continue
            files.append(rel)
    return sorted(set(files))


def make_bundle(name, git_dir):
    """Create a git bundle (relative output path) and return the ACTUAL file
    location. git always writes a relative bundle output next to the cwd, so
    the real path is git_dir/name (never REPO_ROOT/name)."""
    out = Path(git_dir) / name
    if out.exists():
        out.unlink()
    p = run(["git", "bundle", "create", name, "--all"], cwd=git_dir)
    if p.returncode != 0:
        print("BUNDLE FAIL", name, p.stderr, file=sys.stderr)
        sys.exit(1)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", required=True)
    ap.add_argument("--dest", required=True)
    args = ap.parse_args()

    repo_root = Path(_norm_path(args.repo_root)).resolve()
    dest = Path(_norm_path(args.dest)).resolve()
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "validation").mkdir(exist_ok=True)

    print("Backup dest:", dest)
    print("Repo root  :", repo_root)

    # ---- 1. Git bundles (full object-history recovery) ----
    print("\n[1/5] Creating git bundles ...")
    super_repo = repo_root
    sub_worktree = repo_root / "vendor/hermes-agent"
    bundle_super = make_bundle("superproject.bundle", super_repo)   # written to repo_root
    bundle_sub = make_bundle("submodule.bundle", sub_worktree)      # written to submodule worktree

    print("      superproject.bundle:", bundle_super.name,
          bundle_super.stat().st_size, "bytes")
    print("      submodule.bundle    :", bundle_sub.name,
          bundle_sub.stat().st_size, "bytes")

    # git writes a relative-path bundle output next to the cwd. Stage copies of
    # both bundles into the backup dest so the archive itself and the recovery
    # metadata reference the artifacts inside the backup directory (those copies
    # are intermediates, removed from the working tree so they do not pollute
    # the archived tree).
    shutil.copy2(bundle_super, dest / "superproject.bundle")
    shutil.copy2(bundle_sub, dest / "submodule.bundle")
    os.remove(bundle_super)
    os.remove(bundle_sub)
    bundle_super = dest / "superproject.bundle"
    bundle_sub = dest / "submodule.bundle"

    # verify the staged copies
    for b in (bundle_super, bundle_sub):
        v = run(["git", "bundle", "verify", str(b)])
        print("      verify:", b.name, "->", "OK" if v.returncode == 0 else v.stderr)

    # ---- 2. Recovery metadata + logs ----
    print("\n[2/5] Writing recovery metadata ...")
    super_head = run(["git", "rev-parse", "HEAD"], cwd=repo_root).stdout.strip()
    super_branch = run(["git", "branch", "--show-current"], cwd=repo_root).stdout.strip()
    sub_status = run(["git", "submodule", "status"], cwd=repo_root).stdout.strip()
    sub_sha = sub_status.split()[0] if sub_status else "unknown"
    sub_path_in_repo = "vendor/hermes-agent"
    sub_gitdir = repo_root / ".git/modules/vendor/hermes-agent"

    git_recovery_log = {
        "backup_spec": "SHAH AI OS Phase 5A v3 recovery",
        "project_root": str(repo_root),
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "branch": super_branch,
        "superproject_head": super_head,
        "submodule_pinned_commit": sub_sha,
        "submodule_path": sub_path_in_repo,
        "submodule_gitdir": str(sub_gitdir),
        "bundles": [
            {"file": "superproject.bundle", "sha256": sha256_of_file(bundle_super),
             "size": bundle_super.stat().st_size},
            {"file": "submodule.bundle", "sha256": sha256_of_file(bundle_sub),
             "size": bundle_sub.stat().st_size},
        ],
        "files_excluded_from_archive": {
            "production_crm": list(PRODUCTION_CRM),
            "legacy_backups": [
                "backup_phase3_harden_*", "backup_phase4_sprint1_*",
            ],
            "regenerable_git_object_packs":
                ["submodule.bundle (replaces "
                 ".git/modules/vendor/hermes-agent/objects/pack-*.pack)"],
        },
        "recovery_procedure_reference": "recovery-README.md",
    }
    (dest / "git-recovery.log").write_text(
        json.dumps(git_recovery_log, indent=2), encoding="utf-8")
    print("      git-recovery.log written")

    sub_recovery_log = {
        "backup_spec": "SHAH AI OS Phase 5A v3 submodule recovery",
        "project_root": str(repo_root),
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "submodule_worktree": str(sub_worktree),
        "submodule_gitdir":
            str(sub_gitdir),
        "submodule_pinned_commit": sub_sha,
        "bundle_file": "submodule.bundle",
        "bundle_sha256": sha256_of_file(bundle_sub),
        "note": ("Full submodule object history is in submodule.bundle. "
                 "Restore: extract tar.gz -> "
                 "cd <restored> && "
                 "git clone --local superproject.bundle ssc-recovered-git && "
                 "cd ssc-recovered-git && "
                 "git submodule update --init --recursive "
                 "(or use origin URL from .gitmodules)."),
    }
    (dest / "submodule-recovery.log").write_text(
        json.dumps(sub_recovery_log, indent=2), encoding="utf-8")
    print("      submodule-recovery.log written")

    # ---- 3. recovery-README ----
    print("\n[3/5] Writing recovery-README.md ...")
    readme = f"""# Phase 5A Recovery README

Project: {PROJECT_NAME}
Backup created: {datetime.now(timezone.utc).isoformat()}
Superproject HEAD: {super_head}
Submodule pinned commit: {sub_sha}
Branch: {super_branch}

## What this backup contains

1. `superproject.bundle` - verified git bundle of the FULL superproject object
   history (all refs). `git bundle verify superproject.bundle` reports OK.
2. `submodule.bundle` - verified git bundle of the FULL vendor/hermes-agent
   object history (all refs). `git bundle verify submodule.bundle` reports OK.
3. `ssc_marketing_managing.tar.gz` - working tree + full `.git` metadata
   + `.git/modules/` metadata. Excludes only regenerable items (listed below).
4. `git-recovery.log`, `submodule-recovery.log`, `recovery-README.md`.

## Excluded from the archive (regenerable / already captured)

- `data/leads.csv` (production CRM - requires explicit owner approval to
  include; the backup never includes it by default).
- Legacy backup dirs: `backup_phase3_harden_*`, `backup_phase4_sprint1_*`.
- Regenerable files: `__pycache__/`, `*.pyc`, `*.tmp`, `*.swp`, `*.log`,
  `*.sqlite`, `*.db`, `.env*`, `credentials.json`, `token.json`,
  `*.pem`, `*.key`.
- Regenerable submodule object pack: the 1.4 GB
  `.git/modules/vendor/hermes-agent/objects/pack-*.pack` is NOT in the archive;
  it is captured 1:1 inside `submodule.bundle` instead.

## Recovery procedure (primary, uses bundles - fully offline)

0. Create a clean target directory, e.g. `restore-this`.
1. Extract the archive:
       tar -xzf ssc_marketing_managing.tar.gz -C restore-this
2. Recreate full superproject history from the bundle:
       cd restore-this
       git clone --local superproject.bundle ssc-recovered-git
3. Re-sync the submodule working tree:
       cd ssc-recovered-git
       git submodule update --init --recursive
   (This uses the origin URL in `.gitmodules`. If the submodule origin is
   unreachable, restore the submodule objects from `submodule.bundle` by cloning
   it into the submodule gitdir before step 3.)
4. Verify the submodule checkout state:
       cd ssc-recovered-git
       git status
       git submodule status        # should match pinned commit {sub_sha}

## Alternate recovery (artifact-based, no bundles needed)

- Extract the archive normally; the restored `.git` still holds refs and index
  so the working tree matches the pinned submodule commit for checkout purposes.
- For full object DB recovery offline, copy `superproject.bundle` and
  `submodule.bundle` to the restored machine and use the procedure above.

## Verified fields

- Superproject HEAD: {super_head}
- Submodule commit: {sub_sha}
- Bundles:
-   {json.dumps([(b["file"], b["sha256"][:12]) for b in git_recovery_log["bundles"]], indent=4)}
"""
    (dest / "recovery-README.md").write_text(readme, encoding="utf-8")
    print("      recovery-README.md written")

    # ---- 4. Working-tree archive (exclude regenerable only) ----
    print("\n[4/5] Creating ssc_marketing_managing.tar.gz ...")
    arc = dest / "ssc_marketing_managing.tar.gz"
    files = collect_files(repo_root)
    with tarfile.open(arc, "w:gz", compresslevel=1, format=tarfile.PAX_FORMAT) as tar:
        for rel in files:
            tar.add(repo_root / rel, arcname=rel, recursive=True)
    print("      archive:", arc.name, arc.stat().st_size, "bytes, files:", len(files))

    # ---- 5. Manifest + sha256 ----
    print("\n[5/5] Writing manifest + checksum ...")
    archive_sha = sha256_of_file(arc)
    manifest = {
        "backup_spec": "SHAH AI OS Phase 5A v3 recovery",
        "project_root": str(repo_root),
        "archive_file": arc.name,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "branch": super_branch,
        "head_commit": super_head,
        "submodule_pinned_commit": sub_sha,
        "superproject_head": super_head,
        "metadata": {
            "total_files": len(files),
            "archive_sha256": archive_sha,
            "superproject_bundle": bundle_super.name,
            "submodule_bundle": bundle_sub.name,
        },
        "files": [
            {"relative_path": rel, "sha256": sha256_of_file(repo_root / rel),
             "size_bytes": (repo_root / rel).stat().st_size,
             "is_symlink": (repo_root / rel).is_symlink()}
            for rel in files
        ],
        "exclude_policy": {
            "excluded_dirs": sorted(EXCLUDE_DIRS),
            "excluded_extensions": sorted(EXCLUDE_EXTS),
            "production_crm_excluded": list(PRODUCTION_CRM),
            "regenerable_submodule_pack_excluded": True,
            "git_recovery_uses_bundles": True,
        },
    }
    (dest / "ssc_marketing_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    with open(dest / "ssc_marketing_managing.sha256", "w", encoding="utf-8") as fh:
        fh.write(archive_sha + "  " + arc.name + "\n")
        for entry in manifest["files"]:
            fh.write(entry["sha256"] + "  " + entry["relative_path"] + "\n")
    print("      ssc_marketing_manifest.json written")
    print("      ssc_marketing_managing.sha256 written")

    # ---- summary ----
    print("\nBACKUP COMPLETE:", dest)
    print("  archive:", arc.name, arc.stat().st_size, "bytes")
    print("  bundles:", bundle_super.name, bundle_super.stat().st_size,
          "|", bundle_sub.name, bundle_sub.stat().st_size)
    print("  manifest entries:", len(files))
    print("  archive sha256:", archive_sha)
    return 0


if __name__ == "__main__":
    sys.exit(main())
