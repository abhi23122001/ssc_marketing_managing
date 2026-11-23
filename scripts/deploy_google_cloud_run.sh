#!/usr/bin/env bash
# scripts/deploy_google_cloud_run.sh
# Automated Google Cloud Run Deployment Script for SHAH GROUP AI OS

set -e

REGION="${REGION:-asia-south1}"
PROJECT_ID="${PROJECT_ID:-$(gcloud config get-value project 2>/dev/null || true)}"

echo "======================================================================"
echo "SHAH GROUP AI OS — GOOGLE CLOUD RUN DEPLOYMENT WIZARD"
echo "======================================================================"

if ! command -v gcloud &> /dev/null; then
    echo "[ERROR] Google Cloud SDK ('gcloud') is not installed."
    echo "Install via: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

if [ -z "$PROJECT_ID" ] || [ "$PROJECT_ID" = "(unset)" ]; then
    read -p "Enter Google Cloud Project ID: " PROJECT_ID
    gcloud config set project "$PROJECT_ID"
fi

echo "[1/4] Enabling required APIs..."
gcloud services enable cloudbuild.googleapis.com run.googleapis.com containerregistry.googleapis.com --project "$PROJECT_ID"

echo "[2/4] Submitting build to Google Cloud Build..."
gcloud builds submit --tag "gcr.io/$PROJECT_ID/shah-group-ai-os:latest" --project "$PROJECT_ID"

echo "[3/4] Deploying container to Google Cloud Run..."
gcloud run deploy shah-group-ai-os \
    --image "gcr.io/$PROJECT_ID/shah-group-ai-os:latest" \
    --platform managed \
    --region "$REGION" \
    --allow-unauthenticated \
    --port 8080 \
    --memory 1Gi \
    --cpu 1 \
    --min-instances 0 \
    --max-instances 5 \
    --set-env-vars "APP_ENV=production,PYTHONUNBUFFERED=1" \
    --project "$PROJECT_ID"

echo "[4/4] Getting live service URL..."
SERVICE_URL=$(gcloud run services describe shah-group-ai-os --platform managed --region "$REGION" --format="value(status.url)" --project "$PROJECT_ID")

echo "======================================================================"
echo "DEPLOYMENT COMPLETE!"
echo "Live URL: $SERVICE_URL"
echo "Health:   $SERVICE_URL/health"
echo "======================================================================"
