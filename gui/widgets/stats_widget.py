"""Statistics widget for planned moves."""

from __future__ import annotations

from collections import Counter

from PyQt6.QtWidgets import QGridLayout, QLabel, QWidget

from config.file_types import FILE_TYPES
from core.organizer import OrganizationPlan


class StatsWidget(QWidget):
    """Displays counts by category."""

    def __init__(self) -> None:
        super().__init__()
        self._labels: dict[str, QLabel] = {}
        layout = QGridLayout(self)
        for index, category in enumerate(FILE_TYPES):
            name = QLabel(f"{category.title()}:")
            value = QLabel("0")
            self._labels[category] = value
            layout.addWidget(name, index // 2, (index % 2) * 2)
            layout.addWidget(value, index // 2, (index % 2) * 2 + 1)

    def update_from_plans(self, plans: list[OrganizationPlan]) -> None:
        counts = Counter(str(plan.category).split("/")[0] for plan in plans)
        for category, label in self._labels.items():
            label.setText(str(counts.get(category, 0)))
