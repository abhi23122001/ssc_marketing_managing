# Module 06 — Contractor Lead Research & CRM

## Purpose

A local contractor lead-research and CRM workbench for SHAH AI. It helps the
owner build qualified lists of contractors and project teams (EPC, construction,
mining, electrical, infrastructure, power and solar), track qualification and
follow-up, and export a clean CSV for external use — without ever sending
messages or contacting anyone automatically.

Everything lives in `data/leads.csv` (CSV storage). There are no external
accounts, APIs or paid services.

## What this module produces

- Lead-capture records with company, website, public phone/email (where
  verified), address, source URL and date checked.
- Lead qualification status, priority, stage and follow-up date.
- A console dashboard: totals, verified/unverified, category counts, location
  counts, follow-up due/overdue, stage summary.
- CSV import/export, duplicate detection, input validation and automatic
  backups before any write.

## Files in this module

| File | Purpose |
|---|---|
| `README.md` | This file |
| `scripts/CRM-Leads.py` | Core Python CLI: add / list / search / edit / delete / dashboard / backup / import / export / validate / rebuild-sample |
| `Start-SHAI-CRM.ps1` | Windows 11 console launcher for the CRM |
| `data/leads.csv` | Canonical lead data (seed: 4 example rows) |

## Lead data model (`data/leads.csv`)

| Column | Meaning |
|---|---|
| `company` | Company / firm name (required) |
| `business_category` | EPC, construction, mining, electrical, infrastructure, survey services, etc. |
| `city` / `state` | Public service location |
| `address` / `phone` / `email` | Public contact details, only where verified |
| `website` | Public website (required) |
| `source_url` / `source_date_checked` | Original public source and date checked |
| `lead_acquired_date` | Date the lead was captured |
| `verification_status` | `Confirmed` or `Unconfirmed` — verified contact data only |
| `priority` | `High` / `Medium` / `Low` |
| `stage` | `New` / `Contacted` / `Qualified` / `Disqualified` / `Customer` |
| `follow_up_date` | Next follow-up date (`YYYY-MM-DD`) |
| `notes` | Free text |
| `qualification_status` | `Qualified` / `Partial` / `Unqualified` / `Pending` |
| `lead_source` | How the lead was captured |

## How to use

Run `.\Start-SHAI-CRM.ps1` from the module folder, then choose from the menu,
or run the Python CLI directly:

```powershell
python scripts\CRM-Leads.py list --data data\leads.csv
python scripts\CRM-Leads.py dashboard --data data\leads.csv
python scripts\CRM-Leads.py add --data data\leads.csv --company "..." --website "..." --city "..."
```

Full command reference:

| Command | What it does |
|---|---|
| `add` | Add a lead (duplicates are refused) |
| `list` | List leads |
| `search` | Search by text across all fields |
| `edit` | Edit by company + `--set field=value` |
| `delete` | Delete a lead |
| `dashboard` | CRM dashboard (totals, category/location counts, follow-up due/overdue) |
| `backup` | Backup `leads.csv` before any write |
| `import` | Import a CSV (validated + duplicate-protected) |
| `export` | Export the full lead list to CSV |
| `validate` | Validate all rows (required fields, phone/email shape, allowed values) |
| `rebuild-sample` | Restore the embedded 4-row sample set |

## Integration with the Command Center

- Modules 06 and 07 appear automatically in the start command center launcher
  (`Start-SHAI-Center.ps1`) because each module folder contains a `README.md`.
- Public business data is recorded with its `source_url` and `source_date_checked`
  so nothing is invented. Phone numbers, emails, addresses and company details are
  recorded only from verified public sources.
- Research actions never contact any company. Outreach drafts are prepared for the
  owner and only sent after explicit approval.

## Safety and draft rules

- Draft-only. Nothing is published or sent without an owner approval record
  (see `shared/templates/approval-form.md`).
- Public, non-PII data only. No personal data, no restricted scraping.
- No fabricated phone numbers, emails, addresses or company details.
