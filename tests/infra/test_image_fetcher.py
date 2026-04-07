import os
import tempfile
from unittest.mock import patch, MagicMock
from infra.image_fetcher import ImageFetcher


def test_get_cached_image_when_exists():
    with tempfile.TemporaryDirectory() as cache_dir:
        os.makedirs(os.path.join(cache_dir, "clear"), exist_ok=True)
        cached_path = os.path.join(cache_dir, "clear", "img1.jpg")
        with open(cached_path, "wb") as f:
            f.write(b"fake image data")

        fetcher = ImageFetcher(
            cache_dir=cache_dir, defaults_dir="/nonexistent", access_key="key", max_images=50
        )
        result = fetcher.get_image("clear", "clear blue sky")
        assert result == cached_path


@patch("infra.image_fetcher.requests.get")
def test_fetch_from_unsplash_when_no_cache(mock_get):
    with tempfile.TemporaryDirectory() as cache_dir:
        search_resp = MagicMock()
        search_resp.status_code = 200
        search_resp.json.return_value = {
            "results": [
                {"urls": {"raw": "https://example.com/photo.jpg"}, "id": "abc123"}
            ]
        }
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
