"""Set macOS desktop wallpaper via NSWorkspace (Sequoia+) with AppleScript fallback."""

import subprocess
import logging
import sys

logger = logging.getLogger(__name__)


def _set_via_nsworkspace(image_path: str) -> bool:
    """Set wallpaper via PyObjC NSWorkspace (works on macOS Sequoia)."""
    try:
        import AppKit
        import Foundation

        file_url = Foundation.NSURL.fileURLWithPath_(image_path)
        ws = AppKit.NSWorkspace.sharedWorkspace()
        for screen in AppKit.NSScreen.screens():
            result, error = ws.setDesktopImageURL_forScreen_options_error_(
                file_url, screen, {}, None
            )
            if not result:
                return False
        # Restart WallpaperAgent to force refresh
        subprocess.run(["killall", "WallpaperAgent"], capture_output=True)
        return True
    except Exception:
        logger.exception("Failed to set wallpaper via NSWorkspace")
        return False


def _set_via_system_events(image_path: str) -> bool:
    script = f'''
    tell application "System Events"
        tell every desktop
            set picture to "{image_path}"
        end tell
    end tell
    '''
    result = subprocess.run(["osascript", "-e", script], capture_output=True, timeout=10)
    return result.returncode == 0


def _set_via_finder(image_path: str) -> bool:
    script = f'''
    tell application "Finder"
        set desktop picture to POSIX file "{image_path}"
    end tell
    '''
    result = subprocess.run(["osascript", "-e", script], capture_output=True, timeout=10)
    return result.returncode == 0


def set_wallpaper(image_path: str) -> bool:
    if sys.platform == "darwin":
        if _set_via_nsworkspace(image_path):
            logger.info("Wallpaper set via NSWorkspace: %s", image_path)
            return True

    if _set_via_system_events(image_path):
        logger.info("Wallpaper set via System Events: %s", image_path)
        return True

    logger.warning("System Events failed, trying Finder fallback")
    if _set_via_finder(image_path):
        logger.info("Wallpaper set via Finder: %s", image_path)
        return True

    logger.error("Failed to set wallpaper: %s", image_path)
    return False
