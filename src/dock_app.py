"""macOS Dock-based weather display app using tkinter + PyObjC."""

import io
import logging
import tkinter as tk
from typing import Optional

from PIL import Image, ImageDraw

from wallpaper_renderer import _get_font
from weather_fetcher import WeatherData

logger = logging.getLogger(__name__)

ICON_SIZE = 128

# Pillow cannot render emoji, so use short Japanese text for Dock icon
_ICON_TEXT = {
    "clear": "晴",
    "partly_cloudy": "曇",
    "fog": "霧",
    "drizzle": "小雨",
    "rain": "雨",
    "snow": "雪",
    "shower": "雨",
    "thunderstorm": "雷",
    "unknown": "？",
}

# Background colors per weather category
_ICON_BG = {
    "clear": (30, 100, 180, 220),
    "partly_cloudy": (80, 90, 110, 220),
    "fog": (100, 100, 110, 220),
    "drizzle": (60, 70, 100, 220),
    "rain": (40, 50, 80, 220),
    "snow": (120, 130, 150, 220),
    "shower": (50, 55, 85, 220),
    "thunderstorm": (30, 30, 50, 220),
    "unknown": (60, 60, 60, 220),
}


def generate_dock_icon(weather: WeatherData, mapping: dict) -> Image.Image:
    """Generate a 128x128 dock icon image with weather info."""
    img = Image.new("RGBA", (ICON_SIZE, ICON_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    category = mapping.get("category", "unknown")
    bg_color = _ICON_BG.get(category, _ICON_BG["unknown"])

    draw.rounded_rectangle(
        [0, 0, ICON_SIZE - 1, ICON_SIZE - 1],
        radius=24,
        fill=bg_color,
    )

    # Weather text label (top)
    weather_text = _ICON_TEXT.get(category, "？")
    font_label = _get_font(30)
    bbox = draw.textbbox((0, 0), weather_text, font=font_label)
    label_w = bbox[2] - bbox[0]
    draw.text(
        ((ICON_SIZE - label_w) / 2, 10), weather_text, font=font_label, fill="white"
    )

    # Temperature (middle)
    font_temp = _get_font(28)
    temp_text = f"{weather.temperature:.0f}\u00b0C"
    bbox = draw.textbbox((0, 0), temp_text, font=font_temp)
    temp_w = bbox[2] - bbox[0]
    draw.text(
        ((ICON_SIZE - temp_w) / 2, 48), temp_text, font=font_temp, fill="white"
    )

    # Precipitation (bottom)
    font_small = _get_font(18)
    precip_text = f"\u964d\u6c34{weather.precipitation_probability}%"
    bbox = draw.textbbox((0, 0), precip_text, font=font_small)
    precip_w = bbox[2] - bbox[0]
    draw.text(
        ((ICON_SIZE - precip_w) / 2, 88),
        precip_text,
        font=font_small,
        fill=(200, 220, 255, 255),
    )

    return img


def _pil_to_nsimage(pil_image: Image.Image):
    """Convert PIL Image to NSImage via TIFF bytes."""
    import AppKit

    buf = io.BytesIO()
    pil_image.save(buf, format="TIFF")
    ns_data = AppKit.NSData.dataWithBytes_length_(buf.getvalue(), len(buf.getvalue()))
    ns_image = AppKit.NSImage.alloc().initWithData_(ns_data)
    return ns_image


def _set_dock_icon(pil_image: Image.Image) -> None:
    """Set the macOS Dock icon to the given PIL image."""
    import AppKit

    ns_image = _pil_to_nsimage(pil_image)
    AppKit.NSApp.setApplicationIconImage_(ns_image)


class DockWeatherApp:
    def __init__(self, weather_app, interval_min: int = 10) -> None:
        self._weather_app = weather_app
        self._interval_ms = interval_min * 60 * 1000
        self._weather: Optional[WeatherData] = None
        self._mapping: Optional[dict] = None
        self._root: Optional[tk.Tk] = None
        self._dock_icon_pending: Optional[Image.Image] = None

    def update_display(self, weather: WeatherData, mapping: dict) -> None:
        self._weather = weather
        self._mapping = mapping

        # Generate icon and schedule setting it on the main thread
        try:
            self._dock_icon_pending = generate_dock_icon(weather, mapping)
            if self._root:
                self._root.after(0, self._apply_dock_icon)
        except Exception:
            logger.exception("Failed to generate dock icon")

        # Update detail window contents
        if self._root:
            self._root.after(0, self._populate_detail_window)

        logger.info(
            "Dock updated: %s %.1f\u00b0C", mapping["icon"], weather.temperature
        )

    def _apply_dock_icon(self) -> None:
        if self._dock_icon_pending is None:
            return
        try:
            _set_dock_icon(self._dock_icon_pending)
            self._dock_icon_pending = None
        except Exception:
            logger.exception("Failed to set dock icon")

    def _show_window(self) -> None:
        self._root.deiconify()
        self._root.lift()
        self._root.focus_force()

    def _hide_window(self) -> None:
        self._root.withdraw()

    def _populate_detail_window(self) -> None:
        for widget in self._root.winfo_children():
            widget.destroy()

        if self._weather is None:
            tk.Label(
                self._root,
                text="\u30c7\u30fc\u30bf\u53d6\u5f97\u4e2d...",
                font=("Helvetica", 16),
            ).pack(pady=40)
            return

        w = self._weather
        m = self._mapping

        frame = tk.Frame(self._root, padx=20, pady=15)
        frame.pack(fill="both", expand=True)

        tk.Label(
            frame,
            text=f"{m['icon']} {m['description']}",
            font=("Helvetica", 22),
        ).pack(anchor="w")
        tk.Label(
            frame,
            text=f"{w.temperature:.1f}\u00b0C",
            font=("Helvetica", 40, "bold"),
        ).pack(anchor="w", pady=(5, 10))
        tk.Label(
            frame,
            text=f"\u6700\u9ad8 {w.temp_max:.0f}\u00b0C / \u6700\u4f4e {w.temp_min:.0f}\u00b0C",
            font=("Helvetica", 14),
        ).pack(anchor="w")
        tk.Label(
            frame,
            text=f"\u964d\u6c34\u78ba\u7387: {w.precipitation_probability}%",
            font=("Helvetica", 14),
        ).pack(anchor="w")
        tk.Label(
            frame,
            text=f"\u98a8\u901f: {w.wind_speed:.1f} m/s",
            font=("Helvetica", 14),
        ).pack(anchor="w")

    def _on_tick(self) -> None:
        try:
            self._weather_app.tick()
        except Exception:
            logger.exception("Error during tick")
        self._root.after(self._interval_ms, self._on_tick)

    def run(self) -> None:
        self._root = tk.Tk()
        self._root.title("\u5929\u6c17\u60c5\u5831")
        self._root.geometry("300x260")
        self._root.resizable(False, False)

        # Close button hides window instead of quitting
        self._root.protocol("WM_DELETE_WINDOW", self._hide_window)

        # Dock click re-shows the window
        self._root.createcommand(
            "::tk::mac::ReopenApplication", self._show_window
        )

        # Start hidden, show after first data arrives
        self._root.withdraw()

        # Initial tick after event loop starts
        self._root.after(100, self._on_tick)

        self._root.mainloop()
