from __future__ import annotations

from pathlib import Path

from core.mover import FileMover


def test_resolve_destination_adds_numeric_suffix(tmp_path: Path) -> None:
    destination = tmp_path / "document" / "report.pdf"
    destination.parent.mkdir()
    destination.write_text("existing", encoding="utf-8")

    assert FileMover().resolve_destination(destination) == tmp_path / "document" / "report (1).pdf"
