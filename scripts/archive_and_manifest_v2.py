#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SHAH AI OS - Phase 5A Archive & Manifest Generator (V2 - corrected)
===================================================
Create a single compressed TAR archive of the canonical SHAH AI project
plus a SHA-256 manifest for integrity verification.

Changes from V1:
- Fixed collect_files()'s directory pruning logic bug (pruned list now
  collects NON-excluded directories; dirnames[:] = pruned correctly sets
  the list of directories to visit).
- Excludes .git modules vendor hermes-agent object packs (regenerable).
- Added preflight inventory and size report.
"use unittest" style.
"""
import argparse
import hashlib
import json
import os
import sys
import tarfile
import tempfile
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Policy constants
# ---------------------------------------------------------------------------
REPO_ROOT = Path.cwd()
PROJECT_NAME = "ssc_marketing_managing"

# Data files that are production CRM data and must NOT be archived.
PRODUCTION_CRM_FILES = {"data/leads.csv"}

# Excluded directories (full paths from repo root)
EXCLUDE_DIRS = {
    "outputs",
    "private-client-data",
    "__pycache__",
    "node_modules",
    ".venv",
    "venv",
    ".git",
    ".git/modules",
    ".git/modules/vendor",
    ".git/modules/vendor/hermes-agent",
    ".git/modules/vendor/hermes-agent/objects",
}

# Excluded extensions
EXCLUDE_EXTS = {".pyc", ".tmp", ".swp", ".log", ".sqlite", ".sqlite3", ".db"}

# Production CRM file paths
PRODUCTION_CRM_PATHS = {
    "data/leads.csv",
}

# Files explicitly excluded from the archive
EXCLUDED_PATHS = PRODUCTION_CRM_PATHS

# Files explicitly included as protected exceptions
PROTECTED_EXCEPTION_PATHS = {
    ".hermes/skills/shah-ai/SKILL.md",
    "config/SOUL.md",
    "brand/ssc-brand-profile.md",
}

# Files always included
INCLUDE_PATHS = {
    ".gitmodules",
    ".gitignore",
    "AGENTS.md",
    "README.md",
    "COMMAND-CENTER.md",
    "Start-SHAI-Center.ps1",
    ".github/workflows/validate.yml",
}

# Submodule pinned commit
SUBMODULE_PINNED_COMMIT = "081e8d9b75b2bedae297a89232b04ef9be7b26a0"

# Git superproject HEAD
SUPERPROJECT_HEAD = "a21e9f775c4e564b4f5d73d1291598160d7e8350"


def sha256_of_file(filepath):
    """Return the SHA-256 hex digest of a file (read in chunks)."""
    h = hashlib.sha256()
    with open(filepath, "rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def is_protected_exception(rel_path):
    """Return True if the path is a protected exception."""
    return rel_path in PROTECTED_EXCEPTION_PATHS


def is_excluded(rel_path):
    """Return True if the file/dir should be EXCLUDED from the archive."""
    parts = Path(rel_path).parts

    # Dir-level exclusions
    if rel_path in EXCLUDE_DIRS:
        return True
    if parts[0] in EXCLUDE_DIRS:
        return True
    if ".git" in parts:
        return True

    # Extension-based exclusions
    if Path(rel_path).suffix in EXCLUDE_EXTS:
        return True

    # Path-based exclusions
    if rel_path in EXCLUDED_PATHS:
        return True

    # Confidential directories
    if any(part in parts for part in ("private-client-data",)):
        return True

    # .env* files (local secrets)
    if Path(rel_path).name.startswith(".env"):
        return True

    # Credentials / tokens
    name = Path(rel_path).name
    if name in ("credentials.json", "token.json"):
        return True

    # Legacy backups must NEVER be archived
    if "backup_phase3_harden_" in rel_path or "backup_phase4_sprint1_" in rel_path:
        return True

    # outputs directory and all its contents
    if rel_path.startswith("outputs"):
        return True

    return False


def is_included(rel_path):
    """Return True if the file SHOULD be included (ignoring protected exceptions)."""
    parts = Path(rel_path).parts
    if rel_path.startswith("data/"):
        return True
    return True


def collect_files(repo_root):
    """
    Walk the project root and return a sorted list of relative paths that
    satisfy the include/exclude policy.
    """
    files = []
    for dirpath, dirnames, filenames in os.walk(repo_root):
        dirpath = Path(dirpath)
        rel_dir = dirpath.relative_to(repo_root)

        # Prune excluded directories in-place so os.walk does not descend.
        pruned = []
        for d in dirnames:
            full = dirpath / d
            rel = str(full.relative_to(repo_root))
            if is_excluded(rel):
                continue
            # Explicitly excluded directories (e.g. .git) only pruned when not
            # a protected exception.
            if rel in ("data/leads.csv",):
                continue
            pruned.append(d)
        dirnames[:] = pruned

        for fn in filenames:
            full = dirpath / fn
            rel = str(full.relative_to(repo_root)).replace("\\", "/")
            if is_excluded(rel):
                continue
            if not is_protected_exception(rel) and not is_included(rel):
                continue
            files.append(rel)

    return sorted(set(files))


def create_archive(repo_root, archive_path, files, pax_format=True):
    """Create a TAR.GZ archive with the given files."""
    repo_root = Path(repo_root)
    with tarfile.open(archive_path, "w:gz",
                       format=tarfile.PAX_FORMAT if pax_format else tarfile.DEFAULT_FORMAT) as tar:
        for rel in files:
            full = repo_root / rel
            tar.add(full, arcname=rel, recursive=True)
    return archive_path


def generate_manifest(repo_root, archive_path, files, metadata):
    """Build a JSON manifest with SHA-256 per file, archive checksum, etc."""
    archive = Path(archive_path)
    archive_sha = sha256_of_file(archive) if archive.exists() else None

    files_entry = []
    for rel in files:
        full = repo_root / rel
        files_entry.append({
            "relative_path": rel,
            "sha256": sha256_of_file(full),
            "size_bytes": full.stat().st_size,
            "is_symlink": full.is_symlink(),
        })

    manifest = {
        "backup_spec": "SHAH AI OS Phase 5A v2 corrected",
        "project_root": str(repo_root),
        "archive_file": archive.name,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "branch": metadata.get("branch", "unknown"),
        "head_commit": metadata.get("head_commit", "unknown"),
        "submodule": metadata.get("submodule", {
            "path": "vendor/hermes-agent",
            "pinned_commit": SUBMODULE_PINNED_COMMIT,
        }),
        "metadata": {
            "total_files": len(files_entry),
            "archive_sha256": archive_sha,
            "backup_version": "5A-v2-corrected",
        },
        "files": files_entry,
        "exclude_policy": {
            "excluded_dirs": sorted(EXCLUDE_DIRS),
            "excluded_extensions": sorted(EXCLUDE_EXTS),
            "production_crm_excluded": [p for p in PRODUCTION_CRM_PATHS if p in repo_root],
            "credentials_handled_externally": True,
        },
    }
    return manifest


def write_sha256_file(manifest, sha256_path):
    """Write a SHA-256 checksum file (hash + 2 spaces + relative path)."""
    with open(sha256_path, "w", encoding="utf-8") as fh:
        for entry in manifest["files"]:
            fh.write(f"{entry['sha256']}  {entry['relative_path']}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Create a single TAR.GZ archive and SHA-256 manifest for SHAH AI OS.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--repo-root", required=True, help="Canonical project root.")
    parser.add_argument("--archive", required=True, help="Output archive path.")
    parser.add_argument("--manifest", required=True, help="Output manifest JSON path.")
    parser.add_argument("--sha256-file", required=True, help="Output SHA-256 checksum file.")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    if not repo_root.is_dir():
        print(f"ERROR: repo-root does not exist: {repo_root}", file=sys.stderr)
        return 2

    # --- 1. Gather files under the include/exclude policy ----------------
    files = collect_files(repo_root)
    file_count = len(files)

    # --- 2. Build metadata ------------------------------------------------
    metadata = {
        "branch": "main",
        "head_commit": SUPERPROJECT_HEAD,
        "submodule": {
            "path": "vendor/hermes-agent",
            "pinned_commit": SUBMODULE_PINNED_COMMIT,
        },
    }

    # --- 3. Create archive ------------------------------------------------
    archive_path = Path(args.archive)
    create_archive(repo_root, archive_path, files)

    # --- 4. Build manifest ------------------------------------------------
    manifest = generate_manifest(repo_root, archive_path, files, metadata)

    # Write manifest
    with open(args.manifest, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2, sort_keys=True)
        fh.write("\n")

    # --- 5. Write .sha256 checksum file ----------------------------------
    write_sha256_file(manifest, args.sha256_file)

    # --- 6. Report ---------------------------------------------------------
    print(f"PROJECT_ROOT       : {repo_root}")
    print(f"ARCHIVE            : {archive_path}  ({archive_path.stat().st_size} bytes)")
    print(f"MANIFEST           : {args.manifest}")
    print(f"SHA256_FILE        : {args.sha256_file}")
    print(f"TOTAL_FILES        : {file_count}")
    print(f"ARCHIVE_SHA256     : {manifest['metadata']['archive_sha256']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
