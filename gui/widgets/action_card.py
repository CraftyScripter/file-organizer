"""Large quick action button."""

from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QToolButton, QVBoxLayout

from gui.icons import icon


class ActionCard(QFrame):
    triggered = pyqtSignal(str)

    def __init__(self, action_id: str, title: str, subtitle: str, icon_name: str) -> None:
        super().__init__()
        self.setObjectName("ActionCard")
        self._action_id = action_id
        self._icon_name = icon_name
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._button = QToolButton()
        self._button.setObjectName("ActionIconButton")
        self._button.setIcon(icon(icon_name))
        self._button.setToolTip(title)
        self._button.clicked.connect(lambda: self.triggered.emit(self._action_id))

        title_label = QLabel(title)
        title_label.setObjectName("ActionTitle")
        subtitle_label = QLabel(subtitle)
        subtitle_label.setObjectName("ActionSubtitle")
        subtitle_label.setWordWrap(True)

        text = QVBoxLayout()
        text.setSpacing(4)
        text.addWidget(title_label)
        text.addWidget(subtitle_label)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(12)
        layout.addWidget(self._button)
        layout.addLayout(text, stretch=1)

    def refresh_icon(self) -> None:
        """Refresh the icon when theme changes."""
        self._button.setIcon(icon(self._icon_name))

    def set_selected(self, selected: bool) -> None:
        self.setProperty("selected", selected)
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    def mousePressEvent(self, event: object) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.triggered.emit(self._action_id)
        super().mousePressEvent(event)
