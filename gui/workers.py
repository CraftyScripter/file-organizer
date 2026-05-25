"""Background workers used by the redesigned GUI."""

from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot

from core.analytics_engine import AnalyticsEngine
from core.classifier import OrganizationMode
from core.duplicate_cleaner import DuplicateCleaner
from core.organizer import FileOrganizer
from services.undo_service import UndoService


class OperationWorker(QObject):
    progress = pyqtSignal(int, int, str)
    preview_ready = pyqtSignal(list)
    finished = pyqtSignal(str, list)
    stats_ready = pyqtSignal(object)
    failed = pyqtSignal(str)

    def __init__(
        self,
        task: str,
        organizer: FileOrganizer,
        undo_service: UndoService,
        analytics_engine: AnalyticsEngine,
        duplicate_cleaner: DuplicateCleaner,
        directory: Path,
        mode: OrganizationMode,
        recursive: bool,
    ) -> None:
        super().__init__()
        self._task = task
        self._organizer = organizer
        self._undo_service = undo_service
        self._analytics_engine = analytics_engine
        self._duplicate_cleaner = duplicate_cleaner
        self._directory = directory
        self._mode = mode
        self._recursive = recursive
        self._cancelled = False

    def cancel(self) -> None:
        self._cancelled = True

    @pyqtSlot()
    def run(self) -> None:
        try:
            if self._task == "preview":
                plans = self._organizer.preview(self._directory, self._mode, self._recursive)
                self.preview_ready.emit(plans)
                self.stats_ready.emit(self._analytics_engine.snapshot(self._directory, self._recursive))
                self.finished.emit(self._task, plans)
                return
            if self._task == "refresh":
                plans = self._organizer.preview(self._directory, self._mode, self._recursive)
                self.preview_ready.emit(plans)
                self.stats_ready.emit(self._analytics_engine.snapshot(self._directory, self._recursive))
                self.finished.emit(self._task, plans)
                return
            if self._task == "undo":
                results = self._undo_service.undo_last()
                self.stats_ready.emit(self._analytics_engine.snapshot(self._directory, self._recursive))
                self.finished.emit(self._task, results)
                return
            if self._task == "remove_duplicates":
                summary = self._duplicate_cleaner.remove_duplicates(self._directory)
                self.stats_ready.emit(self._analytics_engine.snapshot(self._directory, self._recursive))
                self.finished.emit(self._task, [summary])
                return
            if self._task == "stats":
                self.stats_ready.emit(self._analytics_engine.snapshot(self._directory, self._recursive))
                self.finished.emit(self._task, [])
                return

            results = self._organizer.organize(
                self._directory,
                self._mode,
                self._recursive,
                progress_callback=lambda current, total, path: self.progress.emit(current, total, str(path)),
                cancel_callback=lambda: self._cancelled,
            )
            self.stats_ready.emit(self._analytics_engine.snapshot(self._directory, self._recursive))
            self.finished.emit(self._task, results)
        except Exception as exc:  # noqa: BLE001 - UI boundary should surface unexpected failures.
            self.failed.emit(str(exc))
