"""Read motivation comment from a markdown file in the Obsidian vault."""

import logging
from pathlib import Path
from typing import Optional

from domain.models import MotivationData

logger = logging.getLogger(__name__)


def read_motivation(file_path: str) -> Optional[MotivationData]:
    """Read motivation comment from a file. Returns None if file doesn't exist or is empty."""
    path = Path(file_path)
    if not path.is_file():
        return None

    try:
        text = path.read_text(encoding="utf-8").strip()
    except Exception:
        logger.warning("Failed to read motivation file: %s", file_path)
        return None

    if not text:
        return None

    return MotivationData(comment=text)
