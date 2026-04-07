import os
import tempfile
from PIL import Image
from infra.wallpaper_renderer import render_dashboard
from domain.models import WeatherData, TaskItem, MotivationData, DashboardData


def _create_test_image(path: str, width: int = 3840, height: int = 2160) -> None:
    img = Image.new("RGB", (width, height), color=(100, 150, 200))
    img.save(path)


def _make_dashboard_data(
    num_tasks: int = 3,
    motivation_text: str = "Keep going!",
) -> DashboardData:
    weather = WeatherData(
        temperature=22.5, weather_code=0, wind_speed=3.2,
        temp_max=28.0, temp_min=18.0, precipitation_probability=10,
    )
    tasks = [
        TaskItem(
            title=f"Task {i+1}: Some work item",
            file_path=f"/vault/tasks/{i:03d}.md",
            priority="high",
            status="todo",
            progress=f"0/{i+1}",
            tags=["dev"] if i % 2 == 0 else [],
        )
        for i in range(num_tasks)
    ]
    motivation = MotivationData(comment=motivation_text) if motivation_text else None
    return DashboardData(
        weather=weather,
        weather_mapping={"icon": "☀️", "description": "快晴", "category": "clear"},
        tasks=tasks,
        motivation=motivation,
    )


def test_render_dashboard_creates_output_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        base_path = os.path.join(tmpdir, "base.jpg")
        output_path = os.path.join(tmpdir, "output.jpg")
        _create_test_image(base_path)

        data = _make_dashboard_data()
        config = {
            "width": 1500, "height": 1000,
            "sections": ["weather", "tasks", "motivation"],
            "section_weights": [30, 40, 30],
            "card_opacity": 0.6, "font_size": 36,
        }
        result = render_dashboard(base_path, output_path, data, config)
        assert result == output_path
        assert os.path.exists(output_path)


def test_render_dashboard_output_is_valid_jpeg():
    with tempfile.TemporaryDirectory() as tmpdir:
        base_path = os.path.join(tmpdir, "base.jpg")
        output_path = os.path.join(tmpdir, "output.jpg")
        _create_test_image(base_path)

        data = _make_dashboard_data()
        config = {
            "width": 1500, "height": 1000,
            "sections": ["weather", "tasks", "motivation"],
            "section_weights": [30, 40, 30],
            "card_opacity": 0.6, "font_size": 36,
        }
        render_dashboard(base_path, output_path, data, config)
        with Image.open(output_path) as img:
            assert img.format == "JPEG"
            assert img.size[0] > 0
            assert img.size[1] > 0


def test_render_dashboard_no_tasks():
    with tempfile.TemporaryDirectory() as tmpdir:
        base_path = os.path.join(tmpdir, "base.jpg")
        output_path = os.path.join(tmpdir, "output.jpg")
        _create_test_image(base_path)

        data = _make_dashboard_data(num_tasks=0)
        config = {
            "width": 1500, "height": 1000,
            "sections": ["weather", "tasks", "motivation"],
            "section_weights": [30, 40, 30],
            "card_opacity": 0.6, "font_size": 36,
        }
        result = render_dashboard(base_path, output_path, data, config)
        assert os.path.exists(result)


def test_render_dashboard_no_motivation():
    with tempfile.TemporaryDirectory() as tmpdir:
        base_path = os.path.join(tmpdir, "base.jpg")
        output_path = os.path.join(tmpdir, "output.jpg")
        _create_test_image(base_path)

        data = _make_dashboard_data(motivation_text="")
        config = {
            "width": 1500, "height": 1000,
            "sections": ["weather", "tasks", "motivation"],
            "section_weights": [30, 40, 30],
            "card_opacity": 0.6, "font_size": 36,
        }
        result = render_dashboard(base_path, output_path, data, config)
        assert os.path.exists(result)


def test_render_dashboard_section_toggle():
    """Test that disabling sections still produces valid output."""
    with tempfile.TemporaryDirectory() as tmpdir:
        base_path = os.path.join(tmpdir, "base.jpg")
        output_path = os.path.join(tmpdir, "output.jpg")
        _create_test_image(base_path)

        data = _make_dashboard_data()
        config = {
            "width": 1500, "height": 1000,
            "sections": ["weather"],  # only weather
            "section_weights": [100],
            "card_opacity": 0.6, "font_size": 36,
        }
        result = render_dashboard(base_path, output_path, data, config)
        assert os.path.exists(result)


def test_render_dashboard_custom_weights():
    """Test custom section weight distribution."""
    with tempfile.TemporaryDirectory() as tmpdir:
        base_path = os.path.join(tmpdir, "base.jpg")
        output_path = os.path.join(tmpdir, "output.jpg")
        _create_test_image(base_path)

        data = _make_dashboard_data()
        config = {
            "width": 1500, "height": 1000,
            "sections": ["weather", "tasks", "motivation"],
            "section_weights": [20, 50, 30],
            "card_opacity": 0.8, "font_size": 42,
        }
        result = render_dashboard(base_path, output_path, data, config)
        assert os.path.exists(result)
