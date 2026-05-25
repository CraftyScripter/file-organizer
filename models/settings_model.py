"""Typed setting option metadata used by the settings UI."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SelectOption:
    label: str
    value: str


THEME_OPTIONS = [
    SelectOption("System", "system"),
    SelectOption("Dark", "dark"),
    SelectOption("Light", "light"),
]
MODE_OPTIONS = [
    SelectOption("Type", "type"),
    SelectOption("Extension", "extension"),
    SelectOption("Size", "size"),
    SelectOption("Created Date", "created_date"),
    SelectOption("Modified Date", "modified_date"),
    SelectOption("Custom Rules", "custom_rules"),
]
CONFLICT_OPTIONS = [
    SelectOption("Rename", "rename"),
    SelectOption("Skip", "skip"),
    SelectOption("Replace", "replace"),
]
DUPLICATE_OPTIONS = [
    SelectOption("Review", "review"),
    SelectOption("Skip", "skip"),
    SelectOption("Replace", "replace"),
    SelectOption("Merge", "merge"),
]
