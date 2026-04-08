from domain.models import WeatherData, TaskItem, MotivationData, GoalData, ProjectGoal, ScheduleItem, DashboardData


def test_weather_data_creation():
    w = WeatherData(
        temperature=22.5, weather_code=0, wind_speed=3.2,
        temp_max=28.0, temp_min=18.0, precipitation_probability=10,
    )
    assert w.temperature == 22.5
    assert w.weather_code == 0


def test_task_item_creation():
    t = TaskItem(
        title="Fix bug", file_path="/vault/tasks/001.md",
        priority="high", status="todo", progress="0/3", tags=["bug"],
    )
    assert t.title == "Fix bug"
    assert t.priority == "high"


def test_motivation_data_creation():
    m = MotivationData(comment="Great job today!")
    assert m.comment == "Great job today!"


def test_goal_data_with_projects():
    g = GoalData(
        title="W15",
        theme="毎日目標を見る",
        project_goals=[
            ProjectGoal(project="proj-a", goals=["goal1", "goal2"]),
            ProjectGoal(project="proj-b", goals=["goal3"]),
        ],
        tasks=["task1", "task2"],
        today_schedule=[
            ScheduleItem(time="09:00", description="work (2h)"),
        ],
    )
    assert len(g.project_goals) == 2
    assert g.project_goals[0].project == "proj-a"
    assert len(g.tasks) == 2
    assert g.today_schedule[0].time == "09:00"


def test_dashboard_data_creation():
    w = WeatherData(
        temperature=22.5, weather_code=0, wind_speed=3.2,
        temp_max=28.0, temp_min=18.0, precipitation_probability=10,
    )
    motivation = MotivationData(comment="Keep going!")
    goal = GoalData(title="W15", theme="test", project_goals=[], tasks=[], today_schedule=[])
    d = DashboardData(
        weather=w,
        weather_mapping={"icon": "☀️", "description": "快晴"},
        motivation=motivation,
        monthly_goal=goal,
    )
    assert d.weather.temperature == 22.5
    assert d.motivation.comment == "Keep going!"
    assert d.monthly_goal.title == "W15"


def test_dashboard_data_empty():
    w = WeatherData(
        temperature=0.0, weather_code=0, wind_speed=0.0,
        temp_max=0.0, temp_min=0.0, precipitation_probability=0,
    )
    d = DashboardData(weather=w, weather_mapping={})
    assert d.motivation is None
    assert d.monthly_goal is None
