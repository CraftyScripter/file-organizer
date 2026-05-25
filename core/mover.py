"""Collision-safe file moving."""

from __future__ import annotations

from dataclasses import dataclass
import logging
from pathlib import Path
import shutil

from core.duplicate_detector import DuplicateDetector

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class MoveResult:
    source: Path
    destination: Path
    action: str
    success: bool
    error: str | None = None


class FileMover:
    """Moves files while handling duplicates and filename collisions."""

    def __init__(self, duplicate_detector: DuplicateDetector | None = None) -> None:
        self._duplicate_detector = duplicate_detector or DuplicateDetector()

    def resolve_destination(self, destination: Path) -> Path:
        if not destination.exists():
            return destination

        stem = destination.stem
        suffix = destination.suffix
        parent = destination.parent
        counter = 1
        while True:
            candidate = parent / f"{stem} ({counter}){suffix}"
            if not candidate.exists():
                return candidate
            counter += 1

    def move(self, source: Path, destination: Path) -> MoveResult:
        try:
            destination.parent.mkdir(parents=True, exist_ok=True)
            if destination.exists() and self._duplicate_detector.is_duplicate(source, destination):
                logger.info("Duplicate detected, leaving source in place: %s", source)
                return MoveResult(source=source, destination=destination, action="duplicate", success=True)

            final_destination = self.resolve_destination(destination)
            shutil.move(str(source), str(final_destination))
            logger.info("Moved %s -> %s", source, final_destination)
            return MoveResult(source=source, destination=final_destination, action="moved", success=True)
        except PermissionError as exc:
            logger.exception("Permission denied moving %s", source)
            return MoveResult(source=source, destination=destination, action="error", success=False, error=str(exc))
        except OSError as exc:
            logger.exception("Failed moving %s", source)
            return MoveResult(source=source, destination=destination, action="error", success=False, error=str(exc))

    def move_back(self, source: Path, destination: Path) -> MoveResult:
        return self.move(source, destination)
