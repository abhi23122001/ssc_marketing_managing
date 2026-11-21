#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SHAH AI - Shared Automation Planner (dry-run only).

A local, draft-only automation runbook tool. It declares triggers + allowed
actions and produces a validated, human-readable dry-run status report.

DESIGN (safety by construction):
 * No network calls.
 * No state-changing operations: every declared action is a dry-run record.
 * Actions that would publish, send, message or spend require an explicit
   owner approval record (shared/templates/approval-form.md).
 * The tool never sends email, posts to social media, contacts leads or
   writes to data/leads.csv.

Run directly:
    python3 shared/scripts/AutomationPlanner.py show
    python3 shared/scripts/AutomationPlanner.py plan --rulefile data/automation-rules.csv
"""
import argparse
import csv
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve()
REPO_ROOT = None
for candidate in [HERE] + list(HERE.parents):
    if (Path(candidate) / "modules").is_dir():
        REPO_ROOT = Path(candidate)
        break
if REPO_ROOT is None:
    REPO_ROOT = Path.cwd().resolve()

DEFAULT_RULES = REPO_ROOT / "data" / "automation-rules.csv"
OUTPUTS_DIR = REPO_ROOT / "outputs"


# --- Rules vocabulary --------------------------------------------------------
ALLOWED_ACTIONS = {
    "test-set",
    "report-generate",
    "scheduler-run",
    "calendar-generate",
    "sentiment-write",
    "summary-write",
    "draft-write",
}
STATE_CHANGING = {"report-generate", "scheduler-run", "calendar-generate"}


def _rule():
    print("")


def _section(title):
    print("")
    print("  " + "=" * 66)
    print("  " + title)
    print("  " + "=" * 66)


def validate_rule(rule):
    """Return a list of human-readable warnings for a rule (dry-run only)."""
    warnings = []
    action = (rule.get("action") or "").strip().lower()
    if action not in ALLOWED_ACTIONS:
        warnings.append("unknown action {!r}".format(rule.get("action")))
    if action in STATE_CHANGING:
        approval = (rule.get("approval_required") or "").strip().lower()
        if approval not in {"1", "true", "yes", "approved"}:
            warnings.append("state-changing action {} requires approval_required=yes".format(action))
    if not (rule.get("trigger") or "").strip():
        warnings.append("missing trigger")
    if not (rule.get("action") or "").strip():
        warnings.append("missing action")
    return warnings


def load_rules(path):
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    lines = []
    for raw in text.splitlines():
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        lines.append(stripped)
    if not lines:
        return []
    reader = csv.DictReader(lines)
    if reader.fieldnames is None:
        return []
    rows = []
    for row in reader:
        if row is not None:
            rows.append(row)
    return rows


def dry_run_report(rules):
    print("=" * 66)
    print("  SHAH AI - Automation Dry-Run Report (LOCAL ONLY)")
    print("  Date: {}".format(date.today().isoformat()))
    print("  Note: this is a draft runbook only. No network/state change.")
    print("=" * 66)

    _section("Rules declared ({})".format(len(rules)))
    for i, rule in enumerate(rules, 1):
        action = (rule.get("action") or "").strip().lower()
        status = "STATE_CHANGING-ENABLED" if action in STATE_CHANGING else "INACTIVE"
        print("  {}. [{}] trigger={!r:<34} action={!r:<24} {}".format(
            i, status, rule.get("trigger", ""), rule.get("action", ""), rule.get("approval_required", "")))

    _section("Validation")
    issues = []
    for i, rule in enumerate(rules, 1):
        for w in validate_rule(rule):
            issues.append("rule {}: {}".format(i, w))
    if issues:
        for issue in issues:
            print("  WARNING: {}".format(issue))
    else:
        print("  OK: all rules valid. State-changing actions carry approval_required=yes.")

    _section("Status")
    print("  Total rules  : {}".format(len(rules)))
    print("  Dry-run mode : ON (no execution)")
    print("  Network      : OFF")
    print("  Publishing   : BLOCKED until owner approval record present")
    return bool(issues)


def build_parser():
    p = argparse.ArgumentParser(prog="AutomationPlanner.py", description="SHAH AI Shared Automation Planner (draft-only)")
    sub = p.add_subparsers(dest="command", required=True)

    sp = sub.add_parser("show", help="Show current rules (empty if none)")
    sp.set_defaults(func=lambda a: dry_run_report(load_rules(DEFAULT_RULES)))

    sp = sub.add_parser("plan", help="Validate rules from a CSV and print the dry-run report")
    sp.add_argument("--rulefile", type=Path, default=DEFAULT_RULES)
    sp.set_defaults(func=lambda a: dry_run_report(load_rules(a.rulefile)))

    return p


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    return 0 if not args.func(args) else 1


if __name__ == "__main__":
    sys.exit(main())
