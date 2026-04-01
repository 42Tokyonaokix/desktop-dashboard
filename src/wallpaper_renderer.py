"""Render weather info overlay onto wallpaper image using Pillow."""

import logging
import os
from PIL import Image, ImageDraw, ImageFont

from weather_fetcher import WeatherData

logger = logging.getLogger(__name__)

_FONT_DIR = os.path.join(os.path.dirname(__file__), "..", "fonts")
_FONT_PATH = os.path.join(_FONT_DIR, "NotoSansJP-Regular.ttf")

_PADDING = 20
_BOX_MARGIN = 40
_LINE_SPACING = 8


_FALLBACK_FONTS = [
    "/System/Library/Fonts/\u30d2\u30e9\u30ae\u30ce\u89d2\u30b4\u30b7\u30c3\u30af W3.ttc",
    "/Library/Fonts/Arial Unicode.ttf",
    "/System/Library/Fonts/HelveticaNeue.ttc",
]


def _get_font(size: int) -> ImageFont.FreeTypeFont:
    if os.path.exists(_FONT_PATH):
        return ImageFont.truetype(_FONT_PATH, size)
    for fallback in _FALLBACK_FONTS:
        try:
            return ImageFont.truetype(fallback, size)
        except OSError:
            continue
    return ImageFont.load_default()


def render_overlay(
    base_image_path: str,
    output_path: str,
    weather: WeatherData,
    icon: str,
    description: str,
    position: str = "bottom_right",
    opacity: float = 0.7,
    font_size: int = 48,
) -> str:
    img = Image.open(base_image_path).convert("RGBA")
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    font_large = _get_font(font_size)
    font_small = _get_font(font_size // 2)

    lines = [
        (f"{icon} {weather.temperature:.1f}°C", font_large),
        (description, font_small),
        (f"最高 {weather.temp_max:.0f}°C / 最低 {weather.temp_min:.0f}°C", font_small),
        (f"降水確率 {weather.precipitation_probability}%", font_small),
    ]

    line_heights = []
    line_widths = []
    for text, font in lines:
        bbox = draw.textbbox((0, 0), text, font=font)
        line_widths.append(bbox[2] - bbox[0])
        line_heights.append(bbox[3] - bbox[1])

    box_width = max(line_widths) + _PADDING * 2
    box_height = sum(line_heights) + _LINE_SPACING * (len(lines) - 1) + _PADDING * 2

    img_w, img_h = img.size
    if "right" in position:
        box_x = img_w - box_width - _BOX_MARGIN
    else:
        box_x = _BOX_MARGIN

    if "bottom" in position:
        box_y = img_h - box_height - _BOX_MARGIN
    else:
        box_y = _BOX_MARGIN

    alpha = int(255 * opacity)
    draw.rounded_rectangle(
        [box_x, box_y, box_x + box_width, box_y + box_height],
        radius=15,
        fill=(0, 0, 0, alpha),
    )

    y_offset = box_y + _PADDING
    for text, font in lines:
        draw.text((box_x + _PADDING, y_offset), text, font=font, fill=(255, 255, 255, 255))
        bbox = draw.textbbox((0, 0), text, font=font)
        y_offset += (bbox[3] - bbox[1]) + _LINE_SPACING

    result = Image.alpha_composite(img, overlay).convert("RGB")
    result.save(output_path, "JPEG", quality=95)
    logger.info("Rendered overlay to: %s", output_path)
    return output_path
