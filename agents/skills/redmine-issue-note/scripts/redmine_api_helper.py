import argparse
import json
import os
from pathlib import Path
from urllib import error, request

DEFAULT_PROJECT_ROOTS = ("team-ss", "standard")
SKILL_ROOT = Path(__file__).resolve().parent.parent


def _load_dotenv() -> None:
    candidates = [
        SKILL_ROOT / ".env",
    ]

    for env_path in candidates:
        if not env_path.exists():
            continue

        for raw_line in env_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue

            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip("'").strip('"')

            if key and key not in os.environ:
                os.environ[key] = value


def _headers():
    _load_dotenv()
    api_key = os.getenv("REDMINE_API_KEY")
    if not api_key:
        raise SystemExit("Missing REDMINE_API_KEY. Put it in .env as REDMINE_API_KEY=<your_key>")
    return {
        "Content-Type": "application/json",
        "X-Redmine-API-Key": api_key,
    }


def _url(base_url: str, path: str) -> str:
    return f"{base_url.rstrip('/')}/{path.lstrip('/')}"


def _request(method: str, url: str, payload: dict | None = None) -> dict:
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    req = request.Request(url=url, data=body, headers=_headers(), method=method)
    try:
        with request.urlopen(req) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except error.HTTPError as exc:
        details = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"HTTP {exc.code}: {details}") from exc


def _get_current_user(base_url: str) -> dict:
    data = _request("GET", _url(base_url, "/users/current.json"))
    return data.get("user", {})


def _get_projects(base_url: str, limit: int = 200) -> list[dict]:
    data = _request("GET", _url(base_url, f"/projects.json?limit={limit}"))
    return data.get("projects", [])


def _resolve_project_id(base_url: str, project_ref: str) -> int:
    if project_ref.isdigit():
        return int(project_ref)
    for project in _get_projects(base_url):
        if project.get("identifier") == project_ref:
            return int(project["id"])
    raise SystemExit(f"Unknown project reference: {project_ref}")


def create_issue(base_url: str, payload_path: str) -> None:
    with open(payload_path, "r", encoding="utf-8") as fh:
        payload = json.load(fh)
    data = _request("POST", _url(base_url, "/issues.json"), payload)
    print(json.dumps(data, ensure_ascii=False, indent=2))


def update_issue(base_url: str, issue_id: int, payload_path: str) -> None:
    with open(payload_path, "r", encoding="utf-8") as fh:
        payload = json.load(fh)
    data = _request("PUT", _url(base_url, f"/issues/{issue_id}.json"), payload)
    print(json.dumps({"ok": True, "issue_id": issue_id, "response": data}, ensure_ascii=False, indent=2))


def get_issue(base_url: str, issue_id: int) -> None:
    data = _request("GET", _url(base_url, f"/issues/{issue_id}.json"))
    print(json.dumps(data, ensure_ascii=False, indent=2))


def add_time_entry(base_url: str, payload_path: str) -> None:
    with open(payload_path, "r", encoding="utf-8") as fh:
        payload = json.load(fh)
    data = _request("POST", _url(base_url, "/time_entries.json"), payload)
    print(json.dumps(data, ensure_ascii=False, indent=2))


def list_activities(base_url: str) -> None:
    data = _request("GET", _url(base_url, "/enumerations/time_entry_activities.json"))
    activities = [
        {
            "id": activity.get("id"),
            "name": activity.get("name"),
            "is_default": activity.get("is_default"),
            "active": activity.get("active"),
        }
        for activity in data.get("time_entry_activities", [])
    ]
    print(json.dumps(activities, ensure_ascii=False, indent=2))


def list_trackers(base_url: str) -> None:
    data = _request("GET", _url(base_url, "/trackers.json"))
    trackers = [
        {
            "id": tracker.get("id"),
            "name": tracker.get("name"),
            "default_status": tracker.get("default_status", {}).get("name"),
        }
        for tracker in data.get("trackers", [])
    ]
    print(json.dumps(trackers, ensure_ascii=False, indent=2))


def list_statuses(base_url: str) -> None:
    data = _request("GET", _url(base_url, "/issue_statuses.json"))
    statuses = [
        {
            "id": status.get("id"),
            "name": status.get("name"),
            "is_closed": status.get("is_closed"),
        }
        for status in data.get("issue_statuses", [])
    ]
    print(json.dumps(statuses, ensure_ascii=False, indent=2))


