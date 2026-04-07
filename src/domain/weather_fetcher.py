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
