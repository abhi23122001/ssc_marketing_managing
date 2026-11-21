# SHAH Group AI OS — Database Schema Reference

**Database File**: `data/sgcc_foundation.sqlite`
**Total Tables**: 66

## Table Summary
| Table Name | Row Count | Primary Purpose |
|------------|-----------|-----------------|
| `ai_agents` | 4 | System / Domain table |
| `ai_tasks` | 3 | System / Domain table |
| `ai_tool_executions` | 0 | System / Domain table |
| `approvals` | 5 | System / Domain table |
| `attendance_logs` | 5 | System / Domain table |
| `audit_logs` | 16 | System / Domain table |
| `cash_advance` | 0 | System / Domain table |
| `departments` | 0 | System / Domain table |
| `employee_documents` | 0 | System / Domain table |
| `employees` | 0 | System / Domain table |
| `expense_claims` | 0 | System / Domain table |
| `expense_vendors` | 3 | System / Domain table |
| `geofences` | 0 | System / Domain table |
| `leaves` | 0 | System / Domain table |
| `payroll_runs` | 0 | System / Domain table |
| `payslips` | 0 | System / Domain table |
| `resources` | 258 | System / Domain table |
| `roles` | 7 | System / Domain table |
| `sessions` | 202 | System / Domain table |
| `sites` | 4 | System / Domain table |
| `social_account_syncs` | 0 | System / Domain table |
| `social_accounts` | 5 | System / Domain table |
| `social_agent_runs` | 0 | System / Domain table |
| `social_approvals` | 0 | System / Domain table |
| `social_brand_assets` | 0 | System / Domain table |
| `social_brand_profiles` | 0 | System / Domain table |
| `social_calendar_entries` | 0 | System / Domain table |
| `social_campaigns` | 3 | System / Domain table |
| `social_client_profiles` | 0 | System / Domain table |
| `social_comments` | 0 | System / Domain table |
| `social_competitor_profiles` | 0 | System / Domain table |
| `social_content_ideas` | 0 | System / Domain table |
| `social_content_items` | 6 | System / Domain table |
| `social_content_versions` | 1 | System / Domain table |
| `social_employee_kpis` | 0 | System / Domain table |
| `social_integration_logs` | 0 | System / Domain table |
| `social_lead_attribution` | 0 | System / Domain table |
| `social_leads` | 8 | System / Domain table |
| `social_media_assets` | 0 | System / Domain table |
| `social_messages` | 0 | System / Domain table |
| `social_notifications` | 0 | System / Domain table |
| `social_publish_jobs` | 0 | System / Domain table |
| `social_published_posts` | 0 | System / Domain table |
| `social_reports` | 1 | System / Domain table |
| `social_scripts` | 0 | System / Domain table |
| `social_subtitles` | 0 | System / Domain table |
| `social_tasks` | 0 | System / Domain table |
| `social_thumbnails` | 0 | System / Domain table |
| `social_trends` | 0 | System / Domain table |
| `social_video_jobs` | 0 | System / Domain table |
| `social_workspaces` | 0 | System / Domain table |
| `users` | 32 | System / Domain table |
| `workspaces` | 3 | System / Domain table |
| `business_estimates` | 5 | Business Operations: Project Estimates & BOQ |
| `business_quotations` | 5 | Business Operations: Taxable Quotations (18% GST) |
| `business_work_orders` | 5 | Business Operations: Work Orders & Field QC Status |
| `business_invoices` | 5 | Business Operations: Tax Invoices & Billing |
| `business_payments` | 10 | Business Operations: Inward Payments & Settlements |
| `ai_research_items` | 37 | AI Brain: Autonomous Daily Industry & Tender Research |
| `ai_marketing_briefs` | 19 | AI Brain: Daily Morning Marketing Briefs (Asia/Kolkata) |
| `ai_generated_reports` | 16 | AI Brain: Daily, Weekly, Monthly Performance Reports |
| `ai_business_alerts` | 6 | AI Brain: Proactive Business Risk & Tender Alerts |
| `ai_knowledge_base` | 11 | AI Brain: Company Standards, SOPs & Software Guides |
| `ai_scheduler_jobs` | 7 | AI Brain: Persistent Central Scheduler Standing Jobs |
| `ai_scheduler_runs` | 13 | AI Brain: Central Scheduler Execution & Retry History |

## Detailed Table Schemas
### `ai_agents`
| cid | Column Name | Type | Not Null | Default Value | Primary Key |
|-----|-------------|------|----------|---------------|-------------|
| 0 | `id` | INTEGER | 0 | None | 1 |
| 1 | `workspace_id` | TEXT | 0 | None | 0 |
| 2 | `code` | TEXT | 1 | None | 0 |
| 3 | `name` | TEXT | 1 | None | 0 |
| 4 | `description` | TEXT | 1 | '' | 0 |
| 5 | `agent_type` | TEXT | 1 | 'general' | 0 |
| 6 | `tool_access` | TEXT | 1 | '{}' | 0 |
| 7 | `status` | TEXT | 1 | 'active' | 0 |
| 8 | `created_at` | TEXT | 1 | datetime('now') | 0 |

```sql
CREATE TABLE ai_agents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workspace_id TEXT,
    code TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    agent_type TEXT NOT NULL DEFAULT 'general',
    tool_access TEXT NOT NULL DEFAULT '{}',
    status TEXT NOT NULL DEFAULT 'active',
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
)
```

### `ai_tasks`
| cid | Column Name | Type | Not Null | Default Value | Primary Key |
|-----|-------------|------|----------|---------------|-------------|
| 0 | `id` | INTEGER | 0 | None | 1 |
| 1 | `workspace_id` | TEXT | 0 | None | 0 |
| 2 | `agent_id` | INTEGER | 0 | None | 0 |
| 3 | `title` | TEXT | 1 | None | 0 |
| 4 | `description` | TEXT | 1 | '' | 0 |
| 5 | `priority` | TEXT | 1 | 'medium' | 0 |
| 6 | `assigned_to` | INTEGER | 0 | None | 0 |
| 7 | `status` | TEXT | 1 | 'open' | 0 |
| 8 | `result_summary` | TEXT | 1 | '' | 0 |
| 9 | `audit_note` | TEXT | 1 | '' | 0 |
| 10 | `tool_requests` | TEXT | 1 | '{}' | 0 |
| 11 | `created_at` | TEXT | 1 | datetime('now') | 0 |
| 12 | `updated_at` | TEXT | 1 | datetime('now') | 0 |
| 13 | `started_at` | TEXT | 0 | None | 0 |
| 14 | `completed_at` | TEXT | 0 | None | 0 |

```sql
CREATE TABLE ai_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workspace_id TEXT,
    agent_id INTEGER,
    title TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    priority TEXT NOT NULL DEFAULT 'medium',
    assigned_to INTEGER,
    status TEXT NOT NULL DEFAULT 'open',  -- open, in_progress, completed, blocked, cancelled
    result_summary TEXT NOT NULL DEFAULT '',
    audit_note TEXT NOT NULL DEFAULT '',
    tool_requests TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    started_at TEXT,
    completed_at TEXT,
    FOREIGN KEY (agent_id) REFERENCES ai_agents(id) ON DELETE SET NULL,
    FOREIGN KEY (assigned_to) REFERENCES employees(id) ON DELETE SET NULL
)
```

### `ai_tool_executions`
| cid | Column Name | Type | Not Null | Default Value | Primary Key |
|-----|-------------|------|----------|---------------|-------------|
| 0 | `id` | INTEGER | 0 | None | 1 |
| 1 | `ai_task_id` | INTEGER | 0 | None | 0 |
| 2 | `tool_name` | TEXT | 1 | None | 0 |
| 3 | `args` | TEXT | 1 | '{}' | 0 |
| 4 | `allowed` | INTEGER | 1 | 0 | 0 |
| 5 | `result` | TEXT | 1 | '{}' | 0 |
| 6 | `executed_by` | INTEGER | 0 | None | 0 |
| 7 | `started_at` | TEXT | 1 | datetime('now') | 0 |
| 8 | `completed_at` | TEXT | 0 | None | 0 |

```sql
CREATE TABLE ai_tool_executions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ai_task_id INTEGER,
    tool_name TEXT NOT NULL,
    args TEXT NOT NULL DEFAULT '{}',
    allowed INTEGER NOT NULL DEFAULT 0,
    result TEXT NOT NULL DEFAULT '{}',
    executed_by INTEGER,
    started_at TEXT NOT NULL DEFAULT (datetime('now')),
    completed_at TEXT,
    FOREIGN KEY (ai_task_id) REFERENCES ai_tasks(id) ON DELETE CASCADE,
    FOREIGN KEY (executed_by) REFERENCES employees(id) ON DELETE SET NULL
)
```

### `approvals`
| cid | Column Name | Type | Not Null | Default Value | Primary Key |
|-----|-------------|------|----------|---------------|-------------|
| 0 | `id` | INTEGER | 0 | None | 1 |
| 1 | `resource_id` | INTEGER | 1 | None | 0 |
| 2 | `title` | TEXT | 1 | None | 0 |
| 3 | `description` | TEXT | 1 | '' | 0 |
| 4 | `status` | TEXT | 1 | 'draft' | 0 |
| 5 | `current_stage` | TEXT | 1 | 'review' | 0 |
| 6 | `requested_by` | INTEGER | 1 | None | 0 |
| 7 | `created_at` | TEXT | 1 | datetime('now') | 0 |
| 8 | `updated_at` | TEXT | 1 | datetime('now') | 0 |
| 9 | `metadata` | TEXT | 1 | '{}' | 0 |

```sql
CREATE TABLE approvals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            resource_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL DEFAULT '',
            status TEXT NOT NULL DEFAULT 'draft',   -- draft, pending, approved, rejected, withdrawn
            current_stage TEXT NOT NULL DEFAULT 'review',
            requested_by INTEGER NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at TEXT NOT NULL DEFAULT (datetime('now')),
            metadata TEXT NOT NULL DEFAULT '{}',
            FOREIGN KEY (resource_id) REFERENCES resources(id) ON DELETE CASCADE,
            FOREIGN KEY (requested_by) REFERENCES users(id)
        )
```

### `attendance_logs`
| cid | Column Name | Type | Not Null | Default Value | Primary Key |
|-----|-------------|------|----------|---------------|-------------|
| 0 | `id` | INTEGER | 0 | None | 1 |
| 1 | `workspace_id` | TEXT | 0 | None | 0 |
| 2 | `employee_id` | INTEGER | 1 | None | 0 |
| 3 | `site_id` | INTEGER | 1 | None | 0 |
| 4 | `check_in` | TEXT | 1 | None | 0 |
| 5 | `check_out` | TEXT | 1 | '' | 0 |
| 6 | `gps_lat` | REAL | 1 | 0 | 0 |
| 7 | `gps_lng` | REAL | 1 | 0 | 0 |
| 8 | `geofence_passed` | INTEGER | 1 | 0 | 0 |
| 9 | `selfie_taken` | INTEGER | 1 | 0 | 0 |
| 10 | `status` | TEXT | 1 | 'present' | 0 |
| 11 | `notes` | TEXT | 1 | '' | 0 |
| 12 | `created_at` | TEXT | 1 | datetime('now') | 0 |

