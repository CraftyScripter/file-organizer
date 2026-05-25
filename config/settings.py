"""Persistent user settings and application paths."""

from __future__ import annotations

from dataclasses import dataclass, field
import json
import logging
from pathlib import Path
from typing import Any

from config.constants import LOG_DIR, LOG_PATH, SETTINGS_PATH


DEFAULT_RULES: list[dict[str, Any]] = [
    {
        "name": "Large PDFs to Books",
        "enabled": True,
        "conditions": {"ext": "pdf", "size_gt_mb": 50},
        "destination": "Books",
    }
]


@dataclass(slots=True)
class AppSettings:
    """Runtime settings loaded from disk and edited through the GUI."""

    default_folder: Path = Path.home() / "Downloads"
    recursive: bool = False
    ignore_hidden: bool = True
    auto_organize_downloads: bool = False
    theme: str = "dark"
    animations_enabled: bool = True
    notifications_enabled: bool = True
    startup_behavior: str = "last_folder"
    default_mode: str = "type"
    conflict_strategy: str = "rename"
    duplicate_handling: str = "review"
    watchdog_enabled: bool = False
    watchdog_recursive: bool = False
    watchdog_debounce_ms: int = 500
    watchdog_batch_updates: bool = True
    accent_color: str = "#7c5cff"
    font_size: int = 13
    compact_mode: bool = False
    card_radius: int = 14
    custom_rules: list[dict[str, Any]] = field(default_factory=lambda: list(DEFAULT_RULES))

    @classmethod
    def load(cls, path: Path = SETTINGS_PATH) -> "AppSettings":
        if not path.exists():
            settings = cls()
            settings.save(path)
            return settings

        data = json.loads(path.read_text(encoding="utf-8"))
        return cls(
            default_folder=Path(data.get("default_folder", Path.home() / "Downloads")),
            recursive=False,
            ignore_hidden=bool(data.get("ignore_hidden", True)),
            auto_organize_downloads=bool(data.get("auto_organize_downloads", False)),
            theme=str(data.get("theme", "dark")),
            animations_enabled=bool(data.get("animations_enabled", True)),
            notifications_enabled=bool(data.get("notifications_enabled", True)),
            startup_behavior=str(data.get("startup_behavior", "last_folder")),
            default_mode=str(data.get("default_mode", "type")),
            conflict_strategy=str(data.get("conflict_strategy", "rename")),
            duplicate_handling=str(data.get("duplicate_handling", "review")),
            watchdog_enabled=bool(data.get("watchdog_enabled", data.get("auto_organize_downloads", False))),
            watchdog_recursive=False,
            watchdog_debounce_ms=int(data.get("watchdog_debounce_ms", 500)),
            watchdog_batch_updates=bool(data.get("watchdog_batch_updates", True)),
            accent_color=str(data.get("accent_color", "#7c5cff")),
            font_size=int(data.get("font_size", 13)),
            compact_mode=bool(data.get("compact_mode", False)),
            card_radius=int(data.get("card_radius", 14)),
            custom_rules=list(data.get("custom_rules", DEFAULT_RULES)),
        )

    def save(self, path: Path = SETTINGS_PATH) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "default_folder": str(self.default_folder),
            "recursive": False,
            "ignore_hidden": self.ignore_hidden,
            "auto_organize_downloads": self.auto_organize_downloads,
            "theme": self.theme,
            "animations_enabled": self.animations_enabled,
            "notifications_enabled": self.notifications_enabled,
            "startup_behavior": self.startup_behavior,
            "default_mode": self.default_mode,
            "conflict_strategy": self.conflict_strategy,
            "duplicate_handling": self.duplicate_handling,
            "watchdog_enabled": self.watchdog_enabled,
            "watchdog_recursive": False,
            "watchdog_debounce_ms": self.watchdog_debounce_ms,
            "watchdog_batch_updates": self.watchdog_batch_updates,
            "accent_color": self.accent_color,
            "font_size": self.font_size,
            "compact_mode": self.compact_mode,
            "card_radius": self.card_radius,
            "custom_rules": self.custom_rules,
        }
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def configure_logging() -> None:
    """Configure file and console logging for the desktop app."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
        handlers=[
            logging.FileHandler(LOG_PATH, encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )
