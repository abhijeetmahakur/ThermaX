"""
Mini Line-Graph Widget using PyQtGraph for real-time performance.
"""

import pyqtgraph as pg
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore    import Qt
from PyQt5.QtGui     import QColor


class MiniGraph(QWidget):
    """
    Compact real-time line graph.
    Shows a rolling history of a single metric.
    """

    def __init__(self, color: str = "#00D4FF", y_max: float = 100,
                 label: str = "", fill: bool = True, parent=None):
        super().__init__(parent)
        self._color = color
        self._y_max = y_max
        self._fill  = fill

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Configure PyQtGraph
        pg.setConfigOption("background", "transparent")
        pg.setConfigOption("foreground", "#475569")
        pg.setConfigOption("antialias",  True)

        self._plot = pg.PlotWidget()
        self._plot.setBackground("transparent")
        self._plot.hideAxis("bottom")
        self._plot.hideAxis("left")
        self._plot.setYRange(0, y_max, padding=0)
        self._plot.setMouseEnabled(x=False, y=False)
        self._plot.setMenuEnabled(False)
        self._plot.showGrid(x=False, y=False)
        self._plot.setContentsMargins(0, 0, 0, 0)

        # Pen
        pen = pg.mkPen(color=QColor(color), width=2)
        self._curve = self._plot.plot(pen=pen)

        if fill:
            fill_color = QColor(color)
            fill_color.setAlphaF(0.15)
            self._curve.setFillLevel(0)
            self._curve.setBrush(pg.mkBrush(fill_color))

        layout.addWidget(self._plot)

    def update_data(self, data: list):
        x = list(range(len(data)))
        self._curve.setData(x, data)

    def set_color(self, color: str):
        self._color = color
        pen = pg.mkPen(color=QColor(color), width=2)
        self._curve.setPen(pen)
        if self._fill:
            fill_color = QColor(color)
            fill_color.setAlphaF(0.15)
            self._curve.setBrush(pg.mkBrush(fill_color))


class DualGraph(QWidget):
    """
    Two overlapping line graphs (e.g. download + upload).
    """

    def __init__(self, color1: str = "#00D4FF", color2: str = "#F472B6",
                 y_max: float = 10, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        pg.setConfigOption("background", "transparent")
        pg.setConfigOption("antialias",  True)

        self._plot = pg.PlotWidget()
        self._plot.setBackground("transparent")
        self._plot.hideAxis("bottom")
        self._plot.hideAxis("left")
        self._plot.setYRange(0, y_max, padding=0)
        self._plot.setMouseEnabled(x=False, y=False)
        self._plot.setMenuEnabled(False)
        self._plot.setContentsMargins(0, 0, 0, 0)

        pen1 = pg.mkPen(color=QColor(color1), width=2)
        pen2 = pg.mkPen(color=QColor(color2), width=2)

        self._curve1 = self._plot.plot(pen=pen1)
        self._curve2 = self._plot.plot(pen=pen2)

        fill1 = QColor(color1); fill1.setAlphaF(0.12)
        fill2 = QColor(color2); fill2.setAlphaF(0.12)
        self._curve1.setFillLevel(0); self._curve1.setBrush(pg.mkBrush(fill1))
        self._curve2.setFillLevel(0); self._curve2.setBrush(pg.mkBrush(fill2))

        layout.addWidget(self._plot)

    def update_data(self, data1: list, data2: list):
        n = max(len(data1), len(data2))
        self._curve1.setData(list(range(len(data1))), data1)
        self._curve2.setData(list(range(len(data2))), data2)
        peak = max(max(data1, default=1), max(data2, default=1), 1)
        self._plot.setYRange(0, peak * 1.2, padding=0)
