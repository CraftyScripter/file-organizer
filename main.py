"""Application entry point."""

from __future__ import annotations

import sys

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication

from config.constants import APP_ICON_PATH
from config.settings import AppSettings, configure_logging
from gui.main_window import MainWindow


def main() -> int:
    configure_logging()
    settings = AppSettings.load()
    app = QApplication(sys.argv)
    if APP_ICON_PATH.exists():
        app.setWindowIcon(QIcon(str(APP_ICON_PATH)))
    window = MainWindow(settings)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
