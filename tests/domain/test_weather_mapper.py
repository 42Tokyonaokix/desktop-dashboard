from domain.weather_mapper import WeatherMapper


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
