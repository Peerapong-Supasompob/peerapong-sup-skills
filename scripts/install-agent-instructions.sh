#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 1 ]; then
  echo "usage: ./scripts/install-agent-instructions.sh /path/to/project" >&2
  exit 1
fi

WORKSPACE="$1"
TARGET="$WORKSPACE/AGENTS.md"
MARKER_START="<!-- redmine-issue-note:start -->"
MARKER_END="<!-- redmine-issue-note:end -->"
TMP_FILE="$(mktemp)"

if [ ! -d "$WORKSPACE" ]; then
  echo "Workspace path does not exist: $WORKSPACE" >&2
  exit 1
fi

cat > "$TMP_FILE" <<'EOF'
<!-- redmine-issue-note:start -->
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
<!-- redmine-issue-note:end -->
EOF

if [ -f "$TARGET" ] && grep -q "$MARKER_START" "$TARGET"; then
  awk -v start="$MARKER_START" -v end="$MARKER_END" -v repl="$TMP_FILE" '
    $0 == start {
      while ((getline line < repl) > 0) print line
      skip = 1
      next
    }
    $0 == end {
      skip = 0
      next
    }
    !skip { print }
  ' "$TARGET" > "$TARGET.tmp"
  mv "$TARGET.tmp" "$TARGET"
elif [ -f "$TARGET" ]; then
  {
    cat "$TARGET"
    echo
    cat "$TMP_FILE"
  } > "$TARGET.tmp"
  mv "$TARGET.tmp" "$TARGET"
else
  cp "$TMP_FILE" "$TARGET"
fi

rm -f "$TMP_FILE"
echo "Installed universal agent instructions: $TARGET"

