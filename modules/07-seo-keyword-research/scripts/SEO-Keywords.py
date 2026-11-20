#!/usr/bin/env python3
"""
SHAH AI - Module 07 SEO & Keyword Research (core).

Local-first SEO planning and research for Shah Surveyors & Consultancy (SSC).
Reads/writes a CSV at data/keywords.csv. No external accounts, APIs, or paid
services. Search volumes / competition are only ever recorded when a verified
source supports them - otherwise they stay blank or 'Unverified'.

Subcommands:
  add, list, search, edit, delete, validate, import, export,
  cluster, report, local, rebuild-sample

Run directly:
  python3 scripts/SEO-Keywords.py add --keyword "..." ...
  python3 scripts/SEO-Keywords.py report --out 07-seo-plan.md
  python3 scripts/SEO-Keywords.py -h        (help)
"""

import argparse
import csv
import shutil
from datetime import date, datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Repository root resolution.
# ---------------------------------------------------------------------------
def find_repo_root() -> Path:
    candidate = Path(__file__).resolve()
    for parent in [candidate, *candidate.parents]:
        if (parent / "modules").is_dir():
            return parent
    return Path.cwd().resolve()


REPO_ROOT = find_repo_root()
DEFAULT_DATA = REPO_ROOT / "data" / "keywords.csv"

# Intent vocabulary used across the seed set.
INTENT_VALUES = {"informational", "local-info", "service", "transactional"}

# ---------------------------------------------------------------------------
# CSV helpers
# ---------------------------------------------------------------------------
def load_rows(path: Path):
    rows = []
    if not path.exists():
        return rows
    with path.open("r", newline="", encoding="utf-8") as fh:
        for line in fh:
            if line.lstrip().startswith("#"):
                continue
        fh.seek(0)
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            return rows
        for row in reader:
            rows.append(row)
    return rows


def save_rows(path: Path, rows, fieldnames):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    with tmp.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: (row.get(k) or "") for k in fieldnames})
    shutil.move(str(tmp), str(path))


def normalize_keyword(value: str) -> str:
    return " ".join(str(value).split()).lower()


def candidate_key(row) -> str:
    return normalize_keyword(row.get("keyword"))


def trim(value: str) -> str:
    return (value or "").strip()


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------
def validate_row(row, index, fieldnames):
    issues = []
    keyword = trim(row.get("keyword"))
    if not keyword:
        issues.append("row {}: keyword is required".format(index))
        return issues  # nothing else to validate without a keyword
    service = trim(row.get("target_service"))
    location = trim(row.get("target_location"))
    intent = trim(row.get("search_intent"))
    if not service:
        issues.append("row {}: target_service is required".format(index))
    if not location:
        issues.append("row {}: target_location is required".format(index))
    if intent:
        tokens = [t.strip() for t in intent.replace("/", " ").split() if t.strip()]
        for token in tokens:
            if token not in INTENT_VALUES:
                issues.append("row {}: search_intent {!r} contains invalid token {!r}".format(index, intent, token))
    # Competition / volume only when supported by a verified source.
    comp = trim(row.get("competition"))
    if comp and comp not in {"Low", "Medium", "High", "Unverified"}:
        issues.append("row {}: competition {!r} must be Low/Medium/High or Unverified".format(index, comp))
    volume = trim(row.get("search_volume"))
    if volume and not volume.isdigit():
        issues.append("row {}: search_volume must be an integer or blank, got {!r}".format(index, volume))
    return issues


