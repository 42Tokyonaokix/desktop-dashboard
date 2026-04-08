# Desktop Dashboard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transform weather-desktop into desktop-dashboard — a macOS wallpaper dashboard displaying weather, Obsidian vault tasks, and AI-generated motivation comments in a 3-section card layout.

**Architecture:** domain/infra 2-layer separation. `src/domain/` handles data retrieval (weather API, Obsidian vault reading). `src/infra/` handles output (wallpaper rendering, macOS wallpaper setting, Dock icon, settings UI). Data flows via `DashboardData` dataclass. tkinter manages all scheduling via `.after()` (no `schedule` library).

**Tech Stack:** Python 3.10+, Pillow, requests, PyYAML, tkinter, PyObjC (AppKit)

---

## File Structure

### New files to create

| File | Responsibility |
|------|---------------|
| `src/domain/__init__.py` | Domain package init |
| `src/domain/models.py` | Shared dataclasses: `WeatherData`, `TaskItem`, `MotivationData`, `DashboardData` |
| `src/domain/weather_fetcher.py` | Open-Meteo / YOLP API calls (moved from `src/weather_fetcher.py`) |
| `src/domain/weather_mapper.py` | WMO code mapping (moved from `src/weather_mapper.py`) |
| `src/domain/task_reader.py` | Read Obsidian vault task files, filter by status/priority |
| `src/domain/motivation_reader.py` | Read motivation comment from vault file |
| `src/infra/__init__.py` | Infra package init |
| `src/infra/image_fetcher.py` | Unsplash image fetch + cache (moved from `src/image_fetcher.py`) |
| `src/infra/wallpaper_setter.py` | macOS AppleScript wallpaper setting (moved from `src/wallpaper_setter.py`) |
| `src/infra/wallpaper_renderer.py` | 3-section card-style wallpaper rendering (rewrite of `src/wallpaper_renderer.py`) |
| `src/infra/dock_icon.py` | Dock icon generation with task badge (extracted from `src/dock_app.py`) |
| `src/infra/settings_window.py` | tkinter settings dashboard UI (rewrite of `src/dock_app.py`) |
| `src/config.py` | Config loader with new dashboard/obsidian sections (stays at src/ root) |
| `src/main.py` | Main orchestrator with tkinter.after() scheduling (rewrite) |
| `tests/domain/__init__.py` | Test package init |
| `tests/domain/test_weather_fetcher.py` | Weather fetcher tests (moved) |
| `tests/domain/test_weather_mapper.py` | Weather mapper tests (moved) |
| `tests/domain/test_task_reader.py` | Task reader tests (new) |
| `tests/domain/test_motivation_reader.py` | Motivation reader tests (new) |
| `tests/domain/test_models.py` | Model dataclass tests (new) |
| `tests/infra/__init__.py` | Test package init |
| `tests/infra/test_image_fetcher.py` | Image fetcher tests (moved) |
| `tests/infra/test_wallpaper_setter.py` | Wallpaper setter tests (moved) |
| `tests/infra/test_wallpaper_renderer.py` | Wallpaper renderer tests (rewritten) |
| `tests/infra/test_dock_icon.py` | Dock icon tests (moved/updated) |
| `tests/infra/test_settings_window.py` | Settings window tests (new) |

### Files to delete after migration

| File | Reason |
|------|--------|
| `src/weather_fetcher.py` | Moved to `src/domain/weather_fetcher.py` |
| `src/weather_mapper.py` | Moved to `src/domain/weather_mapper.py` |
| `src/image_fetcher.py` | Moved to `src/infra/image_fetcher.py` |
| `src/wallpaper_renderer.py` | Rewritten as `src/infra/wallpaper_renderer.py` |
| `src/wallpaper_setter.py` | Moved to `src/infra/wallpaper_setter.py` |
| `src/dock_app.py` | Split into `src/infra/dock_icon.py` + `src/infra/settings_window.py` |
| `tests/test_weather_fetcher.py` | Moved to `tests/domain/` |
| `tests/test_weather_mapper.py` | Moved to `tests/domain/` |
| `tests/test_config.py` | Moved to `tests/` (updated imports) |
| `tests/test_image_fetcher.py` | Moved to `tests/infra/` |
| `tests/test_wallpaper_renderer.py` | Rewritten in `tests/infra/` |
| `tests/test_wallpaper_setter.py` | Moved to `tests/infra/` |
| `tests/test_dock_app.py` | Replaced by `tests/infra/test_dock_icon.py` |
| `tests/test_main.py` | Rewritten in `tests/` |

---

## Task 1: Project setup — directory structure and model definitions

**Files:**
- Create: `src/domain/__init__.py`
- Create: `src/domain/models.py`
- Create: `src/infra/__init__.py`
- Create: `tests/domain/__init__.py`
- Create: `tests/infra/__init__.py`
- Create: `tests/domain/test_models.py`
- Modify: `src/__init__.py`

- [ ] **Step 1: Create domain and infra package directories**

```bash
mkdir -p src/domain src/infra tests/domain tests/infra
```

- [ ] **Step 2: Create package init files**

`src/domain/__init__.py`:
```python
```

`src/infra/__init__.py`:
```python
```

`tests/domain/__init__.py`:
```python
```

`tests/infra/__init__.py`:
```python
```

- [ ] **Step 3: Write the failing test for domain models**

`tests/domain/test_models.py`:
```python
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
```

- [ ] **Step 4: Run test to verify it fails**

