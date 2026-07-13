param(
  [string]$ApiKey = $env:REDMINE_API_KEY
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($ApiKey)) {
  throw "Missing API key. Set `$env:REDMINE_API_KEY or pass -ApiKey."
}

$repo = Split-Path -Parent $PSScriptRoot
$skillDir = Join-Path $repo "skills\productivity\redmine-issue-note"
$envPath = Join-Path $skillDir ".env"

New-Item -ItemType Directory -Force -Path $skillDir | Out-Null
Set-Content -LiteralPath $envPath -Encoding UTF8 -Value @(
  "REDMINE_API_KEY=$ApiKey"
)

Write-Host "Wrote $envPath"
Write-Host "Do not commit .env. Commit .env.example only."

