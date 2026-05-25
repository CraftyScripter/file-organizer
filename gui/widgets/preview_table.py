"""Card-based preview list for planned moves."""

from __future__ import annotations

from pathlib import Path
import subprocess

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImageReader, QPixmap
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QScrollArea, QVBoxLayout, QWidget

from config.file_types import category_for_extension
from core.organizer import OrganizationPlan
from models.preview_model import PreviewRow


class PreviewTable(QScrollArea):
    """Searchable card list for move previews."""

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("PreviewList")
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._rows: list[PreviewRow] = []
        self._query = ""
        self._content = QWidget()
        self._layout = QVBoxLayout(self._content)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(6)
        self._layout.addStretch()
        self.setWidget(self._content)

    def set_plans(self, plans: list[OrganizationPlan]) -> None:
        self._rows = [self._row_from_plan(plan) for plan in plans]
        self._render()

    def set_search(self, text: str) -> None:
        self._query = text.casefold().strip()
        self._render()

    def rows(self) -> list[PreviewRow]:
        return list(self._rows)

    def _render(self) -> None:
        while self._layout.count() > 1:
            item = self._layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        for row in self._filtered_rows():
            self._layout.insertWidget(self._layout.count() - 1, self._card(row))

    def _filtered_rows(self) -> list[PreviewRow]:
        if not self._query:
            return self._rows
        return [
            row
            for row in self._rows
            if self._query in row.filename.casefold()
            or self._query in str(row.source).casefold()
            or self._query in str(row.destination).casefold()
            or self._query in row.action.casefold()
        ]

    def _card(self, row: PreviewRow) -> QFrame:
        card = QFrame()
        card.setObjectName("PreviewCard")
        thumbnail = self._preview_widget(row.source, row.file_type)
        name = QLabel(row.filename)
        name.setObjectName("PreviewFileName")
        name.setToolTip(str(row.source))
        meta = QLabel(f"{row.file_type.title()} | {row.action.title()} | {row.status.title()}")
        meta.setObjectName("PreviewMeta")
        source = QLabel(f"From: {row.source.parent}")
        source.setObjectName("PreviewPath")
        source.setToolTip(str(row.source))
        destination = QLabel(f"To: {row.destination.parent / row.destination.name}")
        destination.setObjectName("PreviewPath")
        destination.setToolTip(str(row.destination))
        reason = QLabel(row.reason)
        reason.setObjectName("PreviewReason")

        open_button = QPushButton("Open")
        open_button.clicked.connect(lambda: self._open_path(row.source))
        reveal = QPushButton("Reveal")
        reveal.clicked.connect(lambda: self._open_path(row.source.parent))
        actions = QHBoxLayout()
        actions.setSpacing(6)
        actions.addWidget(open_button)
        actions.addWidget(reveal)
        actions.addStretch()

        text = QVBoxLayout()
        text.setSpacing(2)
        text.addWidget(name)
        text.addWidget(meta)
        text.addWidget(source)
        text.addWidget(destination)
        text.addWidget(reason)
        text.addLayout(actions)

        layout = QHBoxLayout(card)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(8)
        layout.addWidget(thumbnail)
        layout.addLayout(text, stretch=1)
        return card

    @staticmethod
    def _row_from_plan(plan: OrganizationPlan) -> PreviewRow:
        file_type = category_for_extension(plan.source.suffix.lower().lstrip("."))
        status = "review" if plan.action in {"duplicate", "rename"} else "ready"
        return PreviewRow(
            source=plan.source,
            destination=plan.destination,
            file_type=file_type,
            reason=f"Matched {plan.category}",
            status=status,
            action=plan.action,
        )

    @staticmethod
    def _icon_text(row: PreviewRow) -> str:
        mapping = {"image": "IMG", "document": "DOC", "video": "VID", "audio": "AUD", "archive": "ZIP"}
        return mapping.get(row.file_type, "FILE")

    @staticmethod
    def _preview_widget(path: Path, file_type: str) -> QLabel:
        preview = QLabel()
        preview.setObjectName("PreviewIcon")
        preview.setFixedSize(56, 56)
        preview.setAlignment(Qt.AlignmentFlag.AlignCenter)

        if file_type == "image":
            reader = QImageReader(str(path))
            if reader.canRead():
                pixmap = QPixmap(str(path))
                if not pixmap.isNull():
                    preview.setPixmap(
                        pixmap.scaled(
                            preview.size(),
                            Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                            Qt.TransformationMode.SmoothTransformation,
                        )
                    )
                    preview.setStyleSheet("border-image: none;")
                    return preview

        preview.setText(PreviewTable._icon_text(PreviewRow(path, path, file_type, "", "", "")))
        return preview

    @staticmethod
    def _open_path(path: Path) -> None:
        try:
            subprocess.Popen(["xdg-open", str(path)])
        except OSError:
            return
