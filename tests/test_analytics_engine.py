from __future__ import annotations

from pathlib import Path

from core.analytics_engine import AnalyticsEngine
from core.scanner import FileScanner


def test_snapshot_includes_duplicate_files(tmp_path: Path) -> None:
    folder = tmp_path / "folder"
    folder.mkdir()
    first = folder / "one.txt"
    second = folder / "two.txt"
    first.write_text("same", encoding="utf-8")
    second.write_text("same", encoding="utf-8")

    engine = AnalyticsEngine(FileScanner())
    snapshot = engine.snapshot(folder)

    assert snapshot.duplicates == 1
    assert snapshot.duplicate_files == ["two.txt"]