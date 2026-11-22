# SHAH GROUP AI OS — GOOGLE OAUTH & GOOGLE WORKSPACE SETUP GUIDE

**Target System:** SHAH GROUP AI OS  
**Application URL:** `http://127.0.0.1:8899/`  
**Supported Google Services:** Google Drive (Cloud Document Vault), Google Sheets (Two-Tier Live Ledger Mirroring), Google Business Profile (Local Search & Posts), YouTube Data API (Shorts & Video Publishing).

---

## 1. ARCHITECTURAL OVERVIEW: TWO-TIER GOOGLE INTEGRATION

SHAH GROUP AI OS employs a reliable **Two-Tier Synchronization Architecture**:

```
+-------------------------------------------------------------+
|                  LOCAL BUSINESS OS (TIER 1)                 |
|  - SQLite Primary Engine (Fast, Transactional, Offline)     |
|  - Local Document Vault (15 Category Folders in data/drive)  |
|  - Local Safe CSV Mirrors (12 Modules in data/sheets_sync)   |
+-------------------------------------------------------------+
                             |
                   Official Google OAuth 2.0
                             |
                             v
+-------------------------------------------------------------+
|                  GOOGLE CLOUD CLOUD (TIER 2)                |
|  - Google Drive Company Vault                               |
|  - Master Google Sheet: Shah AI OS                          |
|    ID: 17CpMIB7mMrBalL6juZMmKVFvm2j5IvLXJjYdsbAmU5c         |
|  - Google Business Profile Listing                          |
|  - YouTube Official Channel (@ShahGroupOfficial)            |
+-------------------------------------------------------------+
```

### Safety and Privacy Guarantees:
- **No Mock Tokens:** When unauthenticated, the system accurately displays `Authorization Required`.
- **Zero Data Loss:** If internet connectivity drops or tokens expire, the system queues changes in the local Tier 1 storage without disruption.
- **Data Protection:** Secrets are stored locally in `data/oauth_config.json` with file permissions restricted to the application host.

---

## 2. GOOGLE CLOUD PROJECT PREREQUISITES

1. Log in to [Google Cloud Console](https://console.cloud.google.com/) using your Google account (e.g. `shahgroupofficial@gmail.com`).
2. Create a new Google Cloud Project named `Shah-Group-AI-OS` (or select your existing company project).
3. Confirm that project billing is either free-tier or linked to your organization. (Google Drive and Sheets APIs are free within standard quotas).

---

## 3. STEP 1: ENABLE REQUIRED GOOGLE APIS

Navigate to **APIs & Services** -> **Library** ([Direct Link](https://console.cloud.google.com/apis/library)) and enable:

1. **Google Drive API** (`drive.googleapis.com`)
2. **Google Sheets API** (`sheets.googleapis.com`)
3. **Google Business Profile API** (`mybusiness.googleapis.com`)
4. **YouTube Data API v3** (`youtube.googleapis.com`)

---

## 4. STEP 2: CONFIGURE OAUTH 2.0 CONSENT SCREEN

1. Go to **APIs & Services** -> **OAuth consent screen** ([Direct Link](https://console.cloud.google.com/apis/credentials/consent)).
2. Select **User Type:** `External` (or `Internal` if Google Workspace organization).
3. Fill in:
   - **App name:** `SHAH GROUP AI OS`
   - **User support email:** Your email address.
   - **Developer contact info:** Your email address.
4. Click **Save and Continue**.
5. Click **Add or Remove Scopes** and add:
   - `https://www.googleapis.com/auth/drive.file` (Create & access app-specific Drive files)
   - `https://www.googleapis.com/auth/spreadsheets` (Read & write master Google Sheets)
   - `https://www.googleapis.com/auth/business.manage` (Manage Google Business Profile)
   - `https://www.googleapis.com/auth/youtube.upload` (Upload YouTube Shorts and videos)
   - `https://www.googleapis.com/auth/userinfo.email` (Identity verification)
6. Click **Save and Continue**.
7. Under **Test Users**, click **+ ADD USERS** and enter:
   - `shahgroupofficial@gmail.com` (and any other admin emails who will authorize the app).
8. Click **Save and Continue**.

---

## 5. STEP 3: CREATE OAUTH 2.0 CLIENT ID

1. Navigate to **APIs & Services** -> **Credentials** ([Direct Link](https://console.cloud.google.com/apis/credentials)).
2. Click **+ CREATE CREDENTIALS** -> **OAuth client ID**.
3. Set **Application type:** `Web application`.
4. Set **Name:** `SHAH GROUP AI OS Desktop Client`.
5. Under **Authorized redirect URIs**, click **+ ADD URI** and add:
   ```
   http://127.0.0.1:8899/api/oauth/callback/google
   ```
6. Click **Create**.
7. Download the credentials JSON or copy the **Client ID** and **Client Secret**.

---

## 6. STEP 4: STORE CREDENTIALS & AUTHORIZE IN SHAH GROUP AI OS

### Option A: Via Dashboard (Recommended)
1. Open `http://127.0.0.1:8899/` and sign in as `owner`.
2. Go to **Owner Setup Center** -> **Submit & Store Credentials Safely**.
3. Select **Google Ecosystem (Drive, Sheets, GBP)**.
4. Paste the **Client ID** and **Client Secret**.
5. Click **Save Credential Safely**.
6. Under **Google Cloud Ecosystem Setup**, click **Authorize Google Account**.
7. Authorize with your Google Account in the browser window that opens.

### Option B: Via Local Configuration File
Open `data/oauth_config.json` and paste your credentials:
```json
{
  "google": {
    "client_id": "YOUR_CLIENT_ID.apps.googleusercontent.com",
    "client_secret": "GOCSPX-YOUR_CLIENT_SECRET",
    "redirect_uri": "http://127.0.0.1:8899/api/oauth/callback/google",
    "scopes": [
      "https://www.googleapis.com/auth/drive.file",
      "https://www.googleapis.com/auth/spreadsheets",
      "https://www.googleapis.com/auth/business.manage",
      "https://www.googleapis.com/auth/youtube.upload"
    ]
  }
}
```

---

## 7. STEP 5: VERIFY MASTER GOOGLE SHEET MIRRORING

The master Google Sheet is already registered:
- **Sheet Name:** `Shah AI OS`
- **Spreadsheet ID:** `17CpMIB7mMrBalL6juZMmKVFvm2j5IvLXJjYdsbAmU5c`
- **Direct Link:** `https://docs.google.com/spreadsheets/d/17CpMIB7mMrBalL6juZMmKVFvm2j5IvLXJjYdsbAmU5c/edit`

Ensure the authorized Google account has **Editor** permissions on this spreadsheet. Once connected, changes to the 12 active business modules (Employees, Sites, Invoices, Quotations, Clients, Leads, Tasks, Payroll, Expenses, Attendance, Equipment, Vendor Directory) will mirror seamlessly.
