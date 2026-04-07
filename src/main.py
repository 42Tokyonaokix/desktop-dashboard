"""Desktop Dashboard — main orchestrator."""

import logging
import os
import signal
import sys
from typing import Optional

import yaml

from config import load_config
from domain.weather_fetcher import fetch_open_meteo
from domain.models import WeatherData, DashboardData
from domain.weather_mapper import WeatherMapper
from domain.task_reader import read_tasks
from domain.motivation_reader import read_motivation
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
        """Run without UI — for headless mode."""
        import time
        import schedule

        logger.info("Desktop Dashboard started (headless)")
        self.tick_all()

        def handle_sigterm(*_):
            logger.info("Shutting down...")
            sys.exit(0)

        signal.signal(signal.SIGTERM, handle_sigterm)
        signal.signal(signal.SIGINT, handle_sigterm)

        weather_interval = self._config.get("weather", {}).get("check_interval_min", 10)
        obsidian_interval = self._config["obsidian"].get("check_interval_min", 5)

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
