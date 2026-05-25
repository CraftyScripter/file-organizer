"""Duplicate cleanup that keeps one copy and quarantines extras."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
import logging
from pathlib import Path
import re

from config.constants import DUPLICATE_QUARANTINE_DIR
from core.duplicate_detector import DuplicateDetector
from core.history_manager import HistoryManager
from core.mover import FileMover, MoveResult
from core.scanner import FileScanner

logger = logging.getLogger(__name__)

COPY_MARKERS = (
    "copy",
    "copied",
    "duplicate",
    "dup",
)
COPY_SUFFIX_PATTERN = re.compile(r"(?i)(?:\s*[-_]\s*copy|\s+copy|\s+\(\d+\)|\s+-\s+\d+)$")


@dataclass(frozen=True, slots=True)
class DuplicateCleanupSummary:
    removed: int
    kept: int
    bytes_saved: int
    results: list[MoveResult]


class DuplicateCleaner:
    """Finds exact duplicates in one folder and moves duplicate copies away."""

    def __init__(
        self,
        scanner: FileScanner,
        detector: DuplicateDetector,
        mover: FileMover,
        history_manager: HistoryManager,
        quarantine_root: Path = DUPLICATE_QUARANTINE_DIR,
    ) -> None:
        self._scanner = scanner
        self._detector = detector
        self._mover = mover
        self._history_manager = history_manager
        self._quarantine_root = quarantine_root

    def remove_duplicates(self, folder: Path) -> DuplicateCleanupSummary:
        groups = self._duplicate_groups(folder)
        run_id = self._history_manager.create_run("duplicate_cleanup", folder)
        quarantine = self._quarantine_root / datetime.now().strftime("%Y%m%d-%H%M%S")
        results: list[MoveResult] = []
        kept = 0
        bytes_saved = 0

        for paths in groups:
            keeper = self._choose_keeper(paths)
            duplicates = [path for path in paths if path != keeper]
            kept += 1
            for duplicate in duplicates:
                destination = self._mover.resolve_destination(quarantine / duplicate.name)
                result = self._mover.move(duplicate, destination)
                results.append(result)
                self._history_manager.add_move(
                    run_id,
                    result.source,
                    result.destination,
                    "moved",
                    result.success,
                    result.error,
                )
                if result.success:
                    try:
                        bytes_saved += result.destination.stat().st_size
                    except OSError:
                        logger.warning("Could not read quarantined duplicate size: %s", result.destination)
                logger.info("Duplicate cleanup kept %s and quarantined %s", keeper, duplicate)

        return DuplicateCleanupSummary(
            removed=sum(1 for result in results if result.success),
            kept=kept,
            bytes_saved=bytes_saved,
            results=results,
        )

    def _duplicate_groups(self, folder: Path) -> list[list[Path]]:
        by_size: dict[int, list[Path]] = defaultdict(list)
        for path in self._scanner.iter_files(folder, recursive=False):
            try:
                by_size[path.stat().st_size].append(path)
            except OSError:
                continue

        groups_by_hash: dict[str, list[Path]] = defaultdict(list)
        for paths in by_size.values():
            if len(paths) < 2:
                continue
            for path in paths:
                try:
                    groups_by_hash[self._detector.sha256(path)].append(path)
                except OSError:
                    logger.warning("Could not hash duplicate candidate: %s", path)

        return [paths for paths in groups_by_hash.values() if len(paths) > 1]

    def _choose_keeper(self, paths: list[Path]) -> Path:
        """Choose the file that most likely represents the user's original."""
        return min(paths, key=self._original_score)

    @staticmethod
    def _original_score(path: Path) -> tuple[int, int, float, str]:
        stem = path.stem.casefold()
        score = 0
        if "original" in stem:
            score -= 80
        if stem.startswith("copy of "):
            score += 140
        if any(marker in stem.split() for marker in COPY_MARKERS):
            score += 110
        if COPY_SUFFIX_PATTERN.search(path.stem):
            score += 90
        if re.search(r"(?i)\(\d+\)$", path.stem):
            score += 70
        if re.search(r"(?i)\bcopy\s*\d*$", path.stem):
            score += 90

        normalized_length = len(DuplicateCleaner._normalized_original_stem(path.stem))
        try:
            modified_at = path.stat().st_mtime
        except OSError:
            modified_at = float("inf")
        return (score, normalized_length, modified_at, path.name.casefold())

    @staticmethod
    def _normalized_original_stem(stem: str) -> str:
        value = re.sub(r"(?i)^copy of\s+", "", stem)
        value = COPY_SUFFIX_PATTERN.sub("", value)
        value = re.sub(r"(?i)\s*\(\d+\)$", "", value)
        value = re.sub(r"(?i)\bcopy\s*\d*$", "", value)
        return value.strip().casefold()
