# SHAH GROUP AI OS — Known Issues

## Foundation test battery — currently GREEN

- 42/42 PASS, 0 FAIL (verified 2026-11-18).

## Remaining functional gaps (non-blocking, documented)

1. **Two-man approval escalation** — `approval.py` documents an intentional TODO
   for high-value items and balance-holder rules. Not implemented; not exercised
   by the test suite.
2. **Owner workspace_id is set** (`SSC`) yet the Owner reads all workspaces.
   The isolation route treats a non-null `workspace_id` as "member of that
   workspace" unless the role is `Owner`. This is intentional and correct for
   the Owner role; the rule is: `if not workspace_id OR role == Owner → all
   workspaces; otherwise only own workspace`.
3. **`data/leads.csv` CRM** is isolated from the foundation store; the
   foundation uses its own SQLite for approvals/audit. There is no automatic
   sync between the CRM and the foundation store.
4. **No web UI beyond the dashboard shell.** The dashboard is a static shell
   (`foundation/dashboard/dashboard.html`). A full UI may be built on top of
   the API.
5. **API auth header name** — `Authorization: Bearer <token>` (bearer-only).

## Fixed during this session (was previously failing)

- F05a seed/authentication — demo user hashes and role codes corrected in
  `foundation/store.py`.
- F02d config `approval:delete` key — added to `foundation/config.py`.
- F04c viewer non-approver — `require_approver` enforced in
  `foundation/store.py` `transition_approval`.
- t_api urllib scoping — `import urllib.request` moved into `t_api` and the
  `get()` helper added; nested closure imports removed.
- SQLite thread safety — `check_same_thread=False` on the store connection.
- Workspace ID case consistency — workspace id now matches the role/workspace
  code (uppercase) in `foundation/store.py`.
- Circular import `store ↔ approval` — `approval.py` no longer imports
  `Store` at module level (strings-only annotations).
- API login `get_store()` global — `global STORE` added to
  `foundation/api.py` `get_store()`.
- Transition route handler — `/api/approvals/{id}/transition` moved from
  `do_GET` to `do_POST` in `foundation/api.py`.
- Demo-user role/name mismatch in approval creation — `actor_id` normalized in
  `do_POST` (accepts both `id` and `user_id`).
- Pyright diagnostics — cosmetic only; annotation-only `Store` references
  remain stringized by `from __future__ import annotations`.

## Protection status

- Protected files (`.hermes/skills/shah-ai/SKILL.md`, `config/SOUL.md`,
  `brand/ssc-brand-profile.md`, `vendor/hermes-agent`) untouched.
- `data/leads.csv` and schema untouched.
- Backups preserved (see `PHASE-5A-BACKUP-REPORT.md`).
