# SHAH GROUP AI OS — AUTONOMOUS AI BRAIN & PROACTIVE OPERATIONS MANUAL

## 1. System Identity and Architectural Overview

The **SHAH GROUP AI BRAIN** is the central autonomous intelligence system powering:
1. **Shah Surveyors & Consultancy (SSC)** — Geospatial surveying, DGPS, RTK, Drone photogrammetry, Aerial LiDAR, GPR, and cadastral mapping.
2. **Shah Infra Developers (INFRA)** — Civil infrastructure, road works, earthwork grading, industrial parks, and MoRTH-compliant highway engineering.

Unlike generic LLM chatbots, the SHAH Group AI Brain is:
- **Local-First & Stdlib Python**: Runs completely locally with zero external API fees or required third-party services.
- **Strictly Grounded (No Hallucinations)**: Answers software and how-to questions strictly from verified system documentation; answers business figures exclusively from live, authorized SQLite database tables (`business_invoices`, `business_payments`, `expense_claims`, `attendance_logs`, `social_leads`).
- **Autonomous & Scheduled**: Runs proactively on a background daemon scheduler without waiting for owner prompts or requiring an active browser window.
- **Timezone-Aware**: All operations, marketing schedules, and report timestamps default to **Asia/Kolkata (IST, UTC+5:30)**.
- **Multi-Tenant Data Isolated**: Strictly segregates SSC and INFRA operational records, allowing cross-workspace consolidated views exclusively to the `Owner` role.

---

## 2. Core Operational Capabilities

### 2.1 Universal Business AI Assistant (Ask Anything)
The AI Assistant processes multi-lingual queries in **Hindi**, **English**, or **Hinglish** through an intent classification engine:

| Intent Category | Query Examples | Processing Mechanism | Output Guarantee |
|---|---|---|---|
| `SOFTWARE_DOCS` | *"Estimate kaise banate hain?"*, *"How to issue a work order and pass QC?"* | Searches internal knowledge base and verified software documentation. | Explains the actual implemented interface, step-by-step navigation path, and never hallucinates non-existent options. |
| `BUSINESS_DATA` | *"Total profit kitna hua hai?"*, *"Pending inward payments status batao"* | Queries authorized database tables for the active tenant workspace. | Calculates real taxable invoiced totals, cash collections, operational expenses, and net profit with live timestamp and data source citation. |
| `RESEARCH_TENDERS` | *"GeM portal aur highway survey tenders kya chal rahe hain?"* | Queries verified public procurement indexes (CPPP, GeM, NHAI). | Returns verified source URLs, publication dates, tender scope summaries, and recommended bidding actions. |
| `TECHNICAL_SOP` | *"DGPS RTK accuracy tolerances kya hain?"*, *"MoRTH Section 300 earthwork compaction rules"* | Retrieves authoritative engineering standards from the Knowledge Base. | Cites Survey of India (SOI), DGCA Green Zone drone rules, and MoRTH specifications. |

---

### 2.2 Autonomous Daily Research Engine
Operates automatically every morning without owner intervention:
- **SSC Workspace**: Researches dual-frequency GNSS/RTK innovations, Survey of India benchmark integration, DGCA drone airspace regulations, and national highway tender notices (CPPP/NHAI).
- **INFRA Workspace**: Researches MoRTH technical circulars, industrial corridor earthwork tenders, warehouse logistics park demand along state bypasses, and geosynthetic retaining wall standards.
- **Persistence**: All items stored in `ai_research_items` with source name, URL link, publication date, relevance score (0–100%), and recommended commercial action.

---

### 2.3 Daily Autonomous Marketing Manager
Synthesizes dedicated strategic briefs every morning for SSC and INFRA:
- **Market Trends & Competitor Analysis**: Highlights high-performing B2B opportunities and competitor content gaps.
- **Platform Directives**: Formulates targeted concepts for **LinkedIn** (technical case studies), **Instagram/Facebook** (video reels/carousels), and **YouTube Shorts** (field machine demos).
- **Intelligent Posting Times (Asia/Kolkata Timezone)**:
  - **10:15 AM IST (LinkedIn)**: Target morning commercial review window for EPC contractors, project heads, and corporate developers.
  - **06:30 PM IST (Instagram/Facebook)**: Target evening prime engagement window for civil engineers and site contractors.
- **Dual-Language Scripts & Approval Staging**: Synthesizes Hindi and English voiceover transcripts and automatically routes generated campaigns to the `approvals` queue for owner sign-off.

