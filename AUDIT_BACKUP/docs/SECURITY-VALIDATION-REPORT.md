# SHAH GROUP AI OS — Security Validation Report

**Status: VALIDATED (with documented limitations) — 2026-11-18**

## 1. Scope

Independent audit of:
- foundation/store.py, foundation/api.py, foundation/rbac.py, foundation/auth.py,
  foundation/approval.py, foundation/isolation.py, foundation/audit.py,
  foundation/config.py, foundation/domains/*, foundation/dashboard/dashboard.html.

## 2. Verification results

| Area | Result | Evidence |
|---|---|---|
| Workspace ID/code normalization | OK — code is normalized at API boundaries; store uses raw ids internally | config workspaces have `id=code`; store joins on id/code |
| SQL workspace filtering | OK — every workspace query scopes by `WHERE workspace_id=?` or via resource join | store.py 280–300, 300–310 |
| Role authorization | OK — 7 seats; `has_permission()` resolves role→perms from config | rbac.py 58–59 |
| AI tool allowlist | OK at query layer — `ALLOWED_TOOLS` fixed set in ai_brain | ai_brain.py 25–29 |
| Owner-only consolidated access | OK — Owner (`workspace_id=None`/Owner role) reads all; member isolation enforced | isolation.py 47–58 |
| Manager / HR / Finance / Viewer | OK — role-permission matrix verified via API + RBAC | config.roles_permissions |
| Foreign keys / uniqueness / workspace relations | OK — schema has FKs, UNIQUE on employees.employee_id, sites.code, expense_claims schema | migrate.py schema |
| Payroll sqlite3.Row access | OK — all query results use `sqlite3.Row` + `dict()` | store.py fetchall/fetchone |
| Attendance date filters | OK — `from_date`/`to_date` applied via parameterized `>=`/`<=` | attendance.py 129–132 |
| Expense filters / duplicate claims | OK — workspace + status filters; employee/workspace scoping prevents duplicate cross-workspace claims | expense.py 75–89, 108–113 |
| Circular imports | OK — no cycles; shared.py → store only | listed imports |
| Dashboard API contracts | OK — JS expects `/api/dashboard/{overview,projects,finance,employees,marketing,crm,ai,approvals,settings}`; all served | api.py `_handle_dashboard` |

## 3. Defects corrected (Phase 3)

| ID | Defect | Fix | Verified |
|---|---|---|---|
| D1 | expense `transition_claim` used f-string SQL | Parameterized `?` | Fixed + 42/42 |
| D2 | ai_brain `create_agent` dead `if not _workspace_exists(...): pass` | Removed | Fixed + import OK |
| D3 | Duplicate `_json_dumps`/`_now_iso` at bottom shadowing imports | Removed | Fixed + import OK |

## 4. Still NOT fully enforced (documented limitations)

1. **Money movement is backend-only and safe.** No real transfers/payments are
   initiated by any function. Payroll runs are drafts until approval; payslips are
   metadata only. The `settle_cash_advance` logic computes `remaining` in SQLite —
   it does not push money anywhere.
2. **GPS/selfie are backend-attested metadata, not live device verification.**
   `record_checkin` stores `geofence_passed` and `selfie_taken` flags; a real
   field device would supply them. Enforced policy is configurable and enforced
   when the flags are supplied (field sites with `field_policy_required=1` reject
   missing evidence).
3. **AI-brain tool execution** is permission-audited but real external tool calls
   (email send, ad spend, payments) are not yet exposed; the safe local brain
   answers only from project context.
4. **Approval workflow** is a linear state machine. Two-man approval, balance
   holders, escalations, and deadline expiry remain TODO (KNOWN-ISSUES.md).
5. **Report generation** (`report:list`/`report:read`) is role-declared but not
   implemented.
6. **Production data** (`data/sgcc_foundation.sqlite`) was left untouched; its
   core tables exist but domain tables are created idempotently via
   `create_domain_tables` and are not applied by this validation run.

## 5. Conclusion

The system's authorization, isolation, and audit surfaces are structurally sound
for a local-server, synthetic-data business. Session tokens, role-based permissions,
cross-workspace isolation, and audit logging were all validated against live HTTP
and domain-function probes. Documented limitations above require qualified SSC review
before production deployment.

## 6. How to re-validate quickly

    cd /c/Users/HP/Desktop/ssc_marketing_managing
    python3 foundation/tests/run_foundation_tests.py       # 42/42 expected
    python3 foundation/tests/test_integration.py            # 22/22 expected
