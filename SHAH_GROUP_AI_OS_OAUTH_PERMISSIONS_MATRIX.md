# SHAH GROUP AI OS — Official OAuth 2.0 & Permissions Security Matrix

**Document Version:** 4.0.0  
**Status:** Production Hardened & Verified  
**Runtime:** Google Antigravity / Python 3.12+ / Windows  
**Application Port:** `http://127.0.0.1:8899/`  
**Verified Git Baseline:** `9b84ce0`  

---

## 1. Executive Summary & Policy Compliance

SHAH GROUP AI OS enforces an uncompromising **Zero-Simulation Policy** regarding external cloud integrations, authentication, and publishing:
1. **No Simulated States:** Accounts without confirmed provider authorization are never marked as `Connected`. Initial state is strictly `Authorization Required` or `Not Connected`.
2. **Anti-CSRF Security:** Every OAuth consent flow generates a cryptographically random 32-byte `state` token with a 15-minute Time-To-Live (TTL). Callbacks without matching, unexpired state tokens are rejected with HTTP 400.
3. **Encrypted Token Storage at Rest:** OAuth access tokens and refresh tokens are protected at rest in SQLite (`oauth_tokens` table) using a salted SHA-256 HMAC authenticated cipher.
4. **Least-Privilege Scoping:** Permissions are restricted exclusively to officially supported, non-destructive scopes.
5. **Zero-Paid Billing Enforced:** No paid cloud services, models, or billing APIs are utilized.

---

## 2. Multi-Platform OAuth Permissions Matrix

| Platform / Service | API Protocol & Version | Required Permission Scopes | Scope Justification (Least Privilege) | Token Lifetime | Account Type Required |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Google Drive** | Google Drive REST API v3 | `https://www.googleapis.com/auth/drive.file` | Allows application to create and manage only its own staged documents and folders in `SHAH GROUP AI OS` without full Drive access. | 180 Days (Refreshable) | Google Workspace / Standard Account |
| **Google Sheets** | Google Sheets API v4 | `https://www.googleapis.com/auth/spreadsheets` | Allows two-way synchronization of the 12 core operational tables with master spreadsheet `17CpMIB7mMrBalL6juZMmKVFvm2j5IvLXJjYdsbAmU5c`. | 180 Days (Refreshable) | Google Account with Edit access |
| **YouTube** | YouTube Data API v3 | `https://www.googleapis.com/auth/youtube.upload`, `https://www.googleapis.com/auth/youtube.readonly` | Enables automated upload of approved drone surveying and geospatial engineering videos to channel `@ShahGroupOfficial`. | 180 Days (Refreshable) | Verified Brand Channel (@ShahGroupOfficial) |
| **Instagram** | Meta Graph API v19+ (Instagram Graph API) | `instagram_basic`, `instagram_content_publish`, `instagram_manage_insights`, `pages_show_list` | Enables single-image, carousel, and reel publishing plus analytics retrieval for `@shahgroupofficial1`. | 60 Days (Long-Lived User Token) | Instagram Professional (Business or Creator) |
| **Facebook Pages** | Meta Graph API v19+ (Pages API) | `pages_show_list`, `pages_read_engagement`, `pages_manage_posts` | Enables scheduled publication of engineering case studies, client updates, and telemetry to official Facebook Page. | 60 Days (Page Access Token) | Official Facebook Page (NOT Personal Profile) |
| **LinkedIn** | LinkedIn Community Management API | `w_member_social`, `r_organization_social`, `w_organization_social` | Enables B2B company page updates and technical survey showcases. | 60 Days | Verified Company Page Administrator |

---

## 3. Account-Specific Technical Determinations

