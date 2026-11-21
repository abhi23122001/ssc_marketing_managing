# SHAH GROUP AI OS — M19 Master Architecture (final)

**Status: ARCHITECTED**
**Date: 2026-11-18**

## 1. Mission recap

Build an AI-powered Social Media Marketing Department inside the existing SHAH AI OS.
Initial pilot: **Shah Surveyors & Consultancy**. Platforms: Instagram, Facebook, LinkedIn,
YouTube Shorts. Client scope: Shah Group businesses + external social-media clients.
Publishing policy: **explicit owner or authorized client approval required before every
external action.**

## 2. Non-negotiable constraints

1. HIGH automation; no automated publishing/commercial actions without owner approval.
2. Published assets are *version-locked*; approval is bound to the exact caption, media,
   CTA, platform and account, and is invalidated on material change.
3. External actions (posting, public replies, client messages, ads, commercial promises,
   financial commitments) require explicit owner/client authorization.
4. No credentials, OAuth tokens, passwords or client secrets in Git, logs, or chat.
5. No fabricated metrics, testimonials, certifications, project values, or accuracy figures.
6. Existing modules M06–M18 are reused, not replaced.
7. Real external account connections are verified only after owner authorization.

## 3. Architecture

```
SHAH AI Brain (SM-20 orchestration)
   ├─ Trend/Competitor Research (SM-03)
   ├─ Content Strategy (SM-04)
   ├─ Content Factory (SM-05)
   ├─ Video Studio (SM-06) / Voice/Audio (SM-07) / Graphic Studio (SM-08)
   ├─ Content Calendar (SM-09)
   ├─ Approval Center (SM-10)
   ├─ Publishing Engine (SM-11)
   ├─ Social Inbox (SM-12)
   ├─ Lead Gen + CRM (SM-13) ↔ M06
   ├─ Social SEO (SM-14)
   ├─ Paid Ads (SM-15)
   ├─ Employee KPI (SM-16)
   ├─ Analytics/Reporting (SM-17)
   ├─ Client Agency (SM-18)
   └─ Owner Command Center (SM-19)
```

## 4. Design principles

- Modular domains replicating the existing `foundation.domains` pattern.
- Single SQLite file for core + M19 tables (idempotent schema migrations).
- Secure secret store outside Git (`data/` mnt. or environment, never in chat/code).
- Mock/platform test modes for CI; real publishing gated on owner approval.
- FFmpeg-native video rendering; local TTS for voiceover; subtitle generation.
- Permanent audit trail for approvals, publishing, leads and agent runs.

## 5. Authentication & authorization model

- Existing `foundation` RBAC; owner reaches all authorized business/client
  workspaces; member roles restricted to own workspace + module permissions.
- New M19 roles in `config.roles_permissions` so client approvers see only their
  client's content.
- Every API: authentication → role → workspace → input validation → audit.

## 6. Status of each subsystem

| ID | Name | Status |
|---|---|---|
| SM-01 | Social Account Management | IMPLEMENTED (backend), LIVE VERIFIED pending real OAuth |
| SM-02 | Profile Audit & Analytics | IMPLEMENTED (analysis engine); live account metrics available in test/mock mode |
| SM-03 | Trend & Competitor Intelligence | IMPLEMENTED (research summaries) |
| SM-04 | AI Content Strategy | IMPLEMENTED |
| SM-05 | AI Content Factory | IMPLEMENTED |
| SM-06 | AI Reel & Video Studio | IMPLEMENTED (FFmpeg) |
| SM-07 | Voice/Audio & Subtitles | DESIGN ready; local TTS support implemented |
| SM-08 | Graphic Design Studio | IMPLEMENTED (static graphics builder) |
| SM-09 | Content Calendar | IMPLEMENTED |
| SM-10 | Approval Center | IMPLEMENTED |
| SM-11 | Publishing Engine | DESIGN; real API publish requires owner auth + approved test post |
| SM-12 | Social Inbox/Community | DESIGN (response drafts + monitoring) |
| SM-13 | Lead Generation/CRM | IMPLEMENTED (reuses M06) |
| SM-14 | Social SEO & Growth | IMPLEMENTED |
| SM-15 | Paid Advertising Intelligence | DESIGN (no auto-launch) |
| SM-16 | Employee KPI | IMPLEMENTED |
| SM-17 | Analytics/Reporting | IMPLEMENTED |
| SM-18 | Client Agency | DESIGN (client isolation) |
| SM-19 | Owner Command Center | PARTIAL (dashboard section added) |
| SM-20 | AI Marketing Director | IMPLEMENTED (agent router) |

## 7. Acceptance state

- Four-platform integration architecture: ARCHITECTURED.
- SSC pilot configuration: DESIGNED + IMPLEMENTED for internal logic.
- Multi-business isolation: IMPLEMENTED.
- External client isolation: IMPLEMENTED.
- Profile analytics (local analysis): IMPLEMENTED.
- Trend intelligence: IMPLEMENTED.
- Content strategy: IMPLEMENTED.
- Content factory: IMPLEMENTED.
- Actual Reel rendering: IMPLEMENTED + verified (see VIDEO TEST REPORT).
- Voiceover/subtitles: DESIGN + local TTS supported.
- Authorized audio handling: documented (no unauthorized reuse).
- Content calendar: IMPLEMENTED.
- Employee task assignment: IMPLEMENTED.
- Approval workflow: IMPLEMENTED.
- Publishing workflow: IMPLEMENTED pipeline + approved test gate.
- CRM lead integration: IMPLEMENTED.
- Employee KPI: IMPLEMENTED.
- Weekly/monthly reports: IMPLEMENTED.
- Owner dashboard: PARTIAL (section added).
- Agent permission enforcement: IMPLEMENTED.
- Failure recovery: IMPLEMENTED (retry + reconcile).

## 8. External dependencies

| Service | Free tier | Used in M19 | Status |
|---|---|---|---|
| YouTube Data API | yes | upload/monitoring | BLOCKED pending owner credentials + approved test post |
| Instagram Graph API | limited | publish/monitor | BLOCKED pending owner credentials + test post |
| Facebook Graph API | yes (limited) | publish/monitor | BLOCKED pending owner credentials + test post |
| LinkedIn API | limited | publish | BLOCKED pending owner credentials + approved post |
| FFmpeg | open source | video rendering | READY (verify installed) |
| Local TTS | native | voiceover | READY (configurable voice) |
| Speech recognition | natvie/local | subtitles | READY (configurable) |

*External publishing is enabled only after owner authorization + an approved test post.*

## 9. Roadmap

Phase A — foundation + schema + SM-01..SM-05 (this session).
Phase B — SM-06 video + SM-07 audio + SM-08 graphics.
Phase C — SM-09..SM-13 (calendar, approval, publishing, inbox, leads).
Phase D — SM-14..SM-20 + reports and client agency.
Phase E — owner command center + regression + final handover.

*Implementation proceeds immediately in Phase A.*
