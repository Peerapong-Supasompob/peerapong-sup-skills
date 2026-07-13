$ErrorActionPreference = "Stop"

$repo = Split-Path -Parent $PSScriptRoot
Get-ChildItem -Path $repo -Recurse -Filter SKILL.md |
  Where-Object { $_.FullName -notmatch "\\node_modules\\" } |
  ForEach-Object { $_.FullName.Substring($repo.Length + 1) } |
  Sort-Object

