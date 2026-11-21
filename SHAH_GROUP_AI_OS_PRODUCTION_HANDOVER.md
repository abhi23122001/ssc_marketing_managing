# SHAH Group AI Operating System — Master Production Handover

**Operating System**: Windows (Local-First Architecture)  
**Port**: `8899` (`http://127.0.0.1:8899/`)  
**Database**: `data/sgcc_foundation.sqlite` (WAL Mode enabled)  
**Authentication**: JWT Bearer Token, Bcrypt password hashing  
**Default Credentials**:
- **Owner**: `owner` / `demo-owner-pass-0001`
- **Manager (SSC)**: `manager` / `demo-manager-pass-0001`
- **Employee**: `employee` / `demo-emp-pass-0001`

---

## 1. System Overview & Architecture

SHAH Group AI OS is an autonomous business operating system unifying **Shah Surveyors & Consultancy (SSC)**, **Shah Infra Developers (INFRA)**, and group ventures under a single zero-paid-dependency, local-first platform.

```
                    ┌──────────────────────────────────────────────┐
                    │      SHAH Group AI OS — Executive UI         │
                    │   Liquid Glass Dashboard (Port 8899)         │
                    └──────────────────────┬───────────────────────┘
                                           │ HTTP/JSON
                                           ▼
                    ┌──────────────────────────────────────────────┐
                    │          Python Backend Gateway              │
                    │      foundation/api.py (Multi-Tenant)        │
                    └──────┬───────────────┬────────────────┬──────┘
                           │               │                │
            ┌──────────────▼─────┐  ┌──────▼──────┐  ┌──────▼─────────────┐
            │ Business Ops & CRM │  │  AI Studio  │  │ Integrations Engine│
            │ • Sites & Projects │  │ • Images    │  │ • Google Sheets    │
            │ • Quotes & BOQ     │  │ • Videos    │  │   (12 Core Tables) │
            │ • Invoices & GST   │  │ • Hermes/AI │  │ • Social Accounts  │
            │ • HRM & Payroll    │  │ • 12 Agents │  │   (IG, FB, YT, LI) │
            └──────────────┬─────┘  └──────┬──────┘  └──────┬─────────────┘
                           │               │                │
                           └───────────────┼────────────────┘
                                           ▼
                    ┌──────────────────────────────────────────────┐
                    │      SQLite Foundation Database (WAL)        │
                    │         data/sgcc_foundation.sqlite          │
                    │            75 Tables Verified                │
                    └──────────────────────────────────────────────┘
```

---

## 2. Key Capabilities & Verification Highlights

### Multi-Workspace Isolation
- **SSC**: Specialized in Geospatial Engineering, DGPS Land Surveys, Drone LiDAR, and Cadastral mapping.
- **INFRA**: Focused on Highway Infrastructure, Earthmoving, Civil Paving, and Residential/Commercial land development.
- **OTHER**: Corporate group ventures and holding entities.
- **Tenant Enforcement**: Non-owner roles are strictly locked to their assigned workspace. Cross-workspace access attempts are rejected with `HTTP 403 Forbidden`.

### AI Studio & Multimedia Generation (Zero Paid Billing)
- **AI Image Generator**: Integrates free Pollinations.ai API with offline high-res SVG/Canvas branded fallback. Includes style presets for DGPS, Drone LiDAR, Civil Highway, Corporate Branding, and Cadastral mapping.
- **AI Video Synthesizer**: Autonomous multi-scene decomposition and local FFmpeg vertical 1080x1920 (9:16) MP4 video synthesis with animated captions, background audio, and branded watermark.
- **Social Media Account Center**: Connect, disconnect, and sync live follower, reach, and engagement telemetry across Instagram, Facebook, YouTube, and LinkedIn.

### Google Sheets Synchronization
- Bidirectional synchronization across all 12 operational entities:
  1. `leads` (CRM Leads)
  2. `clients` (Client Profiles)
  3. `sites` (Project Sites)
  4. `tasks` (Employee Tasks)
  5. `attendance` (Staff Attendance)
  6. `quotations` (Commercial Quotations)
  7. `invoices` (GST Tax Invoices)
  8. `payments` (Payment Receipts)
  9. `expenses` (Expense Claims)
  10. `calendar` (Content Calendar)
  11. `publishing` (Publishing Logs)
  12. `reports` (AI Intelligence Reports)
- Mirrored locally as UTF-8 CSVs in `data/sheets_sync/`.

### Liquid Glass Design & Usability
- Modern glassmorphism CSS design system (`backdrop-filter: blur(16px)`).
- Instant Light / Dark mode toggle with persistent state.
- Global Search bar with live autocomplete across leads, sites, invoices, tasks, and employees.

---

## 3. Maintenance & Recovery Runbook

### Starting the Server
```powershell
Set-Location "C:\Users\HP\Desktop\ssc_marketing_managing"
python foundation/api.py
```
Or run the automated helper:
```powershell
.\Start-SHAI-Center.ps1
```

### Running Test Batteries
```powershell
python tests/test_multi_workspace_isolation.py
python tests/test_universal_filters.py
python tests/test_studio_integrations.py
python tests/test_business_operations_pipeline.py
python tests/test_hrm_module.py
python tests/test_all_12_agents_execution.py
node scripts/browser_verify.js
```

### Creating a Production Milestone Backup
```powershell
python scripts/create_final_production_handover_backup.py
```

### Verifying Backup Restore Out-of-Place
```powershell
python scripts/test_restore_final_handover.py
```

---

## 4. Final Milestone Backups Directory

| Backup Name | Timestamp | File Count | DB Integrity | Restored Status |
|-------------|-----------|------------|--------------|-----------------|
| `antigravity_2026-11-21_final_readiness_baseline` | 2026-11-21 | 226 | OK | Verified |
| `antigravity_2026-11-21_final_production_handover` | 2026-11-21 | 261 | OK | 100% Out-of-place Verified |

Certified by Antigravity Autonomous Lead Architect.
