# Module 02 — Daily Content Planner

## Purpose

A repeatable content-planning workbench for SHAH AI to keep SSC's marketing
consistent. It turns broad campaign goals into a short, daily, weekly, and
monthly plan, tracks the status of each planned item, and keeps content ideas
from duplicating each other.

It works entirely from CSV files and Markdown templates. No accounts, APIs, or
paid services are used.

## What this module now contains

| File | Purpose |
|---|---|
| `data/content-calendar.csv` | Daily, weekly, and monthly content calendar (with sample rows) |
| `shared/scripts/Calendar.ps1` | Console views: daily, weekly, monthly, next-7-days |
| `data/instagram-library.csv` | SSI & Facebook content asset ideas |
| `shared/templates/content-template.md` | Shared content draft template |
| `shared/templates/qa-checklist.md` | Public-content QA checklist |
| `shared/templates/marketing-brief-template.md` | Marketing brief template |

## Draft output format

A content item uses `shared/templates/content-template.md`:
```markdown
---
date_proposed: 2026-W48
platform: Instagram Reels
language: English
status: DRAFT
---

# Hook / headline

Main message and value point.

## Visual / shot list
- ...

## Caption
...

## Taglines / hashtags
...

## Proof required
- ...

## Approval required
- Owner approval (complete `approval-form.md`).
```

## Quick workflow

1. Open `data/content-calendar.csv` and fill in date, platform, pillar, topic,
   format, audience, language, status, proof.
2. Mark each new topic as `DRAFT` until the owner approves the date.
3. Run a QA check on the draft (`shared/templates/qa-checklist.md`).
4. After owner approval, keep the item draft for review; do not schedule without
   an explicit approval record.
5. Avoid duplication by reading `data/content-calendar.csv` before adding a new
   idea — check overlaps in pillar, format, and theme.

## Quick workflow

```powershell
# Next 7 days default; limit like -Days 7
.\shared\scripts\Calendar.ps1 [-Days 7] [-View daily|weekly|monthly|next]

# Examples
.\shared\scripts\Calendar.ps1 -View daily -Days 7
.\shared\scripts\Calendar.ps1 -View weekly
.\shared\scripts\Calendar.ps1 -View monthly
```

## Inputs

- Owner's preferred planning period.
- Campaign goal for the week (optional).
- Services to feature (from the confirmed SCC list).
- Location context: Singrauli, Waidhan, Madhya Pradesh (only when genuinely relevant).

## Approval boundary

- Planned dates are proposals until the owner sets a calendar.
- No publishing or scheduling without explicit approval.

## CSV storage

`data/content-calendar.csv` has these columns:
`date_proposal`, `platform`, `content_pillar`, `topic`, `format`, `target_audience`,
`language`, `status`, `proof_required`.

Sample rows are templates; replace with real SSC campaign plans before publishing
any calendar publicly.
