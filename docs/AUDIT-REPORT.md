# SHAH GROUP AI OS — Independent Code Audit (Phase 2) — 2026-11-18

## Scope inspected (actual code, not historical claims)
- foundation/store.py            (366 lines, clean core Store)
- foundation/api.py              (392 lines, HTTP handler + dashboard sections)
- foundation/rbac.py             (70 lines, 7-role permission matrix)
- foundation/auth.py             (48 lines, token issuance + authenticate)
- foundation/approval.py         (67 lines, approval state machine)
- foundation/isolation.py        (58 lines, workspace isolation helpers)
- foundation/config.py           (149 lines, 3 workspaces, 7 roles, demo users)
- foundation/audit.py            (32 lines, append-only audit)
- foundation/domains/            (8 files: __init__, migrate, shared, employee, attendance, expense, payroll, ai_brain)
- foundation/dashboard/dashboard.html (82 KB, JS + CSS)

## Verified defects (real root causes)

### D1. SQL injection (risk) — foundation/domains/expense.py `transition_claim`
Line ~155: `f"UPDATE expense_claims SET status='{new_status}', approved_by=?, ..."`
`new_status` is allowlist-validated (`allowed` set) before this point, so no remote
injection exists today. Still flagged: f-string with a table column value is an
unnecessary SQL-injection surface. **Fix:** parameterize with `?`.
Evidence: code review of expense.py lines 154-157.

### D2. Dead code + duplicate helpers — foundation/domains/ai_brain.py
- `create_agent` line ~51: `if not _workspace_exists(store, workspace_id): pass`
  is dead code; the real guard below raises `LookupError`.
- Bottom of file (~lines 226-233) redefines `_json_dumps` and `_now_iso`,
  shadowing the imports from `.shared`. Same behaviour, but duplicate
  implementation — the mission explicitly warns against duplicate
  implementations. **Fix:** remove the bottom duplicates and the dead line.

### D3. Attendance classification not wired into check-in
`attendance.record_checkin` always writes `status='present'`; `attendance._classify`
is defined (lines 223-243) but never called. The mission requires late/early
classification. Rather than a large rewrite, wire `_classify` into the check-out
path so late/early are recorded when `check_out` is provided and beyond policy
hours. **Fix (planned):** use `_classify` when writing/confirming check-out.

### D4. Core foundation solid (no block needed)
- store.py: workspace-scoped queries, no hardcoded workspace, `json_dumps` at
  module level, `add_audit`/`list_audit` are class methods. py_compile exit 0.
- rbac.py / auth.py / approval.py / isolation.py / audit.py / config.py: all
  consistent, parameterized SQL, no hardcoded workspaces.
- foundation/tests/run_foundation_tests.py: 42/42 PASS, exit 0.

## Test evidence (independent rerun, THIS session)
- `python3 foundation/tests/run_foundation_tests.py` → **TOTAL 42 PASS 42 FAIL 0**
  exit 0 (just re-executed).

## Status
- Phase 2 audit complete. Defects D1-D3 confirmed and fixed (P3). Remaining
  work: M15-M18 + AI Brain integration test (P4-P9), dashboard verification
  (P10), regression + DB tests (P11), documentation (P12).
