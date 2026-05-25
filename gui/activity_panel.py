"""Live activity feed panel."""

from __future__ import annotations

from datetime import datetime
from textwrap import shorten

from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, Qt
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QScrollArea, QVBoxLayout, QWidget


MAX_ACTIVITY_ITEMS = 40


class ActivityPanel(QFrame):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("ActivityPanel")
        self.setMinimumWidth(260)
        self.setMaximumWidth(320)

        title = QLabel("Activity")
        title.setObjectName("PanelTitle")
        subtitle = QLabel("Live folder events")
        subtitle.setObjectName("ActivitySubtitle")
        clear = QPushButton("Clear")
        clear.setObjectName("ActivityClearButton")
        clear.clicked.connect(self.clear)

        header_text = QVBoxLayout()
        header_text.setContentsMargins(0, 0, 0, 0)
        header_text.setSpacing(2)
        header_text.addWidget(title)
        header_text.addWidget(subtitle)
        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.addLayout(header_text, stretch=1)
        header.addWidget(clear)

        self._empty = QLabel("No activity yet")
        self._empty.setObjectName("EmptyState")
        self._activity_items: list[QFrame] = []
        self._items = QWidget()
        self._items_layout = QVBoxLayout(self._items)
        self._items_layout.setContentsMargins(0, 0, 0, 0)
        self._items_layout.setSpacing(8)
        self._items_layout.addWidget(self._empty)
        self._items_layout.addStretch()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setWidget(self._items)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        layout.addLayout(header)
        layout.addWidget(scroll, stretch=1)

    def add_activity(self, action: str, detail: str) -> None:
        self._empty.hide()
        item = QFrame()
        item.setObjectName("ActivityItem")

        title = QLabel(self._label_action(action))
        title.setObjectName("ActivityTitle")
        time = QLabel(datetime.now().strftime("%H:%M:%S"))
        time.setObjectName("ActivityTime")
        body = QLabel(shorten(detail.replace("\n", " "), width=44, placeholder="..."))
        body.setObjectName("ActivityBody")
        body.setToolTip(detail)
        body.setWordWrap(False)

        top = QHBoxLayout()
        top.setContentsMargins(0, 0, 0, 0)
        top.setSpacing(8)
        top.addWidget(title, stretch=1)
        top.addWidget(time)

        item_layout = QVBoxLayout(item)
        item_layout.setContentsMargins(12, 10, 12, 10)
        item_layout.setSpacing(4)
        item_layout.addLayout(top)
        item_layout.addWidget(body)

        self._items_layout.insertWidget(0, item)
        self._activity_items.insert(0, item)
        self._trim_items()

        animation = QPropertyAnimation(item, b"maximumHeight", item)
        animation.setDuration(160)
        animation.setStartValue(0)
        animation.setEndValue(70)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        animation.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)

    def clear(self) -> None:
        for widget in self._activity_items:
            self._items_layout.removeWidget(widget)
            widget.deleteLater()
        self._activity_items.clear()
        self._empty.show()

    def _trim_items(self) -> None:
        while len(self._activity_items) > MAX_ACTIVITY_ITEMS:
            widget = self._activity_items.pop()
            self._items_layout.removeWidget(widget)
            widget.deleteLater()

    @staticmethod
    def _label_action(action: str) -> str:
        labels = {
            "folder changed": "Updated",
            "created": "Created",
            "deleted": "Deleted",
            "modified": "Changed",
            "moved": "Moved",
            "duplicates removed": "Duplicates",
        }
        return labels.get(action.casefold(), action.title())