```sql
CREATE TABLE attendance_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workspace_id TEXT,
    employee_id INTEGER NOT NULL,
    site_id INTEGER NOT NULL,
    check_in TEXT NOT NULL,
    check_out TEXT NOT NULL DEFAULT '',
    gps_lat REAL NOT NULL DEFAULT 0,
    gps_lng REAL NOT NULL DEFAULT 0,
    geofence_passed INTEGER NOT NULL DEFAULT 0,
    selfie_taken INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'present',  -- present, absent, late, early, no_show
    notes TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE,
    FOREIGN KEY (site_id) REFERENCES sites(id) ON DELETE CASCADE
)
```

### `audit_logs`
| cid | Column Name | Type | Not Null | Default Value | Primary Key |
|-----|-------------|------|----------|---------------|-------------|
| 0 | `id` | INTEGER | 0 | None | 1 |
| 1 | `actor_id` | INTEGER | 0 | None | 0 |
| 2 | `actor_username` | TEXT | 0 | None | 0 |
| 3 | `action` | TEXT | 1 | None | 0 |
| 4 | `target` | TEXT | 1 | None | 0 |
| 5 | `details` | TEXT | 1 | '{}' | 0 |
| 6 | `workspace_id` | TEXT | 0 | None | 0 |
| 7 | `created_at` | TEXT | 1 | datetime('now') | 0 |

```sql
CREATE TABLE audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            actor_id INTEGER,
            actor_username TEXT,
            action TEXT NOT NULL,
            target TEXT NOT NULL,
            details TEXT NOT NULL DEFAULT '{}',
            workspace_id TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (actor_id) REFERENCES users(id)
        )
```

### `cash_advance`
| cid | Column Name | Type | Not Null | Default Value | Primary Key |
|-----|-------------|------|----------|---------------|-------------|
| 0 | `id` | INTEGER | 0 | None | 1 |
| 1 | `workspace_id` | TEXT | 0 | None | 0 |
| 2 | `employee_id` | INTEGER | 1 | None | 0 |
| 3 | `amount` | REAL | 1 | 0 | 0 |
| 4 | `currency` | TEXT | 1 | 'INR' | 0 |
| 5 | `status` | TEXT | 1 | 'advanced' | 0 |
| 6 | `advance_date` | TEXT | 1 | datetime('now') | 0 |
| 7 | `settled_at` | TEXT | 0 | None | 0 |
| 8 | `created_at` | TEXT | 1 | datetime('now') | 0 |

```sql
CREATE TABLE cash_advance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workspace_id TEXT,
    employee_id INTEGER NOT NULL,
    amount REAL NOT NULL DEFAULT 0,
    currency TEXT NOT NULL DEFAULT 'INR',
    status TEXT NOT NULL DEFAULT 'advanced',  -- advanced, settled, partially_settled
    advance_date TEXT NOT NULL DEFAULT (datetime('now')),
    settled_at TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE
)
```

### `departments`
| cid | Column Name | Type | Not Null | Default Value | Primary Key |
|-----|-------------|------|----------|---------------|-------------|
| 0 | `id` | INTEGER | 0 | None | 1 |
| 1 | `workspace_id` | TEXT | 0 | None | 0 |
| 2 | `code` | TEXT | 1 | None | 0 |
| 3 | `label` | TEXT | 1 | None | 0 |
| 4 | `created_at` | TEXT | 1 | datetime('now') | 0 |

```sql
CREATE TABLE departments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workspace_id TEXT,
    code TEXT UNIQUE NOT NULL,
    label TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
)
```

### `employee_documents`
| cid | Column Name | Type | Not Null | Default Value | Primary Key |
|-----|-------------|------|----------|---------------|-------------|
| 0 | `id` | INTEGER | 0 | None | 1 |
| 1 | `employee_id` | INTEGER | 1 | None | 0 |
| 2 | `doc_type` | TEXT | 1 | None | 0 |
| 3 | `doc_url` | TEXT | 1 | '' | 0 |
| 4 | `uploaded_by` | INTEGER | 1 | None | 0 |
| 5 | `created_at` | TEXT | 1 | datetime('now') | 0 |

```sql
CREATE TABLE employee_documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER NOT NULL,
    doc_type TEXT NOT NULL,
    doc_url TEXT NOT NULL DEFAULT '',
    uploaded_by INTEGER NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE
)
```

### `employees`
| cid | Column Name | Type | Not Null | Default Value | Primary Key |
|-----|-------------|------|----------|---------------|-------------|
| 0 | `id` | INTEGER | 0 | None | 1 |
| 1 | `workspace_id` | TEXT | 0 | None | 0 |
| 2 | `employee_id` | TEXT | 1 | None | 0 |
| 3 | `name` | TEXT | 1 | None | 0 |
| 4 | `designation` | TEXT | 1 | '' | 0 |
| 5 | `department_id` | INTEGER | 0 | None | 0 |
| 6 | `hire_date` | TEXT | 1 | '' | 0 |
| 7 | `resignation_date` | TEXT | 1 | '' | 0 |
| 8 | `status` | TEXT | 1 | 'active' | 0 |
| 9 | `email` | TEXT | 1 | '' | 0 |
| 10 | `phone` | TEXT | 1 | '' | 0 |
| 11 | `manager_id` | INTEGER | 0 | None | 0 |
| 12 | `created_at` | TEXT | 1 | datetime('now') | 0 |

```sql
CREATE TABLE employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workspace_id TEXT,
    employee_id TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    designation TEXT NOT NULL DEFAULT '',
    department_id INTEGER,
    hire_date TEXT NOT NULL DEFAULT '',
    resignation_date TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'active',  -- active, resigned, left
    email TEXT NOT NULL DEFAULT '',
    phone TEXT NOT NULL DEFAULT '',
    manager_id INTEGER,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE SET NULL,
    FOREIGN KEY (manager_id) REFERENCES employees(id) ON DELETE SET NULL
)
```

### `expense_claims`
| cid | Column Name | Type | Not Null | Default Value | Primary Key |
|-----|-------------|------|----------|---------------|-------------|
| 0 | `id` | INTEGER | 0 | None | 1 |
| 1 | `workspace_id` | TEXT | 0 | None | 0 |
| 2 | `employee_id` | INTEGER | 1 | None | 0 |
| 3 | `project_id` | TEXT | 1 | '' | 0 |
| 4 | `category` | TEXT | 1 | 'travel' | 0 |
| 5 | `amount` | REAL | 1 | 0 | 0 |
| 6 | `currency` | TEXT | 1 | 'INR' | 0 |
| 7 | `receipt_url` | TEXT | 1 | '' | 0 |
| 8 | `cash_advance_id` | INTEGER | 0 | None | 0 |
| 9 | `status` | TEXT | 1 | 'submitted' | 0 |
| 10 | `submitted_by` | INTEGER | 1 | None | 0 |
| 11 | `notes` | TEXT | 1 | '' | 0 |
| 12 | `submitted_at` | TEXT | 1 | datetime('now') | 0 |
| 13 | `approved_by` | INTEGER | 0 | None | 0 |
| 14 | `approved_at` | TEXT | 0 | None | 0 |
| 15 | `created_at` | TEXT | 1 | datetime('now') | 0 |

```sql
CREATE TABLE expense_claims (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workspace_id TEXT,
    employee_id INTEGER NOT NULL,
    project_id TEXT NOT NULL DEFAULT '',
    category TEXT NOT NULL DEFAULT 'travel',  -- travel, food_lodging, fuel, site_expense, equipment_maintenance, other
    amount REAL NOT NULL DEFAULT 0,
    currency TEXT NOT NULL DEFAULT 'INR',
    receipt_url TEXT NOT NULL DEFAULT '',
    cash_advance_id INTEGER,
    status TEXT NOT NULL DEFAULT 'submitted',  -- submitted, pending_approval, approved, rejected, settled
    submitted_by INTEGER NOT NULL,
    notes TEXT NOT NULL DEFAULT '',
    submitted_at TEXT NOT NULL DEFAULT (datetime('now')),
    approved_by INTEGER,
    approved_at TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE
)
```

### `expense_vendors`
| cid | Column Name | Type | Not Null | Default Value | Primary Key |
|-----|-------------|------|----------|---------------|-------------|
| 0 | `id` | INTEGER | 0 | None | 1 |
| 1 | `workspace_id` | TEXT | 0 | None | 0 |
| 2 | `name` | TEXT | 1 | None | 0 |
| 3 | `category` | TEXT | 1 | 'vendor' | 0 |
| 4 | `contact` | TEXT | 1 | '' | 0 |
| 5 | `created_at` | TEXT | 1 | datetime('now') | 0 |

```sql
CREATE TABLE expense_vendors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workspace_id TEXT,
    name TEXT NOT NULL,
    category TEXT NOT NULL DEFAULT 'vendor',
    contact TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
)
```

### `geofences`
| cid | Column Name | Type | Not Null | Default Value | Primary Key |
|-----|-------------|------|----------|---------------|-------------|
| 0 | `id` | INTEGER | 0 | None | 1 |
| 1 | `site_id` | INTEGER | 1 | None | 0 |
| 2 | `name` | TEXT | 1 | None | 0 |
| 3 | `polygon_json` | TEXT | 1 | '{}' | 0 |
| 4 | `enabled` | INTEGER | 1 | 1 | 0 |
| 5 | `created_at` | TEXT | 1 | datetime('now') | 0 |

```sql
CREATE TABLE geofences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    site_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    polygon_json TEXT NOT NULL DEFAULT '{}',
    enabled INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (site_id) REFERENCES sites(id) ON DELETE CASCADE
)
```

### `leaves`
| cid | Column Name | Type | Not Null | Default Value | Primary Key |
|-----|-------------|------|----------|---------------|-------------|
| 0 | `id` | INTEGER | 0 | None | 1 |
| 1 | `employee_id` | INTEGER | 1 | None | 0 |
| 2 | `type` | TEXT | 1 | 'annual' | 0 |
| 3 | `start_date` | TEXT | 1 | None | 0 |
| 4 | `end_date` | TEXT | 1 | None | 0 |
| 5 | `days` | REAL | 1 | 0 | 0 |
| 6 | `status` | TEXT | 1 | 'applied' | 0 |
| 7 | `approved_by` | INTEGER | 0 | None | 0 |
| 8 | `reason` | TEXT | 1 | '' | 0 |
| 9 | `created_at` | TEXT | 1 | datetime('now') | 0 |

