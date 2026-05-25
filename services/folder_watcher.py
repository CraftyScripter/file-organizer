"""Realtime folder watching with watchdog bridged into Qt signals."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
import logging
from pathlib import Path
import threading
from typing import Literal

from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot
from watchdog.events import FileMovedEvent, FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

logger = logging.getLogger(__name__)

WatchEventKind = Literal["created", "deleted", "modified", "moved"]


@dataclass(frozen=True, slots=True)
class WatchEvent:
    kind: WatchEventKind
    path: Path
    destination: Path | None = None


class _WatchdogHandler(FileSystemEventHandler):
    def __init__(self, enqueue: callable) -> None:
        super().__init__()
        self._enqueue = enqueue

    def on_created(self, event: FileSystemEvent) -> None:
        if not event.is_directory:
            self._enqueue(WatchEvent("created", Path(event.src_path)))

    def on_deleted(self, event: FileSystemEvent) -> None:
        if not event.is_directory:
            self._enqueue(WatchEvent("deleted", Path(event.src_path)))

    def on_modified(self, event: FileSystemEvent) -> None:
        if not event.is_directory:
            self._enqueue(WatchEvent("modified", Path(event.src_path)))

    def on_moved(self, event: FileMovedEvent) -> None:
        if not event.is_directory:
            self._enqueue(WatchEvent("moved", Path(event.src_path), Path(event.dest_path)))


class FolderWatcher(QObject):
    """Starts watchdog observers and emits debounced Qt signals."""

    file_created = pyqtSignal(str)
    file_deleted = pyqtSignal(str)
    file_modified = pyqtSignal(str)
    file_moved = pyqtSignal(str, str)
    batch_ready = pyqtSignal(list)
    stats_updated = pyqtSignal()
    status_changed = pyqtSignal(str)

    def __init__(self, folder: Path, recursive: bool = False, debounce_ms: int = 500) -> None:
        super().__init__()
        self._folder = folder
        self._recursive = False
        self._debounce_seconds = max(debounce_ms, 75) / 1000
        self._observer: Observer | None = None
        self._events: deque[WatchEvent] = deque()
        self._lock = threading.Lock()
        self._timer: threading.Timer | None = None
        self._handler = _WatchdogHandler(self._enqueue)

    @pyqtSlot()
    def start(self) -> None:
        if self._observer is not None:
            return
        try:
            self._folder.mkdir(parents=True, exist_ok=True)
            observer = Observer()
            observer.schedule(self._handler, str(self._folder), recursive=self._recursive)
            observer.start()
            self._observer = observer
        except OSError as exc:
            logger.exception("Failed to start folder watcher for %s", self._folder)
            self.status_changed.emit("Watch error")
            return
        logger.info("Started watching %s recursive=%s", self._folder, self._recursive)
        self.status_changed.emit("Live watching")

    @pyqtSlot()
    def stop(self) -> None:
        if self._timer is not None:
            self._timer.cancel()
            self._timer = None
        if self._observer is None:
            return
        self._observer.stop()
        self._observer.join(timeout=5)
        self._observer = None
        logger.info("Stopped folder watcher")
        self.status_changed.emit("Not watching")

    def _enqueue(self, event: WatchEvent) -> None:
        with self._lock:
            self._events.append(event)
            if self._timer is not None:
                self._timer.cancel()
            self._timer = threading.Timer(self._debounce_seconds, self._flush)
            self._timer.daemon = True
            self._timer.start()

    def _flush(self) -> None:
        with self._lock:
            events = list(self._events)
            self._events.clear()
            self._timer = None

        if not events:
            return

        for event in events:
            if event.kind == "created":
                self.file_created.emit(str(event.path))
            elif event.kind == "deleted":
                self.file_deleted.emit(str(event.path))
            elif event.kind == "modified":
                self.file_modified.emit(str(event.path))
            elif event.kind == "moved" and event.destination is not None:
                self.file_moved.emit(str(event.path), str(event.destination))
        self.batch_ready.emit(events)
        self.stats_updated.emit()
