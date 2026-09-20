# Sets up Google OAuth Client ID for WanderPath (local).
# You must create the Client ID in YOUR Google account — Google does not
# allow anyone else to mint one for your project.

$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent
$frontendEnv = Join-Path $root "frontend\.env.local"
$backendEnv = Join-Path $root "backend\.env"

Write-Host ""
Write-Host "=== WanderPath - Google OAuth setup ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Browser opens Google Cloud Console."
Write-Host "2. Create (or pick) a project."
Write-Host "3. APIs and Services > Credentials > Create Credentials > OAuth client ID"
Write-Host "4. Application type: Web application"
Write-Host "5. Authorized JavaScript origins:  http://localhost:3000"
Write-Host "6. Authorized redirect URIs:       http://localhost:3000"
Write-Host "7. Copy the Client ID (ends with .apps.googleusercontent.com)"
Write-Host ""

Start-Process "https://console.cloud.google.com/apis/credentials/oauthclient"

$clientId = Read-Host "Paste Google Client ID here"
$clientId = $clientId.Trim()
if (-not $clientId -or $clientId -notmatch '\.apps\.googleusercontent\.com$') {
  Write-Host "Invalid Client ID. Expected something ending with .apps.googleusercontent.com" -ForegroundColor Red
  exit 1
}

function Set-EnvKey([string]$path, [string]$key, [string]$value) {
  if (-not (Test-Path $path)) {
    Set-Content -Path $path -Value "$key=$value`n" -Encoding UTF8
    return
  }
  $lines = Get-Content $path
  $found = $false
  $out = foreach ($line in $lines) {
    if ($line -match "^$([regex]::Escape($key))=") {
      $found = $true
      "$key=$value"
    } else {
      $line
    }
  }
  if (-not $found) { $out += "$key=$value" }
  Set-Content -Path $path -Value ($out -join "`n") -Encoding UTF8
}

Set-EnvKey $frontendEnv "NEXT_PUBLIC_GOOGLE_CLIENT_ID" $clientId
Set-EnvKey $backendEnv "GOOGLE_CLIENT_ID" $clientId
Set-EnvKey $backendEnv "ALLOW_DEV_LOGIN" "true"

Write-Host ""
Write-Host "Saved to:" -ForegroundColor Green
Write-Host "  $frontendEnv"
Write-Host "  $backendEnv"
Write-Host ""
Write-Host "Restart BOTH servers (backend + frontend), then open http://localhost:3000/login"
Write-Host ""
