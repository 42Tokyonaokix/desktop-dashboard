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
