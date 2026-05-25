"""Modern metric card widget."""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame, QGraphicsDropShadowEffect, QLabel, QVBoxLayout
from PyQt6.QtGui import QColor


class StatCard(QFrame):
    def __init__(self, title: str, value: str = "0", detail: str = "") -> None:
        super().__init__()
        self.setObjectName("StatCard")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._title = QLabel(title)
        self._title.setObjectName("StatCardTitle")
        self._value = QLabel(value)
        self._value.setObjectName("StatCardValue")
        self._detail = QLabel(detail)
        self._detail.setObjectName("StatCardDetail")
        self._detail.setWordWrap(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(8)
        layout.addWidget(self._title)
        layout.addWidget(self._value)
        layout.addWidget(self._detail)
        layout.addStretch()

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(28)
        shadow.setOffset(0, 10)
        shadow.setColor(QColor(0, 0, 0, 70))
        self.setGraphicsEffect(shadow)

        self.setMinimumHeight(132)
        self.setMaximumHeight(132)

    def set_value(self, value: str, detail: str = "") -> None:
        self._value.setText(value)
        self._detail.setText(detail)