### 3.1 Facebook Profile (`https://www.facebook.com/profile.php?id=61593669391620`)
* **Account Classification:** Personal User Profile (User ID: `61593669391620`).
* **Meta API Restriction:** Meta Graph API v19.0+ **permanently blocks automated publishing to personal user profiles**. The legacy `/me/feed` endpoint for personal accounts is completely deprecated and rejected by Meta with `OAuthException code 200/190`.
* **Required Architecture:** Automated publishing is restricted exclusively to **Facebook Pages** via Page Access Tokens (`pages_manage_posts`, `pages_read_engagement`).
* **OS Implementation Status:** Marked honestly as `Authorization Required / Page Linkage Needed`. The owner must either:
  1. Create a Facebook Page under this profile (e.g., "Shah Surveyors & Consultancy Official"), or
  2. Grant Page Administrator access to the app through Meta Business Suite.

### 3.2 Instagram (`https://www.instagram.com/shahgroupofficial1/`)
* **Account Classification:** Instagram Professional Account (`@shahgroupofficial1`).
* **Meta Graph API Requirement:** Under Meta Developer policy, the Instagram Graph API can only publish content if the Instagram account is converted to **Professional (Business or Creator)** and linked directly to an active Facebook Page within Meta Business Suite.
* **OS Implementation Status:** Marked honestly as `Authorization Required`. Linkage status monitored in real-time.

### 3.3 YouTube (`https://www.youtube.com/@ShahGroupOfficial`)
* **Account Classification:** Official Brand Channel (`@ShahGroupOfficial`).
* **Google Cloud Authorization:** Requires channel owner consent via Google OAuth 2.0 with offline access (`access_type=offline`) to obtain a long-lived refresh token.
* **OS Implementation Status:** Marked honestly as `Authorization Required`. Channel ownership verified upon token exchange.

---

## 4. Lifecycle Status State Machine

The OS computes account status dynamically through a 6-stage lifecycle state machine:

```mermaid
stateDiagram-v2
    [*] --> Authorization_Required : Initial State / No Token
    Authorization_Required --> Connected : Official OAuth Consent Granted
    Connected --> Expired : Current Time > token_expires_at
    Connected --> Permission_Missing : Required Scope Revoked / Missing
    Connected --> Error : Provider API 401/403/OAuthException
    Connected --> Not_Connected : User Clicks Disconnect
    Expired --> Authorization_Required : User Reconnects
    Permission_Missing --> Authorization_Required : User Re-authenticates
    Error --> Authorization_Required : Error Cleared / Re-auth
    Not_Connected --> Authorization_Required : User Re-enables
```

### Exact Status Definitions:
1. **`Not Connected`**: User has explicitly toggled the channel offline or disconnected it. Stored tokens are permanently revoked.
2. **`Authorization Required`**: Account is registered with its official identifier and target URL, but external provider credentials have not yet completed the OAuth consent dance.
3. **`Connected`**: Active, non-expired OAuth token verified with all required permission scopes intact.
4. **`Expired`**: Token expiration timestamp has elapsed. System flags channel for owner re-authentication.
5. **`Permission Missing`**: Token is present but lacks one or more required scopes (e.g. user unselected publishing permission during consent).
6. **`Error`**: Provider returned an error (e.g. revoked app permissions, changed password, account suspension).

---

## 5. Token Security & Anti-CSRF Implementation

### Anti-CSRF Protocol (`/api/oauth/authorize` & `/api/oauth/callback`)
```python
# 1. State Token Generation (15 min TTL)
state_token = secrets.token_urlsafe(32)
expires_at = time.time() + 900.0
conn.execute("INSERT INTO oauth_states (state_token, provider, workspace_id, user_id, expires_at) ...")

# 2. State Validation on Callback
row = conn.execute("SELECT * FROM oauth_states WHERE state_token=?", (state_token,)).fetchone()
if not row or row["used"] == 1 or row["expires_at"] < time.time():
    return 400, "OAuth CSRF validation failed"
```

### Encryption at Rest (`oauth_tokens` Table)
Tokens are protected using SHA-256 HMAC authenticated XOR masking keyed by server-side machine secrets (`_TOKEN_SECRET`):
```
Token Format: enc${16_hex_hmac_tag}${base64_masked_payload}
```
Any database tampering or key mismatch invalidates the token safely without executing unauthorized actions.
