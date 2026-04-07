import os
import tempfile
from domain.motivation_reader import read_motivation
from domain.models import MotivationData


def test_read_motivation_from_file():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write("今日はタスクを3つ完了しました。次は認証機能の実装です。\n")
        f.write("「継続は力なり」— 大切なのは一歩ずつ進むこと。\n")
        f.flush()
        result = read_motivation(f.name)
    os.unlink(f.name)

    assert isinstance(result, MotivationData)
    assert "タスクを3つ完了" in result.comment
    assert "継続は力なり" in result.comment


def test_read_motivation_nonexistent_file_returns_none():
    result = read_motivation("/nonexistent/motivation.md")
    assert result is None


def test_read_motivation_empty_file_returns_none():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write("")
        f.flush()
        result = read_motivation(f.name)
    os.unlink(f.name)

    assert result is None


def test_read_motivation_whitespace_only_returns_none():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write("   \n\n  \n")
        f.flush()
        result = read_motivation(f.name)
    os.unlink(f.name)

    assert result is None