# ---------------------------------------------------------------------------
# Rebuild embedded sample
# ---------------------------------------------------------------------------
def rebuild_sample(path: Path):
    sample = [
        # Land / Topographical Survey (local)
        {"keyword":"land-survey-Singrauli","primary_keyword":"land survey singrauli",
         "secondary_keywords":"topographical survey singrauli, land surveying singrauli, survey company singrauli",
         "search_intent":"local-info","target_service":"Land Survey","target_location":"Singrauli",
         "cluster":"Land Survey / Local","competition":"Unverified","search_volume":"",
         "source_url":"","research_date":"2026-11-17"},
        {"keyword":"topographical-survey-Waidhan","primary_keyword":"topographical survey waidhan",
         "secondary_keywords":"topo survey waidhan, survey singrauli, waidhan survey",
         "search_intent":"local-info","target_service":"Topographical Survey","target_location":"Waidhan",
         "cluster":"Topographical Survey / Local","competition":"Unverified","search_volume":"",
         "source_url":"","research_date":"2026-11-17"},
        # Drone Survey
        {"keyword":"drone-survey-Madhya-Pradesh","primary_keyword":"drone survey madhya pradesh",
         "secondary_keywords":"aerial survey MP, drone mapping Madhya Pradesh, photogrammetry india",
         "search_intent":"local-info / informational","target_service":"Drone Survey",
         "target_location":"Madhya Pradesh","cluster":"Drone Survey / Regional",
         "competition":"Unverified","search_volume":"",
         "source_url":"https://www.linkedin.com/company/complete-surveying-solutions","research_date":"2026-11-17"},
        {"keyword":"drone-photogrammetry-site","primary_keyword":"drone photogrammetry site",
         "secondary_keywords":"aerial photogrammetry, drone mapping India, ortho mapping",
         "search_intent":"informational","target_service":"Drone Survey","target_location":"India",
         "cluster":"Drone Survey / National","competition":"Unverified","search_volume":"",
         "source_url":"https://www.linkedin.com/company/complete-surveying-solutions","research_date":"2026-11-17"},
        # LiDAR
        {"keyword":"liDAR-survey-India","primary_keyword":"LiDAR survey India",
         "secondary_keywords":"lidar mapping, airborne LiDAR, point cloud processing",
         "search_intent":"informational","target_service":"LiDAR Survey","target_location":"India",
         "cluster":"LiDAR Survey / National","competition":"Unverified","search_volume":"",
         "source_url":"","research_date":"2026-11-17"},
        # DGPS / Total Station
        {"keyword":"dgps-survey-total-station","primary_keyword":"DGPS survey total station India",
         "secondary_keywords":"RTK survey, total station survey, differential GPS India",
         "search_intent":"local-info / service","target_service":"DGPS Survey","target_location":"India",
         "cluster":"DGPS / Total Station Survey","competition":"Unverified","search_volume":"",
         "source_url":"https://shahisurvey.in","research_date":"2026-11-17"},
        {"keyword":"total-station-survey-Bhopal","primary_keyword":"total station survey Bhopal",
         "secondary_keywords":"total station contractor Bhopal, survey Bhopal MP",
         "search_intent":"local-info","target_service":"Total Station Survey","target_location":"Bhopal",
         "cluster":"Total Station Survey / Local","competition":"Unverified","search_volume":"",
         "source_url":"https://www.shahisurvey.in","research_date":"2026-11-17"},
        # GPR
        {"keyword":"gpr-survey-geophysical","primary_keyword":"GPR survey geophysical India",
         "secondary_keywords":"ground penetrating radar, subsurface survey India, geophysical survey",
         "search_intent":"informational","target_service":"GPR Survey","target_location":"India",
         "cluster":"GPR Survey / National","competition":"Unverified","search_volume":"",
         "source_url":"","research_date":"2026-11-17"},
        # Geospatial
        {"keyword":"geospatial-services-contractor","primary_keyword":"geospatial services contractor",
         "secondary_keywords":"GIS consultant India, mapping services India, survey contractor",
         "search_intent":"local-info","target_service":"Geospatial Services","target_location":"India",
         "cluster":"Geospatial Services / National","competition":"Unverified","search_volume":"",
         "source_url":"https://rudrax.com","research_date":"2026-11-17"},
        # Construction
        {"keyword":"construction-survey-site","primary_keyword":"construction survey site work",
         "secondary_keywords":"site survey for construction, construction layout, stakeout services",
         "search_intent":"service","target_service":"Construction Survey","target_location":"India",
         "cluster":"Construction Survey / National","competition":"Unverified","search_volume":"",
         "source_url":"https://bbapl.in","research_date":"2026-11-17"},
        {"keyword":"survey-services-EPC","primary_keyword":"survey services EPC contractor",
         "secondary_keywords":"EPC survey support, construction survey contractor, project survey",
         "search_intent":"service","target_service":"Construction / EPC Survey","target_location":"India",
         "cluster":"Construction / EPC Survey / National","competition":"Unverified","search_volume":"",
         "source_url":"","research_date":"2026-11-17"},
        # Mining
        {"keyword":"mining-survey-Singrauli","primary_keyword":"mining survey singrauli",
         "secondary_keywords":"mining survey MP, surveyor for mining, geological survey India",
         "search_intent":"local-info / service","target_service":"Mining Survey","target_location":"Singrauli",
         "cluster":"Mining Survey / Local","competition":"Unverified","search_volume":"",
         "source_url":"https://www.linkedin.com/company/rudrax-mapping-solution","research_date":"2026-11-17"},
        # Power & Solar
        {"keyword":"power-and-solar-survey","primary_keyword":"power and solar survey",
         "secondary_keywords":"solar project survey, solar resource assessment, PV layout survey, wind survey",
         "search_intent":"service","target_service":"Power and Solar Survey","target_location":"India",
         "cluster":"Power & Solar Survey / National","competition":"Unverified","search_volume":"",
         "source_url":"","research_date":"2026-11-17"},
        {"keyword":"solar-plant-survey","primary_keyword":"solar plant survey",
         "secondary_keywords":"solar farm survey, solar layout surveyor, SPV survey India",
         "search_intent":"service","target_service":"Power and Solar Survey","target_location":"India",
         "cluster":"Power & Solar Survey / National","competition":"Unverified","search_volume":"",
         "source_url":"","research_date":"2026-11-17"},
        {"keyword":"grid-transmission-survey","primary_keyword":"transmission line survey",
         "secondary_keywords":"transmission line topography, tower footing survey, line survey India",
         "search_intent":"service","target_service":"Power and Solar Survey","target_location":"India",
         "cluster":"Power & Solar Survey / National","competition":"Unverified","search_volume":"",
         "source_url":"","research_date":"2026-11-17"},
        # Local (Singrauli / Waidhan)
        {"keyword":"survey-company-Singrauli","primary_keyword":"survey company singrauli",
         "secondary_keywords":"topographical survey singrauli, survey firm singrauli, land surveyor singrauli",
         "search_intent":"local-info","target_service":"Land Survey","target_location":"Singrauli",
         "cluster":"Land Survey / Local","competition":"Unverified","search_volume":"",
         "source_url":"","research_date":"2026-11-17"},
        {"keyword":"survey-firm-Waidhan","primary_keyword":"survey firm waidhan",
         "secondary_keywords":"topographical survey waidhan, survey services madhya pradesh",
         "search_intent":"local-info","target_service":"Topographical Survey","target_location":"Waidhan",
         "cluster":"Topographical Survey / Local","competition":"Unverified","search_volume":"",
         "source_url":"","research_date":"2026-11-17"},
        {"keyword":"surveyor-MP-infrastructure","primary_keyword":"surveyor Madhya Pradesh infrastructure",
         "secondary_keywords":"infrastructure survey MP, highway survey, railway survey India",
         "search_intent":"service","target_service":"Construction / Infrastructure Survey","target_location":"Madhya Pradesh",
         "cluster":"Construction Survey / Regional","competition":"Unverified","search_volume":"",
         "source_url":"","research_date":"2026-11-17"},
        {"keyword":"cadastral-survey-land","primary_keyword":"cadastral survey land",
         "secondary_keywords":"revenue survey, land records survey, boundary survey India",
         "search_intent":"local-info / service","target_service":"Land Survey","target_location":"India",
         "cluster":"Land Survey / National","competition":"Unverified","search_volume":"",
         "source_url":"https://rudrax.com","research_date":"2026-11-17"},
        {"keyword":"contour-survey-topo","primary_keyword":"contour survey topography",
         "secondary_keywords":"contour mapping, topo sheet survey, elevation survey",
         "search_intent":"informational","target_service":"Topographical Survey","target_location":"India",
         "cluster":"Topographical Survey / National","competition":"Unverified","search_volume":"",
         "source_url":"","research_date":"2026-11-17"},
    ]
    save_rows(path, sample, fieldnames)
    print("Rebuilt sample keyword data ({}) -> {}".format(len(sample), path))


