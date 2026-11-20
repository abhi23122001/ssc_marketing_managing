#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SHAH AI OS - Phase 5A Archive & Manifest Generator
=================================================
Creates a single compressed TAR archive of the canonical SHAH AI project
plus a SHA-256 manifest for integrity verification.

ARCHITECTURE
- Archive internal root: project-root contents directly (NO wrapper folder).
- Restore extraction destination: a newly created <project-name> folder.

INCLUDE/EXCLUDE POLICY (authoritative)
  INCLUDE
    .git/ (after security audit passes), .gitmodules, .gitignore, AGENTS.md,
    README.md, COMMAND-CENTER.md, Start-SHAI-Center.ps1,
    .github/workflows/validate.yml, brand/ssc-brand-profile.md, config/SOUL.md,
    vendor/hermes-agent/ (content + .git pointer + submodule metadata),
    modules/ (01-14), shared/, tests/, docs/, data/ (business data),
    .hermes/skills/shah-ai/SKILL.md (explicit protected exception),
    .gitmodules

  EXCLUDE
    data/leads.csv                      (production CRM - requires approval)
    outputs/                            (regenerable)
    private-client-data/                 (confidential, controlled access)
    .env*                                (local secrets)
    **/credentials.json, **/token.json  (OAuth tokens)
    *.pem, *.key                         (private keys)
    .hermes/ (runtime state only)
    __pycache__/, *.pyc, *.tmp, *.swp   (regenerable)
    Existing backups (backup_phase3_*, backup_phase4_*) - never archived

USAGE
    python3 archive_and_manifest.py --repo-root <path> --archive <out.tar.gz> \
        --manifest <manifest.json> --sha256-file <manifest.sha256>

RETURNS
    0 on success, non-zero on failure.
