"""Undo support for the latest organization run."""

from __future__ import annotations

import logging

from core.history_manager import HistoryManager
from core.mover import FileMover, MoveResult

logger = logging.getLogger(__name__)


class UndoService:
    """Moves files from their organized destinations back to original paths."""

    def __init__(self, history_manager: HistoryManager, mover: FileMover) -> None:
        self._history_manager = history_manager
        self._mover = mover

    def undo_last(self) -> list[MoveResult]:
        run_id = self._history_manager.get_last_active_run_id()
        if run_id is None:
            return []

        results: list[MoveResult] = []
        for original_source, organized_destination in self._history_manager.list_successful_moves(run_id):
            if not organized_destination.exists():
                logger.warning("Cannot undo missing file: %s", organized_destination)
                results.append(
                    MoveResult(
                        source=organized_destination,
                        destination=original_source,
                        action="missing",
                        success=False,
                        error="Organized file no longer exists",
                    )
                )
                continue
            results.append(self._mover.move_back(organized_destination, original_source))

        if all(result.success for result in results):
            self._history_manager.mark_undone(run_id)
        return results
