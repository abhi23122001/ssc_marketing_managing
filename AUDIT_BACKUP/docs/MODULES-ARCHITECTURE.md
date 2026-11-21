# SHAH AI Marketing Management System — Architecture

This document records the approved architecture for the SHAH AI Marketing
Management System. It sits on top of the existing repository and does not
modify upstream Hermes source.

---

## 1. Overview

SHAH AI is the branded AI assistant for Shah Surveyors & Consultancy (SSC).
The assistant's core runtime is **Hermes Agent** (upstream, pinned as a Git
submodule). This system adds a text-management layer: a command center,
ten content modules, shared templates, scripts, data, and a publishing gate.

**Design rules**

- Hermes is the AI brain, not a replacement.
- SHAH AI persona (`config/SOUL.md`) and SHAH AI skill (`.hermes/skills/shah-ai/SKILL.md`)
  are the content engine.
- Output is text-based and local. No external accounts, APIs, or paid
  services are required.
- Windows-native (PowerShell + Python stdlib).
- Everything is draft-only until an explicit owner approval record exists.

## 2. Component diagram

```
Central AI runtime (Hermes Agent, upstream)
  - vendor/hermes-agent (protected)
  - config/SOUL.md
  - .hermes/skills/shah-ai/SKILL.md

Management layer
  -COMMAND-CENTER.md                 (hub)
  -Start-SHAI-Center.ps1             (console launcher)
  -modules/                          (10 modules)
  -shared/templates/                 (briefs, checklists, forms)
  -shared/scripts/                   (Open-Readme.ps1, Write-Draft.ps1)
  -data/                             (non-confidential CSV)
  -outputs/  (gitignored)
  -generated/  (gitignored)
  -media/                            (asset library)
  -private-client-data/  (gitignored)

Publishing gate
  - Module 09 approval/publishing workflow
  - docs/CONTENT-QA-CHECKLIST.md

CI
  - .github/workflows/validate.yml  (extended, upstream untouched)
```

## 3. Folder layout

```
ssc_marketing_managing/
├── COMMAND-CENTER.md
├── Start-SHAI-Center.ps1
├── modules/                  # 10 modules, one folder each
├── shared/
│   ├── templates/            # briefs, checklists, forms, skeletons
│   └── scripts/              # Windows-compatible helper scripts
├── data/                     # non-confidential structured data
├── outputs/                  (gitignored) draft deliverables
├── generated/                (gitignored) AI illustrations, labeled
├── media/                    asset library (footage, photos)
├── private-client-data/      (gitignored) confidential work
├── vendor/hermes-agent/      UPSTREAM — do not modify
├── .github/workflows/validate.yml
└── .gitignore
```

## 4. Module map

| # | Module | Purpose | Output |
|---|---|---|---|
| 1 | 01-marketing-command-center | Launcher + dashboard | CLI, hub |
| 2 | 02-daily-content-planner | Weekly plan table | Markdown table |
| 3 | 03-instagram-facebook-content-studio | Reels, carousels, captions | Drafts |
| 4 | 04-linkedin-b2b-marketing | B2B posts, outreach drafts | Drafts |
| 5 | 05-google-business-profile-management | GBP posts, local SEO | Drafts |
| 6 | `06-contractor-lead-research-crm` | Contractor lead research & CRM | `data/leads.csv` + portal scripts (`Start-SHAI-CRM.ps1`) + dashboard |
| 7 | `07-seo-keyword-research` | SEO & keyword research | `data/keywords.csv` + portal scripts (`Start-SHAI-SEO.ps1`) + SEO plan |
| 8 | 08-ai-image-video-workflow | Illustrative media workflow | Drafts + labeled AI visuals |
|| 9 | 09-content-approval-publishing-workflow | Approval gate | Approval records |
|| 10 | 10-analytics-monthly-reporting | Monthly report skeleton | Draft reports |
|| 11 | 11-marketing-command-center | Unified marketing command center (launcher + proxy) | launcher + dashboard |
|| 12 | 12-content-calendar-content-generation | Content calendar + content generation | drafts + tests |
|| 13 | 13-contractor-lead-intelligence | Contractor lead intelligence | lead list + analysis |
|| 14 | 14-email-assistant | Email assistant (draft-only; Gmail sync disabled) | drafts + tests |
|| Shared scripts | shared/scripts/Task-Followup.ps1 + shared/scripts/AutomationPlanner.py | Task follow-up + automation dry-run | view only |

## 5. Technology choices

| Component | Choice | Reason |
|---|---|---|
| AI core | Hermes Agent (upstream, pinned) | Existing branded runtime + skill |
| Identity | config/SOUL.md | Existing persona template |
| Orchestration | PowerShell 5.1+ console launcher | Native on Windows 11 |
| Scripting | Python 3 stdlib only | No pip; portable helpers |
| Content library | Markdown + CSV | Reviewable, no lock-in |
| Media | ffmpeg + GIMP/Inkscape (free) | Free/OSS, Windows-compatible |
| AI image/video | Owner-chosen provider | External decision delegated to owner |
| CI | GitHub Actions (existing validate.yml) | Extended, never rewritten |

## 6. Draft → approval → publish workflow

```
Request / brief
  → Module script prepares structured DRAFT (markdown/CSV)
  → Apply CONTENT-QA-CHECKLIST
  → Flag technical claims for qualified SSC review
  → Owner approval record (who, channel, date)
  → Only then: publish / schedule / send / contact
```

## 7. Required integrations

- **Hermes Agent** — central runtime + `/shah-ai` skill for drafting and QA.
- **Windows 11 console** — PowerShell 5.1+ menu and script dispatch.
- **Free/OSS media tools** — ffmpeg, GIMP, Inkscape, or owner's chosen
  AI image/video provider.
- **Git + GitHub Actions** — CI validation, extended and upstream-protected.
- **Excel / Google Sheets** — CSV interchange.

## 8. Guardrails

- `vendor/hermes-agent` is protected; CI validation ensures it is not
  altered.
- No publishing without an approval record.
- No fabricated clients, projects, certifications, accuracy, prices, or
  contact details.
- No unrestricted scraping or personal-data exposure.
- AI visuals are labeled illustrative and never project evidence.
- Confidential data stays gitignored and out of the repo.
