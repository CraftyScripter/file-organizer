"""Dataclasses for preview rows."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class PreviewRow:
    source: Path
    destination: Path
    file_type: str
    reason: str
    status: str
    action: str

    @property
    def filename(self) -> str:
        return self.source.name
