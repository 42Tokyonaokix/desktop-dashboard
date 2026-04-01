# Weather Wallpaper Changer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a macOS desktop app that automatically changes wallpaper based on current weather, with weather info overlay.

**Architecture:** Polling-based architecture with change detection. 10-min interval polls Open-Meteo API, compares weather code to previous state, fetches wallpaper from Unsplash (or cache) on change, renders weather overlay with Pillow, sets wallpaper via AppleScript subprocess. All modules are flat Python files at project root.

**Tech Stack:** Python 3.10+, requests, Pillow, BeautifulSoup4, PyYAML, schedule

---

## File Structure

| File | Responsibility |
|------|---------------|
| `src/weather_mapper.py` | WMO weather code → search query, icon, description mapping |
| `src/config.py` | Load and validate config.yaml, provide defaults |
| `src/wallpaper_setter.py` | Set macOS wallpaper via AppleScript subprocess |
| `src/weather_fetcher.py` | Fetch weather data from Open-Meteo, YOLP, Yahoo scraping |
| `src/image_fetcher.py` | Fetch images from Unsplash, manage local cache + defaults |
| `src/wallpaper_renderer.py` | Render weather info overlay onto wallpaper image with Pillow |
| `src/main.py` | Orchestrator: scheduler, change detection, main loop |
| `config.yaml` | User configuration file |
| `requirements.txt` | Python dependencies |
| `tests/test_weather_mapper.py` | Tests for weather_mapper |
| `tests/test_config.py` | Tests for config |
| `tests/test_wallpaper_setter.py` | Tests for wallpaper_setter |
| `tests/test_weather_fetcher.py` | Tests for weather_fetcher |
| `tests/test_image_fetcher.py` | Tests for image_fetcher |
| `tests/test_wallpaper_renderer.py` | Tests for wallpaper_renderer |
| `tests/test_main.py` | Tests for main orchestrator |

---

### Task 1: Project Setup

**Files:**
- Create: `requirements.txt`
- Create: `config.yaml`
- Create: `.gitignore`
- Create: `src/__init__.py`
- Create: `tests/__init__.py`
- Create: `tests/conftest.py`

- [ ] **Step 1: Create requirements.txt**

```
requests>=2.28
Pillow>=10.0
beautifulsoup4>=4.12
PyYAML>=6.0
schedule>=1.2
pytest>=7.0
```

- [ ] **Step 2: Create .gitignore**

```
__pycache__/
*.pyc
cache/
*.egg-info/
.venv/
venv/
output_wallpaper_*.jpg
```

- [ ] **Step 3: Create config.yaml with defaults**

```yaml
# 位置情報
location:
  latitude: 35.6762
  longitude: 139.6503

# 更新設定
check_interval_min: 10

# オーバーレイ設定
overlay:
  position: bottom_right
  opacity: 0.7
  font_size: 48

# APIキー
unsplash:
  access_key: "YOUR_UNSPLASH_ACCESS_KEY"

yahoo:
  client_id: ""

# キャッシュ設定
cache:
  max_images: 50
```

- [ ] **Step 4: Create src/__init__.py (empty) and tests/__init__.py (empty)**

- [ ] **Step 5: Create tests/conftest.py**

```python
import os
import sys

# Add src to path so tests can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
```

- [ ] **Step 6: Create directory structure**

```bash
mkdir -p src tests cache defaults fonts icons
```

- [ ] **Step 7: Install dependencies and verify**

```bash
pip install -r requirements.txt
python -c "import requests, PIL, bs4, yaml, schedule; print('All dependencies OK')"
```

- [ ] **Step 8: Commit**

```bash
git add requirements.txt config.yaml .gitignore src/__init__.py tests/__init__.py tests/conftest.py
git commit -m "chore: initial project setup with dependencies and config"
```

---

### Task 2: Weather Mapper

**Files:**
- Create: `src/weather_mapper.py`
- Create: `tests/test_weather_mapper.py`

This module is pure data with no external dependencies. It maps WMO weather codes to search queries, icons, and Japanese descriptions.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_weather_mapper.py
from weather_mapper import WeatherMapper