---

### 2.4 Proactive Business Alert Engine
Continuously audits live operational conditions and flags actionable alerts to `ai_business_alerts`:
1. **Uncontacted High-Priority Leads**: Detects high-priority inquiries uncontacted for >24 hours and prompts immediate consultant allocation.
2. **Overdue Receivables**: Flags outstanding invoices exceeding ₹20,000 awaiting client payment.
3. **Pending Field QC**: Alerts the owner when raw survey measurements require QC approval before final deliverable release.
4. **Unapproved Expense Claims**: Summarizes submitted field travel/fuel vouchers awaiting manager approval.
- **Resolution**: Supports one-click *"Acknowledge & Resolve"* from the dashboard, timestamping closure.

---

### 2.5 Automated Reporting Engine (Daily, Weekly, Monthly)
Generates authoritative business intelligence documents directly from database records:
- **Daily Operations Report**: Active survey sites, new and qualified leads, field attendance logs, invoiced revenue, collections, operating profit, and marketing directives.
- **Weekly Executive Review**: Aggregated client onboarding, work order execution metrics, and strategic next-week goals.
- **Monthly Strategic P&L Closure**: Full month-end profit-and-loss closure, payroll overview, operational risk analysis, and corporate tender growth strategies.
- **Export & Storage**: Stored permanently in `ai_generated_reports` and exportable as formatted JSON or printable layouts.

---

### 2.6 Central Background Scheduler Daemon
- File: `foundation/scheduler.py`
- Runs as a persistent daemon thread alongside the server.
- Checks `ai_scheduler_jobs` every 30 seconds.
- Automatically executes due standing jobs:
  - `daily_research_ssc` (06:00 IST)
  - `daily_research_infra` (06:15 IST)
  - `daily_marketing_brief` (07:30 IST)
  - `daily_business_report` (20:00 IST)
  - `proactive_alerts_scan` (Hourly)
  - `weekly_business_report` (Saturday 19:00 IST)
  - `monthly_business_report` (Last day of month 21:00 IST)
- Logs all execution outcomes, timestamps, run counts, and diagnostics in `ai_scheduler_runs`.

---

## 3. Database Architecture (New Intelligence Tables)

The SQLite database (`data/sgcc_foundation.sqlite`) contains 66 tables, including 7 dedicated AI Brain tables:

```sql
-- 1. Autonomous Research Items
CREATE TABLE IF NOT EXISTS ai_research_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workspace_id TEXT NOT NULL,
    category TEXT NOT NULL,
    topic TEXT NOT NULL,
    summary TEXT NOT NULL,
    source_url TEXT,
    source_name TEXT,
    publication_date TEXT,
    retrieved_at TEXT NOT NULL,
    relevance_score INTEGER DEFAULT 80,
    recommended_action TEXT,
    verification_status TEXT DEFAULT 'verified',
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- 2. Daily Marketing Briefs
CREATE TABLE IF NOT EXISTS ai_marketing_briefs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workspace_id TEXT NOT NULL,
    brief_date TEXT NOT NULL,
    industry_trends TEXT NOT NULL,
    competitor_insights TEXT,
    recommended_posts TEXT NOT NULL,
    reel_ideas TEXT,
    platform_recommendations TEXT,
    posting_schedule TEXT,
    target_audience TEXT,
    cta_objective TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- 3. Automated Generated Reports
CREATE TABLE IF NOT EXISTS ai_generated_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workspace_id TEXT NOT NULL,
    report_type TEXT NOT NULL,
    period_label TEXT NOT NULL,
    title TEXT NOT NULL,
    summary TEXT NOT NULL,
    content_json TEXT NOT NULL,
    financial_snapshot TEXT,
    metrics_json TEXT,
    recommendations_json TEXT,
    generated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- 4. Proactive Business Alerts
CREATE TABLE IF NOT EXISTS ai_business_alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workspace_id TEXT NOT NULL,
    category TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    why_it_matters TEXT,
    supporting_data TEXT,
    recommended_action TEXT,
    priority TEXT NOT NULL DEFAULT 'medium',
    status TEXT NOT NULL DEFAULT 'active',
    alert_hash TEXT UNIQUE,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    resolved_at TEXT
);

-- 5. Memory & Internal Knowledge Base
CREATE TABLE IF NOT EXISTS ai_knowledge_base (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workspace_id TEXT NOT NULL,
    category TEXT NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    tags TEXT,
    source_file TEXT,
    verified INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- 6. Background Scheduler Jobs
CREATE TABLE IF NOT EXISTS ai_scheduler_jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_key TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    frequency TEXT NOT NULL,
    schedule_time TEXT NOT NULL,
    timezone TEXT NOT NULL DEFAULT 'Asia/Kolkata',
    is_enabled INTEGER NOT NULL DEFAULT 1,
    last_run_at TEXT,
    next_run_at TEXT,
    last_status TEXT DEFAULT 'pending',
    last_error TEXT,
    run_count INTEGER NOT NULL DEFAULT 0
);

-- 7. Scheduler Execution History
CREATE TABLE IF NOT EXISTS ai_scheduler_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_key TEXT NOT NULL,
    started_at TEXT NOT NULL,
    completed_at TEXT,
    status TEXT NOT NULL,
    summary TEXT,
    error_log TEXT
);
```

