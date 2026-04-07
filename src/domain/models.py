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
