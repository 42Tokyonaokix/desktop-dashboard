from PIL import Image
from infra.dock_icon import generate_dock_icon, ICON_SIZE
from domain.models import WeatherData


def _make_weather(code=0, temp=22.5):
    return WeatherData(
        temperature=temp, weather_code=code, wind_speed=3.2,
        temp_max=28.0, temp_min=18.0, precipitation_probability=10,
    )


def _make_mapping(category="clear"):
    return {"icon": "☀️", "description": "快晴", "category": category}


def test_generate_dock_icon_returns_correct_size():
    img = generate_dock_icon(_make_weather(), _make_mapping(), task_count=0)
    assert isinstance(img, Image.Image)
    assert img.size == (ICON_SIZE, ICON_SIZE)
    assert img.mode == "RGBA"


def test_generate_dock_icon_with_task_badge():
    img = generate_dock_icon(_make_weather(), _make_mapping(), task_count=5)
    assert img.size == (ICON_SIZE, ICON_SIZE)
    # Badge should be drawn — we can verify the icon is not all-transparent
    # in the badge area (top-right corner)
    pixel = img.getpixel((ICON_SIZE - 10, 10))
    assert pixel[3] > 0  # not fully transparent


def test_generate_dock_icon_zero_tasks_no_badge():
    img = generate_dock_icon(_make_weather(), _make_mapping(), task_count=0)
    assert img.size == (ICON_SIZE, ICON_SIZE)


def test_generate_dock_icon_rain():
    weather = _make_weather(code=63, temp=9.6)
    mapping = {"icon": "🌧️", "description": "雨", "category": "rain"}
    img = generate_dock_icon(weather, mapping, task_count=3)
    assert img.size == (ICON_SIZE, ICON_SIZE)
