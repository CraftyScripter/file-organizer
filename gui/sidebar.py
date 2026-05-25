"""Animated application sidebar."""

from __future__ import annotations

from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, Qt, pyqtSignal
from PyQt6.QtWidgets import QFrame, QLabel, QToolButton, QVBoxLayout

from config.constants import SIDEBAR_COLLAPSED_WIDTH, SIDEBAR_EXPANDED_WIDTH
from gui.icons import icon


class Sidebar(QFrame):
    page_selected = pyqtSignal(str)

    PAGES = [
        ("dashboard", "Dashboard", "fa5s.home"),
        ("organize", "Organize", "fa5s.folder"),
        ("preview", "Preview", "fa5s.eye"),
        ("quarantine", "Quarantine", "fa5s.box"),
        ("analytics", "Analytics", "fa5s.chart-bar"),
        ("history", "History", "fa5s.history"),
        ("settings", "Settings", "fa5s.cog"),
        ("about", "About", "fa5s.info-circle"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("Sidebar")
        self._expanded = True
        self._buttons: dict[str, QToolButton] = {}
        self.setMinimumWidth(SIDEBAR_EXPANDED_WIDTH)
        self.setMaximumWidth(SIDEBAR_EXPANDED_WIDTH)

        self._animation = QPropertyAnimation(self, b"maximumWidth", self)
        self._animation.setDuration(180)
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        self._toggle = QToolButton()
        self._toggle.setObjectName("SidebarToggle")
        self._toggle.setIcon(icon("fa5s.bars"))
        self._toggle.setToolTip("Collapse sidebar")
        self._toggle.clicked.connect(self.toggle)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 18, 16, 18)
        layout.setSpacing(6)
        self._brand = QLabel("File Organizer")
        self._brand.setObjectName("SidebarBrand")
        self._brand.setMinimumHeight(28)
        layout.addWidget(self._brand)
        layout.addWidget(self._toggle)
        
        for page_id, title, icon_name in self.PAGES:
            button = QToolButton()
            button.setObjectName("SidebarButton")
            button.setText(title)
            button.setIcon(icon(icon_name))
            button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
            button.setCheckable(True)
            button.setMinimumHeight(42)
            button.setToolTip(title)
            button.setAutoRaise(True)
            button.clicked.connect(lambda checked=False, value=page_id: self.select(value))
            self._buttons[page_id] = button
            layout.addWidget(button)
            
        layout.addStretch()
        self.select("dashboard")

    def toggle(self) -> None:
        self._expanded = not self._expanded
        target = SIDEBAR_EXPANDED_WIDTH if self._expanded else SIDEBAR_COLLAPSED_WIDTH
        self.setMinimumWidth(target)
        self._animation.stop()
        self._animation.setStartValue(self.maximumWidth())
        self._animation.setEndValue(target)
        self._animation.start()
        style = Qt.ToolButtonStyle.ToolButtonTextBesideIcon if self._expanded else Qt.ToolButtonStyle.ToolButtonIconOnly
        for button in self._buttons.values():
            button.setToolButtonStyle(style)
        self._brand.setVisible(self._expanded)
        self._toggle.setToolTip("Collapse sidebar" if self._expanded else "Expand sidebar")

    def select(self, page_id: str) -> None:
        for key, button in self._buttons.items():
            button.setChecked(key == page_id)
        self.page_selected.emit(page_id)
    
    def refresh_icons(self) -> None:
        """Refresh all icons when theme changes."""
        from gui.icons import icon as get_icon
        
        # Refresh toggle button
        self._toggle.setIcon(get_icon("fa5s.bars"))
        
        # Refresh all page buttons
        for (page_id, title, icon_name), button in zip(self.PAGES, self._buttons.values()):
            button.setIcon(get_icon(icon_name))