"""Render 3-section dashboard overlay onto wallpaper image using Pillow."""

import logging
import os
from PIL import Image, ImageDraw, ImageFont

from domain.models import DashboardData, TaskItem, MotivationData, GoalData

logger = logging.getLogger(__name__)

_FONT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "fonts")
_FONT_PATH = os.path.join(_FONT_DIR, "NotoSansJP-Regular.ttf")

_FALLBACK_FONTS = [
    "/System/Library/Fonts/ヒラギノ丸ゴ ProN W4.ttc",
    "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",
    "/Library/Fonts/Arial Unicode.ttf",
    "/System/Library/Fonts/HelveticaNeue.ttc",
]

_EMOJI_FONT_PATH = "/System/Library/Fonts/Apple Color Emoji.ttc"

_CARD_RADIUS = 20
_CARD_PADDING = 24
_CARD_GAP = 16
_LINE_SPACING = 4
_GROUP_SPACING = 16


def _get_font(size: int) -> ImageFont.FreeTypeFont:
    if os.path.exists(_FONT_PATH):
        return ImageFont.truetype(_FONT_PATH, size)
    for fallback in _FALLBACK_FONTS:
        try:
            return ImageFont.truetype(fallback, size)
        except OSError:
            continue
    return ImageFont.load_default()


_EMOJI_VALID_SIZES = [20, 40, 64, 96, 160]


def _get_emoji_font(size: int) -> ImageFont.FreeTypeFont:
    # Apple Color Emoji only supports specific sizes, snap to nearest valid
    best = min(_EMOJI_VALID_SIZES, key=lambda s: abs(s - size))
    try:
        return ImageFont.truetype(_EMOJI_FONT_PATH, best)
    except OSError:
        return _get_font(size)


def _is_emoji(char: str) -> bool:
    cp = ord(char)
    return (
        0x1F600 <= cp <= 0x1F64F or  # Emoticons
        0x1F300 <= cp <= 0x1F5FF or  # Misc Symbols
        0x1F680 <= cp <= 0x1F6FF or  # Transport
        0x1F900 <= cp <= 0x1F9FF or  # Supplemental
        0x2600 <= cp <= 0x26FF or    # Misc symbols (☀, ⛅ etc)
        0x2700 <= cp <= 0x27BF or    # Dingbats
        0xFE00 <= cp <= 0xFE0F or    # Variation selectors
        0x200D == cp or              # ZWJ
        0x20E3 == cp or              # Combining enclosing keycap
        0x1FA00 <= cp <= 0x1FA6F or  # Chess symbols
        0x1FA70 <= cp <= 0x1FAFF     # Symbols extended
    )


def _strip_variation_selectors(text: str) -> str:
    """Remove variation selectors and other invisible unicode that cause rendering issues."""
    return "".join(
        c for c in text
        if not (0xFE00 <= ord(c) <= 0xFE0F)  # Variation selectors
        and not (0x200B <= ord(c) <= 0x200F)  # Zero-width chars
        and ord(c) != 0x20E3                  # Combining enclosing keycap
    )


