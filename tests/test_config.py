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
