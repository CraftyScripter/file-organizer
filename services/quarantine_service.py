"""Operations for duplicate quarantine files."""

from __future__ import annotations

from pathlib import Path

from core.history_manager import HistoryManager, QuarantinedDuplicate
from core.mover import FileMover, MoveResult


class QuarantineService:
    def __init__(self, history_manager: HistoryManager, mover: FileMover) -> None:
        self._history_manager = history_manager
        self._mover = mover

    def list_items(self) -> list[QuarantinedDuplicate]:
        return [
            item
            for item in self._history_manager.list_quarantined_duplicates()
            if item.quarantine_path.exists()
        ]

    def restore(self, item: QuarantinedDuplicate) -> MoveResult:
        return self._mover.move_back(item.quarantine_path, item.original_path)

    @staticmethod
    def delete_permanently(item: QuarantinedDuplicate) -> bool:
        try:
            item.quarantine_path.unlink()
        except OSError:
            return False
        return True

    @staticmethod
    def can_preview(path: Path) -> bool:
        return path.exists() and path.is_file()