---

## 4. API Endpoints Reference

All endpoints require authentication (`Bearer <session_token>`).

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/intelligence/ask` | Multi-lingual assistant query `{query, workspace}`. Returns structured intent, answer, and data citations. |
| `GET` | `/api/intelligence/research` | Fetch latest categorized research items (`?workspace=SSC&category=tenders`). |
| `POST` | `/api/intelligence/research/run` | Trigger on-demand autonomous research generation `{category, workspace}`. |
| `GET` | `/api/intelligence/briefs` | Fetch the morning marketing brief for the active workspace. |
| `POST` | `/api/intelligence/briefs/generate` | Synthesize a new daily marketing brief with Asia/Kolkata posting times. |
| `GET` | `/api/intelligence/alerts` | Query active proactive business risk alerts (`?workspace=SSC&status=active`). |
| `POST` | `/api/intelligence/alerts/scan` | Trigger live business condition scan across invoices, leads, and work orders. |
| `POST` | `/api/intelligence/alerts/{id}/resolve` | Acknowledge and resolve an active business alert. |
| `GET` | `/api/intelligence/reports` | List generated business reports (`?workspace=SSC&type=daily`). |
| `GET` | `/api/intelligence/reports/{id}` | Retrieve full report details including parsed JSON metrics. |
| `POST` | `/api/intelligence/reports/generate` | Generate a new Daily, Weekly, or Monthly executive report. |
| `GET` | `/api/intelligence/scheduler/jobs` | Monitor standing background scheduler jobs and next run timestamps. |
| `GET` | `/api/intelligence/scheduler/runs` | Retrieve scheduler execution history and diagnostics log. |
| `POST` | `/api/intelligence/scheduler/run-now` | Manually trigger execution of any standing job `{job_key}`. |
| `GET` | `/api/intelligence/knowledge` | Search company SOPs, DGPS tolerances, and software guides (`?q=dgps`). |
| `POST` | `/api/intelligence/knowledge` | Register a new internal engineering SOP or guide `{category, title, content, tags}`. |

---

## 5. Verification & Acceptance Evidence

The Autonomous AI Brain has been fully verified across automated unit tests, integration tests, live API checks, and headless browser tests:

- **13/13 Mandatory Acceptance Points Passed** (`tests/test_autonomous_ai_brain.py`):
  - 100% test pass on software docs, source-backed external research, autonomous daily research, separate SSC/INFRA marketing briefs, Asia/Kolkata posting times, live DB statistics in reports, weekly and monthly report generation, live business alert triggers, scheduler job execution, execution history tracking, multi-tenant workspace isolation, and report storage/export.
- **7/7 Live API Integration Tests Passed** (`tests/test_ai_intelligence_api.py`):
  - All HTTP endpoints responding cleanly with status 200.
- **Live Chrome CDP Browser Audit**:
  - `scripts/browser_verify.js` executed through headless Chrome.
  - Successfully clicked through all 10 core tabs and all 8 AI Command Center sub-views.
  - **Zero console errors** (`Total Console Errors / Unhandled Exceptions: 0`).
- **Milestone Backup & Out-of-Place Restore Verified**:
  - Backup target: `backups/antigravity_2026-11-21_ai_brain_autonomous` (208 files).
  - Out-of-place restore to `C:\temp\antigravity_restore_ai_brain`.
  - **0 SHA-256 checksum mismatches**.
  - Restored SQLite integrity check: `ok` across all 66 tables.
