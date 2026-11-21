# SHAH Group AI OS — API Endpoints Reference

Base URL: `http://127.0.0.1:8899`
Authentication: `Authorization: Bearer <session_token>` or `X-Session-Token: <session_token>`

## Endpoint Catalog

| Method | Path | Auth Required | Description / Scope |
|---|---|---|---|
| `GET` | `/health` | No | Service health and name (`SHAH-Group-AI-OS`) |
| `GET` | `/` | No | Serves single-page application dashboard (`dashboard.html`) |
| `POST` | `/api/auth/login` | No | Authenticate user with `username` and `password`, returns session token |
| `POST` | `/api/auth/logout` | Yes | Invalidate caller session token |
| `GET` | `/api/auth/me` | Yes | Return authenticated user context and permissions |
| `GET` | `/api/permissions` | Yes | List all system permissions and matrix |
| `GET` | `/api/roles` | Yes | List system roles |
| `GET` | `/api/users` | Yes (Owner/Manager) | List registered users with active statuses |
| `POST` | `/api/users` | Yes (Owner/Manager) | Create new user account |
| `PUT` | `/api/users/{id}` | Yes (Owner/Manager) | Update user details (name, role, workspace, password) |
| `POST` | `/api/users/{id}/deactivate` | Yes (Owner/Manager) | Deactivate user account |
| `POST` | `/api/users/{id}/activate` | Yes (Owner/Manager) | Activate user account |
| `GET` | `/api/workspaces` | Yes | List workspaces available to caller |
| `GET` | `/api/workspaces/{code}/resources` | Yes | List workspace-scoped resources (e.g. SSC, INFRA) |
| `GET` | `/api/workspaces/{code}/contacts` | Yes | List contacts/clients for specific workspace |
| `GET` | `/api/approvals` | Yes | List approvals for workspace |
| `POST` | `/api/approvals` | Yes | Submit new approval request |
| `GET` | `/api/approvals/{id}` | Yes | Get approval details |
| `POST` | `/api/approvals/{id}/transition` | Yes (Approver/Owner) | Approve, reject, or withdraw approval request |
| `GET` | `/api/audit/{code}` | Yes | Retrieve workspace audit log trail |
| `GET` | `/api/dashboard/overview` | Yes | Aggregate dashboard KPIs (revenue, projects, staff, pending approvals) |
| `GET` | `/api/dashboard/workspaces` | Yes | Workspace summary stats |
| `GET` | `/api/dashboard/projects` | Yes | Project breakdown and site operations overview |
| `GET` | `/api/dashboard/finance` | Yes | Finance, expense claims, cash advances summary |
| `GET` | `/api/dashboard/employees` | Yes | HR, attendance, staff check-in counts |
| `GET` | `/api/dashboard/marketing` | Yes | Marketing campaigns and active ad stats |
| `GET` | `/api/dashboard/crm` | Yes | CRM leads, conversions, pipeline value |
| `GET` | `/api/dashboard/approvals` | Yes | Pending approval workflow queue |
| `GET` | `/api/dashboard/settings` | Yes | System settings and runtime config |
| `GET` | `/api/content` | Yes | List social and marketing content items |
| `POST` | `/api/content` | Yes | Draft new marketing content item / script |
| `GET` | `/api/content/{id}` | Yes | Content item details |
| `GET` | `/api/content/{id}/script` | Yes | Retrieve generated script for content item |
| `GET` | `/api/media` | Yes | List uploaded media assets |
| `POST` | `/api/media` | Yes | Register/upload media asset |
| `GET` | `/api/publish` | Yes | List publishing schedule |
| `POST` | `/api/publish` | Yes | Schedule/queue approved content item for publication |
| `GET` | `/api/social/accounts` | Yes | List connected social accounts |
| `POST` | `/api/social/accounts` | Yes | Register new social account |
| `GET` | `/api/leads` | Yes | Query leads and enquiries |
| `POST` | `/api/leads` | Yes | Create new lead or capture incoming enquiry |
| `POST` | `/api/leads/sync-csv` | Yes (Owner/Manager) | Sync historical leads from `data/leads.csv` into `social_leads` with deduplication |
| `POST` | `/api/leads/{id}/status` | Yes (Owner/Manager) | Update lead qualification and contact status |
| `POST` | `/api/leads/{id}/convert` | Yes (Owner/Manager) | Convert lead to client profile and optional active project site |
| `GET` | `/api/clients` | Yes | Query converted and registered client company profiles |
| `POST` | `/api/clients` | Yes (Owner/Manager) | Register new client company profile |
| `GET` | `/api/sites` | Yes | Query registered survey and infrastructure sites |
| `POST` | `/api/sites` | Yes (Owner/Manager) | Register new survey site with coordinates, geofence, and deliverable policy |
| `GET` | `/api/finance/vendors` | Yes | Query registered equipment and survey supply vendors |
| `POST` | `/api/finance/vendors` | Yes (Owner/Manager) | Register new equipment or service vendor |
| `GET` | `/api/finance/expenses` | Yes | Query submitted expense claims for workspace |
| `POST` | `/api/finance/expenses` | Yes | Submit staff expense claim with automatic approval queue staging |
| `GET` | `/api/employees` | Yes | Query workspace employee master directory |
| `POST` | `/api/employees` | Yes (Owner/HR/Manager) | Register new employee with role, designation, department, and salary |
| `GET` | `/api/attendance` | Yes | Query GPS attendance and check-in logs |
| `POST` | `/api/attendance` | Yes | Submit field check-in or check-out event with GPS coordinates and notes |
| `GET` | `/api/leaves` | Yes | Query submitted employee leave requests |
| `POST` | `/api/leaves` | Yes | Submit leave request with automatic approval queue staging |
| `GET` | `/api/payroll/runs` | Yes (Owner/Finance) | List all payroll execution runs for workspace |
| `POST` | `/api/payroll/calculate` | Yes (Owner/Finance) | Dry-run payroll calculation preview for month/year |
| `POST` | `/api/payroll/run` | Yes (Owner/Finance) | Execute payroll run, generate itemized payslips & auto-stage approval |
| `GET` | `/api/payroll/runs/{id}` | Yes (Owner/Finance) | Fetch payroll run details and list of all itemized payslips |
| `POST` | `/api/payroll/runs/{id}/approve` | Yes (Owner/Finance) | Approve payroll run, transitions status to approved |
| `GET` | `/api/payroll/payslips` | Yes (Owner/Finance/HR) | Query employee payslips with optional filtering |
| `GET` | `/api/payroll/payslips/{id}` | Yes | Fetch individual employee payslip breakdown |
| `POST` | `/api/leads/{id}/follow-up` | Yes | Schedule follow-up date and assigned staff member for lead |
| `GET` | `/api/leads/due-follow-ups` | Yes | Query pending leads with scheduled follow-up dates |
| `GET` | `/api/leads/export` | Yes | Export leads to RFC-4180 CSV file |
| `GET` | `/api/finance/expenses/export` | Yes | Export expense claims to CSV file |
| `GET` | `/api/sites/export` | Yes | Export survey/infrastructure sites to CSV file |
| `GET` | `/api/employees/export` | Yes | Export employee master list to CSV file |
| `POST` | `/api/ai-brain/action` | Yes | Autonomous AI tool execution route with mandatory Owner approval gating for sensitive actions |
| `POST` | `/api/ai-brain/tasks` | Yes | Create and dispatch AI task with real tool execution gating |
| `GET` | `/api/reports` | Yes | List generated business and performance reports |
| `POST` | `/api/reports` | Yes | Generate new report (weekly, monthly, project) |
| `GET` | `/api/system` | Yes | System environment diagnostics |
| `GET` | `/api/system/usage` | Yes | Server CPU, memory, and disk usage |
| `GET` | `/api/system/health` | Yes | System health audit checks |
| `GET` | `/api/ai-brain` | Yes | AI Brain status and context summary |
| `GET` | `/api/ai-brain/agents` | Yes | List registered AI agents |
| `GET` | `/api/ai-brain/tasks` | Yes | Query AI task queues and results |
| `POST` | `/api/intelligence/ask` | Yes | Universal Multi-lingual Business AI Assistant (Software docs, live DB calculations, tenders, engineering SOPs) |
| `GET` | `/api/intelligence/research` | Yes | Query autonomous daily industry research, tender notices, and tech intelligence |
| `POST` | `/api/intelligence/research/run` | Yes | Trigger autonomous daily research job for workspace without prompting |
| `GET` | `/api/intelligence/briefs` | Yes | Fetch morning strategic marketing brief for SSC or INFRA |
| `POST` | `/api/intelligence/briefs/generate` | Yes | Synthesize morning marketing brief with Asia/Kolkata posting time optimization |
| `GET` | `/api/intelligence/alerts` | Yes | Query proactive business risk, overdue invoice, pending QC, and uncontacted lead alerts |
| `POST` | `/api/intelligence/alerts/scan` | Yes | Trigger proactive business conditions scan across live database records |
| `POST` | `/api/intelligence/alerts/{id}/resolve` | Yes | Acknowledge and resolve an active business alert |
| `GET` | `/api/intelligence/reports` | Yes | List factual Daily, Weekly, and Monthly performance reports |
| `GET` | `/api/intelligence/reports/{id}` | Yes | Fetch detailed report structure with operational and P&L metrics |
| `POST` | `/api/intelligence/reports/generate` | Yes | Generate new Daily, Weekly, or Monthly executive report |
| `GET` | `/api/intelligence/scheduler/jobs` | Yes | List standing persistent scheduler daemon jobs with Asia/Kolkata timing |
| `GET` | `/api/intelligence/scheduler/runs` | Yes | Query scheduler execution history, completion status, and diagnostics |
| `POST` | `/api/intelligence/scheduler/run-now` | Yes | Manually trigger immediate execution of a scheduled intelligence job |
| `GET` | `/api/intelligence/knowledge` | Yes | Query internal company SOPs, DGPS tolerances, MoRTH standards, and software guides |
| `POST` | `/api/intelligence/knowledge` | Yes | Register new authoritative engineering SOP or software document in Knowledge Base |
