# SHAH GROUP AI OS — Tenant Isolation & IDOR Protection Audit Report

**Report Version:** 4.0.0  
**Audit Scope:** Complete Application Backend (`foundation/api.py`, `foundation/store.py`, `foundation/rbac.py`)  
**Verified Baseline:** Commit `9b84ce0`  
**Execution Environment:** Windows / Python 3.12+ / Port 8899  

---

## 1. Multi-Tenant Architecture Overview

SHAH GROUP AI OS operates an isolated multi-tenant architecture designed to manage distinct commercial entities under common executive ownership:
- **`SSC` Workspace:** Shah Surveyors & Consultancy (Geospatial consulting, DGPS RTK surveying, drone mapping, LiDAR analysis, bathymetric surveys).
- **`INFRA` Workspace:** Shah Infra Developers (Highway contracting, civil earthworks, MoRTH compliance, heavy equipment logistics).
- **`OTHER` Workspace:** Reference workspace (Training, testing, cross-firm documentation).

### Tenant Isolation Core Principles:
1. **Zero Data Leakage:** Non-Owner roles (`Manager`, `Project Manager`, `Finance Manager`, `HR Manager`, `Employee`, `Viewer`) can strictly and exclusively access data belonging to their assigned workspace.
2. **Owner Super-User Scope:** The `Owner` role holds global visibility and governance across all workspaces simultaneously (`*` permission).
3. **Defense-in-Depth IDOR Guards:** Direct object queries (`GET /api/sites/{id}`, `GET /api/tasks/{id}`, `GET /api/invoices/{id}`, `GET /api/payroll/payslips/{id}`, `GET /api/media/download/{id}`) enforce strict tenant ownership checks on the underlying record rather than trusting client-supplied parameters.

---

## 2. IDOR Vulnerability Audit & Remediation Matrix

During Phase 4 security hardening, every endpoint in `foundation/api.py` was audited against Insecure Direct Object Reference (IDOR) attacks:

| Endpoint & Method | Potential IDOR Attack Vector | Pre-Hardened State | Hardened Remediation | Audit Result |
| :--- | :--- | :--- | :--- | :--- |
| `GET /api/payroll/payslips/{id}` | INFRA user queries SSC staff salary payslips by enumerating sequential ID. | Fetched `payslips WHERE id=?` directly without workspace join. | Joined `payroll_runs` and verified `pr.workspace_id == user.workspace_id`. Rejects unauthorized cross-tenant requests with **403 Forbidden**. | **SECURED / VERIFIED** |
| `GET /api/tasks/{id}` | SSC Employee views sensitive INFRA heavy contracting work details. | Fetched task by primary key only. | Added explicit validation: `if user.role != 'Owner' and task.workspace_id != ws: raise 403`. | **SECURED / VERIFIED** |
| `GET /api/invoices/{id}` | INFRA staff views commercial pricing, tax, and GST details of SSC client invoices. | Fetched invoice by ID without tenant validation. | Added tenant verification check against `invoice.workspace_id`. Rejects with **403 Forbidden**. | **SECURED / VERIFIED** |
| `POST /api/invoices/{id}/payment` | Non-owner records payments against another workspace's invoice. | Accepted `invoice_id` in body and updated payment. | Verified invoice exists and matches user's workspace before recording payment. | **SECURED / VERIFIED** |
| `GET /api/quotations/{id}` | Competitor analysis by staff viewing quotes across separate business divisions. | Returned quotation directly by ID. | Added tenant check on `quotation.workspace_id`. Rejects with **403 Forbidden**. | **SECURED / VERIFIED** |
| `GET /api/estimates/{id}` | Cross-viewing project cost scopes and estimates. | Fetched estimate without workspace verification. | Verified `estimate.workspace_id == ws`. Rejects with **403 Forbidden**. | **SECURED / VERIFIED** |
| `GET /api/media/download/{id}` | Unauthorized download of client orthophotos or proprietary drone media by ID. | Streamed media file if ID existed on disk. | Verified `asset.workspace_id == ws` before opening file stream. Rejects with **403 Forbidden**. | **SECURED / VERIFIED** |
| `GET /api/reports/{id}` & `ai_generated_reports/{id}` | Reading executive business intelligence reports across divisions. | Returned report by primary key. | Verified `report.workspace_id == ws`. Rejects with **403 Forbidden**. | **SECURED / VERIFIED** |
| `POST /api/sites` | Non-owner attempts to inject project sites into foreign workspace via body JSON. | Accepted `workspace_id` from body JSON if provided. | Checked `if user.role != 'Owner' and target_ws != ws: return 403`. | **SECURED / VERIFIED** |

---

## 3. Real-World Penetration Test Evidence

The automated acceptance test suite (`scripts/run_phase4_acceptance.py`) executed cross-tenant penetration tests:

### Test Case 1: Cross-Workspace Sites Penetration
* **Actor:** User `pm` (Role: `Project Manager`, Assigned Workspace: `INFRA`).
* **Target Request:** `GET /api/sites?workspace=SSC`
* **Response:** `HTTP 403 Forbidden`
* **Server Response Payload:**
  ```json
  {
    "error": "Tenant isolation: role 'Project Manager' assigned to 'INFRA' cannot access 'SSC'"
  }
  ```
* **Verdict:** **PASSED / BLOCKED**

### Test Case 2: Cross-Workspace Tasks Penetration
* **Actor:** User `employee` (Role: `Employee`, Assigned Workspace: `SSC`).
* **Target Request:** `GET /api/tasks?workspace=INFRA`
* **Response:** `HTTP 403 Forbidden`
* **Server Response Payload:**
  ```json
  {
    "error": "Tenant isolation: role 'Employee' assigned to 'SSC' cannot access 'INFRA'"
  }
  ```
* **Verdict:** **PASSED / BLOCKED**

### Test Case 3: IDOR Direct Payslip Access
* **Actor:** User `pm` (Role: `Project Manager`, Assigned Workspace: `INFRA`).
* **Target Request:** `GET /api/payroll/payslips/1` (Belongs to SSC employee)
* **Response:** `HTTP 403 Forbidden`
* **Verdict:** **PASSED / BLOCKED**

### Test Case 4: Owner Super-User Access
* **Actor:** User `owner` (Role: `Owner`, Assigned Workspace: `SSC`).
* **Target Requests:** `GET /api/sites?workspace=SSC` AND `GET /api/sites?workspace=INFRA`
* **Responses:** `HTTP 200 OK` for both workspaces.
* **Verdict:** **PASSED / AUTHORIZED**

---

## 4. Architectural Summary

Tenant isolation in SHAH GROUP AI OS is now enforced at both the route perimeter (`_get_request_workspace`) and the object persistence layer. No user without the explicit `Owner` role can observe, query, modify, or download assets belonging to an isolated workspace.
