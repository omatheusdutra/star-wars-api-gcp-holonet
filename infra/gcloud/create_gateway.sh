#!/usr/bin/env bash
set -euo pipefail

PROJECT_ID="${1:-}"
REGION="${2:-us-central1}"
FUNCTION_NAME="${3:-holonet-api}"
GATEWAY_API_ID="${4:-holonet-api}"
GATEWAY_CONFIG_ID="${5:-holonet-config}"
GATEWAY_ID="${6:-holonet-gateway}"

if [[ -z "$PROJECT_ID" ]]; then
  echo "Usage: ./create_gateway.sh <gcp-project-id> [region] [function-name] [api-id] [config-id] [gateway-id]"
  exit 1
fi

gcloud config set project "$PROJECT_ID"

FUNCTION_URL="$(gcloud functions describe "$FUNCTION_NAME" --gen2 --region "$REGION" --format='value(url)')"
if [[ -z "$FUNCTION_URL" ]]; then
  FUNCTION_URL="$(gcloud functions describe "$FUNCTION_NAME" --gen2 --region "$REGION" --format='value(serviceConfig.uri)')"
fi
if [[ -z "$FUNCTION_URL" ]]; then
  echo "Could not resolve Cloud Function URL for $FUNCTION_NAME in $REGION."
  exit 1
fi

TMP_SPEC="$(mktemp)"
sed "s|\${backend_url}|$FUNCTION_URL|g" api/openapi-gateway.yaml > "$TMP_SPEC"

if ! gcloud api-gateway apis describe "$GATEWAY_API_ID" >/dev/null 2>&1; then
  gcloud api-gateway apis create "$GATEWAY_API_ID"
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
