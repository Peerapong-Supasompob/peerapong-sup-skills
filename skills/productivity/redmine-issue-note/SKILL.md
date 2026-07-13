---
name: redmine-issue-note
description: Generate concise Thai Redmine content and operate Redmine issues from conversation context. Use when the user asks to write, summarize, format, prepare, create, update, or log time in Redmine issues, including issue notes, bug notes, QA notes, UAT notes, implementation summaries, opening a new issue, updating an issue by number, creating spent time entries, listing Redmine metadata, or tracking non-project organizational work.
---

# Redmine Issue Note

Use this skill when the user mentions Redmine, Redmide, open work, issue notes, issue creation, issue updates, or spent time logging.

Use the bundled helper script:

```text
scripts/redmine_api_helper.py
```

The helper loads `REDMINE_API_KEY` from:

1. `.env` in the current working directory
2. `.env` in this skill directory

Keep `.env` out of git. Commit only `.env.example`.

## Default Redmine

- Base URL: `https://mobileapp.nstda.or.th/redmine`
- Default open-work query: `85`
- API key variable: `REDMINE_API_KEY`
- Default day target for time entries: `8` hours

## Core Workflow

1. Infer the user's intent first: `draft note`, `create issue`, `update issue`, `log time`, or `list metadata`.
2. Reuse conversation context. Ask only for missing high-risk fields such as `project`, `tracker`, `issue_id`, or `hours`.
3. When the user says to do the action now, create payloads and call `scripts/redmine_api_helper.py` instead of replying with draft text only.
4. After every successful create or update action, include a clickable Redmine issue link using the issue id.
5. Keep Redmine prose concise, in Thai, and use Textile for `description` or `notes`.

## Script Invocation

Prefer the active runtime Python when available. On Codex Desktop, the bundled runtime often lives at:

```powershell
& "$env:USERPROFILE\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" `
  .\skills\productivity\redmine-issue-note\scripts\redmine_api_helper.py `
  --base-url https://mobileapp.nstda.or.th/redmine list-projects --limit 200
```

Fallback to system Python:

```bash
python skills/productivity/redmine-issue-note/scripts/redmine_api_helper.py \
  --base-url https://mobileapp.nstda.or.th/redmine list-projects --limit 200
```

## Modes

### Draft Note

Return:

- `Subject` as plain text
- `Description` as Textile
- `Comment Spent time` as plain text when relevant

### Create Issue

Required fields:

- `project_id`
- `tracker_id`
- `subject`
- `description`

Useful optional fields:

- `assigned_to_id`
- `priority_id`
- `category_id`
- `fixed_version_id`
- `parent_issue_id`

If project default assignee causes API rejection, retry with current user as assignee when the user did not specify one.

When the user asks to summarize completed work, synthesize the issue `subject` and `description` from the actual conversation context. Do not copy the user's request text directly as placeholder content unless explicitly requested.

After success:

- Return the issue id
- Include `https://mobileapp.nstda.or.th/redmine/issues/<issue_id>`

### Update Issue

Supported updates:

- `notes`
- `subject`
- `description`
- `status_id`
- `assigned_to_id`
- `due_date`
- `done_ratio`
- `fixed_version_id`

Only update fields clearly supported by context.

Field discipline:

- If the user asks only to change the title or subject, update only `subject`
- Do not add `notes`, change `status`, set `due_date`, log time, or modify other fields unless explicitly asked
- After success, include the updated issue URL

### Log Time

Normal rule:

- Use an `issue_id`

Exceptions:

- Team meeting: log at project level to `ISSI-APS` (`team-ss`) without an issue
- Non-project organizational work: log to an approved organization-level project without an issue

Rules:

- If hours are missing, ask for hours
- Choose activity from work context
- Check day summary against the 8-hour target
- Report remaining hours only from API data

## Activity Guidance

Prefer these mappings when available in Redmine:

- `Development`: coding, implementing, fixing, refactoring
- `Testing`: testing, QA, UAT, verification
- `Meeting`: meetings, team syncs
- `Support`: support, coordination
- `Research`: analysis, investigation, study
- `Design`: design work
- `Report`: summary or reporting work

Use `list-activities` when uncertain.

## Metadata Helpers

Use these helper commands before risky operations:

- `list-projects`
- `list-trackers`
- `list-statuses`
- `list-activities`
- `get-issue`
- `summarize-day`

## Helper Examples

List projects:

```powershell
python .\skills\productivity\redmine-issue-note\scripts\redmine_api_helper.py `
  --base-url https://mobileapp.nstda.or.th/redmine list-projects --limit 200
```

Log time to an issue:

```powershell
python .\skills\productivity\redmine-issue-note\scripts\redmine_api_helper.py `
  --base-url https://mobileapp.nstda.or.th/redmine log-time-smart `
  --spent-on 2026-07-13 --issue-id 12274 --hours 2 --summary "ทดสอบ flow create issue"
```

Log team meeting to project:

```powershell
python .\skills\productivity\redmine-issue-note\scripts\redmine_api_helper.py `
  --base-url https://mobileapp.nstda.or.th/redmine log-time-smart `
  --spent-on 2026-07-13 --project team-ss --hours 3 --summary "ประชุมทีม"
```

