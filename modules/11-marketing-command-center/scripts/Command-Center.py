#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module 11 - Unified Marketing Command Center

Dashboard + module navigation for the SHAH AI marketing workflow.
* Lists all existing marketing modules (01-10) with status.
* Dashboard / module navigation.
* Workflow visibility: content, approval, reports.
* Windows-compatible launch: Start-SHAI-Command-Center.ps1
* No external APIs, no paid services, no network calls.
"""

from __future__ import print_function

import os
import sys

# --- Paths --------------------------------------------------------------
HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
MODULES_DIR = os.path.join(PROJECT_ROOT, "modules")
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
SHARED_DIR = os.path.join(PROJECT_ROOT, "shared")

# Short code -> friendly name
MODULE_SHORT = {
    "01": "Marketing Command Center",
    "02": "Daily Content Planner",
    "03": "Instagram / Facebook Content Studio",
    "04": "LinkedIn B2B Marketing",
    "05": "Google Business Profile Management",
    "06": "Contractor Lead Research CRM",
    "07": "SEO / Keyword Research",
    "08": "AI Image / Video Workflow",
    "09": "Content Approval & Publishing",
    "10": "Analytics & Monthly Reporting",
}

MODULE_STATUS = {
    "01": "Ready",
    "02": "Ready",
    "03": "Ready",
    "04": "Ready",
    "05": "Ready",
    "06": "Ready",
    "07": "Ready",
    "08": "Ready",
    "09": "Ready",
    "10": "Ready",
}

MODULE_DIRS = {
    "01": "01-marketing-command-center",
    "02": "02-daily-content-planner",
    "03": "03-instagram-facebook-content-studio",
    "04": "04-linkedin-b2b-marketing",
    "05": "05-google-business-profile-management",
    "06": "06-contractor-lead-research-crm",
    "07": "07-seo-keyword-research",
    "08": "08-ai-image-video-workflow",
    "09": "09-content-approval-publishing-workflow",
    "10": "10-analytics-monthly-reporting",
}


def _rule():
    print("")

def _section(title):
    print("")
    print("  " + "=" * 66)
    print("  " + title)
    print("  " + "=" * 66)


def header():
    _rule()
    print("  SHAH AI MARKETING COMMAND CENTER")
    _rule()
    print("  PROJECT ROOT : %s" % PROJECT_ROOT)
    print("  BRANCH       : main")
    print("  HEAD         : a21e9f775c4e564b4f5d73d1291598160d7e8350")
    print("  MODULES DIR  : %s" % MODULES_DIR)
    print("  DATA DIR     : %s" % DATA_DIR)
    print("  SHARED DIR   : %s" % SHARED_DIR)


def list_modules():
    _section("MODULE NAVIGATION")
    print("  %-4s %-40s %-10s %s" % ("Code", "Module", "Status", "Path"))
    print("  " + "-" * 68)
    for code in sorted(MODULE_SHORT):
        name = MODULE_SHORT[code]
        folder = MODULE_DIRS[code]
        path = os.path.join(MODULES_DIR, folder)
        exists = os.path.isdir(path)
        print("  [%s] %-38s %-10s %s" % (code, name, MODULE_STATUS.get(code, "Ready"), path))
        print("          path exists: %s" % ("yes" if exists else "NO - MISSING"))


def status_only():
    _section("MODULE STATUS SUMMARY")
    print("  %-4s %-35s %s" % ("Code", "Module", "Status"))
    print("  " + "-" * 54)
    for code in sorted(MODULE_SHORT):
        print("  %-4s %-35s %s" % (code, MODULE_SHORT[code], MODULE_STATUS.get(code, "Ready")))


def workflows():
    _section("WORKFLOW VISIBILITY (Content Studio)")
    print("  1. Content brief   -> shared/templates/marketing-brief-template.md")
    print("  2. Draft           -> shared/scripts/Write-Draft.ps1")
    print("  3. Approval        -> shared/templates/approval-form.md")
    print("  4. Publish         -> shared/scripts/Write-Draft.ps1 (publish mode)")
    print("  5. Report          -> modules/10-analytics-monthly-reporting/")
    print("  QA gate before publish: docs/CONTENT-QA-CHECKLIST.md")


def reports():
    _section("REPORTING CALENDAR (sample)")
    print("  Week 1: brand brief + calendar freeze")
    print("  Week 2: module 03 content studio delivery")
    print("  Week 3: module 04 LinkedIn + module 05 GBP refresh")
    print("  Week 4: module 10 analytics review + final report")


def dashboard():
    header()
    list_modules()
    workflows()
    reports()


def list_targets():
    print("  Available actions:")
    print("    dashboard - show full dashboard")
    print("    status    - module status summary")
    print("    modules   - module navigation list")
    print("    workflows - content workflow")
    print("    reports   - reporting calendar")
    print("    exit      - quit")


def main(argv):
    if not argv or argv[0] in ("-h", "--help", "help", "?"):
        dashboard()
        return 0

    cmd = argv[0].lower()
    if cmd == "dashboard":
        dashboard()
    elif cmd == "status":
        status_only()
    elif cmd == "modules":
        list_modules()
    elif cmd == "workflows":
        workflows()
    elif cmd == "reports":
        reports()
    elif cmd == "exit":
        return 0
    else:
        print("Unknown command: %s" % cmd)
        print("Run: Command-Center.py [dashboard|status|modules|workflows|reports]")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
