"""High-level orchestration for previewing and organizing files."""

from __future__ import annotations

from dataclasses import dataclass
import logging
from pathlib import Path
from typing import Callable

from core.classifier import FileClassifier, FileMetadata, OrganizationMode
from core.history_manager import HistoryManager
from core.mover import FileMover, MoveResult
from core.scanner import FileScanner

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class OrganizationPlan:
    source: Path
    destination: Path
    action: str
    category: str


ProgressCallback = Callable[[int, int, Path], None]
CancelCallback = Callable[[], bool]


class FileOrganizer:
    """Coordinates scanning, classification, previewing, moving, and history."""

    def __init__(
        self,
        scanner: FileScanner,
        classifier: FileClassifier,
        mover: FileMover,
        history_manager: HistoryManager,
    ) -> None:
        self._scanner = scanner
        self._classifier = classifier
        self._mover = mover
        self._history_manager = history_manager

    def preview(self, directory: Path, mode: OrganizationMode, recursive: bool = False) -> list[OrganizationPlan]:
        plans: list[OrganizationPlan] = []
        for path in self._scanner.iter_files(directory, recursive):
            metadata = self._metadata(path)
            relative_folder = self._classifier.classify(metadata, mode)
            if relative_folder is None:
                continue
            destination = directory / relative_folder / path.name
            if destination.resolve() == path.resolve():
                continue
            action = "move"
            if destination.exists():
                action = "duplicate" if self._same_size(path, destination) else "rename"
                destination = self._mover.resolve_destination(destination)
            plans.append(OrganizationPlan(path, destination, action, str(relative_folder)))
        return plans

    def organize(
        self,
        directory: Path,
        mode: OrganizationMode,
        recursive: bool = False,
        progress_callback: ProgressCallback | None = None,
        cancel_callback: CancelCallback | None = None,
    ) -> list[MoveResult]:
        plans = self.preview(directory, mode, recursive)
        run_id = self._history_manager.create_run(mode, directory)
        results: list[MoveResult] = []
        total = len(plans)

        for index, plan in enumerate(plans, start=1):
            if cancel_callback and cancel_callback():
                logger.info("Organization cancelled after %s of %s planned moves", index - 1, total)
                break

            result = self._mover.move(plan.source, plan.destination)
            self._history_manager.add_move(
                run_id,
                result.source,
                result.destination,
                result.action,
                result.success,
                result.error,
            )
            results.append(result)
            if not result.success:
                results.extend(self._rollback_successful_moves(results))
                self._history_manager.mark_undone(run_id)
                break
            if progress_callback:
                progress_callback(index, total, plan.source)

        return results

    @staticmethod
    def _metadata(path: Path) -> FileMetadata:
        stat = path.stat()
        return FileMetadata(
            path=path,
            extension=path.suffix.lower().lstrip("."),
            size_bytes=stat.st_size,
            created_at=stat.st_ctime,
            modified_at=stat.st_mtime,
        )

    @staticmethod
    def _same_size(first: Path, second: Path) -> bool:
        try:
            return first.stat().st_size == second.stat().st_size
        except OSError:
            return False

    def _rollback_successful_moves(self, results: list[MoveResult]) -> list[MoveResult]:
        rollback_results: list[MoveResult] = []
        for result in reversed(results):
            if result.success and result.action == "moved" and result.destination.exists():
                rollback = self._mover.move_back(result.destination, result.source)
                rollback_results.append(
                    MoveResult(
                        source=rollback.source,
                        destination=rollback.destination,
                        action="rollback",
                        success=rollback.success,
                        error=rollback.error,
                    )
                )
        return rollback_results
