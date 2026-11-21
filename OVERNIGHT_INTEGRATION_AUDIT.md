# SHAH GROUP AI OS — OVERNIGHT INTEGRATION AUDIT

**Audit Date:** 2026-11-22  
**Auditor:** Lead Systems Architect & Integration Engineer  
**System URL:** `http://127.0.0.1:8899/`  
**Database:** `data/sgcc_foundation.sqlite` (Table: `drive_folders`, `sheets_module_mappings`, `social_accounts`)  
**Cost Enforcement:** 100% Free Tier &bull; Zero Paid Cloud Billing &bull; Zero Paid External APIs  

---

## 1. Executive Summary

The Central Integration & Data Sync Center of SHAH Group AI OS provides unified connectivity across Google Cloud services (Drive, Sheets), official social media publishing channels (Instagram, Facebook, YouTube, LinkedIn), and AI reasoning engines (Hermes Agent CLI).

All local staging, directory structures, database models, synchronization queues, and schema mappings are **100% operational**. Cloud-facing endpoints are protected by an honest OAuth credential boundary: they run in local zero-cost staging mode by default, and allow the business owner to attach live Google Workspace and Meta Developer App credentials without modifying source code.

---

## 2. Integration Status Dashboard

| Integration Service | Target Workspace | Local Staging Status | Cloud API Status | Database Records | Configuration Location |
|---|---|:---:|:---:|:---:|---|
| **Google Drive Staging** | SSC (10) &bull; INFRA (5) | **ACTIVE** | Ready for OAuth | 15 Folders in `drive_folders` | `data/drive_sync/` |
| **Google Sheets 12-Module** | SSC (12) &bull; INFRA (12) | **ACTIVE** | Ready for OAuth | 24 Mappings in `sheets_module_mappings` | `data/sheets_sync/` |
| **Instagram Graph API** | SSC & INFRA | **ACTIVE** | Setup Required | 6 Accounts in `social_accounts` | Settings / Integrations |
| **Facebook Pages API** | SSC & INFRA | **ACTIVE** | Setup Required | 6 Accounts in `social_accounts` | Settings / Integrations |
| **YouTube Studio API** | SSC & INFRA | **ACTIVE** | Setup Required | 5 Channels in `social_accounts` | Settings / Integrations |
| **LinkedIn Pages API** | SSC & INFRA | **ACTIVE** | Setup Required | 6 Accounts in `social_accounts` | Settings / Integrations |
| **Hermes AI Agent** | System-wide | **ACTIVE** | Free Tier (Nous) | Local CLI v0.23.1 | `vendor/hermes-agent/` |

---

## 3. Google Drive Hierarchical Folder Architecture

A 15-folder two-tier hierarchy is established in SQLite and staged on the local disk at `data/drive_sync/`.

### 3.1 SSC (Shah Survey Consultancy) Folders (10 Folders)
1. `SHAH GROUP AI OS / SSC / 01_CRM_Leads` — Lead inquiry captures, WhatsApp transcripts, tender notices.
2. `SHAH GROUP AI OS / SSC / 02_Clients` — Client master dossiers, KYC documents, GST certificates.
3. `SHAH GROUP AI OS / SSC / 03_Projects` — Project charter documents, work orders, site survey scopes.
4. `SHAH GROUP AI OS / SSC / 04_Quotations` — Formal stamped quotations, rate estimates, BOQs.
5. `SHAH GROUP AI OS / SSC / 05_Invoices` — GST Tax Invoices (Rule 46 compliant), payment receipts.
6. `SHAH GROUP AI OS / SSC / 06_Survey_Raw_Data` — DGPS RINEX files, Total Station SDR files, drone logs.
7. `SHAH GROUP AI OS / SSC / 07_Drawings_CAD_GIS` — AutoCAD DWG/DXF drawings, Shapefiles, GeoTIFF orthomosaics.
8. `SHAH GROUP AI OS / SSC / 08_Reports_Deliverables` — Final contour maps, alignment reports, volumetric summaries.
9. `SHAH GROUP AI OS / SSC / 09_HR_Payroll` — Monthly payslips, attendance registers, employee KYC.
10. `SHAH GROUP AI OS / SSC / 10_Marketing_Studio` — Canva graphics, exported reels, marketing collateral.

