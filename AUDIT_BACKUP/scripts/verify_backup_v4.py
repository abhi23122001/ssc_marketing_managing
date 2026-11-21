#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Quick verification for a Phase 5A v4 backup (archive + manifest + hashes)."""
import hashlib
import json
import sys
import tarfile
from pathlib import Path

BACKUP = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(
    "/c/backups/ssc_marketing_managing_backup_20261118-20261118-032550").resolve()
ARCHIVE = BACKUP / "ssc_marketing_managing.tar.gz"
MANIFEST = BACKUP / "ssc_marketing_manifest.json"
SHA256_FILE = BACKUP / "ssc_marketing_managing.sha256"

def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1024*1024), b""):
            h.update(chunk)
    return h.hexdigest()

def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()

def main():
    print("Verifying backup:", BACKUP)
    ok = True

    # archive exists & gzip magic
    if not ARCHIVE.is_file():
        print("FAIL archive missing"); return 1
    magic = open(ARCHIVE, "rb").read(2)
    print("archive bytes:", ARCHIVE.stat().st_size,
          "gzip magic:", magic.hex() == "1f8b")
    if magic != b"\x1f\x8b":
        print("FAIL gzip magic"); ok = False
    else:
        print("PASS gzip magic")

    # open archive
    try:
        t = tarfile.open(ARCHIVE, "r:gz")
        members = t.getmembers()
        t.close()
    except Exception as e:
        print("FAIL open archive:", e); return 1
    print("members:", len(members))

    m = json.loads(MANIFEST.read_text(encoding="utf-8"))
    arc_sha = sha256_file(ARCHIVE)
    print("archive sha256:", arc_sha)
    print("manifest sha256:", m["metadata"]["archive_sha256"])
    if arc_sha != m["metadata"]["archive_sha256"]:
        print("FAIL archive sha mismatch"); ok = False
    else:
        print("PASS archive sha matches manifest")

    # no pack files
    packs = [mi.name for mi in members if "objects/pack-" in mi.name]
    print("pack files in archive:", len(packs))
    if packs:
        print("FAIL pack files present"); ok = False
    else:
        print("PASS no pack files")

    # per-file hashes
    expected = {e["relative_path"]: e["sha256"] for e in m["files"]}
    hash_bad = []
    with tarfile.open(ARCHIVE, "r:gz") as tf:
        members_by_name = {mi.name: mi for mi in tf.getmembers()}
        for rel, exp in sorted(expected.items()):
            if rel not in members_by_name:
                hash_bad.append(rel + ":missing-member"); continue
            f = tf.extractfile(members_by_name[rel])
            if f is None or sha256_bytes(f.read()) != exp:
                hash_bad.append(rel)
    print("per-file hash failures:", len(hash_bad))
    if hash_bad:
        print("FAIL hashes"); ok = False
    else:
        print("PASS all files hashes verified")

    # checksum file
    lines = open(SHA256_FILE, encoding="utf-8").read().splitlines()
    print("sha256 file lines:", len(lines))
    first = lines[0]
    print("checksum first line:", first)
    if not first.startswith(arc_sha + "  ssc_marketing_managing.tar.gz"):
        print("FAIL checksum header"); ok = False
    else:
        print("PASS checksum header")

    print("=" * 40)
    print("RESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())
