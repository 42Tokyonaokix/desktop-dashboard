import os
import tempfile
from domain.goal_reader import read_monthly_goal
from domain.models import GoalData


def test_read_monthly_goal_from_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "2026-04.md")
        with open(path, "w") as f:
            f.write("---\n")
            f.write('title: "2026年4月 マンスリーゴール"\n')
            f.write("date: 2026-04-01\n")
            f.write("tags: [monthly, goal]\n")
            f.write("---\n\n")
            f.write("# 2026年4月 マンスリーゴール\n\n")
            f.write("## 今月のテーマ\n\n")
            f.write("> 毎日、自分の目標を見る\n\n")
            f.write("## 目標\n\n")
            f.write("- **目標1** — 説明\n")
            f.write("- **目標2** — 説明\n")

        result = read_monthly_goal(tmpdir)
        assert isinstance(result, GoalData)
        assert "マンスリーゴール" in result.title
        assert "毎日、自分の目標を見る" in result.theme
        assert len(result.goals) == 2
        assert "目標1" in result.goals[0]


def test_read_monthly_goal_finds_current_month():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create files for different months
        for name in ["2026-03.md", "2026-04.md", "2025-12.md"]:
            with open(os.path.join(tmpdir, name), "w") as f:
                f.write("---\n")
                f.write(f'title: "{name}"\n')
                f.write("---\n\n")
                f.write("## 今月のテーマ\n\n> テーマ\n\n")
                f.write("## 目標\n\n- **ゴール**\n")

        result = read_monthly_goal(tmpdir)
        assert result is not None


def test_read_monthly_goal_empty_dir_returns_none():
    with tempfile.TemporaryDirectory() as tmpdir:
        result = read_monthly_goal(tmpdir)
        assert result is None


def test_read_monthly_goal_nonexistent_dir_returns_none():
    result = read_monthly_goal("/nonexistent/path")
    assert result is None


def test_read_monthly_goal_no_theme_section():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "2026-04.md")
        with open(path, "w") as f:
            f.write("---\n")
            f.write('title: "No theme"\n')
            f.write("---\n\n")
            f.write("## 目標\n\n- **Goal 1**\n")

        result = read_monthly_goal(tmpdir)
        assert result is not None
        assert result.theme == ""
        assert len(result.goals) >= 1
