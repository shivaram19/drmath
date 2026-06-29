#!/usr/bin/env python3
"""Create GitHub issues from docs/project/vikram-drmath-backlog.md.

This script is idempotent: it skips labels/milestones/issues that already exist.
It requires the GitHub CLI (`gh`) to be installed and authenticated.
"""
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

REPO = "shivaram19/drmath"
BACKLOG_PATH = Path(__file__).resolve().parent.parent / "docs" / "project" / "vikram-drmath-backlog.md"

LABELS = [
    # type
    {"name": "type:FR", "color": "0E8A16", "description": "Functional requirement"},
    {"name": "type:NFR", "color": "0052CC", "description": "Non-functional requirement"},
    {"name": "type:bug", "color": "D73A4A", "description": "Bug"},
    {"name": "type:spike", "color": "F9D0C4", "description": "Research or time-boxed investigation"},
    {"name": "type:infra", "color": "BFD4F2", "description": "Infrastructure, tooling, or refactor"},
    {"name": "type:migration", "color": "C2E0C6", "description": "Data or code migration"},
    # priority
    {"name": "priority:critical", "color": "B60205", "description": "Blocks release"},
    {"name": "priority:high", "color": "D93F0B", "description": "High impact"},
    {"name": "priority:medium", "color": "FBCA04", "description": "Medium impact"},
    {"name": "priority:low", "color": "0E8A16", "description": "Low impact"},
    # module
    {"name": "module:pipeline", "color": "C5DEF5", "description": "Content generation pipeline"},
    {"name": "module:content", "color": "C5DEF5", "description": "Question banks and content"},
    {"name": "module:web", "color": "C5DEF5", "description": "Web UI and manager lab"},
    {"name": "module:pwa", "color": "C5DEF5", "description": "Progressive web app"},
    {"name": "module:backend", "color": "C5DEF5", "description": "Backend API and business logic"},
    {"name": "module:db", "color": "C5DEF5", "description": "Database schema and migrations"},
    {"name": "module:sync", "color": "C5DEF5", "description": "Offline sync and queue"},
    {"name": "module:messaging", "color": "C5DEF5", "description": "Telegram, WhatsApp, nudges"},
    {"name": "module:analytics", "color": "C5DEF5", "description": "Analytics and reporting"},
    {"name": "module:admin", "color": "C5DEF5", "description": "Admin and manager features"},
    {"name": "module:flutter", "color": "C5DEF5", "description": "Flutter mobile app"},
    {"name": "module:infra", "color": "C5DEF5", "description": "Deployment and infrastructure"},
    # status
    {"name": "status:blocked", "color": "B60205", "description": "Blocked by dependency or decision"},
    {"name": "status:in-review", "color": "FEF2C0", "description": "Under review"},
    {"name": "status:needs-design", "color": "FEF2C0", "description": "Needs design or ADR"},
]


def gh_api(args: List[str], method: str = "GET", payload: Optional[Dict] = None) -> Dict:
    """Run `gh api` and return parsed JSON."""
    cmd = ["gh", "api", f"repos/{REPO}/{args[0]}", "--method", method]
    for a in args[1:]:
        cmd.append(a)
    if payload is not None:
        for key, value in payload.items():
            cmd.extend(["-f", f"{key}={value}"])
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"gh api failed: {result.stderr.strip()}")
    if not result.stdout.strip():
        return {}
    return json.loads(result.stdout)


def list_existing_labels() -> List[str]:
    try:
        data = gh_api(["labels?per_page=100"])
        return [item["name"] for item in data]
    except RuntimeError as e:
        print(f"Warning: could not list labels: {e}")
        return []


def create_label(label: Dict) -> None:
    try:
        gh_api(
            ["labels"],
            method="POST",
            payload={
                "name": label["name"],
                "color": label["color"],
                "description": label["description"],
            },
        )
        print(f"  created label {label['name']}")
    except RuntimeError as e:
        if "already_exists" in str(e) or "422" in str(e):
            print(f"  label {label['name']} already exists")
        else:
            raise


def ensure_labels() -> None:
    print("Ensuring labels...")
    existing = set(list_existing_labels())
    for label in LABELS:
        if label["name"] in existing:
            print(f"  label {label['name']} already exists")
        else:
            create_label(label)


def list_existing_milestones() -> Dict[str, int]:
    try:
        data = gh_api(["milestones?state=all&per_page=100"])
        return {item["title"]: item["number"] for item in data}
    except RuntimeError as e:
        print(f"Warning: could not list milestones: {e}")
        return {}


