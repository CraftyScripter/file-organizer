"""Analytics page."""

from __future__ import annotations

from PyQt6.QtWidgets import QFrame, QGridLayout, QLabel, QVBoxLayout, QWidget

from gui.widgets.chart_widget import ChartWidget
from models.stats_model import StatsSnapshot, format_bytes


class AnalyticsSummary(QFrame):
    def __init__(self, title: str) -> None:
        super().__init__()
        self.setObjectName("ChartPanel")
        self._title = QLabel(title)
        self._title.setObjectName("PanelTitle")
        self._body = QLabel("No data")
        self._body.setObjectName("AnalyticsText")
        self._body.setWordWrap(True)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)
        layout.addWidget(self._title)
        layout.addWidget(self._body)
        layout.addStretch()

    def set_text(self, text: str) -> None:
        self._body.setText(text)


class AnalyticsPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        title = QLabel("Analytics")
        title.setObjectName("PageTitle")
        self._charts = [
            ChartWidget("Files by type", "pie"),
            ChartWidget("Top categories", "bar"),
        ]
        self._largest = AnalyticsSummary("Selected folder")
        self._duplicates = AnalyticsSummary("Duplicate savings")
        grid = QGridLayout()
        grid.setSpacing(16)
        grid.addWidget(self._charts[0], 0, 0)
        grid.addWidget(self._charts[1], 0, 1)
        grid.addWidget(self._largest, 1, 0)
        grid.addWidget(self._duplicates, 1, 1)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(16)
        layout.addWidget(title)
        layout.addLayout(grid)
        layout.addStretch()

    def update_stats(self, snapshot: StatsSnapshot) -> None:
        for chart in self._charts:
            chart.update_snapshot(snapshot)
        self._largest.set_text(
            f"{snapshot.files:,} files in the main folder\n"
            f"{snapshot.folders:,} subfolders present but not scanned\n"
            f"{snapshot.storage_label} total file size"
        )
        self._duplicates.set_text(
            f"{snapshot.duplicates:,} duplicate files found\n"
            f"{snapshot.duplicate_savings_label} potential savings\n"
            "Live updates run automatically when the main folder changes."
        )
