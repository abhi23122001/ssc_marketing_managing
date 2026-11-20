#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module 12 - Content Calendar & Content Generation (SHAH AI) - core.

Manages the M12 working content calendar (data/m12-content-calendar.csv) and
provides CSV tooling: list, view, add, export, validate, integrity-check.

All paths are resolved relative to the repository root. Everything is local;
there are no external accounts, APIs or paid services. Drafts are written to
outputs/ with an approval-required header and never leave the file system as
published content.

Run directly:
    python3 scripts/ContentCalendar.py list
    python3 scripts/ContentCalendar.py add --date "2026-W48" ...
"""
import argparse
import csv
import sys
from datetime import date
from pathlib import Path

# --- Paths -----------------------------------------------------------------
HERE = Path(__file__).resolve()
REPO_ROOT = None
for candidate in [HERE] + list(HERE.parents):
    if (Path(candidate) / "modules").is_dir():
        REPO_ROOT = Path(candidate)
        break
if REPO_ROOT is None:
    REPO_ROOT = Path.cwd().resolve()

DEFAULT_CALENDAR = REPO_ROOT / "data" / "m12-content-calendar.csv"
SHARED_TEMPLATES = REPO_ROOT / "shared" / "templates"
OUTPUTS_DIR = REPO_ROOT / "outputs"
DEFAULT_OUT_DIR = OUTPUTS_DIR / "12"


# --- Calendar schema (M12 board; deliberately NOT the shared leads.csv) ----
FIELDNAMES = [
    "id",
    "date_proposal",
    "platform",
    "content_pillar",
    "topic",
    "format",
    "target_audience",
    "language",
    "status",
    "proof_required",
    "owner",
    "approval_record",
]


# --- CSV helpers -----------------------------------------------------------
def ensure_header(path: Path, fieldnames):
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="", encoding="utf-8") as fh:
            csv.DictWriter(fh, fieldnames=fieldnames, lineterminator="\n").writeheader()
        return False
    return True


def load_rows(path: Path):
    if not path.exists():
        return []
    with path.open("r", newline="", encoding="utf-8") as fh:
        for line in fh:
            if line.lstrip().startswith("#"):
                continue
        fh.seek(0)
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            return []
        return list(reader)


def save_rows(path: Path, rows, fieldnames):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    with tmp.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: (row.get(k) or "") for k in fieldnames})
    tmp.replace(path)


def next_id(rows):
    ids = [int(r.get("id", "0")) for r in rows]
    return (max(ids) + 1) if ids else 1


# --- Validation ------------------------------------------------------------
def validate_row(row, index, fieldnames):
    issues = []
    for field in fieldnames:
        val = (row.get(field) or "").strip()
        if not val:
            issues.append("row {}: {} is required".format(index, field))
    if "status" in row and row["status"].strip() not in {"DRAFT", "PENDING", "APPROVED"}:
        issues.append("row {}: status {!r} must be DRAFT/PENDING/APPROVED".format(index, row["status"]))
    return issues


# --- Commands --------------------------------------------------------------
def cmd_list(args, path: Path):
    rows = load_rows(path)
    print("=== M12 Content Calendar ({}) ===".format(len(rows)))
    if not rows:
        print("(empty — add your first row with `add`)")
        return
    print("{:<5} {:<10} {:<6} {:<26} {:<22} {:<6} {}".format(
        "id", "date", "status", "platform", "topic", "lang", "owner"))
    for r in rows:
        print("{:<5} {:<10} {:<6} {:<26} {:<22} {:<6} {}".format(
            (r.get("id") or ""), (r.get("date_proposal") or "")[:9], r.get("status") or "",
            (r.get("platform") or "")[:25], (r.get("topic") or "")[:21], (r.get("language") or "")[:4],
            r.get("owner") or ""))


def cmd_view(args, path: Path):
    rows = load_rows(path)
    print("=== M12 Content Calendar (view) ===")
    for r in rows:
        print("---")
        for k in FIELDNAMES:
            print("  {}: {}".format(k, r.get(k, "")))
        print("  draft_output: {}".format(r.get("draft_output", "")))


def cmd_add(args, path: Path):
    rows = load_rows(path)
    new = {f: (getattr(args, f) if hasattr(args, f) else "") for f in FIELDNAMES}
    new["id"] = str(next_id(rows))
    # Keep the board usable without forcing the user to repeat fields:
    # content_pillar defaults to the topic; approval_record defaults to "not yet".
    if not new.get("content_pillar"):
        new["content_pillar"] = new.get("topic", "")
    if not new.get("approval_record"):
        new["approval_record"] = "not yet"
    issues = validate_row(new, len(rows) + 1, FIELDNAMES)
    if issues:
        print("Cannot add: {}".format("; ".join(issues)))
        return
    rows.append(new)
    save_rows(path, rows, FIELDNAMES)
    print("Added row #{} | {} | {} | {}\n{}".format(
        new["id"], new.get("date_proposal") or "", new.get("platform") or "",
        new.get("topic") or "", new.get("language") or ""))


def cmd_export(args, path: Path):
    src = Path(args.out) if getattr(args, "out", None) else DEFAULT_CALENDAR
    rows = load_rows(path)
    src.parent.mkdir(parents=True, exist_ok=True)
    with src.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDNAMES, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: (row.get(k) or "") for k in FIELDNAMES})
    print("Exported {} row(s) -> {}".format(len(rows), src))


def cmd_validate(args, path: Path):
    rows = load_rows(path)
    if not rows:
        print("No calendar rows to validate.")
        return
    total_issues = 0
    for i, row in enumerate(rows, 1):
        for issue in validate_row(row, i, FIELDNAMES):
            print("row {}: {}".format(i, issue))
            total_issues += 1
    if total_issues == 0:
        print("OK: {} row(s) passed validation.".format(len(rows)))
    else:
        print("FAILED: {} row(s) with issues.".format(total_issues))
        sys.exit(1)


def cmd_integrity_check(args, path: Path):
    rows = load_rows(path)
    issues = []
    seen_ids = set()
    for i, row in enumerate(rows, 1):
        for field in FIELDNAMES:
            if not (row.get(field) or "").strip():
                issues.append("row {}: missing field {}".format(i, field))
        rid = row.get("id", "")
        if rid in seen_ids:
            issues.append("row {}: duplicate id {}".format(i, rid))
        seen_ids.add(rid)
    if issues:
        print("INTEGRITY CHECK FAILED: {} issue(s):".format(len(issues)))
        for issue in issues:
            print("  - " + issue)
        sys.exit(1)
    print("INTEGRITY CHECK OK: {} row(s), all fields complete, unique ids.".format(len(rows)))


# --- main ------------------------------------------------------------------
def build_parser():
    p = argparse.ArgumentParser(prog="ContentCalendar.py", description="SHAH AI Module 12 Content Calendar")
    sub = p.add_subparsers(dest="command", required=True)

    def add_common(sub):
        sub.add_argument("--data", type=Path, default=DEFAULT_CALENDAR, help="Path to m12-content-calendar.csv")

    sp = sub.add_parser("list", help="List calendar rows")
    add_common(sp)
    sp.set_defaults(func=cmd_list)

    sp = sub.add_parser("view", help="Show one row in full")
    add_common(sp)
    sp.add_argument("id", nargs="?", default=None, help="Row id (default: first)")
    sp.set_defaults(func=cmd_view)

    sp = sub.add_parser("add", help="Add a calendar row")
    add_common(sp)
    for f in FIELDNAMES:
        sp.add_argument("--" + f, default=None, help="Row field value")
    sp.set_defaults(func=cmd_add)

    sp = sub.add_parser("export", help="Export to CSV")
    add_common(sp)
    sp.add_argument("--out", type=Path, default=DEFAULT_CALENDAR, help="Output path")
    sp.set_defaults(func=cmd_export)

    sp = sub.add_parser("validate", help="Validate all rows")
    add_common(sp)
    sp.set_defaults(func=cmd_validate)

    sp = sub.add_parser("integrity-check", help="Verify completeness and uniqueness")
    add_common(sp)
    sp.set_defaults(func=cmd_integrity_check)

    return p


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args, args.data)
    return 0


if __name__ == "__main__":
    sys.exit(main())
