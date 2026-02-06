#!/usr/bin/env bash
set -euo pipefail

PROJECT_ID="${1:-}"
REGION="${2:-us-central1}"
BACKEND_REF="${3:-holonet-api}"
GATEWAY_API_ID="${4:-holonet-api}"
GATEWAY_CONFIG_ID="${5:-holonet-config}"
GATEWAY_ID="${6:-holonet-gateway}"

if [[ -z "$PROJECT_ID" ]]; then
  echo "Usage: ./create_gateway.sh <gcp-project-id> [region] [function-name] [api-id] [config-id] [gateway-id]"
  exit 1
fi

gcloud config set project "$PROJECT_ID"

BACKEND_URL=""

# 1) Allow passing an explicit backend URL (Cloud Run / Cloud Functions / other).
if [[ "${BACKEND_REF}" =~ ^https?:// ]]; then
  BACKEND_URL="${BACKEND_REF}"
fi

# 2) Backward compatible: try resolving as Cloud Function name (Gen2).
if [[ -z "$BACKEND_URL" ]]; then
  BACKEND_URL="$(gcloud functions describe "$BACKEND_REF" --gen2 --region "$REGION" --format='value(url)' 2>/dev/null || true)"
  if [[ -z "$BACKEND_URL" ]]; then
    BACKEND_URL="$(gcloud functions describe "$BACKEND_REF" --gen2 --region "$REGION" --format='value(serviceConfig.uri)' 2>/dev/null || true)"
  fi
fi

# 3) If still empty, try resolving as Cloud Run service name.
if [[ -z "$BACKEND_URL" ]]; then
  BACKEND_URL="$(gcloud run services describe "$BACKEND_REF" --region "$REGION" --format='value(status.url)' 2>/dev/null || true)"
fi

if [[ -z "$BACKEND_URL" ]]; then
  echo "Could not resolve backend URL for '$BACKEND_REF' in $REGION."
  echo "Pass a Cloud Run URL (https://...) or a Cloud Run service name, or a Cloud Function name."
  exit 1
fi

TMP_SPEC="$(mktemp --suffix=.yaml)"
sed "s|\${backend_url}|$BACKEND_URL|g" api/openapi-gateway.yaml > "$TMP_SPEC"

if ! gcloud api-gateway apis describe "$GATEWAY_API_ID" >/dev/null 2>&1; then
  gcloud api-gateway apis create "$GATEWAY_API_ID"
fi

# Ensure config id is unique (API Gateway does not allow update)
if gcloud api-gateway api-configs describe "$GATEWAY_CONFIG_ID" --api "$GATEWAY_API_ID" >/dev/null 2>&1; then
  GATEWAY_CONFIG_ID="${GATEWAY_CONFIG_ID}-$(date +%Y%m%d%H%M%S)"
fi

gcloud api-gateway api-configs create "$GATEWAY_CONFIG_ID" \
  --api "$GATEWAY_API_ID" \
  --openapi-spec "$TMP_SPEC"

if ! gcloud api-gateway gateways describe "$GATEWAY_ID" --location "$REGION" >/dev/null 2>&1; then
  gcloud api-gateway gateways create "$GATEWAY_ID" \
    --api "$GATEWAY_API_ID" \
    --api-config "$GATEWAY_CONFIG_ID" \
    --location "$REGION"
else
  gcloud api-gateway gateways update "$GATEWAY_ID" \
    --api "$GATEWAY_API_ID" \
    --api-config "$GATEWAY_CONFIG_ID" \
    --location "$REGION"
fi

GATEWAY_HOST="$(gcloud api-gateway gateways describe "$GATEWAY_ID" --location "$REGION" --format='value(defaultHostname)')"
echo "Gateway host: https://$GATEWAY_HOST"
