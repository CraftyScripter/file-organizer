"""Dashboard page."""

from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QFrame, QGridLayout, QLabel, QVBoxLayout, QWidget

from gui.widgets.action_card import ActionCard
from gui.widgets.stat_card import StatCard
from models.stats_model import StatsSnapshot


class DuplicateFilesPanel(QFrame):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("ChartPanel")
        self._title = QLabel("Duplicate files")
        self._title.setObjectName("PanelTitle")
        self._body = QLabel("No duplicate files detected yet.")
        self._body.setObjectName("AnalyticsText")
        self._body.setWordWrap(True)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)
        layout.addWidget(self._title)
        layout.addWidget(self._body)
        layout.addStretch()

    def set_duplicates(self, duplicate_files: list[str]) -> None:
        if not duplicate_files:
            self._body.setText("No duplicate files detected yet.")
            return

        lines = [f"• {path}" for path in duplicate_files[:8]]
        remaining = len(duplicate_files) - len(lines)
        if remaining > 0:
            lines.append(f"+ {remaining} more duplicate file{'s' if remaining != 1 else ''}")
        self._body.setText("\n".join(lines))


class DashboardPage(QWidget):
    action_requested = pyqtSignal(str)

    def __init__(self) -> None:
        super().__init__()
        self._cards = {
            "files": StatCard("Files"),
            "folders": StatCard("Folders"),
            "duplicates": StatCard("Duplicates"),
            "storage": StatCard("Storage"),
        }
        self._duplicate_files = DuplicateFilesPanel()
        title = QLabel("Dashboard")
        title.setObjectName("PageTitle")
        self._empty = QLabel("No folder selected")
        self._empty.setObjectName("EmptyState")

        stats = QGridLayout()
        stats.setSpacing(16)
        for index, card in enumerate(self._cards.values()):
            stats.addWidget(card, 0, index)

        actions = QGridLayout()
        actions.setSpacing(12)
        data = [
            ("type", "Select Type Mode", "Open Organize with type grouping selected", "fa5s.layer-group"),
            ("extension", "Select Extension Mode", "Open Organize with extension grouping selected", "fa5s.file-code"),
            ("created_date", "Select Date Mode", "Open Organize with date grouping selected", "fa5s.calendar"),
            ("size", "Select Size Mode", "Open Organize with size grouping selected", "fa5s.weight"),
            ("custom_rules", "Select Custom Rules", "Open Organize with custom rules selected", "fa5s.sliders-h"),
            ("remove_duplicates", "Remove Duplicates", "Review before moving duplicate copies", "fa5s.clone"),
            ("auto", "Live Watch", "Already watching the main folder", "fa5s.bolt"),
            ("undo", "Undo Last Action", "Review before restoring moved files", "fa5s.undo"),
        ]
        self._action_cards: list[ActionCard] = []
        for index, item in enumerate(data):
            card = ActionCard(*item)
            card.triggered.connect(self.action_requested)
            actions.addWidget(card, index // 2, index % 2)
            self._action_cards.append(card)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(18)
        layout.addWidget(title)
        layout.addWidget(self._empty)
        layout.addLayout(stats)
        layout.addWidget(self._duplicate_files)
        layout.addWidget(QLabel("Quick Actions"))
        layout.addLayout(actions)
        layout.addStretch()

    def refresh_icons(self) -> None:
        """Refresh all action card icons when theme changes."""
        for card in self._action_cards:
            card.refresh_icon()

    def update_stats(self, snapshot: StatsSnapshot) -> None:
        self._empty.setVisible(snapshot.files == 0 and snapshot.folders == 0)
        self._cards["files"].set_value(f"{snapshot.files:,}", "Files in the main folder")
        self._cards["folders"].set_value(f"{snapshot.folders:,}", "Subfolders shown, not scanned")
        self._cards["duplicates"].set_value(f"{snapshot.duplicates:,}", snapshot.duplicate_savings_label)
        self._cards["storage"].set_value(snapshot.storage_label, "Main folder file size")
        self._duplicate_files.set_duplicates(snapshot.duplicate_files)
