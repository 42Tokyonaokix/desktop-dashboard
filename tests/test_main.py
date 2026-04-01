from unittest.mock import patch, MagicMock
from main import WeatherWallpaperApp
from weather_fetcher import WeatherData


def _make_config():
    return {
        "location": {"latitude": 35.6762, "longitude": 139.6503},
        "check_interval_min": 10,
        "overlay": {"position": "bottom_right", "opacity": 0.7, "font_size": 48},
        "unsplash": {"access_key": "test_key"},
        "yahoo": {"client_id": ""},
        "cache": {"max_images": 50},
    }


def _make_weather(code=0, temp=22.5):
    return WeatherData(
        temperature=temp,
        weather_code=code,
        wind_speed=3.2,
        temp_max=28.0,
        temp_min=18.0,
        precipitation_probability=10,
    )


@patch("main.set_wallpaper")
@patch("main.render_overlay")
@patch("main.ImageFetcher")
@patch("main.fetch_open_meteo")
@patch("main.load_config")
def test_first_run_fetches_and_sets_wallpaper(
    mock_config, mock_fetch, mock_image_cls, mock_render, mock_set
):
    mock_config.return_value = _make_config()
    mock_fetch.return_value = _make_weather(code=0, temp=22.5)
    mock_image_instance = MagicMock()
    mock_image_instance.get_image.return_value = "/tmp/base.jpg"
    mock_image_cls.return_value = mock_image_instance
    mock_render.return_value = "/tmp/output.jpg"
    mock_set.return_value = True

    app = WeatherWallpaperApp()
    app.tick()

    mock_fetch.assert_called_once()
    mock_image_instance.get_image.assert_called_once()
    mock_render.assert_called_once()
    mock_set.assert_called_once_with("/tmp/output.jpg")


@patch("main.set_wallpaper")
@patch("main.render_overlay")
@patch("main.ImageFetcher")
@patch("main.fetch_open_meteo")
@patch("main.load_config")
def test_no_weather_change_skips_image_fetch(
    mock_config, mock_fetch, mock_image_cls, mock_render, mock_set
):
    mock_config.return_value = _make_config()
    mock_fetch.return_value = _make_weather(code=0, temp=22.5)
    mock_image_instance = MagicMock()
    mock_image_instance.get_image.return_value = "/tmp/base.jpg"
    mock_image_cls.return_value = mock_image_instance
    mock_render.return_value = "/tmp/output.jpg"
    mock_set.return_value = True

    app = WeatherWallpaperApp()
    app.tick()  # First run
    app.tick()  # Same weather - should skip image fetch

    assert mock_image_instance.get_image.call_count == 1
    assert mock_render.call_count == 1


@patch("main.set_wallpaper")
@patch("main.render_overlay")
@patch("main.ImageFetcher")
@patch("main.fetch_open_meteo")
@patch("main.load_config")
def test_temperature_change_redraws_overlay_only(
    mock_config, mock_fetch, mock_image_cls, mock_render, mock_set
):
    mock_config.return_value = _make_config()
    mock_image_instance = MagicMock()
    mock_image_instance.get_image.return_value = "/tmp/base.jpg"
    mock_image_cls.return_value = mock_image_instance
    mock_render.return_value = "/tmp/output.jpg"
    mock_set.return_value = True

    # First call: code=0, temp=22.5
    mock_fetch.return_value = _make_weather(code=0, temp=22.5)
    app = WeatherWallpaperApp()
    app.tick()

    # Second call: same code, different temp
    mock_fetch.return_value = _make_weather(code=0, temp=25.0)
    app.tick()

    # Image fetched only once, but overlay rendered twice
    assert mock_image_instance.get_image.call_count == 1
    assert mock_render.call_count == 2
    assert mock_set.call_count == 2


@patch("main.set_wallpaper")
@patch("main.render_overlay")
@patch("main.ImageFetcher")
@patch("main.fetch_open_meteo")
@patch("main.load_config")
def test_weather_code_change_fetches_new_image(
    mock_config, mock_fetch, mock_image_cls, mock_render, mock_set
):
    mock_config.return_value = _make_config()
    mock_image_instance = MagicMock()
    mock_image_instance.get_image.return_value = "/tmp/base.jpg"
    mock_image_cls.return_value = mock_image_instance
    mock_render.return_value = "/tmp/output.jpg"
    mock_set.return_value = True

    # First: clear sky
    mock_fetch.return_value = _make_weather(code=0, temp=22.5)
    app = WeatherWallpaperApp()
    app.tick()

    # Second: rain
    mock_fetch.return_value = _make_weather(code=63, temp=18.0)
    app.tick()

    assert mock_image_instance.get_image.call_count == 2
    assert mock_render.call_count == 2
