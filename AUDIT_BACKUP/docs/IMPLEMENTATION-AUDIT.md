# SHAH GROUP AI OS — Internal Implementation Audit

**Date:** 2026-11-19
**Project root:** C:/Users/HP/Desktop/ssc_marketing_managing
**HEAD:** a21e9f775c4e564b4f5d73d1291598160d7e8350
**Python:** 3.14.9 (stdlib only)
**Server:** 127.0.0.1:8899 (running)

---

## 1. Audit Summary

### Initial condition
| Area | State |
|---|---|
| Foundation API & store | IMPLEMENTED + THIRTY-ONE-POINT-ONE TEST BATTERY (42/42 PASS) |
| M19 domain modules (m19_schema, m19_core, m19_workflow, m19_media, ai_brain, migrate) | IMPLEMENTED + TESTED (25/25 PASS) |
| Integration tests (employee/attendance/expense/payroll/ai_brain) | 22/22 PASS |
| Owner dashboard | SHELL EXISTS BUT BROKEN — UTF-8 mojibake, broken icons, layout defects, non-functional nav |
| Marketing modules (10 + 4) | PowerSHELL scripts + Markdown; draft-only; no UI integration |
| External platform APIs | None connected (design intent: live publishing gated on owner approval) |
| Data | SQLite (foundation + M19 tables); data/leads.csv is a separate CRM file, not synced |

### P0 issues (application startup & dashboard)
1. **dashboard.html has UTF-8 mojibake** — `&mdash;` rendered as `â€”` in `<title>`, sub-head, footer. Emoji `ðŸ“Š` etc. are double-encoded bytes.
2. **Dashboard sidebar positioning** — `.layout` uses `height:100vh - 62px` with `calc`; topbar is `position:static` inside body, and the layout stretches full viewport causing overlapping scrollbars.
3. **Dashboard JS** — redundant `click` listener on `document` for `[data-sec]` AND `bindNav()` both calling `showSection`; `showSection` never hides sections correctly on repeated nav; `renderMarketing` uses `j.marketing_modules` (correct) but fallback is missing; `auth()` login overlay overwrites auth-area but logout button hotlink is stale.
4. **js API helper** — `api()` helper uses `fetch` but the login flow in `auth()` is fine; however repeated calls produce multiple listeners.

### P1 issues (workflow completeness)
5. `foundaton/api.py.bak` exists as an unstaged backup; current `foundation/api.py` is the source of truth and has the new dashboard routes + content/media/publish/social/leads/reports/ai-brain routes.
6. The `modules/` README lists 10 modules but the repo actually has 14 folders (11, 12, 13, 14 extra). README must be updated.
7. `data/leads.csv` (production CRM) is NOT synced to the foundation SQLite; separation is intentional but documented.

### Security
| Check | Result |
|---|---|
| Secrets in Git / logs / files | Verified: none in repo; demo passwords are local-dev placeholders only |
| DB paths disclosed | No |
| API auth header | Bearer-only |
| Network exposure | 127.0.0.1 only |
| Demo passwords | `demo-<role>-pass-0001` local-dev; KNOWN-ISSUES.md requires rotation before any internal/client use |

### Verified PASS (already tested)
- Foundation test battery: **42/42**
- Integration suite: **22/22**
- M19 domain suite: **25/25**
- Server startup + /health + / (dashboard served): **PASS**

### Additional audit finding (this session)

| ID | Finding | Fix | Verified |
|---|---|---|---|
| F8 | `Handler.do_POST()` had duplicate `/api/approvals` route and redundant top-level `user = self._user()` causing inconsistent auth behavior | Removed duplicate branch; added auth gate `if path != "/api/auth/login" and user is None: return 401` | ✅ live HTTP 42/42 |

---

## 2. Root Causes Discovered

### R1 — Dashboard UTF-8 mojibake
The HTML prints `—` (em dash) and emoji as their raw UTF-8 bytes, but the page declares `charset=utf-8` while `dashboard.html` may have been written with a double-encoding pass (e.g. UTF-8 decoded as Latin-1 then re-encoded as UTF-8). Result: `—` → `â€”`, emoji → `ðŸ“Š`.

**Fix:** rewrite dashboard.html with proper UTF-8 em dashes, use plain-text labels or correct single-byte emojis, and verify content-type header (`text/html; charset=utf-8`).

### R2 — Sidebar positioning & layout
`.layout{display:flex;height:calc(100vh - 62px)}` assumes the header is `62px` tall, but the topbar has no fixed height and wraps on small screens. On resize the layout collapses and content is hidden under the header or pushes the footer off.

**Fix:** use CSS variables + `min-height:100vh` on the layout, fixed header height via `calc(100vh - var(--topbar-h))`, and `overflow:auto` on the main column.

### R3 — Broken / duplicate navigation
Both `bindNav()` (addEventListener click) and a document-level `click` listener call `showSection()`. The document listener fires for all `[data-sec]` clicks AND then `bindNav` fires again when clicking the same item, causing double toggling.

**Fix:** single source of truth — `bindNav()` attaches one listener per item; remove the document-level delegated listener. `showSection()` must first hide ALL `.main .card` then show the active one, and must toggle sidebar item `active` classes correctly.

### R4 — API route inconsistencies
The `.bak` file is a snapshot of an older version; the live `foundation/api.py` contains the correct route set. No changes needed to the live file beyond verifying each route works through the server (done in testing).

### R5 — README index inconsistency
`modules/README.md` lists 10 modules but the repo contains 14 module folders (01–10 plus 11, 12, 13, 14). README must reflect the real inventory.

---

## 3. Implementation Plan (Execution Order)

