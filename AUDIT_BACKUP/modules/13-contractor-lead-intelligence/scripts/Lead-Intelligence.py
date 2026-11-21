#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module 13 — Contractor Lead Intelligence
========================================

Local-first lead scoring, prioritization, contractor qualification
intelligence and follow-up recommendations for SHAH AI / SSC.

Everything is READ-ONLY with respect to data/leads.csv:
 * Reads the existing 18-column lead records.
 * Computes scores, priorities, contractor qualification intelligence and
 * follow-up recommendations in memory.
 * NEVER modifies, deletes, overwrites or appends to data/leads.csv.
 * No external APIs, paid services, publishing or lead contact.

Subcommands
-----------
  dashboard  - All leads with score, tier and summary (default, no arg)
  score      - Per-lead scoring breakdown
  prioritize - Leads sorted by tier (Tier 1 -> Tier 4)
  qualify    - Contractor qualification intelligence
  recommend  - Follow-up recommendations per lead
  summary    - High-level actionable summary (counts + top leads)
"""

from __future__ import print_function

import argparse
import csv
import sys
from datetime import date, datetime
from pathlib import Path

# --- Paths ---------------------------------------------------------------
HERE = Path(__file__).resolve()
REPO_ROOT = None
for candidate in [HERE] + list(HERE.parents):
    if (Path(candidate) / "modules").is_dir():
        REPO_ROOT = Path(candidate)
        break
if REPO_ROOT is None:
    REPO_ROOT = Path.cwd().resolve()

DATA_FILE = REPO_ROOT / "data" / "leads.csv"

# Existing 18-column schema of data/leads.csv (protected).
LEADS_HEADER = [
    "company", "business_category", "city", "state", "address", "phone",
    "email", "website", "source_url", "source_date_checked",
    "lead_acquired_date", "verification_status", "priority", "stage",
    "follow_up_date", "notes", "qualification_status", "lead_source",
]

# --- Constants (validation + scoring) -------------------------------------
VALID_PRIORITIES = {"High", "Medium", "Low"}
VALID_STAGES = {"New", "Contacted", "Qualified", "Disqualified", "Customer", "Unqualified"}
VALID_VERIFICATION = {"Confirmed", "Unconfirmed", "Unverified"}
VALID_QUALIFICATION = {"Qualified", "Partial", "Unqualified", "Pending", "Disqualified"}
VALID_LEAD_SOURCE = {"Public profile", "Public directory", "Reference", "Manual research", "Enumeration"}

VERIFICATION_POINTS = {"Confirmed": 30, "Unconfirmed": 15, "Unverified": 0}
QUALIFICATION_POINTS = {"Qualified": 40, "Partial": 20, "Pending": 10, "Unqualified": 5, "Disqualified": 0}
PRIORITY_POINTS = {"High": 25, "Medium": 15, "Low": 5}
STAGE_POINTS = {"Customer": 45, "Qualified": 30, "Contacted": 15, "New": 5, "Disqualified": 0, "Unqualified": 0}
CONTRACTOR_CATEGORY_POINTS = {
    "Geospatial / Survey Services": 10,
    "Survey / Building Construction": 8,
    "Construction / Survey Services": 8,
}
LEAD_SOURCE_POINTS = {"Public profile": 5, "Public directory": 5, "Reference": 8, "Manual research": 6, "Enumeration": 4}
DATE_FORMAT = "%Y-%m-%d"
TODAY = date.today()


def find_repo_root() -> Path:
    """Walk up from the script until a directory containing 'modules/' is found."""
    candidate = HERE.resolve()
    for parent in [candidate, *candidate.parents]:
        if (Path(parent) / "modules").is_dir():
            return Path(parent)
    return Path.cwd().resolve()


def read_leads() -> list:
    """Read data/leads.csv without modifying it."""
    if not DATA_FILE.exists():
        return []
    with DATA_FILE.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        return list(reader)


def validate_leads(leads):
    """Return a list of schema/record problems (read-only)."""
    problems = []
    if not leads:
        problems.append("no lead records found")
        return problems
    for i, lead in enumerate(leads, start=2):  # header = row 1
        missing = [k for k in LEADS_HEADER if k not in lead or lead[k] is None or str(lead[k]).strip() == ""]
        if missing:
            problems.append("row %d missing: %s" % (i, ",".join(missing)))
    return problems


def score_lead(lead):
    """Compute a 0-100 lead score + field breakdown."""
    score = 0
    breakdown = {}

    v = lead.get("verification_status") or ""
    s = VERIFICATION_POINTS.get(v, 0)
    score += s
    breakdown["verification"] = (v, s)

    q = lead.get("qualification_status") or ""
    s = QUALIFICATION_POINTS.get(q, 0)
    score += s
    breakdown["qualification"] = (q, s)

    p = lead.get("priority") or ""
    s = PRIORITY_POINTS.get(p, 0)
    score += s
    breakdown["priority"] = (p, s)

    st = lead.get("stage") or ""
    s = STAGE_POINTS.get(st, 0)
    score += s
    breakdown["stage"] = (st, s)

    bc = lead.get("business_category") or ""
    s = CONTRACTOR_CATEGORY_POINTS.get(bc, 0)
    score += s
    breakdown["category"] = (bc, s)

    fu = (lead.get("follow_up_date") or "").strip()
    s = 0
    if fu:
        try:
            fu_date = datetime.strptime(fu, DATE_FORMAT).date()
            days = (fu_date - TODAY).days
            s = 15 if days <= 7 else (8 if days <= 30 else 0)
        except ValueError:
            s = 0
    score += s
    breakdown["follow_up"] = ((fu or "none"), s)

    ls = lead.get("lead_source") or ""
    s = LEAD_SOURCE_POINTS.get(ls, 0)
    score += s
    breakdown["source"] = (ls, s)

    return {"score": min(score, 100), "breakdown": breakdown, "lead": lead}


def lead_tier(score):
    if score >= 70:
        return "Tier 1 - Action Now"
    if score >= 50:
        return "Tier 2 - High"
    if score >= 30:
        return "Tier 3 - Watch"
    return "Tier 4 - Low"


def follow_up_recommendations(lead):
    """Actionable follow-up text derived from existing fields (no contact made)."""
    notes = lead.get("notes") or ""
    stage = lead.get("stage") or ""
    ver = lead.get("verification_status") or ""
    qual = lead.get("qualification_status") or ""
    pri = lead.get("priority") or ""
    fu = (lead.get("follow_up_date") or "").strip()
    recs = []

    if stage == "New":
        recs.append("Prune before contact; collect qualification questionnaire.")
    if qual in ("Qualified", "Partial"):
        recs.append("Send qualification questionnaire / request formal quote.")
    if qual == "Disqualified":
        recs.append("Close follow-up; re-engage next cycle.")
    if ver == "Unconfirmed":
        recs.append("Verify contact details before outreach.")
    if fu:
        try:
            fu_date = datetime.strptime(fu, DATE_FORMAT).date()
            days = (fu_date - TODAY).days
            if days <= 0:
                recs.append("Call today.")
            elif days <= 7:
                recs.append("Call within 7 days.")
            elif days <= 30:
                recs.append("Schedule follow-up within 30 days.")
        except ValueError:
            pass
    if pri == "High":
        recs.append("Immediate follow-up (priority High).")
    if not recs:
        recs.append("Review record; monitor for updates.")
    if notes:
        recs.append("[record note] " + notes)
    return recs


def contractor_candidates(leads):
    """Leads that currently qualify as a contractor prospects."""
    cands = []
    for lead in leads:
        if (lead.get("verification_status") == "Confirmed"
                and lead.get("qualification_status") in ("Qualified", "Partial")
                and lead.get("stage") not in ("Disqualified", "Unqualified")
                and lead.get("business_category")
                and "None" not in lead.get("business_category")):
            cands.append(lead)
    return cands


def compute_all(leads):
    """Attach score/tier/recommendations to each lead; return enriched list."""
    enriched = []
    for lead in leads:
        result = score_lead(lead)
        lead["_score"] = result["score"]
        lead["_tier"] = lead_tier(result["score"])
        lead["_recommendations"] = follow_up_recommendations(lead)
        enriched.append(lead)
    return enriched


def _format_field(lead, key, width=22):
    val = lead.get(key) or ""
    return "%-*s" % (width, str(val))


def _print_lead(lead, show_all_fields=False):
    score = lead.get("_score", 0)
    tier = lead.get("_tier", "Unknown")
    print("  %-4s %-34s score=%3d  %s" % (lead.get("company", "?"), tier, score, lead["business_category"] or ""))
    print("        city=%s  priority=%s  stage=%s  verification=%s  qualification=%s" % (
        lead.get("city") or "", lead.get("priority") or "", lead.get("stage") or "",
        lead.get("verification_status") or "", lead.get("qualification_status") or ""))
    if show_all_fields:
        for k in LEADS_HEADER:
            print("          %-22s %s" % (k, lead.get(k) or ""))
    for rec in lead.get("_recommendations", []):
        print("        REC - %s" % rec)
    print("")


def cmd_dashboard(leads):
    print("SHAH AI - Contractor Lead Intelligence (dashboard)")
    print("Leads in data/leads.csv: %d" % len(leads))
    print("=" * 78)
    for lead in leads:
        _print_lead(lead, show_all_fields=False)
    print("=" * 78)


def cmd_score(leads):
    print("Lead scoring breakdown")
    print("=" * 78)
    for lead in leads:
        sb = lead.get("_score", 0)
        print("  %-34s score=%3d" % (lead.get("company") or "?", sb))
        for k, (label, val) in lead.get("_breakdown", {}).items():
            print("      %-22s %-22s %s" % (k, label or "", val))
    print("=" * 78)


def cmd_prioritize(leads):
    print("Lead prioritization (Tier 1 -> Tier 4)")
    print("=" * 78)
    ordered = sorted(leads, key=lambda x: x.get("_score", 0), reverse=True)
    for lead in ordered:
        print("  [%s] %-34s %3d pts" % (lead.get("_tier", ""), lead.get("company") or "?", lead.get("_score", 0)))
    print("=" * 78)


def cmd_qualify(leads):
    print("Contractor qualification intelligence")
    print("=" * 78)
    cand = contractor_candidates(leads)
    if not cand:
        print("  (no contractor candidates right now)")
    for lead in cand:
        print("  QUALIFIED  %-34s %s" % (lead.get("company") or "?", lead.get("business_category") or ""))
        for rec in lead.get("_recommendations", []):
            print("      REC - %s" % rec)
    unqual = [l for l in leads if l not in cand]
    print("  (remaining leads: %d - not currently contractor-qualified)" % len(unqual))
    print("=" * 78)


def cmd_recommend(leads):
    print("Follow-up recommendations")
    print("=" * 78)
    for lead in leads:
        print("  %-34s [%s]" % (lead.get("company") or "?", lead.get("_tier", "?")))
        for rec in lead.get("_recommendations", []):
            print("      - %s" % rec)
    print("=" * 78)


def cmd_summary(leads):
    print("Actionable lead summary")
    print("=" * 78)
    print("  Total leads        : %d" % len(leads))
    tiers = {}
    for l in leads:
        t = l.get("_tier", "")
        tiers[t] = tiers.get(t, 0) + 1
    print("  By tier:")
    for t in sorted(tiers, key=lambda x: (0 if "Action Now" in x else 1 if "High" in x else 2 if "Watch" in x else 3)):
        print("    %s : %d" % (t, tiers[t]))
    cand = contractor_candidates(leads)
    print("  Contractor candidates : %d" % len(cand))
    print("  Per-company:")
    for lead in sorted(leads, key=lambda x: x.get("_score", 0), reverse=True):
        print("    %-34s %3d (%s) %s" % (lead.get("company") or "?", lead.get("_score", 0), lead.get("_tier", ""), lead.get("business_category") or ""))
    print("=" * 78)


def build_parser():
    parser = argparse.ArgumentParser(description="SHAH AI Contractor Lead Intelligence (M13)")
    sub = parser.add_subparsers(dest="command", help="commands")

    def _add(subfunc):
        subparser = sub.add_parser(subfunc.__name__.replace("cmd_", ""))
        subparser.set_defaults(func=subfunc)
        return subparser

    _add(cmd_dashboard).add_argument("--all", action="store_true", help="show every field")
    _add(cmd_score)
    _add(cmd_prioritize)
    _add(cmd_qualify)
    _add(cmd_recommend)
    _add(cmd_summary)
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    leads = read_leads()
    leads = compute_all(leads)
    if args.command is None:
        cmd_dashboard(leads)
    elif args.command == "dashboard":
        cmd_dashboard(leads)
    elif args.command == "score":
        cmd_score(leads)
    elif args.command == "prioritize":
        cmd_prioritize(leads)
    elif args.command == "qualify":
        cmd_qualify(leads)
    elif args.command == "recommend":
        cmd_recommend(leads)
    elif args.command == "summary":
        cmd_summary(leads)
    else:
        parser.print_help()
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
