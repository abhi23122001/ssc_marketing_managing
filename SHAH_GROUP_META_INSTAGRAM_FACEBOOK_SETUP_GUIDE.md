# SHAH GROUP AI OS — META (INSTAGRAM & FACEBOOK) INTEGRATION GUIDE

**Target System:** SHAH GROUP AI OS  
**Application URL:** `http://127.0.0.1:8899/`  
**Registered Brand Assets:**
1. **Instagram Account:** `https://www.instagram.com/shahgroupofficial1/` (Handle: `shahgroupofficial1`)
2. **Facebook Profile/Page:** `https://www.facebook.com/profile.php?id=61593669391620` (ID: `61593669391620`)

---

## 1. META GRAPH API ARCHITECTURE

To publish content or sync metrics to Instagram and Facebook via the official Meta Graph API:
- **Instagram:** Must be an **Instagram Professional Account** (Business or Creator type). Personal accounts are not supported by the Meta Graph API.
- **Facebook:** The Instagram account must be connected to a **Facebook Page** (not a private personal profile). If `61593669391620` is a personal profile, create or convert it into an official Facebook Page (e.g., "Shah Group Official" or "Shah Survey & Consultants").

---

## 2. STEP 1: PREPARE YOUR META ASSETS

1. **Convert Instagram to Professional Account:**
   - On the Instagram mobile app, log into `@shahgroupofficial1`.
   - Go to **Settings and privacy** -> **Account type and tools** -> **Switch to professional account**.
   - Select category (e.g. `Engineering Service` or `Consulting Agency`).
   - Choose `Business`.

2. **Connect Instagram to your Facebook Page:**
   - In Instagram Settings -> **Business** -> **Connect a Facebook Page**.
   - Select or create the Facebook Page corresponding to Shah Group (`61593669391620`).
   - Confirm Admin access.

---

## 3. STEP 2: CREATE A META DEVELOPER APP

1. Navigate to the [Meta for Developers Portal](https://developers.facebook.com/).
2. Log in with your Facebook account.
3. Click **My Apps** -> **Create App**.
4. Select **App Type:** `Business`.
5. Enter:
   - **App Display Name:** `SHAH GROUP AI OS`
   - **App Contact Email:** `shahgroupofficial@gmail.com`
6. Click **Create App**.

---

## 4. STEP 3: CONFIGURE FACEBOOK LOGIN & PERMISSIONS

1. In the Meta App Dashboard, find **Add Products to Your App**.
2. Locate **Facebook Login for Business** and click **Set Up**.
3. Under **Facebook Login** -> **Settings**:
   - In **Valid OAuth Redirect URIs**, add:
     ```
     http://127.0.0.1:8899/api/oauth/callback/meta
     http://127.0.0.1:8899/api/oauth/callback/facebook
     ```
   - Click **Save Changes**.

4. Required API Permissions (Scopes):
   - `pages_show_list` (List Facebook Pages managed by user)
   - `pages_read_engagement` (Read post analytics and likes)
   - `pages_manage_posts` (Publish posts and updates to Facebook Page)
   - `instagram_basic` (Read Instagram account metadata)
   - `instagram_content_publish` (Publish reels, photos, and carousels)

---

## 5. STEP 4: OBTAIN APP ID & APP SECRET

1. In the left navigation menu, go to **App settings** -> **Basic**.
2. Copy your **App ID**.
3. Under **App secret**, click **Show** and copy the secret.

---

## 6. STEP 5: STORE CREDENTIALS IN SHAH GROUP AI OS

1. Open `http://127.0.0.1:8899/` and log in as `owner`.
2. Go to **Owner Setup Center** -> **Submit & Store Credentials Safely**.
3. In the dropdown, select **Meta Ecosystem (Instagram & Facebook)**.
4. Enter:
   - **Client ID / App ID:** Your Meta App ID.
   - **Client Secret / App Secret:** Your Meta App Secret.
5. Click **Save Credential Safely**. The data will be stored securely in `data/oauth_config.json`.

---

## 7. STEP 6: AUTHORIZE AND TEST PUBLISHING

1. Go to **Owner Setup Center** -> **Category 2: Meta Ecosystem Setup**.
2. Click **Connect Facebook Page & Instagram**.
3. Log in with the Facebook account that owns the page and click **Continue as...**.
4. Grant the permissions requested.
5. Upon redirect, the connection status for both Instagram (`@shahgroupofficial1`) and Facebook (`61593669391620`) will update from `Authorization Required` to `Connected`.

### Publishing Daily AI Campaigns:
1. Go to **AI Brain & Marketing Studio**.
2. Generate your daily technical concept (e.g. DGPS RTK vs Total Station, Highway LiDAR).
3. Click **Save as Verified Draft to Calendar**.
4. In **Social Media Studio**, review the campaign copy, hashtags, and visual directions.
5. Click **Publish to Instagram & Facebook**.
