"""Folder selection widget with drag-and-drop support."""

from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QFileDialog, QHBoxLayout, QLabel, QPushButton, QWidget


class FolderCard(QWidget):
    """Compact folder selector used in the main window."""

    folder_changed = pyqtSignal(Path)

    def __init__(self, initial_folder: Path) -> None:
        super().__init__()
        self._folder = initial_folder
        self.setAcceptDrops(True)

        self._label = QLabel(str(initial_folder))
        self._label.setWordWrap(True)
        button = QPushButton("Select")
        button.clicked.connect(self._select_folder)

        layout = QHBoxLayout(self)
        layout.addWidget(QLabel("Folder:"))
        layout.addWidget(self._label, stretch=1)
        layout.addWidget(button)

    @property
    def folder(self) -> Path:
        return self._folder

    def set_folder(self, folder: Path) -> None:
        self._folder = folder
        self._label.setText(str(folder))
        self.folder_changed.emit(folder)

    def dragEnterEvent(self, event: object) -> None:
        if hasattr(event, "mimeData") and event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: object) -> None:
        urls = event.mimeData().urls()
        if not urls:
            return
        folder = Path(urls[0].toLocalFile())
        if folder.is_dir():
            self.set_folder(folder)

    def _select_folder(self) -> None:
        selected = QFileDialog.getExistingDirectory(self, "Select folder", str(self._folder))
        if selected:
            self.set_folder(Path(selected))
