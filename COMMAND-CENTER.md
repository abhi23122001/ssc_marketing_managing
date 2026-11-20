
# COMMAND-CENTER — SHAH AI Marketing Management System

**Project dashboard and module navigation hub**
For Shah Surveyors & Consultancy (SSC)

---

## 1. Project identity

| Item | Detail |
|---|---|
| AI assistant brand | SHAH AI |
| Business supported | Shah Surveyors & Consultancy (SSC) |
| Owner location context | Singrauli / Waidhan, Madhya Pradesh, India |
| Source runtime | Hermes Agent (upstream, protected) |
| Current phase | Phase 2 — base modules 01–05 functional |

## 2. Status

| Item | State |
|---|---|
| Phase 2 (base modules) | In progress — modules 01–05 fleshed out in this phase |
| Command Center launcher | `Start-SHAI-Center.ps1` |
| Central dashboard | `COMMAND-CENTER.md` |
| Module library | `modules/`, 10 modules |
| Shared templates | `shared/templates/` |
| Shared scripts | `shared/scripts/` |
| Architecture document | `docs/MODULES-ARCHITECTURE.md` |

## 3. Quick start

1. Run the launcher: `.\Start-SHAI-Center.ps1`
2. Select a module number from the menu.
3. Read the module README for that area.
4. Work in drafts — never publish, schedule, message, contact, or spend
   without an explicit owner approval record (see Section 6).

## 4. Module navigation

| # | Module | Path |
|---|---|---|
| 1 | Marketing Command Center | `modules/01-marketing-command-center/` |
| 2 | Daily Content Planner | `modules/02-daily-content-planner/` |
| 3 | Instagram and Facebook Content Studio | `modules/03-instagram-facebook-content-studio/` |
| 4 | LinkedIn B2B Marketing | `modules/04-linkedin-b2b-marketing/` |
| 5 | Google Business Profile Management | `modules/05-google-business-profile-management/` |
| 6 | Contractor Lead Research and CRM | `modules/06-contractor-lead-research-crm/` |
| 7 | SEO and Keyword Research | `modules/07-seo-keyword-research/` |
| 8 | AI Image and Video Creation Workflow | `modules/08-ai-image-video-workflow/` |
| 9 | Content Approval and Publishing Workflow | `modules/09-content-approval-publishing-workflow/` |
| 10 | Analytics and Monthly Reporting | `modules/10-analytics-monthly-reporting/` |
| 11 | Unified Marketing Command Center | `modules/11-marketing-command-center/` |
| 12 | Content Calendar & Content Generation | `modules/12-content-calendar-content-generation/` |
| 13 | Contractor Lead Intelligence | `modules/13-contractor-lead-intelligence/` |
| 14 | Email Assistant | `modules/14-email-assistant/` |
|| Shared scripts | `shared/scripts/Task-Followup.ps1` + `shared/scripts/AutomationPlanner.py` |
|| Shared templates | `shared/templates/` (brief, draft, QA, approval, report) |

## 4.1 Module 06 — Contractor Lead Research and CRM

Run the console launcher from the module folder:

```powershell
.\06-contractor-lead-research-crm\Start-SHAI-CRM.ps1
```

Main commands: `list`, `search`, `dashboard`, `validate`, `backup`, `import`, `export`.

## 4.2 Module 07 — SEO and Keyword Research

Run the console launcher from the module folder:

```powershell
.\07-seo-keyword-research\Start-SHAI-SEO.ps1
```

Main commands: `list`, `search`, `cluster`, `local`, `report`.

## 5. Approval and publishing rules

- **Draft-only by default.** Every output is a draft until approved.
- **Do not publish, schedule, send, message, contact, or spend** without an
  explicit owner approval record for that exact action.
- **No fabricated proof.** Clients, projects, approvals, certifications,
  equipment, accuracy, results, testimonials, prices, and contact details
  must not be invented.
- **No unregistered org references** (NTPC, NCL, SECL, Coal India, etc.) as
  client or project proof without explicit owner approval and evidence.
- **Confidential material** (drawings, coordinates, reports, credentials,
  personal data) stays out of Git and public content.

## 5. Pending drafts, approvals and tasks summary

Draft-only board. Working files live in `data/` and each module folder.

| File | Purpose |
|---|---|
| `data/content-calendar.csv` | Daily / weekly / monthly content planning |
| `data/instagram-library.csv` | SSI & Facebook content asset ideas |
| `data/linkedin-topics.csv` | LinkedIn B2B topic list |
| `data/status-tasks.csv` | Open tasks and approvals |
| `data/gbp-audit-checklist.csv` | GBP audit checklist |

Approval and publishing rules (unchanged): work is draft-only by default; the owner
must approve every external action; no fabricated proof, accuracy claims, or confidential
data in Git or public content.

## 6. Directory map

```
├── COMMAND-CENTER.md
├── Start-SHAI-Center.ps1
├── modules/                  # 10 requested modules (one folder each)
├── shared/
│   ├── templates/            # briefs, checklists, forms, skeletons
│   └── scripts/              # Windows-compatible helper scripts
├── data/                     # non-confidential structured data (CSV)
├── outputs/                  (gitignored) draft deliverables
├── generated/                (gitignored) AI illustrations, labeled
├── media/                    asset library (footage, photos)
├── private-client-data/      (gitignored) confidential work
└── vendor/hermes-agent/      UPSTREAM — do not modify
```

## 7. How to add work

- **New content:** open the relevant module README and use the shared
  templates in `shared/templates/` for brief, draft, QA, and approval.
- **Data:** add non-confidential CSVs to `data/` (keywords, calendars,
  verified lead lists).
- `data/leads.csv` — contractor lead list (Module 06, verified public data only).
- `data/keywords.csv` — SEO keyword library (Module 07).

- **Media:** place approved/owned footage in `media/`; label AI-generated
  visuals clearly and never present them as project evidence.
- **Report:** use the analytics module with owner-supplied metrics only.

## 8. Quick references

- Full architecture: `docs/MODULES-ARCHITECTURE.md`
- Setup guide: `docs/SETUP-WINDOWS.md`
- Public content QA: `docs/CONTENT-QA-CHECKLIST.md`
- SHAH AI brand profile: `brand/ssc-brand-profile.md`
- SHAH AI skill: `.hermes/skills/shah-ai/SKILL.md`
- SHAH AI persona: `config/SOUL.md`
