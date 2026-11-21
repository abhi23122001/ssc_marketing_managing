# SHAH GROUP AI OS — Security & Permissions

## Roles and permission matrix

| Role | Approver | Workspace scope | Approve | Comment | Report | AI brain |
|---|---|---|---|---|---|---|
|| Owner | Yes | All (consolidated) | Yes | Yes | Yes | Yes |
|| Manager | Yes | Own | Yes | Yes | Yes | Yes |
| Project Manager | Yes | Own | Yes (comment) | Yes | Yes | No |
| Finance Manager | Yes | Own | Yes | Yes | Yes | No |
| HR Manager | No | Own | No | Yes | Yes | No |
| Employee | No | Own | No | Comment | Yes | No |
| Viewer | No | Own | No | No | No | No |

Permission vocabulary (`foundation/config.py`):

- `workspace:list`, `workspace:read`, `workspace:manage`
- `resource:list`, `resource:read`, `resource:create`, `resource:edit`, `resource:delete`
- `approval:list`, `approval:read`, `approval:approve`, `approval:comment`,
  `approval:create`, `approval:delete`
- `audit:list`, `audit:read`
- `report:list`, `report:read`
- `ai:brain:query`

## Isolation rule

- A user may touch records only in their own workspace, except the Owner who
  reaches all workspaces for consolidated reporting.
- Enforced at the store-query layer in `foundation/store.py` and
  `foundation/isolation.py` (`assert_isolated_to`).
- Owner consolidation access logged to the audit trail.

## Approval lifecycle

draft → pending → approved / rejected / withdrawn

- Approver roles: Owner, Manager, Finance Manager, Project Manager.
- Non-approver plays (`Viewer`, `Employee`, etc.) receive `PermissionError`.
- `require_approver` checks `users.role_id` joined with `roles.code`.

## Security controls

- Passwords hashed with PBKDF2-SHA256 (100,000 iterations, per-user random
  16-byte salt). Stored as `pbkdf2$<salt_hex>$<dk_hex>`.
- Session tokens: `secrets.token_urlsafe(32)`, 1-hour expiry.
- SQLite connection opened with `check_same_thread=False` (threaded HTTP
  server) and `journal_mode=WAL`.
- Bearer-only auth: `Authorization: Bearer <token>`.
- All business data is workspace-scoped; the Owner reads all via a documented
  branch.
- No network access; local-only service on `127.0.0.1`.

## Protected data

- `data/leads.csv` (production CRM) is never touched or exported by the
  foundation stack.
- Protected files (`.hermes/skills/shah-ai/SKILL.md`, `config/SOUL.md`,
  `brand/ssc-brand-profile.md`, `vendor/hermes-agent`) are untouched.