### 3.2 INFRA (Civil & Infrastructure) Folders (5 Folders)
1. `SHAH GROUP AI OS / INFRA / 01_Tenders_Estimates` — Tender bidding documents, NIT downloads, rate analysis.
2. `SHAH GROUP AI OS / INFRA / 02_Project_Sites` — Site inspection logs, soil test reports, DPRs.
3. `SHAH GROUP AI OS / INFRA / 03_Billing_Invoices` — Contractor RA bills, measurement book (MB) scans, GST invoices.
4. `SHAH GROUP AI OS / INFRA / 04_Vendors_Procurement` — Vendor purchase orders, cement/steel test certificates.
5. `SHAH GROUP AI OS / INFRA / 05_Site_Photos_Media` — Progress photos, drone flyover videos, milestone evidence.

---

## 4. Google Sheets 12-Module Enterprise Mapping

The system defines 24 active mappings in `sheets_module_mappings` (12 for SSC, 12 for INFRA) to allow bi-directional or export synchronization with corporate spreadsheets.

| Module Key | Module Name | Destination Spreadsheet | Default Worksheet | Sync Frequency |
|---|---|---|---|:---:|
| `crm` | CRM Leads & Enquiries | `SG_SSC_Master_Operations` | `Leads_Master` | Real-time on Create |
| `clients` | Client Master Directory | `SG_SSC_Master_Operations` | `Clients` | Daily / Manual |
| `projects` | Project Registry & Milestones | `SG_SSC_Master_Operations` | `Projects_Register` | On Status Change |
| `quotations` | Quotations & Estimates | `SG_SSC_Finance_Accounts` | `Quotations_Log` | On Generation |
| `invoices` | GST Tax Invoices | `SG_SSC_Finance_Accounts` | `GST_Invoices` | On Finalize / Record |
| `payments` | Payment Receipts & Ledger | `SG_SSC_Finance_Accounts` | `Payments_Ledger` | On Receipt |
| `expenses` | Expense Claims & Petties | `SG_SSC_Finance_Accounts` | `Expenses_Claims` | On Approval |
| `vendors` | Vendor Directory & Payables | `SG_SSC_Finance_Accounts` | `Vendors_Register` | Weekly |
| `payroll` | Monthly Salary & Payslips | `SG_SSC_HR_Payroll` | `Payroll_Register` | Monthly on Process |
| `employees` | Staff Directory & Skills | `SG_SSC_HR_Payroll` | `Employees` | On HR Update |
| `tasks` | Employee Tasks & Directives | `SG_SSC_Master_Operations` | `Tasks_Kanban` | Real-time |
| `inventory` | Survey Instruments & Assets | `SG_SSC_Master_Operations` | `Instruments_Assets` | Monthly Audit |

---

## 5. Social Media Integration Architecture

The platform supports multi-platform publishing across 4 networks:
1. **Instagram**: Supports Feed Posts (1080x1080, 1080x1350), Stories/Reels (1080x1920), and Reels Publishing via Meta Graph API v19.0.
2. **Facebook Pages**: Feed updates, albums, video publishing, and direct message webhooks.
3. **YouTube**: Video Shorts and long-form video upload via YouTube Data v3 API.
4. **LinkedIn**: Corporate page updates, hiring notices, and company announcements.

### Multi-Step Publishing Pipeline:
All posts pass through a controlled enterprise workflow:
$$\text{Draft} \longrightarrow \text{Pending Review} \longrightarrow \text{Approved (Owner/Manager)} \longrightarrow \text{Scheduled} \longrightarrow \text{Published}$$
No content can be published without explicit Owner or Manager approval.

---

## 6. Zero Paid API & Honest OAuth Boundary

### 6.1 Current Operational Mode
- Staging directory `data/drive_sync/` and `data/sheets_sync/` act as fully functional local file repositories.
- Exporting to CSV, TSV, or local JSON mirrors cloud formats with zero external dependencies.

### 6.2 Steps for the Business Owner to Enable Live Cloud Sync (When Desired)
1. Go to **Google Cloud Console** (`console.cloud.google.com`).
2. Create a project named `SHAH-GROUP-AI-OS` (Free Tier).
3. Enable `Google Drive API` and `Google Sheets API`.
4. Create an **OAuth 2.0 Client ID** (Desktop Application).
5. Open the **SHAH Group AI OS** dashboard, navigate to **Integrations &rarr; Settings**.
6. Paste the Client ID and Client Secret, then click **Authorize Google Account**.
7. The system will securely store the refresh token in `google_sheets_config` and activate live cloud streaming.

---

## 7. Audit Verdict: PASS

The integration subsystem is well-structured, adheres strictly to the zero paid API rule, maintains complete separation between SSC and INFRA corporate assets, and provides a clear transition path to live cloud synchronization.