def summarize_day_data(base_url: str, spent_on: str, user_id: int | None, limit: int) -> dict:
    resolved_user_id = user_id or _get_current_user(base_url).get("id")
    if not resolved_user_id:
        raise SystemExit("Unable to resolve current user id")
    query = f"/time_entries.json?user_id={resolved_user_id}&spent_on={spent_on}&limit={limit}"
    data = _request("GET", _url(base_url, query))
    entries = data.get("time_entries", [])
    total_hours = sum(float(entry.get("hours", 0) or 0) for entry in entries)
    return {
        "spent_on": spent_on,
        "user_id": resolved_user_id,
        "target_hours": 8,
        "total_hours": total_hours,
        "remaining_hours": max(0.0, 8 - total_hours),
        "entries": [
            {
                "id": entry.get("id"),
                "issue_id": entry.get("issue", {}).get("id"),
                "issue_subject": entry.get("issue", {}).get("subject"),
                "project": entry.get("project", {}).get("name"),
                "activity": entry.get("activity", {}).get("name"),
                "hours": entry.get("hours"),
                "comments": entry.get("comments"),
            }
            for entry in entries
        ],
    }


def summarize_day(base_url: str, spent_on: str, user_id: int | None, limit: int) -> None:
    print(json.dumps(summarize_day_data(base_url, spent_on, user_id, limit), ensure_ascii=False, indent=2))


def _activity_name_map(base_url: str) -> dict[str, dict]:
    data = _request("GET", _url(base_url, "/enumerations/time_entry_activities.json"))
    return {
        str(activity.get("name", "")).strip().lower(): activity
        for activity in data.get("time_entry_activities", [])
    }


def _pick_activity(base_url: str, summary: str, explicit_activity: str | None) -> dict:
    activities = _activity_name_map(base_url)
    if explicit_activity:
        key = explicit_activity.strip().lower()
        if key in activities:
            return activities[key]
        if explicit_activity.isdigit():
            for activity in activities.values():
                if int(activity.get("id", 0) or 0) == int(explicit_activity):
                    return activity
        raise SystemExit(f"Unknown activity: {explicit_activity}")

    normalized = summary.strip().lower()
    keyword_map = [
        ("meeting", ("meeting", "ประชุม")),
        ("testing", ("test", "testing", "verify", "uat", "qa", "ทดสอบ", "ตรวจสอบ")),
        ("development", ("develop", "development", "code", "implement", "fix", "ปรับ", "แก้", "พัฒนา")),
        ("support", ("support", "ช่วย", "ซัพพอร์ต", "ประสาน")),
        ("research", ("research", "analysis", "analyze", "ศึกษา", "วิเคราะห์")),
        ("design", ("design", "ออกแบบ")),
        ("report", ("report", "สรุป", "รายงาน")),
    ]
    for activity_name, keywords in keyword_map:
        if any(keyword in normalized for keyword in keywords) and activity_name in activities:
            return activities[activity_name]
    if "development" in activities:
        return activities["development"]
    if activities:
        return next(iter(activities.values()))
    raise SystemExit("No active time entry activities available")


def log_time_smart(
    base_url: str,
    spent_on: str,
    hours: float,
    summary: str,
    issue_id: int | None,
    project_ref: str | None,
    activity_ref: str | None,
    limit: int,
) -> None:
    before = summarize_day_data(base_url, spent_on, None, limit)
    activity = _pick_activity(base_url, summary, activity_ref)
    time_entry = {
        "spent_on": spent_on,
        "hours": hours,
        "activity_id": activity.get("id"),
        "comments": summary,
    }
    if issue_id is not None:
        time_entry["issue_id"] = issue_id
    elif project_ref:
        time_entry["project_id"] = _resolve_project_id(base_url, project_ref)
    else:
        raise SystemExit("log-time-smart requires either --issue-id or --project")

    payload = {"time_entry": time_entry}
    result = _request("POST", _url(base_url, "/time_entries.json"), payload)
    after = summarize_day_data(base_url, spent_on, None, limit)
    response = {
        "selected_activity": {
            "id": activity.get("id"),
            "name": activity.get("name"),
        },
        "created": result.get("time_entry", result),
        "day_summary_before": before,
        "day_summary_after": after,
        "warning": None if after["total_hours"] >= 8 else f"Remaining {after['remaining_hours']} hours to reach 8",
    }
    print(json.dumps(response, ensure_ascii=False, indent=2))


