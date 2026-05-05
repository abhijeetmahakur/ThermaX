"""
Reusable styled UI widgets:
  - StatCard          : metric display card with icon + value
  - SectionTitle      : styled section heading
  - GlowButton        : neon-glow push button
  - ModeButton        : toggle button for performance mode selection
  - AlertBanner       : slide-in alert notification
  - ProgressBar       : styled horizontal progress bar
  - SidebarButton     : icon + label navigation button
"""

from PyQt5.QtWidgets import (QWidget, QLabel, QVBoxLayout, QHBoxLayout,
                              QPushButton, QFrame, QSizePolicy, QProgressBar,
                              QGraphicsDropShadowEffect)
from PyQt5.QtCore    import Qt, QTimer, QPropertyAnimation, pyqtSignal, QSize
from PyQt5.QtGui     import QColor, QFont, QIcon, QPainter, QBrush, QPen


# ─────────────────────────── StatCard ─────────────────────────────────────────
class StatCard(QWidget):
    """
    Glass-morphism stat card.
    Shows an icon, metric title, large value and optional subtitle.
    """

    def __init__(self, title: str, icon: str = "●",
                 color: str = "#00D4FF", parent=None):
        super().__init__(parent)
        self._color = color
        self._setup_ui(title, icon, color)
        self._apply_style(color)

    def _setup_ui(self, title, icon, color):
        self.setObjectName("StatCard")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(4)

        # Header row
        hdr = QHBoxLayout()
        hdr.setSpacing(8)

        self._icon_lbl = QLabel(icon)
        self._icon_lbl.setStyleSheet(f"color: {color}; font-size: 18px;")
        self._icon_lbl.setFixedWidth(24)

        self._title_lbl = QLabel(title)
        self._title_lbl.setStyleSheet("color: #94A3B8; font-size: 11px; font-weight: 600; letter-spacing: 1px;")

        hdr.addWidget(self._icon_lbl)
        hdr.addWidget(self._title_lbl)
        hdr.addStretch()
        layout.addLayout(hdr)

        # Value
        self._value_lbl = QLabel("—")
        self._value_lbl.setStyleSheet(f"color: #E2E8F0; font-size: 26px; font-weight: 700;")
        layout.addWidget(self._value_lbl)

        # Sub value
        self._sub_lbl = QLabel("")
        self._sub_lbl.setStyleSheet("color: #475569; font-size: 11px;")
        layout.addWidget(self._sub_lbl)

    def _apply_style(self, color):
        self.setStyleSheet(f"""
            QWidget#StatCard {{
                background: #111827;
                border: 1px solid #1E293B;
                border-radius: 12px;
            }}
            QWidget#StatCard:hover {{
                border: 1px solid {color}55;
                background: #1A2235;
            }}
        """)

    def set_value(self, value: str, sub: str = ""):
        self._value_lbl.setText(value)
        self._sub_lbl.setText(sub)

    def set_color(self, color: str):
        self._color = color
        self._icon_lbl.setStyleSheet(f"color: {color}; font-size: 18px;")
        self._apply_style(color)


# ─────────────────────────── SectionTitle ─────────────────────────────────────
class SectionTitle(QLabel):
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            color: #E2E8F0;
            font-size: 15px;
            font-weight: 700;
            letter-spacing: 0.5px;
            padding: 8px 0 4px 0;
        """)


# ─────────────────────────── GlowButton ───────────────────────────────────────
class GlowButton(QPushButton):
    """
    Neon-glow push button with hover animation.
    """

    def __init__(self, text: str, color: str = "#00D4FF", parent=None):
        super().__init__(text, parent)
        self._color = color
        self._apply_style(color)
        self.setCursor(Qt.PointingHandCursor)

    def _apply_style(self, color):
        self.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {color};
                border: 1px solid {color};
                border-radius: 8px;
                padding: 8px 20px;
                font-size: 13px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background: {color}22;
                border: 1px solid {color};
            }}
            QPushButton:pressed {{
                background: {color}44;
            }}
        """)

    def set_color(self, color: str):
        self._color = color
        self._apply_style(color)


