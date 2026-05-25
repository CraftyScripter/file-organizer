"""Preview facade for the GUI."""

from __future__ import annotations

from pathlib import Path

from core.classifier import OrganizationMode
from core.organizer import FileOrganizer, OrganizationPlan


class PreviewService:
    """Builds move previews without touching files."""

    def __init__(self, organizer: FileOrganizer) -> None:
        self._organizer = organizer

    def preview(self, directory: Path, mode: OrganizationMode, recursive: bool) -> list[OrganizationPlan]:
        return self._organizer.preview(directory, mode, recursive)
