from domain.models import WeatherData, TaskItem, MotivationData, DashboardData


def test_weather_data_creation():
    w = WeatherData(
        temperature=22.5,
        weather_code=0,
        wind_speed=3.2,
        temp_max=28.0,
        temp_min=18.0,
        precipitation_probability=10,
    )
    assert w.temperature == 22.5
    assert w.weather_code == 0


def test_task_item_creation():
    t = TaskItem(
        title="Fix bug",
        file_path="/vault/tasks/001.md",
        priority="high",
        status="todo",
        progress="0/3",
        tags=["bug"],
    )
    assert t.title == "Fix bug"
    assert t.priority == "high"
    assert t.tags == ["bug"]


def test_motivation_data_creation():
    m = MotivationData(comment="Great job today!")
    assert m.comment == "Great job today!"


def test_dashboard_data_creation():
    w = WeatherData(
        temperature=22.5, weather_code=0, wind_speed=3.2,
        temp_max=28.0, temp_min=18.0, precipitation_probability=10,
    )
    tasks = [
        TaskItem(title="Task 1", file_path="/a.md", priority="high",
                 status="todo", progress="0/1", tags=[]),
    ]
    motivation = MotivationData(comment="Keep going!")
    d = DashboardData(
        weather=w,
        weather_mapping={"icon": "☀️", "description": "快晴", "category": "clear"},
        tasks=tasks,
        motivation=motivation,
    )
    assert d.weather.temperature == 22.5
    assert len(d.tasks) == 1
    assert d.motivation.comment == "Keep going!"


def test_dashboard_data_empty_tasks_and_motivation():
    w = WeatherData(
        temperature=0.0, weather_code=0, wind_speed=0.0,
        temp_max=0.0, temp_min=0.0, precipitation_probability=0,
    )
    d = DashboardData(
        weather=w,
        weather_mapping={},
        tasks=[],
        motivation=None,
    )
    assert d.tasks == []
    assert d.motivation is None
