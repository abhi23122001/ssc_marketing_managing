# SHAH Group AI OS — Manual Testing Guide

This guide walks through manual verification of the SHAH Group AI OS via web browser and curl.

---

## 1. Startup & Access

### Step 1: Start Server
Open PowerShell in the project directory:
```powershell
cd C:\Users\HP\Desktop\ssc_marketing_managing
python foundation/api.py
```
Expected output:
```text
SHAI foundation API listening on http://127.0.0.1:8899
```

### Step 2: Open Dashboard
Open your browser and navigate to:
```text
http://127.0.0.1:8899/
```
The unified dark-themed dashboard loads immediately.

---

## 2. Authentication Testing

| Role | Username | Password | Expected Workspace Access |
|---|---|---|---|
| **Owner** | `owner` | `demo-owner-pass-0001` | Full cross-workspace access (`SSC`, `INFRA`, `OTHER`) |
| **Manager** | `manager` | `demo-manager-pass-0001` | `SSC` workspace management, approvals, team |
| **Employee** | `employee` | `demo-employee-pass-0001` | `SSC` check-in, task completion |
| **Viewer** | `viewer` | `demo-viewer-pass-0001` | `INFRA` read-only access (cannot create or edit) |
| **Finance Manager** | `finance` | `demo-finance-pass-0001` | `INFRA` expense claims & approvals |
| **Project Manager** | `pm` | `demo-pm-pass-0001` | `INFRA` projects & site operations |
| **HR Manager** | `hr` | `demo-hr-pass-0001` | `OTHER` employee records & attendance |

### Manual Verification Steps:
1. Log in as `owner`. Verify header displays `owner (Owner)`.
2. Navigate between tabs: **Overview**, **Workspaces**, **Projects**, **Finance**, **Employees**, **Marketing**, **CRM**, **Approvals**, **Settings**, **AI Brain**.
3. Under **Settings -> Roles & Users**:
   - Verify all users are rendered with username, role, workspace, status.
   - Click **+ Add user**. Enter new test user. Verify immediate appearance in the table.
   - Click **Edit** on a user. Update full name. Save and verify updated value.
   - Click **Deactivate**. Verify status pill changes to `inactive`.
   - Click **Activate**. Verify status pill returns to `active`.
4. Click **Logout**. Verify session token is cleared and user is prompted to log in.

---

## 3. Workspace Data Isolation Testing
1. Log in as `viewer` (assigned to `INFRA`).
2. Try viewing `SSC` resources.
3. Verify that `SSC` private records are blocked with HTTP 403.
4. Log back in as `owner`. Verify both `SSC` and `INFRA` records are accessible in consolidated views.
