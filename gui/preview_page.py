"""Preview page."""

from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget

from core.organizer import OrganizationPlan
from gui.widgets.preview_table import PreviewTable


class PreviewPage(QWidget):
    preview_requested = pyqtSignal()
    organize_requested = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        title = QLabel("Preview")
        title.setObjectName("PageTitle")
        self._search = QLineEdit()
        self._search.setPlaceholderText("Search preview")
        self._filter = QComboBox()
        self._filter.addItems(["All statuses", "Ready", "Review"])
        self._table = PreviewTable()
        self._empty = QLabel("No files found")
        self._empty.setObjectName("EmptyState")
        preview_button = QPushButton("Preview")
        preview_button.clicked.connect(self.preview_requested)
        organize_button = QPushButton("Confirm Moves")
        organize_button.clicked.connect(self.organize_requested)
        self._search.textChanged.connect(self._table.set_search)

        toolbar = QHBoxLayout()
        toolbar.addWidget(self._search, stretch=1)
        toolbar.addWidget(self._filter)
        toolbar.addWidget(preview_button)
        toolbar.addWidget(organize_button)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(14)
        layout.addWidget(title)
        layout.addLayout(toolbar)
        layout.addWidget(self._empty)
        layout.addWidget(self._table, stretch=1)

    def set_plans(self, plans: list[OrganizationPlan]) -> None:
        self._empty.setVisible(not plans)
        self._table.set_plans(plans)
