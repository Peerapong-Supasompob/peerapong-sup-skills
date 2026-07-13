param(
  [Parameter(Mandatory = $true)]
  [string]$WorkspacePath
)

$ErrorActionPreference = "Stop"

$target = Join-Path $WorkspacePath "AGENTS.md"
$markerStart = "<!-- redmine-issue-note:start -->"
$markerEnd = "<!-- redmine-issue-note:end -->"
$blockBody = @'
# Redmine Issue Note

Use these instructions when the user mentions Redmine, Redmide, open work, issue notes, issue creation, issue updates, or spent time logging.

Canonical skill source in this repo:

```text
skills/productivity/redmine-issue-note/SKILL.md
```

Helper script:

```text
skills/productivity/redmine-issue-note/scripts/redmine_api_helper.py
```

Rules:

- Use `REDMINE_API_KEY` from environment or from `skills/productivity/redmine-issue-note/.env`
- Do not print or expose the API key
- Use base URL `https://mobileapp.nstda.or.th/redmine`
- Default open-work query is `85`
- Write Redmine prose in concise Thai
- Use Textile for Redmine `description` and `notes`
- Ask only for missing high-risk fields such as `project`, `tracker`, `issue_id`, or `hours`
- When performing the action, call the helper script instead of only drafting text
- After create/update success, include the issue URL `https://mobileapp.nstda.or.th/redmine/issues/<issue_id>`
- For spent time, report daily total and remaining hours only from API data

PowerShell example:

```powershell
& "$env:USERPROFILE\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" `
  .\skills\productivity\redmine-issue-note\scripts\redmine_api_helper.py `
  --base-url https://mobileapp.nstda.or.th/redmine list-projects --limit 200
```

Fallback:

```bash
python skills/productivity/redmine-issue-note/scripts/redmine_api_helper.py \
  --base-url https://mobileapp.nstda.or.th/redmine list-projects --limit 200
```
'@

$block = @(
  $markerStart
  $blockBody.TrimEnd()
  $markerEnd
) -join "`n"

if (-not (Test-Path -LiteralPath $WorkspacePath)) {
  throw "Workspace path does not exist: $WorkspacePath"
}

if (Test-Path -LiteralPath $target) {
  $existing = Get-Content -Raw -LiteralPath $target
  if ($existing.Contains($markerStart)) {
    $pattern = [regex]::Escape($markerStart) + ".*?" + [regex]::Escape($markerEnd)
    $updated = [regex]::Replace($existing, $pattern, $block, "Singleline")
    Set-Content -LiteralPath $target -Encoding UTF8 -Value $updated
  } else {
    Add-Content -LiteralPath $target -Encoding UTF8 -Value "`n$block"
  }
} else {
  Set-Content -LiteralPath $target -Encoding UTF8 -Value $block
}

Write-Host "Installed universal agent instructions: $target"

