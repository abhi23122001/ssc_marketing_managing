# SHAH Group AI OS — Project Architecture

## 1. Overview
SHAH Group AI OS is an integrated Business Operating System designed specifically for:
1. **Shah Surveyors & Consultancy (SSC)**: Land surveying, DGPS, RTK, topographical, drone, LiDAR, GPR, alignment, FLS, and DPR documentation.
2. **Shah Infra Developers (INFRA)**: Civil infrastructure, road/railway works, solar EPC, geotechnical borings, contractor management, and project billing.
3. Additional workspaces (e.g., `OTHER`, client agencies).

The system enforces strict multi-workspace data isolation while giving executive cross-workspace visibility to the `Owner` role.

---

## 2. Directory Structure

```text
ssc_marketing_managing/
├── foundation/                     # Core Business OS foundation engine
│   ├── api.py                      # Multi-threaded HTTP REST API & static server (port 8899)
│   ├── store.py                    # Unified SQLite Store & query interface
│   ├── auth.py                     # PBKDF2 authentication & session token management
│   ├── rbac.py                     # Role-based access control (7 roles x granular permissions)
│   ├── isolation.py                # Multi-workspace tenant data isolation
│   ├── approval.py                 # Multi-stage approval state machine
│   ├── audit.py                    # Tamper-evident audit logging engine
│   ├── config.py                   # Runtime configuration & demo seed users
│   ├── domains/                    # Domain-specific business logic & schemas
│   │   ├── m19_schema.py           # SQLite tables for marketing, content, CRM, media
│   │   ├── m19_core.py             # Content, leads, social, campaign logic
│   │   ├── m19_media.py            # FFmpeg & asset processing engine
│   │   ├── m19_workflow.py         # Publishing & approval workflow
│   │   └── migrate.py              # Domain migrations
│   ├── dashboard/                  # Single Page Application frontend
│   │   └── dashboard.html          # Unified dark-mode reactive dashboard
│   └── tests/                      # Core automated test batteries
│       ├── run_foundation_tests.py # 45-point foundation test runner
│       ├── test_integration.py     # 22 cross-workspace integration tests
│       └── test_m19_domain.py      # 25 domain logic unit tests
├── modules/                        # Business operating modules (01 to 14)
│   ├── 01-marketing-command-center/
│   ├── 02-daily-content-planner/
│   ├── 03-instagram-facebook-content-studio/
│   ├── 04-linkedin-b2b-marketing/
│   ├── 05-google-business-profile-management/
│   ├── 06-contractor-lead-research-crm/
│   ├── 07-seo-keyword-research/
│   ├── 08-ai-image-video-workflow/
│   ├── 09-content-approval-publishing-workflow/
│   ├── 10-analytics-monthly-reporting/
│   ├── 11-marketing-command-center/
│   ├── 12-content-calendar-content-generation/
│   ├── 13-contractor-lead-intelligence/
│   └── 14-email-assistant/
├── data/                           # Production persistent state
│   ├── sgcc_foundation.sqlite      # SQLite database (WAL mode)
│   ├── leads.csv                   # Historical contractor CRM leads
│   └── keywords.csv                # Targeted regional SEO keywords
├── scripts/                        # Utility & DevOps maintenance scripts
│   ├── create_pre_dev_backup.py    # Transactional online backup generator
│   └── verify_pre_dev_backup.py    # Isolated restore testing utility
├── backups/                        # Verified point-in-time recovery archives
│   └── antigravity_2026-11-20_pre_dev/
└── tests/                          # Additional test suites
```

---

## 3. Technology Stack & Runtime
- **Backend**: Python 3.14.9 / 3.15.2 using standard library (`http.server.ThreadingHTTPServer`, `sqlite3`, `hashlib`, `json`).
- **Database**: SQLite 3 with Write-Ahead Logging (`PRAGMA journal_mode=WAL`).
- **Frontend**: Vanilla HTML5, CSS3 Custom Properties, and ES6+ JavaScript async/await (No build step or bloated node_modules required).
- **Authentication**: Stateless bearer session tokens mapped to `sessions` table in SQLite; PBKDF2-SHA256 password hashing.
- **Port**: `8899` (binds to `127.0.0.1:8899`).

---

## 4. Security & Tenant Isolation
1. **Workspace Boundary**: Every business record is tagged with `workspace_id` (e.g., `SSC`, `INFRA`). Users assigned to `INFRA` cannot read or modify `SSC` data.
2. **Owner Super-user**: The `Owner` role retains cross-workspace oversight to monitor consolidated revenue, reports, and approvals.
3. **RBAC Engine**: 7 distinct system roles:
   - `Owner`: Full access (`*`)
   - `Manager`: Operational management in assigned workspace
   - `Project Manager`: Project execution, sites, and tasks
   - `Finance Manager`: Expense claims, invoices, and financial approvals
   - `HR Manager`: Employee records, attendance, and payroll runs
   - `Employee`: Check-in, task completion, profile view
   - `Viewer`: Read-only access to assigned workspace resources
