# M19 Agent Permission Matrix

## Authoritative rule

- Every agent tool call executes a backend permission check (RBAC + workspace isolation).
- An AI agent cannot bypass normal backend authorization.
- External actions are blocked by the approval machine regardless of agent.
- The Owner reaches all workspaces; non-owner roles are scoped to their own.

## Roles & capabilities

| Role | Workspaces | Content | Tasks | Publishing | Leads | Analytics |
|---|---|---|---|---|---|---|
| Owner | All | Full | Full | Pending owner approval | Full | Full |
| Marketing Manager | Assigned | Create/task/mgmt | Full | No | Assigned | Full |
| Content Creator | Assigned | Task + media | Full | No | No | No |
| Video Editor | Assigned | Video jobs | Full | No | No | No |
| Social Media Manager | Assigned | Account + calendar | Full | No | No | No |
| Lead Manager | Assigned | Enquiries/CRM | No | No | Full | No |
| Client Approver | Only own client | Own content | No | No | Own leads | Own reports |
| Viewer | Read-only | Authorized read | No | No | No | No |

## Agent tool permission checks

| Tool | Required permission | Workspace scope |
|---|---|---|
| `m19:account:*` | `m19:accounts:read` / `m19:accounts:write` | Own or owner |
| `m19:strategy:*` | `m19:content:write` | Own or owner |
| `m19:video:render` | `m19:video:write` | Own |
| `m19:publish:enqueue` | `m19:publish:write` | Own or owner |
| `m19:lead:*` | `m19:lead:write` | Own or owner |
| `m19:report:*` | `m19:report:read` | Own or owner |
| `m19:client:*` | `m19:client:read/write` | Owner / client approver only |

## External-action guard (always enforced)

- Publish, message send, ad launch, quotation, payment: blocked unless an explicit owner/client approval exists for that exact content version + platform + account.

## Audit

All agent tool calls are recorded: `social_agent_runs(agent_code, tool_name, permission_ok, status, result_summary)`.
