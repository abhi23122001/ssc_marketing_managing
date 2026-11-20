# M19 Client Agency Report

## Objective

Provide the Shah Group with the ability to manage social media for external clients as a commercial service, with per-client workspaces and a client portal.

## Client workspace features

- `social_client_profiles`: client profile, company, brand guidelines, service package, contract metadata, billing.
- `social_accounts` with `client_workspace_id`: client platform accounts (separated from Shah Group internal accounts).
- `social_content_items` / `social_calendar_entries` scoped to `client_workspace_id`.
- `social_approvals`: client approver role can approve only their own content.
- `social_published_posts`: publishing history per client account.
- `social_reports`: monthly reports per client workspace.
- `social_leads`: client-scope CRM records.

## Client portal restrictions

Client cannot:
- Access another client's data.
- View Shah Group internal information.
- View internal employee payroll.
- Access other client credentials.
- Change platform credentials without permission.
- Publish content without required authorization.

Owner can view all authorized clients and has consolidated access.

## Agency readiness

The agency module is implemented as local business logic (SM-18: `create_client`, `list_clients`, `social_client_profiles`). The dashboard M19 section ("Client Management") and the client portal UI are pending the owner's UI build.

## Example workflow

1. Owner registers client `CLIENT-X` (`social_client_profiles.client_workspace_id = "CLIENT-X"`).
2. Client's accounts are added as `social_accounts(workspace_id=SSC, client_workspace_id="CLIENT-X")`.
3. Owner assigns production tasks to employees via `social_tasks` scoped to `SSC`.
4. Client views/approves only content in `CLIENT-X`.
