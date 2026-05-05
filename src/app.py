"""
ThermaX — Main Application Window
Futuristic JARVIS-style performance control center
"""

import sys
from PyQt5.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
                              QLabel, QPushButton, QStackedWidget, QFrame,
                              QSizePolicy, QButtonGroup, QApplication,
                              QGraphicsDropShadowEffect)
from PyQt5.QtCore    import Qt, QTimer, pyqtSignal, QPoint, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui     import QFont, QColor, QIcon, QPixmap, QPainter, QLinearGradient

from src.utils.theme         import ThemeManager
from src.monitors.data_worker import DataWorker
from src.panels.dashboard     import DashboardPanel
from src.panels.performance   import PerformancePanel
from src.panels.cooling       import CoolingPanel
from src.panels.gaming        import GamingPanel
from src.panels.ai_optimizer  import AIPanel
from src.panels.system_health import SystemHealthPanel
from src.widgets.stat_card    import AlertBanner, SidebarButton


# ─────────────────────────────────────────────────────────────────────────────
# NOTIFICATION OVERLAY
# ─────────────────────────────────────────────────────────────────────────────
class NotificationOverlay(QWidget):
    """Floating notification stack anchored to top-right of main window"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setFixedWidth(340)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignTop)
        self._layout = layout

    def show_notification(self, message: str, level: str = "info"):
        banner = AlertBanner(message, level, duration_ms=5000, parent=self)
        self._layout.insertWidget(0, banner)
        self.adjustSize()
        self._reposition()

    def _reposition(self):
        if self.parent():
            pw = self.parent().width()
            self.move(pw - self.width() - 16, 70)


# ─────────────────────────────────────────────────────────────────────────────
# HEADER BAR
# ─────────────────────────────────────────────────────────────────────────────
class HeaderBar(QFrame):
    theme_toggled     = pyqtSignal()
    minimize_clicked  = pyqtSignal()
    maximize_clicked  = pyqtSignal()
    close_clicked     = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(58)
        self.setObjectName("HeaderBar")
        self._drag_pos = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 0, 16, 0)
        layout.setSpacing(12)

        # Logo + name
        logo = QLabel("⬡")
        logo.setStyleSheet("color: #00D4FF; font-size: 22px;")
        name = QLabel("ThermaX")
        name.setFont(QFont("Segoe UI", 14, QFont.Bold))
        name.setStyleSheet("color: #E2E8F0; letter-spacing: 1px;")
        version = QLabel("v1.0")
        version.setStyleSheet("color: #475569; font-size: 11px; padding-top: 2px;")

        layout.addWidget(logo)
        layout.addWidget(name)
        layout.addWidget(version)
        layout.addStretch()

        # Live clock
        self._clock = QLabel()
        self._clock.setStyleSheet("color: #475569; font-size: 12px; font-variant-numeric: tabular-nums;")
        self._tick()
        self._clock_timer = QTimer(self)
        self._clock_timer.timeout.connect(self._tick)
        self._clock_timer.start(1000)
        layout.addWidget(self._clock)
        layout.addSpacing(12)

        # Theme toggle
        self._theme_btn = QPushButton("☀")
        self._theme_btn.setFixedSize(36, 36)
        self._theme_btn.setToolTip("Toggle Dark / Light mode")
        self._theme_btn.setCursor(Qt.PointingHandCursor)
        self._style_icon_btn(self._theme_btn)
        self._theme_btn.clicked.connect(self.theme_toggled.emit)
        layout.addWidget(self._theme_btn)

        # Window controls
        for symbol, sig, color in [
            ("─", self.minimize_clicked, "#475569"),
            ("□", self.maximize_clicked, "#475569"),
            ("✕", self.close_clicked,    "#EF4444"),
        ]:
            btn = QPushButton(symbol)
            btn.setFixedSize(32, 32)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    color: {color};
                    border: none;
                    border-radius: 6px;
                    font-size: 13px;
                }}
                QPushButton:hover {{ background: {color}22; }}
            """)
            btn.clicked.connect(sig.emit)
            layout.addWidget(btn)

        self.setStyleSheet("""
            QFrame#HeaderBar {
                background: #080C18;
                border-bottom: 1px solid #1E293B;
            }
        """)

    def _style_icon_btn(self, btn):
        btn.setStyleSheet("""
            QPushButton {
                background: #111827;
                color: #94A3B8;
                border: 1px solid #1E293B;
                border-radius: 8px;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #1A2235;
                color: #E2E8F0;
            }
        """)

    def _tick(self):
        from datetime import datetime
        self._clock.setText(datetime.now().strftime("%a, %d %b  %H:%M:%S"))

    # Draggable window
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos() - self.window().frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self._drag_pos:
            self.window().move(event.globalPos() - self._drag_pos)


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
class Sidebar(QFrame):
    page_changed = pyqtSignal(int)

    NAV_ITEMS = [
        ("📊", "Dashboard"),
        ("⚡", "Performance"),
        ("🌡", "Cooling"),
        ("🎮", "Gaming"),
        ("🤖", "AI Optimizer"),
        ("💚", "System Health"),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(200)
        self.setObjectName("Sidebar")
        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet("""
            QFrame#Sidebar {
                background: #080C18;
                border-right: 1px solid #1E293B;
            }
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 16, 0, 16)
        layout.setSpacing(2)

        nav_label = QLabel("NAVIGATION")
        nav_label.setStyleSheet("""
            color: #334155;
            font-size: 10px;
            font-weight: 700;
            letter-spacing: 2px;
            padding: 0 16px;
            margin-bottom: 8px;
        """)
        layout.addWidget(nav_label)

        self._btn_group = QButtonGroup(self)
        self._btn_group.setExclusive(True)
        self._buttons = []

        for idx, (icon, label) in enumerate(self.NAV_ITEMS):
            btn = SidebarButton(icon, label)
            self._btn_group.addButton(btn, idx)
            layout.addWidget(btn)
            self._buttons.append(btn)
            btn.clicked.connect(lambda checked, i=idx: self.page_changed.emit(i))

        layout.addStretch()

        # Bottom: CPU/RAM mini display
        self._cpu_mini  = self._mini_stat("CPU", "#00D4FF")
        self._ram_mini  = self._mini_stat("RAM", "#10B981")

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color: #1E293B;")
        layout.addWidget(sep)
        layout.addWidget(self._cpu_mini)
        layout.addWidget(self._ram_mini)

        # Select first button
        self._buttons[0].setChecked(True)

    def _mini_stat(self, label: str, color: str) -> QWidget:
        w = QWidget()
        hl = QHBoxLayout(w)
        hl.setContentsMargins(16, 4, 16, 4)
        hl.setSpacing(8)
        lbl = QLabel(label)
        lbl.setStyleSheet(f"color: {color}; font-size: 11px; font-weight: 700; min-width: 34px;")
        val = QLabel("—")
        val.setStyleSheet("color: #94A3B8; font-size: 11px;")
        from PyQt5.QtWidgets import QProgressBar
        bar = QProgressBar()
        bar.setRange(0, 100)
        bar.setValue(0)
        bar.setTextVisible(False)
        bar.setFixedHeight(4)
        bar.setStyleSheet(f"""
            QProgressBar {{ background: #1E293B; border-radius: 2px; }}
            QProgressBar::chunk {{ background: {color}; border-radius: 2px; }}
        """)
        inner = QVBoxLayout()
        inner.setSpacing(2)
        inner.addWidget(val)
        inner.addWidget(bar)
        hl.addWidget(lbl)
        hl.addLayout(inner, 1)
        w._val = val
        w._bar = bar
        return w

    def select_page(self, idx: int):
        self._buttons[idx].setChecked(True)

    def update_mini(self, cpu_pct: float, ram_pct: float):
        self._cpu_mini._val.setText(f"{cpu_pct:.0f}%")
        self._cpu_mini._bar.setValue(int(cpu_pct))
        self._ram_mini._val.setText(f"{ram_pct:.0f}%")
        self._ram_mini._bar.setValue(int(ram_pct))


# ─────────────────────────────────────────────────────────────────────────────
# MAIN WINDOW
# ─────────────────────────────────────────────────────────────────────────────
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._theme  = ThemeManager.instance()
        self._maximised = False
        self._setup_window()
        self._setup_ui()
        self._start_worker()

    # ── Window Setup ──────────────────────────────────────────────
    def _setup_window(self):
        self.setWindowTitle("ThermaX — Performance Control Center")
        self.setMinimumSize(1200, 760)
        self.resize(1380, 860)
        self.setWindowFlags(Qt.FramelessWindowHint)   # custom title bar
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        self.setStyleSheet(self._theme.stylesheet())

    # ── UI Construction ───────────────────────────────────────────
    def _setup_ui(self):
        root = QWidget()
        self.setCentralWidget(root)
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # ── Header ────────────────────────────────────────────────
        self._header = HeaderBar()
        self._header.theme_toggled.connect(self._toggle_theme)
        self._header.minimize_clicked.connect(self.showMinimized)
        self._header.maximize_clicked.connect(self._toggle_maximize)
        self._header.close_clicked.connect(self.close)
        root_layout.addWidget(self._header)

        # ── Body (sidebar + content) ──────────────────────────────
        body = QWidget()
        body_layout = QHBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)

        # Sidebar
        self._sidebar = Sidebar()
        self._sidebar.page_changed.connect(self._switch_page)
        body_layout.addWidget(self._sidebar)

        # Content stack
        self._stack = QStackedWidget()
        self._stack.setStyleSheet("QStackedWidget { background: #0A0E1A; }")
        body_layout.addWidget(self._stack, 1)
        root_layout.addWidget(body, 1)

        # ── Pages ────────────────────────────────────────────────
        self._dashboard    = DashboardPanel()
        self._performance  = PerformancePanel()
        self._cooling      = CoolingPanel()
        self._gaming       = GamingPanel()
        self._ai           = AIPanel()
        self._health       = SystemHealthPanel()

        for panel in (self._dashboard, self._performance, self._cooling,
                      self._gaming, self._ai, self._health):
            self._stack.addWidget(panel)

        # ── Notification overlay ──────────────────────────────────
        self._notif = NotificationOverlay(root)
        self._notif.move(self.width() - 356, 70)
        self._notif.show()

        # ── Connect signals ───────────────────────────────────────
        self._gaming.notification.connect(self._show_notification)
        self._cooling.fan_mode_changed.connect(
            lambda mode, pct: self._show_notification(
                f"Fan mode changed: {mode.upper()}", "info"))
        self._performance.mode_changed.connect(
            lambda mode: self._show_notification(
                f"Performance mode: {mode.capitalize()}", "info"))

    # ── Data Worker ────────────────────────────────────────────────
    def _start_worker(self):
        self._worker = DataWorker(interval_ms=1000)
        self._worker.data_ready.connect(self._on_data)
        self._worker.start()

        # Slower AI scan (every 5 s)
        self._ai_timer = QTimer(self)
        self._ai_timer.timeout.connect(lambda: self._ai.update_data(self._last_data))
        self._ai_timer.start(5000)
        self._last_data = {}

        # Alert checks every 5 s
        self._alert_timer = QTimer(self)
        self._alert_timer.timeout.connect(self._check_alerts)
        self._alert_timer.start(5000)

    def _on_data(self, data: dict):
        self._last_data = data
        cpu = data.get("cpu", {})
        ram = data.get("ram", {})

        # Update active panel
        idx = self._stack.currentIndex()
        panels = [self._dashboard, self._performance, self._cooling,
                  self._gaming, self._ai, self._health]
        panels[idx].update_data(data)

        # Always update sidebar mini stats
        self._sidebar.update_mini(cpu.get("usage", 0), ram.get("percent", 0))

    # ── Alert Checker ─────────────────────────────────────────────
    def _check_alerts(self):
        if not self._last_data:
            return
        cpu  = self._last_data.get("cpu",  {})
        gpu  = self._last_data.get("gpu",  {})
        ram  = self._last_data.get("ram",  {})
        disk = self._last_data.get("disk", {})

        thresh = self._cooling.threshold

        cpu_t = cpu.get("temp", 0)
        gpu_t = gpu.get("temp", 0)

        if cpu_t > thresh:
            msg = f"🔥 CPU temperature {cpu_t:.0f}°C exceeds threshold ({thresh}°C)!"
            self._show_notification(msg, "critical")
            self._health.add_alert(msg)

        if gpu_t > thresh:
            msg = f"🔥 GPU temperature {gpu_t:.0f}°C exceeds threshold ({thresh}°C)!"
            self._show_notification(msg, "critical")
            self._health.add_alert(msg)

        ram_pct = ram.get("percent", 0)
        if ram_pct > 90:
            msg = f"⚠ RAM usage critical: {ram_pct:.0f}%"
            self._show_notification(msg, "warning")
            self._health.add_alert(msg)

        for p in disk.get("partitions", []):
            if p.get("percent", 0) > 90:
                msg = f"💾 Disk {p['mountpoint']} is {p['percent']:.0f}% full"
                self._show_notification(msg, "warning")
                self._health.add_alert(msg)

    # ── Page Switching ────────────────────────────────────────────
    def _switch_page(self, idx: int):
        self._stack.setCurrentIndex(idx)
        # Immediately update new panel with latest data
        if self._last_data:
            panels = [self._dashboard, self._performance, self._cooling,
                      self._gaming, self._ai, self._health]
            panels[idx].update_data(self._last_data)

    # ── Notification ──────────────────────────────────────────────
    def _show_notification(self, message: str, level: str = "info"):
        self._notif.show_notification(message, level)
        self._notif.move(self.width() - 356, 70)

    # ── Theme ─────────────────────────────────────────────────────
    def _toggle_theme(self):
        self._theme.toggle()
        self.setStyleSheet(self._theme.stylesheet())

    # ── Window controls ───────────────────────────────────────────
    def _toggle_maximize(self):
        if self._maximised:
            self.showNormal()
        else:
            self.showMaximized()
        self._maximised = not self._maximised

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "_notif"):
            self._notif.move(self.width() - 356, 70)

    def closeEvent(self, event):
        if hasattr(self, "_worker"):
            self._worker.stop()
        event.accept()
