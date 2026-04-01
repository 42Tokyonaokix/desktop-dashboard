from unittest.mock import patch, MagicMock
from wallpaper_setter import set_wallpaper


@patch("wallpaper_setter.subprocess.run")
def test_set_wallpaper_system_events_success(mock_run):
    mock_run.return_value = MagicMock(returncode=0)
    result = set_wallpaper("/tmp/test.jpg")
    assert result is True
    args = mock_run.call_args[0][0]
    assert args[0] == "osascript"
    assert "System Events" in args[2]


@patch("wallpaper_setter.subprocess.run")
def test_set_wallpaper_falls_back_to_finder(mock_run):
    # First call (System Events) fails, second call (Finder) succeeds
    mock_run.side_effect = [
        MagicMock(returncode=1),
        MagicMock(returncode=0),
    ]
    result = set_wallpaper("/tmp/test.jpg")
    assert result is True
    assert mock_run.call_count == 2
    second_call_script = mock_run.call_args_list[1][0][0][2]
    assert "Finder" in second_call_script


@patch("wallpaper_setter.subprocess.run")
def test_set_wallpaper_both_fail(mock_run):
    mock_run.return_value = MagicMock(returncode=1)
    result = set_wallpaper("/tmp/test.jpg")
    assert result is False
