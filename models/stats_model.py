"""Dashboard and analytics data models."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class FolderUsage:
    name: str
    bytes_used: int
    files: int


@dataclass(frozen=True, slots=True)
class StatsSnapshot:
    files: int = 0
    folders: int = 0
    duplicates: int = 0
    storage_bytes: int = 0
    duplicate_savings_bytes: int = 0
    duplicate_files: list[str] = field(default_factory=list)
    files_by_type: dict[str, int] = field(default_factory=dict)
    folder_usage: list[FolderUsage] = field(default_factory=list)
    timeline: list[tuple[str, int]] = field(default_factory=list)

    @property
    def storage_label(self) -> str:
        return format_bytes(self.storage_bytes)

    @property
    def duplicate_savings_label(self) -> str:
        return format_bytes(self.duplicate_savings_bytes)


def format_bytes(value: int) -> str:
    size = float(value)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1024 or unit == "TB":
            return f"{size:.1f} {unit}" if unit != "B" else f"{int(size)} B"
        size /= 1024
    return f"{size:.1f} TB"
