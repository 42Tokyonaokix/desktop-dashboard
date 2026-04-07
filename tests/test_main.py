from unittest.mock import patch, MagicMock
from main import DashboardApp
from domain.models import WeatherData, TaskItem, MotivationData


def _make_config():
    return {
        "location": {"latitude": 35.6762, "longitude": 139.6503},
        "check_interval_min": 10,
        "weather": {"check_interval_min": 10},
        "overlay": {"position": "bottom_right", "opacity": 0.7, "font_size": 48},
        "unsplash": {"access_key": "test_key"},
        "yahoo": {"client_id": ""},
        "cache": {"max_images": 50},
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


def _make_weather(code=0, temp=22.5):
    return WeatherData(
        temperature=temp, weather_code=code, wind_speed=3.2,
        temp_max=28.0, temp_min=18.0, precipitation_probability=10,
    )


@patch("main.set_wallpaper")
@patch("main.render_dashboard")
@patch("main.ImageFetcher")
@patch("main.fetch_open_meteo")
@patch("main.read_tasks")
@patch("main.read_motivation")
@patch("main.load_config")
def test_tick_all_fetches_weather_tasks_and_renders(
    mock_config, mock_motivation, mock_tasks, mock_fetch,
    mock_image_cls, mock_render, mock_set
):
    mock_config.return_value = _make_config()
    mock_fetch.return_value = _make_weather()
    mock_tasks.return_value = [
        TaskItem(title="Task 1", file_path="/a.md", priority="high",
                 status="todo", progress="0/1", tags=[]),
    ]
    mock_motivation.return_value = MotivationData(comment="Keep going!")
    mock_image_instance = MagicMock()
    mock_image_instance.get_image.return_value = "/tmp/base.jpg"
    mock_image_cls.return_value = mock_image_instance
    mock_render.return_value = "/tmp/output.jpg"
    mock_set.return_value = True

    app = DashboardApp()
    app.tick_all()

    mock_fetch.assert_called_once()
    mock_tasks.assert_called_once()
    mock_motivation.assert_called_once()
    mock_render.assert_called_once()
    mock_set.assert_called_once()


@patch("main.set_wallpaper")
@patch("main.render_dashboard")
@patch("main.ImageFetcher")
@patch("main.fetch_open_meteo")
@patch("main.read_tasks")
@patch("main.read_motivation")
@patch("main.load_config")
def test_tick_weather_only_updates_weather(
    mock_config, mock_motivation, mock_tasks, mock_fetch,
    mock_image_cls, mock_render, mock_set
):
    mock_config.return_value = _make_config()
    mock_fetch.return_value = _make_weather()
    mock_tasks.return_value = []
    mock_motivation.return_value = None
    mock_image_instance = MagicMock()
    mock_image_instance.get_image.return_value = "/tmp/base.jpg"
    mock_image_cls.return_value = mock_image_instance
    mock_render.return_value = "/tmp/output.jpg"
    mock_set.return_value = True

    app = DashboardApp()
    app.tick_all()  # initial
    mock_fetch.reset_mock()

    mock_fetch.return_value = _make_weather(temp=25.0)
    app.tick_weather()

    mock_fetch.assert_called_once()
