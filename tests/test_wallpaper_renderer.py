import os
import tempfile
from PIL import Image
from wallpaper_renderer import render_overlay
from weather_fetcher import WeatherData


def _create_test_image(path: str, width: int = 1920, height: int = 1080) -> None:
    img = Image.new("RGB", (width, height), color=(100, 150, 200))
    img.save(path)


def test_render_overlay_creates_output_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        base_path = os.path.join(tmpdir, "base.jpg")
        output_path = os.path.join(tmpdir, "output.jpg")
        _create_test_image(base_path)

        weather = WeatherData(
            temperature=22.5,
            weather_code=0,
            wind_speed=3.2,
            temp_max=28.0,
            temp_min=18.0,
            precipitation_probability=10,
        )

        result = render_overlay(
            base_image_path=base_path,
            output_path=output_path,
            weather=weather,
            icon="☀️",
            description="快晴",
            position="bottom_right",
            opacity=0.7,
            font_size=48,
        )
        assert result == output_path
        assert os.path.exists(output_path)

        with Image.open(output_path) as img:
            assert img.size == (1920, 1080)


def test_render_overlay_different_positions():
    with tempfile.TemporaryDirectory() as tmpdir:
        base_path = os.path.join(tmpdir, "base.jpg")
        _create_test_image(base_path)

        weather = WeatherData(
            temperature=5.0,
            weather_code=71,
            wind_speed=10.0,
            temp_max=8.0,
            temp_min=-2.0,
            precipitation_probability=80,
        )

        for position in ["bottom_right", "bottom_left", "top_right", "top_left"]:
            output_path = os.path.join(tmpdir, f"output_{position}.jpg")
            result = render_overlay(
                base_image_path=base_path,
                output_path=output_path,
                weather=weather,
                icon="❄️",
                description="雪",
                position=position,
                opacity=0.7,
                font_size=48,
            )
            assert os.path.exists(result)
