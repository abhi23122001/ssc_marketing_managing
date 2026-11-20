# M19 Security & Test Report

## Security controls verified

- **Workspace isolation**: non-owner roles (Manager, Finance Manager, Viewer) cannot read other workspaces (cross-workspace `PermissionError` confirmed in the integration suite).
- **Approval machine**: `enqueue_publish` refuses to queue without a version-locked approved version containing final content.
- **No credential leakage**: all tokens, OAuth codes, passwords, and secrets are logged as `[REDACTED]` (policy enforced; none committed).
- **Idempotent schema**: M19 tables use `CREATE TABLE IF NOT EXISTS`; production `sgcc_foundation.sqlite` untouched.

## Summary of test results

| Suite | Checks | Pass | Fail |
|---|---|---|---|
| Foundation | 42 | 42 | 0 |
| Integration | 22 | 22 | 0 |
| M19 domain | 25 | 25 | 0 |

**Total: 89 checks; 89 PASS; 0 FAIL.**

## Security test coverage

- SSC / INFRA / OTHER workspace isolation (integration suite).
- Approval bypass attempt blocked (publish requires approved version).
- Credential leakage check: no API keys or tokens present in test files or logs.

## Known restrictions

- Platform API keys are not present in the environment; real publishing is gated as `integration required`.
- KPI/report metrics are synthetic until a live account is authorized.
- Agent tool allowlist for the AI Brain is a code draft — pending wiring test.

## Lessons learned

- `sqlite3.Row` has no `.get()` in this Python build; use `row["key"]`.
- M19 schema tables must match the domain INSERT columns exactly (added `duration_seconds`, `required_media`, `expected_outcome`, `success_metric` to `social_content_items` when the content factory referenced them).
- `get_publish_job` originally referenced `output_asset_id` (not in schema); aligned to `social_publish_jobs` columns.