def create_milestone(title: str) -> int:
    try:
        result = gh_api(
            ["milestones"],
            method="POST",
            payload={"title": title},
        )
        print(f"  created milestone {title}")
        return result["number"]
    except RuntimeError as e:
        if "already_exists" in str(e) or "422" in str(e):
            print(f"  milestone {title} already exists")
            milestones = list_existing_milestones()
            return milestones[title]
        raise


def ensure_milestones(milestone_titles: List[str]) -> Dict[str, int]:
    print("Ensuring milestones...")
    existing = list_existing_milestones()
    numbers = {}
    for title in milestone_titles:
        if title in existing:
            print(f"  milestone {title} already exists")
            numbers[title] = existing[title]
        else:
            numbers[title] = create_milestone(title)
    return numbers


def parse_backlog(path: Path) -> List[Dict]:
    """Parse the markdown backlog into issue dicts."""
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    issues: List[Dict] = []
    current_milestone: Optional[str] = None
    current_issue: Optional[Dict] = None
    body_lines: List[str] = []

    def close_current_issue() -> None:
        nonlocal current_issue, body_lines
        if current_issue is not None:
            current_issue["body"] = "\n".join(body_lines).strip()
            issues.append(current_issue)
            current_issue = None
        body_lines = []

    for line in lines:
        stripped = line.strip()

        # Detect milestone heading: ### v0.X — Title
        if stripped.startswith("### ") and "v0." in stripped:
            close_current_issue()
            current_milestone = stripped.replace("### ", "").strip()
            continue

        # Detect issue heading: #### ISSUE-XXX — Title
        if stripped.startswith("#### ISSUE-"):
            close_current_issue()
            match = re.match(r"####\s+(ISSUE-\d+)\s+—\s+(.+)", stripped)
            if match:
                issue_id, title = match.groups()
                current_issue = {
                    "issue_id": issue_id,
                    "title": f"{issue_id} — {title}",
                    "milestone": current_milestone,
                    "labels": [],
                    "body": "",
                }
            continue

        # Detect labels line
        if current_issue is not None and stripped.startswith("- **Labels:**"):
            labels_part = stripped.replace("- **Labels:**", "").strip()
            # Labels are comma-separated and may be wrapped in backticks
            current_issue["labels"] = [
                lab.strip().strip("`") for lab in labels_part.split(",") if lab.strip()
            ]
            continue

        # Accumulate body lines
        if current_issue is not None:
            body_lines.append(line)

    close_current_issue()
    return issues


def list_existing_open_issue_titles() -> List[str]:
    """Return titles of open issues to avoid duplicates."""
    try:
        # paginate through all open issues
        titles = []
        page = 1
        while True:
            data = gh_api([f"issues?state=open&per_page=100&page={page}"])
            if not data:
                break
            titles.extend(item["title"] for item in data)
            if len(data) < 100:
                break
            page += 1
        return titles
    except RuntimeError as e:
        print(f"Warning: could not list existing issues: {e}")
        return []


def create_issue(issue: Dict, milestone_numbers: Dict[str, int]) -> None:
    payload = {
        "title": issue["title"],
        "body": issue["body"],
        "labels": issue["labels"],
    }
    milestone_title = issue.get("milestone")
    if milestone_title and milestone_title in milestone_numbers:
        payload["milestone"] = milestone_numbers[milestone_title]

    cmd = ["gh", "api", f"repos/{REPO}/issues", "--method", "POST", "--input", "-"]
    result = subprocess.run(cmd, input=json.dumps(payload), capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"gh api failed: {result.stderr.strip()}")
    data = json.loads(result.stdout)
    print(f"  created #{data['number']}: {data['title']}")


def main() -> int:
    if not BACKLOG_PATH.exists():
        print(f"Backlog not found: {BACKLOG_PATH}", file=sys.stderr)
        return 1

    issues = parse_backlog(BACKLOG_PATH)
    if not issues:
        print("No issues found in backlog.")
        return 0

    print(f"Parsed {len(issues)} issues from backlog.\n")

    ensure_labels()
    milestone_titles = [issue["milestone"] for issue in issues if issue.get("milestone")]
    milestone_numbers = ensure_milestones(list(dict.fromkeys(milestone_titles)))

    print("\nChecking existing open issues...")
    existing_titles = set(list_existing_open_issue_titles())

    print(f"\nCreating {len(issues)} issues...")
    created = 0
    skipped = 0
    for issue in issues:
        if issue["title"] in existing_titles:
            print(f"  skipped (already open): {issue['title']}")
            skipped += 1
            continue
        try:
            create_issue(issue, milestone_numbers)
            created += 1
        except RuntimeError as e:
            print(f"  FAILED to create {issue['title']}: {e}", file=sys.stderr)

    print(f"\nDone: {created} created, {skipped} skipped.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
