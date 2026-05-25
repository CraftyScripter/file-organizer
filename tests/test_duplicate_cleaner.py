from __future__ import annotations

from pathlib import Path

from core.duplicate_cleaner import DuplicateCleaner
from core.duplicate_detector import DuplicateDetector
from core.history_manager import HistoryManager
from core.mover import FileMover
from core.scanner import FileScanner


def test_duplicate_cleaner_quarantines_extra_copies(tmp_path: Path) -> None:
    folder = tmp_path / "folder"
    quarantine = tmp_path / "quarantine"
    db_path = tmp_path / "app.db"
    folder.mkdir()
    first = folder / "a.txt"
    second = folder / "b.txt"
    unique = folder / "c.txt"
    first.write_text("same", encoding="utf-8")
    second.write_text("same", encoding="utf-8")
    unique.write_text("different", encoding="utf-8")

    cleaner = DuplicateCleaner(
        FileScanner(),
        DuplicateDetector(),
        FileMover(DuplicateDetector()),
        HistoryManager(db_path),
        quarantine,
    )

    summary = cleaner.remove_duplicates(folder)

    assert summary.removed == 1
    assert len(list(folder.iterdir())) == 2
    assert unique.exists()
    assert len(list(quarantine.rglob("*.txt"))) == 1


def test_duplicate_cleaner_prefers_original_looking_name(tmp_path: Path) -> None:
    folder = tmp_path / "folder"
    quarantine = tmp_path / "quarantine"
    db_path = tmp_path / "app.db"
    folder.mkdir()
    copy = folder / "report copy.txt"
    original = folder / "report.txt"
    copy.write_text("same", encoding="utf-8")
    original.write_text("same", encoding="utf-8")

    cleaner = DuplicateCleaner(
        FileScanner(),
        DuplicateDetector(),
        FileMover(DuplicateDetector()),
        HistoryManager(db_path),
        quarantine,
    )

    summary = cleaner.remove_duplicates(folder)

    assert summary.removed == 1
    assert original.exists()
    assert not copy.exists()
    assert (next(quarantine.rglob("*.txt"))).name == "report copy.txt"


def test_duplicate_cleaner_treats_numbered_suffix_as_copy(tmp_path: Path) -> None:
    folder = tmp_path / "folder"
    quarantine = tmp_path / "quarantine"
    db_path = tmp_path / "app.db"
    folder.mkdir()
    original = folder / "photo.png"
    copy = folder / "photo (1).png"
    original.write_bytes(b"same")
    copy.write_bytes(b"same")

    cleaner = DuplicateCleaner(
        FileScanner(),
        DuplicateDetector(),
        FileMover(DuplicateDetector()),
        HistoryManager(db_path),
        quarantine,
    )

    cleaner.remove_duplicates(folder)

    assert original.exists()
    assert not copy.exists()