def _project_is_under_roots(project: dict, projects_by_id: dict[int, dict], root_ids: set[int]) -> bool:
    current = project
    visited = set()
    while current:
        project_id = current.get("id")
        if project_id in root_ids:
            return True
        parent = current.get("parent")
        if not parent:
            return False
        parent_id = parent.get("id")
        if not parent_id or parent_id in visited:
            return False
        visited.add(parent_id)
        current = projects_by_id.get(parent_id)
    return False


def list_projects(base_url: str, limit: int, roots: list[str]) -> None:
    all_projects = _get_projects(base_url, limit)
    projects_by_id = {project.get("id"): project for project in all_projects if project.get("id") is not None}
    root_ids = {
        project.get("id")
        for project in all_projects
        if project.get("identifier") in roots and project.get("id") is not None
    }
    projects = [
        {
            "id": project.get("id"),
            "identifier": project.get("identifier"),
            "name": project.get("name"),
            "parent": project.get("parent", {}).get("name"),
        }
        for project in all_projects
        if not root_ids or _project_is_under_roots(project, projects_by_id, root_ids)
    ]
    print(json.dumps(projects, ensure_ascii=False, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description="Simple Redmine API helper")
    parser.add_argument("--base-url", required=True, help="Redmine base URL")
    sub = parser.add_subparsers(dest="command", required=True)

    p_create = sub.add_parser("create-issue")
    p_create.add_argument("--payload", required=True, help="Path to JSON payload")

    p_update = sub.add_parser("update-issue")
    p_update.add_argument("--issue-id", required=True, type=int)
    p_update.add_argument("--payload", required=True, help="Path to JSON payload")

    p_get = sub.add_parser("get-issue")
    p_get.add_argument("--issue-id", required=True, type=int)

    p_time = sub.add_parser("add-time-entry")
    p_time.add_argument("--payload", required=True, help="Path to JSON payload")

    sub.add_parser("list-activities")
    sub.add_parser("list-trackers")
    sub.add_parser("list-statuses")

    p_day = sub.add_parser("summarize-day")
    p_day.add_argument("--spent-on", required=True, help="Date in YYYY-MM-DD format")
    p_day.add_argument("--user-id", type=int, help="Redmine user id; defaults to current user")
    p_day.add_argument("--limit", type=int, default=100, help="Maximum number of time entries to read")

    p_time_smart = sub.add_parser("log-time-smart")
    p_time_smart.add_argument("--spent-on", required=True, help="Date in YYYY-MM-DD format")
    p_time_smart.add_argument("--hours", required=True, type=float, help="Hours to log")
    p_time_smart.add_argument("--summary", required=True, help="Work summary used for comments and activity inference")
    p_time_smart.add_argument("--issue-id", type=int, help="Target issue id")
    p_time_smart.add_argument("--project", help="Target project id or identifier when logging without issue")
    p_time_smart.add_argument("--activity", help="Explicit activity name or id")
    p_time_smart.add_argument("--limit", type=int, default=100, help="Maximum number of time entries to read for day summary")

    p_projects = sub.add_parser("list-projects")
    p_projects.add_argument("--limit", type=int, default=100, help="Maximum number of projects to return")
    p_projects.add_argument("--roots", nargs="+", default=list(DEFAULT_PROJECT_ROOTS), help="Root project identifiers to include with all descendants")

    args = parser.parse_args()

    if args.command == "create-issue":
        create_issue(args.base_url, args.payload)
    elif args.command == "update-issue":
        update_issue(args.base_url, args.issue_id, args.payload)
    elif args.command == "get-issue":
        get_issue(args.base_url, args.issue_id)
    elif args.command == "add-time-entry":
        add_time_entry(args.base_url, args.payload)
    elif args.command == "list-activities":
        list_activities(args.base_url)
    elif args.command == "list-trackers":
        list_trackers(args.base_url)
    elif args.command == "list-statuses":
        list_statuses(args.base_url)
    elif args.command == "summarize-day":
        summarize_day(args.base_url, args.spent_on, args.user_id, args.limit)
    elif args.command == "log-time-smart":
        log_time_smart(args.base_url, args.spent_on, args.hours, args.summary, args.issue_id, args.project, args.activity, args.limit)
    elif args.command == "list-projects":
        list_projects(args.base_url, args.limit, args.roots)
    else:
        raise SystemExit(f"Unknown command: {args.command}")


if __name__ == "__main__":
    main()
