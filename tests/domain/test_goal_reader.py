import os
import tempfile
from domain.goal_reader import read_monthly_goal, _parse_goal_file
from domain.models import GoalData
from pathlib import Path


SAMPLE_WEEKLY_GOAL = """---
title: "2026-W15 ウィークリーゴール"
date: 2026-04-07
tags: [weekly, goal]
---

# 2026年4月第二週 ウィークリーゴール

## 今週のテーマ

> 毎日、自分の目標を見る

## 目標

### noche-parameter-poc
- 実際に動作確認をし、性能を証明する。
- アイデアをインサイトとして提示する。

### task-update
- ai が中心となって働くやり方の基礎を作成する。
- タスク管理をできるようになる。

## タスク

### task-update
- desktop-dashboard のセットアップ
- obsidian側でのタスク管理セットアップ

#### niche-parameter-poc
- 実装をとりあえず完璧にする。
- 実際に使用してみる

## 日別スケジュール

### 月 (04/07)
- 09:00
- 12:00

### 火 (04/08)
- 09:00
\tniche ロジック部分の調査 (2h)
- 12:00
\t実装の理解を進める (2h)

### 水 (04/09)
- 09:00
- 12:00
"""


def test_parse_project_goals():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(SAMPLE_WEEKLY_GOAL)
        f.flush()
        result = _parse_goal_file(Path(f.name))
    os.unlink(f.name)

    assert result is not None
    assert result.theme == "毎日、自分の目標を見る"
    assert len(result.project_goals) == 2
    assert result.project_goals[0].project == "noche-parameter-poc"
    assert len(result.project_goals[0].goals) == 2
    assert "動作確認" in result.project_goals[0].goals[0]
    assert result.project_goals[1].project == "task-update"


def test_parse_tasks():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(SAMPLE_WEEKLY_GOAL)
        f.flush()
        result = _parse_goal_file(Path(f.name))
    os.unlink(f.name)

    assert len(result.tasks) >= 2
    assert any("desktop-dashboard" in t for t in result.tasks)


def test_read_monthly_goal_from_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "2026-W15.md")
        with open(path, "w") as f:
            f.write(SAMPLE_WEEKLY_GOAL)

        result = read_monthly_goal(tmpdir)
        assert result is not None
        assert "ウィークリーゴール" in result.title


def test_read_monthly_goal_empty_dir_returns_none():
    with tempfile.TemporaryDirectory() as tmpdir:
        result = read_monthly_goal(tmpdir)
        assert result is None


def test_read_monthly_goal_nonexistent_dir_returns_none():
    result = read_monthly_goal("/nonexistent/path")
    assert result is None


def test_parse_no_theme():
    content = "---\ntitle: test\n---\n\n## 目標\n\n### proj\n- goal1\n"
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(content)
        f.flush()
        result = _parse_goal_file(Path(f.name))
    os.unlink(f.name)

    assert result is not None
    assert result.theme == ""
    assert len(result.project_goals) == 1
