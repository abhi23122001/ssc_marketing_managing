# SHAH GROUP AI OS — Launch Guide

**Date:** 2026-11-19
**Project root:** C:/Users/HP/Desktop/ssc_marketing_managing
**Python:** 3.14.9 (stdlib only)
**Server:** 127.0.0.1:8899 (running)

---

## 1. What This Is

The SHAH Group AI OS is a locally-hosted business operating system for
**Shah Surveyors & Consultancy (SSC)** and the **SHAH INFRA DEVELOPERS**
workspace, with an **OTHER** workspace for reference. It provides:

- Foundation API (auth, RBAC, approvals, audit, workspaces)
- M19 business modules (communication, content, media, workflow, AI brain)
- Integrated domains (employees, attendance, expense, payroll)
- Marketing/AI module skeletons (content, media, publishing, analytics, email)

---

## 2. Prerequisites

- Python 3.14+ (Python 3.14.9 confirmed; stdlib only — no pip installs required)
- SQLite 3 (bundled with Python)
- 127.0.0.1 or localhost (no network exposure)
- ffmpeg (optional — for media rendering; required only for the M19 media pipeline)

---

## 3. Starting the Application

### 3.1 Start the API server

```bash
cd /c/Users/HP/Desktop/ssc_marketing_managing
python3 foundation/api.py
```

The server will listen on `127.0.0.1:8899` (configurable in
`foundation/config.py` via `host` and `port`).

### 3.2 Open the dashboard

`http://127.0.0.1:8899/`

### 3.3 Log in

| Role | Username | Password |
|---|---|---|
| Owner | owner | demo-owner-pass-0001 |
| Manager | manager | demo-manager-pass-0001 |
| Finance Manager | finance | demo-finance-pass-0001 |
| HR Manager | hr | demo-hr-pass-0001 |
| Project Manager | pm | demo-pm-pass-0001 |
| Employee | employee | demo-employee-pass-0001 |
| Viewer | viewer | demo-viewer-pass-0001 |

⚠️ Demo passwords are **local-development placeholders only**. Rotate before
any internal or client-facing use (see `foundation/config.py` `demo_users`).

---

## 4. Verifying the Installation (Quick Checklist)

### 4.1 Server
- [ ] `GET http://127.0.0.1:8899/health` returns `{"ok": true, ...}`

### 4.2 Dashboard
- [ ] `GET http://127.0.0.1:8899/` returns 200 with HTML

### 4.3 API
- [ ] `GET http://127.0.0.1:8899/api/workspaces` returns 200
- [ ] `GET http://127.0.0.1:8899/api/audit/SSC` returns 200
- [ ] `GET http://127.0.0.1:8899/api/auth/me` returns 200

### 4.4 Auth
- [ ] `POST http://127.0.0.1:8899/api/auth/login` with `{"username":"owner","password":"demo-owner-pass-0001"}` returns a token
- [ ] Unauthenticated POST requests return 401

### 4.5 Tests
- [ ] `python3 foundation/tests/run_foundation_tests.py` → 42/42 PASS
- [ ] `python3 foundation/tests/test_integration.py` → 22/22 PASS
- [ ] `python3 foundation/tests/test_m19_domain.py` → 25/25 PASS

---

## 5. Running the Test Suites

```bash
# 1. Foundation battery
python3 foundation/tests/run_foundation_tests.py

# 2. Integration suite
python3 foundation/tests/test_integration.py

# 3. M19 domain suite
python3 foundation/tests/test_m19_domain.py

# 4. In-process regression (existing module tests)
python3 -m pytest tests/ -v
```

All suites are stdlib-only and can run without any pip installs.

---

## 6. Common Operations

### 5.1 Create an approval (SOA workflow)
```bash
# 1. Get an auth token from /api/auth/login
# 2. POST /api/approvals with:
{
  "title": "My approval",
  "resource_key": "workspace-sites",
  "description": "Optional description"
}
```
Requires an `Owner`/`Manager`-seated token.

### 5.2 Transition an approval
```bash
# POST /api/approvals/{id}/transition
{
  "status": "approved",
  "note": "Approved by owner"
}
```
Requires `Owner`/`Manager`/`Finance Manager`/`Project Manager` role.

### 5.3 View audit feed
```bash
# GET /api/audit/SSC
```

### 5.4 View dashboard overview
```bash
# GET /api/dashboard/overview
```

---

## 7. Data & Backups

### 7.1 Database
- **Path:** `data/sgcc_foundation.sqlite` (SQLite + WAL)
- Existing tables: `approvals`, `audit_logs`, `resources`, `roles`,
  `sessions`, `users`, `workspaces`
- Missing tables (open items): `social_content_items`, `social_media_assets`,
  `social_accounts`, `social_leads`, `ai_agents`

### 7.2 Preserved backups
- `backup_phase4_sprint1_20261117-182949/`
- `backup_phase3_harden_20261117-100628/`
- Other `backup_phase3_harden_*` directories

All backups are preserved. No protected files were changed; no CRM data was
touched during this session.

---

## 8. Remaining Work

### 8.1 Blocked by external credentials
- Instagram/Facebook/LinkedIn/YouTube publishing (OAuth credentials required)
- Live FFmpeg render with real footage

### 8.2 Open items (tracked)
- Domain-table initialization (safe idempotent migrations recommended)
- Marketing module UI routes (backend verified; tables missing)
- `POST /api/publish` route mismatch
- `POST /api/content` string-formatting bug

### 8.3 Not implemented
- Production-native Android/iOS apps
- Real external platform API publishing

---

## 9. Logout

```bash
# POST /api/auth/logout
```
Returns `{"ok": true}`.