def test_clear_sky_mapping():
    mapper = WeatherMapper()
    result = mapper.get_mapping(0)
    assert result["description"] == "快晴"
    assert result["icon"] == "☀️"
    assert "clear" in result["query"].lower()


def test_rain_mapping():
    mapper = WeatherMapper()
    result = mapper.get_mapping(63)
    assert result["description"] == "雨"
    assert result["icon"] == "🌧️"
    assert "rain" in result["query"].lower()


def test_snow_mapping():
    mapper = WeatherMapper()
    result = mapper.get_mapping(73)
    assert result["description"] == "雪"
    assert result["icon"] == "❄️"
    assert "snow" in result["query"].lower()


def test_thunderstorm_mapping():
    mapper = WeatherMapper()
    result = mapper.get_mapping(95)
    assert result["description"] == "雷雨"
    assert result["icon"] == "⛈️"


def test_unknown_code_returns_default():
    mapper = WeatherMapper()
    result = mapper.get_mapping(999)
    assert result["description"] == "不明"
    assert result["query"] is not None


def test_get_all_categories():
    mapper = WeatherMapper()
    categories = mapper.get_categories()
    assert "clear" in categories
    assert "rain" in categories
    assert "snow" in categories
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_weather_mapper.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'weather_mapper'`

- [ ] **Step 3: Write implementation**

```python
# src/weather_mapper.py
"""WMO weather code to search query, icon, and description mapping."""

from dataclasses import dataclass

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

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_weather_mapper.py -v`
Expected: All 6 tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/weather_mapper.py tests/test_weather_mapper.py
git commit -m "feat: add weather code to search query/icon mapper"
```

---

### Task 3: Config Loader

**Files:**
- Create: `src/config.py`
- Create: `tests/test_config.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_config.py
import os
import tempfile
from config import load_config


def test_load_config_from_file():
    content = """
location:
  latitude: 34.0
  longitude: 135.0
check_interval_min: 5
overlay:
  position: top_left
  opacity: 0.5
  font_size: 36
unsplash:
  access_key: "test_key"
yahoo:
  client_id: "yahoo_key"
cache:
  max_images: 30
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(content)
        f.flush()
        config = load_config(f.name)

    os.unlink(f.name)
    assert config["location"]["latitude"] == 34.0
    assert config["check_interval_min"] == 5
    assert config["unsplash"]["access_key"] == "test_key"


def test_load_config_uses_defaults_for_missing_keys():
    content = """
unsplash:
  access_key: "my_key"
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(content)
        f.flush()
        config = load_config(f.name)

    os.unlink(f.name)
    assert config["location"]["latitude"] == 35.6762
    assert config["check_interval_min"] == 10
    assert config["overlay"]["position"] == "bottom_right"
    assert config["cache"]["max_images"] == 50


def test_load_config_missing_file_returns_defaults():
    config = load_config("/nonexistent/path.yaml")
    assert config["location"]["latitude"] == 35.6762
    assert config["unsplash"]["access_key"] == ""
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_config.py -v`
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Write implementation**

```python
# src/config.py
"""Load and validate configuration from YAML file."""

import yaml
from pathlib import Path

DEFAULTS = {
    "location": {
        "latitude": 35.6762,
        "longitude": 139.6503,
    },
    "check_interval_min": 10,
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
}


def _deep_merge(base: dict, override: dict) -> dict:
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def load_config(path: str = "config.yaml") -> dict:
    config_path = Path(path)
    if not config_path.exists():
        return {**DEFAULTS, "unsplash": {"access_key": ""}}

    with open(config_path, "r") as f:
        user_config = yaml.safe_load(f) or {}

    return _deep_merge(DEFAULTS, user_config)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_config.py -v`
Expected: All 3 tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/config.py tests/test_config.py
git commit -m "feat: add YAML config loader with defaults and deep merge"
```

---

### Task 4: Wallpaper Setter

**Files:**
- Create: `src/wallpaper_setter.py`
- Create: `tests/test_wallpaper_setter.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_wallpaper_setter.py
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_wallpaper_setter.py -v`
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Write implementation**

```python
# src/wallpaper_setter.py
"""Set macOS desktop wallpaper via AppleScript subprocess."""

