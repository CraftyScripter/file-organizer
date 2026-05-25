"""Efficient filesystem scanning."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path


class FileScanner:
    """Scans a directory and yields candidate files lazily."""

    def __init__(self, ignore_hidden: bool = True) -> None:
        self._ignore_hidden = ignore_hidden

    def iter_files(self, directory: Path, recursive: bool = False) -> Iterator[Path]:
        if not directory.exists():
            raise FileNotFoundError(f"Directory does not exist: {directory}")
        if not directory.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {directory}")

        iterator = directory.rglob("*") if recursive else directory.iterdir()
        for path in iterator:
            if self._ignore_hidden and self._is_hidden(path, directory):
                continue
            if path.is_file():
                yield path

    def _is_hidden(self, path: Path, root: Path) -> bool:
        try:
            relative_parts = path.relative_to(root).parts
        except ValueError:
            relative_parts = path.parts
        return any(part.startswith(".") for part in relative_parts)
