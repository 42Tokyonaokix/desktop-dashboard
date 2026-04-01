"""Weather Wallpaper Changer - main orchestrator."""

import logging
import os
import signal
import sys
from typing import Optional

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

        rendered_path = render_overlay(
            base_image_path=self._current_base_image,
            output_path=output_path,
            weather=weather,
            icon=mapping["icon"],
            description=mapping["description"],
            position=self._config["overlay"]["position"],
            opacity=self._config["overlay"]["opacity"],
            font_size=self._config["overlay"]["font_size"],
        )

        set_wallpaper(rendered_path)

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