import subprocess
import logging

logger = logging.getLogger(__name__)


def _set_via_system_events(image_path: str) -> bool:
    script = f'''
    tell application "System Events"
        tell every desktop
            set picture to "{image_path}"
        end tell
    end tell
    '''
    result = subprocess.run(["osascript", "-e", script], capture_output=True, timeout=10)
    return result.returncode == 0


def _set_via_finder(image_path: str) -> bool:
    script = f'''
    tell application "Finder"
        set desktop picture to POSIX file "{image_path}"
    end tell
    '''
    result = subprocess.run(["osascript", "-e", script], capture_output=True, timeout=10)
    return result.returncode == 0


def set_wallpaper(image_path: str) -> bool:
    if _set_via_system_events(image_path):
        logger.info("Wallpaper set via System Events: %s", image_path)
        return True

    logger.warning("System Events failed, trying Finder fallback")
    if _set_via_finder(image_path):
        logger.info("Wallpaper set via Finder: %s", image_path)
        return True

    logger.error("Failed to set wallpaper: %s", image_path)
    return False
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_wallpaper_setter.py -v`
Expected: All 3 tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/wallpaper_setter.py tests/test_wallpaper_setter.py
git commit -m "feat: add wallpaper setter with System Events + Finder fallback"
```

---

### Task 5: Weather Fetcher

**Files:**
- Create: `src/weather_fetcher.py`
- Create: `tests/test_weather_fetcher.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_weather_fetcher.py
from unittest.mock import patch, MagicMock
import json
from weather_fetcher import fetch_open_meteo, fetch_yolp_rainfall, WeatherData


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


@patch("weather_fetcher.requests.get")
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


@patch("weather_fetcher.requests.get")
def test_fetch_open_meteo_failure_returns_none(mock_get):
    mock_get.side_effect = Exception("Network error")
    data = fetch_open_meteo(35.6762, 139.6503)
    assert data is None


@patch("weather_fetcher.requests.get")
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


@patch("weather_fetcher.requests.get")
def test_fetch_yolp_rainfall_no_client_id_returns_none(mock_get):
    rainfall = fetch_yolp_rainfall(35.6762, 139.6503, "")
    assert rainfall is None
    mock_get.assert_not_called()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_weather_fetcher.py -v`
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Write implementation**

```python
# src/weather_fetcher.py
"""Fetch weather data from Open-Meteo API and Yahoo YOLP API."""

import logging
from dataclasses import dataclass

import requests

logger = logging.getLogger(__name__)

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
YOLP_URL = "https://map.yahooapis.jp/weather/V1/place"


@dataclass
class WeatherData:
    temperature: float
    weather_code: int
    wind_speed: float
    temp_max: float
    temp_min: float
    precipitation_probability: int


def fetch_open_meteo(latitude: float, longitude: float) -> WeatherData | None:
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
) -> dict | None:
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

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_weather_fetcher.py -v`
Expected: All 4 tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/weather_fetcher.py tests/test_weather_fetcher.py
git commit -m "feat: add weather fetcher for Open-Meteo and YOLP APIs"
```

---

### Task 6: Image Fetcher

**Files:**
- Create: `src/image_fetcher.py`
- Create: `tests/test_image_fetcher.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_image_fetcher.py
import os
import tempfile
from unittest.mock import patch, MagicMock
from image_fetcher import ImageFetcher


def test_get_cached_image_when_exists():
    with tempfile.TemporaryDirectory() as cache_dir:
        # Create a fake cached image
        os.makedirs(os.path.join(cache_dir, "clear"), exist_ok=True)
        cached_path = os.path.join(cache_dir, "clear", "img1.jpg")
        with open(cached_path, "wb") as f:
            f.write(b"fake image data")

        fetcher = ImageFetcher(
            cache_dir=cache_dir, defaults_dir="/nonexistent", access_key="key", max_images=50
        )
        result = fetcher.get_image("clear", "clear blue sky")
        assert result == cached_path


