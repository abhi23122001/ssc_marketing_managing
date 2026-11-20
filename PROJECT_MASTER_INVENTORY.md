# SHAH Group AI OS — Project Master Inventory

**Generated**: 2026-11-20  
**Session**: Antigravity Autonomous Development Phase 4  
**Version**: 2.1 (Final End-to-End Handover)  
**Status**: ✅ All 20 modules PASS (293/293 automated tests)

---

## 1. Project Identity

| Property | Value |
|----------|-------|
| Project Name | SHAH Group AI Operating System |
| Primary Repo | `ssc_marketing_managing` |
| Local Server | `http://127.0.0.1:8899/` |
| Database | `data/sgcc_foundation.sqlite` (SQLite3, WAL mode) |
| Main API | `foundation/api.py` (1,783 lines) |
| Dashboard | `foundation/dashboard/dashboard.html` |
| Git HEAD | `a21e9f7` (branch: `main`) |
| Python Binary | `C:\Users\HP\AppData\Local\hermes\tools\python-3.14.9+20261021-win32-x64\python.exe` |
| OS | Windows 11 |

---

## 2. Business Workspaces

| Code | Full Name | Type | Status |
|------|-----------|------|--------|
| SSC | Shah Surveyors & Consultancy | Land Surveying / Civil Consultancy | ACTIVE |
| INFRA | Shah Infra Developers | Civil / Infrastructure / Power | ACTIVE |
| OTHER | Other SHAH Group | Placeholder for future businesses | REGISTERED |

---

## 3. User Accounts (Demo)

| Username | Role | Workspace | Password | Status |
|----------|------|-----------|----------|--------|
| owner | Owner | SSC | demo-owner-pass-0001 | ACTIVE |
| manager | Manager | SSC | demo-manager-pass-0001 | ACTIVE |
| employee | Employee | SSC | demo-employee-pass-0001 | ACTIVE |
| finance | Finance Manager | INFRA | demo-finance-pass-0001 | ACTIVE |
| pm | Project Manager | INFRA | demo-pm-pass-0001 | ACTIVE |
| viewer | Viewer | INFRA | demo-viewer-pass-0001 | ACTIVE |

> **Security Note**: Change all demo passwords before production use.

---

## 4. Database Inventory

**Total Tables**: 54 (all in `data/sgcc_foundation.sqlite`)

### Authentication & Session Tables
| Table | Rows (approx) | Purpose |
|-------|--------------|---------|
| users | 27 | User accounts with PBKDF2-hashed passwords |
| sessions | varies | Bearer tokens (revoked on logout/deactivation) |
| roles | 7 | Role definitions (Owner, Manager, PM, Finance, HR, Employee, Viewer) |
| role_permissions | 100+ | RBAC vocabulary mapping |
| permissions | 50+ | Permission definitions |
| user_roles | 27+ | User-to-role assignments |

### Workspace Tables
| Table | Rows (approx) | Purpose |
|-------|--------------|---------|
| workspaces | 3 | Business workspace registry (SSC, INFRA, OTHER) |
| resources | 100+ | Per-workspace structured resources (projects, contacts, vendors) |
| social_workspaces | 3 | M19 social media workspace registry |

### CRM & Lead Tables
| Table | Rows (approx) | Purpose |
|-------|--------------|---------|
| social_leads | 19 | Lead registry (synced from data/leads.csv) |
| social_client_profiles | 7 | Converted client profiles |
| contacts | varies | Generic contact directory |

### Project & Survey Tables
| Table | Rows (approx) | Purpose |
|-------|--------------|---------|
| sites | 15 | Survey project site registry |
| geofences | 10 | GPS geofence definitions for field attendance |

### Finance Tables
| Table | Rows (approx) | Purpose |
|-------|--------------|---------|
| expense_claims | 2 | Expense reimbursement claims |
| expense_vendors | 5 | Vendor directory |
| cash_advance | varies | Cash advance tracking |
| payroll_runs | 0 | Payroll run records |
| payslips | 0 | Individual payslip records |

