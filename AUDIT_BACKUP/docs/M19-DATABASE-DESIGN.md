# M19 Database Design

## Overview

M19 extends the existing SHAH Group SQLite foundation with a business-isolated social media marketing schema. All M19 tables are created idempotently (`CREATE TABLE IF NOT EXISTS`) and never touch existing user data.

## Workspace Ownership

Every M19 table that stores business data owns a `workspace_id` referencing `social_workspaces.id`. External clients use `client_workspace_id` (finding either in business code, e.g. `client_workspace_id OR workspace_id` for reads required by `enqueue_publish()` with the `get_content_workspace()` helper).

## M19 Tables

| Table | Purpose |
|---|---|
| `social_workspaces` | Business/client workspaces (SSC, INFRA, CLIENT-X, ...). |
| `social_accounts` | Social account registry (platform, account id, connection status, granted permissions, token expiry). |
| `social_account_syncs` | Per-account sync history (status, scope, error). |
| `social_brand_profiles` | Brand kit per business/client. |
| `social_brand_assets` | Brand assets (logo, colours) tied to a brand profile. |
| `social_trends` | Trend research entries with source, freshness, priority. |
| `social_competitor_profiles` | Competitor profile registry. |
| `social_content_ideas` | Draft content ideas (business/project fields). |
| `social_content_items` | Published content items (section, pillar, format, script, caption, cta, version fields). |
| `social_content_versions` | Versioned content snapshots (script, caption, cta, keywords). |
| `social_media_assets` | Uploaded media with checksum, duration, resolution, thumbnail. |
| `social_video_jobs` | Video render jobs (input/output asset, status, retry count, timestamps). |
| `social_subtitles` | Subtitle files per video job. |
| `social_thumbnails` | Thumbnail assets per media. |
| `social_calendar_entries` | Calendar/spread entries (platform, publish date/time, status, assignees). |
| `social_tasks` | Production tasks (content, employee, due date, status). |
| `social_approvals` | Version-locked approvals (final script/caption/cta, approved_at). |
| `social_publish_jobs` | Publishing queue (content, version, account, publish_at, status). |
| `social_published_posts` | Post registry after publishing (platform post id, status, performance summary). |
| `social_comments` / `social_messages` | Comments and message records with sentiment, spam flag, response draft. |
| `social_leads` | Social enquiries (lead status, priority, assignment). |
| `social_lead_attribution` | Lead attribution events. |
| `social_employee_kpis` | Employee KPI records (per week/month). |
| `social_campaigns` | Campaign definitions. |
| `social_reports` | Generated reports (summary, raw metrics). |
| `social_client_profiles` | External client profiles. |
| `social_notifications` | Internal alerts (title, severity, read status). |
| `social_agent_runs` | Agent execution records (tool, permission_ok, status). |
| `social_integration_logs` | Platform integration logs (service, operation, status, error). |

## Key Indexes

`social_accounts(workspace_id)`, `social_accounts(client_workspace_id)`, `social_content_items(workspace_id)`, `social_leads(workspace_id)`, `social_video_jobs(workspace_id)`, `social_approvals(content_id)`, `social_publish_jobs(content_id)`, `social_comments(account_id)`, `social_agent_runs(workspace_id)`.

## Schema Safety

- Idempotent: all tables created with `CREATE TABLE IF NOT EXISTS`.
- No destructive migrations; production `sgcc_foundation.sqlite` is never modified by M19 during validation.
- Foreign keys enforce workspace ownership (`ON DELETE CASCADE/SET NULL`).
- Business isolation: non-owner roles cannot read other workspaces' records (enforced at API and domain level).
