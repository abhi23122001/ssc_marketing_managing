# SHAH Group AI OS — Next Phase Roadmap

**Version**: 1.0  
**Date**: 2026-11-20  
**Current State**: Phase 3/4 Complete — 293/293 tests PASS, full HR, Payroll, Follow-ups, CSV Exports, Security hardening & AI tool execution operational

---

## Roadmap Overview

```
Phase 1 ✅ DONE  — Discovery, Audit, Security Hardening
Phase 2 ✅ DONE  — Business Workflows, CRM, Finance, Testing
Phase 3 ✅ DONE  — HR & Payroll, Security Hardening, Follow-ups, CSV Exports, Rate-Limiting, 293/293 Tests
Phase 4 🚀 NEXT  — Dedicated Invoicing & Quotations with PDF Generation, GST Engine
Phase 5 🔮 FUTURE — Google Sheets, Android App, Multi-site Field Sensor Integration
```

---

## Phase 3 — Recommended Next Sprint

**Estimated effort**: 1–2 Antigravity sessions (~4–8 hours)

### 3A — HR & Employee Module (Priority: HIGH)

The `employees`, `departments`, `attendance_logs`, `leaves`, `payslips` tables all exist in the database with 0 rows. The API layer needs to be built.

**Tasks**:
1. Add `GET /api/employees` and `POST /api/employees` endpoints to `foundation/api.py`
2. Add `list_employees()` and `create_employee()` to `foundation/store.py`
3. Add `GET /api/attendance` and `POST /api/attendance` endpoints
4. Add `GET /api/leaves` and `POST /api/leaves` endpoints  
5. Build Employee tab in dashboard to show real employee records (not just users)
6. Seed 5–10 synthetic employee records for testing
7. Write `tests/test_hrm_module.py` with 15+ checks

**Acceptance criteria**:
- Employee records can be created and listed via API
- Attendance log can be submitted via API
- Leave requests route to approval queue
- Dashboard Employee tab shows real HR data

---

### 3B — Payroll Calculator (Priority: HIGH)

**Tasks**:
1. Add `POST /api/payroll/run` endpoint to trigger payroll calculation
2. Implement salary calculation logic in `foundation/domains/payroll.py` (new file)
3. Generate payslip records in `payslips` table
4. Add payslip download/print endpoint (HTML or PDF)
5. Write `tests/test_payroll.py` with 10+ checks

**Acceptance criteria**:
- Payroll run calculates gross, deductions, net pay per employee
- Payslip record created per employee per period
- Payslip printable from dashboard

---

### 3C — Production Security Hardening (Priority: HIGH)

**Tasks**:
1. Add nginx reverse proxy configuration (`config/nginx.conf`)
2. Add request rate limiting middleware to `foundation/api.py` (token bucket algorithm)
3. Add failed-login counter and account lockout to `foundation/store.py`
4. Add password complexity validation to `POST /api/auth/password`
5. Add minimum-8-char enforcement to `POST /api/users`
6. Document nginx + Let's Encrypt setup procedure

**Acceptance criteria**:
- Brute-force login blocked after 5 failures
- Requests rate-limited to 100/minute per IP
- Password rejects short/simple passwords
- Nginx config documented for HTTPS setup

---

### 3D — Follow-up Scheduler (Priority: MEDIUM)

**Tasks**:
1. Add `follow_up_at` datetime column to `social_leads` table
2. Add `GET /api/leads/due-follow-ups` endpoint
3. Add follow-up scheduling UI to CRM tab (date picker on lead row)
4. Add `GET /api/notifications` endpoint returning overdue follow-ups
5. Add notification badge to dashboard header

**Acceptance criteria**:
- Follow-up dates can be set per lead
- Dashboard shows overdue follow-up count in badge
- Due follow-ups list visible on CRM tab

---

### 3E — Export & Reports (Priority: MEDIUM)

**Tasks**:
1. Add `GET /api/leads/export` → CSV download
2. Add `GET /api/finance/expenses/export` → CSV download  
3. Add `GET /api/sites/export` → CSV download
4. Add Chart.js to dashboard for KPI visualization
5. Add bar chart: leads by status per workspace
6. Add line chart: expenses over time

**Acceptance criteria**:
- Export buttons download real CSV data
- Dashboard shows at least 2 interactive charts

---

## Phase 4 — Advanced Features

**Estimated effort**: 2–3 Antigravity sessions

### 4A — Invoice & Quotation Module
- Proper invoice numbering (SSC-INV-2026-001 format)
- Quotation with itemized BOQ (Bill of Quantities)
- GST calculation (18% / 28% per line item)
- PDF generation (using `reportlab` or `weasyprint`)
- Invoice status tracking (draft → sent → paid → overdue)

