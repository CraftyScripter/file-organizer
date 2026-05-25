"""Application-wide constants."""

from __future__ import annotations

from pathlib import Path

APP_NAME = "Intelligent File Organizer"
APP_ROOT = Path(__file__).resolve().parents[1]
STORAGE_DIR = APP_ROOT / "storage"
LOG_DIR = STORAGE_DIR / "logs"
DATABASE_PATH = STORAGE_DIR / "app.db"
SETTINGS_PATH = STORAGE_DIR / "settings.json"
LOG_PATH = LOG_DIR / "file_organizer.log"
DUPLICATE_QUARANTINE_DIR = STORAGE_DIR / "duplicate_quarantine"

DEFAULT_WINDOW_WIDTH = 1400
DEFAULT_WINDOW_HEIGHT = 900
SIDEBAR_EXPANDED_WIDTH = 240
SIDEBAR_COLLAPSED_WIDTH = 72

WATCH_DEBOUNCE_MS = 500
DEFAULT_PAGE_SIZE = 250

THEMES_DIR = APP_ROOT / "themes"
DARK_THEME_PATH = THEMES_DIR / "dark.qss"
LIGHT_THEME_PATH = THEMES_DIR / "light.qss"

ASSETS_DIR = APP_ROOT / "assets"
APP_ICON_PATH = ASSETS_DIR / "file-organizer.png"
