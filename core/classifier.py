"""Destination classification strategies."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Literal

from config.file_types import category_for_extension

OrganizationMode = Literal["type", "extension", "size", "created_date", "modified_date", "custom_rules"]


@dataclass(frozen=True, slots=True)
class FileMetadata:
    """Small immutable metadata object used by rules and classifiers."""

    path: Path
    extension: str
    size_bytes: int
    created_at: float
    modified_at: float


class FileClassifier:
    """Classifies files into relative destination folders."""

    def __init__(self, custom_rules: list[dict[str, Any]] | None = None) -> None:
        self._custom_rules = custom_rules or []

    def classify(self, metadata: FileMetadata, mode: OrganizationMode) -> Path | None:
        if mode == "custom_rules":
            return self._classify_by_custom_rules(metadata)
        if mode == "type":
            category = category_for_extension(metadata.extension)
            return Path(category) if category != "unknown" else None
        if mode == "extension":
            return Path(metadata.extension or "no_extension")
        if mode == "size":
            return Path(self._size_bucket(metadata.size_bytes))
        if mode == "created_date":
            return Path(datetime.fromtimestamp(metadata.created_at).strftime("%Y/%m"))
        if mode == "modified_date":
            return Path(datetime.fromtimestamp(metadata.modified_at).strftime("%Y/%m"))
        raise ValueError(f"Unsupported organization mode: {mode}")

    def _classify_by_custom_rules(self, metadata: FileMetadata) -> Path | None:
        for rule in self._custom_rules:
            if not rule.get("enabled", True):
                continue
            if self._matches_rule(metadata, rule.get("conditions", {})):
                destination = str(rule.get("destination", "")).strip()
                if destination:
                    return Path(destination)
        return self.classify(metadata, "type")

    @staticmethod
    def _matches_rule(metadata: FileMetadata, conditions: dict[str, Any]) -> bool:
        extension = str(conditions.get("ext", "")).lower().lstrip(".")
        if extension and metadata.extension != extension:
            return False

        category = str(conditions.get("type", "")).lower()
        if category and category_for_extension(metadata.extension) != category:
            return False

        size_mb = metadata.size_bytes / (1024 * 1024)
        if "size_gt_mb" in conditions and size_mb <= float(conditions["size_gt_mb"]):
            return False
        if "size_lt_mb" in conditions and size_mb >= float(conditions["size_lt_mb"]):
            return False

        name_contains = str(conditions.get("name_contains", ""))
        if name_contains and name_contains.lower() not in metadata.path.name.lower():
            return False
        return True

    @staticmethod
    def _size_bucket(size_bytes: int) -> str:
        mb = size_bytes / (1024 * 1024)
        if mb < 1:
            return "small"
        if mb < 100:
            return "medium"
        if mb < 1024:
            return "large"
        return "huge"
