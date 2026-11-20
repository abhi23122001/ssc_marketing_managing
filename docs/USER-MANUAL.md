# SHAH GROUP AI OS — User Manual

## 1. What it is

A local, stdlib-only foundation platform for Shah Surveyors & Consultancy (SSC)
with multi-role access control, business-data isolation across workspaces
(SSC/INFRA/OTHER), an approval workflow, and audit logging.

## 2. Roles

| Role | Approver | Workspace access |
|---|---|---|
| Owner | Yes | All workspaces (consolidated) |
| Manager | Yes | Own workspace only |
| Project Manager | Yes | Own workspace only |
| Finance Manager | Yes | Own workspace only |
| HR Manager | No | Own workspace only |
| Employee | No | Own workspace only |
| Viewer | No | Own workspace only |

## 3. Starting the system

    cd /c/Users/HP/Desktop/ssc_marketing_managing
    python3 foundation/api.py

Serves on `127.0.0.1:8899`.

## 4. Logging in

POST `/api/auth/login` with `{"username":"owner","password":"demo-owner-pass-0001"}`.
Response: `{token, user, workspace}`.

Demo credentials (local development only):

- Owner — `owner` / `demo-owner-pass-0001`
- Manager — `manager` / `demo-manager-pass-0001`
- Project Manager — `pm` / `demo-pm-pass-0001`
- Finance Manager — `finance` / `demo-finance-pass-0001`
- HR Manager — `hr` / `demo-hr-pass-0001`
- Employee — `employee` / `demo-employee-pass-0001`
- Viewer — `viewer` / `demo-viewer-pass-0001`

## 5. Using the workspaces

Each user sees only their own workspace's records, except the Owner who reads
across SSC, INFRA and OTHER.

- `GET /api/workspaces/{code}/resources`

## 6. Approvals

- Owner/Manager/Finance Manager/Project Manager may create and approve approvals.
- Viewer/Employee/HR Manager/others cannot approve (`403`).

## 7. Audit

- `GET /api/audit/{code}` — workspace-scoped audit feed.

## 8. Dashboard

- `GET /` — owner dashboard (static HTML shell).

## 9. Data isolation rules

- A user may touch records only in their own workspace (Owner consolidated).
- All business-data queries are workspace-scoped at the store layer.
- Isolation enforcement is audited; an Owner consolidation access is logged.

## 10. Security notes

- Passwords are hashed with PBKDF2-SHA256 (100,000 iterations, per-user salt).
- Session tokens are `secrets.token_urlsafe(32)`; expired sessions are rejected.
- No network access; this is a local-only system.
- Demo users are local-development placeholders, not production accounts.
