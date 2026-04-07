import os
import tempfile
from domain.task_reader import read_tasks
from domain.models import TaskItem


def _write_task_file(dir_path: str, filename: str, frontmatter: str) -> str:
    path = os.path.join(dir_path, filename)
    with open(path, "w") as f:
        f.write(f"---\n{frontmatter}---\n\n## Content\nSome body text.\n")
    return path


def test_read_tasks_finds_high_priority_todo():
    with tempfile.TemporaryDirectory() as tmpdir:
        _write_task_file(tmpdir, "001-task.md", (
            'title: "Important task"\n'
            'status: todo\n'
            'priority: high\n'
            'progress: 0/3\n'
            'tags: [bug, urgent]\n'
        ))
        tasks = read_tasks(tmpdir, status="todo", priority="high", max_items=8)
        assert len(tasks) == 1
        assert tasks[0].title == "Important task"
        assert tasks[0].priority == "high"
        assert tasks[0].tags == ["bug", "urgent"]
        assert tasks[0].progress == "0/3"


def test_read_tasks_filters_out_done():
    with tempfile.TemporaryDirectory() as tmpdir:
        _write_task_file(tmpdir, "001-done.md", (
            'title: "Done task"\n'
            'status: done\n'
            'priority: high\n'
            'progress: 3/3\n'
            'tags: []\n'
        ))
        _write_task_file(tmpdir, "002-todo.md", (
            'title: "Todo task"\n'
            'status: todo\n'
            'priority: high\n'
            'progress: 0/2\n'
            'tags: []\n'
        ))
        tasks = read_tasks(tmpdir, status="todo", priority="high", max_items=8)
        assert len(tasks) == 1
        assert tasks[0].title == "Todo task"


def test_read_tasks_filters_by_priority():
    with tempfile.TemporaryDirectory() as tmpdir:
        _write_task_file(tmpdir, "001-low.md", (
            'title: "Low priority"\n'
            'status: todo\n'
            'priority: low\n'
            'progress: 0/1\n'
            'tags: []\n'
        ))
        _write_task_file(tmpdir, "002-high.md", (
            'title: "High priority"\n'
            'status: todo\n'
            'priority: high\n'
            'progress: 0/1\n'
            'tags: []\n'
        ))
        tasks = read_tasks(tmpdir, status="todo", priority="high", max_items=8)
        assert len(tasks) == 1
        assert tasks[0].title == "High priority"


def test_read_tasks_respects_max_items():
    with tempfile.TemporaryDirectory() as tmpdir:
        for i in range(10):
            _write_task_file(tmpdir, f"{i:03d}-task.md", (
                f'title: "Task {i}"\n'
                'status: todo\n'
                'priority: high\n'
                f'progress: 0/{i+1}\n'
                'tags: []\n'
            ))
        tasks = read_tasks(tmpdir, status="todo", priority="high", max_items=3)
        assert len(tasks) == 3


def test_read_tasks_scans_subdirectories():
    with tempfile.TemporaryDirectory() as tmpdir:
        subdir = os.path.join(tmpdir, "project-a")
        os.makedirs(subdir)
        _write_task_file(subdir, "001-task.md", (
            'title: "Nested task"\n'
            'status: todo\n'
            'priority: high\n'
            'progress: 0/1\n'
            'tags: []\n'
        ))
        tasks = read_tasks(tmpdir, status="todo", priority="high", max_items=8)
        assert len(tasks) == 1
        assert tasks[0].title == "Nested task"


def test_read_tasks_empty_dir_returns_empty_list():
    with tempfile.TemporaryDirectory() as tmpdir:
        tasks = read_tasks(tmpdir, status="todo", priority="high", max_items=8)
        assert tasks == []


def test_read_tasks_nonexistent_dir_returns_empty_list():
    tasks = read_tasks("/nonexistent/path", status="todo", priority="high", max_items=8)
    assert tasks == []


def test_read_tasks_case_insensitive_status():
    with tempfile.TemporaryDirectory() as tmpdir:
        _write_task_file(tmpdir, "001-task.md", (
            'title: "Case test"\n'
            'status: TODO\n'
            'priority: HIGH\n'
            'progress: 0/1\n'
            'tags: []\n'
        ))
        tasks = read_tasks(tmpdir, status="todo", priority="high", max_items=8)
        assert len(tasks) == 1
