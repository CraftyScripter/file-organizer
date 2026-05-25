"""History window."""

from __future__ import annotations

from PyQt6.QtWidgets import QHeaderView, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

from core.history_manager import HistoryManager


class HistoryWindow(QWidget):
    """Displays recent organization runs."""

    def __init__(self, history_manager: HistoryManager) -> None:
        super().__init__()
        self.setWindowTitle("History")
        self.resize(760, 360)
        self._history_manager = history_manager
        self._table = QTableWidget(0, 4)
        self._table.setHorizontalHeaderLabels(["Timestamp", "Files moved", "Mode", "Undo"])
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._table.verticalHeader().setVisible(False)

        layout = QVBoxLayout(self)
        layout.addWidget(self._table)
        self.refresh()

    def refresh(self) -> None:
        runs = self._history_manager.list_runs()
        self._table.setRowCount(len(runs))
        for row, run in enumerate(runs):
            self._table.setItem(row, 0, QTableWidgetItem(run.timestamp))
            self._table.setItem(row, 1, QTableWidgetItem(str(run.files_moved)))
            self._table.setItem(row, 2, QTableWidgetItem(run.mode))
            self._table.setItem(row, 3, QTableWidgetItem("Undone" if run.undone else "Available"))
