"""History page."""

from __future__ import annotations

from PyQt6.QtWidgets import QHeaderView, QLabel, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

from core.history_manager import HistoryManager


class HistoryPage(QWidget):
    def __init__(self, history_manager: HistoryManager) -> None:
        super().__init__()
        self._history_manager = history_manager
        title = QLabel("History")
        title.setObjectName("PageTitle")
        self._empty = QLabel("No activity")
        self._empty.setObjectName("EmptyState")
        self._table = QTableWidget(0, 5)
        self._table.setHorizontalHeaderLabels(["Run", "Timestamp", "Mode", "Files moved", "Undo"])
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._table.verticalHeader().setVisible(False)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.addWidget(title)
        layout.addWidget(self._empty)
        layout.addWidget(self._table, stretch=1)
        self.refresh()

    def refresh(self) -> None:
        runs = self._history_manager.list_runs()
        self._empty.setVisible(not runs)
        self._table.setRowCount(len(runs))
        for row, run in enumerate(runs):
            self._table.setItem(row, 0, QTableWidgetItem(str(run.id)))
            self._table.setItem(row, 1, QTableWidgetItem(run.timestamp))
            self._table.setItem(row, 2, QTableWidgetItem(run.mode))
            self._table.setItem(row, 3, QTableWidgetItem(str(run.files_moved)))
            self._table.setItem(row, 4, QTableWidgetItem("Undone" if run.undone else "Available"))