```sql
CREATE TABLE leaves (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER NOT NULL,
    type TEXT NOT NULL DEFAULT 'annual',  -- annual, sick, casual, leave_without_pay
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    days REAL NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'applied',  -- applied, approved, rejected, carried
    approved_by INTEGER,
    reason TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE,
    FOREIGN KEY (approved_by) REFERENCES employees(id) ON DELETE SET NULL
)
```

### `payroll_runs`
| cid | Column Name | Type | Not Null | Default Value | Primary Key |
|-----|-------------|------|----------|---------------|-------------|
| 0 | `id` | INTEGER | 0 | None | 1 |
| 1 | `workspace_id` | TEXT | 0 | None | 0 |
| 2 | `run_month` | TEXT | 1 | None | 0 |
| 3 | `period` | TEXT | 1 | 'monthly' | 0 |
| 4 | `run_by` | INTEGER | 1 | None | 0 |
| 5 | `status` | TEXT | 1 | 'draft' | 0 |
| 6 | `total_gross` | REAL | 1 | 0 | 0 |
| 7 | `total_deductions` | REAL | 1 | 0 | 0 |
| 8 | `total_in_hand` | REAL | 1 | 0 | 0 |
| 9 | `ledger_snapshot` | TEXT | 1 | '{}' | 0 |
| 10 | `created_at` | TEXT | 1 | datetime('now') | 0 |
| 11 | `processed_at` | TEXT | 0 | None | 0 |

```sql
CREATE TABLE payroll_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workspace_id TEXT,
    run_month TEXT NOT NULL,
    period TEXT NOT NULL DEFAULT 'monthly',
    run_by INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'draft',  -- draft, ready, approved
    total_gross REAL NOT NULL DEFAULT 0,
    total_deductions REAL NOT NULL DEFAULT 0,
    total_in_hand REAL NOT NULL DEFAULT 0,
    ledger_snapshot TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    processed_at TEXT,
    FOREIGN KEY (run_by) REFERENCES employees(id) ON DELETE SET NULL
)
```

### `payslips`
| cid | Column Name | Type | Not Null | Default Value | Primary Key |
|-----|-------------|------|----------|---------------|-------------|
| 0 | `id` | INTEGER | 0 | None | 1 |
| 1 | `payroll_run_id` | INTEGER | 1 | None | 0 |
| 2 | `employee_id` | INTEGER | 1 | None | 0 |
| 3 | `name` | TEXT | 1 | None | 0 |
| 4 | `month` | TEXT | 1 | None | 0 |
| 5 | `gross` | REAL | 1 | 0 | 0 |
| 6 | `deductions` | REAL | 1 | 0 | 0 |
| 7 | `in_hand` | REAL | 1 | 0 | 0 |
| 8 | `report_url` | TEXT | 1 | '' | 0 |
| 9 | `generated_at` | TEXT | 1 | datetime('now') | 0 |

```sql
CREATE TABLE payslips (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    payroll_run_id INTEGER NOT NULL,
    employee_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    month TEXT NOT NULL,
    gross REAL NOT NULL DEFAULT 0,
    deductions REAL NOT NULL DEFAULT 0,
    in_hand REAL NOT NULL DEFAULT 0,
    report_url TEXT NOT NULL DEFAULT '',
    generated_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (payroll_run_id) REFERENCES payroll_runs(id) ON DELETE CASCADE
)
```

### `resources`
| cid | Column Name | Type | Not Null | Default Value | Primary Key |
|-----|-------------|------|----------|---------------|-------------|
| 0 | `id` | INTEGER | 0 | None | 1 |
| 1 | `workspace_id` | TEXT | 1 | None | 0 |
| 2 | `key` | TEXT | 1 | None | 0 |
| 3 | `name` | TEXT | 1 | None | 0 |
| 4 | `description` | TEXT | 1 | '' | 0 |
| 5 | `created_at` | TEXT | 1 | datetime('now') | 0 |

```sql
CREATE TABLE resources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            workspace_id TEXT NOT NULL,
            key TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE
        )
```

### `roles`
| cid | Column Name | Type | Not Null | Default Value | Primary Key |
|-----|-------------|------|----------|---------------|-------------|
| 0 | `id` | INTEGER | 0 | None | 1 |
| 1 | `code` | TEXT | 1 | None | 0 |
| 2 | `label` | TEXT | 1 | None | 0 |
| 3 | `seat` | TEXT | 1 | 'other' | 0 |

```sql
CREATE TABLE roles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            label TEXT NOT NULL,
            seat TEXT NOT NULL DEFAULT 'other'
        )
```

### `sessions`
| cid | Column Name | Type | Not Null | Default Value | Primary Key |
|-----|-------------|------|----------|---------------|-------------|
| 0 | `token` | TEXT | 0 | None | 1 |
| 1 | `user_id` | INTEGER | 1 | None | 0 |
| 2 | `created_at` | TEXT | 1 | datetime('now') | 0 |
| 3 | `expires_at` | TEXT | 1 | None | 0 |

```sql
CREATE TABLE sessions (
            token TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            expires_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
```

### `sites`
| cid | Column Name | Type | Not Null | Default Value | Primary Key |
|-----|-------------|------|----------|---------------|-------------|
| 0 | `id` | INTEGER | 0 | None | 1 |
| 1 | `workspace_id` | TEXT | 0 | None | 0 |
| 2 | `name` | TEXT | 1 | None | 0 |
| 3 | `code` | TEXT | 1 | None | 0 |
| 4 | `address` | TEXT | 1 | '' | 0 |
| 5 | `geofence_radius_m` | REAL | 1 | 100 | 0 |
| 6 | `field_policy_required` | INTEGER | 1 | 0 | 0 |
| 7 | `created_at` | TEXT | 1 | datetime('now') | 0 |

```sql
CREATE TABLE sites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workspace_id TEXT,
    name TEXT NOT NULL,
    code TEXT UNIQUE NOT NULL,
    address TEXT NOT NULL DEFAULT '',
    geofence_radius_m REAL NOT NULL DEFAULT 100,
    field_policy_required INTEGER NOT NULL DEFAULT 0,  -- 1 = GPS/selfie/geofencing mandatory
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
)
```

### `social_account_syncs`
| cid | Column Name | Type | Not Null | Default Value | Primary Key |
|-----|-------------|------|----------|---------------|-------------|
| 0 | `id` | INTEGER | 0 | None | 1 |
| 1 | `account_id` | INTEGER | 1 | None | 0 |
| 2 | `status` | TEXT | 1 | 'ok' | 0 |
| 3 | `scope` | TEXT | 1 | 'ok' | 0 |
| 4 | `error` | TEXT | 0 | None | 0 |
| 5 | `started_at` | TEXT | 1 | None | 0 |
| 6 | `finished_at` | TEXT | 0 | None | 0 |

```sql
CREATE TABLE social_account_syncs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'ok',
    scope TEXT NOT NULL DEFAULT 'ok',
    error TEXT,
    started_at TEXT NOT NULL,
    finished_at TEXT,
    FOREIGN KEY (account_id) REFERENCES social_accounts(id) ON DELETE CASCADE
)
```

### `social_accounts`
| cid | Column Name | Type | Not Null | Default Value | Primary Key |
|-----|-------------|------|----------|---------------|-------------|
| 0 | `id` | INTEGER | 0 | None | 1 |
| 1 | `workspace_id` | TEXT | 1 | None | 0 |
| 2 | `client_workspace_id` | TEXT | 0 | None | 0 |
| 3 | `platform` | TEXT | 1 | None | 0 |
| 4 | `platform_account_id` | TEXT | 1 | '' | 0 |
| 5 | `display_name` | TEXT | 1 | '' | 0 |
| 6 | `account_url` | TEXT | 1 | '' | 0 |
| 7 | `account_category` | TEXT | 1 | '' | 0 |
| 8 | `account_owner` | TEXT | 1 | '' | 0 |
| 9 | `connection_status` | TEXT | 1 | 'disconnected' | 0 |
| 10 | `granted_permissions` | TEXT | 1 | '{}' | 0 |
| 11 | `token_expires_at` | TEXT | 0 | None | 0 |
| 12 | `last_sync_at` | TEXT | 0 | None | 0 |
| 13 | `last_failed_sync_at` | TEXT | 0 | None | 0 |
| 14 | `last_error` | TEXT | 0 | None | 0 |
| 15 | `connected_date` | TEXT | 1 | datetime('now') | 0 |
| 16 | `authorized_user` | TEXT | 1 | 'owner' | 0 |

```sql
CREATE TABLE social_accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workspace_id TEXT NOT NULL,
    client_workspace_id TEXT,
    platform TEXT NOT NULL,
    platform_account_id TEXT NOT NULL DEFAULT '',
    display_name TEXT NOT NULL DEFAULT '',
    account_url TEXT NOT NULL DEFAULT '',
    account_category TEXT NOT NULL DEFAULT '',
    account_owner TEXT NOT NULL DEFAULT '',
    connection_status TEXT NOT NULL DEFAULT 'disconnected',
    granted_permissions TEXT NOT NULL DEFAULT '{}',
    token_expires_at TEXT,
    last_sync_at TEXT,
    last_failed_sync_at TEXT,
    last_error TEXT,
    connected_date TEXT NOT NULL DEFAULT (datetime('now')),
    authorized_user TEXT NOT NULL DEFAULT 'owner',
    UNIQUE(workspace_id, platform, platform_account_id),
    FOREIGN KEY (workspace_id) REFERENCES social_workspaces(id) ON DELETE CASCADE,
    FOREIGN KEY (client_workspace_id) REFERENCES social_workspaces(id) ON DELETE SET NULL,
    CHECK (platform IN ('instagram','facebook','linkedin','youtube'))
)
```

### `social_agent_runs`
| cid | Column Name | Type | Not Null | Default Value | Primary Key |
|-----|-------------|------|----------|---------------|-------------|
| 0 | `id` | INTEGER | 0 | None | 1 |
| 1 | `agent_code` | TEXT | 1 | '' | 0 |
| 2 | `workspace_id` | TEXT | 1 | None | 0 |
| 3 | `client_workspace_id` | TEXT | 0 | None | 0 |
| 4 | `tool_name` | TEXT | 1 | '' | 0 |
| 5 | `permission_ok` | INTEGER | 1 | 0 | 0 |
| 6 | `status` | TEXT | 1 | 'running' | 0 |
| 7 | `result_summary` | TEXT | 1 | '' | 0 |
| 8 | `error` | TEXT | 0 | None | 0 |
| 9 | `queue_time` | TEXT | 0 | None | 0 |
| 10 | `started_at` | TEXT | 0 | None | 0 |
| 11 | `processing_time` | TEXT | 0 | None | 0 |
| 12 | `completed_at` | TEXT | 0 | None | 0 |
| 13 | `created_at` | TEXT | 1 | datetime('now') | 0 |

