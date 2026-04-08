"""Read weekly/monthly goal file from Obsidian vault."""

import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

import yaml

from domain.models import GoalData, ProjectGoal, ScheduleItem

logger = logging.getLogger(__name__)

_WEEKDAY_NAMES = ["月", "火", "水", "木", "金", "土", "日"]


def _parse_goal_file(file_path: Path) -> Optional[GoalData]:
    """Parse a weekly/monthly goal markdown file."""
    try:
        text = file_path.read_text(encoding="utf-8")
    except Exception:
        logger.warning("Failed to read goal file: %s", file_path)
        return None

    # Parse frontmatter for title
    title = file_path.stem
    if text.startswith("---"):
        end = text.find("---", 3)
        if end != -1:
            try:
                fm = yaml.safe_load(text[3:end])
                if fm and "title" in fm:
                    title = fm["title"]
            except yaml.YAMLError:
                pass

    # Extract theme
    theme = ""
    theme_match = re.search(r"##\s*今[月週]のテーマ\s*\n+>\s*(.+)", text)
    if theme_match:
        theme = theme_match.group(1).strip()

    # Extract project goals from "## 目標" section
    project_goals = _parse_project_goals(text)

    # Extract tasks from "## タスク" section
    tasks = _parse_tasks(text)

    # Extract today's schedule from "## 日別スケジュール" section
    today_schedule = _parse_today_schedule(text)

    return GoalData(
        title=title,
        theme=theme,
        project_goals=project_goals,
        tasks=tasks,
        today_schedule=today_schedule,
    )


def _parse_project_goals(text: str) -> list[ProjectGoal]:
    """Parse project-grouped goals from ## 目標 section."""
    goal_match = re.search(r"##\s*目標\s*\n([\s\S]*?)(?=\n## |\Z)", text)
    if not goal_match:
        return []

    section = goal_match.group(1)
    projects = []
    current_project = None
    current_goals = []

    for line in section.split("\n"):
        # ### or #### project name
        header_match = re.match(r"#{3,4}\s+(.+)", line)
        if header_match:
            if current_project is not None:
                projects.append(ProjectGoal(project=current_project, goals=current_goals))
            current_project = header_match.group(1).strip()
            current_goals = []
        elif line.strip().startswith("- ") and current_project is not None:
            current_goals.append(line.strip()[2:].strip())

    if current_project is not None:
        projects.append(ProjectGoal(project=current_project, goals=current_goals))

    return projects


def _parse_tasks(text: str) -> list[str]:
    """Parse tasks from ## タスク section."""
    task_match = re.search(r"##\s*タスク\s*\n([\s\S]*?)(?=\n## |\Z)", text)
    if not task_match:
        return []

    tasks = []
    for line in task_match.group(1).split("\n"):
        line = line.strip()
        if line.startswith("- "):
            tasks.append(line[2:].strip())

    return tasks


def _parse_today_schedule(text: str) -> list[ScheduleItem]:
    """Parse today's schedule from ## 日別スケジュール section."""
    schedule_match = re.search(r"##\s*日別スケジュール\s*\n([\s\S]*?)(?=\n## |\Z)", text)
    if not schedule_match:
        return []

    section = schedule_match.group(1)
    today_weekday = _WEEKDAY_NAMES[datetime.now().weekday()]

    # Find today's day block (### 月, ### 火, etc.)
    day_pattern = rf"###\s*{re.escape(today_weekday)}\s*\([^)]*\)\s*\n([\s\S]*?)(?=\n### |\Z)"
    day_match = re.search(day_pattern, section)
    if not day_match:
        return []

    items = []
    day_block = day_match.group(1)
    current_time = None

    for line in day_block.split("\n"):
        # Time slot line: - HH:MM
        time_match = re.match(r"^-\s*(\d{2}:\d{2})\s*$", line.strip())
        if time_match:
            current_time = time_match.group(1)
            continue

        # Indented description under a time slot
        desc_line = line.strip()
        if desc_line.startswith("- "):
            desc_line = desc_line[2:].strip()

        if desc_line and current_time:
            items.append(ScheduleItem(time=current_time, description=desc_line))

    return items


def read_monthly_goal(goal_dir: str) -> Optional[GoalData]:
    """Read the current week/month goal file from the goal directory."""
    dir_path = Path(goal_dir)
    if not dir_path.is_dir():
        return None

    # Look for current month file (YYYY-MM.md)
    current_month = datetime.now().strftime("%Y-%m")
    current_month_file = dir_path / f"{current_month}.md"
    if current_month_file.is_file():
        return _parse_goal_file(current_month_file)

    # Look for current week file (YYYY-WNN.md)
    current_week = datetime.now().strftime("%Y-W%V")
    current_week_file = dir_path / f"{current_week}.md"
    if current_week_file.is_file():
        return _parse_goal_file(current_week_file)

    # Fallback: most recent .md file
    candidates = sorted(
        [f for f in dir_path.glob("????-*.md") if f.name != "TEMPLATE.md"],
        reverse=True,
    )
    if candidates:
        return _parse_goal_file(candidates[0])

    return None