### 4B — AI Brain — Real LLM Integration
- Wire AI Brain chat to Gemini API (`gemini-2.0-flash`)
- Each specialist agent gets its own system prompt
- Tool execution framework for agents (call internal APIs)
- Agent memory / context storage in `ai_tasks` table
- 12 specialist agents seeded and operational

### 4C — Work Order Module
- Formal Work Order creation (linked to quotation + client)
- WO approval workflow (Manager → Owner)
- WO status tracking (issued → in-progress → completed → closed)
- WO PDF generation
- Link WO to survey sites and project milestones

### 4D — Project Milestones & Gantt
- `project_milestones` table with start/end dates
- Milestone dependency tracking
- Simple Gantt-style bar view in Projects tab
- Milestone completion → auto-trigger invoice

---

## Phase 5 — Future Enhancements

**Estimated effort**: 3+ Antigravity sessions each

### 5A — Google Sheets Integration
- Read leads from Google Sheet (OAuth + Sheets API)
- Push weekly summary report to Google Sheet
- Two-way sync for expense claims
- Credentials stored securely in `config/secrets.json` (gitignored)

**Architecture ready**: The API structure and deduplication logic already exist. Only OAuth flow and Sheets client library needed.

### 5B — Android Mobile App
- React Native or Flutter wrapper around existing API
- Mobile-optimized login and dashboard
- GPS attendance check-in via device GPS
- Push notifications for approvals
- Offline-first SQLite cache

**Architecture ready**: REST API is fully mobile-compatible. No backend changes needed.

### 5C — Multi-site / Cloud Deployment
- Migrate SQLite → PostgreSQL for multi-instance concurrency
- Docker containerization (`Dockerfile`, `docker-compose.yml`)
- Nginx load balancer config
- AWS / GCP deployment guide

### 5D — Document Management System
- File upload endpoint (`POST /api/documents`)
- Versioned document storage with SHA-256 integrity
- Document categories: Survey Reports, Contracts, Permits, Drawings
- Document search and preview
- Link documents to projects, clients, employees

### 5E — Equipment & Calibration Management
- Equipment registry (Total Station, DGPS receiver, Drone, Level)
- Calibration schedule tracking
- Equipment assignment to field teams
- AMC (Annual Maintenance Contract) tracking

---

## Quick Win List (< 2 hours each)

| Task | Benefit | Effort |
|------|---------|--------|
| Add Chart.js KPI charts to dashboard | Visual impact | 2 hrs |
| Add CSV export buttons | Business utility | 1 hr |
| Seed 8 missing AI agents | Complete AI roster | 1 hr |
| Add follow-up date picker to CRM | Sales workflow | 2 hrs |
| Add password complexity validation | Security | 30 min |
| Add account lockout after 5 failures | Security | 1 hr |
| Add nginx HTTPS config doc | Production readiness | 1 hr |
| Add Windows Task Scheduler backup guide | Operations | 30 min |

---

## Technical Debt Backlog

| Item | File | Effort |
|------|------|--------|
| Split `foundation/api.py` into domain-specific files | `foundation/api.py` | 4 hrs |
| Add type hints to all Store methods | `foundation/store.py` | 2 hrs |
| Add request validation middleware | `foundation/api.py` | 2 hrs |
| Move `tmp_full_api_test.py` to `tests/test_live_api.py` | Root | 15 min |
| Remove redundant `tmp_*.py` scratch files | Root | 15 min |
| Add `.env` support for secrets | `foundation/config.py` | 1 hr |
| Add OpenAPI / Swagger documentation generation | New file | 3 hrs |

---

## Recommended Phase 3 Start Prompt

When starting a new Antigravity session for Phase 3, use this prompt:

```
Resume SHAH Group AI OS development. Project is at:
C:\Users\HP\Desktop\ssc_marketing_managing
Server runs on http://127.0.0.1:8899/
Python: C:\Users\HP\AppData\Local\hermes\tools\python-3.14.9+20261021-win32-x64\python.exe

Current state: Phase 2 complete. 226/226 tests pass.
Read FINAL_PROJECT_HANDOVER.md and NEXT_PHASE_ROADMAP.md first.

Your Phase 3 mission:
1. Implement HR & Employee module (Phase 3A)
2. Implement Payroll calculator (Phase 3B)
3. Add security hardening: rate limiting + account lockout (Phase 3C)
4. Add CSV export endpoints (Phase 3E)
5. Run full test suite and verify 226+ tests PASS
6. Create Phase 3 backup and verify restore
7. Update all documentation
```

---

*Roadmap prepared by Antigravity Autonomous Development Agent — 2026-11-20*