```sql
CREATE TABLE social_agent_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_code TEXT NOT NULL DEFAULT '',
    workspace_id TEXT NOT NULL,
    client_workspace_id TEXT,
    tool_name TEXT NOT NULL DEFAULT '',
    permission_ok INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'running',
    result_summary TEXT NOT NULL DEFAULT '',
    error TEXT,
    queue_time TEXT,
    started_at TEXT,
    processing_time TEXT,
    completed_at TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (workspace_id) REFERENCES social_workspaces(id) ON DELETE CASCADE
)
```

### `social_approvals`
| cid | Column Name | Type | Not Null | Default Value | Primary Key |
|-----|-------------|------|----------|---------------|-------------|
| 0 | `id` | INTEGER | 0 | None | 1 |
| 1 | `content_id` | INTEGER | 1 | None | 0 |
| 2 | `client_workspace_id` | TEXT | 0 | None | 0 |
| 3 | `requester_id` | INTEGER | 1 | None | 0 |
| 4 | `approver_ids` | TEXT | 1 | '[]' | 0 |
| 5 | `status` | TEXT | 1 | 'pending' | 0 |
| 6 | `version_locked` | INTEGER | 1 | 1 | 0 |
| 7 | `final_version` | INTEGER | 1 | 0 | 0 |
| 8 | `final_script` | TEXT | 1 | '' | 0 |
| 9 | `final_caption` | TEXT | 1 | '' | 0 |
| 10 | `final_cta` | TEXT | 1 | '' | 0 |
| 11 | `final_hashtags` | TEXT | 1 | '[]' | 0 |
| 12 | `final_media_url` | TEXT | 1 | '' | 0 |
| 13 | `approval_note` | TEXT | 1 | '' | 0 |
| 14 | `approved_at` | TEXT | 0 | None | 0 |
| 15 | `created_at` | TEXT | 1 | datetime('now') | 0 |
| 16 | `updated_at` | TEXT | 1 | datetime('now') | 0 |

```sql
CREATE TABLE social_approvals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content_id INTEGER NOT NULL,
    client_workspace_id TEXT,
    requester_id INTEGER NOT NULL,
    approver_ids TEXT NOT NULL DEFAULT '[]',
    status TEXT NOT NULL DEFAULT 'pending', -- pending, approved, rejected, withdrawn
    version_locked INTEGER NOT NULL DEFAULT 1,
    final_version INTEGER NOT NULL DEFAULT 0,
    final_script TEXT NOT NULL DEFAULT '',
    final_caption TEXT NOT NULL DEFAULT '',
    final_cta TEXT NOT NULL DEFAULT '',
    final_hashtags TEXT NOT NULL DEFAULT '[]',
    final_media_url TEXT NOT NULL DEFAULT '',
    approval_note TEXT NOT NULL DEFAULT '',
    approved_at TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (content_id) REFERENCES social_content_items(id) ON DELETE CASCADE
)
```

### `social_brand_assets`
| cid | Column Name | Type | Not Null | Default Value | Primary Key |
|-----|-------------|------|----------|---------------|-------------|
| 0 | `id` | INTEGER | 0 | None | 1 |
| 1 | `brand_id` | INTEGER | 1 | None | 0 |
| 2 | `filename` | TEXT | 1 | None | 0 |
| 3 | `file_type` | TEXT | 1 | 'image' | 0 |
| 4 | `file_size` | INTEGER | 1 | 0 | 0 |
| 5 | `checksum` | TEXT | 1 | '' | 0 |
| 6 | `content_type` | TEXT | 1 | 'image/png' | 0 |
| 7 | `created_at` | TEXT | 1 | datetime('now') | 0 |

```sql
CREATE TABLE social_brand_assets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    brand_id INTEGER NOT NULL,
    filename TEXT NOT NULL,
    file_type TEXT NOT NULL DEFAULT 'image',
    file_size INTEGER NOT NULL DEFAULT 0,
    checksum TEXT NOT NULL DEFAULT '',
    content_type TEXT NOT NULL DEFAULT 'image/png',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (brand_id) REFERENCES social_brand_profiles(id) ON DELETE CASCADE
)
```

### `social_brand_profiles`
| cid | Column Name | Type | Not Null | Default Value | Primary Key |
|-----|-------------|------|----------|---------------|-------------|
| 0 | `id` | INTEGER | 0 | None | 1 |
| 1 | `workspace_id` | TEXT | 1 | None | 0 |
| 2 | `client_workspace_id` | TEXT | 0 | None | 0 |
| 3 | `business_name` | TEXT | 1 | '' | 0 |
| 4 | `brand_voice` | TEXT | 1 | '' | 0 |
| 5 | `tone` | TEXT | 1 | '' | 0 |
| 6 | `brand_colors` | TEXT | 1 | '{}' | 0 |
| 7 | `brand_logo_url` | TEXT | 1 | '' | 0 |
| 8 | `service_locations` | TEXT | 1 | '[]' | 0 |
| 9 | `created_at` | TEXT | 1 | datetime('now') | 0 |

```sql
CREATE TABLE social_brand_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workspace_id TEXT NOT NULL,
    client_workspace_id TEXT,
    business_name TEXT NOT NULL DEFAULT '',
    brand_voice TEXT NOT NULL DEFAULT '',
    tone TEXT NOT NULL DEFAULT '',
    brand_colors TEXT NOT NULL DEFAULT '{}',
    brand_logo_url TEXT NOT NULL DEFAULT '',
    service_locations TEXT NOT NULL DEFAULT '[]',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(workspace_id, client_workspace_id),
    FOREIGN KEY (workspace_id) REFERENCES social_workspaces(id) ON DELETE CASCADE,
    FOREIGN KEY (client_workspace_id) REFERENCES social_workspaces(id) ON DELETE SET NULL
)
```

### `social_calendar_entries`
| cid | Column Name | Type | Not Null | Default Value | Primary Key |
|-----|-------------|------|----------|---------------|-------------|
| 0 | `id` | INTEGER | 0 | None | 1 |
| 1 | `workspace_id` | TEXT | 1 | None | 0 |
| 2 | `content_id` | INTEGER | 1 | None | 0 |
| 3 | `platform` | TEXT | 1 | 'instagram' | 0 |
| 4 | `publish_date` | TEXT | 1 | '' | 0 |
| 5 | `publish_time` | TEXT | 1 | '' | 0 |
| 6 | `status` | TEXT | 1 | 'planning' | 0 |
| 7 | `assigned_employee_id` | INTEGER | 0 | None | 0 |
| 8 | `internal_review_at` | TEXT | 0 | None | 0 |
| 9 | `approval_deadline` | TEXT | 0 | None | 0 |
| 10 | `publish_platform_account` | TEXT | 0 | None | 0 |
| 11 | `publish_hook` | TEXT | 1 | '' | 0 |
| 12 | `publish_caption` | TEXT | 1 | '' | 0 |
| 13 | `publish_hashtags` | TEXT | 1 | '[]' | 0 |
| 14 | `publish_media_url` | TEXT | 1 | '' | 0 |
| 15 | `version_locked` | INTEGER | 1 | 0 | 0 |
| 16 | `review_notes` | TEXT | 1 | '' | 0 |
| 17 | `created_at` | TEXT | 1 | datetime('now') | 0 |
| 18 | `updated_at` | TEXT | 1 | datetime('now') | 0 |

```sql
CREATE TABLE social_calendar_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workspace_id TEXT NOT NULL,
    content_id INTEGER NOT NULL,
    platform TEXT NOT NULL DEFAULT 'instagram',
    publish_date TEXT NOT NULL DEFAULT '',
    publish_time TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'planning',
    assigned_employee_id INTEGER,
    internal_review_at TEXT,
    approval_deadline TEXT,
    publish_platform_account TEXT,
    publish_hook TEXT NOT NULL DEFAULT '',
    publish_caption TEXT NOT NULL DEFAULT '',
    publish_hashtags TEXT NOT NULL DEFAULT '[]',
    publish_media_url TEXT NOT NULL DEFAULT '',
    version_locked INTEGER NOT NULL DEFAULT 0,
    review_notes TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (content_id) REFERENCES social_content_items(id) ON DELETE CASCADE
)
```

### `social_campaigns`
| cid | Column Name | Type | Not Null | Default Value | Primary Key |
|-----|-------------|------|----------|---------------|-------------|
| 0 | `id` | INTEGER | 0 | None | 1 |
| 1 | `workspace_id` | TEXT | 1 | None | 0 |
| 2 | `client_workspace_id` | TEXT | 0 | None | 0 |
| 3 | `name` | TEXT | 1 | '' | 0 |
| 4 | `campaign_type` | TEXT | 1 | 'brand' | 0 |
| 5 | `objective` | TEXT | 1 | '' | 0 |
| 6 | `budget_plan` | TEXT | 1 | '{}' | 0 |
| 7 | `start_date` | TEXT | 1 | '' | 0 |
| 8 | `end_date` | TEXT | 1 | '' | 0 |
| 9 | `status` | TEXT | 1 | 'planning' | 0 |
| 10 | `created_at` | TEXT | 1 | datetime('now') | 0 |

```sql
CREATE TABLE social_campaigns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workspace_id TEXT NOT NULL,
    client_workspace_id TEXT,
    name TEXT NOT NULL DEFAULT '',
    campaign_type TEXT NOT NULL DEFAULT 'brand',
    objective TEXT NOT NULL DEFAULT '',
    budget_plan TEXT NOT NULL DEFAULT '{}',
    start_date TEXT NOT NULL DEFAULT '',
    end_date TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'planning',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (workspace_id) REFERENCES social_workspaces(id) ON DELETE CASCADE
)
```

### `social_client_profiles`
| cid | Column Name | Type | Not Null | Default Value | Primary Key |
|-----|-------------|------|----------|---------------|-------------|
| 0 | `id` | INTEGER | 0 | None | 1 |
| 1 | `client_workspace_id` | TEXT | 1 | None | 0 |
| 2 | `company_name` | TEXT | 1 | '' | 0 |
| 3 | `brand_voice` | TEXT | 1 | '' | 0 |
| 4 | `target_audience` | TEXT | 1 | '' | 0 |
| 5 | `service_package` | TEXT | 1 | '' | 0 |
| 6 | `contract_metadata` | TEXT | 1 | '{}' | 0 |
| 7 | `billing_records` | TEXT | 1 | '[]' | 0 |
| 8 | `created_at` | TEXT | 1 | datetime('now') | 0 |

```sql
CREATE TABLE social_client_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_workspace_id TEXT NOT NULL,
    company_name TEXT NOT NULL DEFAULT '',
    brand_voice TEXT NOT NULL DEFAULT '',
    target_audience TEXT NOT NULL DEFAULT '',
    service_package TEXT NOT NULL DEFAULT '',
    contract_metadata TEXT NOT NULL DEFAULT '{}',
    billing_records TEXT NOT NULL DEFAULT '[]',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(client_workspace_id),
    FOREIGN KEY (client_workspace_id) REFERENCES social_workspaces(id) ON DELETE CASCADE
)
```

