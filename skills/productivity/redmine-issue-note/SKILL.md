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

The helper loads `REDMINE_API_KEY` from these sources, in order:

1. Existing process environment variable `REDMINE_API_KEY`
2. `.env` in this skill directory

The helper intentionally does not read project or workspace `.env` files. Keep the Redmine API key isolated in the `redmine-issue-note` skill directory.

If `REDMINE_API_KEY` is missing:

1. Ask the user for the Redmine API access key before attempting Redmine API actions.
2. When the user provides the key, add or update `REDMINE_API_KEY=<provided key>` in the `redmine-issue-note` skill directory's `.env`.
3. Do not print, summarize, or expose the key in responses or command output.
4. Keep `.env` out of git. Commit only `.env.example`.

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
6. For issue notes and work summaries, use the standard templates below unless the user asks for a different format.

## Draft vs Action

If the user asks for Redmine-formatted text but does not explicitly ask to update Redmine, only generate text in chat. Do not call the API.

Draft-only phrases include:

- "สรุปงานรูปแบบ Redmine"
- "ช่วยเขียน note สำหรับ Redmine"
- "ขอข้อความไปใส่ Redmine"
- "format เป็น Redmine"
- "เตรียมข้อความลงเวลา"

After a draft-only response, end with one short follow-up asking whether the user wants Codex to perform the Redmine action, for example:

```text
ต้องการให้ผมอัปเดต Redmine หรือ ลงเวลาทำงานให้เลยไหมครับ?
```

Only call the Redmine API when the user clearly confirms an action such as updating an issue, creating an issue, or logging time.

## Note Templates

Use these concise Thai Textile templates so Redmine updates are easy to scan. Keep bullets short and concrete. Remove unused placeholder lines instead of leaving filler text.

Format `Issue Note` for readability:

- Start with a short `Issue Note` label outside the code block.
- Put the note itself in one `textile` code block so it has a copy button.
- Use 3 short sections: summary, verification, notes.
- Keep each bullet to one idea and avoid long comma-heavy sentences.
- Prefer concrete files, modules, commands, and statuses over broad wording.
- Use `-` for empty notes or no remaining follow-up.

When a response includes both an issue note and spent-time detail, separate them into two copyable blocks:

1. `Issue Note` - the note/description content for Redmine.
2. `Spent Time Comment` - show time and activity outside the copyable block, then put only the detail text in a copyable block.

Do not merge `เวลาทำงาน` into the issue note block unless the user explicitly asks for a single combined note.

### General Work

Issue Note:

```textile
สรุปงาน

- [ทำอะไร]
- [แก้/ปรับส่วนไหน]
- [ผลลัพธ์ที่ได้]

การตรวจสอบ

- [ทดสอบ/ตรวจสอบอะไร]
- ผล: [ผ่าน/ไม่ผ่าน/รอทดสอบ]

หมายเหตุ

- [ข้อจำกัด/สิ่งที่ต้องตามต่อ ถ้าไม่มีใส่ -]
```

Spent Time Comment:

- เวลา: [x] ชม.
- Activity: [Development/Testing/Support/Research]
- รายละเอียด:

```textile
[รายละเอียดสำหรับ comment ตอนลงเวลา]
```

### Bug Fix

Issue Note:

```textile
สรุปบัค

- ปัญหา: [...]
- สาเหตุ: [...]
- การแก้ไข: [...]

การตรวจสอบ

- ทดสอบซ้ำกรณีที่พบปัญหาแล้ว: [...]
- ผล: [...]

หมายเหตุ

- [...]
```

Spent Time Comment:

- เวลา: [x] ชม.
- Activity: [Development/Testing/Support/Research]
- รายละเอียด:

```textile
[รายละเอียดสำหรับ comment ตอนลงเวลา]
```

### Security Review

Issue Note:

```textile
สรุปการแก้ไข Security Review

- ประเด็นที่พบ: [...]
- การแก้ไข: [...]
- ไฟล์/ส่วนที่ปรับ: [...]

การตรวจสอบ

- Security Review: [pass/fail]
- ตรวจ syntax/test: [...]

หมายเหตุ

- [...]
```

Spent Time Comment:

- เวลา: [x] ชม.
- Activity: [Development/Testing/Support/Research]
- รายละเอียด:

```textile
[รายละเอียดสำหรับ comment ตอนลงเวลา]
```

### Feature / Enhancement

Issue Note:

```textile
สรุปการพัฒนา

- เพิ่ม/ปรับฟีเจอร์: [...]
- ส่วนที่เกี่ยวข้อง: [...]
- ผลลัพธ์: [...]

การตรวจสอบ

- ทดสอบ flow หลัก: [...]
- ผล: [...]

หมายเหตุ

- [...]
```

Spent Time Comment:

- เวลา: [x] ชม.
- Activity: [Development/Testing/Support/Research]
- รายละเอียด:

```textile
[รายละเอียดสำหรับ comment ตอนลงเวลา]
```

### Time Entry Comment

```textile
[รายละเอียดสำหรับ comment ตอนลงเวลา]
```

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

