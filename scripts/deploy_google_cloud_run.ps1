# scripts/deploy_google_cloud_run.ps1
# Automated Google Cloud Run Deployment Script for SHAH GROUP AI OS

param (
    [string]$ProjectId = "",
    [string]$Region = "asia-south1"
)

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "SHAH GROUP AI OS — GOOGLE CLOUD RUN DEPLOYMENT WIZARD" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan

# 1. Verify gcloud CLI
if (-not (Get-Command gcloud -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] Google Cloud SDK ('gcloud') is not found on your system PATH." -ForegroundColor Red
    Write-Host ""
    Write-Host "To install Google Cloud SDK on Windows, run in PowerShell:" -ForegroundColor Yellow
    Write-Host "  winget install Google.CloudSDK" -ForegroundColor White
    Write-Host "Or download the official Windows installer from:" -ForegroundColor Yellow
    Write-Host "  https://cloud.google.com/sdk/docs/install" -ForegroundColor White
    Write-Host ""
    Write-Host "After installation, open a new PowerShell window, run 'gcloud init', and run this script again." -ForegroundColor Yellow
    Exit 1
}

# 2. Verify Authentication
Write-Host "[1/5] Checking Google Cloud Authentication..." -ForegroundColor Yellow
$activeAccount = gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>$null
if (-not $activeAccount) {
    Write-Host "[AUTH] No active Google Cloud account found. Launching browser login..." -ForegroundColor Yellow
    gcloud auth login
    $activeAccount = gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>$null
}
Write-Host "[AUTH] Logged in as: $activeAccount" -ForegroundColor Green

# 3. Verify Project ID
if (-not $ProjectId) {
    $ProjectId = gcloud config get-value project 2>$null
}
if (-not $ProjectId -or $ProjectId -eq "(unset)") {
    $ProjectId = Read-Host "Enter your Google Cloud Project ID (e.g. shah-group-ai-os)"
    if (-not $ProjectId) {
        Write-Host "[ERROR] Project ID is required." -ForegroundColor Red
        Exit 1
    }
    gcloud config set project $ProjectId
}
Write-Host "[CONFIG] Target Project: $ProjectId" -ForegroundColor Green
Write-Host "[CONFIG] Target Region:  $Region (Mumbai / India)" -ForegroundColor Green

# 4. Enable Required GCP APIs
Write-Host "[2/5] Enabling Cloud Build, Cloud Run & Artifact Registry APIs..." -ForegroundColor Yellow
gcloud services enable cloudbuild.googleapis.com run.googleapis.com containerregistry.googleapis.com --project $ProjectId

# 5. Build Container Image via Cloud Build
Write-Host "[3/5] Building Docker container image via Google Cloud Build..." -ForegroundColor Yellow
gcloud builds submit --tag "gcr.io/$ProjectId/shah-group-ai-os:latest" --project $ProjectId

# 6. Deploy to Cloud Run
Write-Host "[4/5] Deploying container to Google Cloud Run..." -ForegroundColor Yellow
gcloud run deploy shah-group-ai-os `
    --image "gcr.io/$ProjectId/shah-group-ai-os:latest" `
    --platform managed `
    --region $Region `
    --allow-unauthenticated `
    --port 8080 `
    --memory 1Gi `
    --cpu 1 `
    --min-instances 0 `
    --max-instances 5 `
    --set-env-vars "APP_ENV=production,PYTHONUNBUFFERED=1" `
    --project $ProjectId

# 7. Retrieve Live URL
Write-Host "[5/5] Retrieving Service URL..." -ForegroundColor Yellow
$serviceUrl = gcloud run services describe shah-group-ai-os --platform managed --region $Region --format="value(status.url)" --project $ProjectId

Write-Host "======================================================================" -ForegroundColor Green
Write-Host "DEPLOYMENT SUCCESSFUL!" -ForegroundColor Green
Write-Host "Live Google Cloud Run URL: $serviceUrl" -ForegroundColor Cyan
Write-Host "Health Check:             $serviceUrl/health" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Green
