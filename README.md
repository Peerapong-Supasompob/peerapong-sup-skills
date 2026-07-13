# redmine-skills

Agent skills for Redmine issue notes, issue operations, and time logging.

โครง repo นี้เก็บ skill ทุกตัวไว้ใต้ `skills/` โดยแต่ละ skill เป็น directory ของตัวเองและมี `SKILL.md` พร้อมไฟล์ประกอบ เช่น helper scripts หรือ reference files.

## Layout

- `.claude-plugin/plugin.json` - plugin manifest แบบ repo ตัวอย่าง
- `.codex-plugin/plugin.json` - plugin manifest สำหรับ Codex
- `scripts/` - scripts สำหรับ list/link/config skill
- `skills/productivity/redmine-issue-note/` - Redmine skill

## Install

### จาก GitHub

หลัง push repo ขึ้น GitHub แล้วติดตั้งได้ด้วย:

```bash
npx skills add <github-user>/<repo-name>
```

ตัวอย่าง:

```bash
npx skills add your-org/redmine-skills
```

### Local dev loop

Windows / Codex:

```powershell
.\scripts\link-codex-skills.ps1
```

ถ้าเครื่องบล็อก PowerShell scripts ให้เรียกแบบนี้:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\link-codex-skills.ps1
```

macOS/Linux / Claude-style:

```bash
./scripts/link-skills.sh
```

ดูรายการ skill ทั้งหมด:

```bash
./scripts/list-skills.sh
```

หรือบน PowerShell:

```powershell
.\scripts\list-skills.ps1
```

ถ้าเครื่องบล็อก PowerShell scripts:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\list-skills.ps1
```

## Universal IDE Setup

ใช้แนวทางเดียวสำหรับ Codex, Cursor, Antigravity, VS Code agents, Windsurf, Continue และ IDE/agent อื่น ๆ:

1. เก็บ skill ตัวจริงไว้ที่ `skills/productivity/redmine-issue-note/`
2. เพิ่ม instruction block กลางลงใน `<project>/AGENTS.md`
3. ให้ agent อ่าน `AGENTS.md` แล้วเรียก helper script จาก path เดียวกัน

ติดตั้ง instruction block เข้า workspace ปลายทาง:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install-agent-instructions.ps1 -WorkspacePath C:\path\to\project
```

หรือบน macOS/Linux:

```bash
./scripts/install-agent-instructions.sh /path/to/project
```

สคริปต์จะสร้างหรืออัปเดต:

```text
<project>/AGENTS.md
```

สำหรับ Cursor ถ้า agent ไม่ดึง `AGENTS.md` อัตโนมัติ ให้แนบหรืออ้างถึงไฟล์นี้ใน prompt เช่น:

```text
Read AGENTS.md and use the redmine-issue-note instructions.
```

สำหรับ Antigravity ให้เปิด workspace ที่มี `AGENTS.md` อยู่ที่ root.

## Redmine Config

อย่า commit `.env` หรือ API key ขึ้น GitHub ให้ commit เฉพาะ `.env.example`

ตั้งค่า local `.env` หลัง clone:

```powershell
$env:REDMINE_API_KEY = "replace-with-real-key"
.\scripts\config-redmine.ps1
```

ถ้าเครื่องบล็อก PowerShell scripts:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\config-redmine.ps1
```

หรือส่ง key ตรง ๆ:

```powershell
.\scripts\config-redmine.ps1 -ApiKey "replace-with-real-key"
```

บน macOS/Linux:

```bash
REDMINE_API_KEY="replace-with-real-key" ./scripts/config-redmine.sh
```

ไฟล์ config จะถูกเขียนที่:

```text
skills/productivity/redmine-issue-note/.env
```

## Reference

### Productivity

- [redmine-issue-note](./skills/productivity/redmine-issue-note/SKILL.md) - Generate concise Thai Redmine content, create/update issues, and log spent time via Redmine API helper.
