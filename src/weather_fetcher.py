"""Fetch weather data from WMO API."""

from dataclasses import dataclass


@dataclass
class WeatherData:
    """Weather data container."""

    temperature: float
    weather_code: int
    wind_speed: float
    temp_max: float
    temp_min: float
    precipitation_probability: int
