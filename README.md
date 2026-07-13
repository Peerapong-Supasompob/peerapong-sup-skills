# peerapong-sup-skills

Personal agent skills for project workflows.

Each skill lives under `skills/` in its own directory with a `SKILL.md` file and any bundled scripts or reference files.

## Layout

- `.claude-plugin/plugin.json` - Claude-style plugin manifest
- `.codex-plugin/plugin.json` - Codex plugin manifest
- `scripts/` - helper scripts for listing, linking, and local configuration
- `skills/engineering/php-project-env/` - PHP `.env` loading with `vlucas/phpdotenv`
- `skills/productivity/redmine-issue-note/` - Redmine issue notes, issue operations, and time logging

## Install

After this repo is on GitHub:

```bash
npx skills add Peerapong-Supasompob/peerapong-sup-skills
```

## Local Dev Loop

Windows / Codex:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\link-codex-skills.ps1
```

macOS/Linux / Claude-style:

```bash
./scripts/link-skills.sh
```

List all skills:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\list-skills.ps1
```

```bash
./scripts/list-skills.sh
```

## Universal IDE Setup

Use one instruction path for Codex, Cursor, Antigravity, VS Code agents, Windsurf, Continue, and other IDE agents:

1. Keep the canonical skill source under `skills/`
2. Add a project-level instruction block to `<project>/AGENTS.md`
3. Ask the agent to read `AGENTS.md` before using the workflow

Install the Redmine instruction block into a target workspace:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install-agent-instructions.ps1 -WorkspacePath C:\path\to\project
```

or:

```bash
./scripts/install-agent-instructions.sh /path/to/project
```

The script creates or updates:

```text
<project>/AGENTS.md
```

For Cursor, if the agent does not load `AGENTS.md` automatically, reference it in the prompt:

```text
Read AGENTS.md and use the redmine-issue-note instructions.
```

For Antigravity, open the workspace that has `AGENTS.md` at the root.

## Redmine Config

Do not commit `.env` or API keys. Commit `.env.example` only.

Create the local Redmine `.env` after cloning:

```powershell
$env:REDMINE_API_KEY = "replace-with-real-key"
powershell -ExecutionPolicy Bypass -File .\scripts\config-redmine.ps1
```

or:

```bash
REDMINE_API_KEY="replace-with-real-key" ./scripts/config-redmine.sh
```

The config file is written to:

```text
skills/productivity/redmine-issue-note/.env
```

## Reference

### Engineering

- [php-project-env](./skills/engineering/php-project-env/SKILL.md) - Implement and debug PHP project `.env` loading with `vlucas/phpdotenv`, Docker paths, and safe secret verification.

### Productivity

- [redmine-issue-note](./skills/productivity/redmine-issue-note/SKILL.md) - Generate concise Thai Redmine content, create/update issues, and log spent time via Redmine API helper.
