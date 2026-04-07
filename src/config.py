"""Load and validate configuration from YAML file."""

import yaml
from pathlib import Path

DEFAULTS = {
    "location": {
        "latitude": 35.6762,
        "longitude": 139.6503,
    },
    "check_interval_min": 10,
    "overlay": {
        "position": "bottom_right",
        "opacity": 0.7,
        "font_size": 48,
    },
    "unsplash": {
        "access_key": "",
    },
    "yahoo": {
        "client_id": "",
    },
    "cache": {
        "max_images": 50,
    },
    "obsidian": {
        "vault_dir": "",
        "tasks": {
            "max_items": 8,
            "status": "todo",
            "priority": "high",
        },
        "motivation_file": "",
        "check_interval_min": 5,
    },
    "dashboard": {
        "width": 1500,
        "height": 1000,
        "sections": ["weather", "tasks", "motivation"],
        "section_weights": [30, 40, 30],
        "card_opacity": 0.6,
        "font_size": 36,
    },
}


def _deep_merge(base: dict, override: dict) -> dict:
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def load_config(path: str = "config.yaml") -> dict:
    config_path = Path(path)
    if not config_path.exists():
        return DEFAULTS.copy()

    with open(config_path, "r") as f:
        user_config = yaml.safe_load(f) or {}

    return _deep_merge(DEFAULTS, user_config)
