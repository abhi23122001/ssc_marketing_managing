# SHAH GROUP AI OS — M19 Master Architecture

**Status: ARCHITECTED → implementation in progress**
**Date: 2026-11-18**
**Project: SHAH AI OS — M19 Social Media Marketing Department**

## 1. Overview

M19 builds a complete AI-powered Social Media Marketing Department inside the
existing SHAH AI OS. It is NOT a scheduler or chatbot: it is an autonomous,
coordinated marketing department spanning research → strategy → production →
approval → publishing → monitoring → lead capture → reporting.

**Automation level:** HIGH. **Publishing policy:** every external publication,
public reply, or commercial action requires explicit owner/client approval.

## 2. Technology stack and constraints

- Python (stdlib + optional FFmpeg).
- SQLite (foundation store + new M19 tables) initially.
- Local-first; FFmpeg for video processing; existing Hermes orchestration.
- No subscriptions or automated charges.
- No Google Sheets, no Android (this mission).
- External platform APIs only where officially supported, with per-account
  authorization; a *test/mock mode* is used for automated validation and real
  publishing is gated behind owner approval.

## 3. Integration map (existing modules)

| Module | Resources in repo | Reuse | Required action |
|---|---|---|---|
| M06 CRM | `modules/06-crm/scripts` + README | Lead status, pipeline, follow-ups | Port CRM lead classification & sync into SM-13; expose API |
| M07 SEO | module/07 README + SEO-Keywords.py | Keywords, search intent | Reuse keyword research in SM-14 and SM-05 |
| M11 Marketing Command Center | Command-Center.py, README | Campaign & strategy planning | Integrate content strategy → campaign workflow into SM-04/SM-09 |
| M12 Content Calendar | ContentCalendar.py + README | Calendar schema | Reuse for SM-09; keep M12 intact |
| M13 Contractor lead intelligence | Lead-Intelligence.py | Lead classification | Reuse lead classification in SM-13 |
| M14 Email Assistant | EmailAssistant.py + README | Email drafting only | Reuse in SM-12 community manager drafts (never auto-send) |
| M15 HR/Employees | domain/employee.py | Employee identity/roles, KPI employees | Reuse for KPI assignment and role-based access |
| M16 Attendance | domain/attendance.py | Employee work records | Not directly reused; noted for KPI time-tracking context |
| M17 Expense | domain/expense.py | Campaign expense records | Optional: campaign expense tracking |
| M18 Payroll | domain/payroll.py | Payroll | KPI reporting only through authorized workflows |
| SHAH AI Brain | domain/ai_brain.py | Agent registry, tool execution, audit | Reuse as the M19 orchestration hub (SM-20) |

**What is NOT yet in the repo (MISSING):**

- M19 social-account registry and connection-status service.
- M19 trend/competitor research module (SM-03).
- M19 content-factory and strategy modules (SM-04/SM-05).
- M19 video/audio/graphic studios (SM-06/SM-07/SM-08).
- M19 publishing engine and platform OAuth bridges.
- M19 lead-generation and CRM-sync service.
- M19 KPI, analytics, client-agency and command-center screens.
- M19 database schema tables.

## 4. Missing services, APIs and database relationships

### 4.1 Missing services
- secure secret storage (OAuth tokens, not in Git or chat).
- per-account connection-status and sync-history service.
- platform media-processing queues (video, audio, thumbnail).
- publishing queue with idempotent dispatch and retry.
- ISO8601/date scheduling and alert service.

### 4.2 Required new APIs (foundation/api.py additions)
account registry, account connection status, profile analytics, trend research,
competitor research, content ideas, scripts/captions, media uploads, video jobs,
content calendar, task assignment, approvals, publish queue, published posts,
comments/messages, leads, KPI, reports, client workspaces, brand settings,
agent status.

### 4.3 Required new database tables (M19 schema)
`social_workspace`, `social_account`, `social_platform_permissions`,
`social_sync_history`, `social_brand`, `social_brand_asset`, `social_trend`,
`social_competitor`, `social_content_idea`, `social_script`,
`social_media_asset`, `social_video_job`, `social_subtitle`,
`social_thumbnail`, `social_content_item`, `social_content_version`,
`social_calendar_entry`, `social_approval`, `social_publish_job`,
`social_published_post`, `social_lead`, `social_employee_kpi`,
`social_campaign`, `social_agent_run`, `social_integration_log`.

## 5. System architecture (data flow)

```
SHAH AI Brain (SM-20)
   │  permission-checked tool calls
   ▼
Research: SM-03 trends/competitors  →  SM-04 strategy  →  SM-05 content factory
   ▼
Production: SM-06 video  +  SM-07 audio  +  SM-08 graphics
   ▼
SM-09 calendar → SM-10 approval → SM-11 publishing
   ▼
SM-12 inbox → SM-13 lead gen/CRM ↔ M06
   ▼
SM-16 KPI ↔ M15/M18  →  SM-17 reporting  →  SM-19 command center
```

## 6. Agent registry (SM-20)

| Agent | Tools | Workspace role |
|---|---|---|
| Marketing Director | route to all | Owner/Manager |
| Profile Auditor | social_account:read | Manager+ |
| Trend Researcher | social_account:read, trend:write | Manager+ |
| Content Strategist | content_strategy:write | Manager+ |
| Script Writer | script:write | User/Manager |
| Video Editor | video_job:create | User+ |
| Voice/Audio Agent | audio_job:create, subtitle:create | User+ |
| Graphic Designer | graphic_asset:create | User+ |
| SEO Agent | seo:analyze | Manager+ |
| Calendar Planner | calendar:create, approval_request | Manager+ |
| Publisher | publish:approve checkout | Owner+ |
| Community Manager | comment:read, draft_reply | Manager+ |
| Lead Gen Agent | lead:create (CRM sync) | Manager+ |
| Analytics Agent | report:read | Manager+ |
| KPI Agent | kpi:read | Manager+ |
| Client Account Manager | client:write | Owner+ |
| Campaign Analyst | campaign:read | Manager+ |

## 7. Publishing and approval core rule

```
content item → version locked → approval requested (owner/client)
   → explicit approve (exact version) → publish queue → verify approval again
   → real platform API → reconcile status → audit
   ← NO publish without explicit approval on the exact version
```

## 8. Status taxonomy per subsystem

PLANNED / DESIGNED / IMPLEMENTED / UNIT TESTED / INTEGRATION TESTED /
SECURITY TESTED / LIVE VERIFIED / BLOCKED / PARTIAL / PENDING.

## 9. Acceptance definition

A subsystem is complete only when its acceptance tests pass for the real
capability (not mocks) and external-platform features are separately marked
`BLOCKED`/`PENDING` until an authorized live test succeeds.

## 10. Ownership

The owner retains approval control for every publishing action. AI operates
within approved internal workflows only.

---

*Document current as of Phase 1 (preservation). Implementation follows in
dependency order: DB schema → SM-01 → SM-02/SM-03 → SM-04/SM-05 → SM-06/SM-07/SM-08
→ SM-09/SM-10/SM-11 → SM-12/SM-13/SM-14/SM-15 → SM-16/SM-17 → SM-18/SM-19/SM-20.*