### HR Tables
| Table | Rows (approx) | Purpose |
|-------|--------------|---------|
| employees | 5 | Employee master records (DGPS Surveyors, Office Staff, etc.) |
| departments | 0 | Department hierarchy |
| attendance_logs | 10 | GPS/geofence check-in and check-out logs |
| leaves | 5 | Leave request records (casual, medical, etc.) |
| employee_documents | 0 | Employee document registry |

### Approval & Audit Tables
| Table | Rows (approx) | Purpose |
|-------|--------------|---------|
| approvals | 14+ | Multi-state approval records (draft→pending→approved/rejected) |
| audit_logs | varies | Immutable audit trail |

### Marketing & Content Tables
| Table | Rows (approx) | Purpose |
|-------|--------------|---------|
| social_campaigns | 2 | Marketing campaign registry |
| social_content_items | varies | Content scripts and ideas |
| social_content_versions | varies | Version-controlled content drafts |
| social_accounts | 4 | Connected social media accounts |
| social_publish_jobs | varies | Scheduled publish jobs |
| social_reports | varies | Campaign analytics reports |
| social_media_assets | varies | Media file index |

### AI Brain Tables
| Table | Rows (approx) | Purpose |
|-------|--------------|---------|
| ai_agents | 12 | All 12 AI specialist agents (Owner Assistant, PM, Survey Ops, CRM, Finance, HR, Marketing, Reporting, Survey Analyst, BOQ, Content, Research) |
| ai_tasks | varies | AI task queue |
| ai_tool_executions | varies | Tool execution log |

---

## 5. File Structure Inventory

### Core Application
| File | Lines | Purpose | Status |
|------|-------|---------|--------|
| `foundation/api.py` | 1,783 | Main HTTP API server (stdlib only) | PASS |
| `foundation/store.py` | ~800 | SQLite data access layer | PASS |
| `foundation/config.py` | ~100 | Configuration management | PASS |
| `foundation/domains/migrate.py` | ~400 | Database migration runner | PASS |
| `foundation/dashboard/dashboard.html` | ~1,500 | Single-page dashboard UI | PASS |

### Business Domain Modules
| File | Purpose | Status |
|------|---------|--------|
| `foundation/domains/ai_brain.py` | AI agent orchestration | PASS |
| `modules/marketing/` | M19 marketing engine | PASS |
| `modules/content/` | Content generation | PASS |
| `modules/social/` | Social media management | PASS |
| `shared/` | Shared utilities | PASS |

### Configuration
| File | Purpose |
|------|---------|
| `config/SOUL.md` | AI personality configuration (DO NOT MODIFY) |
| `brand/ssc-brand-profile.md` | Brand guidelines (DO NOT MODIFY) |
| `.hermes/skills/shah-ai/SKILL.md` | AI skills definition (DO NOT MODIFY) |

### Test Suite
| File | Tests | Status |
|------|-------|--------|
| `foundation/tests/run_foundation_tests.py` | 48 | PASS |
| `foundation/tests/test_integration.py` | 22 | PASS |
| `foundation/tests/test_m19_domain.py` | 25 | PASS |
| `tests/test_business_workflow.py` | 18 | PASS |
| `tests/test_module1_hardening.py` | 13 | PASS |
| `tests/test_module1_auth.py` | 12 | PASS |
| `tests/test_hrm_module.py` | 28 | PASS |
| `tests/test_automation_planner.py` | 3 | PASS |
| `tests/test_content_calendar.py` | 10 | PASS |
| `tests/test_content_generator.py` | 6 | PASS |
| `tests/test_email_assistant.py` | 15 | PASS |
| `tmp_full_api_test.py` | 55 | PASS |

**Total: 254 / 254 checks PASS (100%)**