# ---- main ------------------------------------------------------------------
fieldnames = [
    "keyword", "primary_keyword", "secondary_keywords", "search_intent",
    "target_service", "target_location", "cluster", "competition", "search_volume",
    "source_url", "research_date",
]

def build_parser():
    p = argparse.ArgumentParser(prog="SEO-Keywords.py", description="SHAH AI Module 07 SEO & Keyword Research")
    sub = p.add_subparsers(dest="command", required=True)

    def add_common(sub):
        sub.add_argument("--data", type=Path, default=DEFAULT_DATA, help="Path to keywords.csv")

    sp = sub.add_parser("add", help="Add a keyword")
    add_common(sp)
    for f in fieldnames:
        sp.add_argument("--" + f, default=None, help="Keyword field value")
    sp.set_defaults(func=cmd_add)

    sp = sub.add_parser("list", help="List keywords")
    add_common(sp)
    sp.add_argument("--cluster")
    sp.add_argument("--target_service")
    sp.add_argument("--target_location")
    sp.add_argument("--search", default=None)
    sp.set_defaults(func=cmd_list)

    sp = sub.add_parser("search", help="Search keywords")
    add_common(sp)
    sp.add_argument("--query", required=True)
    sp.set_defaults(func=cmd_search)

    sp = sub.add_parser("edit", help="Edit a keyword")
    add_common(sp)
    sp.add_argument("--keyword", required=True)
    sp.add_argument("--set", action="append", default=[], help="field=value (repeat)")
    sp.set_defaults(func=cmd_edit)

    sp = sub.add_parser("delete", help="Delete a keyword")
    add_common(sp)
    sp.add_argument("--keyword", required=True)
    sp.set_defaults(func=cmd_delete)

    sp = sub.add_parser("validate", help="Validate keyword data")
    add_common(sp)
    sp.set_defaults(func=cmd_validate)

    sp = sub.add_parser("import", help="Import keywords from CSV")
    add_common(sp)
    sp.add_argument("--file", required=True)
    sp.set_defaults(func=cmd_import)

    sp = sub.add_parser("export", help="Export keywords to CSV")
    add_common(sp)
    sp.add_argument("--file", required=True)
    sp.set_defaults(func=cmd_export)

    sp = sub.add_parser("cluster", help="Group keywords by cluster -> service-page keyword map")
    add_common(sp)
    sp.add_argument("--target_service", default=None)
    sp.set_defaults(func=cmd_cluster)

    sp = sub.add_parser("local", help="List local (Singrauli / Waidhan / MP) keywords")
    add_common(sp)
    sp.set_defaults(func=cmd_local)

    sp = sub.add_parser("report", help="Generate the SEO planning draft (title/meta, blog ideas, on-page checklist, content calendar, competitor framework)")
    add_common(sp)
    sp.add_argument("--out", default="07-seo-plan.md", help="Output filename (saved under outputs/)")
    sp.set_defaults(func=cmd_report)

    return p

