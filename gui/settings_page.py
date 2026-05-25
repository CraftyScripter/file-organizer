"""Settings page with real controls instead of a JSON editor."""

from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from config.settings import AppSettings
from models.settings_model import CONFLICT_OPTIONS, DUPLICATE_OPTIONS, MODE_OPTIONS, THEME_OPTIONS


class SettingsPage(QWidget):
    settings_applied = pyqtSignal(object)
    reset_requested = pyqtSignal()

    def __init__(self, settings: AppSettings) -> None:
        super().__init__()
        self._settings = settings
        title = QLabel("Settings")
        title.setObjectName("PageTitle")
        self._tabs = QTabWidget()
        self._build_general()
        self._build_organization()
        self._build_monitoring()
        self._build_appearance()
        self._build_advanced()
        apply = QPushButton("Apply")
        cancel = QPushButton("Cancel")
        reset = QPushButton("Reset")
        apply.clicked.connect(self.apply)
        cancel.clicked.connect(self.reload)
        reset.clicked.connect(self._reset)
        buttons = QHBoxLayout()
        buttons.addStretch()
        buttons.addWidget(reset)
        buttons.addWidget(cancel)
        buttons.addWidget(apply)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.addWidget(title)
        layout.addWidget(self._tabs, stretch=1)
        layout.addLayout(buttons)

    def _combo(self, options: object, value: str) -> QComboBox:
        combo = QComboBox()
        for option in options:
            combo.addItem(option.label, option.value)
        index = combo.findData(value)
        combo.setCurrentIndex(max(index, 0))
        return combo

    def _build_general(self) -> None:
        page = QWidget()
        form = QFormLayout(page)
        self._theme = self._combo(THEME_OPTIONS, self._settings.theme)
        self._animations = QCheckBox()
        self._animations.setChecked(self._settings.animations_enabled)
        self._notifications = QCheckBox()
        self._notifications.setChecked(self._settings.notifications_enabled)
        self._startup = QComboBox()
        self._startup.addItems(["last_folder", "downloads", "none"])
        self._startup.setCurrentText(self._settings.startup_behavior)
        form.addRow("Theme", self._theme)
        form.addRow("Animations", self._animations)
        form.addRow("Enable notifications", self._notifications)
        form.addRow("Startup behavior", self._startup)
        self._tabs.addTab(page, "General")

    def _build_organization(self) -> None:
        page = QWidget()
        form = QFormLayout(page)
        self._default_mode = self._combo(MODE_OPTIONS, self._settings.default_mode)
        self._conflict = self._combo(CONFLICT_OPTIONS, self._settings.conflict_strategy)
        self._duplicates = self._combo(DUPLICATE_OPTIONS, self._settings.duplicate_handling)
        form.addRow("Default mode", self._default_mode)
        form.addRow("Conflict strategy", self._conflict)
        form.addRow("Duplicate handling", self._duplicates)
        self._tabs.addTab(page, "Organization")

    def _build_monitoring(self) -> None:
        page = QWidget()
        form = QFormLayout(page)
        self._watch_status = QLabel("Watching live for the selected main folder")
        self._watch_status.setObjectName("WatchStatus")
        self._debounce = QSpinBox()
        self._debounce.setRange(75, 1000)
        self._debounce.setSingleStep(25)
        self._debounce.setValue(min(self._settings.watchdog_debounce_ms, 150))
        self._batch = QCheckBox()
        self._batch.setChecked(self._settings.watchdog_batch_updates)
        form.addRow("Live watching", self._watch_status)
        form.addRow("Refresh delay", self._debounce)
        form.addRow("Group rapid events", self._batch)
        self._tabs.addTab(page, "Monitoring")

    def _build_appearance(self) -> None:
        page = QWidget()
        form = QFormLayout(page)
        self._accent = QComboBox()
        self._accent.addItem("System", "system")
        for color in ("#7c5cff", "#00c2a8", "#ff6b6b", "#ffcc66"):
            self._accent.addItem(color, color)
        index = self._accent.findData(self._settings.accent_color)
        self._accent.setCurrentIndex(max(index, 0))
        self._font_size = QSpinBox()
        self._font_size.setRange(11, 18)
        self._font_size.setValue(self._settings.font_size)
        self._compact = QCheckBox()
        self._compact.setChecked(self._settings.compact_mode)
        self._radius = QSpinBox()
        self._radius.setRange(6, 24)
        self._radius.setValue(self._settings.card_radius)
        form.addRow("Accent color", self._accent)
        form.addRow("Font size", self._font_size)
        form.addRow("Compact mode", self._compact)
        form.addRow("Card radius", self._radius)
        self._tabs.addTab(page, "Appearance")

    def _build_advanced(self) -> None:
        page = QWidget()
        form = QFormLayout(page)
        form.addRow("Database", QLabel("storage/app.db"))
        form.addRow("Logs", QLabel("storage/logs/file_organizer.log"))
        form.addRow("Export", QPushButton("Export History"))
        form.addRow("Reset", QPushButton("Reset Application Data"))
        self._tabs.addTab(page, "Advanced")

    def apply(self) -> None:
        self._settings.theme = self._theme.currentData()
        self._settings.animations_enabled = self._animations.isChecked()
        self._settings.notifications_enabled = self._notifications.isChecked()
        self._settings.startup_behavior = self._startup.currentText()
        self._settings.default_mode = self._default_mode.currentData()
        self._settings.recursive = False
        self._settings.conflict_strategy = self._conflict.currentData()
        self._settings.duplicate_handling = self._duplicates.currentData()
        self._settings.watchdog_enabled = True
        self._settings.auto_organize_downloads = True
        self._settings.watchdog_recursive = False
        self._settings.watchdog_debounce_ms = self._debounce.value()
        self._settings.watchdog_batch_updates = self._batch.isChecked()
        self._settings.accent_color = self._accent.currentData()
        self._settings.font_size = self._font_size.value()
        self._settings.compact_mode = self._compact.isChecked()
        self._settings.card_radius = self._radius.value()
        self._settings.save()
        self.settings_applied.emit(self._settings)

    def reload(self) -> None:
        self._settings = AppSettings.load()
        self.settings_applied.emit(self._settings)

    def _reset(self) -> None:
        self._settings = AppSettings()
        self._settings.save()
        self.settings_applied.emit(self._settings)
        self.reset_requested.emit()
