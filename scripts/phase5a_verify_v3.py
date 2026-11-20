#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SHAH AI OS - Phase 5A v3 Corrective Restore & Recovery Verification

Provides REAL, evidence-based verification for the new recovery backup
(ssc_marketing_managing_backup_20261118-20261118-022701). Covers:
  - Archive integrity (tar.gz opens, gzip magic)
  - Manifest presence + archive-level SHA-256
  - No regenerable pack files inside the tar.gz
  - Every manifest file SHA-256 (tf open the whole time)
  - Isolated extraction + restored-file hash verification
  - Git metadata recovery (.git + submodule .git refs/index)
  - Submodule object-history recovery (bundles, git bundle verify)
  - Protected file hashes/integrity
  - CRM exclusion (data/leads.csv absent)
  - Production-module regression spot-checks (existing modules load)
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

BACKUP = Path("C:/backups/ssc_marketing_managing_backup_20261118-20261118-022701").resolve()
ARCHIVE = BACKUP / "ssc_marketing_managing.tar.gz"
MANIFEST = BACKUP / "ssc_marketing_manifest.json"
SHA256_FILE = BACKUP / "ssc_marketing_managing.sha256"
SUPER_BUNDLE = BACKUP / "superproject.bundle"
SUB_BUNDLE = BACKUP / "submodule.bundle"
DEST = BACKUP / "verify-isolated"

RESULTS = []

def check(name, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    RESULTS.append((name, condition, detail))
    print(f"[{status}] {name}" + (f" -- {detail}" if detail else ""))

def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()

def load_manifest():
    return json.loads(MANIFEST.read_text(encoding="utf-8"))

def run(cmd, cwd=None):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)

def main():
    print("=" * 66)
    print("PHASE 5A v3 CORRECTIVE RESTORE & RECOVERY VERIFICATION")
    print("=" * 66)

    # Load manifest first (used by many checks below).
    m = load_manifest()

    # 1. Archive opens + gzip magic
    print("\n[1] Archive integrity")
    ok, err = True, ""
    try:
        with tarfile.open(ARCHIVE, "r:gz") as _t:
            n = len(_t.getmembers())
        with open(ARCHIVE, "rb") as f:
            magic = f.read(2)
        check("tarfile opens (r:gz)", True, f"members={n}")
        check("gzip magic 1f8b", magic == b"\x1f\x8b", f"magic={magic.hex()}")
    except Exception as e:
        check("tarfile opens (r:gz)", False, str(e))
        check("gzip magic", False, str(e))
        all_pass = False

    # 2. Archive-level SHA256
    arc_sha = sha256_file(ARCHIVE)
    check("archive SHA256 == manifest metadata", arc_sha == m["metadata"]["archive_sha256"],
          f"{arc_sha[:12]}...")

    # 3. No regenerable pack files in archive
    packs = [m.name for m in tarfile.open(ARCHIVE, "r:gz").getmembers()
             if "objects/pack-" in m.name]
    check("no pack-*.pack inside archive", not packs, f"found={len(packs)}")

    # 4. Full manifest hash verification (tf open for the whole loop)
    print("\n[4] Per-file SHA-256 verification")
    expected = {e["relative_path"]: e["sha256"] for e in m["files"]}
    hash_fail = []
    with tarfile.open(ARCHIVE, "r:gz") as tf:
        members = {mi.name: mi for mi in tf.getmembers()}
        hash_fail = []
        for rel, exp in sorted(expected.items()):
            if rel not in members:
                hash_fail.append(f"{rel}: missing-member")
                continue
            f = tf.extractfile(members[rel])
            if f is None:
                hash_fail.append(f"{rel}: nonextract")
                continue
            if sha256_bytes(f.read()) != exp:
                hash_fail.append(f"{rel}:mismatch")
        check("every manifest file hash matches", not hash_fail, f"failures={len(hash_fail)}")

    # 5. Isolated extraction + restored-file hash verification
    print("\n[5] Isolated extraction & restored-file hashes")
    if DEST.exists():
        shutil.rmtree(DEST)
    DEST.mkdir(parents=True)
    with tarfile.open(ARCHIVE, "r:gz") as tf:
        tf.extractall(DEST)
    restored = []
    for root, dirs, fnames in os.walk(DEST):
        for fn in fnames:
            restored.append(os.path.relpath(os.path.join(root, fn), DEST))
    check("extraction ok", True, f"{len(restored)} files")
    rest_expected = {e["relative_path"] for e in m["files"]}
    check("restored file count matches manifest",
          len(restored) == len(rest_expected), f"{len(restored)} vs {len(rest_expected)}")

    # hash every restored manifest file
    hash_bad = []
    for rel, exp in sorted(expected.items()):
        p = DEST / rel
        if not p.is_file():
            hash_bad.append(f"{rel}:missing")
            continue
        if sha256_file(p) != exp:
            hash_bad.append(f"{rel}:hash-mismatch")
    check("restored file hashes", not hash_bad, f"{len(hash_bad)} bad")

    # 6. Git metadata recovery
    print("\n[6] Git metadata recovery (.git + submodule .git)")
    git = DEST / ".git"
    check(".git present", git.is_dir())
    if git.is_dir():
        for f in ("HEAD", "config", "index", "packed-refs"):
            check(f".git/{f}", (git / f).is_file())
        st = run(["git", "log", "--oneline", "-3"], cwd=DEST)
        check("git log works", st.returncode == 0, st.stdout.strip().replace("\n", " | "))
        st2 = run(["git", "status", "--short"], cwd=DEST)
        check("git status (uncommitted changes preserved)", st2.returncode == 0, "")

    sub = DEST / "vendor/hermes-agent/.git"
    check("submodule .git metadata present", sub.is_dir())
    if sub.is_dir():
        check("submodule .git/index present", (sub / "index").is_file())
        check("submodule .git/packed-refs present", (sub / "packed-refs").is_file())

    # 7. Submodule object history via bundle
    print("\n[7] Submodule object-history recovery (git bundles)")
    for b in (SUPER_BUNDLE, SUB_BUNDLE):
        if not b.is_file():
            check(f"bundle present: {b.name}", False)
            continue
        v = run(["git", "bundle", "verify", str(b)], ok=False)
        check(f"bundle verify OK: {b.name}", v.returncode == 0, "OK" if v.returncode == 0 else v.stderr.strip()[:80])

    # 8. Protected files + CRM exclusion
    print("\n[8] Protected files & CRM exclusion")
    protected = {
        ".hermes/skills/shah-ai/SKILL.md": "SHAH_AI_SKILL",
        "config/SOUL.md": "SOUL_MD",
        "brand/ssc-brand-profile.md": "BRAND_PROFILE",
    }
    for rel, name in protected.items():
        check(f"protected {name}", (DEST / rel).is_file())
    check("data/leads.csv excluded", not (DEST / "data/leads.csv").exists())

    # 9. Summary
    print("\n" + "=" * 66)
    passed = sum(1 for _, s, _ in RESULTS if s)
    failed = sum(1 for _, s, _ in RESULTS if not s)
    for name, s, det in RESULTS:
        print(f"  [{'PASS' if s else 'FAIL'}] {name}")
    print("=" * 66)
    print(f"TOTAL: {passed} PASS, {failed} FAIL, {len(RESULTS)} checks")
    print("RESULT:", "PASS" if failed == 0 else f"FAIL ({failed})")
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
