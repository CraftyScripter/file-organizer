"""Icon helpers with a qtawesome fallback and theme support."""

from __future__ import annotations

from PyQt6.QtGui import QColor, QIcon, QPixmap

try:
    import qtawesome as qta
except ImportError:  # pragma: no cover - depends on optional desktop dependency.
    qta = None

# Theme configuration for icons
_THEME_COLORS = {
    "dark": {
        "default": "#cdd0d4",      # Light gray - visible on dark
        "hover": "#e0e3e8",        # Lighter on hover
        "checked": "#7eb09a",      # Green when selected
        "accent": "#7eb09a",
    },
    "light": {
        "default": "#6b5a48",       # Warm brown - visible on paper
        "hover": "#4a3727",         # Darker brown on hover
        "checked": "#5a7a4a",       # Sage green when selected
        "accent": "#5a7a4a",
    },
    "paper": {
        "default": "#6b5a48",       # Warm brown - visible on paper
        "hover": "#4a3727",         # Darker brown on hover
        "checked": "#5a7a4a",       # Sage green when selected
        "accent": "#5a7a4a",
    },
}

_current_theme = "dark"


def set_theme(theme: str) -> None:
    """Set current theme for icon coloring."""
    global _current_theme
    _current_theme = theme


def get_icon_color(state: str = "default") -> str:
    """Get icon color for current theme and state."""
    theme_colors = _THEME_COLORS.get(_current_theme, _THEME_COLORS["dark"])
    return theme_colors.get(state, theme_colors["default"])


def icon(name: str, color: str | None = None) -> QIcon:
    """Load icon with theme-aware coloring."""
    if qta is not None:
        if color is not None:
            return qta.icon(name, color=color)
        c_default = get_icon_color("default")
        c_hover = get_icon_color("hover")
        c_checked = get_icon_color("checked")
        return qta.icon(
            name,
            color=c_default,
            color_active=c_hover,
            color_selected=c_checked,
            color_off=c_default,
            color_off_active=c_hover,
            color_on=c_checked,
            color_on_active=c_hover,
        )
    
    # Fallback to colored square
    pixmap = QPixmap(20, 20)
    pixmap.fill(QColor(color or get_icon_color()))
    return QIcon(pixmap)