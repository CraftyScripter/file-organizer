"""Organize page."""

from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QGridLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from core.classifier import OrganizationMode
from gui.widgets.action_card import ActionCard


class OrganizePage(QWidget):
    preview_requested = pyqtSignal()
    organize_requested = pyqtSignal()
    mode_changed = pyqtSignal(str)

    def __init__(self, default_mode: str) -> None:
        super().__init__()
        self._current_mode = default_mode or "type"
        self._mode_cards: dict[str, ActionCard] = {}

        title = QLabel("Organize")
        title.setObjectName("PageTitle")
        helper = QLabel("Choose one organization mode. Click anywhere on a card to select it.")
        helper.setObjectName("PageHelper")

        actions = QGridLayout()
        actions.setSpacing(12)
        modes = [
            ("type", "Organize by Type", "Documents, images, media, archives", "fa5s.layer-group"),
            ("extension", "Organize by Extension", "Precise suffix grouping", "fa5s.file-code"),
            ("size", "Organize by Size", "Small, medium, large, huge", "fa5s.weight"),
            ("created_date", "Organize by Date", "Create year and month folders", "fa5s.calendar"),
            ("modified_date", "Organize by Modified Date", "Group by last changed month", "fa5s.clock"),
            ("custom_rules", "Custom Rules", "Apply configured rule set", "fa5s.sliders-h"),
        ]
        for index, item in enumerate(modes):
            card = ActionCard(*item)
            card.setToolTip(f"Select {item[1]}")
            card.triggered.connect(self.set_mode)
            self._mode_cards[item[0]] = card
            actions.addWidget(card, index // 2, index % 2)

        preview = QPushButton("Preview")
        preview.clicked.connect(self.preview_requested)
        organize = QPushButton("Start Organizing")
        organize.clicked.connect(self.organize_requested)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(16)
        layout.addWidget(title)
        layout.addWidget(helper)
        layout.addLayout(actions)
        layout.addWidget(preview)
        layout.addWidget(organize)
        layout.addStretch()
        self._sync_cards()

    def mode(self) -> OrganizationMode:
        return self._current_mode

    def recursive(self) -> bool:
        return False

    def set_mode(self, mode: str) -> None:
        if mode not in self._mode_cards or mode == self._current_mode:
            return
        self._current_mode = mode
        self._sync_cards()
        self.mode_changed.emit(self.mode())

    def refresh_icons(self) -> None:
        """Refresh all action card icons when theme changes."""
        for card in self._mode_cards.values():
            card.refresh_icon()

    def _sync_cards(self) -> None:
        for mode, card in self._mode_cards.items():
            card.set_selected(mode == self._current_mode)
