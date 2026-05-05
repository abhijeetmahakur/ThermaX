"""
Circular Gauge Widget
Draws an arc-based gauge with animated value transitions.
"""

import math
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore    import Qt, QRectF, QPropertyAnimation, pyqtProperty
from PyQt5.QtGui     import (QPainter, QColor, QPen, QFont, QLinearGradient,
                              QConicalGradient, QRadialGradient, QBrush)


class CircularGauge(QWidget):
    """
    Animated circular gauge.
    Shows value (0–100) as a coloured arc with neon glow.
    """

    def __init__(self, title: str = "", unit: str = "%",
                 color: str = "#00D4FF", bg_color: str = "#111827",
                 size: int = 180, parent=None):
        super().__init__(parent)
        self._title    = title
        self._unit     = unit
        self._color    = QColor(color)
        self._bg_color = QColor(bg_color)
        self._value    = 0.0
        self._target   = 0.0
        self._anim_val = 0.0
        self._sub_text = ""

        self.setFixedSize(size, size)
        self.setMinimumSize(size, size)

        # Smooth animation
        self._anim = QPropertyAnimation(self, b"anim_value", self)
        self._anim.setDuration(600)

    # ── Animated property ──────────────────────────────────────────
    def get_anim_value(self): return self._anim_val
    def set_anim_value(self, v):
        self._anim_val = v
        self.update()
    anim_value = pyqtProperty(float, get_anim_value, set_anim_value)

    # ── Public API ─────────────────────────────────────────────────
    def set_value(self, value: float, sub_text: str = ""):
        value = max(0.0, min(100.0, value))
        self._target   = value
        self._sub_text = sub_text
        self._anim.stop()
        self._anim.setStartValue(self._anim_val)
        self._anim.setEndValue(value)
        self._anim.start()

    def set_color(self, color: str):
        self._color = QColor(color)
        self.update()

    # ── Painting ───────────────────────────────────────────────────
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()
        cx, cy = w / 2, h / 2
        margin = int(w * 0.10)
        rect   = QRectF(margin, margin, w - 2*margin, h - 2*margin)

        # Start/span angles (Qt: 0=3 o'clock, CCW positive)
        start_angle = 225   # bottom-left
        span_angle  = -270  # clockwise sweep of 270°

        # ── Background track ──
        pen = QPen(QColor(30, 40, 60), int(w * 0.06))
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        painter.drawArc(rect,
                        int(start_angle * 16),
                        int(span_angle  * 16))

        # ── Coloured value arc ──
        pct  = self._anim_val / 100.0
        fill = span_angle * pct

        pen2 = QPen(self._color, int(w * 0.055))
        pen2.setCapStyle(Qt.RoundCap)
        painter.setPen(pen2)
        painter.drawArc(rect,
                        int(start_angle * 16),
                        int(fill * 16))

        # ── Glow effect (second, thinner lighter arc) ──
        glow_color = QColor(self._color)
        glow_color.setAlphaF(0.25)
        pen3 = QPen(glow_color, int(w * 0.10))
        pen3.setCapStyle(Qt.RoundCap)
        painter.setPen(pen3)
        painter.drawArc(rect,
                        int(start_angle * 16),
                        int(fill * 16))

        # ── Center text – value ──
        font = QFont("Segoe UI", int(w * 0.17), QFont.Bold)
        painter.setFont(font)
        painter.setPen(QColor(226, 232, 240))
        val_str = f"{int(self._anim_val)}"
        painter.drawText(QRectF(0, cy - h*0.22, w, h*0.30),
                         Qt.AlignCenter, val_str)

        # ── Unit ──
        font2 = QFont("Segoe UI", int(w * 0.095))
        painter.setFont(font2)
        painter.setPen(self._color)
        painter.drawText(QRectF(0, cy + h*0.02, w, h*0.16),
                         Qt.AlignCenter, self._unit)

        # ── Sub-text (e.g. temperature or freq) ──
        if self._sub_text:
            font3 = QFont("Segoe UI", int(w * 0.075))
            painter.setFont(font3)
            painter.setPen(QColor(148, 163, 184))
            painter.drawText(QRectF(0, cy + h*0.16, w, h*0.14),
                             Qt.AlignCenter, self._sub_text)

        # ── Title below gauge ──
        font4 = QFont("Segoe UI", int(w * 0.082), QFont.DemiBold)
        painter.setFont(font4)
        painter.setPen(QColor(148, 163, 184))
        painter.drawText(QRectF(0, h - int(h*0.22), w, int(h*0.22)),
                         Qt.AlignCenter, self._title)

        painter.end()
