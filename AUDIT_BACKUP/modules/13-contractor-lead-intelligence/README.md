# Module 13 - Contractor Lead Intelligence

## Purpose
Lead scoring, prioritization, contractor qualification intelligence and
follow-up recommendations for SHAH AI / SSC.

M13 reads the existing `data/leads.csv` (18-column schema) and produces:
- Lead scores (0-100)
- Prioritization tiers (Tier 1 -> Tier 4)
- Contractor qualification intelligence
- Follow-up recommendations
- Actionable lead summaries

## Data model (read-only)
- Source: `data/leads.csv` (protected file - header and records NOT modified)
- Output: terminal summaries only (read-only). No CSV schema changes.
- No external APIs, paid services, publishing or lead contact.

## Files
- `README.md` - this file
- `Start-SHAI-Lead-Intelligence.ps1` - Windows launcher
- `scripts/Lead-Intelligence.py` - scoring & intelligence engine

## Run (from project root)
```powershell
PS> .\modules\13-contractor-lead-intelligence\Start-SHAI-Lead-Intelligence.ps1
PS> .\modules\13-contractor-lead-intelligence\Start-SHAI-Lead-Intelligence.ps1 score
PS> .\modules\13-contractor-lead-intelligence\Start-SHAI-Lead-Intelligence.ps1 prioritize
PS> .\modules\13-contractor-lead-intelligence\Start-SHAI-Lead-Intelligence.ps1 qualify
PS> .\modules\13-contractor-lead-intelligence\Start-SHAI-Lead-Intelligence.ps1 recommend
PS> .\modules\13-contractor-lead-intelligence\Start-SHAI-Lead-Intelligence.ps1 summary
```

## Integration with M11
Uses the same module layout and conventions as M01/M06: local Python CLI,
no external calls, and works alongside `modules/11-marketing-command-center/`.
