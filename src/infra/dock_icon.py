"""macOS Dock icon generation with weather info and task badge."""

import io
import logging
from PIL import Image, ImageDraw

from domain.models import WeatherData

logger = logging.getLogger(__name__)

ICON_SIZE = 128

_ICON_TEXT = {
    "clear": "晴", "partly_cloudy": "曇", "fog": "霧", "drizzle": "小雨",
    "rain": "雨", "snow": "雪", "shower": "雨", "thunderstorm": "雷", "unknown": "？",
}

_ICON_BG = {
    "clear": (30, 100, 180, 220), "partly_cloudy": (80, 90, 110, 220),
    "fog": (100, 100, 110, 220), "drizzle": (60, 70, 100, 220),
    "rain": (40, 50, 80, 220), "snow": (120, 130, 150, 220),
    "shower": (50, 55, 85, 220), "thunderstorm": (30, 30, 50, 220),
    "unknown": (60, 60, 60, 220),
}


def _get_font(size: int):
    """Get font — import from infra.wallpaper_renderer to share logic."""
    import os
    from PIL import ImageFont
    font_dir = os.path.join(os.path.dirname(__file__), "..", "..", "fonts")
    font_path = os.path.join(font_dir, "NotoSansJP-Regular.ttf")
    fallbacks = [
        "/System/Library/Fonts/ヒラギノ丸ゴ ProN W4.ttc",
        "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",
        "/Library/Fonts/Arial Unicode.ttf",
        "/System/Library/Fonts/HelveticaNeue.ttc",
    ]
    if os.path.exists(font_path):
        return ImageFont.truetype(font_path, size)
    for fb in fallbacks:
        try:
            return ImageFont.truetype(fb, size)
        except OSError:
            continue
    return ImageFont.load_default()


def generate_dock_icon(
    weather: WeatherData, mapping: dict, task_count: int = 0
) -> Image.Image:
    """Generate a 128x128 dock icon with weather info and optional task badge."""
    img = Image.new("RGBA", (ICON_SIZE, ICON_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    category = mapping.get("category", "unknown")
    bg_color = _ICON_BG.get(category, _ICON_BG["unknown"])

    draw.rounded_rectangle(
        [0, 0, ICON_SIZE - 1, ICON_SIZE - 1], radius=24, fill=bg_color,
    )

    # Weather text label (top)
    weather_text = _ICON_TEXT.get(category, "？")
    font_label = _get_font(30)
    bbox = draw.textbbox((0, 0), weather_text, font=font_label)
    label_w = bbox[2] - bbox[0]
    draw.text(((ICON_SIZE - label_w) / 2, 10), weather_text, font=font_label, fill="white")

    # Temperature (middle)
    font_temp = _get_font(28)
    temp_text = f"{weather.temperature:.0f}°C"
    bbox = draw.textbbox((0, 0), temp_text, font=font_temp)
    temp_w = bbox[2] - bbox[0]
    draw.text(((ICON_SIZE - temp_w) / 2, 48), temp_text, font=font_temp, fill="white")

    # Precipitation (bottom)
    font_small = _get_font(18)
    precip_text = f"降水{weather.precipitation_probability}%"
    bbox = draw.textbbox((0, 0), precip_text, font=font_small)
    precip_w = bbox[2] - bbox[0]
    draw.text(
        ((ICON_SIZE - precip_w) / 2, 88), precip_text,
        font=font_small, fill=(200, 220, 255, 255),
    )

    # Task count badge (top-right corner)
    if task_count > 0:
        badge_r = 16
        badge_cx = ICON_SIZE - badge_r - 4
        badge_cy = badge_r + 4
        draw.ellipse(
            [badge_cx - badge_r, badge_cy - badge_r,
             badge_cx + badge_r, badge_cy + badge_r],
            fill=(220, 50, 50, 255),
        )
        badge_font = _get_font(14)
        badge_text = str(min(task_count, 99))
        bbox = draw.textbbox((0, 0), badge_text, font=badge_font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        draw.text(
            (badge_cx - tw / 2, badge_cy - th / 2 - 2),
            badge_text, font=badge_font, fill="white",
        )

    return img


def pil_to_nsimage(pil_image: Image.Image):
    """Convert PIL Image to NSImage via TIFF bytes."""
    import AppKit
    buf = io.BytesIO()
    pil_image.save(buf, format="TIFF")
    ns_data = AppKit.NSData.dataWithBytes_length_(buf.getvalue(), len(buf.getvalue()))
    return AppKit.NSImage.alloc().initWithData_(ns_data)


def set_dock_icon(pil_image: Image.Image) -> None:
    """Set the macOS Dock icon to the given PIL image."""
    import AppKit
    ns_image = pil_to_nsimage(pil_image)
    AppKit.NSApp.setApplicationIconImage_(ns_image)
