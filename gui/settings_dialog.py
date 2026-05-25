"""Settings dialog."""

from __future__ import annotations

import json

from PyQt6.QtWidgets import QCheckBox, QDialog, QDialogButtonBox, QLabel, QPlainTextEdit, QVBoxLayout

from config.settings import AppSettings


class SettingsDialog(QDialog):
    """Allows users to edit monitoring and JSON custom rules."""

    def __init__(self, settings: AppSettings) -> None:
        super().__init__()
        self.setWindowTitle("Settings")
        self._settings = settings

        self._auto_downloads = QCheckBox("Auto organize Downloads")
        self._auto_downloads.setChecked(settings.auto_organize_downloads)
        self._ignore_hidden = QCheckBox("Ignore hidden files")
        self._ignore_hidden.setChecked(settings.ignore_hidden)
        self._rules = QPlainTextEdit(json.dumps(settings.custom_rules, indent=2))
        self._rules.setMinimumHeight(180)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(self._auto_downloads)
        layout.addWidget(self._ignore_hidden)
        layout.addWidget(QLabel("Custom rules JSON"))
        layout.addWidget(self._rules)
        layout.addWidget(buttons)

    def apply_to_settings(self) -> AppSettings:
        self._settings.auto_organize_downloads = self._auto_downloads.isChecked()
        self._settings.recursive = False
        self._settings.ignore_hidden = self._ignore_hidden.isChecked()
        self._settings.custom_rules = json.loads(self._rules.toPlainText() or "[]")
        self._settings.save()
        return self._settings
