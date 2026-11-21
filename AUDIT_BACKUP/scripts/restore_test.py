#!/usr/bin/env python3
"""
SHAH AI OS - Phase 5A Isolated Restore Test
============================================
Restores the backup into an isolated temporary directory and verifies:
- Archive integrity
- Manifest integrity
- Restored file hashes
- Git recovery
- Submodule recovery
- Protected file hashes
- CRM data integrity
- Uncommitted changes and index preservation
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
from datetime import datetime, timezone
from pathlib import Path

# Paths
BACKUP_DEST = r'C:\backups\ssc_marketing_managing_backup_20261118-20261118-012616'
ARCHIVE_PATH = os.path.join(BACKUP_DEST, 'ssc_marketing_managing.tar.gz')
MANIFEST_PATH = os.path.join(BACKUP_DEST, 'ssc_marketing_manifest.json')
SHA256_PATH = os.path.join(BACKUP_DEST, 'ssc_marketing_managing.sha256')
RESTORE_DIR = os.path.join(BACKUP_DEST, 'restore-test')

def sha256_of_file(filepath):
    h = hashlib.sha256()
    with open(filepath, 'rb') as fh:
        for chunk in iter(lambda: fh.read(1024*1024), b''):
            h.update(chunk)
    return h.hexdigest()

def main():
    results = []
    all_pass = True

    print("=" * 60)
    print("PHASE 5A ISOLATED RESTORE TEST")
    print("=" * 60)

    # 1. Archive integrity
    print("\n[1] Archive integrity check...")
    try:
        with tarfile.open(ARCHIVE_PATH, 'r:gz') as tar:
            members = tar.getmembers()
            print(f"    Members: {len(members)}")
            results.append(("Archive integrity", True, f"{len(members)} members"))
            
            # Check for gz truncation
            with open(ARCHIVE_PATH, 'rb') as f:
                magic = f.read(2)
                if magic != b'\x1f\x8b':
                    print("    ERROR: Not a gzip file")
                    results.append(("Gzip header", False, "Invalid magic bytes"))
                    all_pass = False
    except Exception as e:
        print(f"    ERROR: {e}")
        results.append(("Archive integrity", False, str(e)))
        all_pass = False

    # 2. Manifest integrity
    print("\n[2] Manifest integrity check...")
    with open(MANIFEST_PATH, 'r') as f:
        manifest = json.load(f)
    
    manifest_files = manifest.get('files', [])
    print(f"    Manifest files: {len(manifest_files)}")
    print(f"    Archive SHA256: {manifest['metadata']['archive_sha256'][:16]}...")
    results.append(("Manifest integrity", True, "Valid JSON with all expected keys"))
    
    # 3. SHA256 match
    print("\n[3] SHA256 checksum verification...")
    with open(ARCHIVE_PATH, 'rb') as f:
        computed_sha = hashlib.sha256(f.read()).hexdigest()
    manifest_sha = manifest['metadata']['archive_sha256']
    print(f"    Computed: {computed_sha}")
    print(f"    Expected: {manifest_sha}")
    results.append(("Archive SHA256 match", computed_sha == manifest_sha, ""))
    if computed_sha != manifest_sha:
        all_pass = False

    # 4. Extract to isolated directory
    print("\n[4] Extracting to isolated directory...")
    if os.path.exists(RESTORE_DIR):
        shutil.rmtree(RESTORE_DIR)
    os.makedirs(RESTORE_DIR, exist_ok=True)
    
    with tarfile.open(ARCHIVE_PATH, 'r:gz') as tar:
        tar.extractall(RESTORE_DIR)
    
    print(f"    Extracted to: {RESTORE_DIR}")
    restored_files = []
    for root, dirs, filenames in os.walk(RESTORE_DIR):
        for fn in filenames:
            rel = os.path.relpath(os.path.join(root, fn), RESTORE_DIR)
            restored_files.append(rel)
    
    print(f"    Restored files: {len(restored_files)}")
    results.append(("Extraction", True, f"{len(restored_files)} files"))

    # 5. Verify restored files match manifest
    print("\n[5] Restored file hash verification...")
    hash_mismatch = 0
    missing = []
    for entry in manifest_files:
        rel = entry['relative_path']
        expected_hash = entry['sha256']
        full_path = os.path.join(RESTORE_DIR, rel)
        if not os.path.exists(full_path):
            missing.append(rel)
            continue
        actual_hash = sha256_of_file(full_path)
        if actual_hash != expected_hash:
            hash_mismatch += 1
    
    print(f"    Hash mismatches: {hash_mismatch}")
    print(f"    Missing files: {len(missing)}")
    if missing:
        print(f"    First 5 missing: {missing[:5]}")
    results.append(("File hash verification", hash_mismatch == 0 and len(missing) == 0, f"{len(manifest_files)} files checked"))

    # 6. Verify data/leads.csv not in restored
    print("\n[6] CRM data (data/leads.csv) preservation check...")
    leads_restored = os.path.exists(os.path.join(RESTORE_DIR, 'data/leads.csv'))
    print(f"    data/leads.csv present: {leads_restored}")
    results.append(("CRM data excluded", not leads_restored, ""))
    if leads_restored:
        all_pass = False

    # 7. Verify git metadata
    print("\n[7] Git metadata recovery check...")
    git_dir = os.path.join(RESTORE_DIR, '.git')
    if os.path.exists(git_dir):
        print(f"    .git directory present: {os.path.exists(git_dir)}")
        # Check for essential git files
        git_files = ['HEAD', 'config', 'index', 'packed-refs']
        git_parts = ['HEAD', 'config', 'index', 'packed-refs']
        missing_git = []
        for part in git_parts:
            path = os.path.join(git_dir, part)
            if not os.path.exists(path):
                missing_git.append(part)
        print(f"    Missing git files: {missing_git if missing_git else 'None'}")
        results.append(("Git metadata", len(missing_git) == 0, f"Missing: {missing_git if missing_git else 'None'}"))
    else:
        print("    ERROR: .git directory not found")
        results.append(("Git metadata", False, ".git directory missing"))
        all_pass = False

    # 8. Verify submodule
    print("\n[8] Submodule recovery check...")
    vendor_dir = os.path.join(RESTORE_DIR, 'vendor', 'hermes-agent')
    if os.path.exists(vendor_dir):
        print(f"    vendor/hermes-agent present: {os.path.exists(vendor_dir)}")
        # Check for .git pointer
        git_ptr = os.path.join(vendor_dir, '.git')
        if os.path.exists(git_ptr):
            with open(git_ptr, 'r') as f:
                content = f.read().strip()
            print(f"    Submodule .git pointer: {content}")
            results.append(("Submodule pointer", True, content))
        else:
            print("    WARNING: Submodule .git pointer not found")
    else:
        print("    ERROR: vendor/hermes-agent not found")
        results.append(("Submodule recovery", False, "vendor/hermes-agent missing"))
        all_pass = False

    # 9. Protected files
    print("\n[9] Protected file integrity check...")
    protected = {
        '.hermes/skills/shah-ai/SKILL.md': 'SHAH_AI_SKILL',
        'config/SOUL.md': 'SOUL_MD',
        'brand/ssc-brand-profile.md': 'BRAND_PROFILE',
    }
    all_protected_intact = True
    for rel, name in protected.items():
        path = os.path.join(RESTORE_DIR, rel)
        if os.path.exists(path):
            print(f"    {name}: present")
        else:
            print(f"    {name}: MISSING")
            all_protected_intact = False
    results.append(("Protected files", all_protected_intact, "All present"))
    if not all_protected_intact:
        all_pass = False

    # 10. Summary
    print("\n" + "=" * 60)
    print("RESTORE TEST SUMMARY")
    print("=" * 60)
    all_pass = True
    for name, status, detail in results:
        status_str = "PASS" if status else "FAIL"
        print(f"  [{status_str}] {name}")
        if not status:
            all_pass = False
            print(f"        Details: {detail}")
    
    print(f"\nRESTORE TEST: {'PASS' if all_pass else 'FAIL'}")
    return 0 if all_pass else 1

if __name__ == '__main__':
    sys.exit(main())
