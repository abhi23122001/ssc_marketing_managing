# Module 12 — Content Calendar & Content Generation

SHAH AI — Shah Surveyors & Consultancy (SSC)

## Purpose

This module fills the **M12 numbering gap** between M11 (Unified Marketing
Command Center) and M13 (Contractor Lead Intelligence). Its purpose is to bring
the content-generation work currently split across modules 02 (Daily Content
Planner), 03 (Instagram/Facebook), 04 (LinkedIn) and 05 (Google Business Profile)
into one shared calendar plus one generative drafting tool.

It does **not** invent a new CRM, does not contact anyone, and performs no
external action.

## What this module produces

- A working content calendar (`data/m12-content-calendar.csv`) used as the M12
  working board. It is a **new** file and is deliberately separate from the
  shared `data/content-calendar.csv` managed by Module 02.
- Draft content files in `outputs/12-*` generated from each calendar row.
- Pure-function drafting helpers (no API calls): blog briefs, reel scripts,
  LinkedIn posts, GBP post drafts, bilingual outreach drafts.

## Rules (unchanged)

- Everything is **draft-only**. No publishing, scheduling, messaging, contacting,
  profile edits, or spending without an explicit owner approval record
  (`shared/templates/approval-form.md`).
- `data/leads.csv` schema and records are protected. This module never reads or
  writes `data/leads.csv`.
- Template-driven generation only. No external accounts, APIs or paid services.

## Files

| File | Purpose |
|---|---|
| `README.md` | This file |
| `scripts/ContentCalendar.py` | CLI: `list`, `view`, `add`, `export`, `validate`, `integrity-check` |
| `scripts/ContentGenerator.py` | Pure drafting helpers + CLI: `generate-all`, `generate-one` |
| `Start-SHAI-Command-Center.ps1` | Windows 11 launcher (dispatches the two Python scripts) |

## How to use

```powershell
# from the project root
PS> .\\modules\\12-content-calendar-content-generation\\Start-SHAI-Command-Center.ps1 list
PS> .\\modules\\12-content-calendar-content-generation\\Start-SHAI-Command-Center.ps1 view
PS> .\\modules\\12-content-calendar-content-generation\\Start-SHAI-Command-Center.ps1 add --date "2026-W48" --platform "Instagram Reels" --topic "Topographical survey basics" --language en
PS> .\\modules\\12-content-calendar-content-generation\\Start-SHAI-Command-Center.ps1 export --out outputs\\12-calendar.csv
PS> .\\modules\\12-content-calendar-content-generation\\Start-SHAI-Command-Center.ps1 validate
PS> .\\modules\\12-content-calendar-content-generation\\Start-SHAI-Command-Center.ps1 integrity-check
PS> .\\modules\\12-content-calendar-content-generation\\Start-SHAI-Command-Center.ps1 generate-all
```

Direct Python use:

```powershell
python scripts\\ContentCalendar.py list
python scripts\\ContentGenerator.py generate-all --calendar data\\m12-content-calendar.csv --out outputs\\12
```

## Output draft header

Every generated file is written to `outputs/` with a standard header:

```markdown
---
status: DRAFT
source: modules/12-content-calendar-content-generation/scripts/ContentGenerator.py
approval_required: yes
module: 12-content-calendar-content-generation
---
```

## Integration

- Reads the working board `data/m12-content-calendar.csv` (new file).
- Consumes the shared templates in `shared/templates/` for QA and approval forms.
- Visible from the Command Center (`COMMAND-CENTER.md`, `docs/MODULES-ARCHITECTURE.md`).
