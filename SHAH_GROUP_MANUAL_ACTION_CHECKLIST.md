# SHAH GROUP AI OS — OWNER MANUAL ACTION CHECKLIST

**Target System:** SHAH GROUP AI OS  
**Application URL:** `http://127.0.0.1:8899/`  
**Owner Account:** `owner` / `ShahGroup_Owner_Secured_2026!#`  
**Dedicated In-App Wizard:** Navigation -> **Owner Setup Center** (`#sec-owner-setup`)

---

## 1. CHECKLIST OVERVIEW

All internal software logic, algorithms, databases, schemas, templates, and UI components have been autonomously implemented, tested, and verified.

The 16 items below represent the external account authorizations, credentials, and genuine business assets that only the business owner can provide.

Use this checklist alongside the in-app **Owner Setup Center**, which tracks real-time progress as each item is completed.

---

## 2. CATEGORY 1: GOOGLE CLOUD ECOSYSTEM (4 TASKS)

- [ ] **Task 1.1: Create/Select Google Cloud Project**
  - **Portal:** [Google Cloud Console](https://console.cloud.google.com/)
  - **Action:** Create project `Shah-Group-AI-OS` or select existing company project.
  - **Requirement:** Enable Google Drive, Google Sheets, Google Business Profile, and YouTube Data API v3.

- [ ] **Task 1.2: Configure OAuth Consent Screen & Scopes**
  - **Portal:** [Google OAuth Consent Screen](https://console.cloud.google.com/apis/credentials/consent)
  - **Action:** Set User Type to External, add App Name `SHAH GROUP AI OS`, and add scopes:
    - `https://www.googleapis.com/auth/drive.file`
    - `https://www.googleapis.com/auth/spreadsheets`
    - `https://www.googleapis.com/auth/business.manage`
    - `https://www.googleapis.com/auth/youtube.upload`
  - Add your admin email to **Test Users**.

- [ ] **Task 1.3: Generate OAuth Client ID & Store in AI OS**
  - **Portal:** [Google Credentials](https://console.cloud.google.com/apis/credentials)
  - **Action:** Create Web Client with Redirect URI:
    ```
    http://127.0.0.1:8899/api/oauth/callback/google
    ```
  - **In App:** Go to **Owner Setup Center** -> **Submit Credentials Safely** -> Select Google -> Enter Client ID & Secret -> Save.

- [ ] **Task 1.4: Grant Spreadsheet Editor Permissions**
  - **Spreadsheet:** `https://docs.google.com/spreadsheets/d/17CpMIB7mMrBalL6juZMmKVFvm2j5IvLXJjYdsbAmU5c/edit`
  - **Action:** Open sheet `Shah AI OS` and verify your authorized Google account has `Editor` access.

---

## 3. CATEGORY 2: META (INSTAGRAM & FACEBOOK) (3 TASKS)

- [ ] **Task 2.1: Convert Instagram to Professional Account**
  - **Account:** `@shahgroupofficial1` (`https://www.instagram.com/shahgroupofficial1/`)
  - **Action:** In Instagram App Settings -> Switch account type to **Professional / Business**.

- [ ] **Task 2.2: Connect Instagram to Facebook Page**
  - **Facebook Entity:** ID `61593669391620` (`https://www.facebook.com/profile.php?id=61593669391620`)
  - **Action:** Ensure the Facebook entity is a Page with Admin rights, and link `@shahgroupofficial1` in Page Settings.

- [ ] **Task 2.3: Create Meta Business App & Save App ID**
  - **Portal:** [Meta for Developers](https://developers.facebook.com/)
  - **Action:** Create Business App, add Facebook Login with redirect URI:
    ```
    http://127.0.0.1:8899/api/oauth/callback/meta
    ```
  - **In App:** Enter App ID & App Secret into **Owner Setup Center** and click **Connect Facebook & Instagram**.

---

## 4. CATEGORY 3: YOUTUBE OFFICIAL CHANNEL (2 TASKS)

- [ ] **Task 3.1: Confirm Channel Ownership / Manager Role**
  - **Channel:** `@ShahGroupOfficial` (`https://www.youtube.com/@ShahGroupOfficial`)
  - **Action:** Verify your Google account has Manager/Owner permissions in [YouTube Studio](https://studio.youtube.com/).

- [ ] **Task 3.2: Authorize YouTube Data API via OAuth**
  - **In App:** Go to **Owner Setup Center** -> **Category 3: YouTube Official Setup** -> Click **Authorize YouTube Channel Ownership**.

---

## 5. CATEGORY 4: REAL BUSINESS PROFILES & METRICS (4 TASKS)

- [ ] **Task 4.1: Enter Registered Business GSTIN & PAN**
  - **In App:** Go to **Settings** -> **Company Profile**. Enter official Legal Name, GSTIN, PAN, and Registered Head Office Address.

- [ ] **Task 4.2: Enter Official Bank Account Details**
  - **In App:** Enter Beneficiary Name, Account Number, IFSC Code, and Bank Branch for automated invoice generation.

- [ ] **Task 4.3: Enter Genuine Staff Profiles**
  - **In App:** Go to **HRMS** -> **Employees**. Add real engineers, surveyors, and admin staff to replace purged demo entries.

- [ ] **Task 4.4: Enter Active Project Sites & Client Directory**
  - **In App:** Go to **Sites & Projects** and **CRM / Clients**. Create real ongoing site records (highway chainages, solar parks, industrial yards).

---

## 6. CATEGORY 5: BRAND ASSETS & TEMPLATES (3 TASKS)

- [ ] **Task 5.1: Upload High-Resolution Company Logo**
  - **In App:** In **Company Profile**, upload high-resolution PNG/SVG logos with transparent background for invoice headers.

- [ ] **Task 5.2: Upload Authorized Digital Signature / Stamp**
  - **In App:** Upload authorized signatory stamp/signature for PDF invoice and quotation sign-offs.

- [ ] **Task 5.3: Select Brand Primary & Accent Colors**
  - **In App:** Confirm brand hex codes (Default: `#0047AB` Shah Cobalt Blue, `#FFBF00` Construction Gold).