def _draw_text_with_emoji(
    draw: ImageDraw.ImageDraw,
    pos: tuple,
    text: str,
    font: ImageFont.FreeTypeFont,
    fill,
    font_size: int,
) -> tuple:
    """Draw text with emoji support. Returns (width, height) of rendered text."""
    x, y = pos
    emoji_font = _get_emoji_font(font_size)
    total_w = 0
    max_h = 0

    # Split text into emoji and non-emoji segments
    segments = []
    current = ""
    current_is_emoji = False
    for char in text:
        is_em = _is_emoji(char)
        if is_em != current_is_emoji and current:
            segments.append((current, current_is_emoji))
            current = ""
        current += char
        current_is_emoji = is_em
    if current:
        segments.append((current, current_is_emoji))

    for segment_text, is_em in segments:
        if is_em:
            clean = _strip_variation_selectors(segment_text)
            if not clean:
                continue
            draw.text((x + total_w, y), clean, font=emoji_font,
                      fill=fill, embedded_color=True)
            bbox = draw.textbbox((0, 0), clean, font=emoji_font)
        else:
            clean = _strip_variation_selectors(segment_text)
            draw.text((x + total_w, y), clean, font=font, fill=fill)
            bbox = draw.textbbox((0, 0), clean, font=font)
        seg_w = bbox[2] - bbox[0]
        seg_h = bbox[3] - bbox[1]
        total_w += seg_w
        max_h = max(max_h, seg_h)

    return (total_w, max_h)


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
    font_small = _get_font(max(font_size // 2, 28))

    cx = x + _CARD_PADDING
    cy = y + _CARD_PADDING
    white = (255, 255, 255, 255)
    dim = (200, 200, 200, 255)

    # Line 1: icon + temperature (large)
    font_temp = _get_font(font_size)
    font_detail = _get_font(max(font_size // 2, 32))
    dim = (200, 200, 200, 255)

    temp_text = f"{icon} {weather.temperature:.1f}°C"
    _, th = _draw_text_with_emoji(draw, (cx, cy), temp_text, font_temp, white, font_size)
    cy += th + _LINE_SPACING

    # Line 2: details (smaller, with separators)
    detail_text = f"{desc}  |  最高{weather.temp_max:.0f}°C / 最低{weather.temp_min:.0f}°C  |  降水{weather.precipitation_probability}%"
    draw.text((cx, cy), detail_text, font=font_detail, fill=dim)


def _render_weekly_tasks_section(
    draw: ImageDraw.ImageDraw,
    x: int, y: int, w: int, h: int,
    data: DashboardData, font_size: int, opacity: float,
) -> None:
    """Render weekly tasks card."""
    _draw_card(draw, x, y, w, h, opacity)

    font_title = _get_font(max(font_size * 3 // 4, 48))
    font_item = _get_font(max(font_size // 3, 24))

    cx = x + _CARD_PADDING
    cy = y + _CARD_PADDING
    white = (255, 255, 255, 255)
    dim = (180, 180, 180, 255)
    max_y = y + h - _CARD_PADDING

    _, header_h = _draw_text_with_emoji(draw, (cx, cy), "📋 Weekly Tasks", font_title, white, max(font_size * 3 // 4, 48))
    cy += header_h + _GROUP_SPACING

    goal = data.monthly_goal
    if goal is None or not goal.tasks:
        draw.text((cx, cy), "No tasks", font=font_item, fill=dim)
        return

    max_text_width = w - _CARD_PADDING * 2
    for task in goal.tasks:
        if cy + 30 > max_y:
            break
        line = f"・{_strip_markdown(task)}"
        wrapped = _wrap_text(draw, line, font_item, max_text_width)
        for wline in wrapped:
            if cy + 20 > max_y:
                break
            draw.text((cx, cy), wline, font=font_item, fill=white)
            bbox = draw.textbbox((0, 0), wline, font=font_item)
            cy += (bbox[3] - bbox[1]) + _LINE_SPACING


def _render_today_plan_section(
    draw: ImageDraw.ImageDraw,
    x: int, y: int, w: int, h: int,
    data: DashboardData, font_size: int, opacity: float,
) -> None:
    """Render today's schedule card."""
    _draw_card(draw, x, y, w, h, opacity)

    font_title = _get_font(max(font_size * 3 // 4, 48))
    font_item = _get_font(max(font_size // 3, 24))
    font_time = _get_font(max(font_size // 3, 24))

    cx = x + _CARD_PADDING
    cy = y + _CARD_PADDING
    white = (255, 255, 255, 255)
    dim = (180, 180, 180, 255)
    time_color = (140, 200, 255, 255)
    max_y = y + h - _CARD_PADDING

    _, header_h = _draw_text_with_emoji(draw, (cx, cy), "📅 Today's Schedule", font_title, white, max(font_size * 3 // 4, 48))
    cy += header_h + _GROUP_SPACING

    goal = data.monthly_goal
    if goal is None or not goal.today_schedule:
        draw.text((cx, cy), "No schedule today", font=font_item, fill=dim)
        return

    for item in goal.today_schedule:
        if cy + 30 > max_y:
            break
        time_text = f"{item.time}  "
        draw.text((cx, cy), time_text, font=font_time, fill=time_color)
        bbox = draw.textbbox((0, 0), time_text, font=font_time)
        time_w = bbox[2] - bbox[0]

        desc = _strip_markdown(item.description)
        max_desc_width = w - _CARD_PADDING * 2 - time_w
        wrapped = _wrap_text(draw, desc, font_item, max_desc_width)
        for i, wline in enumerate(wrapped):
            if cy + 20 > max_y:
                break
            draw.text((cx + time_w if i == 0 else cx + time_w, cy), wline, font=font_item, fill=white)
            bbox = draw.textbbox((0, 0), wline, font=font_item)
            cy += (bbox[3] - bbox[1]) + _LINE_SPACING


def _render_motivation_section(
    draw: ImageDraw.ImageDraw,
    x: int, y: int, w: int, h: int,
    data: DashboardData, font_size: int, opacity: float,
) -> None:
    """Render motivation comment card."""
    _draw_card(draw, x, y, w, h, opacity)

    font_title = _get_font(max(font_size * 3 // 4, 48))
    font_body = _get_font(max(font_size // 3, 24))

    cx = x + _CARD_PADDING
    cy = y + _CARD_PADDING
    white = (255, 255, 255, 255)
    dim = (180, 180, 180, 255)

    max_y = y + h - _CARD_PADDING

    # Section header
    _, header_h = _draw_text_with_emoji(draw, (cx, cy), "💬 Today", font_title, white, max(font_size * 3 // 4, 48))
    cy += header_h + _GROUP_SPACING

    if data.motivation is None or not data.motivation.comment:
        draw.text((cx, cy), "No message yet", font=font_body, fill=dim)
        return

    # Word-wrap the motivation text within the card width
    max_text_width = w - _CARD_PADDING * 2

    for line in data.motivation.comment.split("\n"):
        line = _strip_markdown(line)
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


def _strip_markdown(text: str) -> str:
    """Remove markdown formatting from text."""
    import re
    # Remove checkbox markers
    text = re.sub(r'\[[ x/]\]\s*', '', text)
    # Remove bold **text** or __text__
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'__(.+?)__', r'\1', text)
    # Remove italic *text* or _text_
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    # Remove inline code `text`
    text = re.sub(r'`(.+?)`', r'\1', text)
    # Remove markdown links [text](url)
    text = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', text)
    # Remove heading markers
    text = re.sub(r'^#{1,6}\s+', '', text)
    # Remove blockquote markers
    text = re.sub(r'^>\s+', '', text)
    # Remove list markers
    text = re.sub(r'^[-*+]\s+', '', text)
    return text.strip()


def _wrap_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.FreeTypeFont,
    max_width: int,
) -> list[str]:
    """Wrap text to fit within max_width pixels."""
    text = _strip_variation_selectors(text)
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


def _render_goal_section(
    draw: ImageDraw.ImageDraw,
    x: int, y: int, w: int, h: int,
    data: DashboardData, font_size: int, opacity: float,
) -> None:
    """Render monthly goal card."""
    _draw_card(draw, x, y, w, h, opacity)

    font_title = _get_font(max(font_size * 3 // 4, 48))
    font_theme = _get_font(max(font_size * 2 // 5, 32))
    font_item = _get_font(max(font_size // 3, 24))

    cx = x + _CARD_PADDING
    cy = y + _CARD_PADDING
    white = (255, 255, 255, 255)
    dim = (180, 180, 180, 255)
    accent = (255, 220, 100, 255)
    max_y = y + h - _CARD_PADDING

    # Section header
    _, header_h = _draw_text_with_emoji(draw, (cx, cy), "🎯 Weekly Goal", font_title, white, max(font_size * 3 // 4, 48))
    cy += header_h + _GROUP_SPACING

    if data.monthly_goal is None:
        draw.text((cx, cy), "No goal set", font=font_item, fill=dim)
        return

    # Theme
    if data.monthly_goal.theme:
        theme_text = f"「{data.monthly_goal.theme}」"
        draw.text((cx, cy), theme_text, font=font_theme, fill=accent)
        bbox = draw.textbbox((0, 0), theme_text, font=font_theme)
        cy += (bbox[3] - bbox[1]) + _GROUP_SPACING

    # Project-grouped goals
    font_project = _get_font(max(font_size * 2 // 5, 30))
    project_color = (100, 200, 255, 255)
    max_text_width = w - _CARD_PADDING * 2

    for pg in data.monthly_goal.project_goals:
        if cy + 30 > max_y:
            break
        # Project name
        draw.text((cx, cy), f"■ {pg.project}", font=font_project, fill=project_color)
        bbox = draw.textbbox((0, 0), f"■ {pg.project}", font=font_project)
        cy += (bbox[3] - bbox[1]) + _LINE_SPACING

        # Goals under project
        for goal in pg.goals:
            if cy + 20 > max_y:
                break
            line = f"  ・{_strip_markdown(goal)}"
            wrapped = _wrap_text(draw, line, font_item, max_text_width)
            for wline in wrapped:
                if cy + 20 > max_y:
                    break
                draw.text((cx, cy), wline, font=font_item, fill=white)
                bbox = draw.textbbox((0, 0), wline, font=font_item)
                cy += (bbox[3] - bbox[1]) + _LINE_SPACING

        cy += _GROUP_SPACING


_SECTION_RENDERERS = {
    "weather": _render_weather_section,
    "motivation": _render_motivation_section,
    "goal": _render_goal_section,
    "weekly_tasks": _render_weekly_tasks_section,
    "today_plan": _render_today_plan_section,
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

    # Sections that should be placed side-by-side
    _SIDE_BY_SIDE = {"weekly_tasks", "today_plan"}

    # Render each section
    current_y = dash_y
    i = 0
    while i < len(active_sections):
        section_name = active_sections[i]
        section_h = section_heights[i]

        # Check if this and the next section should be side-by-side
        if (i + 1 < len(active_sections)
                and section_name in _SIDE_BY_SIDE
                and active_sections[i + 1] in _SIDE_BY_SIDE):
            next_name = active_sections[i + 1]
            next_h = section_heights[i + 1]
            pair_h = max(section_h, next_h)
            half_w = (dash_w - _CARD_GAP) // 2

            # Left card
            renderer_left = _SECTION_RENDERERS[section_name]
            renderer_left(draw, dash_x, current_y, half_w, pair_h, data, font_size, opacity)

            # Right card
            renderer_right = _SECTION_RENDERERS[next_name]
            renderer_right(draw, dash_x + half_w + _CARD_GAP, current_y, half_w, pair_h, data, font_size, opacity)

            current_y += pair_h + _CARD_GAP
            i += 2
        else:
            renderer = _SECTION_RENDERERS[section_name]
            renderer(draw, dash_x, current_y, dash_w, section_h, data, font_size, opacity)
            current_y += section_h + _CARD_GAP
            i += 1

    result = Image.alpha_composite(img, overlay).convert("RGB")
    result.save(output_path, "JPEG", quality=95)
    logger.info("Rendered dashboard to: %s", output_path)
    return output_path