Run: `cd /Users/naoki/development/03_my-devlopment/weather-desktop && python -m pytest tests/domain/test_models.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'domain'"

- [ ] **Step 5: Write domain models**

`src/domain/models.py`:
```python
"""Shared data models for the desktop dashboard."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class WeatherData:
    temperature: float
    weather_code: int
    wind_speed: float
    temp_max: float
    temp_min: float
    precipitation_probability: int


@dataclass
class TaskItem:
    title: str
    file_path: str
    priority: str
    status: str
    progress: str
    tags: list[str] = field(default_factory=list)


@dataclass
class MotivationData:
    comment: str


@dataclass
class DashboardData:
    weather: WeatherData
    weather_mapping: dict
    tasks: list[TaskItem] = field(default_factory=list)
    motivation: Optional[MotivationData] = None
```

- [ ] **Step 6: Update conftest.py for new package structure**

`tests/conftest.py`:
```python
import os
import sys

# Add src to path so tests can import domain.* and infra.* packages
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
```

- [ ] **Step 7: Run test to verify it passes**

Run: `cd /Users/naoki/development/03_my-devlopment/weather-desktop && python -m pytest tests/domain/test_models.py -v`
Expected: PASS (all 5 tests)

- [ ] **Step 8: Commit**

```bash
git add src/domain/ src/infra/ tests/domain/ tests/infra/ tests/conftest.py
git commit -m "feat: add domain/infra directory structure and shared models"
```

---

## Task 2: Migrate weather modules to domain layer

**Files:**
- Create: `src/domain/weather_fetcher.py` (move from `src/weather_fetcher.py`)
- Create: `src/domain/weather_mapper.py` (move from `src/weather_mapper.py`)
- Create: `tests/domain/test_weather_fetcher.py` (move from `tests/test_weather_fetcher.py`)
- Create: `tests/domain/test_weather_mapper.py` (move from `tests/test_weather_mapper.py`)
- Delete: `src/weather_fetcher.py`
- Delete: `src/weather_mapper.py`
- Delete: `tests/test_weather_fetcher.py`
- Delete: `tests/test_weather_mapper.py`

- [ ] **Step 1: Move weather_fetcher.py to domain and update imports**

`src/domain/weather_fetcher.py` — copy from `src/weather_fetcher.py` but replace `WeatherData` import with domain models:

```python
"""Fetch weather data from Open-Meteo API and Yahoo YOLP API."""

import logging
from typing import Optional, Dict

import requests

from domain.models import WeatherData

logger = logging.getLogger(__name__)

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
YOLP_URL = "https://map.yahooapis.jp/weather/V1/place"


def fetch_open_meteo(latitude: float, longitude: float) -> Optional[WeatherData]:
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,weather_code,wind_speed_10m",
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max",
        "timezone": "Asia/Tokyo",
    }
    try:
        resp = requests.get(OPEN_METEO_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        current = data["current"]
        daily = data["daily"]
        return WeatherData(
            temperature=current["temperature_2m"],
            weather_code=current["weather_code"],
            wind_speed=current["wind_speed_10m"],
            temp_max=daily["temperature_2m_max"][0],
            temp_min=daily["temperature_2m_min"][0],
            precipitation_probability=daily["precipitation_probability_max"][0],
        )
    except Exception:
        logger.exception("Failed to fetch Open-Meteo data")
        return None


def fetch_yolp_rainfall(
    latitude: float, longitude: float, client_id: str
) -> Optional[Dict]:
    if not client_id:
        return None

    params = {
        "appid": client_id,
        "coordinates": f"{longitude},{latitude}",
        "output": "json",
    }
    try:
        resp = requests.get(YOLP_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        weathers = data["Feature"][0]["Property"]["WeatherList"]["Weather"]
        result = {}
        for w in weathers:
            result[w["Type"]] = w["Rainfall"]
        return result
    except Exception:
        logger.exception("Failed to fetch YOLP rainfall data")
        return None
```

- [ ] **Step 2: Move weather_mapper.py to domain**

`src/domain/weather_mapper.py` — copy from `src/weather_mapper.py` unchanged (no internal dependencies):

```python
"""WMO weather code to search query, icon, and description mapping."""

_MAPPINGS: dict[str, dict] = {
    "clear": {
        "codes": [0],
        "query": "clear blue sky landscape",
        "icon": "☀️",
        "description": "快晴",
    },
    "partly_cloudy": {
        "codes": [1, 2, 3],
        "query": "partly cloudy sky",
        "icon": "⛅",
        "description": "晴れ/曇り",
    },
    "fog": {
        "codes": [45, 48],
        "query": "foggy morning landscape",
        "icon": "🌫️",
        "description": "霧",
    },
    "drizzle": {
        "codes": [51, 53, 55],
        "query": "drizzle rain soft",
        "icon": "🌦️",
        "description": "霧雨",
    },
    "rain": {
        "codes": [61, 63, 65],
        "query": "rainy day city",
        "icon": "🌧️",
        "description": "雨",
    },
    "snow": {
        "codes": [71, 73, 75],
        "query": "snowy winter landscape",
        "icon": "❄️",
        "description": "雪",
    },
    "shower": {
        "codes": [80, 81, 82],
        "query": "rain shower dramatic sky",
        "icon": "🌧️",
        "description": "にわか雨",
    },
    "thunderstorm": {
        "codes": [95, 96, 99],
        "query": "thunderstorm lightning",
        "icon": "⛈️",
        "description": "雷雨",
    },
}

_DEFAULT = {
    "query": "sky landscape nature",
    "icon": "🌤️",
    "description": "不明",
    "category": "unknown",
}


class WeatherMapper:
    def __init__(self) -> None:
        self._code_to_category: dict[int, str] = {}
        for category, data in _MAPPINGS.items():
            for code in data["codes"]:
                self._code_to_category[code] = category

    def get_mapping(self, weather_code: int) -> dict:
        category = self._code_to_category.get(weather_code)
        if category is None:
            return {**_DEFAULT}
        data = _MAPPINGS[category]
        return {
            "query": data["query"],
            "icon": data["icon"],
            "description": data["description"],
            "category": category,
        }

    def get_categories(self) -> list[str]:
        return list(_MAPPINGS.keys())
```

- [ ] **Step 3: Move and update weather fetcher tests**

`tests/domain/test_weather_fetcher.py`:
```python
from unittest.mock import patch, MagicMock
from domain.weather_fetcher import fetch_open_meteo, fetch_yolp_rainfall
from domain.models import WeatherData


def _mock_open_meteo_response():
    return {
        "current": {
            "temperature_2m": 22.5,
            "weather_code": 0,
            "wind_speed_10m": 3.2,
        },
        "daily": {
            "temperature_2m_max": [28.0],
            "temperature_2m_min": [18.0],
            "precipitation_probability_max": [10],
        },
    }


@patch("domain.weather_fetcher.requests.get")
def test_fetch_open_meteo_success(mock_get):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = _mock_open_meteo_response()
    mock_get.return_value = mock_resp

    data = fetch_open_meteo(35.6762, 139.6503)
    assert isinstance(data, WeatherData)
    assert data.temperature == 22.5
    assert data.weather_code == 0
    assert data.temp_max == 28.0
    assert data.temp_min == 18.0
    assert data.precipitation_probability == 10


@patch("domain.weather_fetcher.requests.get")
def test_fetch_open_meteo_failure_returns_none(mock_get):
    mock_get.side_effect = Exception("Network error")
    data = fetch_open_meteo(35.6762, 139.6503)
    assert data is None


@patch("domain.weather_fetcher.requests.get")
def test_fetch_yolp_rainfall_success(mock_get):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "Feature": [
            {
                "Property": {
                    "WeatherList": {
                        "Weather": [
                            {"Type": "observation", "Rainfall": 1.5},
                            {"Type": "forecast", "Rainfall": 3.0},
                        ]
                    }
                }
            }
        ]
    }
    mock_get.return_value = mock_resp

    rainfall = fetch_yolp_rainfall(35.6762, 139.6503, "test_client_id")
    assert rainfall is not None
    assert rainfall["observation"] == 1.5


@patch("domain.weather_fetcher.requests.get")
def test_fetch_yolp_rainfall_no_client_id_returns_none(mock_get):
    rainfall = fetch_yolp_rainfall(35.6762, 139.6503, "")
    assert rainfall is None
    mock_get.assert_not_called()
```

- [ ] **Step 4: Move weather mapper tests**

`tests/domain/test_weather_mapper.py` — copy from `tests/test_weather_mapper.py` with updated import:
```python
from domain.weather_mapper import WeatherMapper
```
(Keep existing test bodies unchanged — just update the import line at the top.)

- [ ] **Step 5: Delete old files**

```bash
rm src/weather_fetcher.py src/weather_mapper.py
rm tests/test_weather_fetcher.py tests/test_weather_mapper.py
```

- [ ] **Step 6: Run migrated tests**

Run: `cd /Users/naoki/development/03_my-devlopment/weather-desktop && python -m pytest tests/domain/ -v`
Expected: PASS (all weather fetcher + mapper + model tests)

- [ ] **Step 7: Commit**

```bash
git add src/domain/weather_fetcher.py src/domain/weather_mapper.py tests/domain/
git add -u  # stages deletions
git commit -m "refactor: migrate weather modules to domain layer"
```

---

## Task 3: Migrate infra modules (image_fetcher, wallpaper_setter)

**Files:**
- Create: `src/infra/image_fetcher.py` (move from `src/image_fetcher.py`)
- Create: `src/infra/wallpaper_setter.py` (move from `src/wallpaper_setter.py`)
- Create: `tests/infra/test_image_fetcher.py` (move)
- Create: `tests/infra/test_wallpaper_setter.py` (move)
- Delete: `src/image_fetcher.py`, `src/wallpaper_setter.py`
- Delete: `tests/test_image_fetcher.py`, `tests/test_wallpaper_setter.py`

- [ ] **Step 1: Move image_fetcher.py to infra**

`src/infra/image_fetcher.py` — copy from `src/image_fetcher.py` unchanged (no internal dependencies to update).

- [ ] **Step 2: Move wallpaper_setter.py to infra**

`src/infra/wallpaper_setter.py` — copy from `src/wallpaper_setter.py` unchanged (no internal dependencies).

- [ ] **Step 3: Move and update test imports**

`tests/infra/test_image_fetcher.py`:
```python
# Replace: from image_fetcher import ImageFetcher
# With:
from infra.image_fetcher import ImageFetcher
```
(Keep all test bodies unchanged.)

`tests/infra/test_wallpaper_setter.py`:
```python
# Replace: from wallpaper_setter import set_wallpaper
# With:
from infra.wallpaper_setter import set_wallpaper
```
(Keep all test bodies unchanged.)

- [ ] **Step 4: Delete old files**

```bash
rm src/image_fetcher.py src/wallpaper_setter.py
rm tests/test_image_fetcher.py tests/test_wallpaper_setter.py
```

- [ ] **Step 5: Run migrated tests**

Run: `cd /Users/naoki/development/03_my-devlopment/weather-desktop && python -m pytest tests/infra/test_image_fetcher.py tests/infra/test_wallpaper_setter.py -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add src/infra/image_fetcher.py src/infra/wallpaper_setter.py tests/infra/
git add -u
git commit -m "refactor: migrate image_fetcher and wallpaper_setter to infra layer"
```

---

## Task 4: Update config.py with new dashboard/obsidian settings

**Files:**
- Modify: `src/config.py`
- Modify: `tests/test_config.py`
- Modify: `config.example.yaml`

- [ ] **Step 1: Write the failing test for new config keys**

Add to `tests/test_config.py` (keep existing tests, add new ones):

```python
def test_load_config_has_obsidian_defaults():
    config = load_config("/nonexistent/path.yaml")
    assert "obsidian" in config
    assert config["obsidian"]["vault_dir"] == ""
    assert config["obsidian"]["tasks"]["max_items"] == 8
    assert config["obsidian"]["tasks"]["status"] == "todo"
    assert config["obsidian"]["tasks"]["priority"] == "high"
    assert config["obsidian"]["motivation_file"] == ""
    assert config["obsidian"]["check_interval_min"] == 5


def test_load_config_has_dashboard_defaults():
    config = load_config("/nonexistent/path.yaml")
    assert "dashboard" in config
    assert config["dashboard"]["width"] == 1500
    assert config["dashboard"]["height"] == 1000
    assert config["dashboard"]["sections"] == ["weather", "tasks", "motivation"]
    assert config["dashboard"]["section_weights"] == [30, 40, 30]
    assert config["dashboard"]["card_opacity"] == 0.6
    assert config["dashboard"]["font_size"] == 36
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /Users/naoki/development/03_my-devlopment/weather-desktop && python -m pytest tests/test_config.py::test_load_config_has_obsidian_defaults -v`
Expected: FAIL with KeyError

- [ ] **Step 3: Update config.py DEFAULTS**

`src/config.py` — replace DEFAULTS with:
```python
DEFAULTS = {
    "location": {
        "latitude": 35.6762,
        "longitude": 139.6503,
    },
    "weather": {
        "check_interval_min": 10,
    },
    "overlay": {
        "position": "bottom_right",
        "opacity": 0.7,
        "font_size": 48,
    },
    "unsplash": {
        "access_key": "",
    },
    "yahoo": {
        "client_id": "",
    },
    "cache": {
        "max_images": 50,
    },
    "obsidian": {
        "vault_dir": "",
        "check_interval_min": 5,
        "tasks": {
            "max_items": 8,
            "status": "todo",
            "priority": "high",
        },
        "motivation_file": "",
    },
    "dashboard": {
        "width": 1500,
        "height": 1000,
        "sections": ["weather", "tasks", "motivation"],
        "section_weights": [30, 40, 30],
        "card_opacity": 0.6,
        "font_size": 36,
    },
}
```

Note: `check_interval_min` moved under `weather` key. Keep the old top-level `check_interval_min` in `_deep_merge` backward compatibility — or just update references later. For now, add both to DEFAULTS.

Actually, to avoid breaking existing config.yaml files, keep `check_interval_min` at root as well:

```python
    "check_interval_min": 10,  # backward compat, prefer weather.check_interval_min
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /Users/naoki/development/03_my-devlopment/weather-desktop && python -m pytest tests/test_config.py -v`
Expected: PASS (all old + new tests)

- [ ] **Step 5: Update config.example.yaml**

```yaml
# 位置情報
location:
  latitude: 35.6762
  longitude: 139.6503

# 天気更新設定
weather:
  check_interval_min: 10

# オーバーレイ設定（レガシー、wallpaper_renderer用）
overlay:
  position: bottom_right
  opacity: 0.7
  font_size: 48

# APIキー
unsplash:
  access_key: ""

yahoo:
  client_id: ""

# キャッシュ設定
cache:
  max_images: 50

# Obsidian vault 設定
obsidian:
  vault_dir: "/Users/naoki/development/02_obsidian-vault"
  check_interval_min: 5
  tasks:
    max_items: 8
    status: "todo"
    priority: "high"
  motivation_file: "/Users/naoki/development/02_obsidian-vault/dashboard/motivation.md"

# ダッシュボード壁紙設定
dashboard:
  width: 1500
  height: 1000
  sections:
    - weather
    - tasks
    - motivation
  section_weights: [30, 40, 30]
  card_opacity: 0.6
  font_size: 36
```

- [ ] **Step 6: Commit**

```bash
git add src/config.py config.example.yaml tests/test_config.py
git commit -m "feat: add obsidian and dashboard config sections"
```

---

## Task 5: Implement task_reader — Obsidian vault task file parser

**Files:**
- Create: `src/domain/task_reader.py`
- Create: `tests/domain/test_task_reader.py`

- [ ] **Step 1: Write the failing tests**

`tests/domain/test_task_reader.py`:
```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /Users/naoki/development/03_my-devlopment/weather-desktop && python -m pytest tests/domain/test_task_reader.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'domain.task_reader'"

- [ ] **Step 3: Implement task_reader.py**

`src/domain/task_reader.py`:
```python
"""Read task files from Obsidian vault directory."""

import logging
from pathlib import Path
from typing import Optional

import yaml

from domain.models import TaskItem

logger = logging.getLogger(__name__)


def _parse_frontmatter(file_path: Path) -> Optional[dict]:
    """Parse YAML frontmatter from a markdown file."""
    try:
        text = file_path.read_text(encoding="utf-8")
    except Exception:
        logger.warning("Failed to read file: %s", file_path)
        return None

    if not text.startswith("---"):
        return None

    end = text.find("---", 3)
    if end == -1:
        return None

    try:
        return yaml.safe_load(text[3:end])
    except yaml.YAMLError:
        logger.warning("Failed to parse frontmatter: %s", file_path)
        return None


def read_tasks(
    vault_dir: str,
    status: str = "todo",
    priority: str = "high",
    max_items: int = 8,
) -> list[TaskItem]:
    """Read task files matching status and priority filters."""
    dir_path = Path(vault_dir)
    if not dir_path.is_dir():
        return []

    tasks: list[TaskItem] = []

    for md_file in sorted(dir_path.rglob("*.md")):
        fm = _parse_frontmatter(md_file)
        if fm is None:
            continue

        file_status = str(fm.get("status", "")).strip().lower()
        file_priority = str(fm.get("priority", "")).strip().lower()

        if file_status != status.lower() or file_priority != priority.lower():
            continue

        tasks.append(TaskItem(
            title=fm.get("title", md_file.stem),
            file_path=str(md_file),
            priority=fm.get("priority", ""),
            status=fm.get("status", ""),
            progress=str(fm.get("progress", "")),
            tags=fm.get("tags", []) or [],
        ))

        if len(tasks) >= max_items:
            break

    return tasks
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /Users/naoki/development/03_my-devlopment/weather-desktop && python -m pytest tests/domain/test_task_reader.py -v`
Expected: PASS (all 8 tests)

- [ ] **Step 5: Commit**

```bash
git add src/domain/task_reader.py tests/domain/test_task_reader.py
git commit -m "feat: add task_reader for Obsidian vault task parsing"
```

---

## Task 6: Implement motivation_reader — vault motivation file reader

**Files:**
- Create: `src/domain/motivation_reader.py`
- Create: `tests/domain/test_motivation_reader.py`

- [ ] **Step 1: Write the failing tests**

`tests/domain/test_motivation_reader.py`:
```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /Users/naoki/development/03_my-devlopment/weather-desktop && python -m pytest tests/domain/test_motivation_reader.py -v`
Expected: FAIL

- [ ] **Step 3: Implement motivation_reader.py**

`src/domain/motivation_reader.py`:
```python
"""Read motivation comment from a markdown file in the Obsidian vault."""

import logging
from pathlib import Path
from typing import Optional

from domain.models import MotivationData

logger = logging.getLogger(__name__)


def read_motivation(file_path: str) -> Optional[MotivationData]:
    """Read motivation comment from a file. Returns None if file doesn't exist or is empty."""
    path = Path(file_path)
    if not path.is_file():
        return None

    try:
        text = path.read_text(encoding="utf-8").strip()
    except Exception:
        logger.warning("Failed to read motivation file: %s", file_path)
        return None

    if not text:
        return None

    return MotivationData(comment=text)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /Users/naoki/development/03_my-devlopment/weather-desktop && python -m pytest tests/domain/test_motivation_reader.py -v`
Expected: PASS (all 4 tests)

- [ ] **Step 5: Commit**

```bash
git add src/domain/motivation_reader.py tests/domain/test_motivation_reader.py
git commit -m "feat: add motivation_reader for vault motivation file"
```

---

## Task 7: Rewrite wallpaper_renderer — 3-section card layout

**Files:**
- Create: `src/infra/wallpaper_renderer.py`
- Create: `tests/infra/test_wallpaper_renderer.py`
- Delete: `src/wallpaper_renderer.py` (after migration)
- Delete: `tests/test_wallpaper_renderer.py` (after migration)

- [ ] **Step 1: Write the failing tests**

`tests/infra/test_wallpaper_renderer.py`:
```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /Users/naoki/development/03_my-devlopment/weather-desktop && python -m pytest tests/infra/test_wallpaper_renderer.py -v`
Expected: FAIL

- [ ] **Step 3: Implement wallpaper_renderer.py**

`src/infra/wallpaper_renderer.py`:
```python
"""Render 3-section dashboard overlay onto wallpaper image using Pillow."""

