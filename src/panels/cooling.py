"""
Cooling Control Panel — temperature dashboard + fan control
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QScrollArea, QFrame, QSlider, QButtonGroup,
                              QPushButton, QProgressBar, QSizePolicy)
from PyQt5.QtCore    import Qt, pyqtSignal
from PyQt5.QtGui     import QFont, QColor

from src.widgets.stat_card  import SectionTitle, GlowButton, StatCard
from src.widgets.graph_widget import MiniGraph


# ── Temperature bar widget ────────────────────────────────────────────────────
class TempBar(QWidget):
    """Horizontal temperature-colored progress bar with label"""

    def __init__(self, label: str, unit: str = "°C", parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        top = QHBoxLayout()
        self._label = QLabel(label)
        self._label.setStyleSheet("color: #94A3B8; font-size: 12px; font-weight: 600;")
        self._value = QLabel("—")
        self._value.setStyleSheet("color: #E2E8F0; font-size: 13px; font-weight: 700;")
        self._unit  = unit
        top.addWidget(self._label)
        top.addStretch()
        top.addWidget(self._value)
        layout.addLayout(top)

        self._bar = QProgressBar()
        self._bar.setRange(0, 100)
        self._bar.setValue(0)
        self._bar.setTextVisible(False)
        self._bar.setFixedHeight(6)
        self._bar.setStyleSheet("""
            QProgressBar { background: #1E293B; border-radius: 3px; }
            QProgressBar::chunk { background: #10B981; border-radius: 3px; }
        """)
        layout.addWidget(self._bar)

    def set_temp(self, temp: float):
        self._value.setText(f"{temp:.0f}{self._unit}")
        pct = min(int((temp / 100) * 100), 100)
        self._bar.setValue(pct)

        if temp < 60:
            chunk_color = "#10B981"
        elif temp < 80:
            chunk_color = "#F59E0B"
        else:
            chunk_color = "#EF4444"

        self._bar.setStyleSheet(f"""
            QProgressBar {{ background: #1E293B; border-radius: 3px; }}
            QProgressBar::chunk {{ background: {chunk_color}; border-radius: 3px; }}
        """)


# ── Fan Mode Button ───────────────────────────────────────────────────────────
class FanModeBtn(QPushButton):
    def __init__(self, text: str, color: str = "#00D4FF", parent=None):
        super().__init__(text, parent)
        self._color = color
        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(40)
        self._set_inactive()
        self.toggled.connect(lambda c: self._set_active() if c else self._set_inactive())

    def _set_active(self):
        self.setStyleSheet(f"""
            QPushButton {{
                background: {self._color}22;
                border: 1px solid {self._color};
                border-radius: 8px;
                color: {self._color};
                font-weight: 700;
                font-size: 12px;
                padding: 8px 14px;
            }}
        """)

    def _set_inactive(self):
        self.setStyleSheet("""
            QPushButton {
                background: #111827;
                border: 1px solid #1E293B;
                border-radius: 8px;
                color: #94A3B8;
                font-size: 12px;
                padding: 8px 14px;
            }
            QPushButton:hover {
                background: #1A2235;
                border: 1px solid #334155;
            }
        """)


# ── Main Panel ────────────────────────────────────────────────────────────────
class CoolingPanel(QWidget):
    fan_mode_changed = pyqtSignal(str, int)   # (mode, manual_pct)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._fan_mode   = "auto"
        self._manual_pct = 50
        self._setup_ui()

    def _setup_ui(self):
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        container = QWidget()
        layout    = QVBoxLayout(container)
        layout.setContentsMargins(24, 20, 24, 24)
        layout.setSpacing(20)

        # Header
        title = QLabel("Cooling Control")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setStyleSheet("color: #E2E8F0;")
        sub = QLabel("Monitor temperatures & control fan speed")
        sub.setStyleSheet("color: #475569; font-size: 13px;")
        layout.addWidget(title)
        layout.addWidget(sub)

        # ── Temperature Dashboard ─────────────────────────────────
        layout.addWidget(SectionTitle("Temperature Dashboard"))

        temp_frame = QFrame()
        temp_frame.setStyleSheet("""
            QFrame {
                background: #111827;
                border: 1px solid #1E293B;
                border-radius: 14px;
            }
        """)
        tf_layout = QVBoxLayout(temp_frame)
        tf_layout.setContentsMargins(20, 18, 20, 18)
        tf_layout.setSpacing(14)

        self._cpu_bar = TempBar("🔵  CPU Temperature")
        self._gpu_bar = TempBar("🟣  GPU Temperature")
        self._sys_bar = TempBar("🟡  System (ACPI)")

        tf_layout.addWidget(self._cpu_bar)
        tf_layout.addWidget(self._gpu_bar)
        tf_layout.addWidget(self._sys_bar)

        layout.addWidget(temp_frame)

        # ── Temp Stat Cards ───────────────────────────────────────
        cards_row = QHBoxLayout()
        cards_row.setSpacing(12)
        self.card_cpu_max = StatCard("CPU MAX",   "🔴", "#EF4444")
        self.card_gpu_max = StatCard("GPU MAX",   "🔴", "#8B5CF6")
        self.card_delta   = StatCard("DELTA CPU↔GPU", "📊", "#F59E0B")
        self.card_status  = StatCard("THERMAL STATE", "💚", "#10B981")
        for c in (self.card_cpu_max, self.card_gpu_max,
                  self.card_delta, self.card_status):
            cards_row.addWidget(c)
        layout.addLayout(cards_row)

        # ── Temperature Graph ─────────────────────────────────────
        layout.addWidget(SectionTitle("Temperature History"))

        graph_frame = QFrame()
        graph_frame.setStyleSheet("""
            QFrame {
                background: #111827;
                border: 1px solid #1E293B;
                border-radius: 12px;
            }
        """)
        gfl = QVBoxLayout(graph_frame)
        gfl.setContentsMargins(14, 12, 14, 12)
        gfl.setSpacing(6)

        legend = QHBoxLayout()
        for text, color in (("● CPU", "#EF4444"), ("● GPU", "#8B5CF6")):
            lbl = QLabel(text)
            lbl.setStyleSheet(f"color: {color}; font-size: 11px; font-weight: 600;")
            legend.addWidget(lbl)
        legend.addStretch()

        self._temp_graph = MiniGraph(color="#EF4444", y_max=100, fill=True)
        self._temp_graph.setMinimumHeight(110)

        gfl.addLayout(legend)
        gfl.addWidget(self._temp_graph)
        layout.addWidget(graph_frame)

        # ── Fan Control ───────────────────────────────────────────
        layout.addWidget(SectionTitle("Fan Control"))

        fan_frame = QFrame()
        fan_frame.setStyleSheet("""
            QFrame {
                background: #111827;
                border: 1px solid #1E293B;
                border-radius: 14px;
            }
        """)
        fan_layout = QVBoxLayout(fan_frame)
        fan_layout.setContentsMargins(20, 18, 20, 18)
        fan_layout.setSpacing(14)

        # Fan mode buttons
        fan_mode_row = QHBoxLayout()
        fan_mode_row.setSpacing(10)

        self._fan_btn_auto   = FanModeBtn("🔄  Auto",        "#10B981")
        self._fan_btn_max    = FanModeBtn("🔥  Maximum",     "#EF4444")
        self._fan_btn_manual = FanModeBtn("🎛   Manual",     "#00D4FF")
        self._fan_btn_silent = FanModeBtn("🔇  Silent",      "#06B6D4")

        self._fan_group = QButtonGroup(self)
        for btn in (self._fan_btn_auto, self._fan_btn_max,
                    self._fan_btn_manual, self._fan_btn_silent):
            self._fan_group.addButton(btn)
            fan_mode_row.addWidget(btn)

        self._fan_btn_auto.setChecked(True)

        self._fan_btn_auto.clicked.connect(   lambda: self._set_fan_mode("auto"))
        self._fan_btn_max.clicked.connect(    lambda: self._set_fan_mode("max"))
        self._fan_btn_manual.clicked.connect( lambda: self._set_fan_mode("manual"))
        self._fan_btn_silent.clicked.connect( lambda: self._set_fan_mode("silent"))

        fan_layout.addLayout(fan_mode_row)

        # Manual slider
        slider_frame = QFrame()
        slider_frame.setObjectName("SliderFrame")
        slider_frame.setStyleSheet("QFrame#SliderFrame { background: transparent; }")
        sl_layout = QVBoxLayout(slider_frame)
        sl_layout.setContentsMargins(0, 0, 0, 0)
        sl_layout.setSpacing(6)

        slider_hdr = QHBoxLayout()
        sl_lbl = QLabel("Fan Speed")
        sl_lbl.setStyleSheet("color: #94A3B8; font-size: 12px;")
        self._fan_pct_lbl = QLabel("50%")
        self._fan_pct_lbl.setStyleSheet("color: #00D4FF; font-size: 14px; font-weight: 700;")
        slider_hdr.addWidget(sl_lbl)
        slider_hdr.addStretch()
        slider_hdr.addWidget(self._fan_pct_lbl)

        self._fan_slider = QSlider(Qt.Horizontal)
        self._fan_slider.setRange(0, 100)
        self._fan_slider.setValue(50)
        self._fan_slider.setEnabled(False)
        self._fan_slider.valueChanged.connect(self._on_slider_change)

        sl_layout.addLayout(slider_hdr)
        sl_layout.addWidget(self._fan_slider)
        fan_layout.addWidget(slider_frame)

        # Fan status row
        self._fan_status = QLabel("🟢  Fan mode: Auto  |  System managing fan speed")
        self._fan_status.setStyleSheet("color: #475569; font-size: 12px; font-style: italic;")
        fan_layout.addWidget(self._fan_status)

        layout.addWidget(fan_frame)

        # ── Overheat Warning Config ───────────────────────────────
        layout.addWidget(SectionTitle("Overheat Warning Threshold"))

        warn_frame = QFrame()
        warn_frame.setStyleSheet("""
            QFrame {
                background: #111827;
                border: 1px solid #EF444433;
                border-radius: 12px;
            }
        """)
        wfl = QHBoxLayout(warn_frame)
        wfl.setContentsMargins(18, 14, 18, 14)

        warn_lbl = QLabel("🌡  Alert when CPU/GPU exceeds:")
        warn_lbl.setStyleSheet("color: #94A3B8; font-size: 13px;")

        self._threshold_slider = QSlider(Qt.Horizontal)
        self._threshold_slider.setRange(60, 100)
        self._threshold_slider.setValue(85)
        self._threshold_slider.setFixedWidth(200)

        self._thresh_lbl = QLabel("85°C")
        self._thresh_lbl.setStyleSheet("color: #EF4444; font-size: 14px; font-weight: 700; min-width: 40px;")
        self._threshold_slider.valueChanged.connect(
            lambda v: self._thresh_lbl.setText(f"{v}°C"))

        wfl.addWidget(warn_lbl)
        wfl.addStretch()
        wfl.addWidget(self._threshold_slider)
        wfl.addWidget(self._thresh_lbl)
        layout.addWidget(warn_frame)

        layout.addStretch()
        scroll.setWidget(container)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

        # Tracking
        self._cpu_temps = []
        self._cpu_max   = 0.0
        self._gpu_max   = 0.0

    # ─────────────────────────────────────────────────────────────
    def _set_fan_mode(self, mode: str):
        self._fan_mode = mode
        self._fan_slider.setEnabled(mode == "manual")
        labels = {
            "auto":   "🟢  Fan mode: Auto  |  System managing fan speed",
            "max":    "🔴  Fan mode: Maximum  |  Fan running at 100%",
            "manual": f"🔵  Fan mode: Manual  |  Speed locked at {self._manual_pct}%",
            "silent": "🔵  Fan mode: Silent  |  Minimum fan speed",
        }
        self._fan_status.setText(labels.get(mode, ""))
        self.fan_mode_changed.emit(mode, self._manual_pct)

    def _on_slider_change(self, value: int):
        self._manual_pct = value
        self._fan_pct_lbl.setText(f"{value}%")
        if self._fan_mode == "manual":
            self._fan_status.setText(
                f"🔵  Fan mode: Manual  |  Speed locked at {value}%")
        self.fan_mode_changed.emit(self._fan_mode, value)

    @property
    def threshold(self) -> int:
        return self._threshold_slider.value()

    # ─────────────────────────────────────────────────────────────
    def update_data(self, data: dict):
        cpu = data.get("cpu", {})
        gpu = data.get("gpu", {})

        cpu_t = cpu.get("temp", 0.0)
        gpu_t = gpu.get("temp", 0.0)

        self._cpu_bar.set_temp(cpu_t)
        self._gpu_bar.set_temp(gpu_t)
        self._sys_bar.set_temp(max(cpu_t, gpu_t) * 0.85)

        if cpu_t > self._cpu_max: self._cpu_max = cpu_t
        if gpu_t > self._gpu_max: self._gpu_max = gpu_t

        self.card_cpu_max.set_value(f"{self._cpu_max:.0f}°C", "session peak")
        self.card_gpu_max.set_value(f"{self._gpu_max:.0f}°C", "session peak")
        self.card_delta.set_value(f"{abs(cpu_t - gpu_t):.0f}°C", "CPU vs GPU")

        # Thermal state
        max_t = max(cpu_t, gpu_t)
        if max_t < 65:
            state, color = "🟢  Cool", "#10B981"
        elif max_t < 80:
            state, color = "🟡  Warm", "#F59E0B"
        else:
            state, color = "🔴  Hot",  "#EF4444"
        self.card_status.set_value(state)
        self.card_status.set_color(color)

        # Graph
        self._cpu_temps.append(cpu_t)
        self._cpu_temps = self._cpu_temps[-60:]
        self._temp_graph.update_data(self._cpu_temps)