@patch("image_fetcher.requests.get")
def test_fetch_from_unsplash_when_no_cache(mock_get):
    with tempfile.TemporaryDirectory() as cache_dir:
        # Mock Unsplash search response
        search_resp = MagicMock()
        search_resp.status_code = 200
        search_resp.json.return_value = {
            "results": [
                {"urls": {"raw": "https://example.com/photo.jpg"}, "id": "abc123"}
            ]
        }

        # Mock image download response
        download_resp = MagicMock()
        download_resp.status_code = 200
        download_resp.content = b"fake image bytes"

        mock_get.side_effect = [search_resp, download_resp]

        fetcher = ImageFetcher(
            cache_dir=cache_dir, defaults_dir="/nonexistent", access_key="test_key", max_images=50
        )
        result = fetcher.get_image("rain", "rainy day city")
        assert result is not None
        assert os.path.exists(result)
        assert "rain" in result


def test_fallback_to_default_image():
    with tempfile.TemporaryDirectory() as tmpdir:
        cache_dir = os.path.join(tmpdir, "cache")
        defaults_dir = os.path.join(tmpdir, "defaults")
        os.makedirs(defaults_dir, exist_ok=True)

        # Create a default image
        default_img = os.path.join(defaults_dir, "rain.jpg")
        with open(default_img, "wb") as f:
            f.write(b"default rain image")

        fetcher = ImageFetcher(
            cache_dir=cache_dir, defaults_dir=defaults_dir, access_key="", max_images=50
        )
        result = fetcher.get_image("rain", "rainy day")
        assert result == default_img


def test_no_image_available_returns_none():
    with tempfile.TemporaryDirectory() as tmpdir:
        fetcher = ImageFetcher(
            cache_dir=os.path.join(tmpdir, "cache"),
            defaults_dir=os.path.join(tmpdir, "defaults"),
            access_key="",
            max_images=50,
        )
        result = fetcher.get_image("unknown_category", "query")
        assert result is None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_image_fetcher.py -v`
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Write implementation**

```python
# src/image_fetcher.py
"""Fetch wallpaper images from Unsplash API with local cache and defaults fallback."""

import logging
import os
from pathlib import Path

import requests

logger = logging.getLogger(__name__)

UNSPLASH_SEARCH_URL = "https://api.unsplash.com/search/photos"


class ImageFetcher:
    def __init__(
        self, cache_dir: str, defaults_dir: str, access_key: str, max_images: int
    ) -> None:
        self._cache_dir = cache_dir
        self._defaults_dir = defaults_dir
        self._access_key = access_key
        self._max_images = max_images

    def get_image(self, category: str, query: str) -> str | None:
        # 1. Check cache
        cached = self._get_cached(category)
        if cached:
            return cached

        # 2. Try Unsplash
        if self._access_key:
            fetched = self._fetch_from_unsplash(category, query)
            if fetched:
                return fetched

        # 3. Fallback to defaults
        return self._get_default(category)

    def _get_cached(self, category: str) -> str | None:
        category_dir = os.path.join(self._cache_dir, category)
        if not os.path.isdir(category_dir):
            return None
        images = [
            f for f in os.listdir(category_dir)
            if f.lower().endswith((".jpg", ".jpeg", ".png"))
        ]
        if not images:
            return None
        return os.path.join(category_dir, images[0])

    def _fetch_from_unsplash(self, category: str, query: str) -> str | None:
        try:
            params = {
                "query": query,
                "orientation": "landscape",
                "per_page": 1,
            }
            headers = {"Authorization": f"Client-ID {self._access_key}"}
            resp = requests.get(
                UNSPLASH_SEARCH_URL, params=params, headers=headers, timeout=15
            )
            resp.raise_for_status()
            results = resp.json().get("results", [])
            if not results:
                return None

            image_url = results[0]["urls"]["raw"] + "&w=3840&h=2160&fit=crop"
            image_id = results[0]["id"]

            img_resp = requests.get(image_url, timeout=30)
            img_resp.raise_for_status()

            category_dir = os.path.join(self._cache_dir, category)
            os.makedirs(category_dir, exist_ok=True)
            self._enforce_cache_limit(category_dir)

            save_path = os.path.join(category_dir, f"{image_id}.jpg")
            with open(save_path, "wb") as f:
                f.write(img_resp.content)

            logger.info("Downloaded image from Unsplash: %s", save_path)
            return save_path

        except Exception:
            logger.exception("Failed to fetch from Unsplash")
            return None

    def _get_default(self, category: str) -> str | None:
        defaults_path = Path(self._defaults_dir)
        for ext in (".jpg", ".jpeg", ".png"):
            candidate = defaults_path / f"{category}{ext}"
            if candidate.exists():
                return str(candidate)
        return None

    def _enforce_cache_limit(self, category_dir: str) -> None:
        images = sorted(
            Path(category_dir).glob("*"),
            key=lambda p: p.stat().st_mtime,
        )
        while len(images) >= self._max_images:
            oldest = images.pop(0)
            oldest.unlink()
            logger.info("Removed old cached image: %s", oldest)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_image_fetcher.py -v`
Expected: All 4 tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/image_fetcher.py tests/test_image_fetcher.py
git commit -m "feat: add image fetcher with Unsplash API, cache, and defaults fallback"
```

