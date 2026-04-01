"""Set macOS desktop wallpaper via AppleScript subprocess."""

import subprocess
import logging

logger = logging.getLogger(__name__)


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
    if _set_via_system_events(image_path):
        logger.info("Wallpaper set via System Events: %s", image_path)
        return True

    logger.warning("System Events failed, trying Finder fallback")
    if _set_via_finder(image_path):
        logger.info("Wallpaper set via Finder: %s", image_path)
        return True

    logger.error("Failed to set wallpaper: %s", image_path)
    return False