class FilledButton(QPushButton):
    """Solid filled button"""
    def __init__(self, text: str, color: str = "#00D4FF", parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet(f"""
            QPushButton {{
                background: {color};
                color: #0A0E1A;
                border: none;
                border-radius: 8px;
                padding: 9px 22px;
                font-size: 13px;
                font-weight: 700;
            }}
            QPushButton:hover {{
                background: {color}CC;
            }}
            QPushButton:pressed {{
                background: {color}88;
            }}
        """)


# ─────────────────────────── ModeButton ───────────────────────────────────────
class ModeButton(QPushButton):
    """
    Performance mode button (icon + label + description).
    Toggles into an active state with neon highlight.
    """
    clicked_mode = pyqtSignal(str)

    def __init__(self, mode_id: str, title: str, icon: str,
                 description: str, color: str, parent=None):
        super().__init__(parent)
        self._mode_id = mode_id
        self._color   = color
        self._active  = False
        self.setCursor(Qt.PointingHandCursor)
        self.setCheckable(True)
        self.setMinimumHeight(90)

        inner = QVBoxLayout(self)
        inner.setContentsMargins(14, 12, 14, 12)
        inner.setSpacing(3)

        top = QHBoxLayout()
        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet(f"font-size: 22px; color: {color};")
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(f"color: #E2E8F0; font-size: 13px; font-weight: 700;")
        top.addWidget(icon_lbl)
        top.addWidget(title_lbl)
        top.addStretch()

        desc_lbl = QLabel(description)
        desc_lbl.setStyleSheet("color: #475569; font-size: 11px;")
        desc_lbl.setWordWrap(True)

        inner.addLayout(top)
        inner.addWidget(desc_lbl)

        self._deactivate()
        self.clicked.connect(lambda: self.clicked_mode.emit(self._mode_id))

    def _activate(self):
        self.setStyleSheet(f"""
            QPushButton {{
                background: {self._color}18;
                border: 1px solid {self._color};
                border-radius: 10px;
            }}
        """)

    def _deactivate(self):
        self.setStyleSheet("""
            QPushButton {
                background: #111827;
                border: 1px solid #1E293B;
                border-radius: 10px;
            }
            QPushButton:hover {
                background: #1A2235;
                border: 1px solid #334155;
            }
        """)

    def set_active(self, active: bool):
        self._active = active
        self.setChecked(active)
        if active:
            self._activate()
        else:
            self._deactivate()


# ─────────────────────────── AlertBanner ──────────────────────────────────────
class AlertBanner(QFrame):
    """
    Temporary alert notification that auto-dismisses.
    """
    dismissed = pyqtSignal()

    LEVELS = {
        "info":    ("#00D4FF", "ℹ"),
        "warning": ("#F59E0B", "⚠"),
        "critical":("#EF4444", "🔥"),
        "success": ("#10B981", "✓"),
    }

    def __init__(self, message: str, level: str = "info",
                 duration_ms: int = 5000, parent=None):
        super().__init__(parent)
        color, icon = self.LEVELS.get(level, self.LEVELS["info"])

        self.setObjectName("AlertBanner")
        self.setStyleSheet(f"""
            QFrame#AlertBanner {{
                background: {color}18;
                border: 1px solid {color}88;
                border-radius: 10px;
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)

        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet(f"font-size: 16px; color: {color};")
        msg_lbl  = QLabel(message)
        msg_lbl.setStyleSheet(f"color: #E2E8F0; font-size: 12px;")
        msg_lbl.setWordWrap(True)

        close_btn = QPushButton("✕")
        close_btn.setStyleSheet(f"color: {color}; border: none; background: transparent; font-size: 14px;")
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setFixedSize(24, 24)
        close_btn.clicked.connect(self._dismiss)

        layout.addWidget(icon_lbl)
        layout.addWidget(msg_lbl, 1)
        layout.addWidget(close_btn)

        if duration_ms > 0:
            QTimer.singleShot(duration_ms, self._dismiss)

    def _dismiss(self):
        self.hide()
        self.dismissed.emit()


# ─────────────────────────── SidebarButton ────────────────────────────────────
class SidebarButton(QPushButton):
    """Navigation button for the sidebar"""

    def __init__(self, icon: str, label: str,
                 color: str = "#00D4FF", parent=None):
        super().__init__(parent)
        self._color  = color
        self._active = False
        self.setCursor(Qt.PointingHandCursor)
        self.setCheckable(True)
        self.setMinimumHeight(52)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setSpacing(12)

        self._icon_lbl  = QLabel(icon)
        self._icon_lbl.setStyleSheet("font-size: 18px;")
        self._label_lbl = QLabel(label)
        self._label_lbl.setStyleSheet("font-size: 13px; font-weight: 500;")

        layout.addWidget(self._icon_lbl)
        layout.addWidget(self._label_lbl)
        layout.addStretch()

        self._set_inactive()
        self.toggled.connect(self._on_toggle)

    def _on_toggle(self, checked):
        if checked:
            self._set_active()
        else:
            self._set_inactive()

    def _set_active(self):
        self._icon_lbl.setStyleSheet(f"font-size: 18px; color: {self._color};")
        self._label_lbl.setStyleSheet(f"font-size: 13px; font-weight: 600; color: {self._color};")
        self.setStyleSheet(f"""
            QPushButton {{
                background: {self._color}18;
                border-left: 3px solid {self._color};
                border-radius: 0;
                text-align: left;
            }}
        """)

    def _set_inactive(self):
        self._icon_lbl.setStyleSheet("font-size: 18px; color: #475569;")
        self._label_lbl.setStyleSheet("font-size: 13px; font-weight: 500; color: #94A3B8;")
        self.setStyleSheet("""
            QPushButton {
                background: transparent;
                border-left: 3px solid transparent;
                border-radius: 0;
            }
            QPushButton:hover {
                background: #1A2235;
            }
        """)
