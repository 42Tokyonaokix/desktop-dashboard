import os
import tempfile
from config import load_config


def test_load_config_from_file():
    content = """
location:
  latitude: 34.0
  longitude: 135.0
check_interval_min: 5
overlay:
  position: top_left
  opacity: 0.5
  font_size: 36
unsplash:
  access_key: "test_key"
yahoo:
  client_id: "yahoo_key"
cache:
  max_images: 30
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(content)
        f.flush()
        config = load_config(f.name)

    os.unlink(f.name)
    assert config["location"]["latitude"] == 34.0
    assert config["check_interval_min"] == 5
    assert config["unsplash"]["access_key"] == "test_key"


def test_load_config_uses_defaults_for_missing_keys():
    content = """
unsplash:
  access_key: "my_key"
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(content)
        f.flush()
        config = load_config(f.name)

    os.unlink(f.name)
    assert config["location"]["latitude"] == 35.6762
    assert config["check_interval_min"] == 10
    assert config["overlay"]["position"] == "bottom_right"
    assert config["cache"]["max_images"] == 50


def test_load_config_missing_file_returns_defaults():
    config = load_config("/nonexistent/path.yaml")
    assert config["location"]["latitude"] == 35.6762
    assert config["unsplash"]["access_key"] == ""


def test_load_config_has_obsidian_defaults():
    config = load_config("/nonexistent/path.yaml")
    assert "obsidian" in config
    assert config["obsidian"]["vault_dir"] == ""
    assert config["obsidian"]["tasks"]["max_items"] == 8
    assert config["obsidian"]["tasks"]["status"] == "todo"
    assert config["obsidian"]["tasks"]["priority"] == "high"
    assert config["obsidian"]["motivation_file"] == ""
    assert config["obsidian"]["check_interval_min"] == 5


def test_load_config_has_dashboard_defaults():
    config = load_config("/nonexistent/path.yaml")
    assert "dashboard" in config
    assert config["dashboard"]["width"] == 1500
    assert config["dashboard"]["height"] == 1000
    assert config["dashboard"]["sections"] == ["weather", "tasks", "motivation"]
    assert config["dashboard"]["section_weights"] == [30, 40, 30]
    assert config["dashboard"]["card_opacity"] == 0.6
    assert config["dashboard"]["font_size"] == 36