def cmd_add(args, path):
    rows = load_rows(path)
    new = {}
    for f in fieldnames:
        new[f] = (getattr(args, f) or "")
    key = candidate_key(new)
    for i, r in enumerate(rows):
        if candidate_key(r) == key:
            print("WARNING: keyword {!r} already exists. Not adding duplicate.".format(new["keyword"]))
            return
    rows.append(new)
    save_rows(path, rows, fieldnames)
    print("Added keyword #{}: {} ({})".format(len(rows), new["keyword"], new["target_location"]))

def cmd_list(args, path):
    rows = load_rows(path)
    if not rows:
        print("No keyword rows.")
        return
    filtered = rows
    if args.target_service:
        filtered = [r for r in filtered if trim(r.get("target_service")) == args.target_service]
    if args.target_location:
        filtered = [r for r in filtered if trim(r.get("target_location")) == args.target_location]
    if args.cluster:
        filtered = [r for r in filtered if trim(r.get("cluster")) == args.cluster]
    if args.search:
        q = args.search.lower()
        filtered = [r for r in filtered if q in " ".join(str(r.get(k) or "") for k in r).lower()]
    print("=== Keywords ({}) ===".format(len(filtered)))
    for i, r in enumerate(filtered, 1):
        print("{:<3} {} | {} | {} | {} | {} | {} | {}".format(
            i, r.get("keyword"), r.get("target_service"), r.get("target_location"),
            r.get("cluster"), r.get("search_intent"), r.get("competition"), r.get("search_volume")))

