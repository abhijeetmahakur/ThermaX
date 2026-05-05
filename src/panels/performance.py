"""
Performance Modes Panel — Quiet / Balanced / Performance / Turbo
"""

import psutil
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                              QLabel, QScrollArea, QFrame, QSlider, QSpinBox,
                              QGroupBox)
from PyQt5.QtCore    import Qt, pyqtSignal
from PyQt5.QtGui     import QFont

from src.widgets.stat_card import (ModeButton, SectionTitle, FilledButton,
                                    GlowButton, StatCard)


MODES = {
    "quiet": {
        "title":       "Quiet Mode",
        "icon":        "🔇",
        "description": "Low power · Silent fan · Battery saving",
        "color":       "#06B6D4",
        "cpu_pct":     30,
        "fan":         "auto_quiet",
    },
    "balanced": {
        "title":       "Balanced Mode",
        "icon":        "⚖",
        "description": "Balanced power and performance",
        "color":       "#10B981",
        "cpu_pct":     60,
        "fan":         "auto",
    },
    "performance": {
        "title":       "Performance Mode",
        "icon":        "🚀",
        "description": "Higher clocks · Optimised for gaming",
        "color":       "#8B5CF6",
        "cpu_pct":     85,
        "fan":         "auto_high",
    },
    "turbo": {
        "title":       "Turbo Mode",
        "icon":        "⚡",
        "description": "Max clocks · Max fan · Full power",
        "color":       "#EF4444",
        "cpu_pct":     100,
        "fan":         "max",
    },
}


class PerformancePanel(QWidget):
    mode_changed = pyqtSignal(str)   # emits mode_id

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_mode = "balanced"
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

        # ── Header ──────────────────────────────────────────────
        title = QLabel("Performance Modes")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setStyleSheet("color: #E2E8F0;")
        sub   = QLabel("Choose power plan to match your workload")
        sub.setStyleSheet("color: #475569; font-size: 13px;")
        layout.addWidget(title)
        layout.addWidget(sub)

        # ── Mode Buttons ─────────────────────────────────────────
        layout.addWidget(SectionTitle("Power Plan"))
        grid = QGridLayout()
        grid.setSpacing(12)
        self._mode_btns = {}

        for idx, (mode_id, cfg) in enumerate(MODES.items()):
            btn = ModeButton(
                mode_id     = mode_id,
                title       = cfg["title"],
                icon        = cfg["icon"],
                description = cfg["description"],
                color       = cfg["color"],
            )
            btn.clicked_mode.connect(self._on_mode_clicked)
            row, col = divmod(idx, 2)
            grid.addWidget(btn, row, col)
            self._mode_btns[mode_id] = btn

        layout.addLayout(grid)

        # ── Active Indicator ─────────────────────────────────────
        self._active_label = QLabel()
        self._active_label.setAlignment(Qt.AlignCenter)
        self._active_label.setStyleSheet("""
            background: #111827;
            border: 1px solid #1E293B;
            border-radius: 10px;
            padding: 10px;
            color: #94A3B8;
            font-size: 13px;
        """)
        layout.addWidget(self._active_label)

        # ── CPU Power Stats ──────────────────────────────────────
        layout.addWidget(SectionTitle("Current CPU Power"))
        stats_row = QHBoxLayout()
        stats_row.setSpacing(12)

        self.card_proc   = StatCard("PROCESSES",    "🔄", "#00D4FF")
        self.card_threads = StatCard("THREADS",    "🧵", "#8B5CF6")
        self.card_power  = StatCard("POWER PLAN",  "⚡", "#F59E0B")

        for c in (self.card_proc, self.card_threads, self.card_power):
            stats_row.addWidget(c)
        layout.addLayout(stats_row)

        # ── Boost switch description ─────────────────────────────
        info_box = QFrame()
        info_box.setStyleSheet("""
            QFrame {
                background: #111827;
                border: 1px solid #1E293B;
                border-radius: 12px;
            }
        """)
        ib_layout = QVBoxLayout(info_box)
        ib_layout.setContentsMargins(18, 16, 18, 16)
        ib_layout.setSpacing(8)

        info_title = QLabel("💡  About Performance Modes")
        info_title.setStyleSheet("color: #E2E8F0; font-size: 14px; font-weight: 700;")
        ib_layout.addWidget(info_title)

        tips = [
            ("🔇 Quiet",       "Runs CPU at ≤30% TDP. Best for office work or reading."),
            ("⚖  Balanced",    "System default. Adjusts dynamically between 30–60%."),
            ("🚀 Performance", "Boosts clocks. Ideal for gaming at ~85% TDP ceiling."),
            ("⚡ Turbo",       "Removes all CPU limits. Max heat but max speed."),
        ]
        for icon_txt, desc in tips:
            row = QHBoxLayout()
            il  = QLabel(icon_txt)
            il.setStyleSheet("color: #00D4FF; font-size: 12px; font-weight: 700; min-width: 110px;")
            dl  = QLabel(desc)
            dl.setStyleSheet("color: #94A3B8; font-size: 12px;")
            dl.setWordWrap(True)
            row.addWidget(il)
            row.addWidget(dl, 1)
            ib_layout.addLayout(row)

        layout.addWidget(info_box)
        layout.addStretch()

        scroll.setWidget(container)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

        # Activate default
        self._activate_mode("balanced")

    # ─────────────────────────────────────────────────────────────
    def _on_mode_clicked(self, mode_id: str):
        self._activate_mode(mode_id)
        self.mode_changed.emit(mode_id)

    def _activate_mode(self, mode_id: str):
        self._current_mode = mode_id
        for mid, btn in self._mode_btns.items():
            btn.set_active(mid == mode_id)
        cfg = MODES[mode_id]
        self._active_label.setText(
            f"{cfg['icon']}  Active: <b style='color:{cfg['color']}'>{cfg['title']}</b>"
            f"  —  {cfg['description']}"
        )

    def update_data(self, data: dict):
        cpu = data.get("cpu", {})
        try:
            proc_count   = len(list(psutil.process_iter()))
            thread_count = sum(p.num_threads() for p in psutil.process_iter()
                               if p.status() == psutil.STATUS_RUNNING)
        except Exception:
            proc_count, thread_count = 0, 0

        self.card_proc.set_value(str(proc_count),    "running processes")
        self.card_threads.set_value(str(thread_count), "active threads")
        self.card_power.set_value(MODES[self._current_mode]["title"],
                                   f"CPU {cpu.get('usage', 0):.0f}% load")
