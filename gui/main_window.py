"""Modern PyQt6 application shell."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from PyQt6.QtCore import QDateTime, QPropertyAnimation, QThread, QTimer, Qt
from PyQt6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QGraphicsOpacityEffect
from config.constants import APP_ICON_PATH, APP_NAME, DARK_THEME_PATH, DEFAULT_WINDOW_HEIGHT, DEFAULT_WINDOW_WIDTH, LIGHT_THEME_PATH
from config.settings import AppSettings
from core.analytics_engine import AnalyticsEngine
from core.classifier import FileClassifier, OrganizationMode
from core.duplicate_cleaner import DuplicateCleaner, DuplicateCleanupSummary
from core.duplicate_detector import DuplicateDetector
from core.history_manager import HistoryManager
from core.mover import FileMover, MoveResult
from core.organizer import FileOrganizer, OrganizationPlan
from core.scanner import FileScanner
from gui.activity_panel import ActivityPanel
from gui.about_page import AboutPage
from gui.analytics import AnalyticsPage
from gui.dashboard import DashboardPage
from gui.history_page import HistoryPage
from gui.organize_page import OrganizePage
from gui.preview_page import PreviewPage
from gui.quarantine_page import QuarantinePage
from gui.settings_page import SettingsPage
from gui.sidebar import Sidebar
from gui.workers import OperationWorker
from services.folder_watcher import FolderWatcher, WatchEvent
from services.quarantine_service import QuarantineService
from services.undo_service import UndoService

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Primary desktop interface."""

    def __init__(self, settings: AppSettings) -> None:
        super().__init__()
        self.setWindowTitle(APP_NAME)
        if APP_ICON_PATH.exists():
            self.setWindowIcon(QIcon(str(APP_ICON_PATH)))
        self.resize(DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT)
        self.setMinimumSize(1080, 720)
        self._settings = settings
        self._history_manager = HistoryManager()
        self._worker_thread: QThread | None = None
        self._worker: OperationWorker | None = None
        self._watcher_thread: QThread | None = None
        self._watcher: FolderWatcher | None = None
        self._last_plans: list[OrganizationPlan] = []
        self._running_task: str | None = None
        self._live_refresh_pending = False
        # Track last applied resolved theme/accent to avoid unnecessary reflows
        self._last_resolved_accent: str | None = None
        self._last_resolved_theme: str | None = None
        self._theme_poll_timer = QTimer(self)
        self._theme_poll_timer.setInterval(2000)
        self._theme_poll_timer.timeout.connect(self._refresh_system_theme)

        self._sidebar = Sidebar()
        self._stack = QStackedWidget()
        self._activity = ActivityPanel()
        self._dashboard = DashboardPage()
        self._organize = OrganizePage(settings.default_mode)
        self._preview = PreviewPage()
        self._quarantine = QuarantinePage()
        self._analytics = AnalyticsPage()
        self._history = HistoryPage(self._history_manager)
        self._settings_page = SettingsPage(settings)
        self._about_page = AboutPage()
        self._pages = {
            "dashboard": self._dashboard,
            "organize": self._organize,
            "preview": self._preview,
            "quarantine": self._quarantine,
            "analytics": self._analytics,
            "history": self._history,
            "settings": self._settings_page,
            "about": self._about_page,
        }
        for page in self._pages.values():
            self._stack.addWidget(page)

        self._folder_caption = QLabel("Main folder")
        self._folder_caption.setObjectName("FolderCaption")
        self._folder_path = QLabel(self._folder_path_text())
        self._folder_path.setObjectName("FolderPath")
        self._folder_path.setToolTip(str(self._settings.default_folder))
        self._folder_button = QPushButton("Choose folder")
        self._folder_button.setObjectName("FolderSelector")
        self._folder_button.setToolTip("Select the main folder to organize. Subfolders are not scanned.")
        self._folder_button.clicked.connect(self._choose_folder)
        self._watch_status = QLabel("Starting watcher")
        self._watch_status.setObjectName("WatchStatus")
        self._watch_status.setProperty("state", "starting")
        self._watch_status.setMinimumWidth(150)
        self._watch_status_frames = ["|", "/", "-", "\\"]
        self._watch_status_index = 0
        self._watch_status_base = "Watching live"
        self._watch_status_timer = QTimer(self)
        self._watch_status_timer.setInterval(160)
        self._watch_status_timer.timeout.connect(self._tick_watch_status)
        self._search = QLineEdit()
        self._search.setPlaceholderText("Search")
        self._search.textChanged.connect(self._preview.findChild(QLineEdit).setText)
        self._progress = QProgressBar()
        self._progress.setRange(0, 100)
        self._progress.setFixedWidth(180)
        self._progress.setVisible(False)
        self._progress.setTextVisible(False)
        self._last_scan = QLabel("Last scan: never")
        self._last_scan.setObjectName("LastScan")

        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(18, 12, 18, 12)
        top_bar.setSpacing(14)
        folder_info = QVBoxLayout()
        folder_info.setContentsMargins(0, 0, 0, 0)
        folder_info.setSpacing(2)
        folder_info.addWidget(self._folder_caption)
        folder_info.addWidget(self._folder_path)
        top_bar.addLayout(folder_info)
        top_bar.addWidget(self._folder_button)
        top_bar.addWidget(self._watch_status)
        top_bar.addStretch()
        top_bar.addWidget(self._search)
        top_bar.addWidget(self._progress)
        top_bar.addWidget(self._last_scan)

        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)
        body.addWidget(self._sidebar)
        body.addWidget(self._stack, stretch=1)
        body.addWidget(self._activity)

        root = QWidget()
        root.setObjectName("Root")
        layout = QVBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addLayout(top_bar)
        layout.addLayout(body, stretch=1)
        self.setCentralWidget(root)

        self._toast = QFrame(root)
        self._toast.setObjectName("ToastNotification")
        self._toast.setFrameShape(QFrame.Shape.NoFrame)
        self._toast.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self._toast.setFixedWidth(360)
        self._toast.setVisible(False)
        self._toast_title = QLabel("Notification")
        self._toast_title.setObjectName("ToastTitle")
        self._toast_body = QLabel("")
        self._toast_body.setObjectName("ToastBody")
        self._toast_body.setWordWrap(True)
        toast_layout = QVBoxLayout(self._toast)
        toast_layout.setContentsMargins(16, 14, 16, 14)
        toast_layout.setSpacing(6)
        toast_layout.addWidget(self._toast_title)
        toast_layout.addWidget(self._toast_body)
        self._toast_opacity = QGraphicsOpacityEffect(self._toast)
        self._toast.setGraphicsEffect(self._toast_opacity)
        self._toast_opacity.setOpacity(0.0)
        self._toast_animation = QPropertyAnimation(self._toast_opacity, b"opacity", self)
        self._toast_animation.setDuration(220)
        self._toast_animation.finished.connect(self._on_toast_animation_finished)
        self._toast_hide_timer = QTimer(self)
        self._toast_hide_timer.setSingleShot(True)
        self._toast_hide_timer.timeout.connect(self._begin_toast_hide)
        self._toast_pending_hide = False
        self._position_toast()

        self._connect_signals()
        self._apply_theme()
        self._sync_theme_polling()
        self._start_watcher()
        self._run_operation("refresh")

    def closeEvent(self, event: object) -> None:
        self._stop_watcher()
        if self._worker:
            self._worker.cancel()
        event.accept()

    def resizeEvent(self, event: object) -> None:
        super().resizeEvent(event)
        self._position_toast()

    def _connect_signals(self) -> None:
        self._sidebar.page_selected.connect(self._select_page)
        self._dashboard.action_requested.connect(self._quick_action)
        self._organize.preview_requested.connect(lambda: self._run_operation("preview"))
        self._organize.organize_requested.connect(lambda: self._run_operation("organize"))
        self._organize.mode_changed.connect(self._mode_changed)
        self._preview.preview_requested.connect(lambda: self._run_operation("preview"))
        self._preview.organize_requested.connect(lambda: self._run_operation("organize"))
        self._quarantine.restore_requested.connect(self._restore_quarantined)
        self._quarantine.delete_requested.connect(self._delete_quarantined)
        self._settings_page.settings_applied.connect(self._settings_applied)

        from PyQt6.QtGui import QGuiApplication
        app = QGuiApplication.instance()
        if app:
            app.styleHints().colorSchemeChanged.connect(self._on_color_scheme_changed)

    def _select_page(self, page_id: str) -> None:
        self._stack.setCurrentWidget(self._pages[page_id])
        if page_id == "history":
            self._history.refresh()
        if page_id == "quarantine":
            self._refresh_quarantine()

    def _quick_action(self, action_id: str) -> None:
        if action_id == "undo":
            if self._confirm_action(
                "Undo last action?",
                "This will restore files from the latest completed action.",
                "Undo",
            ):
                self._run_operation("undo")
            return
        if action_id == "remove_duplicates":
            if self._confirm_action(
                "Remove duplicate files?",
                "Duplicate copies will be moved to quarantine. The likely original copy will be kept.",
                "Remove duplicates",
            ):
                self._run_operation("remove_duplicates")
            return
        if action_id == "auto":
            self._settings.watchdog_enabled = True
            self._settings.auto_organize_downloads = True
            self._settings.save()
            self._start_watcher()
            self._schedule_live_refresh("Live organizer is watching this folder")
            return
        self._organize.set_mode(action_id)
        self._sidebar.select("organize")
        self.statusBar().showMessage("Mode selected. Use Preview or Start Organizing to continue.")

    def _confirm_action(self, title: str, message: str, accept_label: str) -> bool:
        dialog = QMessageBox(self)
        dialog.setIcon(QMessageBox.Icon.Question)
        dialog.setWindowTitle(title)
        dialog.setText(title)
        dialog.setInformativeText(message)
        dialog.setStandardButtons(QMessageBox.StandardButton.Cancel | QMessageBox.StandardButton.Yes)
        dialog.button(QMessageBox.StandardButton.Yes).setText(accept_label)
        dialog.setDefaultButton(QMessageBox.StandardButton.Cancel)
        return dialog.exec() == QMessageBox.StandardButton.Yes

    def _choose_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Select folder", str(self._settings.default_folder))
        if not folder:
            return
        self._settings.default_folder = Path(folder)
        self._settings.save()
        self._folder_path.setText(self._folder_path_text())
        self._folder_path.setToolTip(str(self._settings.default_folder))
        self._activity.add_activity("Folder", str(self._settings.default_folder))
        self._notify_success(f"Main folder set to {self._settings.default_folder.name or self._settings.default_folder}")
        self._restart_watcher()
        self._schedule_live_refresh("Main folder changed")

    def _folder_path_text(self) -> str:
        path = str(self._settings.default_folder)
        return path if len(path) <= 48 else f"...{path[-45:]}"

    def _mode_changed(self, mode: str) -> None:
        self._settings.default_mode = mode
        self._settings.save()

    def _settings_applied(self, settings: AppSettings) -> None:
        self._settings = settings
        self._apply_theme()
        self._sync_theme_polling()
        self._folder_path.setText(self._folder_path_text())
        self._folder_path.setToolTip(str(self._settings.default_folder))
        self._notify_success("Settings applied")
        self._restart_watcher()
        self._schedule_live_refresh("Settings applied")

    def _build_services(self) -> tuple[FileOrganizer, UndoService, AnalyticsEngine, DuplicateCleaner]:
        scanner = FileScanner(ignore_hidden=self._settings.ignore_hidden)
        classifier = FileClassifier(self._settings.custom_rules)
        detector = DuplicateDetector()
        mover = FileMover(detector)
        organizer = FileOrganizer(scanner, classifier, mover, self._history_manager)
        undo_service = UndoService(self._history_manager, mover)
        analytics = AnalyticsEngine(FileScanner(ignore_hidden=self._settings.ignore_hidden))
        duplicate_cleaner = DuplicateCleaner(
            FileScanner(ignore_hidden=self._settings.ignore_hidden),
            detector,
            mover,
            self._history_manager,
        )
        return organizer, undo_service, analytics, duplicate_cleaner

    def _run_operation(self, task: str) -> None:
        if self._worker_thread is not None:
            if task == "refresh":
                self._live_refresh_pending = True
                self.statusBar().showMessage("Refresh queued")
            else:
                self.statusBar().showMessage("An operation is already running.")
            return
        organizer, undo_service, analytics, duplicate_cleaner = self._build_services()
        self._worker_thread = QThread(self)
        self._running_task = task
        self._set_operation_busy(True)
        self._notify_info(f"{self._operation_label(task)} started")
        self._worker = OperationWorker(
            task=task,
            organizer=organizer,
            undo_service=undo_service,
            analytics_engine=analytics,
            duplicate_cleaner=duplicate_cleaner,
            directory=self._settings.default_folder,
            mode=self._organize.mode(),
            recursive=False,
        )
        self._worker.moveToThread(self._worker_thread)
        self._worker_thread.started.connect(self._worker.run)
        self._worker.progress.connect(self._update_progress)
        self._worker.preview_ready.connect(self._preview_ready)
        self._worker.stats_ready.connect(self._stats_ready)
        self._worker.finished.connect(self._operation_finished)
        self._worker.failed.connect(self._operation_failed)
        self._worker.finished.connect(self._worker_thread.quit)
        self._worker.failed.connect(self._worker_thread.quit)
        self._worker_thread.finished.connect(self._cleanup_worker)
        self._progress.setValue(0)
        self._worker_thread.start()

    def _update_progress(self, current: int, total: int, path: str) -> None:
        self._progress.setVisible(True)
        self._progress.setRange(0, 100)
        self._progress.setValue(int(current / total * 100) if total else 0)
        self.statusBar().showMessage(f"Processing {Path(path).name}")

    def _preview_ready(self, plans: list[OrganizationPlan]) -> None:
        self._last_plans = plans
        self._preview.set_plans(plans)
        if self._running_task != "refresh":
            self._stack.setCurrentWidget(self._preview)
            self._activity.add_activity("Preview", f"{len(plans):,} planned actions")

    def _stats_ready(self, snapshot: object) -> None:
        self._dashboard.update_stats(snapshot)
        self._analytics.update_stats(snapshot)
        self._refresh_quarantine()
        self._last_scan.setText(f"Last scan: {QDateTime.currentDateTime().toString('HH:mm:ss')}")

    def _operation_finished(self, task: str, payload: list[Any]) -> None:
        self._progress.setValue(100)
        if task == "preview":
            self._activity.add_activity("Preview", f"{len(payload):,} planned actions")
            self._notify_success(f"Preview ready: {len(payload):,} planned action{'s' if len(payload) != 1 else ''}")
            self.statusBar().showMessage("Preview ready")
        if task == "organize":
            moved = sum(1 for item in payload if isinstance(item, MoveResult) and item.success and item.action == "moved")
            errors = sum(1 for item in payload if isinstance(item, MoveResult) and not item.success)
            self._activity.add_activity("Moved", f"{moved:,} files organized, {errors:,} errors")
            self._history.refresh()
            if errors:
                self._notify_warning(f"Organizing finished with {errors} error{'s' if errors != 1 else ''}")
            else:
                self._notify_success(f"Organized {moved} file{'s' if moved != 1 else ''}")
            self.statusBar().showMessage(f"Done. Moved {moved} files. Errors: {errors}")
        elif task == "undo":
            restored = sum(1 for item in payload if isinstance(item, MoveResult) and item.success)
            self._activity.add_activity("Undo", f"{restored:,} files restored")
            self._history.refresh()
            self._notify_success(f"Restored {restored} file{'s' if restored != 1 else ''}")
            self.statusBar().showMessage("Undo complete")
        elif task == "remove_duplicates":
            summary = payload[0] if payload and isinstance(payload[0], DuplicateCleanupSummary) else None
            removed = summary.removed if summary else 0
            saved = summary.bytes_saved if summary else 0
            errors = sum(1 for result in summary.results if not result.success) if summary else 0
            self._activity.add_activity("Duplicates removed", f"{removed:,} files quarantined, {errors:,} errors")
            self._history.refresh()
            self._refresh_quarantine()
            if errors:
                self._notify_warning(f"Duplicate cleanup finished with {errors} error{'s' if errors != 1 else ''}")
            else:
                self._notify_success(f"Quarantined {removed} duplicate file{'s' if removed != 1 else ''}")
            self.statusBar().showMessage(f"Removed {removed} duplicate files. Recovered {saved:,} bytes.")
            self._schedule_live_refresh("Duplicate cleanup complete")
        elif task == "stats":
            self._activity.add_activity("Stats", "Folder statistics refreshed")
            self._notify_success("Statistics refreshed")
            self.statusBar().showMessage("Stats updated")
        elif task == "refresh":
            self._activity.add_activity("Refresh", "Live preview updated")
            self._notify_success("Live refresh complete")
            self.statusBar().showMessage("Live refresh complete")
        self._set_operation_busy(False)

    def _operation_failed(self, message: str) -> None:
        logger.error("Operation failed: %s", message)
        if self._running_task:
            self._activity.add_activity("Failed", f"{self._operation_label(self._running_task)}: {message}")
        self._set_operation_busy(False)
        self._notify_error(message)
        QMessageBox.critical(self, "Operation failed", message)

    def _cleanup_worker(self) -> None:
        if self._worker:
            self._worker.deleteLater()
        if self._worker_thread:
            self._worker_thread.deleteLater()
        self._worker = None
        self._worker_thread = None
        self._running_task = None
        self._set_operation_busy(False)
        if self._live_refresh_pending:
            self._live_refresh_pending = False
            QTimer.singleShot(0, lambda: self._run_operation("refresh"))

    def _set_operation_busy(self, busy: bool) -> None:
        self._progress.setVisible(busy)
        if busy:
            self._progress.setRange(0, 0)
        else:
            self._progress.setRange(0, 100)
            self._progress.setValue(0)

    def _notify_info(self, message: str, timeout_ms: int = 3500) -> None:
        self._show_notification(message, "info", timeout_ms)

    def _notify_success(self, message: str, timeout_ms: int = 3500) -> None:
        self._show_notification(message, "success", timeout_ms)

    def _notify_warning(self, message: str, timeout_ms: int = 4500) -> None:
        self._show_notification(message, "warning", timeout_ms)

    def _notify_error(self, message: str, timeout_ms: int = 6500) -> None:
        self._show_notification(message, "error", timeout_ms)

    def _show_notification(self, message: str, state: str, timeout_ms: int) -> None:
        if state != "error" and not self._settings.notifications_enabled:
            return
        self._toast_hide_timer.stop()
        self._toast_pending_hide = False
        self._toast.setProperty("state", state)
        self._toast_title.setText({"info": "Started", "success": "Completed", "warning": "Completed with issues", "error": "Failed"}.get(state, "Notification"))
        self._toast_body.setText(message)
        self._toast.style().unpolish(self._toast)
        self._toast.style().polish(self._toast)
        self._toast.update()
        self._position_toast()
        self._toast.setVisible(True)
        self._toast.raise_()
        self._toast_opacity.setOpacity(0.0)
        self._toast_animation.stop()
        self._toast_animation.setStartValue(0.0)
        self._toast_animation.setEndValue(1.0)
        self._toast_animation.start()
        if timeout_ms > 0:
            self._toast_hide_timer.start(timeout_ms)

    def _begin_toast_hide(self) -> None:
        if not self._toast.isVisible():
            return
        self._toast_pending_hide = True
        self._toast_animation.stop()
        self._toast_animation.setStartValue(self._toast_opacity.opacity())
        self._toast_animation.setEndValue(0.0)
        self._toast_animation.start()

    def _on_toast_animation_finished(self) -> None:
        if self._toast_pending_hide:
            self._toast_pending_hide = False
            self._toast.setVisible(False)

    def _position_toast(self) -> None:
        if not hasattr(self, "_toast"):
            return
        root = self.centralWidget()
        if root is None:
            return
        margin = 18
        self._toast.adjustSize()
        x = max(margin, root.width() - self._toast.width() - margin)
        y = margin
        self._toast.move(x, y)

    @staticmethod
    def _operation_label(task: str) -> str:
        labels = {
            "preview": "Preview",
            "organize": "Organizing files",
            "undo": "Undo",
            "remove_duplicates": "Duplicate cleanup",
            "stats": "Stats refresh",
            "refresh": "Live refresh",
        }
        return labels.get(task, task.replace("_", " ").title())

    def _start_watcher(self) -> None:
        self._stop_watcher()
        self._watcher_thread = QThread(self)
        self._watcher = FolderWatcher(
            self._settings.default_folder,
            recursive=False,
            debounce_ms=min(self._settings.watchdog_debounce_ms, 150),
        )
        self._watcher.moveToThread(self._watcher_thread)
        self._watcher_thread.started.connect(self._watcher.start)
        self._watcher.file_created.connect(lambda path: self._activity.add_activity("Created", Path(path).name))
        self._watcher.file_deleted.connect(lambda path: self._activity.add_activity("Deleted", Path(path).name))
        self._watcher.file_modified.connect(lambda path: self._activity.add_activity("Modified", Path(path).name))
        self._watcher.file_moved.connect(lambda old, new: self._activity.add_activity("Moved", f"{Path(old).name} -> {Path(new).name}"))
        self._watcher.batch_ready.connect(self._watch_batch)
        self._watcher.status_changed.connect(self._update_watch_status)
        self._watcher_thread.start()
        self._update_watch_status("Live watching")

    def _stop_watcher(self) -> None:
        if self._watcher is not None:
            self._watcher.stop()
            self._watcher.deleteLater()
            self._watcher = None
        if self._watcher_thread is not None:
            self._watcher_thread.quit()
            self._watcher_thread.wait(3000)
            self._watcher_thread.deleteLater()
            self._watcher_thread = None
        self._watch_status_timer.stop()
        self._watch_status.setProperty("state", "idle")
        self._watch_status.setText("Not watching")
        self._watch_status.style().unpolish(self._watch_status)
        self._watch_status.style().polish(self._watch_status)
        self._watch_status.update()

    def _update_watch_status(self, message: str) -> None:
        if message == "Live watching":
            self._watch_status_base = "Watching live"
            self._watch_status_index = 0
            self._watch_status.setProperty("state", "live")
            self._watch_status_timer.start()
            self._tick_watch_status()
        elif message == "Not watching":
            self._watch_status_timer.stop()
            self._watch_status.setProperty("state", "idle")
            self._watch_status.setText("Not watching")
        elif message == "Watch error":
            self._watch_status_timer.stop()
            self._watch_status.setProperty("state", "error")
            self._watch_status.setText("Watch error")
        else:
            self._watch_status_base = message
            self._watch_status.setProperty("state", "live")
            self._watch_status_timer.start()
            self._tick_watch_status()
        self._watch_status.style().unpolish(self._watch_status)
        self._watch_status.style().polish(self._watch_status)
        self._watch_status.update()

    def _tick_watch_status(self) -> None:
        if self._watch_status.property("state") != "live":
            return
        frame = self._watch_status_frames[self._watch_status_index % len(self._watch_status_frames)]
        self._watch_status.setText(f"{self._watch_status_base} {frame}")
        self._watch_status_index = (self._watch_status_index + 1) % len(self._watch_status_frames)

    def _restart_watcher(self) -> None:
        self._start_watcher()

    def _watch_batch(self, events: list[WatchEvent]) -> None:
        if self._settings.watchdog_batch_updates:
            self._activity.add_activity("Folder changed", f"{len(events)} update{'s' if len(events) != 1 else ''} detected")
        self._schedule_live_refresh("Folder change detected")

    def _schedule_live_refresh(self, message: str) -> None:
        self.statusBar().showMessage(message)
        if self._worker_thread is not None:
            self._live_refresh_pending = True
            return
        QTimer.singleShot(0, lambda: self._run_operation("refresh"))

    def _quarantine_service(self) -> QuarantineService:
        return QuarantineService(self._history_manager, FileMover(DuplicateDetector()))

    def _refresh_quarantine(self) -> None:
        self._quarantine.set_items(self._quarantine_service().list_items())

    def _restore_quarantined(self, item: object) -> None:
        if not self._confirm_action(
            "Restore quarantined file?",
            "This will move the duplicate copy back to its original location.",
            "Restore",
        ):
            return
        result = self._quarantine_service().restore(item)
        if result.success:
            self._activity.add_activity("Restored", result.destination.name)
        else:
            QMessageBox.warning(self, "Restore failed", result.error or "Could not restore this file.")
        self._refresh_quarantine()
        self._schedule_live_refresh("Quarantine updated")

    def _delete_quarantined(self, item: object) -> None:
        if not self._confirm_action(
            "Delete quarantined file permanently?",
            "This cannot be undone from inside the app.",
            "Delete",
        ):
            return
        if self._quarantine_service().delete_permanently(item):
            self._activity.add_activity("Deleted", item.quarantine_path.name)
        else:
            QMessageBox.warning(self, "Delete failed", "Could not delete this quarantined file.")
        self._refresh_quarantine()
        self._schedule_live_refresh("Quarantine updated")

    def _resolve_theme(self, theme: str) -> str:
        if theme == "system":
            from PyQt6.QtGui import QGuiApplication
            from PyQt6.QtCore import Qt
            app = QGuiApplication.instance()
            if app:
                color_scheme = app.styleHints().colorScheme()
                if color_scheme == Qt.ColorScheme.Dark:
                    return "dark"
                elif color_scheme == Qt.ColorScheme.Light:
                    return "light"
            return "dark"  # Default fallback
        return theme

    def _resolve_accent_color(self, accent: str) -> str:
        if accent == "system":
            from PyQt6.QtGui import QGuiApplication, QPalette
            app = QGuiApplication.instance()
            if app:
                color = app.palette().color(QPalette.ColorRole.Highlight)
                if color.isValid():
                    return color.name()
            return "#7c5cff"  # Default fallback
        return accent

    def _accent_tokens(self, accent: str) -> dict[str, str]:
        from PyQt6.QtGui import QColor

        color = QColor(accent)
        if not color.isValid():
            color = QColor("#7c5cff")

        def relative_luminance(qcolor: QColor) -> float:
            def channel(value: int) -> float:
                normalized = value / 255.0
                return normalized / 12.92 if normalized <= 0.03928 else ((normalized + 0.055) / 1.055) ** 2.4

            red = channel(qcolor.red())
            green = channel(qcolor.green())
            blue = channel(qcolor.blue())
            return 0.2126 * red + 0.7152 * green + 0.0722 * blue

        def contrast_ratio(first: QColor, second: QColor) -> float:
            first_luminance = relative_luminance(first)
            second_luminance = relative_luminance(second)
            lighter = max(first_luminance, second_luminance)
            darker = min(first_luminance, second_luminance)
            return (lighter + 0.05) / (darker + 0.05)

        lightness = color.lightness()
        hover = color.darker(118) if lightness > 128 else color.lighter(118)
        soft = QColor(color)
        soft.setAlpha(36)
        strong = QColor(color)
        strong.setAlpha(56)
        black = QColor("#1a1c1e")
        white = QColor("#ffffff")
        foreground = black.name() if contrast_ratio(color, black) >= contrast_ratio(color, white) else white.name()

        return {
            "accent": color.name(),
            "accent_hover": hover.name(),
            "accent_soft": f"rgba({soft.red()}, {soft.green()}, {soft.blue()}, {soft.alpha()})",
            "accent_soft_strong": f"rgba({strong.red()}, {strong.green()}, {strong.blue()}, {strong.alpha()})",
            "accent_foreground": foreground,
        }

    def _on_color_scheme_changed(self, scheme: Any = None) -> None:
        if self._settings.theme == "system" or self._settings.accent_color == "system":
            self._apply_theme()

    def _sync_theme_polling(self) -> None:
        if self._settings.theme == "system" or self._settings.accent_color == "system":
            if not self._theme_poll_timer.isActive():
                self._theme_poll_timer.start()
        elif self._theme_poll_timer.isActive():
            self._theme_poll_timer.stop()

    def _refresh_system_theme(self) -> None:
        if self._settings.theme != "system" and self._settings.accent_color != "system":
            return

        resolved_theme = self._resolve_theme(self._settings.theme)
        resolved_accent = self._resolve_accent_color(self._settings.accent_color)
        if resolved_theme != self._last_resolved_theme or resolved_accent != self._last_resolved_accent:
            self._apply_theme()

    def _apply_theme(self) -> None:
        from gui.icons import set_theme as set_icons_theme
        
        resolved_theme = self._resolve_theme(self._settings.theme)
        resolved_accent = self._resolve_accent_color(self._settings.accent_color)
        accent_tokens = self._accent_tokens(resolved_accent)
        
        # Update icon theme first
        set_icons_theme(resolved_theme)
        
        # Then apply CSS
        path = LIGHT_THEME_PATH if resolved_theme == "light" else DARK_THEME_PATH
        if path.exists():
            style = path.read_text(encoding="utf-8")
            style = style.replace("@font_size", f"{self._settings.font_size}px")
            # Replace longer/more specific tokens first to avoid partial
            # substitution (e.g. replacing @accent before @accent_hover)
            style = style.replace("@accent_soft_strong", accent_tokens["accent_soft_strong"])
            style = style.replace("@accent_soft", accent_tokens["accent_soft"])
            style = style.replace("@accent_hover", accent_tokens["accent_hover"])
            style = style.replace("@accent_foreground", accent_tokens["accent_foreground"])
            style = style.replace("@accent", accent_tokens["accent"])
            style = style.replace("@radius", f"{self._settings.card_radius}px")
            self.setStyleSheet(style)

        # Remember what we applied so we can skip redundant reflows
        self._last_resolved_accent = resolved_accent
        self._last_resolved_theme = resolved_theme

        # Refresh sidebar icons with new theme colors
        self._sidebar.refresh_icons()
        self._dashboard.refresh_icons()
        self._organize.refresh_icons()
