"""Analytics computations for dashboard and charts."""

from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

from config.file_types import category_for_extension
from core.duplicate_detector import DuplicateDetector
from core.scanner import FileScanner
from models.stats_model import FolderUsage, StatsSnapshot


class AnalyticsEngine:
    """Builds folder snapshots without touching UI objects."""

    def __init__(self, scanner: FileScanner | None = None, duplicate_detector: DuplicateDetector | None = None) -> None:
        self._scanner = scanner or FileScanner()
        self._duplicate_detector = duplicate_detector or DuplicateDetector()

    def snapshot(self, folder: Path, recursive: bool = False, detect_duplicates: bool = True) -> StatsSnapshot:
        if not folder.exists() or not folder.is_dir():
            return StatsSnapshot()

        files = 0
        folders = self._count_folders(folder, recursive)
        storage_bytes = 0
        files_by_type: Counter[str] = Counter()
        folder_usage: dict[str, list[int]] = defaultdict(lambda: [0, 0])
        timeline: Counter[str] = Counter()
        duplicates = 0
        duplicate_savings = 0
        duplicate_files: list[str] = []
        seen_hashes: dict[tuple[int, str], Path] = {}

        paths = sorted(self._scanner.iter_files(folder, recursive), key=lambda path: str(path).casefold())
        for path in paths:
            try:
                stat = path.stat()
            except OSError:
                continue

            files += 1
            storage_bytes += stat.st_size
            category = category_for_extension(path.suffix.lower().lstrip("."))
            files_by_type[category] += 1
            top = self._top_folder_name(path, folder)
            folder_usage[top][0] += stat.st_size
            folder_usage[top][1] += 1
            timeline[datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d")] += 1

            if detect_duplicates:
                key = self._duplicate_key(path, stat.st_size)
                if key is not None:
                    if key in seen_hashes:
                        duplicates += 1
                        duplicate_savings += stat.st_size
                        duplicate_files.append(self._display_path(path, folder))
                    else:
                        seen_hashes[key] = path

        usage = [
            FolderUsage(name=name, bytes_used=values[0], files=values[1])
            for name, values in sorted(folder_usage.items(), key=lambda item: item[1][0], reverse=True)
        ]
        return StatsSnapshot(
            files=files,
            folders=folders,
            duplicates=duplicates,
            storage_bytes=storage_bytes,
            duplicate_savings_bytes=duplicate_savings,
            duplicate_files=duplicate_files[:20],
            files_by_type=dict(files_by_type),
            folder_usage=usage[:12],
            timeline=sorted(timeline.items())[-30:],
        )

    @staticmethod
    def _top_folder_name(path: Path, root: Path) -> str:
        try:
            relative = path.relative_to(root)
        except ValueError:
            return root.name
        return relative.parts[0] if len(relative.parts) > 1 else "Root"

    @staticmethod
    def _count_folders(folder: Path, recursive: bool) -> int:
        try:
            if recursive:
                return sum(1 for item in folder.rglob("*") if item.is_dir())
            return sum(1 for item in folder.iterdir() if item.is_dir())
        except OSError:
            return 0

    def _duplicate_key(self, path: Path, size: int) -> tuple[int, str] | None:
        try:
            return (size, self._duplicate_detector.sha256(path))
        except OSError:
            return None

    @staticmethod
    def _display_path(path: Path, root: Path) -> str:
        try:
            relative = path.relative_to(root)
        except ValueError:
            return str(path)
        return str(relative)
