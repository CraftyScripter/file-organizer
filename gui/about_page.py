"""About page for the application."""

from __future__ import annotations

from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget


class AboutPage(QWidget):
    def __init__(self) -> None:
        super().__init__()

        title = QLabel("About Developer")
        title.setObjectName("PageTitle")

        intro = QLabel(
            "Hi, I'm Anuj — a developer passionate about building useful software and solving real-world problems through code. "
            "I enjoy creating reliable and efficient applications with a strong focus on backend development, automation, data extraction, and productivity tools."
        )
        intro.setWordWrap(True)

        project = QLabel(
            "This app was created with the idea of making everyday tasks simpler, faster, and more organized. "
            "I believe software should feel clean, easy to use, and actually help people instead of adding complexity."
        )
        project.setWordWrap(True)

        growth = QLabel(
            "I continuously work on improving performance, refining the user experience, and introducing meaningful features over time. "
            "Every update is focused on making the app more useful, polished, and enjoyable to use."
        )
        growth.setWordWrap(True)

        work_title = QLabel("What I Enjoy Building")
        work_title.setObjectName("PanelTitle")

        work_items = QLabel(
            "• Backend Systems\n"
            "• Automation Tools\n"
            "• Web Data Extraction\n"
            "• Productivity Applications\n"
            "• Scalable Software Solutions"
        )
        work_items.setWordWrap(True)

        connect_title = QLabel("Connect With Me")
        connect_title.setObjectName("PanelTitle")

        thanks = QLabel("Thank you for using this app ❤️")
        thanks.setObjectName("PageHelper")

        card = QFrame()
        card.setObjectName("AboutCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(14)
        card_layout.addWidget(title)
        card_layout.addWidget(intro)
        card_layout.addWidget(project)
        card_layout.addWidget(growth)
        card_layout.addWidget(work_title)
        card_layout.addWidget(work_items)
        card_layout.addWidget(connect_title)
        card_layout.addWidget(thanks)

        github = self._link_button("GitHub", "https://github.com/CraftyScripter")
        linkedin = self._link_button("LinkedIn", "https://www.linkedin.com/in/anuj-kumar-04594629b/")

        socials = QHBoxLayout()
        socials.setSpacing(12)
        socials.addWidget(github)
        socials.addWidget(linkedin)
        socials.addStretch()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(18)
        layout.addWidget(card)
        layout.addLayout(socials)
        layout.addStretch()

    def _link_button(self, label: str, url: str) -> QPushButton:
        button = QPushButton(label)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(url)))
        return button