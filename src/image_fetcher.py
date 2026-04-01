"""Fetch wallpaper images from Unsplash API with local cache and defaults fallback."""

import logging
import os
from pathlib import Path
from typing import Optional

import requests

logger = logging.getLogger(__name__)

UNSPLASH_SEARCH_URL = "https://api.unsplash.com/search/photos"


class ImageFetcher:
    def __init__(
        self, cache_dir: str, defaults_dir: str, access_key: str, max_images: int
    ) -> None:
        self._cache_dir = cache_dir
        self._defaults_dir = defaults_dir
        self._access_key = access_key
        self._max_images = max_images

    def get_image(self, category: str, query: str) -> Optional[str]:
        cached = self._get_cached(category)
        if cached:
            return cached
        if self._access_key:
            fetched = self._fetch_from_unsplash(category, query)
            if fetched:
                return fetched
        return self._get_default(category)

    def _get_cached(self, category: str) -> Optional[str]:
        category_dir = os.path.join(self._cache_dir, category)
        if not os.path.isdir(category_dir):
            return None
        images = [
            f for f in os.listdir(category_dir)
            if f.lower().endswith((".jpg", ".jpeg", ".png"))
        ]
        if not images:
            return None
        return os.path.join(category_dir, images[0])

    def _fetch_from_unsplash(self, category: str, query: str) -> Optional[str]:
        try:
            params = {
                "query": query,
                "orientation": "landscape",
                "per_page": 1,
            }
            headers = {"Authorization": f"Client-ID {self._access_key}"}
            resp = requests.get(
                UNSPLASH_SEARCH_URL, params=params, headers=headers, timeout=15
            )
            resp.raise_for_status()
            results = resp.json().get("results", [])
            if not results:
                return None
            image_url = results[0]["urls"]["raw"] + "&w=3840&h=2160&fit=crop"
            image_id = results[0]["id"]
            img_resp = requests.get(image_url, timeout=30)
            img_resp.raise_for_status()
            category_dir = os.path.join(self._cache_dir, category)
            os.makedirs(category_dir, exist_ok=True)
            self._enforce_cache_limit(category_dir)
            save_path = os.path.join(category_dir, f"{image_id}.jpg")
            with open(save_path, "wb") as f:
                f.write(img_resp.content)
            logger.info("Downloaded image from Unsplash: %s", save_path)
            return save_path
        except Exception:
            logger.exception("Failed to fetch from Unsplash")
            return None

    def _get_default(self, category: str) -> Optional[str]:
        defaults_path = Path(self._defaults_dir)
        for ext in (".jpg", ".jpeg", ".png"):
            candidate = defaults_path / f"{category}{ext}"
            if candidate.exists():
                return str(candidate)
        return None

    def _enforce_cache_limit(self, category_dir: str) -> None:
        images = sorted(
            Path(category_dir).glob("*"),
            key=lambda p: p.stat().st_mtime,
        )
        while len(images) >= self._max_images:
            oldest = images.pop(0)
            oldest.unlink()
            logger.info("Removed old cached image: %s", oldest)
