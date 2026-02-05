param(
    [string]$LocalBaseUrl = "http://127.0.0.1:8000",
    [string]$GatewayHost = "",
    [string]$ApiKey = "",
    [string]$RunUrl = "",
    [switch]$SkipTests
)

$ErrorActionPreference = "Stop"

function Write-Section($title) {
    Write-Host "`n== $title ==" -ForegroundColor Cyan
}

function Invoke-Check($name, $url, $headers = $null) {
    try {
        $resp = Invoke-RestMethod -Uri $url -Headers $headers -TimeoutSec 60
        Write-Host "[OK] $name -> $url" -ForegroundColor Green
        return $true
    } catch {
        $status = $null
        try {
            $status = $_.Exception.Response.StatusCode.value__
        } catch {}
        if ($status) {
            Write-Host "[FAIL] $name -> $url (HTTP $status)" -ForegroundColor Red
        } else {
            Write-Host "[FAIL] $name -> $url ($($_.Exception.Message))" -ForegroundColor Red
        }
        return $false
    }
}

function Test-LocalPort($hostname, $port) {
    try {
        $client = New-Object System.Net.Sockets.TcpClient
        $client.Connect($hostname, $port)
        $client.Close()
        return $true
    } catch {
        return $false
    }
}

if (-not $SkipTests) {
    Write-Section "Lint & Tests"
    try { python -m ruff check src tests } catch { Write-Host "ruff check failed" -ForegroundColor Yellow }
    try { python -m ruff format src tests } catch { Write-Host "ruff format failed" -ForegroundColor Yellow }
    try { pytest -q } catch { Write-Host "pytest failed" -ForegroundColor Yellow }
}

Write-Section "Local API"
$localUri = [Uri]$LocalBaseUrl
$localHost = $localUri.Host
$localPort = $localUri.Port
if (Test-LocalPort $localHost $localPort) {
    Invoke-Check "Local /health" "$LocalBaseUrl/health"
    Invoke-Check "Local /films" "$LocalBaseUrl/films"
    Invoke-Check "Local /v1/search" "$LocalBaseUrl/v1/search?resource=people&q=luke"
} else {
    Write-Host "Local server not running on ${localHost}:${localPort}. Skipping Local API checks." -ForegroundColor Yellow
}

Write-Section "Cloud Run (IAM)"
if (-not $RunUrl) {
    try {
        $RunUrl = gcloud run services describe holonet-api --region us-central1 --format="value(status.url)"
    } catch {
        Write-Host "Run URL not provided and gcloud lookup failed. Skipping Cloud Run checks." -ForegroundColor Yellow
    }
}
if ($RunUrl) {
    try {
        $token = gcloud auth print-identity-token
        $auth = @{ Authorization = "Bearer $token" }
        Invoke-Check "Run /health" "$RunUrl/health" $auth
        Invoke-Check "Run /films" "$RunUrl/films" $auth
    } catch {
        Write-Host "Cloud Run checks failed: $($_.Exception.Message)" -ForegroundColor Yellow
    }
}

Write-Section "API Gateway (API Key)"
if (-not $ApiKey -and $env:HOLONET_API_KEY) {
    $ApiKey = $env:HOLONET_API_KEY
}

if ($GatewayHost -and $ApiKey) {
    $headers = @{ "x-api-key" = $ApiKey }
    Invoke-Check "Gateway /v1/health" "https://$GatewayHost/v1/health" $headers
    Invoke-Check "Gateway /films" "https://$GatewayHost/films" $headers
    Invoke-Check "Gateway /v1/search" "https://$GatewayHost/v1/search?resource=people&q=luke" $headers
} else {
    Write-Host "GatewayHost or ApiKey not provided. Skipping Gateway checks." -ForegroundColor Yellow
}

Write-Host "`nDone." -ForegroundColor Cyan
