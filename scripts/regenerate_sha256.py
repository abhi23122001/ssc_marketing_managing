#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Regenerate the .sha256 checksum file for a completed Phase 5A backup."""
import hashlib
import json
import sys
from pathlib import Path

def sha256_of_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def main():
    if len(sys.argv) != 3:
        print("usage: regenerate_sha256.py <backup-dir> <archive-name>")
        return 2
    dest = Path(sys.argv[1]).resolve()
    archive = (dest / sys.argv[2]).resolve()
    manifest = dest / "ssc_marketing_manifest.json"
    if not archive.is_file() or not manifest.is_file():
        print("missing archive or manifest:", archive, manifest)
        return 1
    m = json.loads(manifest.read_text(encoding="utf-8"))
    out = dest / "ssc_marketing_managing.sha256"
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(m["metadata"]["archive_sha256"] + "  " + archive.name + "\n")
        for entry in m["files"]:
            fh.write(entry["sha256"] + "  " + entry["relative_path"] + "\n")
    print("Regenerated:", out)
    print("lines:", sum(1 for _ in open(out, encoding="utf-8")))
    print("archive sha256:", m["metadata"]["archive_sha256"])
    return 0

if __name__ == "__main__":
    sys.exit(main())