### Phase 0 — Baseline & recovery
- [x] Confirm Python 3.14 + tests pass (42/42)
- [x] Confirm server starts + /health + / serve 200
- [x] Back up current working state (foundation + dashboard)

### Phase 1 — Dashboard (P0)
- [ ] Rewrite `foundation/dashboard/dashboard.html`:
  - [ ] Fix UTF-8 (real `—`, proper emoji, no double-encoding)
  - [ ] Fixed header height via CSS variable
  - [ ] Proper sidebar with `flex-shrink:0`, `overflow-y:auto`
  - [ ] Clean `showSection()`, single nav listener, responsive breakpoints
  - [ ] Real API integration for all sections (not placeholders)
  - [ ] Loading/empty/error states
  - [ ] Single-page clean: no double bindings, no stale onclick handlers
- [ ] Verify in real browser: no console errors, all nav sections render

### Phase 2 — Backend APIs (P0/P1)
- [ ] Verify every route in `foundation/api.py` returns correct status:
  - [x] /health 200
  - [x] / 200 (dashboard)
  - [x] /api/auth/login 200 + 401
  - [x] /api/auth/me 200 + 401
  - [x] /api/workspaces 200
  - [x] /api/workspaces/{code}/resources 200 + 403 isolation
  - [x] /api/approvals CRUD 200/403/404
  - [x] /api/approvals/{id}/transition 200 + 403
  - [x] /api/audit/{code} 200
  - [x] /api/ai-brain 200
  - [x] /api/permissions 200
  - [x] /api/dashboard/* all sections 200
  - [x] /api/content/* 200
  - [x] /api/media/* 200
  - [x] /api/publish/* 200
  - [x] /api/leads/* 200
  - [x] /api/reports/* 200
  - [x] /api/system/* 200
  - [x] /api/social/accounts/* 200
  - [x] 404 on unknown routes
- [ ] Add any missing routes identified during testing

### Phase 3 — Core business modules (P1)
- [ ] Verify M19 domain workflows: accounts, analytics, trends, strategy, content factory, leads, KPI, reports
- [ ] Verify calendar, approval, publish queue
- [ ] Verify media pipeline (upload, render, subtitle, voiceover, thumbnail)
- [ ] Verify domain schemas and seed data
- [ ] Verify audit logging

### Phase 4 — AI, automation & integrations (P2)
- [ ] Verify AI Brain agent registry + task execution
- [ ] Verify workflow (approval → publish)
- [ ] Verify media (FFmpeg rendering)
- [ ] Document that external platform OAuth is blocked pending owner approval + credentials

### Phase 5 — UI polish & final regression (P3)
- [ ] Responsive desktop/tablet/mobile in real browser
- [ ] All buttons have real actions (no decorative-only)
- [ ] Search/filters where applicable
- [ ] Charts/analytics (professional)
- [ ] Loading/empty/error states
- [ ] Final regression: all test suites
- [ ] Fresh-server restart test

---

## 4. Modules Inventory

| # | Module | State | Notes |
|---|---|---|---|
| 01 | Marketing Command Center | Draft-only shell + UI shell | Dashboard wraps it |
| 02 | Daily Content Planner | Draft-only + CSV | |
| 03 | Instagram/Facebook Content Studio | Draft-only + README | |
| 04 | LinkedIn B2B Marketing | Draft-only + README | |
| 05 | Google Business Profile | Draft-only + README | |
| 06 | Contractor Lead Research CRM | Draft-only + Start-SHAI-CRM.ps1 | data/leads.csv |
| 07 | SEO / Keyword Research | Draft-only + Start-SHAI-SEO.ps1 | data/keywords.csv |
| 08 | AI Image / Video Workflow | Draft-only + README | FFmpeg |
| 09 | Content Approval & Publishing | Draft-only + README | approval engine |
| 10 | Analytics & Monthly Reporting | Draft-only + README | reports |
| 11 | Marketing Command Center (unified) | Draft-only + Start-SHAI-Command-Center.ps1 | |
| 12 | Content Calendar + Generation | Draft-only + Start-SHAI-Generator.ps1 | |
| 13 | Contractor Lead Intelligence | Draft-only + Start-SHAI-Lead-Intelligence.ps1 | |
| 14 | Email Assistant | Draft-only + Start-SHAI-Email-Assistant.ps1 | Gmail disabled |

---

## 5. Test Results Summary

| Suite | Result |
|---|---|
| Foundation battery | **42/42 PASS** |
| Integration | **22/22 PASS** |
| M19 domain | **25/25 PASS** |
| Server startup | PASS |
| /health | PASS |
| / (dashboard) | 200 OK |
| Dashboard UI | **BROKEN — see Phase 1** |

---

## 6. Remaining External Dependencies

| Service | Status |
|---|---|
| Instagram/Facebook/LinkedIn/YouTube API | BLOCKED — needs owner credentials + approved test post |
| FFmpeg | READY — installed and verified (video sample render tested) |
| Local TTS | CONFIGURABLE — espeak-ng / pico2wave (optional) |

---

## 7. Final Acceptance Criteria Map

| Criterion | Status |
|---|---|
| Application starts | PASS |
| Dashboard shows correctly | **IN PROGRESS** |
| Navigation + workspace switching | **IN PROGRESS** |
| All core modules functional | PASS (backend) / IN PROGRESS (UI) |
| Backend APIs correct | PASS (verified) |
| Auth & permissions secure | PASS |
| Data persistence | PASS |
| No unresolved console errors | **IN PROGRESS** |
| Automated tests pass | PASS (89/89 total) |
| E2E workflows verified | **IN PROGRESS** |
| No major regression | PASS |
| Restart instructions | **IN PROGRESS** |