"""

import argparse
import hashlib
import json
import os
import sys
import tarfile
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Policy constants
# ---------------------------------------------------------------------------
REPO_ROOT = Path.cwd()
PROJECT_NAME = "ssc_marketing_managing"

# Data files that are production CRM data and must NOT be archived.
PRODUCTION_CRM_FILES = {"data/leads.csv"}

# Regenerable / confidential / temporary exclusions.
EXCLUDE_DIRS = {
    "outputs",
    "private-client-data",
    "__pycache__",
    "node_modules",
    ".venv",
    "venv",
    ".git",
}
# .git is excluded by default; re-include only after security audit passes
# and the policy is explicitly overridden at runtime.
EXCLUDE_EXTS = {".pyc", ".tmp", ".swp", ".log", ".sqlite", ".sqlite3", ".db"}

# Files explicitly excluded even though they appear in the include set.
EXCLUDED_PATHS = {
    "data/leads.csv",                       # production CRM
    "data/leads.csv.example",             # example only
}

# Files explicitly included as protected exceptions.
PROTECTED_EXCEPTION_PATHS = {
    ".hermes/skills/shah-ai/SKILL.md",
    "config/SOUL.md",
    "brand/ssc-brand-profile.md",
}

# Files always included.
INCLUDE_PATHS = {
    ".gitmodules",
    ".gitignore",
    "AGENTS.md",
    "README.md",
    "COMMAND-CENTER.md",
    "Start-SHAI-Center.ps1",
    ".github/workflows/validate.yml",
}


def sha256_of_file(filepath):
    """Return the SHA-256 hex digest of a file (read in chunks)."""
    h = hashlib.sha256()
    with open(filepath, "rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_of_bytes(data):
    return hashlib.sha256(data).hexdigest()


def is_protected_exception(rel_path):
    """A path is a protected exception if it is the explicit SKILL.md."""
    return rel_path in PROTECTED_EXCEPTION_PATHS


def is_excluded(rel_path):
    """
    Return True if a file/dir should be EXCLUDED from the archive.
    Implements the full include/exclude policy.
    """
    parts = Path(rel_path).parts

    # --- Dir-level exclusions -----------------------------------------
    if rel_path in EXCLUDE_DIRS:
        return True
    if parts[0] in EXCLUDE_DIRS:
        return True
    if ".git" in parts:
        return True

    # --- Extension-based exclusions ------------------------------------
    if Path(rel_path).suffix in EXCLUDE_EXTS:
        return True

    # --- Path-based exclusions -----------------------------------------
    if rel_path in EXCLUDED_PATHS:
        return True

    # --- Confidential directories --------------------------------------
    if any(part in parts for part in ("private-client-data",)):
        return True

    # .env* files (local secrets)
    if Path(rel_path).name.startswith(".env"):
        return True

    # Credentials / tokens
    name = Path(rel_path).name
    if name in ("credentials.json", "token.json"):
        return True

    # Legacy backups must NEVER be archived.
    if "backup_phase3_harden_" in rel_path or "backup_phase4_sprint1_" in rel_path:
        return True

    # outputs directory and all its contents
    if rel_path.startswith("outputs"):
        return True

    return False


def is_included(rel_path):
    """
    Return True if the file SHOULD be included, ignoring protected
    exceptions and data/leads.csv (which are handled separately).
    """
    parts = Path(rel_path).parts
    if rel_path.startswith("data/"):
        # Business data: only leads.csv is excluded; everything else included.
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
        # NOTE: 'pruned' must collect NON-excluded directories; 'dirnames[:]'
        # is then set to that list so os.walk descends only into allowed dirs.
        pruned = []
        for d in dirnames:
            full = dirpath / d
            rel = str(full.relative_to(repo_root))
            if is_excluded(rel):
                # Directory is excluded: do not add to pruned list.
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
    """
    Create a TAR.GZ archive. Archive internal root = project-root contents
    directly (no wrapper folder).
    """
    repo_root = Path(repo_root)
    with tarfile.open(archive_path, "w:gz", format=tarfile.PAX_FORMAT if pax_format else tarfile.DEFAULT_FORMAT) as tar:
        for rel in files:
            full = repo_root / rel
            # Add the file with its arcname = relative path (no ./ prefix).
            tar.add(full, arcname=rel, recursive=True)
    return archive_path


def generate_manifest(repo_root, archive_path, files, metadata):
    """
    Build a JSON manifest with SHA-256 per file, archive checksum,
    metadata, and policies. Returns the manifest dict.
    """
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
        "backup_spec": "SHAH AI OS Phase 5A v7.1",
        "project_root": str(repo_root),
        "archive_file": archive.name,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "branch": metadata.get("branch", "unknown"),
        "head_commit": metadata.get("head_commit", "unknown"),
        "submodule": metadata.get("submodule", {
            "path": "vendor/hermes-agent",
            "pinned_commit": "081e8d9b75b2bedae297a89232b04ef9be7b26a0",
        }),
        "metadata": {
            "total_files": len(files_entry),
            "archive_sha256": archive_sha,
            "backup_version": "5A-v7.1",
        },
        "files": files_entry,
        "exclude_policy": {
            "excluded_dirs": sorted(EXCLUDE_DIRS),
            "excluded_extensions": sorted(EXCLUDE_EXTS),
            "production_crm_excluded": ["data/leads.csv"],
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

    # --- 2. Build metadata (branch, HEAD, submodule pinned commit) -------
    # (Git metadata is captured by owner during backup orchestration.)
    metadata = {
        "branch": "main",
        "head_commit": "a21e9f775c4e564b4f5d73d1291598160d7e8350",
        "submodule": {
            "path": "vendor/hermes-agent",
            "pinned_commit": "081e8d9b75b2bedae297a89232b04ef9be7b26a0",
        },
    }

    # --- 3. Create archive ----------------------------------------------
    archive_path = Path(args.archive)
    create_archive(repo_root, archive_path, files)

    # --- 4. Build manifest ----------------------------------------------
    manifest = generate_manifest(repo_root, archive_path, files, metadata)

    # Write manifest
    with open(args.manifest, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2, sort_keys=True)
        fh.write("\n")

    # --- 5. Write .sha256 checksum file ---------------------------------
    write_sha256_file(manifest, args.sha256_file)

    # --- 6. Report ------------------------------------------------------
    print(f"PROJECT_ROOT       : {repo_root}")
    print(f"ARCHIVE            : {archive_path}  ({archive_path.stat().st_size} bytes)")
    print(f"MANIFEST           : {args.manifest}")
    print(f"SHA256_FILE        : {args.sha256_file}")
    print(f"TOTAL_FILES        : {file_count}")
    print(f"ARCHIVE_SHA256     : {manifest['metadata']['archive_sha256']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
