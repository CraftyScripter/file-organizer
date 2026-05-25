from __future__ import annotations

from pathlib import Path

from core.scanner import FileScanner


def test_scanner_does_not_enter_subfolders_by_default(tmp_path: Path) -> None:
    direct_file = tmp_path / "report.pdf"
    nested_file = tmp_path / "project" / "main.py"
    direct_file.write_text("pdf", encoding="utf-8")
    nested_file.parent.mkdir()
    nested_file.write_text("print('keep me here')", encoding="utf-8")

    files = list(FileScanner().iter_files(tmp_path))

    assert files == [direct_file]
