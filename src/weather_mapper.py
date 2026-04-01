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