### `social_comments`
| cid | Column Name | Type | Not Null | Default Value | Primary Key |
|-----|-------------|------|----------|---------------|-------------|
| 0 | `id` | INTEGER | 0 | None | 1 |
| 1 | `account_id` | INTEGER | 1 | None | 0 |
| 2 | `client_workspace_id` | TEXT | 0 | None | 0 |
| 3 | `author` | TEXT | 1 | '' | 0 |
| 4 | `body` | TEXT | 1 | '' | 0 |
| 5 | `sentiment` | TEXT | 1 | 'neutral' | 0 |
| 6 | `is_spam` | INTEGER | 1 | 0 | 0 |
| 7 | `response_draft` | TEXT | 1 | '' | 0 |
| 8 | `response_status` | TEXT | 1 | 'draft' | 0 |
| 9 | `assigned_employee_id` | INTEGER | 0 | None | 0 |
| 10 | `reply_sent_at` | TEXT | 0 | None | 0 |
| 11 | `created_at` | TEXT | 1 | datetime('now') | 0 |

```sql
CREATE TABLE social_comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL,
    client_workspace_id TEXT,
    author TEXT NOT NULL DEFAULT '',
    body TEXT NOT NULL DEFAULT '',
    sentiment TEXT NOT NULL DEFAULT 'neutral',
    is_spam INTEGER NOT NULL DEFAULT 0,
    response_draft TEXT NOT NULL DEFAULT '',
    response_status TEXT NOT NULL DEFAULT 'draft', -- draft, sent, ignored
    assigned_employee_id INTEGER,
    reply_sent_at TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (account_id) REFERENCES social_accounts(id) ON DELETE CASCADE
)
```

### `social_competitor_profiles`
| cid | Column Name | Type | Not Null | Default Value | Primary Key |
|-----|-------------|------|----------|---------------|-------------|
| 0 | `id` | INTEGER | 0 | None | 1 |
| 1 | `workspace_id` | TEXT | 1 | None | 0 |
| 2 | `name` | TEXT | 1 | '' | 0 |
| 3 | `display_name` | TEXT | 1 | '' | 0 |
| 4 | `platform` | TEXT | 1 | 'instagram' | 0 |
| 5 | `account_url` | TEXT | 1 | '' | 0 |
| 6 | `category` | TEXT | 1 | '' | 0 |
| 7 | `followers_fake` | INTEGER | 1 | 0 | 0 |
| 8 | `created_at` | TEXT | 1 | datetime('now') | 0 |

```sql
CREATE TABLE social_competitor_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workspace_id TEXT NOT NULL,
    name TEXT NOT NULL DEFAULT '',
    display_name TEXT NOT NULL DEFAULT '',
    platform TEXT NOT NULL DEFAULT 'instagram',
    account_url TEXT NOT NULL DEFAULT '',
    category TEXT NOT NULL DEFAULT '',
    followers_fake INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (workspace_id) REFERENCES social_workspaces(id) ON DELETE CASCADE
)
```

### `social_content_ideas`
| cid | Column Name | Type | Not Null | Default Value | Primary Key |
|-----|-------------|------|----------|---------------|-------------|
| 0 | `id` | INTEGER | 0 | None | 1 |
| 1 | `workspace_id` | TEXT | 1 | None | 0 |
| 2 | `client_workspace_id` | TEXT | 0 | None | 0 |
| 3 | `pillar` | TEXT | 1 | '' | 0 |
| 4 | `business` | TEXT | 1 | '' | 0 |
| 5 | `platform` | TEXT | 1 | 'instagram' | 0 |
| 6 | `objective` | TEXT | 1 | '' | 0 |
| 7 | `target_audience` | TEXT | 1 | '' | 0 |
| 8 | `journey_stage` | TEXT | 1 | '' | 0 |
| 9 | `content_format` | TEXT | 1 | 'reel' | 0 |
| 10 | `hook` | TEXT | 1 | '' | 0 |
| 11 | `key_message` | TEXT | 1 | '' | 0 |
| 12 | `cta` | TEXT | 1 | '' | 0 |
| 13 | `keywords` | TEXT | 1 | '[]' | 0 |
| 14 | `title` | TEXT | 1 | '' | 0 |
| 15 | `duration_seconds` | REAL | 1 | 0 | 0 |
| 16 | `required_media` | TEXT | 1 | '[]' | 0 |
| 17 | `production_difficulty` | TEXT | 1 | 'medium' | 0 |
| 18 | `expected_outcome` | TEXT | 1 | '' | 0 |
| 19 | `success_metric` | TEXT | 1 | '' | 0 |
| 20 | `priority` | TEXT | 1 | 'medium' | 0 |
| 21 | `status` | TEXT | 1 | 'idea' | 0 |
| 22 | `created_at` | TEXT | 1 | datetime('now') | 0 |
| 23 | `updated_at` | TEXT | 1 | datetime('now') | 0 |

```sql
CREATE TABLE social_content_ideas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workspace_id TEXT NOT NULL,
    client_workspace_id TEXT,
    pillar TEXT NOT NULL DEFAULT '',
    business TEXT NOT NULL DEFAULT '',
    platform TEXT NOT NULL DEFAULT 'instagram',
    objective TEXT NOT NULL DEFAULT '',
    target_audience TEXT NOT NULL DEFAULT '',
    journey_stage TEXT NOT NULL DEFAULT '',
    content_format TEXT NOT NULL DEFAULT 'reel',
    hook TEXT NOT NULL DEFAULT '',
    key_message TEXT NOT NULL DEFAULT '',
    cta TEXT NOT NULL DEFAULT '',
    keywords TEXT NOT NULL DEFAULT '[]',
    title TEXT NOT NULL DEFAULT '',
    duration_seconds REAL NOT NULL DEFAULT 0,
    required_media TEXT NOT NULL DEFAULT '[]',
    production_difficulty TEXT NOT NULL DEFAULT 'medium',
    expected_outcome TEXT NOT NULL DEFAULT '',
    success_metric TEXT NOT NULL DEFAULT '',
    priority TEXT NOT NULL DEFAULT 'medium',
    status TEXT NOT NULL DEFAULT 'idea',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (workspace_id) REFERENCES social_workspaces(id) ON DELETE CASCADE
)
```

### `social_content_items`
| cid | Column Name | Type | Not Null | Default Value | Primary Key |
|-----|-------------|------|----------|---------------|-------------|
| 0 | `id` | INTEGER | 0 | None | 1 |
| 1 | `workspace_id` | TEXT | 1 | None | 0 |
| 2 | `client_workspace_id` | TEXT | 0 | None | 0 |
| 3 | `content_id` | TEXT | 1 | '' | 0 |
| 4 | `pillar` | TEXT | 1 | '' | 0 |
| 5 | `business` | TEXT | 1 | '' | 0 |
| 6 | `platform` | TEXT | 1 | 'instagram' | 0 |
| 7 | `content_format` | TEXT | 1 | 'reel' | 0 |
| 8 | `objective` | TEXT | 1 | '' | 0 |
| 9 | `target_audience` | TEXT | 1 | '' | 0 |
| 10 | `journey_stage` | TEXT | 1 | '' | 0 |
| 11 | `hook` | TEXT | 1 | '' | 0 |
| 12 | `key_message` | TEXT | 1 | '' | 0 |
| 13 | `cta` | TEXT | 1 | '' | 0 |
| 14 | `keywords` | TEXT | 1 | '[]' | 0 |
| 15 | `required_media` | TEXT | 1 | '[]' | 0 |
| 16 | `title` | TEXT | 1 | '' | 0 |
| 17 | `duration_seconds` | REAL | 1 | 0 | 0 |
| 18 | `script` | TEXT | 1 | '' | 0 |
| 19 | `caption` | TEXT | 1 | '' | 0 |
| 20 | `voiceover_text` | TEXT | 1 | '' | 0 |
| 21 | `subtitle_text` | TEXT | 1 | '' | 0 |
| 22 | `thumbnail_text` | TEXT | 1 | '' | 0 |
| 23 | `on_screen_text` | TEXT | 1 | '[]' | 0 |
| 24 | `visual_direction` | TEXT | 1 | '' | 0 |
| 25 | `production_difficulty` | TEXT | 1 | 'medium' | 0 |
| 26 | `priority` | TEXT | 1 | 'medium' | 0 |
| 27 | `expected_outcome` | TEXT | 1 | '' | 0 |
| 28 | `success_metric` | TEXT | 1 | '' | 0 |
| 29 | `assigned_employee_id` | INTEGER | 0 | None | 0 |
| 30 | `calendar_version` | INTEGER | 1 | 1 | 0 |
| 31 | `status` | TEXT | 1 | 'draft' | 0 |
| 32 | `created_at` | TEXT | 1 | datetime('now') | 0 |
| 33 | `updated_at` | TEXT | 1 | datetime('now') | 0 |

```sql
CREATE TABLE social_content_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workspace_id TEXT NOT NULL,
    client_workspace_id TEXT,
    content_id TEXT NOT NULL DEFAULT '',
    pillar TEXT NOT NULL DEFAULT '',
    business TEXT NOT NULL DEFAULT '',
    platform TEXT NOT NULL DEFAULT 'instagram',
    content_format TEXT NOT NULL DEFAULT 'reel',
    objective TEXT NOT NULL DEFAULT '',
    target_audience TEXT NOT NULL DEFAULT '',
    journey_stage TEXT NOT NULL DEFAULT '',
    hook TEXT NOT NULL DEFAULT '',
    key_message TEXT NOT NULL DEFAULT '',
    cta TEXT NOT NULL DEFAULT '',
    keywords TEXT NOT NULL DEFAULT '[]',
    required_media TEXT NOT NULL DEFAULT '[]',
    title TEXT NOT NULL DEFAULT '',
    duration_seconds REAL NOT NULL DEFAULT 0,
    script TEXT NOT NULL DEFAULT '',
    caption TEXT NOT NULL DEFAULT '',
    voiceover_text TEXT NOT NULL DEFAULT '',
    subtitle_text TEXT NOT NULL DEFAULT '',
    thumbnail_text TEXT NOT NULL DEFAULT '',
    on_screen_text TEXT NOT NULL DEFAULT '[]',
    visual_direction TEXT NOT NULL DEFAULT '',
    production_difficulty TEXT NOT NULL DEFAULT 'medium',
    priority TEXT NOT NULL DEFAULT 'medium',
    expected_outcome TEXT NOT NULL DEFAULT '',
    success_metric TEXT NOT NULL DEFAULT '',
    assigned_employee_id INTEGER,
    calendar_version INTEGER NOT NULL DEFAULT 1,
    status TEXT NOT NULL DEFAULT 'draft',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (workspace_id) REFERENCES social_workspaces(id) ON DELETE CASCADE,
    FOREIGN KEY (client_workspace_id) REFERENCES social_workspaces(id) ON DELETE SET NULL
)
```

