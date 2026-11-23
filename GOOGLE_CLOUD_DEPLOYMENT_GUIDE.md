# SHAH GROUP AI OS — GOOGLE CLOUD DEPLOYMENT GUIDE
**Official Step-by-Step Architecture, Containerization & Production Deployment on Google Cloud Platform (GCP)**

---

## 1. EXECUTIVE SUMMARY

SHAH GROUP AI OS has been fully containerized and configured for native deployment on **Google Cloud Platform (GCP)**.

- **Primary Cloud Target:** **Google Cloud Run** (Fully managed serverless container platform)
- **Alternative Free Tier Target:** **Google Compute Engine (GCE)** `e2-micro` VM (Always Free Tier — \$0/month)
- **Container Base:** Python 3.11 Slim (`Dockerfile` included)
- **Default Cloud Port:** `8080` (Standard Google Cloud port; auto-configured via `PORT` environment variable)
- **Health Check Route:** `http://<cloud-url>/health`
- **Data Persistence:** `/app/data` mounted via Persistent Volume Mount / Cloud Storage FUSE.

---

## 2. PREREQUISITES

Before deploying to Google Cloud, ensure you have:
1. A **Google Cloud Account** ([console.cloud.google.com](https://console.cloud.google.com/)).
2. An active **Google Cloud Project** (e.g. `shah-group-ai-os`).
3. An active billing account (new accounts receive **\$300 Free Credits**, and Cloud Run includes **2 million requests/month permanently free**).

---

## 3. DEPLOYMENT METHODS

### METHOD 1: Web Console Deployment (Easiest — No Local Tools Needed)

You do not need to install `gcloud` or Docker on your laptop. You can deploy directly from your web browser:

1. Go to [Google Cloud Console](https://console.cloud.google.com/).
2. Select your Project (e.g., `shah-group-ai-os`).
3. In the top search bar, type **Cloud Run** and click on **Cloud Run**.
4. Click **Create Service** (or **Deploy Container**).
5. Configure the service:
   - **Service Name:** `shah-group-ai-os`
   - **Region:** `asia-south1 (Mumbai)` (lowest latency for India)
   - **CPU allocation and pricing:** CPU is only allocated during request processing.
   - **Ingress Control:** Select **All** (Allow direct access from the internet).
   - **Authentication:** Select **Allow unauthenticated invocations** (Public access for dashboard users).
6. Under **Container(s), Volumes, Networking, Security**:
   - **Container Port:** `8080`
   - **Memory:** `1 GiB`
   - **CPU:** `1`
   - **Execution environment:** Select **Second generation** (Recommended for file operations).
7. Under **Volumes & Mounts** (For SQLite Database Persistence):
   - Click **Add Volume** &rarr; Select **Cloud Storage bucket** (or Persistent Volume).
   - Mount path: `/app/data`
8. Click **Create / Deploy**.
9. Google Cloud will build and launch your service in ~60 seconds and provide an official HTTPS URL:
   `https://shah-group-ai-os-xxxxxx.a.run.app`

---

### METHOD 2: Deploy via Google Cloud Shell (Free In-Browser Terminal)

Google Cloud provides a free, pre-configured Linux terminal directly in your web browser:

1. Open [Google Cloud Console](https://console.cloud.google.com/).
2. In the top right corner, click the **Activate Cloud Shell** icon (`>_`).
3. Upload the project ZIP `SHAH_GROUP_AI_OS_COMPLETE.zip` (click the three dots `⋮` in Cloud Shell &rarr; **Upload**).
4. Run in Cloud Shell:
   ```bash
   unzip SHAH_GROUP_AI_OS_COMPLETE.zip
   cd SHAH_GROUP_AI_OS
   chmod +x scripts/deploy_google_cloud_run.sh
   ./scripts/deploy_google_cloud_run.sh
   ```
5. The automated script will enable Cloud APIs, build the container image, deploy to Cloud Run, and output your live service URL!

---

### METHOD 3: Deploy from Local Windows PC using Google Cloud SDK (`gcloud`)

If you want to deploy directly from your Windows command line:

#### Step 3.1: Install Google Cloud SDK
Open PowerShell as Administrator and run:
```powershell
winget install Google.CloudSDK
```
*Or download the installer from: [https://cloud.google.com/sdk/docs/install](https://cloud.google.com/sdk/docs/install)*

#### Step 3.2: Initialize and Log In
Open a new PowerShell terminal and authenticate:
```powershell
gcloud auth login
gcloud config set project <YOUR_PROJECT_ID>
```

#### Step 3.3: Run the Automated Deployment Script
In the project directory (`C:\Users\HP\Desktop\ssc_marketing_managing`):
```powershell
.\scripts\deploy_google_cloud_run.ps1
```

---

## 4. SQLITE DATABASE PERSISTENCE ON GOOGLE CLOUD

SHAH GROUP AI OS uses SQLite (`data/sgcc_foundation.sqlite`). To ensure all data persists across container restarts:

### Option A: Cloud Run Volume Mount (Recommended for Serverless)
Cloud Run allows mounting a Google Cloud Storage (GCS) bucket directly as a filesystem directory via Cloud Storage FUSE:
1. In Cloud Console, go to **Cloud Storage &rarr; Buckets** and create a bucket named `shah-group-data-bucket`.
2. In your Cloud Run service settings, add a volume pointing to `shah-group-data-bucket` and set Mount Path to `/app/data`.
3. SQLite writes and reads will be automatically synced to Google Cloud Storage.

### Option B: Google Compute Engine (GCE) e2-micro VM (Always Free Tier — \$0/month)
For 100% native SQLite disk performance without container volume abstraction, you can run on a GCE VM:
1. Create an `e2-micro` VM in region `us-central1` or `asia-south1`.
2. Under **Always Free**, Google provides 1 `e2-micro` VM + 30 GB standard persistent disk at **\$0.00/month**.
3. Install Python 3.11 on the VM and run `python foundation/api.py`.
4. Run `systemd` or `pm2` to keep the process running 24/7.

---

## 5. POST-DEPLOYMENT VERIFICATION

Once deployed, verify your live instance:
1. **Health Check:** Open `https://<your-service-url>/health`.
   - Expected response: `{"ok": true, "service": "SHAH-Group-AI-OS", "status": "healthy"}`
2. **Dashboard UI:** Open `https://<your-service-url>/`.
   - Log in using your Owner credentials.
3. **Google Integrations:** Go to **Integration & Sync** (`#integrations`) &rarr; Click **Connect with Google**.
   *(Ensure `https://<your-service-url>/api/oauth/google/callback` is added to your Authorized Redirect URIs in Google Cloud Console).*
