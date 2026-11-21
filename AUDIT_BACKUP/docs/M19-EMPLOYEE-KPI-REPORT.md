# M19 Employee KPI Report

## Objective

Compute transparent, evidence-based employee KPIs from the existing M15 (employees) and M19 task/video records. KPI data is synthetic until the live content/leads/video databases are wired.

## KPI profiles defined

- VIDEO EDITOR: videos assigned, delivered, on-time, turnaround, revision count, quality score, brand compliance.
- GRAPHIC DESIGNER: designs assigned/completed, revision rate, quality score, delivery time.
- CONTENT WRITER: scripts, captions, accuracy, originality, approval rate, revisions.
- SOCIAL MEDIA MANAGER: calendar completion, publishing consistency, account health, comment management, enquiry response.
- LEAD MANAGER: assigned leads, contacted, response time, follow-ups, qualified leads, progression.
- SALES EMPLOYEE: qualified leads, quotations, conversion, revenue, follow-up discipline.

## Formula (transparent)

- `quality_score = min(videos_delivered / max(video_assigned, 1), 1.0)`
- `revision_rate = revision_count / max(videos_assigned, 1)`
- Each KPI record is keyed by `(workspace_id, employee_id, week)`
- Data source, last-updated, missing-data indicator and source field are exposed per record.

## Test evidence

| Check | Result |
|---|---|
| KPI record for employee | `employee_id = 2`, `quality_score` present |
| Week key | `2026-W48` |
| Transparent formulas | Implemented (no hidden weights) |

## Constraints

- No reward for spam/artificial engagement.
- Follower growth not used as the sole metric.
- Controllable work separated from platform-dependent outcomes.
- Missing data is surfaced explicitly.
- AI may recommend improvements but cannot impose salary deductions/penalties (no HR finance action).
