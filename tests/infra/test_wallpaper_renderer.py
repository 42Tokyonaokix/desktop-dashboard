import os
import tempfile
from PIL import Image
from infra.wallpaper_renderer import render_dashboard
from domain.models import WeatherData, MotivationData, GoalData, ProjectGoal, ScheduleItem, DashboardData


def _create_test_image(path: str, width: int = 3840, height: int = 2160) -> None:
    img = Image.new("RGB", (width, height), color=(100, 150, 200))
    img.save(path)


def _make_dashboard_data(motivation_text: str = "Keep going!", with_goal: bool = True) -> DashboardData:
    weather = WeatherData(
        temperature=22.5, weather_code=0, wind_speed=3.2,
        temp_max=28.0, temp_min=18.0, precipitation_probability=10,
    )
    motivation = MotivationData(comment=motivation_text) if motivation_text else None
    goal = GoalData(
        title="W15", theme="毎日目標を見る",
        project_goals=[
            ProjectGoal(project="proj-a", goals=["goal 1", "goal 2"]),
            ProjectGoal(project="proj-b", goals=["goal 3"]),
        ],
        tasks=["task 1", "task 2"],
        today_schedule=[
            ScheduleItem(time="09:00", description="morning work (2h)"),
            ScheduleItem(time="12:00", description="afternoon work (2h)"),
        ],
    ) if with_goal else None
    return DashboardData(
        weather=weather,
        weather_mapping={"icon": "☀️", "description": "快晴", "category": "clear"},
        motivation=motivation,
        monthly_goal=goal,
    )


def test_render_dashboard_creates_output_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        base_path = os.path.join(tmpdir, "base.jpg")
        output_path = os.path.join(tmpdir, "output.jpg")
        _create_test_image(base_path)

        data = _make_dashboard_data()
        config = {
            "width": 1500, "height": 1000,
            "sections": ["weather", "goal", "today_plan", "motivation"],
            "section_weights": [10, 30, 30, 15],
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
            "sections": ["weather", "goal", "today_plan", "motivation"],
            "section_weights": [10, 30, 30, 15],
            "card_opacity": 0.6, "font_size": 36,
        }
        render_dashboard(base_path, output_path, data, config)
        with Image.open(output_path) as img:
            assert img.format == "JPEG"


def test_render_dashboard_no_goal():
    with tempfile.TemporaryDirectory() as tmpdir:
        base_path = os.path.join(tmpdir, "base.jpg")
        output_path = os.path.join(tmpdir, "output.jpg")
        _create_test_image(base_path)

        data = _make_dashboard_data(with_goal=False)
        config = {
            "width": 1500, "height": 1000,
            "sections": ["weather", "goal", "today_plan", "motivation"],
            "section_weights": [10, 30, 30, 15],
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
            "sections": ["weather", "goal", "motivation"],
            "section_weights": [10, 50, 15],
            "card_opacity": 0.6, "font_size": 36,
        }
        result = render_dashboard(base_path, output_path, data, config)
        assert os.path.exists(result)


def test_render_dashboard_section_toggle():
    with tempfile.TemporaryDirectory() as tmpdir:
        base_path = os.path.join(tmpdir, "base.jpg")
        output_path = os.path.join(tmpdir, "output.jpg")
        _create_test_image(base_path)

        data = _make_dashboard_data()
        config = {
            "width": 1500, "height": 1000,
            "sections": ["weather"],
            "section_weights": [100],
            "card_opacity": 0.6, "font_size": 36,
        }
        result = render_dashboard(base_path, output_path, data, config)
        assert os.path.exists(result)
