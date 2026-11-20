# Module 07 — SEO and Keyword Research

## Purpose

A local-first search-optimization support module for SHAH AI. It builds
keyword clusters from service and local terms, maps those keywords to service
pages, and produces a draft SEO plan with title/meta drafts, an on-page SEO
checklist, blog topic ideas, a content calendar and a competitor analysis
framework.

All work is local (`data/keywords.csv`) and draft-only. No external accounts,
paid APIs or live search services are required.

## What this module produces

- Keyword library: primary / secondary keywords, search intent, target service,
  target location, cluster, competition, search volume, source URL and research
  date.
- Keyword clusters grouped by service/region.
- Service-page title and meta description drafts.
- On-page SEO checklist.
- Blog topic ideas (draft-only, no metrics claimed).
- Local SEO content calendar (proposed dates).
- Competitor analysis framework.

## Files in this module

| File | Purpose |
|---|---|
| `README.md` | This file |
| `scripts/SEO-Keywords.py` | Core Python CLI: add / list / search / edit / delete / validate / import / export / cluster / local / report / rebuild-sample |
| `Start-SHAI-SEO.ps1` | Windows 11 console launcher for the SEO module |
| `data/keywords.csv` | Keyword library (seed: 22 rows) |
| `outputs/07-seo-plan.md` | Generated SEO planning draft (regeneratable via `report`) |

## Keyword data model (`data/keywords.csv`)

| Column | Meaning |
|---|---|
| `keyword` | Canonical search term (unique identifier) |
| `primary_keyword` | The main term to target on the page |
| `secondary_keywords` | Supporting terms (comma separated) |
| `search_intent` | informational / local-info / service / transactional |
| `target_service` | Survey service offered (required) |
| `target_location` | Location (Singrauli / Waidhan / Madhya Pradesh / India) |
| `cluster` | Keyword cluster / service-page group |
| `competition` | `Low` / `Medium` / `High` / `Unverified` |
| `search_volume` | Integer volume **only when a verified source exists**; otherwise blank |
| `source_url` | Verified source for the volume/competition value |
| `research_date` | Date the value was researched (`YYYY-MM-DD`) |

## Rules for search volume and competition

- Competition and search volume fields are recorded ONLY where a verified
  source supports them. Blank or `Unverified` means no verified value exists yet.
- Do not copy a number from an unverified snippet. Manual research workflows are
  provided in the README so you can verify values yourself.
- Every seed row in `data/keywords.csv` has `Unverified` or a blank volume, because
  no paid API or live search was used.

## How to use

Run `.\Start-SHAI-SEO.ps1` from the module folder, or run the Python CLI directly:

```powershell
python scripts\SEO-Keywords.py list --data data\keywords.csv
python scripts\SEO-Keywords.py search --data data\keywords.csv --query "survey singrauli"
python scripts\SEO-Keywords.py cluster --data data\keywords.csv
python scripts\SEO-Keywords.py report --data data\keywords.csv --out 07-seo-plan.md
```

Subcommand reference:

| Command | What it does |
|---|---|
| `add` | Add a keyword row |
| `list` | List keywords (filter by cluster / service / location / search text) |
| `search` | Search keywords by text |
| `edit` | Edit a keyword (`--keyword X --set field=value`) |
| `delete` | Delete a keyword |
| `validate` | Validate all rows (required fields, allowed intents, volume format) |
| `import` / `export` | Import / export the keyword library |
| `cluster` | Group keywords by cluster into a page-keyword map |
| `local` | List local (Singrauli / Waidhan / Madhya Pradesh) keywords |
| `report` | Generate the SEO planning draft `outputs/07-seo-plan.md` |
| `rebuild-sample` | Restore the embedded 22-row sample set |

## Integration with the Command Center

- Modules 06 and 07 appear automatically in the start command center launcher
  (`Start-SHAI-Center.ps1`) because each module folder contains a `README.md`.
- The SEO plan, title/meta drafts and blog ideas are ALL drafts. Nothing is
  published without an owner approval record (see
  `shared/templates/approval-form.md`).
- Local terms (Singrauli / Waidhan / Madhya Pradesh) reflect real service areas.
  Internal links, page speed and mobile checks are verified by the owner before
  any live publishing.

## Safety and draft rules

- Draft-only. No publishing, no live search scraping, no data entry into Google
  Search Console or other tools without separate approval.
- Never fabricate search volume, keyword difficulty, rankings or competitor
  performance. Mark estimates clearly as `Unverified`.
- Local keywords are used only where factually relevant to SSC's service areas.
- No doorway pages and no keyword stuffing.
