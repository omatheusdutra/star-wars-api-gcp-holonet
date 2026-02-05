param(
  [string]$ProjectId,
  [string]$Region = "us-central1",
  [string]$FunctionName = "holonet-api"
)

if (-not $ProjectId) {
  Write-Host "Usage: .\\deploy.ps1 -ProjectId <gcp-project-id> [-Region us-central1] [-FunctionName holonet-api]"
  exit 1
}

gcloud config set project $ProjectId

gcloud functions deploy $FunctionName `
  --gen2 `
  --runtime python311 `
  --region $Region `
  --source . `
  --entry-point app `
  --trigger-http `
  --allow-unauthenticated `
  --set-env-vars "PYTHONPATH=src,SWAPI_BASE_URL=https://swapi.dev/api,CACHE_TTL_SECONDS=300,CACHE_BACKEND=inmemory,HTTP_TIMEOUT_SECONDS=4,HTTP_RETRIES=2,MAX_PAGE_SIZE=50,MAX_UPSTREAM_PAGES=5,MAX_EXPAND_CONCURRENCY=8,REQUIRE_API_KEY=false"

Write-Host "Deployed. Attach API Gateway with API key enforcement."
