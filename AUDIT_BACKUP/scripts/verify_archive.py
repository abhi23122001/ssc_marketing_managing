#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SHAH AI OS - Phase 5A Archive Integrity Verifier
================================================
Verifies a generated archive against its manifest:
  - Every manifest entry hash.
  - Missing files.
  - Hash mismatches.
  - Unexpected archive files.
  - Archive member path safety.
  - JSON metadata.
  - Non-zero exit code on failure.

USAGE
    python3 verify_archive.py --archive <archive.tar.gz> --manifest <manifest.json>
"""

import argparse
import hashlib
import json
import sys
import tarfile
from pathlib import Path


def sha256_of_bytes(data):
    return hashlib.sha256(data).hexdigest()


def verify_archive(archive_path, manifest_path):
    """
    Return (ok, report). ok is True only if every check passes.
    report is a human-readable log of each check result.
    """
    report = []
    failures = 0

    def check(name, condition, detail=""):
        nonlocal failures
        status = "PASS" if condition else "FAIL"
        if not condition:
            failures += 1
        report.append(f"[{status}] {name}" + (f" -- {detail}" if detail else ""))

    # --- Read inputs ----------------------------------------------------
    archive = Path(archive_path)
    manifest = Path(manifest_path)
    if not archive.is_file():
        report.append("[FAIL] archive file not found")
        return False, "\n".join(report)
    if not manifest.is_file():
        report.append("[FAIL] manifest file not found")
        return False, "\n".join(report)

    with open(manifest, "r", encoding="utf-8") as fh:
        m = json.load(fh)

    # --- 1. File-count check ---------------------------------------------
    expected_files = {e["relative_path"]: e for e in m.get("files", [])}
    check("Manifest file count", len(expected_files) == m.get("metadata", {}).get("total_files"),
          f"manifest entries={len(expected_files)} declared={m.get('metadata', {}).get('total_files')}")

    # --- 2. Open archive and build member set ----------------------------
    try:
        tf = tarfile.open(archive, "r:gz")
    except Exception as exc:
        report.append(f"[FAIL] cannot open archive (gzip/TAR error): {exc}")
        return False, "\n".join(report)

    members = {}
    for member in tf.getmembers():
        # Path safety: reject absolute, traversal, drive-relative, backslashes.
        name = member.name
        if name.startswith("/") or name.startswith("\\"):
            check(f"Member path absolute (rejected): {name}", False)
            failures += 1
            continue
        if ".." in name.split("/"):
            check(f"Member path traversal (rejected): {name}", False)
            failures += 1
            continue
        if name.startswith(("C:", "D:", "\\\\")):
            check(f"Member path drive-relative (rejected): {name}", False)
            failures += 1
            continue
        members[name] = member

    tf.close()

    # --- 3. Expected files present? --------------------------------------
    missing = sorted(set(expected_files) - set(members))
    if missing:
        check("Missing files in archive", False, f"missing={missing}")
    else:
        check("Missing files in archive", True, f"files present={len(members)}")

    # --- 4. Hash verification --------------------------------------------
    hash_failures = []
    for rel, entry in sorted(expected_files.items()):
        if rel not in members:
            continue
        member = members[rel]
        try:
            f = tf.extractfile(member)
            if f is None:
                hash_failures.append(f"{rel}: cannot extract")
                continue
            data = f.read()
            computed = sha256_of_bytes(data)
            if computed != entry["sha256"]:
                hash_failures.append(f"{rel}: expected={entry['sha256'][:12]} got={computed[:12]}")
        except Exception as exc:
            hash_failures.append(f"{rel}: {exc}")

    if hash_failures:
        check("SHA-256 hash verification", False, f"failures={hash_failures}")
    else:
        check("SHA-256 hash verification", True, f"hashes verified for {len(expected_files)} files")

    # --- 5. Unexpected files in archive ----------------------------------
    unexpected = sorted(set(members) - set(expected_files))
    if unexpected:
        check("Unexpected archive files", False, f"unexpected={unexpected}")
    else:
        check("Unexpected archive files", True, f"no unexpected files")

    # --- 6. JSON metadata ------------------------------------------------
    metadata = m.get("metadata", {})
    check("Manifest JSON structure", "files" in m and "metadata" in m and "files" in m["metadata"])

    # --- 7. Archive-level SHA-256 -----------------------------------------
    h = hashlib.sha256()
    with open(archive, "rb") as _af:
        for _chunk in iter(lambda: _af.read(1024 * 1024), b""):
            h.update(_chunk)
    archive_sha = h.hexdigest()
    check("Archive-level SHA-256", metadata.get("archive_sha256") == archive_sha,
          f"manifest={metadata.get('archive_sha256')[:12]} archive={archive_sha[:12]}")

    # --- 8. Exit-code semantics ------------------------------------------
    ok = failures == 0
    report.append(f"\nRESULT: {'PASS' if ok else 'FAIL'} (failures={failures})")
    return ok, "\n".join(report)


def main():
    parser = argparse.ArgumentParser(
        description="Verify an archive against its SHA-256 manifest.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--archive", required=True, help="Archive file (.tar.gz).")
    parser.add_argument("--manifest", required=True, help="Manifest JSON file.")
    args = parser.parse_args()

    ok, report = verify_archive(args.archive, args.manifest)
    print(report)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
