#!/bin/bash

set -e

PROJECT_ID="lgbtq-ai-prod"
REGION="us-central1"
REPO_NAME="demo-frontend-repo"
SERVICE_NAME="demo-frontend"
IMAGE_NAME="demo-frontend"
IMAGE_TAG="latest"
PLATFORM="managed"

echo "🔑 Setting GCP project and authenticating..."
gcloud config set project $PROJECT_ID
gcloud auth configure-docker $REGION-docker.pkg.dev

echo "✅ Enabling required GCP services..."
gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  compute.googleapis.com \
  containerregistry.googleapis.com

echo "📦 Creating Artifact Registry repo (if not exists)..."
gcloud artifacts repositories describe $REPO_NAME \
  --location=$REGION 2>/dev/null || \
gcloud artifacts repositories create $REPO_NAME \
  --repository-format=docker \
  --location=$REGION \
  --description="Docker repo for demo frontend"

echo "🐳 Creating a cross-platform builder for Docker..."
docker buildx create --use --name mybuilder || true
docker buildx inspect mybuilder --bootstrap

echo "🏗️ Building Docker image for linux/amd64..."
docker buildx build \
  --platform linux/amd64 \
  -t $REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/$IMAGE_NAME:$IMAGE_TAG \
  --push .

echo "☁️ Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image $REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/$IMAGE_NAME:$IMAGE_TAG \
  --platform $PLATFORM \
  --region $REGION \
  --allow-unauthenticated

echo "🌐 Fetching service URL..."
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
  --platform $PLATFORM \
  --region $REGION \
  --format='value(status.url)')

echo "🚀 Deployment complete! Visit your app at:"
echo "$SERVICE_URL"