---

### Task 7: Wallpaper Renderer

**Files:**
- Create: `src/wallpaper_renderer.py`
- Create: `tests/test_wallpaper_renderer.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_wallpaper_renderer.py
import os
import tempfile
from PIL import Image
from wallpaper_renderer import render_overlay
from weather_fetcher import WeatherData


def _create_test_image(path: str, width: int = 1920, height: int = 1080) -> None:
    img = Image.new("RGB", (width, height), color=(100, 150, 200))
    img.save(path)


def test_render_overlay_creates_output_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        base_path = os.path.join(tmpdir, "base.jpg")
        output_path = os.path.join(tmpdir, "output.jpg")
        _create_test_image(base_path)

        weather = WeatherData(
            temperature=22.5,
            weather_code=0,
            wind_speed=3.2,
            temp_max=28.0,
            temp_min=18.0,
            precipitation_probability=10,
        )

        result = render_overlay(
            base_image_path=base_path,
            output_path=output_path,
            weather=weather,
            icon="☀️",
            description="快晴",
            position="bottom_right",
            opacity=0.7,
            font_size=48,
        )
        assert result == output_path
        assert os.path.exists(output_path)

        # Verify output image has same dimensions
        with Image.open(output_path) as img:
            assert img.size == (1920, 1080)


def test_render_overlay_different_positions():
    with tempfile.TemporaryDirectory() as tmpdir:
        base_path = os.path.join(tmpdir, "base.jpg")
        _create_test_image(base_path)

        weather = WeatherData(
            temperature=5.0,
            weather_code=71,
            wind_speed=10.0,
            temp_max=8.0,
            temp_min=-2.0,
            precipitation_probability=80,
        )

        for position in ["bottom_right", "bottom_left", "top_right", "top_left"]:
            output_path = os.path.join(tmpdir, f"output_{position}.jpg")
            result = render_overlay(
                base_image_path=base_path,
                output_path=output_path,
                weather=weather,
                icon="❄️",
                description="雪",
                position=position,
                opacity=0.7,
                font_size=48,
            )
            assert os.path.exists(result)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_wallpaper_renderer.py -v`
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Write implementation**

