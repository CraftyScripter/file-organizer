from __future__ import annotations

from unittest.mock import MagicMock, patch
from PyQt6.QtCore import Qt
from gui.main_window import MainWindow


def test_resolve_theme_light() -> None:
    assert MainWindow._resolve_theme(None, "light") == "light"


def test_resolve_theme_dark() -> None:
    assert MainWindow._resolve_theme(None, "dark") == "dark"


def test_resolve_theme_system_dark() -> None:
    with patch("PyQt6.QtGui.QGuiApplication.instance") as mock_instance:
        mock_app = MagicMock()
        mock_instance.return_value = mock_app
        mock_app.styleHints().colorScheme.return_value = Qt.ColorScheme.Dark
        
        assert MainWindow._resolve_theme(None, "system") == "dark"


def test_resolve_theme_system_light() -> None:
    with patch("PyQt6.QtGui.QGuiApplication.instance") as mock_instance:
        mock_app = MagicMock()
        mock_instance.return_value = mock_app
        mock_app.styleHints().colorScheme.return_value = Qt.ColorScheme.Light
        
        assert MainWindow._resolve_theme(None, "system") == "light"


def test_resolve_theme_system_fallback() -> None:
    with patch("PyQt6.QtGui.QGuiApplication.instance") as mock_instance:
        mock_instance.return_value = None
        
        assert MainWindow._resolve_theme(None, "system") == "dark"


def test_resolve_accent_color_static() -> None:
    assert MainWindow._resolve_accent_color(None, "#ff6b6b") == "#ff6b6b"


def test_resolve_accent_color_system() -> None:
    with patch("PyQt6.QtGui.QGuiApplication.instance") as mock_instance:
        mock_app = MagicMock()
        mock_instance.return_value = mock_app
        mock_color = MagicMock()
        mock_color.isValid.return_value = True
        mock_color.name.return_value = "#123456"
        mock_app.palette().color.return_value = mock_color
        
        assert MainWindow._resolve_accent_color(None, "system") == "#123456"


def test_resolve_accent_color_system_invalid() -> None:
    with patch("PyQt6.QtGui.QGuiApplication.instance") as mock_instance:
        mock_app = MagicMock()
        mock_instance.return_value = mock_app
        mock_color = MagicMock()
        mock_color.isValid.return_value = False
        mock_app.palette().color.return_value = mock_color
        
        assert MainWindow._resolve_accent_color(None, "system") == "#7c5cff"


def test_resolve_accent_color_system_fallback() -> None:
    with patch("PyQt6.QtGui.QGuiApplication.instance") as mock_instance:
        mock_instance.return_value = None
        
        assert MainWindow._resolve_accent_color(None, "system") == "#7c5cff"


def test_accent_tokens_use_system_color() -> None:
    tokens = MainWindow._accent_tokens(None, "#123456")

    assert tokens["accent"] == "#123456"
    assert tokens["accent_foreground"] == "#ffffff"
    assert tokens["accent_soft"] == "rgba(18, 52, 86, 36)"


def test_accent_tokens_choose_light_foreground_for_dark_red() -> None:
    tokens = MainWindow._accent_tokens(None, "#9f1d1d")

    assert tokens["accent_foreground"] == "#ffffff"

