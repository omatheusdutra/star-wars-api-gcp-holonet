#!/usr/bin/env bash
set -euo pipefail

PROJECT_ID="${1:-}"
REGION="${2:-us-central1}"
SERVICE_NAME="${3:-holonet-api}"

if [[ -z "$PROJECT_ID" ]]; then
  echo "Usage: ./deploy_cloudrun.sh <gcp-project-id> [region] [service-name]"
  exit 1
fi

gcloud config set project "$PROJECT_ID"

gcloud run deploy "$SERVICE_NAME" \
  --source . \
  --region "$REGION" \
  --clear-base-image \
  --no-allow-unauthenticated \
  --set-env-vars SWAPI_BASE_URL=https://swapi.dev/api,CACHE_TTL_SECONDS=180,CACHE_BACKEND=inmemory,HTTP_TIMEOUT_SECONDS=6,HTTP_RETRIES=2,MAX_PAGE_SIZE=50,MAX_UPSTREAM_PAGES=6,MAX_EXPAND_CONCURRENCY=8,REQUIRE_API_KEY=false

echo "Deployed. Attach API Gateway with API key enforcement."
