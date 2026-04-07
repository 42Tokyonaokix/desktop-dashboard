import os
import tempfile
from unittest.mock import MagicMock, patch
from infra.settings_window import SettingsWindow


def _make_config():
    return {
        "obsidian": {
            "vault_dir": "/tmp/vault",
            "check_interval_min": 5,
            "tasks": {"max_items": 8, "status": "todo", "priority": "high"},
            "motivation_file": "/tmp/vault/dashboard/motivation.md",
        },
        "dashboard": {
            "width": 1500, "height": 1000,
            "sections": ["weather", "tasks", "motivation"],
            "section_weights": [30, 40, 30],
            "card_opacity": 0.6, "font_size": 36,
        },
    }


def test_settings_window_can_be_instantiated():
    config = _make_config()
    on_update = MagicMock()
    on_save = MagicMock()
    sw = SettingsWindow(config, on_update_callback=on_update, on_save_callback=on_save)
    assert sw is not None
    assert sw._config == config


def test_settings_window_get_config_returns_current():
    config = _make_config()
    sw = SettingsWindow(config, on_update_callback=MagicMock(), on_save_callback=MagicMock())
    result = sw.get_config()
    assert result["dashboard"]["font_size"] == 36
    assert result["obsidian"]["tasks"]["max_items"] == 8


def test_settings_window_update_section_order():
    config = _make_config()
    sw = SettingsWindow(config, on_update_callback=MagicMock(), on_save_callback=MagicMock())
    sw.set_section_order(["tasks", "weather", "motivation"])
    assert sw._config["dashboard"]["sections"] == ["tasks", "weather", "motivation"]


def test_settings_window_toggle_section():
    config = _make_config()
    sw = SettingsWindow(config, on_update_callback=MagicMock(), on_save_callback=MagicMock())
    sw.toggle_section("tasks", enabled=False)
    assert "tasks" not in sw._config["dashboard"]["sections"]
    sw.toggle_section("tasks", enabled=True)
    assert "tasks" in sw._config["dashboard"]["sections"]
