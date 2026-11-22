# SHAH GROUP AI OS — YOUTUBE OFFICIAL CHANNEL INTEGRATION GUIDE

**Target System:** SHAH GROUP AI OS  
**Application URL:** `http://127.0.0.1:8899/`  
**Official Channel:** `https://www.youtube.com/@ShahGroupOfficial`  
**Registered Channel Handle:** `@ShahGroupOfficial`

---

## 1. CAPABILITIES & USE CASES

Connecting YouTube to SHAH GROUP AI OS enables:
1. **Automated YouTube Shorts Publishing:** Upload 9:16 vertical engineering and survey videos directly to `@ShahGroupOfficial`.
2. **AI Marketing Script Production:** Auto-format 4-part scripts (Hook, Problem, Solution, CTA) into optimized YouTube video titles, tags, and description boxes.
3. **Channel Performance Analytics:** Sync view counts, subscribers, and audience engagement into the Executive Overview dashboard.
4. **Honest Connection State:** Displays `Authorization Required` until your Google/YouTube account authorizes the app.

---

## 2. PREREQUISITES

1. Primary Owner or Manager rights to the YouTube Channel `@ShahGroupOfficial`.
2. A Google Cloud project with **YouTube Data API v3** enabled.

---

## 3. STEP-BY-STEP GOOGLE CLOUD CONFIGURATION

### Step 1: Enable YouTube Data API v3
1. Open [Google Cloud Console API Library](https://console.cloud.google.com/apis/library).
2. Select your Google Cloud project (`Shah-Group-AI-OS`).
3. Search for **YouTube Data API v3** and click **Enable**.

### Step 2: Configure Scopes & Consent Screen
1. Go to **APIs & Services** -> **OAuth consent screen** ([Direct Link](https://console.cloud.google.com/apis/credentials/consent)).
2. Add the following scopes:
   - `https://www.googleapis.com/auth/youtube.upload` (Upload videos and Shorts)
   - `https://www.googleapis.com/auth/youtube.readonly` (View channel statistics and video analytics)
3. Ensure your YouTube channel owner email is registered under **Test Users** while the app is in testing mode.

### Step 3: OAuth Redirect URI Verification
1. Under **APIs & Services** -> **Credentials**, select your Web Client credentials.
2. Confirm the redirect URI is configured:
   ```
   http://127.0.0.1:8899/api/oauth/callback/google
   ```

---

## 4. AUTHORIZING YOUTUBE IN SHAH GROUP AI OS

1. Open `http://127.0.0.1:8899/` and log in as `owner`.
2. Navigate to **Owner Setup Center** -> **Category 3: YouTube Official Setup**.
3. Click **Authorize YouTube Channel Ownership**.
4. In the Google OAuth popup, select the account that manages `@ShahGroupOfficial`.
5. If prompted with "Choose a channel or brand account", select **Shah Group Official**.
6. Check the box to grant video upload and viewing permissions.
7. Click **Continue**.
8. Once redirected back, the status badge for `@ShahGroupOfficial` will change from `Authorization Required` to `Connected`.

---

## 5. PRODUCING & PUBLISHING YOUTUBE SHORTS

### Video Format Requirements for YouTube Shorts:
- **Aspect Ratio:** `9:16` (Vertical format: 1080x1920 pixels).
- **Duration:** 15 to 60 seconds (Optimal: 45–55 seconds).
- **Required Tag:** Include `#Shorts` in both title and description.

### Publishing Workflow via AI OS:
1. Open **AI Brain & Marketing Studio**.
2. Select **YouTube Shorts Concept** under content formats.
3. Review the generated 4-part script:
   - **0–5s Hook:** High-contrast engineering question or visual demonstration.
   - **5–20s Problem:** Cost or safety risk of traditional methods.
   - **20–40s Solution:** Drone LiDAR / DGPS RTK / High-speed paving solution.
   - **40–55s CTA:** "Call Shah Group for site survey tenders across India."
4. Click **Save to Calendar** or **Publish via YouTube API**.
