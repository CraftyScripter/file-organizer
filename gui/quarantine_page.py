"""Duplicate quarantine page."""

from __future__ import annotations

from pathlib import Path
import subprocess

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QScrollArea, QVBoxLayout, QWidget

from core.history_manager import QuarantinedDuplicate
from models.stats_model import format_bytes


class QuarantinePage(QWidget):
    restore_requested = pyqtSignal(object)
    delete_requested = pyqtSignal(object)

    def __init__(self) -> None:
        super().__init__()
        title = QLabel("Quarantine")
        title.setObjectName("PageTitle")
        helper = QLabel("Duplicate copies moved here are safe to preview, restore, or delete permanently.")
        helper.setObjectName("PageHelper")
        self._empty = QLabel("No quarantined duplicates")
        self._empty.setObjectName("EmptyState")
        self._items = QWidget()
        self._items_layout = QVBoxLayout(self._items)
        self._items_layout.setContentsMargins(0, 0, 0, 0)
        self._items_layout.setSpacing(10)
        self._items_layout.addWidget(self._empty)
        self._items_layout.addStretch()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setWidget(self._items)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(14)
        layout.addWidget(title)
        layout.addWidget(helper)
        layout.addWidget(scroll, stretch=1)

    def set_items(self, items: list[QuarantinedDuplicate]) -> None:
        self._clear()
        self._empty.setVisible(not items)
        if not items:
            self._items_layout.insertWidget(0, self._empty)
            return
        for item in items:
            self._items_layout.insertWidget(self._items_layout.count() - 1, self._card(item))

    def _clear(self) -> None:
        while self._items_layout.count() > 1:
            entry = self._items_layout.takeAt(0)
            widget = entry.widget()
            if widget is not None and widget is not self._empty:
                widget.deleteLater()

    def _card(self, item: QuarantinedDuplicate) -> QFrame:
        card = QFrame()
        card.setObjectName("PreviewCard")
        name = QLabel(item.quarantine_path.name)
        name.setObjectName("PreviewFileName")
        name.setToolTip(str(item.quarantine_path))
        meta = QLabel(f"{self._size_label(item.quarantine_path)} | quarantined {item.timestamp}")
        meta.setObjectName("PreviewMeta")
        source = QLabel(f"Original: {item.original_path}")
        source.setObjectName("PreviewPath")
        source.setToolTip(str(item.original_path))
        current = QLabel(f"Quarantine: {item.quarantine_path}")
        current.setObjectName("PreviewPath")
        current.setToolTip(str(item.quarantine_path))

        preview = QPushButton("Preview")
        preview.clicked.connect(lambda: self._open_path(item.quarantine_path))
        reveal = QPushButton("Reveal")
        reveal.clicked.connect(lambda: self._open_path(item.quarantine_path.parent))
        restore = QPushButton("Restore")
        restore.clicked.connect(lambda: self.restore_requested.emit(item))
        delete = QPushButton("Delete")
        delete.setObjectName("DangerButton")
        delete.clicked.connect(lambda: self.delete_requested.emit(item))

        actions = QHBoxLayout()
        actions.addWidget(preview)
        actions.addWidget(reveal)
        actions.addWidget(restore)
        actions.addWidget(delete)
        actions.addStretch()

        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(7)
        layout.addWidget(name)
        layout.addWidget(meta)
        layout.addWidget(source)
        layout.addWidget(current)
        layout.addLayout(actions)
        return card

    @staticmethod
    def _size_label(path: Path) -> str:
        try:
            return format_bytes(path.stat().st_size)
        except OSError:
            return "Missing"

    @staticmethod
    def _open_path(path: Path) -> None:
        try:
            subprocess.Popen(["xdg-open", str(path)])
        except OSError:
            return