def cmd_search(args, path):
    rows = load_rows(path)
    if not rows:
        print("No keyword rows.")
        return
    q = args.query.lower()
    matches = [r for r in rows if q in " ".join(str(r.get(k) or "") for k in r).lower()]
    if not matches:
        print("No matches for {!r}.".format(args.query))
        return
    print("=== Search results for {!r} ({} matches) ===".format(args.query, len(matches)))
    for i, r in enumerate(matches, 1):
        print("{}) {} | {} | {} | {} | {} | {} | {}".format(
            i, r.get("keyword"), r.get("target_service"), r.get("target_location"),
            r.get("cluster"), r.get("search_intent"), r.get("competition"), r.get("search_volume")))

def cmd_edit(args, path):
    rows = load_rows(path)
    key = normalize_keyword(args.keyword)
    target = None
    for r in rows:
        if candidate_key(r) == key:
            target = r
            break
    if target is None:
        print("No keyword found for {!r}.".format(args.keyword))
        return
    overrides = {}
    for pair in args.set:
        if "=" in pair:
            k, v = pair.split("=", 1)
            overrides[k.strip()] = v.strip()
    for f in fieldnames:
        target[f] = overrides.get(f, target.get(f, ""))
    save_rows(path, rows, fieldnames)
    print("Updated: {} -> {}".format(args.keyword, target.get("keyword")))

def cmd_delete(args, path):
    rows = load_rows(path)
    key = normalize_keyword(args.keyword)
    for i, r in enumerate(rows):
        if candidate_key(r) == key:
            del rows[i]
            save_rows(path, rows, fieldnames)
            print("Deleted: {}".format(args.keyword))
            return
    print("No keyword found for {!r}.".format(args.keyword))

def cmd_validate(args, path):
    rows = load_rows(path)
    if not rows:
        print("No keyword rows to validate.")
        return
    issues = 0
    for i, row in enumerate(rows, 1):
        for issue in validate_row(row, i, fieldnames):
            print("row {}: {}".format(i, issue))
            issues += 1
    if issues == 0:
        print("OK: {} rows passed validation.".format(len(rows)))
    else:
        print("FAILED: {} row(s) with issues.".format(issues))
        return 1

def cmd_import(args, path):
    src = Path(args.file)
    if not src.exists():
        print("ERROR: import file not found: {}".format(src))
        return
    incoming = load_rows(src)
    if not incoming:
        print("No data rows in import file.")
        return
    existing = load_rows(path)
    issues = 0
    for i, row in enumerate(incoming, 1):
        for issue in validate_row(row, i, fieldnames):
            print("  ISSUE row {}: {}".format(i, issue))
            issues += 1
    if issues:
        print("Cannot import: {} invalid row(s). Fix and retry.".format(issues))
        return
    merged = []
    added = 0
    for row in incoming:
        if any(candidate_key(row) == candidate_key(ex) for ex in existing + merged):
            continue
        merged.append(row)
        added += 1
    if added == 0:
        print("No new rows added.")
        return
    do_backup_existing(path)
    existing.extend(merged)
    save_rows(path, existing, fieldnames)
    print("Imported {} row(s) -> {}. Total: {}.".format(added, path, len(existing)))

def cmd_export(args, path):
    src = Path(args.file)
    rows = load_rows(path)
    src.parent.mkdir(parents=True, exist_ok=True)
    with src.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: (row.get(k) or "") for k in fieldnames})
    print("Exported {} row(s) -> {}".format(len(rows), src))

def do_backup_existing(path):
    if not path.exists():
        return
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    dest = path.with_name("_backup_keywords_{}_{}.csv".format(path.stem, stamp))
    shutil.copy2(str(path), str(dest))
    print("Backup written: {}".format(dest))