### `social_content_versions`
| cid | Column Name | Type | Not Null | Default Value | Primary Key |
|-----|-------------|------|----------|---------------|-------------|
| 0 | `id` | INTEGER | 0 | None | 1 |
| 1 | `content_id` | INTEGER | 1 | None | 0 |
| 2 | `version` | INTEGER | 1 | 1 | 0 |
| 3 | `workflow_state` | TEXT | 1 | 'idea' | 0 |
| 4 | `script` | TEXT | 1 | '' | 0 |
| 5 | `caption` | TEXT | 1 | '' | 0 |
| 6 | `cta` | TEXT | 1 | '' | 0 |
| 7 | `keywords` | TEXT | 1 | '[]' | 0 |
| 8 | `thumbnail_text` | TEXT | 1 | '' | 0 |
| 9 | `status` | TEXT | 1 | 'idea' | 0 |
| 10 | `version_note` | TEXT | 1 | '' | 0 |
| 11 | `created_at` | TEXT | 1 | datetime('now') | 0 |

```sql
CREATE TABLE social_content_versions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content_id INTEGER NOT NULL,
    version INTEGER NOT NULL DEFAULT 1,
    workflow_state TEXT NOT NULL DEFAULT 'idea',
    script TEXT NOT NULL DEFAULT '',
    caption TEXT NOT NULL DEFAULT '',
    cta TEXT NOT NULL DEFAULT '',
    keywords TEXT NOT NULL DEFAULT '[]',
    thumbnail_text TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'idea',
    version_note TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (content_id) REFERENCES social_content_items(id) ON DELETE CASCADE
)
```

### `social_employee_kpis`
| cid | Column Name | Type | Not Null | Default Value | Primary Key |
|-----|-------------|------|----------|---------------|-------------|
| 0 | `id` | INTEGER | 0 | None | 1 |
| 1 | `workspace_id` | TEXT | 1 | None | 0 |
| 2 | `employee_id` | TEXT | 1 | None | 0 |
| 3 | `role_code` | TEXT | 1 | 'content_creator' | 0 |
| 4 | `video_assigned` | INTEGER | 1 | 0 | 0 |
| 5 | `videos_delivered` | INTEGER | 1 | 0 | 0 |
| 6 | `videos_on_time` | INTEGER | 1 | 0 | 0 |
| 7 | `revision_count` | INTEGER | 1 | 0 | 0 |
| 8 | `quality_score` | REAL | 1 | 0.0 | 0 |
| 9 | `brand_compliance` | INTEGER | 1 | 0 | 0 |
| 10 | `designs_assigned` | INTEGER | 1 | 0 | 0 |
| 11 | `designs_completed` | INTEGER | 1 | 0 | 0 |
| 12 | `revision_rate` | REAL | 1 | 0.0 | 0 |
| 13 | `scripts_assigned` | INTEGER | 1 | 0 | 0 |
| 14 | `captions_assigned` | INTEGER | 1 | 0 | 0 |
| 15 | `accuracy` | REAL | 1 | 0.0 | 0 |
| 16 | `approval_rate` | REAL | 1 | 0.0 | 0 |
| 17 | `calendar_completion` | INTEGER | 1 | 0 | 0 |
| 18 | `account_health` | INTEGER | 1 | 0 | 0 |
| 19 | `enquiry_response` | REAL | 1 | 0.0 | 0 |
| 20 | `follow_ups_completed` | INTEGER | 1 | 0 | 0 |
| 21 | `qualified_leads` | INTEGER | 1 | 0 | 0 |
| 22 | `conversion_rate` | REAL | 1 | 0.0 | 0 |
| 23 | `revenue` | REAL | 1 | 0.0 | 0 |
| 24 | `week` | TEXT | 1 | '' | 0 |
| 25 | `month` | TEXT | 1 | '' | 0 |
| 26 | `computed_at` | TEXT | 1 | datetime('now') | 0 |
| 27 | `notes` | TEXT | 1 | '' | 0 |

```sql
CREATE TABLE social_employee_kpis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workspace_id TEXT NOT NULL,
    employee_id TEXT NOT NULL,
    role_code TEXT NOT NULL DEFAULT 'content_creator',
    video_assigned INTEGER NOT NULL DEFAULT 0,
    videos_delivered INTEGER NOT NULL DEFAULT 0,
    videos_on_time INTEGER NOT NULL DEFAULT 0,
    revision_count INTEGER NOT NULL DEFAULT 0,
    quality_score REAL NOT NULL DEFAULT 0.0,
    brand_compliance INTEGER NOT NULL DEFAULT 0,
    designs_assigned INTEGER NOT NULL DEFAULT 0,
    designs_completed INTEGER NOT NULL DEFAULT 0,
    revision_rate REAL NOT NULL DEFAULT 0.0,
    scripts_assigned INTEGER NOT NULL DEFAULT 0,
    captions_assigned INTEGER NOT NULL DEFAULT 0,
    accuracy REAL NOT NULL DEFAULT 0.0,
    approval_rate REAL NOT NULL DEFAULT 0.0,
    calendar_completion INTEGER NOT NULL DEFAULT 0,
    account_health INTEGER NOT NULL DEFAULT 0,
    enquiry_response REAL NOT NULL DEFAULT 0.0,
    follow_ups_completed INTEGER NOT NULL DEFAULT 0,
    qualified_leads INTEGER NOT NULL DEFAULT 0,
    conversion_rate REAL NOT NULL DEFAULT 0.0,
    revenue REAL NOT NULL DEFAULT 0.0,
    week TEXT NOT NULL DEFAULT '',
    month TEXT NOT NULL DEFAULT '',
    computed_at TEXT NOT NULL DEFAULT (datetime('now')),
    notes TEXT NOT NULL DEFAULT '',
    FOREIGN KEY (workspace_id) REFERENCES social_workspaces(id) ON DELETE CASCADE
)
```

### `social_integration_logs`
| cid | Column Name | Type | Not Null | Default Value | Primary Key |
|-----|-------------|------|----------|---------------|-------------|
| 0 | `id` | INTEGER | 0 | None | 1 |
| 1 | `service` | TEXT | 1 | '' | 0 |
| 2 | `operation` | TEXT | 1 | '' | 0 |
| 3 | `status` | TEXT | 1 | 'ok' | 0 |
| 4 | `detail` | TEXT | 1 | '' | 0 |
| 5 | `error` | TEXT | 0 | None | 0 |
| 6 | `started_at` | TEXT | 1 | datetime('now') | 0 |
| 7 | `finished_at` | TEXT | 0 | None | 0 |

```sql
CREATE TABLE social_integration_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    service TEXT NOT NULL DEFAULT '',
    operation TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'ok',
    detail TEXT NOT NULL DEFAULT '',
    error TEXT,
    started_at TEXT NOT NULL DEFAULT (datetime('now')),
    finished_at TEXT
)
```

### `social_lead_attribution`
| cid | Column Name | Type | Not Null | Default Value | Primary Key |
|-----|-------------|------|----------|---------------|-------------|
| 0 | `id` | INTEGER | 0 | None | 1 |
| 1 | `lead_id` | INTEGER | 1 | None | 0 |
| 2 | `source_event` | TEXT | 1 | '' | 0 |
| 3 | `attribution_details` | TEXT | 1 | '{}' | 0 |
| 4 | `captured_at` | TEXT | 1 | datetime('now') | 0 |

```sql
CREATE TABLE social_lead_attribution (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lead_id INTEGER NOT NULL,
    source_event TEXT NOT NULL DEFAULT '',
    attribution_details TEXT NOT NULL DEFAULT '{}',
    captured_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (lead_id) REFERENCES social_leads(id) ON DELETE CASCADE
)
```

### `social_leads`
| cid | Column Name | Type | Not Null | Default Value | Primary Key |
|-----|-------------|------|----------|---------------|-------------|
| 0 | `id` | INTEGER | 0 | None | 1 |
| 1 | `workspace_id` | TEXT | 1 | None | 0 |
| 2 | `client_workspace_id` | TEXT | 0 | None | 0 |
| 3 | `lead_name` | TEXT | 1 | '' | 0 |
| 4 | `company` | TEXT | 1 | '' | 0 |
| 5 | `phone` | TEXT | 1 | '' | 0 |
| 6 | `email` | TEXT | 1 | '' | 0 |
| 7 | `location` | TEXT | 1 | '' | 0 |
| 8 | `platform` | TEXT | 1 | 'instagram' | 0 |
| 9 | `source_post` | TEXT | 1 | '' | 0 |
| 10 | `enquiry_text` | TEXT | 1 | '' | 0 |
| 11 | `service_interest` | TEXT | 1 | '' | 0 |
| 12 | `lead_priority` | TEXT | 1 | 'medium' | 0 |
| 13 | `assigned_employee_id` | INTEGER | 0 | None | 0 |
| 14 | `follow_up_date` | TEXT | 0 | None | 0 |
| 15 | `lead_status` | TEXT | 1 | 'new' | 0 |
| 16 | `quotation_status` | TEXT | 1 | 'none' | 0 |
| 17 | `conversion_status` | TEXT | 1 | 'none' | 0 |
| 18 | `created_at` | TEXT | 1 | datetime('now') | 0 |
| 19 | `updated_at` | TEXT | 1 | datetime('now') | 0 |

```sql
CREATE TABLE social_leads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workspace_id TEXT NOT NULL,
    client_workspace_id TEXT,
    lead_name TEXT NOT NULL DEFAULT '',
    company TEXT NOT NULL DEFAULT '',
    phone TEXT NOT NULL DEFAULT '',
    email TEXT NOT NULL DEFAULT '',
    location TEXT NOT NULL DEFAULT '',
    platform TEXT NOT NULL DEFAULT 'instagram',
    source_post TEXT NOT NULL DEFAULT '',
    enquiry_text TEXT NOT NULL DEFAULT '',
    service_interest TEXT NOT NULL DEFAULT '',
    lead_priority TEXT NOT NULL DEFAULT 'medium',
    assigned_employee_id INTEGER,
    follow_up_date TEXT,
    lead_status TEXT NOT NULL DEFAULT 'new', -- new, qualified, in_progress, won, lost
    quotation_status TEXT NOT NULL DEFAULT 'none',
    conversion_status TEXT NOT NULL DEFAULT 'none',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (workspace_id) REFERENCES social_workspaces(id) ON DELETE CASCADE,
    FOREIGN KEY (client_workspace_id) REFERENCES social_workspaces(id) ON DELETE SET NULL
)
```

