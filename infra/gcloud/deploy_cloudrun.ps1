param(
  [string]$ProjectId,
  [string]$Region = "us-central1",
  [string]$ServiceName = "holonet-api"
)

if (-not $ProjectId) {
  Write-Host "Usage: .\\deploy_cloudrun.ps1 -ProjectId <gcp-project-id> [-Region us-central1] [-ServiceName holonet-api]"
  exit 1
}

gcloud config set project $ProjectId

gcloud run deploy $ServiceName `
  --source . `
  --region $Region `
  --clear-base-image `
  --allow-unauthenticated `
  --set-env-vars SWAPI_BASE_URL=https://swapi.dev/api,CACHE_TTL_SECONDS=180,CACHE_BACKEND=inmemory,HTTP_TIMEOUT_SECONDS=6,HTTP_RETRIES=2,MAX_PAGE_SIZE=50,MAX_UPSTREAM_PAGES=6,MAX_EXPAND_CONCURRENCY=8,REQUIRE_API_KEY=false

Write-Host "Deployed. Attach API Gateway with API key enforcement."