```python
# src/wallpaper_renderer.py
"""Render weather info overlay onto wallpaper image using Pillow."""

import logging
import os
from PIL import Image, ImageDraw, ImageFont

from weather_fetcher import WeatherData

logger = logging.getLogger(__name__)

_FONT_DIR = os.path.join(os.path.dirname(__file__), "..", "fonts")
_FONT_PATH = os.path.join(_FONT_DIR, "NotoSansJP-Regular.ttf")

_PADDING = 20
_BOX_MARGIN = 40
_LINE_SPACING = 8


def _get_font(size: int) -> ImageFont.FreeTypeFont:
    if os.path.exists(_FONT_PATH):
        return ImageFont.truetype(_FONT_PATH, size)
    # Fallback: use default font
    try:
        return ImageFont.truetype("/System/Library/Fonts/HelveticaNeue.ttc", size)
    except OSError:
        return ImageFont.load_default()


def render_overlay(
    base_image_path: str,
    output_path: str,
    weather: WeatherData,
    icon: str,
    description: str,
    position: str = "bottom_right",
    opacity: float = 0.7,
    font_size: int = 48,
) -> str:
    img = Image.open(base_image_path).convert("RGBA")
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    font_large = _get_font(font_size)
    font_small = _get_font(font_size // 2)

    # Build text lines
    lines = [
        (f"{icon} {weather.temperature:.1f}°C", font_large),
        (description, font_small),
        (f"最高 {weather.temp_max:.0f}°C / 最低 {weather.temp_min:.0f}°C", font_small),
        (f"降水確率 {weather.precipitation_probability}%", font_small),
    ]

    # Calculate box size
    line_heights = []
    line_widths = []
    for text, font in lines:
        bbox = draw.textbbox((0, 0), text, font=font)
        line_widths.append(bbox[2] - bbox[0])
        line_heights.append(bbox[3] - bbox[1])

    box_width = max(line_widths) + _PADDING * 2
    box_height = sum(line_heights) + _LINE_SPACING * (len(lines) - 1) + _PADDING * 2

    # Calculate position
    img_w, img_h = img.size
    if "right" in position:
        box_x = img_w - box_width - _BOX_MARGIN
    else:
        box_x = _BOX_MARGIN

    if "bottom" in position:
        box_y = img_h - box_height - _BOX_MARGIN
    else:
        box_y = _BOX_MARGIN

    # Draw semi-transparent background
    alpha = int(255 * opacity)
    draw.rounded_rectangle(
        [box_x, box_y, box_x + box_width, box_y + box_height],
        radius=15,
        fill=(0, 0, 0, alpha),
    )

    # Draw text lines
    y_offset = box_y + _PADDING
    for text, font in lines:
        draw.text((box_x + _PADDING, y_offset), text, font=font, fill=(255, 255, 255, 255))
        bbox = draw.textbbox((0, 0), text, font=font)
        y_offset += (bbox[3] - bbox[1]) + _LINE_SPACING

    # Composite and save
    result = Image.alpha_composite(img, overlay).convert("RGB")
    result.save(output_path, "JPEG", quality=95)
    logger.info("Rendered overlay to: %s", output_path)
    return output_path
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_wallpaper_renderer.py -v`
Expected: All 2 tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/wallpaper_renderer.py tests/test_wallpaper_renderer.py
git commit -m "feat: add wallpaper renderer with Pillow overlay drawing"
```

---

### Task 8: Main Orchestrator

**Files:**
- Create: `src/main.py`
- Create: `tests/test_main.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_main.py
from unittest.mock import patch, MagicMock
from main import WeatherWallpaperApp
from weather_fetcher import WeatherData


def _make_config():
    return {
        "location": {"latitude": 35.6762, "longitude": 139.6503},
        "check_interval_min": 10,
        "overlay": {"position": "bottom_right", "opacity": 0.7, "font_size": 48},
        "unsplash": {"access_key": "test_key"},
        "yahoo": {"client_id": ""},
        "cache": {"max_images": 50},
    }


def _make_weather(code=0, temp=22.5):
    return WeatherData(
        temperature=temp,
        weather_code=code,
        wind_speed=3.2,
        temp_max=28.0,
        temp_min=18.0,
        precipitation_probability=10,
    )


@patch("main.set_wallpaper")
@patch("main.render_overlay")
@patch("main.ImageFetcher")
@patch("main.fetch_open_meteo")
@patch("main.load_config")
def test_first_run_fetches_and_sets_wallpaper(
    mock_config, mock_fetch, mock_image_cls, mock_render, mock_set
):
    mock_config.return_value = _make_config()
    mock_fetch.return_value = _make_weather(code=0, temp=22.5)
    mock_image_instance = MagicMock()
    mock_image_instance.get_image.return_value = "/tmp/base.jpg"
    mock_image_cls.return_value = mock_image_instance
    mock_render.return_value = "/tmp/output.jpg"
    mock_set.return_value = True

    app = WeatherWallpaperApp()
    app.tick()

    mock_fetch.assert_called_once()
    mock_image_instance.get_image.assert_called_once()
    mock_render.assert_called_once()
    mock_set.assert_called_once_with("/tmp/output.jpg")