### `social_media_assets`
| cid | Column Name | Type | Not Null | Default Value | Primary Key |
|-----|-------------|------|----------|---------------|-------------|
| 0 | `id` | INTEGER | 0 | None | 1 |
| 1 | `workspace_id` | TEXT | 1 | None | 0 |
| 2 | `filename` | TEXT | 1 | None | 0 |
| 3 | `file_type` | TEXT | 1 | 'video' | 0 |
| 4 | `content_type` | TEXT | 1 | 'video/mp4' | 0 |
| 5 | `duration_seconds` | REAL | 1 | 0 | 0 |
| 6 | `resolution` | TEXT | 1 | '' | 0 |
| 7 | `frame_rate` | TEXT | 1 | '' | 0 |
| 8 | `has_audio` | INTEGER | 1 | 0 | 0 |
| 9 | `checksum` | TEXT | 1 | '' | 0 |
| 10 | `thumb_url` | TEXT | 1 | '' | 0 |
| 11 | `status` | TEXT | 1 | 'pending' | 0 |
| 12 | `created_at` | TEXT | 1 | datetime('now') | 0 |

```sql
CREATE TABLE social_media_assets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workspace_id TEXT NOT NULL,
    filename TEXT NOT NULL,
    file_type TEXT NOT NULL DEFAULT 'video',
    content_type TEXT NOT NULL DEFAULT 'video/mp4',
    duration_seconds REAL NOT NULL DEFAULT 0,
    resolution TEXT NOT NULL DEFAULT '',
    frame_rate TEXT NOT NULL DEFAULT '',
    has_audio INTEGER NOT NULL DEFAULT 0,
    checksum TEXT NOT NULL DEFAULT '',
    thumb_url TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (workspace_id) REFERENCES social_workspaces(id) ON DELETE CASCADE
)
```

### `social_messages`
| cid | Column Name | Type | Not Null | Default Value | Primary Key |
|-----|-------------|------|----------|---------------|-------------|
| 0 | `id` | INTEGER | 0 | None | 1 |
| 1 | `account_id` | INTEGER | 1 | None | 0 |
| 2 | `client_workspace_id` | TEXT | 0 | None | 0 |
| 3 | `author` | TEXT | 1 | '' | 0 |
| 4 | `body` | TEXT | 1 | '' | 0 |
| 5 | `channel` | TEXT | 1 | 'comment' | 0 |
| 6 | `sentiment` | TEXT | 1 | 'neutral' | 0 |
| 7 | `intent_class` | TEXT | 1 | '' | 0 |
| 8 | `response_draft` | TEXT | 1 | '' | 0 |
| 9 | `response_status` | TEXT | 1 | 'draft' | 0 |
| 10 | `assigned_employee_id` | INTEGER | 0 | None | 0 |
| 11 | `reply_sent_at` | TEXT | 0 | None | 0 |
| 12 | `created_at` | TEXT | 1 | datetime('now') | 0 |

```sql
CREATE TABLE social_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL,
    client_workspace_id TEXT,
    author TEXT NOT NULL DEFAULT '',
    body TEXT NOT NULL DEFAULT '',
    channel TEXT NOT NULL DEFAULT 'comment',
    sentiment TEXT NOT NULL DEFAULT 'neutral',
    intent_class TEXT NOT NULL DEFAULT '',
    response_draft TEXT NOT NULL DEFAULT '',
    response_status TEXT NOT NULL DEFAULT 'draft',
    assigned_employee_id INTEGER,
    reply_sent_at TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (account_id) REFERENCES social_accounts(id) ON DELETE CASCADE
)
```

### `social_notifications`
| cid | Column Name | Type | Not Null | Default Value | Primary Key |
|-----|-------------|------|----------|---------------|-------------|
| 0 | `id` | INTEGER | 0 | None | 1 |
| 1 | `channel` | TEXT | 1 | 'internal' | 0 |
| 2 | `kind` | TEXT | 1 | '' | 0 |
| 3 | `severity` | TEXT | 1 | 'info' | 0 |
| 4 | `message` | TEXT | 1 | '' | 0 |
| 5 | `payload` | TEXT | 1 | '{}' | 0 |
| 6 | `read_by` | INTEGER | 0 | None | 0 |
| 7 | `created_at` | TEXT | 1 | datetime('now') | 0 |

```sql
CREATE TABLE social_notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    channel TEXT NOT NULL DEFAULT 'internal',
    kind TEXT NOT NULL DEFAULT '',
    severity TEXT NOT NULL DEFAULT 'info',
    message TEXT NOT NULL DEFAULT '',
    payload TEXT NOT NULL DEFAULT '{}',
    read_by INTEGER,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
)
```

### `social_publish_jobs`
| cid | Column Name | Type | Not Null | Default Value | Primary Key |
|-----|-------------|------|----------|---------------|-------------|
| 0 | `id` | INTEGER | 0 | None | 1 |
| 1 | `workspace_id` | TEXT | 1 | None | 0 |
| 2 | `content_id` | INTEGER | 1 | None | 0 |
| 3 | `version` | INTEGER | 1 | 1 | 0 |
| 4 | `account_id` | INTEGER | 0 | None | 0 |
| 5 | `client_workspace_id` | TEXT | 0 | None | 0 |
| 6 | `platform` | TEXT | 1 | 'instagram' | 0 |
| 7 | `publish_at` | TEXT | 1 | '' | 0 |
| 8 | `status` | TEXT | 1 | 'scheduled' | 0 |
| 9 | `job_url` | TEXT | 1 | '' | 0 |
| 10 | `output_url` | TEXT | 1 | '' | 0 |
| 11 | `platform_response` | TEXT | 1 | '{}' | 0 |
| 12 | `error` | TEXT | 0 | None | 0 |
| 13 | `retry_count` | INTEGER | 1 | 0 | 0 |
| 14 | `last_attempt_at` | TEXT | 0 | None | 0 |
| 15 | `created_at` | TEXT | 1 | datetime('now') | 0 |
| 16 | `updated_at` | TEXT | 1 | datetime('now') | 0 |

```sql
CREATE TABLE social_publish_jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workspace_id TEXT NOT NULL,
    content_id INTEGER NOT NULL,
    version INTEGER NOT NULL DEFAULT 1,
    account_id INTEGER,
    client_workspace_id TEXT,
    platform TEXT NOT NULL DEFAULT 'instagram',
    publish_at TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'scheduled', -- scheduled, published, failed, reconciled
    job_url TEXT NOT NULL DEFAULT '',
    output_url TEXT NOT NULL DEFAULT '',
    platform_response TEXT NOT NULL DEFAULT '{}',
    error TEXT,
    retry_count INTEGER NOT NULL DEFAULT 0,
    last_attempt_at TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (content_id) REFERENCES social_content_items(id) ON DELETE CASCADE,
    FOREIGN KEY (account_id) REFERENCES social_accounts(id) ON DELETE SET NULL
)
```

### `social_published_posts`
| cid | Column Name | Type | Not Null | Default Value | Primary Key |
|-----|-------------|------|----------|---------------|-------------|
| 0 | `id` | INTEGER | 0 | None | 1 |
| 1 | `workspace_id` | TEXT | 1 | None | 0 |
| 2 | `account_id` | INTEGER | 1 | None | 0 |
| 3 | `platform` | TEXT | 1 | 'instagram' | 0 |
| 4 | `client_workspace_id` | TEXT | 0 | None | 0 |
| 5 | `status` | TEXT | 1 | 'published' | 0 |
| 6 | `post_url` | TEXT | 1 | '' | 0 |
| 7 | `platform_post_id` | TEXT | 1 | '' | 0 |
| 8 | `platform_status` | TEXT | 1 | 'live' | 0 |
| 9 | `performance_summary` | TEXT | 1 | '{}' | 0 |
| 10 | `published_at` | TEXT | 0 | None | 0 |
| 11 | `created_at` | TEXT | 1 | datetime('now') | 0 |

```sql
CREATE TABLE social_published_posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workspace_id TEXT NOT NULL,
    account_id INTEGER NOT NULL,
    platform TEXT NOT NULL DEFAULT 'instagram',
    client_workspace_id TEXT,
    status TEXT NOT NULL DEFAULT 'published',
    post_url TEXT NOT NULL DEFAULT '',
    platform_post_id TEXT NOT NULL DEFAULT '',
    platform_status TEXT NOT NULL DEFAULT 'live',
    performance_summary TEXT NOT NULL DEFAULT '{}',
    published_at TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (account_id) REFERENCES social_accounts(id) ON DELETE CASCADE
)
```

### `social_reports`
| cid | Column Name | Type | Not Null | Default Value | Primary Key |
|-----|-------------|------|----------|---------------|-------------|
| 0 | `id` | INTEGER | 0 | None | 1 |
| 1 | `report_type` | TEXT | 1 | 'weekly' | 0 |
| 2 | `report_period` | TEXT | 1 | '' | 0 |
| 3 | `workspace_id` | TEXT | 1 | None | 0 |
| 4 | `client_workspace_id` | TEXT | 0 | None | 0 |
| 5 | `summary` | TEXT | 1 | '{}' | 0 |
| 6 | `raw_metrics` | TEXT | 1 | '{}' | 0 |
| 7 | `generated_at` | TEXT | 1 | datetime('now') | 0 |
| 8 | `author_id` | INTEGER | 0 | None | 0 |

```sql
CREATE TABLE social_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_type TEXT NOT NULL DEFAULT 'weekly',
    report_period TEXT NOT NULL DEFAULT '',
    workspace_id TEXT NOT NULL,
    client_workspace_id TEXT,
    summary TEXT NOT NULL DEFAULT '{}',
    raw_metrics TEXT NOT NULL DEFAULT '{}',
    generated_at TEXT NOT NULL DEFAULT (datetime('now')),
    author_id INTEGER,
    FOREIGN KEY (workspace_id) REFERENCES social_workspaces(id) ON DELETE CASCADE
)
```

### `social_scripts`
| cid | Column Name | Type | Not Null | Default Value | Primary Key |
|-----|-------------|------|----------|---------------|-------------|
| 0 | `id` | INTEGER | 0 | None | 1 |
| 1 | `content_id` | INTEGER | 1 | None | 0 |
| 2 | `language` | TEXT | 1 | 'en' | 0 |
| 3 | `script` | TEXT | 1 | '' | 0 |
| 4 | `voiceover_text` | TEXT | 1 | '' | 0 |
| 5 | `subtitle_text` | TEXT | 1 | '' | 0 |
| 6 | `on_screen_text` | TEXT | 1 | '[]' | 0 |
| 7 | `conversation_style` | TEXT | 1 | 'professional' | 0 |
| 8 | `created_at` | TEXT | 1 | datetime('now') | 0 |

```sql
CREATE TABLE social_scripts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content_id INTEGER NOT NULL,
    language TEXT NOT NULL DEFAULT 'en',
    script TEXT NOT NULL DEFAULT '',
    voiceover_text TEXT NOT NULL DEFAULT '',
    subtitle_text TEXT NOT NULL DEFAULT '',
    on_screen_text TEXT NOT NULL DEFAULT '[]',
    conversation_style TEXT NOT NULL DEFAULT 'professional',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (content_id) REFERENCES social_content_items(id) ON DELETE CASCADE
)
```

