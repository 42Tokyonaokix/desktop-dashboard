"""Render 3-section dashboard overlay onto wallpaper image using Pillow."""

import logging
import os
from PIL import Image, ImageDraw, ImageFont

from domain.models import DashboardData, TaskItem, MotivationData

logger = logging.getLogger(__name__)

_FONT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "fonts")
_FONT_PATH = os.path.join(_FONT_DIR, "NotoSansJP-Regular.ttf")

_FALLBACK_FONTS = [
    "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",
    "/Library/Fonts/Arial Unicode.ttf",
    "/System/Library/Fonts/HelveticaNeue.ttc",
]

_CARD_RADIUS = 20
_CARD_PADDING = 24
_CARD_GAP = 16
_LINE_SPACING = 6


def _get_font(size: int) -> ImageFont.FreeTypeFont:
    if os.path.exists(_FONT_PATH):
        return ImageFont.truetype(_FONT_PATH, size)
    for fallback in _FALLBACK_FONTS:
        try:
            return ImageFont.truetype(fallback, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _draw_card(
    draw: ImageDraw.ImageDraw,
    x: int, y: int, w: int, h: int,
    opacity: float,
) -> None:
    """Draw a semi-transparent rounded rectangle card."""
    alpha = int(255 * opacity)
    draw.rounded_rectangle(
        [x, y, x + w, y + h],
        radius=_CARD_RADIUS,
        fill=(0, 0, 0, alpha),
    )


def _render_weather_section(
    draw: ImageDraw.ImageDraw,
    x: int, y: int, w: int, h: int,
    data: DashboardData, font_size: int, opacity: float,
) -> None:
    """Render weather info card."""
    _draw_card(draw, x, y, w, h, opacity)

    weather = data.weather
    mapping = data.weather_mapping
    icon = mapping.get("icon", "🌤️")
    desc = mapping.get("description", "")

    font_large = _get_font(font_size)
    font_small = _get_font(max(font_size // 2, 14))

    cx = x + _CARD_PADDING
    cy = y + _CARD_PADDING
    white = (255, 255, 255, 255)

    # Line 1: icon + temperature
    text = f"{icon} {weather.temperature:.1f}°C"
    draw.text((cx, cy), text, font=font_large, fill=white)
    bbox = draw.textbbox((0, 0), text, font=font_large)
    cy += (bbox[3] - bbox[1]) + _LINE_SPACING

    # Line 2: description
    draw.text((cx, cy), desc, font=font_small, fill=white)
    bbox = draw.textbbox((0, 0), desc, font=font_small)
    cy += (bbox[3] - bbox[1]) + _LINE_SPACING

    # Line 3: high/low
    text = f"最高 {weather.temp_max:.0f}°C / 最低 {weather.temp_min:.0f}°C"
    draw.text((cx, cy), text, font=font_small, fill=white)
    bbox = draw.textbbox((0, 0), text, font=font_small)
    cy += (bbox[3] - bbox[1]) + _LINE_SPACING

    # Line 4: precipitation
    text = f"降水確率 {weather.precipitation_probability}%"
    draw.text((cx, cy), text, font=font_small, fill=white)


def _render_tasks_section(
    draw: ImageDraw.ImageDraw,
    x: int, y: int, w: int, h: int,
    data: DashboardData, font_size: int, opacity: float,
) -> None:
    """Render task list card."""
    _draw_card(draw, x, y, w, h, opacity)

    font_title = _get_font(max(font_size // 2 + 4, 16))
    font_item = _get_font(max(font_size // 2 - 2, 12))
    font_tag = _get_font(max(font_size // 3, 10))

    cx = x + _CARD_PADDING
    cy = y + _CARD_PADDING
    white = (255, 255, 255, 255)
    dim = (180, 180, 180, 255)
    tag_color = (140, 200, 255, 255)

    # Section header
    draw.text((cx, cy), "📋 Tasks", font=font_title, fill=white)
    bbox = draw.textbbox((0, 0), "📋 Tasks", font=font_title)
    cy += (bbox[3] - bbox[1]) + _LINE_SPACING * 2

    if not data.tasks:
        draw.text((cx, cy), "No tasks", font=font_item, fill=dim)
        return

    max_y = y + h - _CARD_PADDING
    for task in data.tasks:
        if cy + 30 > max_y:
            break

        # Priority indicator
        pri_mark = "●" if task.priority.lower() == "high" else "○"
        line = f"{pri_mark} {task.title}"
        draw.text((cx, cy), line, font=font_item, fill=white)
        bbox = draw.textbbox((0, 0), line, font=font_item)
        cy += (bbox[3] - bbox[1]) + 2

        # Tags on same or next line
        if task.tags:
            tag_str = "  ".join(f"#{t}" for t in task.tags)
            draw.text((cx + 16, cy), tag_str, font=font_tag, fill=tag_color)
            bbox = draw.textbbox((0, 0), tag_str, font=font_tag)
            cy += (bbox[3] - bbox[1]) + _LINE_SPACING
        else:
            cy += _LINE_SPACING


def _render_motivation_section(
    draw: ImageDraw.ImageDraw,
    x: int, y: int, w: int, h: int,
    data: DashboardData, font_size: int, opacity: float,
) -> None:
    """Render motivation comment card."""
    _draw_card(draw, x, y, w, h, opacity)

    font_title = _get_font(max(font_size // 2 + 4, 16))
    font_body = _get_font(max(font_size // 2 - 2, 12))

    cx = x + _CARD_PADDING
    cy = y + _CARD_PADDING
    white = (255, 255, 255, 255)
    dim = (180, 180, 180, 255)

    # Section header
    draw.text((cx, cy), "💬 Today", font=font_title, fill=white)
    bbox = draw.textbbox((0, 0), "💬 Today", font=font_title)
    cy += (bbox[3] - bbox[1]) + _LINE_SPACING * 2

    if data.motivation is None or not data.motivation.comment:
        draw.text((cx, cy), "No message yet", font=font_body, fill=dim)
        return

    # Word-wrap the motivation text within the card width
    max_text_width = w - _CARD_PADDING * 2
    max_y = y + h - _CARD_PADDING

    for line in data.motivation.comment.split("\n"):
        if cy + 20 > max_y:
            break
        # Simple character-level wrapping for CJK text
        wrapped = _wrap_text(draw, line, font_body, max_text_width)
        for wline in wrapped:
            if cy + 20 > max_y:
                break
            draw.text((cx, cy), wline, font=font_body, fill=white)
            bbox = draw.textbbox((0, 0), wline, font=font_body)
            cy += (bbox[3] - bbox[1]) + _LINE_SPACING


def _wrap_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.FreeTypeFont,
    max_width: int,
) -> list[str]:
    """Wrap text to fit within max_width pixels."""
    if not text:
        return [""]

    lines = []
    current = ""
    for char in text:
        test = current + char
        bbox = draw.textbbox((0, 0), test, font=font)
        if (bbox[2] - bbox[0]) > max_width and current:
            lines.append(current)
            current = char
        else:
            current = test
    if current:
        lines.append(current)
    return lines


_SECTION_RENDERERS = {
    "weather": _render_weather_section,
    "tasks": _render_tasks_section,
    "motivation": _render_motivation_section,
}


def render_dashboard(
    base_image_path: str,
    output_path: str,
    data: DashboardData,
    config: dict,
) -> str:
    """Render the 3-section dashboard overlay onto a wallpaper image.

    Args:
        base_image_path: Path to the background wallpaper image.
        output_path: Where to save the rendered result.
        data: DashboardData containing weather, tasks, motivation.
        config: Dashboard config dict with keys: width, height, sections,
                section_weights, card_opacity, font_size.
    Returns:
        The output_path.
    """
    img = Image.open(base_image_path).convert("RGBA")
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    img_w, img_h = img.size
    dash_w = config.get("width", 1500)
    dash_h = config.get("height", 1000)
    sections = config.get("sections", ["weather", "tasks", "motivation"])
    weights = config.get("section_weights", [30, 40, 30])
    opacity = config.get("card_opacity", 0.6)
    font_size = config.get("font_size", 36)

    # Center the dashboard area
    dash_x = (img_w - dash_w) // 2
    dash_y = (img_h - dash_h) // 2

    # Calculate section heights from weights
    active_sections = [s for s in sections if s in _SECTION_RENDERERS]
    if not active_sections:
        # No sections to render, just save the image as-is
        img.convert("RGB").save(output_path, "JPEG", quality=95)
        return output_path

    # Normalize weights to match active sections
    active_weights = weights[:len(active_sections)]
    total_weight = sum(active_weights)
    available_height = dash_h - _CARD_GAP * (len(active_sections) - 1)
    section_heights = [
        int(available_height * w / total_weight) for w in active_weights
    ]

    # Render each section
    current_y = dash_y
    for i, section_name in enumerate(active_sections):
        renderer = _SECTION_RENDERERS[section_name]
        section_h = section_heights[i]
        renderer(draw, dash_x, current_y, dash_w, section_h, data, font_size, opacity)
        current_y += section_h + _CARD_GAP

    result = Image.alpha_composite(img, overlay).convert("RGB")
    result.save(output_path, "JPEG", quality=95)
    logger.info("Rendered dashboard to: %s", output_path)
    return output_path
