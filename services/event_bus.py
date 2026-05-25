"""Small Qt signal bus for live application updates."""

from __future__ import annotations

from PyQt6.QtCore import QObject, pyqtSignal


class EventBus(QObject):
    folder_changed = pyqtSignal(str)
    preview_updated = pyqtSignal(list)
    stats_updated = pyqtSignal(object)
    history_updated = pyqtSignal()
    activity_created = pyqtSignal(str, str)
    progress_changed = pyqtSignal(int, int, str)
    status_changed = pyqtSignal(str)