### `social_subtitles`
| cid | Column Name | Type | Not Null | Default Value | Primary Key |
|-----|-------------|------|----------|---------------|-------------|
| 0 | `id` | INTEGER | 0 | None | 1 |
| 1 | `video_job_id` | INTEGER | 1 | None | 0 |
| 2 | `language` | TEXT | 1 | 'en' | 0 |
| 3 | `srt_text` | TEXT | 1 | '' | 0 |
| 4 | `status` | TEXT | 1 | 'pending' | 0 |
| 5 | `started_at` | TEXT | 0 | None | 0 |
| 6 | `completed_at` | TEXT | 0 | None | 0 |

```sql
CREATE TABLE social_subtitles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    video_job_id INTEGER NOT NULL,
    language TEXT NOT NULL DEFAULT 'en',
    srt_text TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'pending',
    started_at TEXT,
    completed_at TEXT,
    FOREIGN KEY (video_job_id) REFERENCES social_video_jobs(id) ON DELETE CASCADE
)
```

### `social_tasks`
| cid | Column Name | Type | Not Null | Default Value | Primary Key |
|-----|-------------|------|----------|---------------|-------------|
| 0 | `id` | INTEGER | 0 | None | 1 |
| 1 | `workspace_id` | TEXT | 1 | None | 0 |
| 2 | `content_id` | INTEGER | 1 | None | 0 |
| 3 | `employee_id` | INTEGER | 0 | None | 0 |
| 4 | `due_date` | TEXT | 1 | '' | 0 |
| 5 | `status` | TEXT | 1 | 'open' | 0 |
| 6 | `priority` | TEXT | 1 | 'medium' | 0 |
| 7 | `assignee_notes` | TEXT | 1 | '' | 0 |
| 8 | `created_at` | TEXT | 1 | datetime('now') | 0 |
| 9 | `updated_at` | TEXT | 1 | datetime('now') | 0 |

```sql
CREATE TABLE social_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workspace_id TEXT NOT NULL,
    content_id INTEGER NOT NULL,
    employee_id INTEGER,
    due_date TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'open', -- open, in_progress, done, blocked
    priority TEXT NOT NULL DEFAULT 'medium',
    assignee_notes TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (content_id) REFERENCES social_content_items(id) ON DELETE CASCADE,
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE SET NULL
)
```

### `social_thumbnails`
| cid | Column Name | Type | Not Null | Default Value | Primary Key |
|-----|-------------|------|----------|---------------|-------------|
| 0 | `id` | INTEGER | 0 | None | 1 |
| 1 | `asset_id` | INTEGER | 1 | None | 0 |
| 2 | `filename` | TEXT | 1 | '' | 0 |
| 3 | `thumbnail_url` | TEXT | 1 | '' | 0 |
| 4 | `created_at` | TEXT | 1 | datetime('now') | 0 |

```sql
CREATE TABLE social_thumbnails (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_id INTEGER NOT NULL,
    filename TEXT NOT NULL DEFAULT '',
    thumbnail_url TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (asset_id) REFERENCES social_media_assets(id) ON DELETE CASCADE
)
```

### `social_trends`
| cid | Column Name | Type | Not Null | Default Value | Primary Key |
|-----|-------------|------|----------|---------------|-------------|
| 0 | `id` | INTEGER | 0 | None | 1 |
| 1 | `workspace_id` | TEXT | 1 | None | 0 |
| 2 | `trend_title` | TEXT | 1 | None | 0 |
| 3 | `source` | TEXT | 1 | '' | 0 |
| 4 | `discovery_date` | TEXT | 1 | None | 0 |
| 5 | `relevance` | TEXT | 1 | 'medium' | 0 |
| 6 | `audience_relevance` | TEXT | 1 | 'medium' | 0 |
| 7 | `content_potential` | TEXT | 1 | 'medium' | 0 |
| 8 | `freshness` | TEXT | 1 | 'high' | 0 |
| 9 | `platform` | TEXT | 1 | 'instagram' | 0 |
| 10 | `suggested_hook` | TEXT | 1 | '' | 0 |
| 11 | `suggested_script` | TEXT | 1 | '' | 0 |
| 12 | `suggested_audio` | TEXT | 1 | '' | 0 |
| 13 | `audio_permission` | TEXT | 1 | 'none' | 0 |
| 14 | `content_opportunity` | TEXT | 1 | '' | 0 |
| 15 | `priority` | TEXT | 1 | 'medium' | 0 |
| 16 | `expiry_date` | TEXT | 0 | None | 0 |
| 17 | `reviewed_by` | TEXT | 0 | None | 0 |
| 18 | `created_at` | TEXT | 1 | datetime('now') | 0 |

```sql
CREATE TABLE social_trends (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workspace_id TEXT NOT NULL,
    trend_title TEXT NOT NULL,
    source TEXT NOT NULL DEFAULT '',
    discovery_date TEXT NOT NULL,
    relevance TEXT NOT NULL DEFAULT 'medium',
    audience_relevance TEXT NOT NULL DEFAULT 'medium',
    content_potential TEXT NOT NULL DEFAULT 'medium',
    freshness TEXT NOT NULL DEFAULT 'high',
    platform TEXT NOT NULL DEFAULT 'instagram',
    suggested_hook TEXT NOT NULL DEFAULT '',
    suggested_script TEXT NOT NULL DEFAULT '',
    suggested_audio TEXT NOT NULL DEFAULT '',
    audio_permission TEXT NOT NULL DEFAULT 'none',
    content_opportunity TEXT NOT NULL DEFAULT '',
    priority TEXT NOT NULL DEFAULT 'medium',
    expiry_date TEXT,
    reviewed_by TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (workspace_id) REFERENCES social_workspaces(id) ON DELETE CASCADE
)
```

### `social_video_jobs`
| cid | Column Name | Type | Not Null | Default Value | Primary Key |
|-----|-------------|------|----------|---------------|-------------|
| 0 | `id` | INTEGER | 0 | None | 1 |
| 1 | `workspace_id` | TEXT | 1 | None | 0 |
| 2 | `account_id` | INTEGER | 0 | None | 0 |
| 3 | `input_asset_id` | INTEGER | 1 | None | 0 |
| 4 | `output_asset_id` | INTEGER | 0 | None | 0 |
| 5 | `status` | TEXT | 1 | 'queued' | 0 |
| 6 | `script_id` | INTEGER | 0 | None | 0 |
| 7 | `language` | TEXT | 1 | 'en' | 0 |
| 8 | `duration_seconds` | REAL | 0 | None | 0 |
| 9 | `aspect_ratio` | TEXT | 1 | '9:16' | 0 |
| 10 | `status_detail` | TEXT | 1 | '' | 0 |
| 11 | `queue_time` | TEXT | 0 | None | 0 |
| 12 | `started_at` | TEXT | 0 | None | 0 |
| 13 | `processing_time` | TEXT | 0 | None | 0 |
| 14 | `completed_at` | TEXT | 0 | None | 0 |
| 15 | `retry_count` | INTEGER | 1 | 0 | 0 |
| 16 | `created_at` | TEXT | 1 | datetime('now') | 0 |

```sql
CREATE TABLE social_video_jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workspace_id TEXT NOT NULL,
    account_id INTEGER,
    input_asset_id INTEGER NOT NULL,
    output_asset_id INTEGER,
    status TEXT NOT NULL DEFAULT 'queued',
    script_id INTEGER,
    language TEXT NOT NULL DEFAULT 'en',
    duration_seconds REAL,
    aspect_ratio TEXT NOT NULL DEFAULT '9:16',
    status_detail TEXT NOT NULL DEFAULT '',
    queue_time TEXT,
    started_at TEXT,
    processing_time TEXT,
    completed_at TEXT,
    retry_count INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (workspace_id) REFERENCES social_workspaces(id) ON DELETE CASCADE,
    FOREIGN KEY (account_id) REFERENCES social_accounts(id) ON DELETE SET NULL,
    FOREIGN KEY (input_asset_id) REFERENCES social_media_assets(id) ON DELETE CASCADE,
    FOREIGN KEY (output_asset_id) REFERENCES social_media_assets(id) ON DELETE SET NULL
)
```

### `social_workspaces`
| cid | Column Name | Type | Not Null | Default Value | Primary Key |
|-----|-------------|------|----------|---------------|-------------|
| 0 | `id` | TEXT | 0 | None | 1 |
| 1 | `code` | TEXT | 1 | None | 0 |
| 2 | `label` | TEXT | 1 | None | 0 |
| 3 | `is_isolated` | INTEGER | 1 | 1 | 0 |
| 4 | `created_at` | TEXT | 1 | datetime('now') | 0 |

```sql
CREATE TABLE social_workspaces (
    id TEXT PRIMARY KEY,
    code TEXT UNIQUE NOT NULL,
    label TEXT NOT NULL,
    is_isolated INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
)
```

### `sqlite_sequence`
| cid | Column Name | Type | Not Null | Default Value | Primary Key |
|-----|-------------|------|----------|---------------|-------------|
| 0 | `name` |  | 0 | None | 0 |
| 1 | `seq` |  | 0 | None | 0 |

```sql
CREATE TABLE sqlite_sequence(name,seq)
```

### `users`
| cid | Column Name | Type | Not Null | Default Value | Primary Key |
|-----|-------------|------|----------|---------------|-------------|
| 0 | `id` | INTEGER | 0 | None | 1 |
| 1 | `username` | TEXT | 1 | None | 0 |
| 2 | `password_hash` | TEXT | 1 | None | 0 |
| 3 | `name` | TEXT | 1 | None | 0 |
| 4 | `role_id` | INTEGER | 1 | None | 0 |
| 5 | `workspace_id` | TEXT | 0 | None | 0 |
| 6 | `active` | INTEGER | 1 | 1 | 0 |
| 7 | `created_at` | TEXT | 1 | datetime('now') | 0 |

```sql
CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            name TEXT NOT NULL,
            role_id INTEGER NOT NULL,
            workspace_id TEXT,
            active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (role_id) REFERENCES roles(id)
        )
```

### `workspaces`
| cid | Column Name | Type | Not Null | Default Value | Primary Key |
|-----|-------------|------|----------|---------------|-------------|
| 0 | `id` | TEXT | 0 | None | 1 |
| 1 | `code` | TEXT | 1 | None | 0 |
| 2 | `label` | TEXT | 1 | None | 0 |
| 3 | `is_isolated` | INTEGER | 1 | 1 | 0 |
| 4 | `created_at` | TEXT | 1 | datetime('now') | 0 |

```sql
CREATE TABLE workspaces (
            id TEXT PRIMARY KEY,
            code TEXT UNIQUE NOT NULL,
            label TEXT NOT NULL,
            is_isolated INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
```
