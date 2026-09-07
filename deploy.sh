#!/usr/bin/env bash
set -e

echo "🎬 Deploying Studio Ops Copilot to Google Cloud Run..."

PROJECT_ID=$(gcloud config get-value project 2>/dev/null || echo "")
if [ -z "$PROJECT_ID" ]; then
  echo "Error: Google Cloud project not set. Run 'gcloud config set project <PROJECT_ID>' first."
  exit 1
fi

SERVICE_NAME="studio-ops-copilot"
REGION="us-central1"

echo "Project: $PROJECT_ID"
echo "Service: $SERVICE_NAME"
echo "Region:  $REGION"

# Submit build to Cloud Build and deploy to Cloud Run
gcloud builds submit --config cloudbuild.yaml .

URL=$(gcloud run services describe $SERVICE_NAME --platform managed --region $REGION --format 'value(status.url)')
echo "✅ Deployed successfully!"
echo "🚀 Public URL: $URL"
