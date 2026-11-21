#!/usr/bin/env python3
"""
SHAH AI - Module 06 Contractor Lead Research & CRM (core).

Local-first lead management for Shah Surveyors & Consultancy (SSC).
Reads/writes a CSV file at data/leads.csv. No external accounts, APIs or
paid services. Everything is local and draft-inspection in nature.

Subcommands:
  add, list, search, edit, delete, dashboard, backup, import, export,
  validate, rebuild-sample

Run directly:
  python3 scripts/CRM-Leads.py add --company "..." ...
  python3 scripts/CRM-Leads.py dashboard
  python3 scripts/CRM-Leads.py -h        (help)
"""

import argparse
import csv
import shutil
import sys
from datetime import date, datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Repository root resolution. The script may live anywhere under the repo;
# walk up until a 'modules' directory is found.
# ---------------------------------------------------------------------------
def find_repo_root() -> Path:
    candidate = Path(__file__).resolve()
    for parent in [candidate, *candidate.parents]:
        if (parent / "modules").is_dir():
            return parent
    # Fallback: current working directory
    return Path.cwd().resolve()


REPO_ROOT = find_repo_root()
DEFAULT_DATA = REPO_ROOT / "data" / "leads.csv"

VALID_PRIORITIES = {"High", "Medium", "Low"}
VALID_STAGES = {"New", "Contacted", "Qualified", "Disqualified", "Customer", "Unqualified"}
VALID_VERIFICATION = {"Confirmed", "Unconfirmed", "Unverified"}
VALID_QUALIFICATION = {"Qualified", "Partial", "Unqualified", "Pending"}
VALID_LEAD_SOURCE = {"Public profile", "Public directory", "Reference", "Manual research", "Enumeration"}

# ---------------------------------------------------------------------------
# CSV helpers
# ---------------------------------------------------------------------------
def ensure_header(path: Path, fieldnames):
    """Create the file with a header row if it does not exist yet."""
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="", encoding="utf-8") as fh:
            csv.DictWriter(fh, fieldnames=fieldnames, lineterminator="\n").writeheader()
        return False
    return True


def load_rows(path: Path):
    """Load rows, skipping any lines that start with '#' (comments)."""
    rows = []
    if not path.exists():
        return rows
    with path.open("r", newline="", encoding="utf-8") as fh:
        for line in fh:
            stripped = line.lstrip()
            if stripped.startswith("#"):
                continue
        fh.seek(0)
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            return rows
        for row in reader:
            rows.append(row)
    return rows