def cmd_cluster(args, path):
    rows = load_rows(path)
    groups = {}
    for r in rows:
        cl = trim(r.get("cluster")) or "(unclustered)"
        groups.setdefault(cl, []).append(r)
    print("=== Keyword clusters ({}) ===".format(len(groups)))
    for cl, items in sorted(groups.items()):
        print("\n## Cluster: {}".format(cl))
        print("  count: {}".format(len(items)))
        print("  services: {}".format(", ".join(sorted({trim(x.get('target_service')) for x in items}))))
        print("  primary keyword: {}".format(items[0].get('primary_keyword')))
        for x in items:
            print("    - {} [{}] {}".format(x.get("keyword"), x.get("target_service"), x.get("search_intent")))

def cmd_local(args, path):
    rows = load_rows(path)
    local = [r for r in rows if any(k in " ".join(str(r.get(k) or "") for k in r).lower()
                                   for k in ("singrauli", "waidhan", "madhya pradesh"))]
    print("=== Local keywords ({}) ===".format(len(local)))
    for i, r in enumerate(local, 1):
        print("{}) {} | {} | {} | {} | {}".format(
            i, r.get("keyword"), r.get("target_service"), r.get("target_location"),
            r.get("cluster"), r.get("search_intent")))

def cmd_report(args, path):
    rows = load_rows(path)
    out_dir = REPO_ROOT / "outputs"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / args.out
    md = build_seo_plan(rows)
    out.write_text(md, encoding="utf-8")
    print("SEO plan written: {}".format(out))

