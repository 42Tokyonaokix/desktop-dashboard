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
class ProjectGoal:
    project: str
    goals: list[str] = field(default_factory=list)


@dataclass
class ScheduleItem:
    time: str
    description: str


@dataclass
class GoalData:
    title: str
    theme: str
    project_goals: list[ProjectGoal] = field(default_factory=list)
    tasks: list[str] = field(default_factory=list)
    today_schedule: list[ScheduleItem] = field(default_factory=list)


@dataclass
class DashboardData:
    weather: WeatherData
    weather_mapping: dict
    motivation: Optional[MotivationData] = None
    monthly_goal: Optional[GoalData] = None
