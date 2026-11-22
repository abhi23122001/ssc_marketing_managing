# SHAH GROUP AI OS — GOOGLE BUSINESS PROFILE (GBP) SETUP GUIDE

**Target System:** SHAH GROUP AI OS  
**Application URL:** `http://127.0.0.1:8899/`  
**Integration Module:** `foundation/domains/google_business_profile.py`  
**UI Interface:** Navigation -> **Central Integration Center** -> **Google Business Profile (GBP)** OR **Owner Setup Center** -> **Category 1: Google Cloud Ecosystem Setup**

---

## 1. OVERVIEW & CAPABILITIES

Google Business Profile (GBP) integration enables SHAH GROUP AI OS to directly manage the online local presence of **Shah Survey & Consultants (SSC)** and **Shah Infrastructure & Construction (INFRA)**.

### First-Class Features Supported:
1. **Business Profile Metadata Management:** Sync store name, address, phone number, website URL, coordinates, and operating hours.
2. **Service Catalog Management:** Manage engineering services (DGPS RTK Survey, Drone LiDAR Survey, Highway Alignment, GIS Mapping) and civil construction services (Highway Earthworks, Pipeline Infrastructure, Bridge Construction, Road Works).
3. **Google Posts (Local Updates) Publishing:** Create and publish "What's New", "Event", or "Offer" posts with call-to-action buttons (`LEARN_MORE`, `CALL`, `BOOK`, `SIGN_UP`).
4. **Customer Review Monitoring & Instant Replies:** View received Google reviews and draft or post owner responses directly from the AI OS dashboard.
5. **Zero Simulation Rule:** The system displays `Authorization Required` until real OAuth authorization is granted by Google. No fake success states or mock syncs are displayed.

---

## 2. PREREQUISITES

To connect GBP, the owner must have:
1. A Google Account with **Primary Owner** or **Manager** rights to the verified Google Business Profile for Shah Group / SSC / INFRA.
2. A Google Cloud Console project (`console.cloud.google.com`).

---

## 3. STEP-BY-STEP GOOGLE CLOUD CONFIGURATION

### Step 1: Enable Google My Business APIs in Google Cloud
1. Navigate to [Google Cloud Console API Library](https://console.cloud.google.com/apis/library).
2. Select your Google Cloud Project.
3. Search for and enable the following APIs:
   - **Google My Business API** (`mybusiness.googleapis.com`)
   - **My Business Business Information API** (`mybusinessbusinessinformation.googleapis.com`)
   - **My Business Account Management API** (`mybusinessaccountmanagement.googleapis.com`)
   - **My Business Lodging API** / **My Business Place Actions API**

### Step 2: Configure OAuth 2.0 Consent Screen
1. Go to **APIs & Services** -> **OAuth consent screen** ([Direct Link](https://console.cloud.google.com/apis/credentials/consent)).
2. Select **User Type:** `External` (or `Internal` if using Google Workspace).
3. Fill in:
   - **App name:** `SHAH GROUP AI OS`
   - **User support email:** Your official email (e.g. `shahgroupofficial@gmail.com`).
   - **Developer contact information:** Your admin email.
4. Click **Save and Continue**.
5. On the **Scopes** page, click **Add or Remove Scopes** and add:
   - `https://www.googleapis.com/auth/business.manage`
6. Click **Save and Continue**.
7. If your app is in "Testing" status, add your Google account as a **Test User**.

### Step 3: Create OAuth 2.0 Web Application Credentials
1. Go to **APIs & Services** -> **Credentials** ([Direct Link](https://console.cloud.google.com/apis/credentials)).
2. Click **+ CREATE CREDENTIALS** -> **OAuth client ID**.
3. Select **Application type:** `Web application`.
4. Enter **Name:** `SHAH GROUP AI OS Local Web Client`.
5. Under **Authorized redirect URIs**, add:
   ```
   http://127.0.0.1:8899/api/oauth/callback/google
   ```
6. Click **Create**.
7. Copy your **Client ID** and **Client Secret**.

---

## 4. LINKING CREDENTIALS IN SHAH GROUP AI OS

You can enter the credentials directly inside the application UI:

1. Open `http://127.0.0.1:8899/` and log in as `owner`.
2. Navigate to **Owner Setup Center** (`#sec-owner-setup`) from the left sidebar.
3. Scroll down to **Submit & Store Credentials Safely**.
4. In the provider dropdown, select **Google Ecosystem (Drive, Sheets, GBP)**.
5. Enter:
   - **Client ID:** `your-client-id.apps.googleusercontent.com`
   - **Client Secret:** `GOCSPX-your-client-secret`
6. Click **Save Credential Safely**. The credentials will be saved securely to `data/oauth_config.json`.

---

## 5. INITIATING OAUTH AUTHORIZATION

1. Navigate to **Central Integration Center** -> **Google Business Profile (GBP)**.
2. Under **GBP OAuth Authorization**, click the **Authorize Google Business Profile** link.
3. Google will open the OAuth consent prompt. Sign in with the account that manages the Shah Group business listing.
4. Click **Allow** to grant the `business.manage` permission.
5. Google will redirect back to `http://127.0.0.1:8899/api/oauth/callback/google`.
6. Once authorized, the banner in the GBP panel will update to `Status: Connected` and display your verified locations.

---

## 6. DAILY OPERATIONAL USAGE

### Publishing Local Updates (Google Posts):
1. In the GBP panel, select **Create Google Post**.
2. Select your post type: `What's New`, `Event`, or `Offer`.
3. Enter your post summary or paste from the **AI Marketing Studio**.
4. Choose a Call to Action button (e.g. `Call Now`, `Learn More`).
5. Click **Publish to Google Profile**.

### Managing Reviews & Automated Drafts:
1. View customer reviews in the **Recent Google Reviews** table.
2. Click **Reply** on any review.
3. Use the AI Assistant to generate a polite, professional reply referencing MoRTH standards, high precision, or prompt service delivery.
4. Click **Send Reply to Google**.
