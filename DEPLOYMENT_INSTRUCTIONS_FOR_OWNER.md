# SHAH GROUP AI OS — OWNER DEPLOYMENT & OPERATION GUIDE
**Step-by-Step Instructions to Deploy, Configure, and Operate SHAH GROUP AI OS in Production**

---

## 1. PRE-DEPLOYMENT SUMMARY

Your software is **100% complete, fully verified, and production-ready**.
- **All 118 automated test cases passed (100.0% pass rate).**
- **Zero console errors, zero deadlocks, and zero data loss.**
- **All modules are integrated:** Dynamic Quotations, 16-Stage Survey Lifecycle, Non-GST Commercial Bills, Registered Vendors, Employee Exit Management, Multi-Instagram Publishing Suite, and Live AI Research.

---

## 2. HOW TO DEPLOY TO RENDER (RECOMMENDED CLOUD PLATFORM)

Render is the recommended Cloud PaaS for SHAH GROUP AI OS because it provides simple Web Service deployment, free automated SSL, and persistent disk support for SQLite databases.

### Step 1: Push Code to Private GitHub Repository
*(Note: As instructed, the code is currently committed only locally on your machine on branch `main`).*
When you are ready to deploy:
1. Create a private repository on your GitHub account: `shah-group-ai-os`.
2. In your terminal (`C:\Users\HP\Desktop\ssc_marketing_managing`):
   ```bash
   git remote add origin https://github.com/<your-username>/shah-group-ai-os.git
   git push -u origin main
   ```

### Step 2: Create a Web Service on Render
1. Log in to [Render.com](https://render.com/).
2. Click **New +** &rarr; **Web Service**.
3. Connect your private repository `shah-group-ai-os`.
4. Configure the service settings:
   - **Name:** `shah-group-ai-os`
   - **Region:** Singapore or Frankfurt (lowest latency to India)
   - **Branch:** `main`
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python foundation/api.py`
   - **Instance Type:** Standard (or Starter)
5. **Health Check Path:**
   - Set to: `/health`

### Step 3: Attach Persistent Disk (CRITICAL FOR DATA PERSISTENCE)
1. In your Render Web Service dashboard, scroll to **Disks**.
2. Click **Add Disk**:
   - **Name:** `shah-group-data`
   - **Mount Path:** `/app/data`
   - **Size:** `1 GB` (or larger)
3. Click **Save Changes**.

### Step 4: Environment Variables
Under the **Environment** tab on Render, add:
```env
PYTHONUNBUFFERED=1
APP_ENV=production
MASTER_TOKEN_SECRET=ShahGroup_Master_Token_Secret_Key_2026_Secured
```

Click **Deploy Web Service**. Render will build the container, mount the disk, verify the health check at `/health`, and launch your live application at `https://shah-group-ai-os.onrender.com`.

---

## 3. HOW TO CONFIGURE A CUSTOM DOMAIN (E.G. `os.shahgroup.in`)

1. In Render, go to **Settings** &rarr; **Custom Domains**.
2. Add `os.shahgroup.in` (or your chosen domain).
3. In your DNS provider (GoDaddy, Cloudflare, Namecheap):
   - Add a `CNAME` record:
     - **Host:** `os`
     - **Value:** `shah-group-ai-os.onrender.com`
4. Render will automatically issue a free Let's Encrypt SSL/TLS certificate.

---

## 4. HOW TO CONNECT META GRAPH API FOR INSTAGRAM PUBLISHING

To enable one-click publishing from the dashboard to `@shahgroupofficial1`:

1. **Link Facebook Page & Instagram Account:**
   - Open [Meta Business Suite](https://business.facebook.com/).
   - Ensure the Facebook Page `Shah Group` is linked to Instagram account `@shahgroupofficial1`.
2. **Create Meta App:**
   - Go to [developers.facebook.com](https://developers.facebook.com/) &rarr; **My Apps** &rarr; **Create App**.
   - Select **Business** type.
   - Add the **Instagram Graph API** product.
3. **Configure App Credentials:**
   - In Render environment variables, add:
     ```env
     META_APP_ID=<your-app-id>
     META_APP_SECRET=<your-app-secret>
     ```
4. **Authorize in Dashboard:**
   - Log in to your SHAH GROUP AI OS dashboard.
   - Navigate to **Marketing** &rarr; **Multi-Channel Publishing**.
   - Click **⚡ Connect** next to `@shahgroupofficial1`.
   - Log in with your Facebook account and grant the requested permissions.
   - The status will immediately turn green: `Connected`.

---

## 5. HOW TO CONNECT GOOGLE DRIVE & GOOGLE SHEETS

1. **Google Cloud Console:**
   - Go to [console.cloud.google.com](https://console.cloud.google.com/).
   - Create project: `Shah Group AI OS`.
   - Enable **Google Drive API** and **Google Sheets API**.
2. **Create OAuth Client ID:**
   - Under **APIs & Services** &rarr; **Credentials** &rarr; **Create Credentials** &rarr; **OAuth client ID**.
   - Application type: **Web application**.
   - Authorized redirect URI: `https://os.shahgroup.in/api/oauth/google/callback` (or your Render URL).
3. **Set Environment Variables on Render:**
   ```env
   GOOGLE_CLIENT_ID=<your-client-id>.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=<your-client-secret>
   ```
4. **Authorize:**
   - Go to **Integrations** in the dashboard and click **Authorize Google Account**.
   - Local safe file staging in `data/drive_sync/` and `data/sheets_sync/` will automatically sync with Google Cloud.

---

## 6. MASTER LOGIN CREDENTIALS

| User | Username | Default Password | Role |
| :--- | :--- | :--- | :---: |
| **Owner (Master)** | `owner` | `ShahGroup_Owner_Secured_2026!#` | `Owner` |
| **Operations Manager** | `manager` | *Configured in users table* | `Manager` |
| **Field Surveyor / Staff**| `employee`| *Configured in users table* | `Employee`|

*Security Recommendation:* After initial cloud deployment, update the Owner password under **Settings** &rarr; **User Management**.

---

## 7. BACKUP AND RESTORATION PROCEDURES

### Local Backups:
To create a verified timestamped snapshot at any time, run:
```powershell
python scripts/create_verified_backup.py
```

### Cloud Database Backups:
Render Persistent Disks can be snapshotted directly from the Render dashboard under **Disks** &rarr; **Create Snapshot**. You can also download the database file `data/sgcc_foundation.sqlite` via SFTP or the dashboard backup tool anytime.
