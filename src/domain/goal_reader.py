"""Read monthly goal file from Obsidian vault."""

import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

import yaml

from domain.models import GoalData

logger = logging.getLogger(__name__)


def _parse_goal_file(file_path: Path) -> Optional[GoalData]:
    """Parse a monthly goal markdown file."""
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

    # Extract theme from "## 今月のテーマ" section
    theme = ""
    theme_match = re.search(r"##\s*今月のテーマ\s*\n+>\s*(.+)", text)
    if theme_match:
        theme = theme_match.group(1).strip()

    # Extract goals from "## 目標" section
    goals = []
    goal_match = re.search(r"##\s*目標\s*\n([\s\S]*?)(?=\n##|\Z)", text)
    if goal_match:
        for line in goal_match.group(1).strip().split("\n"):
            line = line.strip()
            if line.startswith("- "):
                goals.append(line[2:].strip())

    return GoalData(title=title, theme=theme, goals=goals)


def read_monthly_goal(goal_dir: str) -> Optional[GoalData]:
    """Read the current month's goal file from the goal directory.

    Looks for a file named YYYY-MM.md matching the current month.
    Falls back to the most recent file if current month not found.
    """
    dir_path = Path(goal_dir)
    if not dir_path.is_dir():
        return None

    # Look for current month file
    current = datetime.now().strftime("%Y-%m")
    current_file = dir_path / f"{current}.md"
    if current_file.is_file():
        return _parse_goal_file(current_file)

    # Fallback: most recent YYYY-MM.md file
    candidates = sorted(dir_path.glob("????-??.md"), reverse=True)
    if candidates:
        return _parse_goal_file(candidates[0])

    return None
