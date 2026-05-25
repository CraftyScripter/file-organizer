"""SHA256 duplicate detection helpers."""

from __future__ import annotations

import hashlib
from pathlib import Path


class DuplicateDetector:
    """Computes hashes and identifies same-content files."""

    def sha256(self, path: Path, chunk_size: int = 1024 * 1024) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as file:
            for chunk in iter(lambda: file.read(chunk_size), b""):
                digest.update(chunk)
        return digest.hexdigest()

    def is_duplicate(self, source: Path, destination: Path) -> bool:
        if not destination.exists() or not destination.is_file():
            return False
        if source.stat().st_size != destination.stat().st_size:
            return False
        return self.sha256(source) == self.sha256(destination)
