import pytest
from unittest.mock import MagicMock, patch
from PIL import Image

from weather_fetcher import WeatherData
from dock_app import generate_dock_icon, DockWeatherApp, ICON_SIZE


def _make_weather(code=0, temp=22.5):
    return WeatherData(
        temperature=temp,
        weather_code=code,
        wind_speed=3.2,
        temp_max=28.0,
        temp_min=18.0,
        precipitation_probability=10,
    )


def _make_mapping(icon="\u2600\ufe0f", description="\u5feb\u6674"):
    return {"icon": icon, "description": description, "category": "clear", "query": "clear blue sky"}


def test_generate_dock_icon_returns_correct_size():
    weather = _make_weather()
    mapping = _make_mapping()
    img = generate_dock_icon(weather, mapping)
    assert isinstance(img, Image.Image)
    assert img.size == (ICON_SIZE, ICON_SIZE)
    assert img.mode == "RGBA"


def test_generate_dock_icon_rain():
    weather = _make_weather(code=63, temp=9.6)
    mapping = _make_mapping(icon="\U0001f327\ufe0f", description="\u96e8")
    img = generate_dock_icon(weather, mapping)
    assert img.size == (ICON_SIZE, ICON_SIZE)


def test_update_display_stores_weather():
    mock_app = MagicMock()
    dock = DockWeatherApp(mock_app, interval_min=10)

    weather = _make_weather()
    mapping = _make_mapping()

    with patch("dock_app._set_dock_icon"):
        dock.update_display(weather, mapping)

    assert dock._weather == weather
    assert dock._mapping == mapping


def test_on_tick_calls_weather_app_tick():
    mock_app = MagicMock()
    dock = DockWeatherApp(mock_app, interval_min=10)
    dock._root = MagicMock()

    dock._on_tick()

    mock_app.tick.assert_called_once()
