#!/usr/bin/env bash
set -euo pipefail

PROJECT_ID="${1:-}"
REGION="${2:-us-central1}"
FUNCTION_NAME="${3:-holonet-api}"

if [[ -z "$PROJECT_ID" ]]; then
  echo "Usage: ./deploy.sh <gcp-project-id> [region] [function-name]"
  exit 1
fi

gcloud config set project "$PROJECT_ID"

gcloud functions deploy "$FUNCTION_NAME" \
  --gen2 \
  --runtime python311 \
  --region "$REGION" \
  --source . \
  --entry-point app \
  --trigger-http \
  --allow-unauthenticated \
  --set-env-vars PYTHONPATH=src,SWAPI_BASE_URL=https://swapi.dev/api,CACHE_TTL_SECONDS=300,CACHE_BACKEND=inmemory,HTTP_TIMEOUT_SECONDS=4,HTTP_RETRIES=2,MAX_PAGE_SIZE=50,MAX_UPSTREAM_PAGES=5,MAX_EXPAND_CONCURRENCY=8,REQUIRE_API_KEY=false

echo "Deployed. Attach API Gateway with API key enforcement."
