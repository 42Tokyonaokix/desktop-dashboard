"""Read task files from Obsidian vault directory."""

import logging
from pathlib import Path
from typing import Optional

import yaml

from domain.models import TaskItem

logger = logging.getLogger(__name__)


def _parse_frontmatter(file_path: Path) -> Optional[dict]:
    """Parse YAML frontmatter from a markdown file."""
    try:
        text = file_path.read_text(encoding="utf-8")
    except Exception:
        logger.warning("Failed to read file: %s", file_path)
        return None

    if not text.startswith("---"):
        return None

    end = text.find("---", 3)
    if end == -1:
        return None

    try:
        return yaml.safe_load(text[3:end])
    except yaml.YAMLError:
        logger.warning("Failed to parse frontmatter: %s", file_path)
        return None


def read_tasks(
    vault_dir: str,
    status: str = "todo",
    priority: str = "high",
    max_items: int = 8,
) -> list[TaskItem]:
    """Read task files matching status and priority filters."""
    dir_path = Path(vault_dir)
    if not dir_path.is_dir():
        return []

    tasks: list[TaskItem] = []

    for md_file in sorted(dir_path.rglob("*.md")):
        fm = _parse_frontmatter(md_file)
        if fm is None:
            continue

        file_status = str(fm.get("status", "")).strip().lower()
        file_priority = str(fm.get("priority", "")).strip().lower()

        if file_status != status.lower() or file_priority != priority.lower():
            continue

        tasks.append(TaskItem(
            title=fm.get("title", md_file.stem),
            file_path=str(md_file),
            priority=fm.get("priority", ""),
            status=fm.get("status", ""),
            progress=str(fm.get("progress", "")),
            tags=fm.get("tags", []) or [],
        ))

        if len(tasks) >= max_items:
            break

    return tasks
