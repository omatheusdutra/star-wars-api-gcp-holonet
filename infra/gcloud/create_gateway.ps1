param(
  [string]$ProjectId,
  [string]$Region = "us-central1",
  [string]$FunctionName = "holonet-api",
  [string]$GatewayApiId = "holonet-api",
  [string]$GatewayConfigId = "holonet-config",
  [string]$GatewayId = "holonet-gateway"
)

if (-not $ProjectId) {
  Write-Host "Usage: .\\create_gateway.ps1 -ProjectId <gcp-project-id> [-Region us-central1] [-FunctionName holonet-api] [-GatewayApiId holonet-api] [-GatewayConfigId holonet-config] [-GatewayId holonet-gateway]"
  exit 1
}

gcloud config set project $ProjectId

$FunctionUrl = gcloud functions describe $FunctionName --gen2 --region $Region --format="value(url)"
if (-not $FunctionUrl) {
  $FunctionUrl = gcloud functions describe $FunctionName --gen2 --region $Region --format="value(serviceConfig.uri)"
}
if (-not $FunctionUrl) {
  Write-Host "Could not resolve Cloud Function URL for $FunctionName in $Region."
  exit 1
}

$TempSpec = Join-Path $env:TEMP ("openapi-gateway-{0}.yaml" -f ([guid]::NewGuid().ToString()))
(Get-Content -Path "api\\openapi-gateway.yaml" -Raw).Replace('${backend_url}', $FunctionUrl) | Set-Content -Encoding UTF8 $TempSpec

try {
  gcloud api-gateway apis describe $GatewayApiId | Out-Null
} catch {
  gcloud api-gateway apis create $GatewayApiId
}

gcloud api-gateway api-configs create $GatewayConfigId `
  --api $GatewayApiId `
  --openapi-spec $TempSpec

gcloud api-gateway gateways describe $GatewayId --location $Region | Out-Null
if ($LASTEXITCODE -eq 0) {
  gcloud api-gateway gateways update $GatewayId `
    --api $GatewayApiId `
    --api-config $GatewayConfigId `
    --location $Region
} else {
  gcloud api-gateway gateways create $GatewayId `
    --api $GatewayApiId `
    --api-config $GatewayConfigId `
    --location $Region
}

$GatewayHost = gcloud api-gateway gateways describe $GatewayId --location $Region --format="value(defaultHostname)"
Write-Host ("Gateway host: https://{0}" -f $GatewayHost)