def save_rows(path: Path, rows, fieldnames):
    """Write rows, preserving comment header rows if present."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    with tmp.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: (row.get(k) or "") for k in fieldnames})
    shutil.move(str(tmp), str(path))


def normalize_company(value: str) -> str:
    return " ".join(str(value).split()).lower()


def candidate_key(row) -> tuple:
    """Deduplication key: normalized company + domain of website + normalized email."""
    company = normalize_company(row.get("company"))
    website = str(row.get("website") or "").strip().lower()
    domain = ""
    if website and website.startswith("http"):
        try:
            domain = website.split("//", 1)[1].split("/", 1)[0]
        except Exception:
            domain = website
    email = normalize_company(row.get("email"))
    return (company, domain, email)


def find_duplicates(rows):
    seen = {}
    dups = []
    for i, row in enumerate(rows):
        key = candidate_key(row)
        if key in seen:
            dups.append((i, seen[key], row.get("company"), key))
        else:
            seen[key] = i
    return dups


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------
def validate_row(row, index, fieldnames):
    """Return a list of human-readable validation issues."""
    issues = []
    company = (row.get("company") or "").strip()
    website = (row.get("website") or "").strip()
    if not company:
        issues.append("row {}: company is required".format(index))
    if not website:
        issues.append("row {}: website is required".format(index))
    if not (row.get("city") or "").strip():
        issues.append("row {}: city is required".format(index))
    phone = (row.get("phone") or "").strip()
    if phone and not (phone.startswith("+") or phone[:1].isdigit()):
        issues.append("row {}: phone does not look like a phone number: {!r}".format(index, phone))
    email = (row.get("email") or "").strip()
    if email and "@" not in email:
        issues.append("row {}: email does not look valid: {!r}".format(index, email))
    stage = (row.get("stage") or "").strip()
    if stage and stage not in VALID_STAGES:
        issues.append("row {}: stage {!r} not in {}".format(index, stage, sorted(VALID_STAGES)))
    priority = (row.get("priority") or "").strip()
    if priority and priority not in VALID_PRIORITIES:
        issues.append("row {}: priority {!r} not in {}".format(index, priority, sorted(VALID_PRIORITIES)))
    verification = (row.get("verification_status") or "").strip()
    if verification and verification not in VALID_VERIFICATION:
        issues.append("row {}: verification_status {!r} not in {}".format(index, verification, sorted(VALID_VERIFICATION)))
    qs = (row.get("qualification_status") or "").strip()
    if qs and qs not in VALID_QUALIFICATION:
        issues.append("row {}: qualification_status {!r} not in {}".format(index, qs, sorted(VALID_QUALIFICATION)))
    return issues


# ---------------------------------------------------------------------------
# Backup
# ---------------------------------------------------------------------------
def do_backup(path: Path):
    if not path.exists():
        print("No lead data to back up.")
        return
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    dest = path.with_name("_backup_{}_{}.csv".format(path.stem, stamp))
    shutil.copy2(str(path), str(dest))
    print("Backup written: {}".format(dest))


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------
def do_dashboard(path: Path, today: date):
    rows = load_rows(path)
    total = len(rows)
    verified = [r for r in rows if (r.get("verification_status") or "").strip() == "Confirmed"]
    unverified = [r for r in rows if (r.get("verification_status") or "").strip() != "Confirmed"]

    category_counts = {}
    location_counts = {}
    for r in rows:
        cat = (r.get("business_category") or "").strip()
        if cat:
            category_counts[cat] = category_counts.get(cat, 0) + 1
        loc = (r.get("city") or "").strip()
        if loc:
            location_counts[loc] = location_counts.get(loc, 0) + 1

    # Follow-up: due when follow_up_date <= today and not a closed customer
    due = []
    overdue = []
    for r in rows:
        fu = (r.get("follow_up_date") or "").strip()
        stage = (r.get("stage") or "").strip()
        if fu:
            try:
                fu_date = datetime.strptime(fu, "%Y-%m-%d").date()
            except ValueError:
                fu_date = None
            if fu_date and fu_date <= today and stage not in ("Customer", "Disqualified"):
                if fu_date < today:
                    overdue.append(r)
                else:
                    due.append(r)

    status_summary = {}
    for r in rows:
        st = (r.get("stage") or "").strip()
        status_summary[st] = status_summary.get(st, 0) + 1

    print("=== SHAH AI - Contractor Lead CRM Dashboard ===")
    print("Total leads:            {}".format(total))
    print("Verified leads:         {}".format(len(verified)))
    print("Unverified leads:       {}".format(len(unverified)))
    print("Category counts:        {}".format(dict(sorted(category_counts.items()))))
    print("Location counts:        {}".format(dict(sorted(location_counts.items()))))
    print("Follow-up due:          {}".format(len(due)))
    print("Follow-up overdue:      {}".format(len(overdue)))
    print("Stage summary:          {}".format(dict(sorted(status_summary.items()))))
    if due:
        print("  Due:")
        for r in due:
            print("    - {} (follow up {})".format(r.get("company"), r.get("follow_up_date")))
    if overdue:
        print("  Overdue:")
        for r in overdue:
            print("    - {} (follow up {}, {})".format(r.get("company"), r.get("follow_up_date"), (r.get("notes") or "").rstrip()))

    return {
        "total": total,
        "verified": len(verified),
        "unverified": len(unverified),
        "category_counts": category_counts,
        "location_counts": location_counts,
        "due": due,
        "overdue": overdue,
        "status_summary": status_summary,
    }


# ---------------------------------------------------------------------------
# Subcommands
# ---------------------------------------------------------------------------
def cmd_add(args, path: Path):
    rows = load_rows(path)
    # Build new row
    new = {}
    for field in fieldnames:
        val = getattr(args, field, None)
        new[field] = (val if val is not None else "") 
    # For fields not passed but required, leave empty (except company/website which are required)
    # Dedup check
    key = candidate_key(new)
    for i, r in enumerate(rows):
        if candidate_key(r) == key:
            print("WARNING: row {} already exists (company={!r}, website={!r}). Not adding duplicate.".format(i, new.get("company"), new.get("website")))
            return
    rows.append(new)
    save_rows(path, rows, fieldnames)
    print("Added lead #{}: {} ({})".format(len(rows), new.get("company"), new.get("city")))
    print("Total leads now: {}".format(len(rows)))


def cmd_list(args, path: Path):
    rows = load_rows(path)
    if not rows:
        print("No lead records.")
        return
    limit = args.limit or len(rows)
    print("=== Leads ({}) ===".format(len(rows)))
    print("{:<4} {:<34} {:<14} {:<12} {:<10} {:<10} {:<11}".format(
        "id", "company", "city", "stage", "priority", "verif", "qual"))
    for i, r in enumerate(rows[:limit], 1):
        print("{:<4} {:<34} {:<14} {:<12} {:<10} {:<11} {:<11}".format(
            i,
            (r.get("company") or "")[:33],
            (r.get("city") or "")[:13],
            (r.get("stage") or "")[:11],
            (r.get("priority") or "")[:9],
            (r.get("verification_status") or "")[:10],
            (r.get("qualification_status") or "")[:10],
        ))


def cmd_search(args, path: Path):
    rows = load_rows(path)
    if not rows:
        print("No lead records.")
        return
    query = args.query.lower()
    matches = []
    for r in rows:
        blob = " ".join(str(r.get(k) or "") for k in r).lower()
        if query in blob:
            matches.append(r)
    if not matches:
        print("No matches for {!r}.".format(args.query))
        return
    print("=== Search results for {!r} ({} matches) ===".format(args.query, len(matches)))
    for i, r in enumerate(matches, 1):
        print("{}) {} | {} | {} | {} | {} | {}".format(
            i, r.get("company"), r.get("city"), r.get("stage"),
            r.get("priority"), r.get("verification_status"), r.get("qualification_status")))


def cmd_edit(args, path: Path):
    rows = load_rows(path)
    company = (args.company or "").strip()
    if not company:
        print("ERROR: --company is required to identify the row.")
        return
    matches = [r for r in rows if normalize_company(r.get("company")) == normalize_company(company)]
    if not matches:
        print("No rows found for company {!r}.".format(company))
        return
    if len(matches) > 1:
        if not args.row_index:
            print("ERROR: {} rows match {!r}. Use --row-index <n> to choose.".format(len(matches), company))
            return
        idx = int(args.row_index)
        if idx < 0 or idx >= len(matches):
            print("ERROR: --row-index {} out of range (0..{}).".format(idx, len(matches)-1))
            return
        target = matches[idx]
    else:
        target = matches[0]

    overrides = {}
    for pair in args.set:
        if "=" in pair:
            k, v = pair.split("=", 1)
            overrides[k.strip()] = v.strip()
    for field in fieldnames:
        target[field] = overrides.get(field, target.get(field, ""))
    save_rows(path, rows, fieldnames)
    print("Updated: {} (row {}).".format(target.get("company"), target.get("company")))


def cmd_delete(args, path: Path):
    rows = load_rows(path)
    company = (args.company or "").strip()
    if not company:
        print("ERROR: --company is required.")
        return
    matches = [r for r in rows if normalize_company(r.get("company")) == normalize_company(company)]
    if not matches:
        print("No rows found for company {!r}.".format(company))
        return
    if len(matches) > 1:
        if not args.row_index:
            print("ERROR: {} rows match {!r}. Use --row-index <n>.".format(len(matches), company))
            return
        idx = int(args.row_index)
        if idx < 0 or idx >= len(matches):
            print("ERROR: --row-index {} out of range.".format(idx))
            return
        target = matches[idx]
    else:
        target = matches[0]
    rows.remove(target)
    save_rows(path, rows, fieldnames)
    print("Deleted: {} (row {}).".format(target.get("company"), target.get("company")))


def cmd_import(args, path: Path):
    src = Path(args.file)
    if not src.exists():
        print("ERROR: import file not found: {}".format(src))
        return
    incoming = load_rows(src)
    if not incoming:
        print("No data rows found in {}".format(src))
        return
    existing = load_rows(path)
    # Validate incoming rows
    issues = 0
    for i, row in enumerate(incoming, 1):
        for issue in validate_row(row, i, fieldnames):
            print("  ISSUE row {}: {}".format(i, issue))
            issues += 1
    if issues:
        print("Cannot import: {} invalid row(s). Fix them and retry.".format(issues))
        return
    # Dedup against existing
    dupes = 0
    merged = []
    added = 0
    for row in incoming:
        if any(candidate_key(row) == candidate_key(ex) for ex in existing + merged):
            dupes += 1
        else:
            merged.append(row)
            added += 1
    if dupes:
        print("Skipped {} duplicate row(s).".format(dupes))
    if added == 0:
        print("No new rows added.")
        return
    # Backup then save
    do_backup(path)
    existing.extend(merged)
    save_rows(path, existing, fieldnames)
    print("Imported {} row(s) -> {}. Total leads: {}.".format(added, path, len(existing)))


def cmd_export(args, path: Path):
    src = Path(args.file)
    rows = load_rows(path)
    src.parent.mkdir(parents=True, exist_ok=True)
    with src.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: (row.get(k) or "") for k in fieldnames})
    print("Exported {} row(s) -> {}".format(len(rows), src))


def cmd_validate(args, path: Path):
    rows = load_rows(path)
    if not rows:
        print("No lead records to validate.")
        return
    issues_total = 0
    for i, row in enumerate(rows, 1):
        for issue in validate_row(row, i, fieldnames):
            print("row {}: {}".format(i, issue))
            issues_total += 1
    if issues_total == 0:
        print("OK: {} rows passed validation.".format(len(rows)))
    else:
        print("FAILED: {} row(s) with issues.".format(issues_total))
        return 1


def cmd_rebuild_sample(args, path: Path):
    sample = [
        {"company":"RudraX Mapping Solutions","business_category":"Geospatial / Survey Services","city":"Bhopal","state":"Madhya Pradesh","address":"","phone":"","email":"","website":"https://www.linkedin.com/company/rudrax-mapping-solution","source_url":"https://www.linkedin.com/company/rudrax-mapping-solution","source_date_checked":"2026-11-17","lead_acquired_date":"2026-11-17","verification_status":"Confirmed","priority":"Medium","stage":"New","follow_up_date":"","notes":"Public-profile lead; verify full contact details before outreach.","qualification_status":"Qualified","lead_source":"Public profile (LinkedIn)"},
        {"company":"Complete Surveying Solutions","business_category":"Geospatial / Survey Services","city":"Indore","state":"Madhya Pradesh","address":"","phone":"","email":"","website":"https://www.linkedin.com/company/complete-surveying-solutions","source_url":"https://www.linkedin.com/company/complete-surveying-solutions","source_date_checked":"2026-11-17","lead_acquired_date":"2026-11-17","verification_status":"Confirmed","priority":"Medium","stage":"New","follow_up_date":"","notes":"Public-profile lead; drone, DGPS, topographical and geospatial.","qualification_status":"Qualified","lead_source":"Public profile (LinkedIn)"},
        {"company":"Shahi Construction","business_category":"Construction / Survey Services","city":"Bhopal","state":"Madhya Pradesh","address":"","phone":"","email":"","website":"https://www.shahisurvey.in","source_url":"https://www.shahisurvey.in/survey-services.html","source_date_checked":"2026-11-17","lead_acquired_date":"2026-11-17","verification_status":"Confirmed","priority":"Low","stage":"New","follow_up_date":"","notes":"Public-profile lead; topographic total-station and land surveying.","qualification_status":"Partial","lead_source":"Public directory (survey-services page)"},
        {"company":"BBPL Building Atelier","business_category":"Survey / Building Construction","city":"Gwalior","state":"Madhya Pradesh","address":"","phone":"","email":"","website":"https://www.bbapl.in","source_url":"https://www.bbapl.in/service/survey-services/","source_date_checked":"2026-11-17","lead_acquired_date":"2026-11-17","verification_status":"Confirmed","priority":"High","stage":"New","follow_up_date":"","notes":"Public-profile lead; land/building surveys, total station, DGPS, drone.","qualification_status":"Qualified","lead_source":"Public profile (website service page)"},
    ]
    save_rows(path, sample, fieldnames)
    print("Rebuilt sample lead data (4 rows) in {} -> {}".format(path, "rebuilt"))


# ---- main ------------------------------------------------------------------
fieldnames = [
    "company", "business_category", "city", "state", "address", "phone", "email",
    "website", "source_url", "source_date_checked", "lead_acquired_date",
    "verification_status", "priority", "stage", "follow_up_date", "notes",
    "qualification_status", "lead_source",
]

def build_parser():
    p = argparse.ArgumentParser(prog="CRM-Leads.py", description="SHAH AI Module 06 Lead CRM")
    sub = p.add_subparsers(dest="command", required=True)

    def add_common(sub):
        sub.add_argument("--data", type=Path, default=DEFAULT_DATA, help="Path to leads.csv (default: data/leads.csv)")

    sp = sub.add_parser("add", help="Add a lead")
    add_common(sp)
    for f in fieldnames:
        sp.add_argument("--" + f, default=None, help="Lead field value (for phone/email/address use quotes)")
    sp.set_defaults(func=cmd_add)

    sp = sub.add_parser("list", help="List leads")
    add_common(sp)
    sp.add_argument("--limit", type=int, default=None)
    sp.set_defaults(func=cmd_list)

    sp = sub.add_parser("search", help="Search leads")
    add_common(sp)
    sp.add_argument("--query", required=True)
    sp.set_defaults(func=cmd_search)

    sp = sub.add_parser("edit", help="Edit a lead")
    add_common(sp)
    sp.add_argument("--company", required=True)
    sp.add_argument("--row-index", type=int, default=None)
    sp.add_argument("--set", action="append", default=[], help="field=value (repeat)")
    sp.set_defaults(func=cmd_edit)

    sp = sub.add_parser("delete", help="Delete a lead")
    add_common(sp)
    sp.add_argument("--company", required=True)
    sp.add_argument("--row-index", type=int, default=None)
    sp.set_defaults(func=cmd_delete)

    sp = sub.add_parser("dashboard", help="Show CRM dashboard")
    add_common(sp)
    sp.add_argument("--today", type=lambda s: datetime.strptime(s, "%Y-%m-%d").date(), default=None)
    sp.set_defaults(func=cmd_dashboard)

    sp = sub.add_parser("backup", help="Backup lead data")
    add_common(sp)
    sp.set_defaults(func=cmd_backup)

    sp = sub.add_parser("import", help="Import leads from CSV")
    add_common(sp)
    sp.add_argument("--file", required=True)
    sp.set_defaults(func=cmd_import)

    sp = sub.add_parser("export", help="Export leads to CSV")
    add_common(sp)
    sp.add_argument("--file", required=True)
    sp.set_defaults(func=cmd_export)

    sp = sub.add_parser("validate", help="Validate lead data")
    add_common(sp)
    sp.set_defaults(func=cmd_validate)

    sp = sub.add_parser("rebuild-sample", help="Restore the embedded sample lead set")
    add_common(sp)
    sp.set_defaults(func=cmd_rebuild_sample)

    return p

def cmd_dashboard(args, path):
    today = args.today or date.today()
    do_dashboard(path, today)

def cmd_backup(args, path):
    do_backup(path)

def cmd_dashboard_main(args):
    do_dashboard(args.data, args.today or date.today())

def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args, args.data)

if __name__ == "__main__":
    sys.exit(main())
