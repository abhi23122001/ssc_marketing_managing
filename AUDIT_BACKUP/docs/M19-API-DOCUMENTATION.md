# M19 API Documentation

## Base

- Audience: developers, dashboard team.
- Local test server: `python3 -m foundation.api` (port 8899); set_store(Store()) before running tests.
- All M19 endpoints are prefixed `/api/m19/*`.

## Design

- Authentication: Bearer token (`X-Session-Token` fallback) from `POST /api/auth/login`.
- Role authorization: RBAC (Owner / Marketing Manager / Content Creator / Video Editor / Social Media Manager / Lead Manager / Client Approver / Viewer).
- Workspace authorization: Owner reaches all workspaces; members scoped to own workspace.
- Response format: JSON objects; errors as `{"error": "..."}` with HTTP status codes.

## Endpoint summary

| Method | Path | Description |
|---|---|---|
| GET | `/api/m19/accounts` | List social accounts (workspace-scoped) |
| POST | `/api/m19/accounts` | Add social account |
| POST | `/api/m19/accounts/{id}/connect` | Verify connection (mock) |
| GET | `/api/m19/trends` | Trend discovery + scoring |
| GET | `/api/m19/content/ideas` | Content ideas (by business) |
| POST | `/api/m19/content` | Create content item |
| POST | `/api/m19/content/{id}/script` | Generate script (HI/EN/Hinglish) |
| POST | `/api/m19/content/{id}/caption` | Generate caption |
| GET | `/api/m19/calendar` | Content calendar entries |
| POST | `/api/m19/calendar` | Create calendar entry |
| POST | `/api/m19/approval` | Request approval |
| POST | `/api/m19/approval/{id}/transition` | Approve/reject/withdraw |
| GET | `/api/m19/publish` | Publishing queue |
| POST | `/api/m19/publish` | Enqueue publish (version-locked) |
| GET | `/api/m19/leads` | Social leads |
| POST | `/api/m19/lead` | Create lead (CRM sync) |
| GET | `/api/m19/kpi` | Employee KPI scorecard |
| GET | `/api/m19/report/weekly` | Weekly report |
| GET | `/api/m19/report/monthly` | Monthly report |
| POST | `/api/m19/asset` | Upload media + checksum |
| POST | `/api/m19/video-job` | Create video render job |
| GET | `/api/m19/video-job/{id}` | Video job status |

## Workspace-scoped reads

All GET endpoints scope to the authenticated user's workspace unless the role is Owner.

## Request/Response contract example (content idea)

**POST** `/api/m19/content`
```json
{
  "content_id": "IDE-7",
  "title": "Test Reel",
  "hook": "Hello",
  "key_message": "Precision surveying",
  "cta": "Contact us",
  "platform": "instagram"
}
```
**201** → `{"id": 1, "content_id": "IDE-7", "status": "draft", ...}`

## Error codes

- 401: authentication required
- 403: role/workspace authorization denied
- 404: resource not found
- 409: conflict (e.g., duplicate account)
- 422: validation error
- 500: internal error (never logs secrets)

## Platform integration note

Real publishing endpoints (`/api/m19/publish`) require platform OAuth tokens. Until authorized, the mock adapter is used and the response includes `"integration_required": true`.
