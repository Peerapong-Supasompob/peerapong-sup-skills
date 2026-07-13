#!/usr/bin/env bash
set -euo pipefail

API_KEY="${REDMINE_API_KEY:-${1:-}}"

if [ -z "$API_KEY" ]; then
  echo "Missing API key. Set REDMINE_API_KEY or pass it as the first argument." >&2
  exit 1
fi

REPO="$(cd "$(dirname "$0")/.." && pwd)"
SKILL_DIR="$REPO/skills/productivity/redmine-issue-note"
ENV_PATH="$SKILL_DIR/.env"

mkdir -p "$SKILL_DIR"
printf 'REDMINE_API_KEY=%s\n' "$API_KEY" > "$ENV_PATH"

echo "Wrote $ENV_PATH"
echo "Do not commit .env. Commit .env.example only."