import logging
import os
from PIL import Image, ImageDraw, ImageFont

from domain.models import DashboardData, TaskItem, MotivationData

logger = logging.getLogger(__name__)

_FONT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "fonts")
_FONT_PATH = os.path.join(_FONT_DIR, "NotoSansJP-Regular.ttf")

_FALLBACK_FONTS = [
    "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",
    "/Library/Fonts/Arial Unicode.ttf",
    "/System/Library/Fonts/HelveticaNeue.ttc",
]

_CARD_RADIUS = 20
_CARD_PADDING = 24
_CARD_GAP = 16
_LINE_SPACING = 6


def _get_font(size: int) -> ImageFont.FreeTypeFont:
    if os.path.exists(_FONT_PATH):
        return ImageFont.truetype(_FONT_PATH, size)
    for fallback in _FALLBACK_FONTS:
        try:
            return ImageFont.truetype(fallback, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _draw_card(
    draw: ImageDraw.ImageDraw,
    x: int, y: int, w: int, h: int,
    opacity: float,
) -> None:
    """Draw a semi-transparent rounded rectangle card."""
    alpha = int(255 * opacity)
    draw.rounded_rectangle(
        [x, y, x + w, y + h],
        radius=_CARD_RADIUS,
        fill=(0, 0, 0, alpha),
    )


def _render_weather_section(
    draw: ImageDraw.ImageDraw,
    x: int, y: int, w: int, h: int,
    data: DashboardData, font_size: int, opacity: float,
) -> None:
    """Render weather info card."""
    _draw_card(draw, x, y, w, h, opacity)

    weather = data.weather
    mapping = data.weather_mapping
    icon = mapping.get("icon", "🌤️")
    desc = mapping.get("description", "")

    font_large = _get_font(font_size)
    font_small = _get_font(max(font_size // 2, 14))

    cx = x + _CARD_PADDING
    cy = y + _CARD_PADDING
    white = (255, 255, 255, 255)

    # Line 1: icon + temperature
    text = f"{icon} {weather.temperature:.1f}°C"
    draw.text((cx, cy), text, font=font_large, fill=white)
    bbox = draw.textbbox((0, 0), text, font=font_large)
    cy += (bbox[3] - bbox[1]) + _LINE_SPACING

    # Line 2: description
    draw.text((cx, cy), desc, font=font_small, fill=white)
    bbox = draw.textbbox((0, 0), desc, font=font_small)
    cy += (bbox[3] - bbox[1]) + _LINE_SPACING

    # Line 3: high/low
    text = f"最高 {weather.temp_max:.0f}°C / 最低 {weather.temp_min:.0f}°C"
    draw.text((cx, cy), text, font=font_small, fill=white)
    bbox = draw.textbbox((0, 0), text, font=font_small)
    cy += (bbox[3] - bbox[1]) + _LINE_SPACING

    # Line 4: precipitation
    text = f"降水確率 {weather.precipitation_probability}%"
    draw.text((cx, cy), text, font=font_small, fill=white)


def _render_tasks_section(
    draw: ImageDraw.ImageDraw,
    x: int, y: int, w: int, h: int,
    data: DashboardData, font_size: int, opacity: float,
) -> None:
    """Render task list card."""
    _draw_card(draw, x, y, w, h, opacity)

    font_title = _get_font(max(font_size // 2 + 4, 16))
    font_item = _get_font(max(font_size // 2 - 2, 12))
    font_tag = _get_font(max(font_size // 3, 10))

    cx = x + _CARD_PADDING
    cy = y + _CARD_PADDING
    white = (255, 255, 255, 255)
    dim = (180, 180, 180, 255)
    tag_color = (140, 200, 255, 255)

    # Section header
    draw.text((cx, cy), "📋 Tasks", font=font_title, fill=white)
    bbox = draw.textbbox((0, 0), "📋 Tasks", font=font_title)
    cy += (bbox[3] - bbox[1]) + _LINE_SPACING * 2

    if not data.tasks:
        draw.text((cx, cy), "No tasks", font=font_item, fill=dim)
        return

    max_y = y + h - _CARD_PADDING
    for task in data.tasks:
        if cy + 30 > max_y:
            break

        # Priority indicator
        pri_mark = "●" if task.priority.lower() == "high" else "○"
        line = f"{pri_mark} {task.title}"
        draw.text((cx, cy), line, font=font_item, fill=white)
        bbox = draw.textbbox((0, 0), line, font=font_item)
        cy += (bbox[3] - bbox[1]) + 2

        # Tags on same or next line
        if task.tags:
            tag_str = "  ".join(f"#{t}" for t in task.tags)
            draw.text((cx + 16, cy), tag_str, font=font_tag, fill=tag_color)
            bbox = draw.textbbox((0, 0), tag_str, font=font_tag)
            cy += (bbox[3] - bbox[1]) + _LINE_SPACING
        else:
            cy += _LINE_SPACING


def _render_motivation_section(
    draw: ImageDraw.ImageDraw,
    x: int, y: int, w: int, h: int,
    data: DashboardData, font_size: int, opacity: float,
) -> None:
    """Render motivation comment card."""
    _draw_card(draw, x, y, w, h, opacity)

    font_title = _get_font(max(font_size // 2 + 4, 16))
    font_body = _get_font(max(font_size // 2 - 2, 12))

    cx = x + _CARD_PADDING
    cy = y + _CARD_PADDING
    white = (255, 255, 255, 255)
    dim = (180, 180, 180, 255)

    # Section header
    draw.text((cx, cy), "💬 Today", font=font_title, fill=white)
    bbox = draw.textbbox((0, 0), "💬 Today", font=font_title)
    cy += (bbox[3] - bbox[1]) + _LINE_SPACING * 2

    if data.motivation is None or not data.motivation.comment:
        draw.text((cx, cy), "No message yet", font=font_body, fill=dim)
        return

    # Word-wrap the motivation text within the card width
    max_text_width = w - _CARD_PADDING * 2
    max_y = y + h - _CARD_PADDING

    for line in data.motivation.comment.split("\n"):
        if cy + 20 > max_y:
            break
        # Simple character-level wrapping for CJK text
        wrapped = _wrap_text(draw, line, font_body, max_text_width)
        for wline in wrapped:
            if cy + 20 > max_y:
                break
            draw.text((cx, cy), wline, font=font_body, fill=white)
            bbox = draw.textbbox((0, 0), wline, font=font_body)
            cy += (bbox[3] - bbox[1]) + _LINE_SPACING


def _wrap_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.FreeTypeFont,
    max_width: int,
) -> list[str]:
    """Wrap text to fit within max_width pixels."""
    if not text:
        return [""]

    lines = []
    current = ""
    for char in text:
        test = current + char
        bbox = draw.textbbox((0, 0), test, font=font)
        if (bbox[2] - bbox[0]) > max_width and current:
            lines.append(current)
            current = char
        else:
            current = test
    if current:
        lines.append(current)
    return lines


_SECTION_RENDERERS = {
    "weather": _render_weather_section,
    "tasks": _render_tasks_section,
    "motivation": _render_motivation_section,
}


def render_dashboard(
    base_image_path: str,
    output_path: str,
    data: DashboardData,
    config: dict,
) -> str:
    """Render the 3-section dashboard overlay onto a wallpaper image.

    Args:
        base_image_path: Path to the background wallpaper image.
        output_path: Where to save the rendered result.
        data: DashboardData containing weather, tasks, motivation.
        config: Dashboard config dict with keys: width, height, sections,
                section_weights, card_opacity, font_size.
    Returns:
        The output_path.
    """
    img = Image.open(base_image_path).convert("RGBA")
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    img_w, img_h = img.size
    dash_w = config.get("width", 1500)
    dash_h = config.get("height", 1000)
    sections = config.get("sections", ["weather", "tasks", "motivation"])
    weights = config.get("section_weights", [30, 40, 30])
    opacity = config.get("card_opacity", 0.6)
    font_size = config.get("font_size", 36)

    # Center the dashboard area
    dash_x = (img_w - dash_w) // 2
    dash_y = (img_h - dash_h) // 2

    # Calculate section heights from weights
    active_sections = [s for s in sections if s in _SECTION_RENDERERS]
    if not active_sections:
        # No sections to render, just save the image as-is
        img.convert("RGB").save(output_path, "JPEG", quality=95)
        return output_path

    # Normalize weights to match active sections
    active_weights = weights[:len(active_sections)]
    total_weight = sum(active_weights)
    available_height = dash_h - _CARD_GAP * (len(active_sections) - 1)
    section_heights = [
        int(available_height * w / total_weight) for w in active_weights
    ]

    # Render each section
    current_y = dash_y
    for i, section_name in enumerate(active_sections):
        renderer = _SECTION_RENDERERS[section_name]
        section_h = section_heights[i]
        renderer(draw, dash_x, current_y, dash_w, section_h, data, font_size, opacity)
        current_y += section_h + _CARD_GAP

    result = Image.alpha_composite(img, overlay).convert("RGB")
    result.save(output_path, "JPEG", quality=95)
    logger.info("Rendered dashboard to: %s", output_path)
    return output_path
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /Users/naoki/development/03_my-devlopment/weather-desktop && python -m pytest tests/infra/test_wallpaper_renderer.py -v`
Expected: PASS (all 7 tests)

- [ ] **Step 5: Delete old renderer files**

```bash
rm src/wallpaper_renderer.py tests/test_wallpaper_renderer.py
```

- [ ] **Step 6: Commit**

```bash
git add src/infra/wallpaper_renderer.py tests/infra/test_wallpaper_renderer.py
git add -u
git commit -m "feat: rewrite wallpaper_renderer with 3-section card layout"
```

---

## Task 8: Extract dock_icon.py with task badge

**Files:**
- Create: `src/infra/dock_icon.py`
- Create: `tests/infra/test_dock_icon.py`
- Delete: `src/dock_app.py` (after Task 9)
- Delete: `tests/test_dock_app.py` (after Task 9)

- [ ] **Step 1: Write the failing tests**

`tests/infra/test_dock_icon.py`:
```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /Users/naoki/development/03_my-devlopment/weather-desktop && python -m pytest tests/infra/test_dock_icon.py -v`
Expected: FAIL

- [ ] **Step 3: Implement dock_icon.py**

`src/infra/dock_icon.py`:
```python
"""macOS Dock icon generation with weather info and task badge."""

import io
import logging
from PIL import Image, ImageDraw

from domain.models import WeatherData

logger = logging.getLogger(__name__)

ICON_SIZE = 128

_ICON_TEXT = {
    "clear": "晴", "partly_cloudy": "曇", "fog": "霧", "drizzle": "小雨",
    "rain": "雨", "snow": "雪", "shower": "雨", "thunderstorm": "雷", "unknown": "？",
}

_ICON_BG = {
    "clear": (30, 100, 180, 220), "partly_cloudy": (80, 90, 110, 220),
    "fog": (100, 100, 110, 220), "drizzle": (60, 70, 100, 220),
    "rain": (40, 50, 80, 220), "snow": (120, 130, 150, 220),
    "shower": (50, 55, 85, 220), "thunderstorm": (30, 30, 50, 220),
    "unknown": (60, 60, 60, 220),
}


def _get_font(size: int):
    """Get font — import from infra.wallpaper_renderer to share logic."""
    import os
    from PIL import ImageFont
    font_dir = os.path.join(os.path.dirname(__file__), "..", "..", "fonts")
    font_path = os.path.join(font_dir, "NotoSansJP-Regular.ttf")
    fallbacks = [
        "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",
        "/Library/Fonts/Arial Unicode.ttf",
        "/System/Library/Fonts/HelveticaNeue.ttc",
    ]
    if os.path.exists(font_path):
        return ImageFont.truetype(font_path, size)
    for fb in fallbacks:
        try:
            return ImageFont.truetype(fb, size)
        except OSError:
            continue
    return ImageFont.load_default()


def generate_dock_icon(
    weather: WeatherData, mapping: dict, task_count: int = 0
) -> Image.Image:
    """Generate a 128x128 dock icon with weather info and optional task badge."""
    img = Image.new("RGBA", (ICON_SIZE, ICON_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    category = mapping.get("category", "unknown")
    bg_color = _ICON_BG.get(category, _ICON_BG["unknown"])

    draw.rounded_rectangle(
        [0, 0, ICON_SIZE - 1, ICON_SIZE - 1], radius=24, fill=bg_color,
    )

    # Weather text label (top)
    weather_text = _ICON_TEXT.get(category, "？")
    font_label = _get_font(30)
    bbox = draw.textbbox((0, 0), weather_text, font=font_label)
    label_w = bbox[2] - bbox[0]
    draw.text(((ICON_SIZE - label_w) / 2, 10), weather_text, font=font_label, fill="white")

    # Temperature (middle)
    font_temp = _get_font(28)
    temp_text = f"{weather.temperature:.0f}°C"
    bbox = draw.textbbox((0, 0), temp_text, font=font_temp)
    temp_w = bbox[2] - bbox[0]
    draw.text(((ICON_SIZE - temp_w) / 2, 48), temp_text, font=font_temp, fill="white")

    # Precipitation (bottom)
    font_small = _get_font(18)
    precip_text = f"降水{weather.precipitation_probability}%"
    bbox = draw.textbbox((0, 0), precip_text, font=font_small)
    precip_w = bbox[2] - bbox[0]
    draw.text(
        ((ICON_SIZE - precip_w) / 2, 88), precip_text,
        font=font_small, fill=(200, 220, 255, 255),
    )

    # Task count badge (top-right corner)
    if task_count > 0:
        badge_r = 16
        badge_cx = ICON_SIZE - badge_r - 4
        badge_cy = badge_r + 4
        draw.ellipse(
            [badge_cx - badge_r, badge_cy - badge_r,
             badge_cx + badge_r, badge_cy + badge_r],
            fill=(220, 50, 50, 255),
        )
        badge_font = _get_font(14)
        badge_text = str(min(task_count, 99))
        bbox = draw.textbbox((0, 0), badge_text, font=badge_font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        draw.text(
            (badge_cx - tw / 2, badge_cy - th / 2 - 2),
            badge_text, font=badge_font, fill="white",
        )

    return img


def pil_to_nsimage(pil_image: Image.Image):
    """Convert PIL Image to NSImage via TIFF bytes."""
    import AppKit
    buf = io.BytesIO()
    pil_image.save(buf, format="TIFF")
    ns_data = AppKit.NSData.dataWithBytes_length_(buf.getvalue(), len(buf.getvalue()))
    return AppKit.NSImage.alloc().initWithData_(ns_data)


def set_dock_icon(pil_image: Image.Image) -> None:
    """Set the macOS Dock icon to the given PIL image."""
    import AppKit
    ns_image = pil_to_nsimage(pil_image)
    AppKit.NSApp.setApplicationIconImage_(ns_image)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /Users/naoki/development/03_my-devlopment/weather-desktop && python -m pytest tests/infra/test_dock_icon.py -v`
Expected: PASS (all 4 tests)

- [ ] **Step 5: Commit**

```bash
git add src/infra/dock_icon.py tests/infra/test_dock_icon.py
git commit -m "feat: add dock_icon with task count badge"
```

---

## Task 9: Implement settings_window — dashboard settings UI

**Files:**
- Create: `src/infra/settings_window.py`
- Create: `tests/infra/test_settings_window.py`
- Delete: `src/dock_app.py`
- Delete: `tests/test_dock_app.py`

- [ ] **Step 1: Write the failing tests**

`tests/infra/test_settings_window.py`:
```python
import os
import tempfile
from unittest.mock import MagicMock, patch
from infra.settings_window import SettingsWindow


def _make_config():
    return {
        "obsidian": {
            "vault_dir": "/tmp/vault",
            "check_interval_min": 5,
            "tasks": {"max_items": 8, "status": "todo", "priority": "high"},
            "motivation_file": "/tmp/vault/dashboard/motivation.md",
        },
        "dashboard": {
            "width": 1500, "height": 1000,
            "sections": ["weather", "tasks", "motivation"],
            "section_weights": [30, 40, 30],
            "card_opacity": 0.6, "font_size": 36,
        },
    }


def test_settings_window_can_be_instantiated():
    config = _make_config()
    on_update = MagicMock()
    on_save = MagicMock()
    sw = SettingsWindow(config, on_update_callback=on_update, on_save_callback=on_save)
    assert sw is not None
    assert sw._config == config


def test_settings_window_get_config_returns_current():
    config = _make_config()
    sw = SettingsWindow(config, on_update_callback=MagicMock(), on_save_callback=MagicMock())
    result = sw.get_config()
    assert result["dashboard"]["font_size"] == 36
    assert result["obsidian"]["tasks"]["max_items"] == 8


def test_settings_window_update_section_order():
    config = _make_config()
    sw = SettingsWindow(config, on_update_callback=MagicMock(), on_save_callback=MagicMock())
    sw.set_section_order(["tasks", "weather", "motivation"])
    assert sw._config["dashboard"]["sections"] == ["tasks", "weather", "motivation"]


def test_settings_window_toggle_section():
    config = _make_config()
    sw = SettingsWindow(config, on_update_callback=MagicMock(), on_save_callback=MagicMock())
    sw.toggle_section("tasks", enabled=False)
    assert "tasks" not in sw._config["dashboard"]["sections"]
    sw.toggle_section("tasks", enabled=True)
    assert "tasks" in sw._config["dashboard"]["sections"]
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /Users/naoki/development/03_my-devlopment/weather-desktop && python -m pytest tests/infra/test_settings_window.py -v`
Expected: FAIL

- [ ] **Step 3: Implement settings_window.py**

`src/infra/settings_window.py`:
```python
"""Dashboard settings window using tkinter."""

import logging
import os
import tkinter as tk
from tkinter import ttk, filedialog
from typing import Callable, Optional

import yaml

logger = logging.getLogger(__name__)


class SettingsWindow:
    """Settings dashboard for configuring wallpaper display."""

    def __init__(
        self,
        config: dict,
        on_update_callback: Callable,
        on_save_callback: Callable,
    ) -> None:
        self._config = config
        self._on_update = on_update_callback
        self._on_save = on_save_callback
        self._root: Optional[tk.Tk] = None
        self._task_editor_window: Optional[tk.Toplevel] = None

    def get_config(self) -> dict:
        return self._config

    def set_section_order(self, order: list[str]) -> None:
        self._config["dashboard"]["sections"] = order

    def toggle_section(self, section: str, enabled: bool) -> None:
        sections = self._config["dashboard"]["sections"]
        if enabled and section not in sections:
            sections.append(section)
        elif not enabled and section in sections:
            sections.remove(section)

    def _build_ui(self) -> None:
        """Build the settings UI with tabs."""
        notebook = ttk.Notebook(self._root)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Tab 1: Display Settings
        display_frame = ttk.Frame(notebook)
        notebook.add(display_frame, text="表示設定")
        self._build_display_tab(display_frame)

        # Tab 2: Vault Settings
        vault_frame = ttk.Frame(notebook)
        notebook.add(vault_frame, text="Vault設定")
        self._build_vault_tab(vault_frame)

        # Tab 3: Task Editor
        task_frame = ttk.Frame(notebook)
        notebook.add(task_frame, text="タスク管理")
        self._build_task_tab(task_frame)

        # Bottom buttons
        btn_frame = ttk.Frame(self._root)
        btn_frame.pack(fill="x", padx=10, pady=(0, 10))

        ttk.Button(btn_frame, text="即時更新", command=self._on_refresh).pack(
            side="left", padx=5
        )
        ttk.Button(btn_frame, text="保存", command=self._on_save_click).pack(
            side="right", padx=5
        )

    def _build_display_tab(self, parent: ttk.Frame) -> None:
        """Build display settings tab: sections, opacity, font, weights."""
        dash = self._config["dashboard"]

        # Section toggles
        lf = ttk.LabelFrame(parent, text="セクション表示")
        lf.pack(fill="x", padx=10, pady=5)

        self._section_vars = {}
        for section in ["weather", "tasks", "motivation"]:
            var = tk.BooleanVar(value=section in dash["sections"])
            self._section_vars[section] = var
            ttk.Checkbutton(lf, text=section, variable=var).pack(anchor="w", padx=10)

        # Section order
        lf2 = ttk.LabelFrame(parent, text="セクション順序 (カンマ区切り)")
        lf2.pack(fill="x", padx=10, pady=5)
        self._order_var = tk.StringVar(value=", ".join(dash["sections"]))
        ttk.Entry(lf2, textvariable=self._order_var, width=40).pack(padx=10, pady=5)

        # Weights
        lf3 = ttk.LabelFrame(parent, text="セクション比率 (カンマ区切り)")
        lf3.pack(fill="x", padx=10, pady=5)
        self._weights_var = tk.StringVar(
            value=", ".join(str(w) for w in dash["section_weights"])
        )
        ttk.Entry(lf3, textvariable=self._weights_var, width=40).pack(padx=10, pady=5)

        # Opacity slider
        lf4 = ttk.LabelFrame(parent, text="カード透明度")
        lf4.pack(fill="x", padx=10, pady=5)
        self._opacity_var = tk.DoubleVar(value=dash["card_opacity"])
        tk.Scale(
            lf4, from_=0.0, to=1.0, resolution=0.05,
            orient="horizontal", variable=self._opacity_var,
        ).pack(fill="x", padx=10)

        # Font size
        lf5 = ttk.LabelFrame(parent, text="フォントサイズ")
        lf5.pack(fill="x", padx=10, pady=5)
        self._fontsize_var = tk.IntVar(value=dash["font_size"])
        tk.Scale(
            lf5, from_=12, to=72, orient="horizontal", variable=self._fontsize_var,
        ).pack(fill="x", padx=10)

    def _build_vault_tab(self, parent: ttk.Frame) -> None:
        """Build vault settings tab: directories, task count."""
        obs = self._config["obsidian"]

        # Vault directory
        lf = ttk.LabelFrame(parent, text="Vault ディレクトリ")
        lf.pack(fill="x", padx=10, pady=5)
        self._vault_dir_var = tk.StringVar(value=obs["vault_dir"])
        row = ttk.Frame(lf)
        row.pack(fill="x", padx=10, pady=5)
        ttk.Entry(row, textvariable=self._vault_dir_var, width=35).pack(side="left")
        ttk.Button(row, text="参照", command=self._browse_vault_dir).pack(side="left", padx=5)

        # Motivation file
        lf2 = ttk.LabelFrame(parent, text="励ましコメントファイル")
        lf2.pack(fill="x", padx=10, pady=5)
        self._motivation_var = tk.StringVar(value=obs["motivation_file"])
        row2 = ttk.Frame(lf2)
        row2.pack(fill="x", padx=10, pady=5)
        ttk.Entry(row2, textvariable=self._motivation_var, width=35).pack(side="left")
        ttk.Button(row2, text="参照", command=self._browse_motivation_file).pack(
            side="left", padx=5
        )

        # Task max items
        lf3 = ttk.LabelFrame(parent, text="タスク表示件数")
        lf3.pack(fill="x", padx=10, pady=5)
        self._max_tasks_var = tk.IntVar(value=obs["tasks"]["max_items"])
        tk.Scale(
            lf3, from_=1, to=20, orient="horizontal", variable=self._max_tasks_var,
        ).pack(fill="x", padx=10)

    def _build_task_tab(self, parent: ttk.Frame) -> None:
        """Build task editor tab: file list + text editor."""
        # File list (left side)
        list_frame = ttk.Frame(parent)
        list_frame.pack(side="left", fill="y", padx=5, pady=5)

        ttk.Label(list_frame, text="タスクファイル:").pack(anchor="w")
        self._task_listbox = tk.Listbox(list_frame, width=30, height=15)
        self._task_listbox.pack(fill="y", expand=True)
        self._task_listbox.bind("<<ListboxSelect>>", self._on_task_select)

        ttk.Button(list_frame, text="更新", command=self._refresh_task_list).pack(
            fill="x", pady=5
        )

        # Editor (right side)
        editor_frame = ttk.Frame(parent)
        editor_frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)

        ttk.Label(editor_frame, text="内容:").pack(anchor="w")
        self._task_editor = tk.Text(editor_frame, wrap="word", width=50, height=15)
        self._task_editor.pack(fill="both", expand=True)

        ttk.Button(editor_frame, text="保存", command=self._save_task_file).pack(
            anchor="e", pady=5
        )

        self._task_files: list[str] = []

    def _browse_vault_dir(self) -> None:
        path = filedialog.askdirectory(initialdir=self._vault_dir_var.get())
        if path:
            self._vault_dir_var.set(path)

    def _browse_motivation_file(self) -> None:
        path = filedialog.askopenfilename(
            initialdir=os.path.dirname(self._motivation_var.get()),
            filetypes=[("Markdown", "*.md"), ("All", "*.*")],
        )
        if path:
            self._motivation_var.set(path)

    def _refresh_task_list(self) -> None:
        """Scan vault tasks directory and populate listbox."""
        self._task_listbox.delete(0, tk.END)
        self._task_files = []

        vault_dir = self._vault_dir_var.get()
        tasks_dir = os.path.join(vault_dir, "tasks")
        if not os.path.isdir(tasks_dir):
            return

        from pathlib import Path
        for md_file in sorted(Path(tasks_dir).rglob("*.md")):
            self._task_files.append(str(md_file))
            display = str(md_file.relative_to(tasks_dir))
            self._task_listbox.insert(tk.END, display)

    def _on_task_select(self, event) -> None:
        """Load selected task file into editor."""
        selection = self._task_listbox.curselection()
        if not selection:
            return

        idx = selection[0]
        file_path = self._task_files[idx]
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            self._task_editor.delete("1.0", tk.END)
            self._task_editor.insert("1.0", content)
        except Exception:
            logger.exception("Failed to read task file: %s", file_path)

    def _save_task_file(self) -> None:
        """Save editor content back to the selected task file."""
        selection = self._task_listbox.curselection()
        if not selection:
            return

        idx = selection[0]
        file_path = self._task_files[idx]
        content = self._task_editor.get("1.0", tk.END)
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            logger.info("Saved task file: %s", file_path)
        except Exception:
            logger.exception("Failed to save task file: %s", file_path)

    def _apply_display_settings(self) -> None:
        """Read UI values back into config."""
        dash = self._config["dashboard"]

        # Sections
        active = [s for s, v in self._section_vars.items() if v.get()]
        # Respect order from order field
        order_str = self._order_var.get()
        ordered = [s.strip() for s in order_str.split(",") if s.strip()]
        dash["sections"] = [s for s in ordered if s in active]

        # Weights
        weight_str = self._weights_var.get()
        try:
            dash["section_weights"] = [int(w.strip()) for w in weight_str.split(",")]
        except ValueError:
            pass

        dash["card_opacity"] = self._opacity_var.get()
        dash["font_size"] = self._fontsize_var.get()

        # Vault settings
        obs = self._config["obsidian"]
        obs["vault_dir"] = self._vault_dir_var.get()
        obs["motivation_file"] = self._motivation_var.get()
        obs["tasks"]["max_items"] = self._max_tasks_var.get()

    def _on_refresh(self) -> None:
        """Immediate wallpaper update."""
        self._apply_display_settings()
        self._on_update()

    def _on_save_click(self) -> None:
        """Save config and trigger update."""
        self._apply_display_settings()
        self._on_save(self._config)
        self._on_update()

    def _show_window(self) -> None:
        if self._root:
            self._root.deiconify()
            self._root.lift()
            self._root.focus_force()

    def _hide_window(self) -> None:
        if self._root:
            self._root.withdraw()

    def run(self, on_tick: Callable, weather_interval_ms: int, obsidian_interval_ms: int) -> None:
        """Start the settings window with tkinter mainloop."""
        self._root = tk.Tk()
        self._root.title("Desktop Dashboard 設定")
        self._root.geometry("700x500")
        self._root.resizable(True, True)

        self._root.protocol("WM_DELETE_WINDOW", self._hide_window)
        self._root.createcommand("::tk::mac::ReopenApplication", self._show_window)

        self._build_ui()
        self._refresh_task_list()

        # Start hidden
        self._root.withdraw()

        # Schedule ticks via tkinter.after()
        def weather_tick():
            on_tick("weather")
            self._root.after(weather_interval_ms, weather_tick)

        def obsidian_tick():
            on_tick("obsidian")
            self._root.after(obsidian_interval_ms, obsidian_tick)

        # Initial tick after event loop starts
        self._root.after(100, lambda: on_tick("all"))
        self._root.after(weather_interval_ms, weather_tick)
        self._root.after(obsidian_interval_ms, obsidian_tick)

        self._root.mainloop()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /Users/naoki/development/03_my-devlopment/weather-desktop && python -m pytest tests/infra/test_settings_window.py -v`
Expected: PASS (all 4 tests)

- [ ] **Step 5: Delete old dock_app files**

```bash
rm src/dock_app.py tests/test_dock_app.py
```

- [ ] **Step 6: Commit**

```bash
git add src/infra/settings_window.py tests/infra/test_settings_window.py
git add -u
git commit -m "feat: add settings_window dashboard UI with task editor"
```

---

## Task 10: Rewrite main.py — orchestrator with tkinter scheduling

**Files:**
- Modify: `src/main.py`
- Modify: `tests/test_main.py`

- [ ] **Step 1: Write the failing tests**

`tests/test_main.py` (complete rewrite):
```python
from unittest.mock import patch, MagicMock
from main import DashboardApp
from domain.models import WeatherData, TaskItem, MotivationData


def _make_config():
    return {
        "location": {"latitude": 35.6762, "longitude": 139.6503},
        "check_interval_min": 10,
        "weather": {"check_interval_min": 10},
        "overlay": {"position": "bottom_right", "opacity": 0.7, "font_size": 48},
        "unsplash": {"access_key": "test_key"},
        "yahoo": {"client_id": ""},
        "cache": {"max_images": 50},
        "obsidian": {
            "vault_dir": "/tmp/vault",
            "check_interval_min": 5,
            "tasks": {"max_items": 8, "status": "todo", "priority": "high"},
            "motivation_file": "/tmp/vault/dashboard/motivation.md",
        },
        "dashboard": {
            "width": 1500, "height": 1000,
            "sections": ["weather", "tasks", "motivation"],
            "section_weights": [30, 40, 30],
            "card_opacity": 0.6, "font_size": 36,
        },
    }


def _make_weather(code=0, temp=22.5):
    return WeatherData(
        temperature=temp, weather_code=code, wind_speed=3.2,
        temp_max=28.0, temp_min=18.0, precipitation_probability=10,
    )


@patch("main.set_wallpaper")
@patch("main.render_dashboard")
@patch("main.ImageFetcher")
@patch("main.fetch_open_meteo")
@patch("main.read_tasks")
@patch("main.read_motivation")
@patch("main.load_config")
def test_tick_all_fetches_weather_tasks_and_renders(
    mock_config, mock_motivation, mock_tasks, mock_fetch,
    mock_image_cls, mock_render, mock_set
):
    mock_config.return_value = _make_config()
    mock_fetch.return_value = _make_weather()
    mock_tasks.return_value = [
        TaskItem(title="Task 1", file_path="/a.md", priority="high",
                 status="todo", progress="0/1", tags=[]),
    ]
    mock_motivation.return_value = MotivationData(comment="Keep going!")
    mock_image_instance = MagicMock()
    mock_image_instance.get_image.return_value = "/tmp/base.jpg"
    mock_image_cls.return_value = mock_image_instance
    mock_render.return_value = "/tmp/output.jpg"
    mock_set.return_value = True

    app = DashboardApp()
    app.tick_all()

    mock_fetch.assert_called_once()
    mock_tasks.assert_called_once()
    mock_motivation.assert_called_once()
    mock_render.assert_called_once()
    mock_set.assert_called_once()


@patch("main.set_wallpaper")
@patch("main.render_dashboard")
@patch("main.ImageFetcher")
@patch("main.fetch_open_meteo")
@patch("main.read_tasks")
@patch("main.read_motivation")
@patch("main.load_config")
def test_tick_weather_only_updates_weather(
    mock_config, mock_motivation, mock_tasks, mock_fetch,
    mock_image_cls, mock_render, mock_set
):
    mock_config.return_value = _make_config()
    mock_fetch.return_value = _make_weather()
    mock_tasks.return_value = []
    mock_motivation.return_value = None
    mock_image_instance = MagicMock()
    mock_image_instance.get_image.return_value = "/tmp/base.jpg"
    mock_image_cls.return_value = mock_image_instance
    mock_render.return_value = "/tmp/output.jpg"
    mock_set.return_value = True

    app = DashboardApp()
    app.tick_all()  # initial
    mock_fetch.reset_mock()

    mock_fetch.return_value = _make_weather(temp=25.0)
    app.tick_weather()

    mock_fetch.assert_called_once()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /Users/naoki/development/03_my-devlopment/weather-desktop && python -m pytest tests/test_main.py -v`
Expected: FAIL

- [ ] **Step 3: Rewrite main.py**

`src/main.py`:
```python
"""Desktop Dashboard — main orchestrator."""

import logging
import os
import signal
import sys
from typing import Optional

from config import load_config
from domain.weather_fetcher import fetch_open_meteo, WeatherData
from domain.weather_mapper import WeatherMapper
from domain.task_reader import read_tasks
from domain.motivation_reader import read_motivation
from domain.models import DashboardData
from infra.image_fetcher import ImageFetcher
from infra.wallpaper_renderer import render_dashboard
from infra.wallpaper_setter import set_wallpaper

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class DashboardApp:
    def __init__(self, config_path: Optional[str] = None) -> None:
        if config_path is None:
            config_path = os.path.join(BASE_DIR, "config.yaml")
        self._config = load_config(config_path)
        self._mapper = WeatherMapper()
        self._image_fetcher = ImageFetcher(
            cache_dir=os.path.join(BASE_DIR, "cache"),
            defaults_dir=os.path.join(BASE_DIR, "defaults"),
            access_key=self._config["unsplash"]["access_key"],
            max_images=self._config["cache"]["max_images"],
        )
        self._prev_weather_code: Optional[int] = None
        self._prev_temperature: Optional[float] = None
        self._current_base_image: Optional[str] = None
        self._output_index = 0
        self._current_weather: Optional[WeatherData] = None
        self._current_mapping: Optional[dict] = None
        self._current_tasks: list = []
        self._current_motivation = None
        self._on_update_callback = None

    def tick_weather(self) -> None:
        """Fetch weather data and re-render if changed."""
        lat = self._config["location"]["latitude"]
        lon = self._config["location"]["longitude"]

        weather = fetch_open_meteo(lat, lon)
        if weather is None:
            logger.warning("Failed to fetch weather, skipping")
            return

        code_changed = weather.weather_code != self._prev_weather_code
        temp_changed = weather.temperature != self._prev_temperature

        if not code_changed and not temp_changed:
            logger.info("No weather change, skipping")
            return

        self._current_weather = weather
        self._current_mapping = self._mapper.get_mapping(weather.weather_code)

        if code_changed or self._current_base_image is None:
            image_path = self._image_fetcher.get_image(
                self._current_mapping.get("category", "unknown"),
                self._current_mapping["query"],
            )
            if image_path is None:
                logger.error("No image available, skipping")
                return
            self._current_base_image = image_path

        self._prev_weather_code = weather.weather_code
        self._prev_temperature = weather.temperature

        self._render_and_set()

    def tick_obsidian(self) -> None:
        """Fetch tasks and motivation from Obsidian vault and re-render."""
        obs_config = self._config["obsidian"]
        vault_dir = obs_config.get("vault_dir", "")
        task_config = obs_config.get("tasks", {})

        if vault_dir:
            tasks_dir = os.path.join(vault_dir, "tasks")
            self._current_tasks = read_tasks(
                tasks_dir,
                status=task_config.get("status", "todo"),
                priority=task_config.get("priority", "high"),
                max_items=task_config.get("max_items", 8),
            )

        motivation_file = obs_config.get("motivation_file", "")
        if motivation_file:
            self._current_motivation = read_motivation(motivation_file)

        self._render_and_set()

    def tick_all(self) -> None:
        """Full update: weather + obsidian + render."""
        lat = self._config["location"]["latitude"]
        lon = self._config["location"]["longitude"]

        weather = fetch_open_meteo(lat, lon)
        if weather is None:
            logger.warning("Failed to fetch weather, skipping")
            return

        self._current_weather = weather
        self._current_mapping = self._mapper.get_mapping(weather.weather_code)

        code_changed = weather.weather_code != self._prev_weather_code
        if code_changed or self._current_base_image is None:
            image_path = self._image_fetcher.get_image(
                self._current_mapping.get("category", "unknown"),
                self._current_mapping["query"],
            )
            if image_path is None:
                logger.error("No image available, skipping")
                return
            self._current_base_image = image_path

        self._prev_weather_code = weather.weather_code
        self._prev_temperature = weather.temperature

        obs_config = self._config["obsidian"]
        vault_dir = obs_config.get("vault_dir", "")
        task_config = obs_config.get("tasks", {})

        if vault_dir:
            tasks_dir = os.path.join(vault_dir, "tasks")
            self._current_tasks = read_tasks(
                tasks_dir,
                status=task_config.get("status", "todo"),
                priority=task_config.get("priority", "high"),
                max_items=task_config.get("max_items", 8),
            )

        motivation_file = obs_config.get("motivation_file", "")
        if motivation_file:
            self._current_motivation = read_motivation(motivation_file)

        self._render_and_set()

    def _render_and_set(self) -> None:
        """Render dashboard and set wallpaper."""
        if self._current_weather is None or self._current_base_image is None:
            return

        data = DashboardData(
            weather=self._current_weather,
            weather_mapping=self._current_mapping or {},
            tasks=self._current_tasks,
            motivation=self._current_motivation,
        )

        self._output_index = 1 - self._output_index
        output_path = os.path.join(
            BASE_DIR, f"output_wallpaper_{self._output_index}.jpg"
        )

        rendered_path = render_dashboard(
            self._current_base_image, output_path, data,
            self._config["dashboard"],
        )

        set_wallpaper(rendered_path)
        logger.info(
            "Dashboard updated: %s %.1f°C, %d tasks",
            self._current_mapping.get("icon", ""),
            self._current_weather.temperature,
            len(self._current_tasks),
        )

        if self._on_update_callback:
            self._on_update_callback(
                self._current_weather, self._current_mapping, len(self._current_tasks)
            )

    def run_headless(self) -> None:
        """Run without UI — for testing or headless mode."""
        import time
        logger.info("Desktop Dashboard started (headless)")
        self.tick_all()

        def handle_sigterm(*_):
            logger.info("Shutting down...")
            sys.exit(0)

        signal.signal(signal.SIGTERM, handle_sigterm)
        signal.signal(signal.SIGINT, handle_sigterm)

        weather_interval = self._config.get("weather", {}).get("check_interval_min", 10)
        obsidian_interval = self._config["obsidian"].get("check_interval_min", 5)

        import schedule
        schedule.every(weather_interval).minutes.do(self.tick_weather)
        schedule.every(obsidian_interval).minutes.do(self.tick_obsidian)

        while True:
            schedule.run_pending()
            time.sleep(1)


def _save_config(config: dict) -> None:
    """Save config back to config.yaml."""
    config_path = os.path.join(BASE_DIR, "config.yaml")
    with open(config_path, "w") as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
    logger.info("Config saved to %s", config_path)


if __name__ == "__main__":
    import yaml

    app = DashboardApp()

    if sys.platform == "darwin" and "--headless" not in sys.argv:
        from infra.dock_icon import generate_dock_icon, set_dock_icon
        from infra.settings_window import SettingsWindow

        def on_update(weather, mapping, task_count):
            try:
                icon_img = generate_dock_icon(weather, mapping, task_count)
                set_dock_icon(icon_img)
            except Exception:
                logger.exception("Failed to update dock icon")

        app._on_update_callback = on_update

        def on_tick(kind: str):
            try:
                if kind == "all":
                    app.tick_all()
                elif kind == "weather":
                    app.tick_weather()
                elif kind == "obsidian":
                    app.tick_obsidian()
            except Exception:
                logger.exception("Error during tick (%s)", kind)

        def on_save(config):
            _save_config(config)

        weather_ms = app._config.get("weather", {}).get("check_interval_min", 10) * 60 * 1000
        obsidian_ms = app._config["obsidian"].get("check_interval_min", 5) * 60 * 1000

        settings = SettingsWindow(
            app._config,
            on_update_callback=lambda: on_tick("all"),
            on_save_callback=on_save,
        )
        settings.run(on_tick, weather_ms, obsidian_ms)
    else:
        app.run_headless()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /Users/naoki/development/03_my-devlopment/weather-desktop && python -m pytest tests/test_main.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/main.py tests/test_main.py
git commit -m "feat: rewrite main.py as DashboardApp orchestrator"
```

---

## Task 11: Clean up — remove old files and update requirements

**Files:**
- Modify: `requirements.txt`
- Delete: remaining old test files (`tests/test_weather_mapper.py`, `tests/test_config.py` if not already moved)
- Modify: `.gitignore` (fix typo on line 7: `ioutput_wallpaper_*.jpg` → `output_wallpaper_*.jpg`)

- [ ] **Step 1: Update requirements.txt**

```
requests>=2.28
Pillow>=10.0
beautifulsoup4>=4.12
PyYAML>=6.0
pytest>=7.0
```

Removed: `schedule>=1.2` (headless mode still uses it — keep if headless is needed, remove if not)
Removed: `rumps>=0.4.0; sys_platform == "darwin"` (unused)

Actually, since `run_headless` uses `schedule`, keep it:

```
requests>=2.28
Pillow>=10.0
beautifulsoup4>=4.12
PyYAML>=6.0
schedule>=1.2
pytest>=7.0
```

- [ ] **Step 2: Fix .gitignore typo**

Change line 7 from `ioutput_wallpaper_*.jpg` to `output_wallpaper_*.jpg`.

- [ ] **Step 3: Remove any remaining old test/source files**

```bash
# Check what old files remain
ls tests/test_*.py 2>/dev/null
ls src/*.py | grep -v __init__ | grep -v config | grep -v main
```

Delete any files that were moved but not yet removed.

- [ ] **Step 4: Run full test suite**

Run: `cd /Users/naoki/development/03_my-devlopment/weather-desktop && python -m pytest -v`
Expected: ALL PASS

- [ ] **Step 5: Commit**

```bash
git add requirements.txt .gitignore
git add -u  # stage any remaining deletions
git commit -m "chore: clean up old files, update requirements, fix gitignore"
```

---

## Task 12: Rename repository to desktop-dashboard

**Files:**
- No file changes — GitHub + git remote operations only

- [ ] **Step 1: Rename on GitHub**

This must be done manually via GitHub UI:
1. Go to https://github.com/42Tokyonaokix/weather-desktop/settings
2. Change repository name to `desktop-dashboard`
3. Click "Rename"

- [ ] **Step 2: Update local remote URL**

```bash
cd /Users/naoki/development/03_my-devlopment/weather-desktop
git remote set-url origin https://github.com/42Tokyonaokix/desktop-dashboard.git
git remote -v  # verify
```

- [ ] **Step 3: Optionally rename local directory**

```bash
cd /Users/naoki/development/03_my-devlopment
mv weather-desktop desktop-dashboard
```

- [ ] **Step 4: Verify everything works**

```bash
cd /Users/naoki/development/03_my-devlopment/desktop-dashboard
python -m pytest -v
git status
git push
```

- [ ] **Step 5: Commit any final changes**

```bash
git add -A
git commit -m "chore: rename repository to desktop-dashboard"
```

---

## Summary of implementation order

| Task | Description | Dependencies |
|------|-------------|--------------|
| 1 | Directory structure + models | None |
| 2 | Migrate weather to domain | Task 1 |
| 3 | Migrate image_fetcher, wallpaper_setter to infra | Task 1 |
| 4 | Update config with new sections | Task 1 |
| 5 | Implement task_reader | Task 1 |
| 6 | Implement motivation_reader | Task 1 |
| 7 | Rewrite wallpaper_renderer (3-section) | Tasks 1, 2 |
| 8 | Extract dock_icon with badge | Tasks 1, 2 |
| 9 | Implement settings_window | Tasks 1, 4 |
| 10 | Rewrite main.py orchestrator | Tasks 2-9 |
| 11 | Clean up and update requirements | Task 10 |
| 12 | Rename repository | Task 11 |

Tasks 2-6 can be parallelized after Task 1. Tasks 7-9 can be parallelized after their dependencies. Task 10 requires all prior tasks. Tasks 11-12 are sequential finalization.
