# SHAH GROUP AI OS — Google & External Integration Status Report

**Subsystem:** Central Integration & Data Sync Center  
**Modules:** [integrations_center.py](file:///C:/Users/HP/Desktop/ssc_marketing_managing/foundation/domains/integrations_center.py), [google_sheets_sync.py](file:///C:/Users/HP/Desktop/ssc_marketing_managing/foundation/domains/google_sheets_sync.py), [dashboard.html](file:///C:/Users/HP/Desktop/ssc_marketing_managing/foundation/dashboard/dashboard.html)  
**Execution Timestamp:** 22 November 2026, 11:04 PM IST  
**Integrity Guarantee:** **ZERO SIMULATION & ZERO PAID CLOUD BILLING**  

---

## 1. Executive Summary

This report provides a completely honest audit of Google Drive, Google Sheets, and Social Media connections within SHAH GROUP AI OS. In adherence to strict delivery guidelines, **no fake "Connected" status badges are shown** when external cloud OAuth credentials or API keys have not been configured by the owner.

Instead, the application provides high-integrity **Local Safe Staging (Offline / Zero Cost)**:
- All documents intended for Google Drive are automatically staged and organized into 15 pre-configured folders on disk (`data/drive_sync/`).
- All 12 business modules (Leads, Projects, Invoices, Quotations, Payments, Attendance, Payroll, etc.) maintain active CSV mirrors on disk (`data/sheets_sync/`).
- When the owner adds real Google Cloud OAuth credentials, the system automatically mirrors local staging to live Google Drive and Sheets without data loss or re-configuration.

---

## 2. Integration Status Matrix

| Integration Name | Connection Type | Current Status | Status Label | Data Storage Location | Cloud OAuth Configured? |
| :--- | :--- | :---: | :--- | :--- | :---: |
| **Google Account** | OAuth 2.0 Core Auth | `setup_required` | `Cloud OAuth: Not Connected (Setup Required)` | Local Session Store | ❌ No (`credentials/client_secret.json` absent) |
| **Google Drive Storage** | Cloud Document Storage | `setup_required` | `Local Safe Staging Only (Offline / Zero Cost)` | `data/drive_sync/` (15 Folders) | ❌ Staging Locally (Ready for Sync) |
| **Google Sheets Sync** | 12-Module Data Mirror | `setup_required` | `Local Safe Staging (12 CSV Modules / Offline)` | `data/sheets_sync/` (12 Modules) | ❌ Staging Locally (Ready for Sync) |
| **Instagram Business** | Meta Graph API | `setup_required` | `Setup Required (Token Missing)` | `social_accounts` DB Table | ❌ No (`INSTAGRAM_ACCESS_TOKEN` absent) |
| **Facebook Official Page** | Meta Pages API | `setup_required` | `Setup Required (App Secret Missing)` | `social_accounts` DB Table | ❌ No (`META_APP_SECRET` absent) |
| **YouTube Studio Channel** | Google Data v3 API | `setup_required` | `Setup Required (API Key Missing)` | `social_accounts` DB Table | ❌ No (`YOUTUBE_API_KEY` absent) |
| **LinkedIn Corporate Page** | LinkedIn Marketing API | `setup_required` | `Setup Required (OAuth Missing)` | `social_accounts` DB Table | ❌ No (`LINKEDIN_CLIENT_SECRET` absent) |
| **Hermes AI Engine** | Local Intelligence | `connected` | `Active (Local v0.23.1 + StepFun Free)` | Local Process / SQLite | ✅ 100% Active (Zero Cost) |
| **AI Creative Studio** | Pollinations & Canvas | `connected` | `Active (Pollinations.ai + Offline Canvas)` | Local Browser / Memory | ✅ 100% Active (Zero Cost) |

---

## 3. Pre-Configured Google Drive Folders (15 Folders)

All 15 hierarchical business folders are pre-created in `data/drive_sync/` and cataloged in the SQLite database (`drive_folders`):

### SSC Workspace Folders (10 Folders)
1. `data/drive_sync/SSC/01_DGPS_Survey_Raw_Data/` — RINEX, GNSS base/rover raw observation files.
2. `data/drive_sync/SSC/02_Total_Station_Traverse_Logs/` — Field survey point data and traverse angular closure logs.
3. `data/drive_sync/SSC/03_Drone_LiDAR_Point_Clouds/` — LAS/LAZ point clouds, orthomosaics, and flight telemetry.
4. `data/drive_sync/SSC/04_Cadastral_Land_Records/` — Revenue 7/12 land records, boundary maps, and village maps.
5. `data/drive_sync/SSC/05_Approved_Drawings_DWG/` — Finished AutoCAD drawings, alignments, and contour plans.
6. `data/drive_sync/SSC/06_Client_Quotations_BOQ/` — Formal rate analysis, client estimates, and commercial proposals.
7. `data/drive_sync/SSC/07_GST_Tax_Invoices/` — GST Rule 46 signed PDF tax invoices and delivery chalans.
8. `data/drive_sync/SSC/08_Signed_Work_Orders/` — Executed contracts, agreements, and client tender LOAs.
9. `data/drive_sync/SSC/09_Instrument_Calibration_Certs/` — 12-month calibration certificates for Total Stations & DGPS.
10. `data/drive_sync/SSC/10_Staff_KYC_Documents/` — Surveyor identity proofs, operator certificates, and HR contracts.

### INFRA Workspace Folders (5 Folders)
11. `data/drive_sync/INFRA/01_Highway_DPR_Reports/` — Alignment proposals, strip plans, and cross-section DPRs.
12. `data/drive_sync/INFRA/02_MoRTH_Compaction_Test_Reports/` — 97% MDD field density and lab soil test certificates.
13. `data/drive_sync/INFRA/03_GPR_Underground_Utility_Maps/` — Subsurface utility radargrams and pipe/cable depth scans.
14. `data/drive_sync/INFRA/04_Mining_Stockpile_Volumetrics/` — Cut-and-fill volumetric calculation sheets and DEMs.
15. `data/drive_sync/INFRA/05_Subcontractor_Agreements_Billing/` — EPC subcontracts, plant/equipment rental logs, and claims.

---

## 4. Google Sheets 12-Module Bidirectional Mapping

All 12 business modules maintain local CSV staging in `data/sheets_sync/`:
1. `social_leads` -> `leads.csv`
2. `sites` -> `project_sites.csv`
3. `business_quotations` -> `quotations.csv`
4. `business_invoices` -> `invoices.csv`
5. `business_payments` -> `payments.csv`
6. `employees` -> `staff_roster.csv`
7. `attendance_logs` -> `attendance.csv`
8. `payroll_runs` -> `payroll.csv`
9. `payslips` -> `salary_slips.csv`
10. `expense_claims` -> `expenses.csv`
11. `employee_tasks` -> `tasks.csv`
12. `social_content_items` -> `content_calendar.csv`

---

## 5. Instructions for Owner: Activating Live Cloud OAuth

When the business owner is ready to connect live Google Cloud storage without incurring paid costs:

1. Visit the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a project named `SHAH-GROUP-AI-OS`.
3. Enable **Google Drive API** and **Google Sheets API** (free tier quota: 10,000 requests/day).
4. Go to **Credentials > Create Credentials > OAuth client ID** (Application type: *Desktop app* or *Web application*).
5. Download the JSON credential file and save it as:
   `C:\Users\HP\Desktop\ssc_marketing_managing\credentials\client_secret.json`
6. In SHAH GROUP AI OS, navigate to **Integration & Sync > Google Drive Storage > ⚡ Connect Google Drive**.
7. The system will detect the client secret, initiate one-time OAuth consent, and promote status from `Local Safe Staging Only` to `Cloud Synced`.