def build_seo_plan(rows):
    lines = []
    lines.append("# SHAH AI - SEO & Keyword Research Plan (DRAFT)")
    lines.append("")
    lines.append("_Generated by Module 07 from data/keywords.csv. Draft only - no outside action.")
    lines.append("All volume/competition fields are Unverified unless sourced.")
    lines.append("")
    lines.append("## 1. Service-page title & meta description drafts")
    lines.append("")
    lines.append("Use only for pages SSC confirms it offers. Local terms (Singrauli / Waidhan / Madhya Pradesh) are factual locations from research.")
    lines.append("")
    services = sorted({trim(r.get("target_service")) for r in rows})
    for svc in services:
        local_cities = sorted({trim(r.get("target_location")) for r in rows
                               if trim(r.get("target_service")) == svc
                               and trim(r.get("target_location")) in ("Singrauli", "Waidhan", "Madhya Pradesh")})
        loc_txt = ", ".join(local_cities) if local_cities else "India"
        pk = ""
        for r in rows:
            if trim(r.get("target_service")) == svc and trim(r.get("primary_keyword")):
                pk = trim(r.get("primary_keyword"))
                break
        pk = pk or svc
        lines.append("### {}".format(svc))
        lines.append("")
        lines.append("Title: {} in {} | {}".format(pk, loc_txt, svc))
        lines.append("")
        lines.append("Meta description: {} services in {}. Supports planning, measurement, documentation and site coordination for EPC contractors and survey teams.".format(svc, loc_txt))
        lines.append("")
    lines.append("## 2. On-page SEO checklist")
    lines.append("")
    lines.append("Use these as a standing checklist for every service page:")
    lines.append("")
    checklist = [
        "- One clear H1 per page; the primary keyword appears naturally in the H1.",
        "- Target keyword in the first 100 words; secondary keywords used naturally.",
        "- Local relevance only where factually true (Singrauli / Waidhan / Madhya Pradesh / India).",
        "- Descriptive H2/H3 headings matching the cluster's supporting keywords.",
        "- Alt text on every image using a natural description, not keyword stuffing.",
        "- 'Last updated' date and author credit where content changed.",
        "- Internal links from the service page to related service pages.",
        "- No doorway pages; no repeated keyword lists; no clickable phrases that say 'read more' repeatedly.",
        "- CTA placed once per page, honest and low-pressure.",
        "- Title tag length <= 60 characters; meta description <= 155 characters.",
        "- Page speed and mobile use verified by the owner before publishing.",
    ]
    for c in checklist:
        lines.append("- " + c)
    lines.append("")
    lines.append("## 3. Blog topic ideas (draft-only, no metrics claimed)")
    lines.append("")
    lines.append("Topics below are content directions only; no search volume or ranking was claimed.")
    lines.append("")
    blog_topics = [
        "How to choose a land survey before buying land in Madhya Pradesh (Singrauli / Waidhan context)",
        "Topographical survey vs. drone survey: when to use each",
        "LiDAR vs. photogrammetry: a practical comparison for site mapping",
        "What is RTK / DGPS and why it matters for construction layout",
        "GPR survey: detecting what the eye cannot see",
        "How survey data reduces cost and delay on EPC sites",
        "Survey workflows for solar and transmission projects in central India",
        "A day in the field: topographical survey for a mining contractor",
        "Why cadastral survey matters for land records in Madhya Pradesh",
        "How to prepare a site for a topographical survey (checklist for contractors)",
        "Drone surveying compliance basics every project developer should know",
        "From field to deliverable: a look at the geospatial data workflow",
    ]
    for t in blog_topics:
        lines.append("- " + t)
    lines.append("")
    lines.append("## 4. Service-page keyword mapping")
    lines.append("")
    lines.append("Grouped from data/keywords.csv (source URL and research date recorded per row).")
    lines.append("")
    groups = {}
    for r in rows:
        cl = trim(r.get("cluster")) or "(unclustered)"
        groups.setdefault(cl, []).append(r)
    for cl, items in sorted(groups.items()):
        lines.append("### {}".format(cl))
        lines.append("")
        lines.append("| Primary | Secondary | Intent | Location |")
        lines.append("|---|---|---|---|")
        for x in items:
            sec = x.get("secondary_keywords") or "—"
            lines.append("| {} | {} | {} | {} |".format(
                x.get("primary_keyword"), sec, x.get("search_intent"), x.get("target_location")))
        lines.append("")
    lines.append("## 5. Local SEO content calendar (proposed dates)")
    lines.append("")
    lines.append("Draft-only. Dates are proposals; final dates require owner approval.")
    lines.append("")
    lines.append("| Week | Platform | Pillar | Topic | Format | Status |")
    lines.append("|---|---|---|---|---|---|")
    cal = [
        ("2026-W48","LinkedIn","Local survey presence","Land survey in Singrauli: why it matters","LinkedIn post","DRAFT"),
        ("2026-W48","Instagram Reels","Survey education","How a topographical survey guides a site","Reel","DRAFT"),
        ("2026-W49","LinkedIn","Local contractor value","Drone surveying for Madhya Pradesh sites","LinkedIn post","DRAFT"),
        ("2026-W49","YouTube","Explainer","Drone vs. manned survey: basics","Short video","DRAFT"),
        ("2026-W50","Instagram Reels","Geospatial explainer","DGPS + total station in one workflow","Reel","DRAFT"),
    ]
    for row in cal:
        lines.append("| {} | {} | {} | {} | {} | {} |".format(*row))
    lines.append("")
    lines.append("## 6. Competitor analysis framework")
    lines.append("")
    lines.append("Fill this only from verified, publicly available sources. No competitor metrics are claimed here.")
    lines.append("")
    lines.append("| Field | What to record | Source / date |")
    lines.append("|---|---|---|")
    comp_fields = [
        "Competitor company name",
        "Website and domain",
        "Service cities / service areas (verified)",
        "Services offered (from their public site)",
        "Online presence (LinkedIn, Google Business Profile, social)",
        "Price transparency (listed packages vs. 'contact us')",
        "Review tone and volume (public review platforms)",
        "Best practice topics they publish on",
    ]
    for f in comp_fields:
        lines.append("- {} | (owner to fill) | (verified source + date) |".format(f))
    lines.append("")
    lines.append("## 7. Research integrity note")
    lines.append("")
    lines.append("- Search volume and keyword difficulty are recorded only against a verified source. Until then they stay blank or 'Unverified'.")
    lines.append("- This plan is a draft; no marketing or SEO action has been taken.")
    lines.append("- Local terms reflect real service areas studied (Singrauli, Waidhan, Madhya Pradesh).")
    return "\n".join(lines)

if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()
    args.func(args, args.data)
