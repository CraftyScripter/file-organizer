"""Background worker objects for long-running operations."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot

from core.classifier import OrganizationMode
from core.mover import MoveResult
from core.organizer import FileOrganizer, OrganizationPlan
from services.undo_service import UndoService

WorkerTask = Literal["preview", "organize", "undo"]


class OrganizeWorker(QObject):
    """Runs preview, organize, or undo actions off the UI thread."""

    progress = pyqtSignal(int, int, str)
    preview_ready = pyqtSignal(list)
    finished = pyqtSignal(list)
    failed = pyqtSignal(str)

    def __init__(
        self,
        task: WorkerTask,
        organizer: FileOrganizer,
        undo_service: UndoService,
        directory: Path,
        mode: OrganizationMode,
        recursive: bool,
    ) -> None:
        super().__init__()
        self._task = task
        self._organizer = organizer
        self._undo_service = undo_service
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
                self.finished.emit(plans)
                return
            if self._task == "undo":
                results = self._undo_service.undo_last()
                self.finished.emit(results)
                return

            results = self._organizer.organize(
                self._directory,
                self._mode,
                self._recursive,
                progress_callback=self._emit_progress,
                cancel_callback=lambda: self._cancelled,
            )
            self.finished.emit(results)
        except Exception as exc:  # noqa: BLE001 - UI boundary should surface unexpected failures.
            self.failed.emit(str(exc))

    def _emit_progress(self, current: int, total: int, path: Path) -> None:
        self.progress.emit(current, total, str(path))