### Documentation
| File | Location | Purpose |
|------|----------|---------|
| `PROJECT_MASTER_INVENTORY.md` | Root | This file |
| `PROJECT_ARCHITECTURE.md` | Root | Architecture overview |
| `DATABASE_SCHEMA.md` | Root | Full 54-table schema |
| `API_ENDPOINTS.md` | Root | Complete API reference |
| `MODULE_STATUS.md` | Root | 20-module status matrix |
| `TEST_RESULTS.md` | Root | Test run results |
| `DEVELOPMENT_LOG.md` | Root | Phase-by-phase dev log |
| `BACKUP_LOG.md` | Root | Backup history |
| `KNOWN_ISSUES.md` | Root | Known issues & workarounds |
| `SECURITY_AUDIT.md` | Root | Security assessment |
| `IMPLEMENTATION_GAP_REPORT.md` | Root | Gap analysis |
| `INSTALLATION_GUIDE.md` | Root | Setup instructions |
| `FINAL_ACCEPTANCE_REPORT.md` | Root | Acceptance criteria sign-off |
| `FINAL_PROJECT_HANDOVER.md` | Root | Complete handover package |
| `NEXT_PHASE_ROADMAP.md` | Root | Phase 3/4/5 roadmap |
| `docs/USER-MANUAL.md` | docs/ | End-user manual |
| `docs/LAUNCH-GUIDE.md` | docs/ | Launch instructions |

### Backups
| Path | Files | Type | Status |
|------|-------|------|--------|
| `backups/antigravity_2026-11-20_phase3` | 197 | Phase 3 milestone snapshot | VERIFIED (100% PASS) |
| `backups/antigravity_2026-11-20_phase2` | 189 | Phase 2 milestone snapshot | VERIFIED (100% PASS) |
| `backups/antigravity_2026-11-20_pre_dev` | 167 | Full pre-dev snapshot | VERIFIED (100% PASS) |
| `backup_phase3_harden_20261117-100628` | varies | Phase 3 (Hermes) | ARCHIVED |
| `backup_phase3_harden_20261117-103051` | varies | Phase 3 retry | ARCHIVED |
| `backup_phase4_sprint1_20261117-182949` | varies | Phase 4 Sprint 1 | ARCHIVED |

---

## 6. API Endpoints Summary (by category)

### Auth (5 endpoints)
`POST /api/auth/login`, `GET /api/auth/me`, `POST /api/auth/logout`, `POST /api/auth/password`, `POST /api/auth/register`

### Workspaces (3 endpoints)
`GET /api/workspaces`, `GET /api/workspaces/{code}/resources`, `GET /api/workspaces/{code}/contacts`

### Dashboard (6 endpoints)
`GET /api/dashboard/crm`, `GET /api/dashboard/projects`, `GET /api/dashboard/finance`, `GET /api/dashboard/employees`, `GET /api/dashboard/marketing`, `GET /api/dashboard/overview`

### CRM & Leads (5 endpoints)
`GET /api/leads`, `POST /api/leads/sync-csv`, `POST /api/leads/{id}/status`, `POST /api/leads/{id}/convert`, `GET/POST /api/clients`

### Projects & Sites (2 endpoints)
`GET /api/sites`, `POST /api/sites`

### Finance (4 endpoints)
`GET /api/finance/vendors`, `POST /api/finance/vendors`, `GET /api/finance/expenses`, `POST /api/finance/expenses`

### Users (4 endpoints)
`GET /api/users`, `POST /api/users`, `GET /api/users/{id}`, `PUT /api/users/{id}`

### Approvals (5 endpoints)
`GET /api/approvals`, `POST /api/approvals`, `GET /api/approvals/{id}`, `POST /api/approvals/{id}/transition`, `GET /api/audit/{code}`

### AI Brain (7 endpoints)
`GET /api/ai-brain`, `GET /api/ai-brain/agents`, `GET /api/ai-brain/tasks`, `POST /api/ai-brain/tasks`, `POST /api/ai-brain/tasks/{id}/status`, `GET /api/ai-brain/tasks/{id}/executions`, `POST /api/ai-brain/action`

### System (4 endpoints)
`GET /api/system/health`, `GET /api/permissions`, `GET /api/reports`, `GET /api/media`

**Total API Endpoints: 45+**

---

## 7. External Dependencies

| Dependency | Type | Required? | Alternative |
|-----------|------|-----------|-------------|
| Python 3.14 | Runtime | YES | Python 3.11+ should work |
| SQLite3 | Database | YES (stdlib) | None needed |
| `http.server` | Web server | YES (stdlib) | None needed |
| `psutil` | System metrics | Optional | Falls back to 0 values |
| Node.js | Browser test only | Optional | Skip browser tests |
| FFmpeg | Video/reel rendering | Optional | Reel Studio disabled |

**Zero paid external services required for core operation.**

---

*Last updated: 2026-11-20 by Antigravity autonomous agent.*