@patch("main.set_wallpaper")
@patch("main.render_overlay")
@patch("main.ImageFetcher")
@patch("main.fetch_open_meteo")
@patch("main.load_config")
def test_no_weather_change_skips_image_fetch(
    mock_config, mock_fetch, mock_image_cls, mock_render, mock_set
):
    mock_config.return_value = _make_config()
    mock_fetch.return_value = _make_weather(code=0, temp=22.5)
    mock_image_instance = MagicMock()
    mock_image_instance.get_image.return_value = "/tmp/base.jpg"
    mock_image_cls.return_value = mock_image_instance
    mock_render.return_value = "/tmp/output.jpg"
    mock_set.return_value = True

    app = WeatherWallpaperApp()
    app.tick()  # First run
    app.tick()  # Same weather - should skip image fetch

    assert mock_image_instance.get_image.call_count == 1
    assert mock_render.call_count == 1


@patch("main.set_wallpaper")
@patch("main.render_overlay")
@patch("main.ImageFetcher")
@patch("main.fetch_open_meteo")
@patch("main.load_config")
def test_temperature_change_redraws_overlay_only(
    mock_config, mock_fetch, mock_image_cls, mock_render, mock_set
):
    mock_config.return_value = _make_config()
    mock_image_instance = MagicMock()
    mock_image_instance.get_image.return_value = "/tmp/base.jpg"
    mock_image_cls.return_value = mock_image_instance
    mock_render.return_value = "/tmp/output.jpg"
    mock_set.return_value = True

    # First call: code=0, temp=22.5
    mock_fetch.return_value = _make_weather(code=0, temp=22.5)
    app = WeatherWallpaperApp()
    app.tick()

    # Second call: same code, different temp
    mock_fetch.return_value = _make_weather(code=0, temp=25.0)
    app.tick()

    # Image fetched only once, but overlay rendered twice
    assert mock_image_instance.get_image.call_count == 1
    assert mock_render.call_count == 2
    assert mock_set.call_count == 2


@patch("main.set_wallpaper")
@patch("main.render_overlay")
@patch("main.ImageFetcher")
@patch("main.fetch_open_meteo")
@patch("main.load_config")
def test_weather_code_change_fetches_new_image(
    mock_config, mock_fetch, mock_image_cls, mock_render, mock_set
):
    mock_config.return_value = _make_config()
    mock_image_instance = MagicMock()
    mock_image_instance.get_image.return_value = "/tmp/base.jpg"
    mock_image_cls.return_value = mock_image_instance
    mock_render.return_value = "/tmp/output.jpg"
    mock_set.return_value = True

    # First: clear sky
    mock_fetch.return_value = _make_weather(code=0, temp=22.5)
    app = WeatherWallpaperApp()
    app.tick()

    # Second: rain
    mock_fetch.return_value = _make_weather(code=63, temp=18.0)
    app.tick()

    assert mock_image_instance.get_image.call_count == 2
    assert mock_render.call_count == 2
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_main.py -v`
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Write implementation**

```python
# src/main.py
"""Weather Wallpaper Changer - main orchestrator."""

import logging
import os
import signal
import sys

import schedule
import time

