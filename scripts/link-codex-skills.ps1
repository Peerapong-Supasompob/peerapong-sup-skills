$ErrorActionPreference = "Stop"

$repo = Split-Path -Parent $PSScriptRoot
$dest = Join-Path $env:USERPROFILE ".codex\skills"
New-Item -ItemType Directory -Force -Path $dest | Out-Null

Get-ChildItem -Path (Join-Path $repo "skills") -Recurse -Filter SKILL.md |
  Where-Object {
    $_.FullName -notmatch "\\node_modules\\" -and
    $_.FullName -notmatch "\\deprecated\\" -and
    $_.FullName -notmatch "\\in-progress\\" -and
    $_.FullName -notmatch "\\personal\\"
  } |
  ForEach-Object {
    $src = Split-Path -Parent $_.FullName
    $name = Split-Path -Leaf $src
    $target = Join-Path $dest $name

    if (Test-Path $target) {
      Remove-Item -LiteralPath $target -Recurse -Force
    }

    Copy-Item -LiteralPath $src -Destination $target -Recurse -Force
    Write-Host "linked $name -> $target"
  }

