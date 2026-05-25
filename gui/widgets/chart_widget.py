"""Chart widgets backed by QtCharts with a graceful fallback."""

from __future__ import annotations

from PyQt6.QtCore import QMargins, Qt
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget

from models.stats_model import StatsSnapshot, format_bytes

try:
    from PyQt6.QtCharts import QBarCategoryAxis, QBarSeries, QBarSet, QChart, QChartView, QPieSeries, QValueAxis
    from PyQt6.QtGui import QPainter
except ImportError:  # pragma: no cover - optional in some PyQt distributions.
    QChart = None


class ChartWidget(QWidget):
    def __init__(self, title: str, chart_type: str) -> None:
        super().__init__()
        self.setObjectName("ChartPanel")
        self._title = title
        self._chart_type = chart_type
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(16, 16, 16, 16)
        self._layout.setSpacing(10)
        self._label = QLabel(title)
        self._label.setObjectName("PanelTitle")
        self._layout.addWidget(self._label)
        self._view: QChartView | QLabel
        if QChart is None:
            self._view = QLabel("QtCharts is not installed")
            self._view.setObjectName("EmptyState")
        else:
            chart = QChart()
            chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
            chart.setBackgroundVisible(False)
            chart.setMargins(QMargins(0, 0, 0, 0))
            chart.legend().setVisible(True)
            chart.legend().setAlignment(Qt.AlignmentFlag.AlignBottom)
            self._view = QChartView(chart)
            self._view.setRenderHint(QPainter.RenderHint.Antialiasing)
            self._view.setMinimumHeight(260)
        self._layout.addWidget(self._view, stretch=1)

    def update_snapshot(self, snapshot: StatsSnapshot) -> None:
        if QChart is None or isinstance(self._view, QLabel):
            return
        chart = self._view.chart()
        chart.removeAllSeries()
        for axis in chart.axes():
            chart.removeAxis(axis)
        chart.setTitle("")
        if self._chart_type == "pie":
            self._update_pie(chart, snapshot)
        elif self._chart_type == "bar":
            self._update_bar(chart, snapshot)
        else:
            self._update_savings(chart, snapshot)

    def _update_pie(self, chart: QChart, snapshot: StatsSnapshot) -> None:
        series = QPieSeries()
        for label, count in sorted(snapshot.files_by_type.items(), key=lambda item: item[1], reverse=True)[:5]:
            series.append(f"{label.title()} ({count})", count)
        if series.count() == 0:
            series.append("No files", 1)
        chart.addSeries(series)

    def _update_bar(self, chart: QChart, snapshot: StatsSnapshot) -> None:
        file_types = sorted(snapshot.files_by_type.items(), key=lambda item: item[1], reverse=True)[:5]
        categories = [name.title()[:14] for name, _ in file_types]
        values = QBarSet("Files")
        for _, count in file_types:
            values.append(count)
        if not file_types:
            values.append(0)
        series = QBarSeries()
        series.append(values)
        chart.addSeries(series)
        axis_x = QBarCategoryAxis()
        axis_x.append(categories or ["No files"])
        axis_y = QValueAxis()
        axis_y.setLabelFormat("%d")
        chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(axis_x)
        series.attachAxis(axis_y)

    def _update_savings(self, chart: QChart, snapshot: StatsSnapshot) -> None:
        series = QPieSeries()
        savings = max(snapshot.duplicate_savings_bytes, 1)
        used = max(snapshot.storage_bytes - snapshot.duplicate_savings_bytes, 1)
        series.append(f"Duplicate savings {format_bytes(snapshot.duplicate_savings_bytes)}", savings)
        series.append("Unique storage", used)
        chart.addSeries(series)
