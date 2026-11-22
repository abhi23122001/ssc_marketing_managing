# SHAH GROUP AI OS — OWNER STEP-BY-STEP SETUP GUIDE

**Application URL:** `http://127.0.0.1:8899/`  
**Target Audience:** Business Owner & Executive Management  
**Master Workspace:** Shah Survey & Consultants (`SSC`) & Shah Infrastructure & Construction (`INFRA`)

---

## 1. FIRST-TIME LOGIN & CREDENTIAL ROTATION

The system is configured with enterprise-grade authentication and session security.

### Login Steps:
1. Open Google Chrome or any modern browser and navigate to:
   ```
   http://127.0.0.1:8899/
   ```
2. Enter the secured owner credentials:
   - **Username:** `owner`
   - **Password:** `ShahGroup_Owner_Secured_2026!#`
3. Click **Sign In**.
4. The system issues a secure JWT token, initializes the session, and redirects to the **Executive Overview**.

> **Security Note:** If you wish to rotate the password to a personal passphrase, navigate to **Settings** -> **Change Password**. Old passwords are automatically invalidated, and active sessions are updated.

---

## 2. INTRODUCING THE OWNER SETUP CENTER

We have introduced a dedicated **Owner Setup Center** (`data-sec="owner-setup"`) accessible directly from the left sidebar navigation.

### Why Use the Setup Center?
- **Tracks Progress in Real-Time:** Monitors external API configurations, file paths, and database record counts.
- **Categorized Guidance:** Groups all remaining setup actions into 5 logical categories:
  1. Google Cloud Ecosystem Setup
  2. Meta (Instagram & Facebook) Setup
  3. YouTube Official Setup
  4. Real Business Info Setup
  5. Brand Setup & Identity
- **Safe Credential Input:** Allows you to enter API keys, Client IDs, and secrets directly into a password-masked UI that saves directly to local disk (`data/oauth_config.json`) without exposing credentials in URLs or source control.

---

## 3. STEP-BY-STEP ONBOARDING WALKTHROUGH

### Phase 1: Connect Google Cloud (Drive, Sheets, GBP)
1. In the sidebar, click **Owner Setup Center**.
2. Scroll to the **Submit & Store Credentials Safely** card.
3. Select **Google Ecosystem (Drive, Sheets, GBP)** from the dropdown.
4. Paste your **Client ID** and **Client Secret** (refer to `SHAH_GROUP_GOOGLE_OAUTH_SETUP_GUIDE.md`).
5. Click **Save Credential Safely**.
6. Under **Category 1: Google Cloud Ecosystem Setup**, click **Authorize Google Account**.
7. In the Google popup, choose your account, accept the scopes, and complete the authorization.
8. Status will update to `Connected` across Google Drive, Google Sheets, and Google Business Profile.

### Phase 2: Connect Meta (Instagram & Facebook)
1. Under **Submit & Store Credentials Safely**, select **Meta Ecosystem (Instagram & Facebook)**.
2. Enter your **Meta App ID** and **App Secret** (refer to `SHAH_GROUP_META_INSTAGRAM_FACEBOOK_SETUP_GUIDE.md`).
3. Click **Save Credential Safely**.
4. Under **Category 2**, click **Connect Facebook Page & Instagram**.
5. Log in to Facebook, select the page connected to `@shahgroupofficial1`, and grant permissions.
6. The status badge will change from `Authorization Required` to `Connected`.

### Phase 3: Connect YouTube Official Channel
1. In **Category 3**, click **Authorize YouTube Channel Ownership**.
2. Select the Google account managing `@ShahGroupOfficial`.
3. Confirm upload and analytics permissions.
4. Status will change to `Connected`.

### Phase 4: Input Real Business Data
The application database has undergone a **Fresh Business Reset**, meaning all dummy employees, mock projects, and fake invoices have been removed.

1. **Add Real Employees:**
   - In the sidebar, click **HRMS** -> **Employees**.
   - Click **+ Add Employee**.
   - Enter your senior surveyor, civil engineer, or accountant details.
2. **Add Active Sites:**
   - Click **Sites & Operations**.
   - Click **+ New Project Site**.
   - Enter your current highway, bridge, or land survey site name, client, and location.
3. **Add Active Clients:**
   - Click **CRM & Clients**.
   - Add your principal government and private clients (e.g. NHAI contractors, State PWD, private developers).

---

## 4. DAILY OPERATING ROUTINE FOR THE OWNER

| Time / Frequency | Module | Action |
| :--- | :--- | :--- |
| **Morning (9:00 AM)** | **Executive Overview** | Review cash flow, pending invoices, attendance summary, and active site counts. |
| **Morning (10:00 AM)**| **AI Brain & Studio** | Generate today's non-repeating engineering concept. Review Hindi/English script and save draft to Content Calendar. |
| **Mid-Day** | **Operations / Sites** | Review engineer task progression, DGPS raw file uploads, and milestone sign-offs. |
| **Afternoon** | **Finance / Invoicing**| Issue GST tax invoices, review incoming client payments, and track receivables. |
| **Weekly** | **Google Sheets Sync** | Confirm master spreadsheet (`Shah AI OS`) reflects up-to-date data across all 12 modules. |