from config import load_config
from weather_fetcher import fetch_open_meteo, fetch_yolp_rainfall, WeatherData
from weather_mapper import WeatherMapper
from image_fetcher import ImageFetcher
from wallpaper_renderer import render_overlay
from wallpaper_setter import set_wallpaper

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class WeatherWallpaperApp:
    def __init__(self, config_path: str = None) -> None:
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
        self._prev_weather_code: int | None = None
        self._prev_temperature: float | None = None
        self._current_base_image: str | None = None
        self._output_index = 0  # Alternate between 2 output files

    def tick(self) -> None:
        lat = self._config["location"]["latitude"]
        lon = self._config["location"]["longitude"]

        weather = fetch_open_meteo(lat, lon)
        if weather is None:
            logger.warning("Failed to fetch weather, skipping update")
            return

        code_changed = weather.weather_code != self._prev_weather_code
        temp_changed = weather.temperature != self._prev_temperature

        if not code_changed and not temp_changed:
            logger.info("No weather change, skipping")
            return

        mapping = self._mapper.get_mapping(weather.weather_code)

        # Fetch new base image if weather code changed
        if code_changed or self._current_base_image is None:
            image_path = self._image_fetcher.get_image(
                mapping.get("category", "unknown"), mapping["query"]
            )
            if image_path is None:
                logger.error("No image available, skipping wallpaper update")
                return
            self._current_base_image = image_path
            logger.info("New base image: %s", image_path)

        # Render overlay (alternating output files to avoid macOS cache issues)
        self._output_index = 1 - self._output_index
        output_path = os.path.join(
            BASE_DIR, f"output_wallpaper_{self._output_index}.jpg"
        )

        render_overlay(
            base_image_path=self._current_base_image,
            output_path=output_path,
            weather=weather,
            icon=mapping["icon"],
            description=mapping["description"],
            position=self._config["overlay"]["position"],
            opacity=self._config["overlay"]["opacity"],
            font_size=self._config["overlay"]["font_size"],
        )

        set_wallpaper(os.path.abspath(output_path))

        self._prev_weather_code = weather.weather_code
        self._prev_temperature = weather.temperature
        logger.info(
            "Wallpaper updated: %s %.1f°C (%s)",
            mapping["icon"],
            weather.temperature,
            mapping["description"],
        )

    def run(self) -> None:
        logger.info("Weather Wallpaper Changer started")
        self.tick()  # Run immediately on start

        interval = self._config["check_interval_min"]
        schedule.every(interval).minutes.do(self.tick)

        def handle_sigterm(*_):
            logger.info("Shutting down...")
            sys.exit(0)

        signal.signal(signal.SIGTERM, handle_sigterm)
        signal.signal(signal.SIGINT, handle_sigterm)

        while True:
            schedule.run_pending()
            time.sleep(1)


if __name__ == "__main__":
    app = WeatherWallpaperApp()
    app.run()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_main.py -v`
Expected: All 4 tests PASS

- [ ] **Step 5: Run all tests together**

Run: `pytest tests/ -v`
Expected: All tests PASS (total: ~20 tests)

- [ ] **Step 6: Commit**

```bash
git add src/main.py tests/test_main.py
git commit -m "feat: add main orchestrator with change detection and scheduling"
```

---

## Self-Review

**Spec coverage check:**
- [x] Open-Meteo API (Task 5)
- [x] YOLP API (Task 5 - fetch_yolp_rainfall implemented but not yet used in main - see note)
- [x] Weather code mapping (Task 2)
- [x] Unsplash image fetch + cache (Task 6)
- [x] Default images fallback (Task 6)
- [x] Pillow overlay rendering (Task 7)
- [x] AppleScript wallpaper setting + Finder fallback (Task 4)
- [x] Config loading (Task 3)
- [x] Change detection (Task 8)
- [x] Memory-based state (Task 8 - _prev_weather_code, _prev_temperature)
- [x] 10-min polling (Task 8)
- [x] Output file rotation for macOS cache issue (Task 8)

**Note:** Yahoo YOLP rainfall data (`fetch_yolp_rainfall`) is implemented in Task 5 but not integrated into the main orchestrator's `tick()`. The spec says it's "補完用" (supplementary). To keep Task 8 focused, YOLP integration can be added as a follow-up once the core loop is working. The function is available and tested.

**Note:** Yahoo天気スクレイピング is listed in the spec as "フォールバック用" but is deferred from this implementation plan. It carries site-structure-change risk and Open-Meteo is sufficient for v1.

**Placeholder scan:** No TBD/TODO found. All code blocks are complete.

**Type consistency:** WeatherData, WeatherMapper, ImageFetcher, render_overlay, set_wallpaper - all signatures consistent across tasks.
