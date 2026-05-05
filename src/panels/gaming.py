"""
Gaming Boost Panel — kill background processes, free RAM, set CPU priority
"""

import psutil
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QScrollArea, QFrame, QTableWidget,
                              QTableWidgetItem, QHeaderView, QAbstractItemView,
                              QPushButton)
from PyQt5.QtCore    import Qt, QTimer, pyqtSignal
from PyQt5.QtGui     import QFont, QColor

from src.monitors.system_monitor import ProcessMonitor
from src.widgets.stat_card       import SectionTitle, FilledButton, GlowButton, StatCard


class GamingPanel(QWidget):
    notification = pyqtSignal(str, str)   # (message, level)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._proc_monitor = ProcessMonitor()
        self._boosted      = False
        self._setup_ui()

        # Refresh process table every 3 s
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._refresh_procs)
        self._timer.start(3000)

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
        title = QLabel("Gaming Boost")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setStyleSheet("color: #E2E8F0;")
        sub = QLabel("Optimise system resources for gaming performance")
        sub.setStyleSheet("color: #475569; font-size: 13px;")
        layout.addWidget(title)
        layout.addWidget(sub)

        # ── Boost Button ─────────────────────────────────────────
        boost_frame = QFrame()
        boost_frame.setObjectName("BoostFrame")
        boost_frame.setStyleSheet("""
            QFrame#BoostFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1a0a2e, stop:1 #0d1117);
                border: 1px solid #8B5CF655;
                border-radius: 16px;
            }
        """)
        bf_layout = QVBoxLayout(boost_frame)
        bf_layout.setContentsMargins(28, 24, 28, 24)
        bf_layout.setSpacing(12)
        bf_layout.setAlignment(Qt.AlignCenter)

        self._boost_icon = QLabel("🎮")
        self._boost_icon.setAlignment(Qt.AlignCenter)
        self._boost_icon.setStyleSheet("font-size: 48px;")

        self._boost_title = QLabel("Gaming Boost Mode")
        self._boost_title.setAlignment(Qt.AlignCenter)
        self._boost_title.setStyleSheet("color: #E2E8F0; font-size: 18px; font-weight: 700;")

        self._boost_desc = QLabel(
            "Kill background tasks · Free RAM · Elevate CPU priority\n"
            "Optimize settings for maximum in-game FPS")
        self._boost_desc.setAlignment(Qt.AlignCenter)
        self._boost_desc.setStyleSheet("color: #475569; font-size: 12px;")
        self._boost_desc.setWordWrap(True)

        self._boost_btn = QPushButton("⚡  ACTIVATE BOOST")
        self._boost_btn.setCursor(Qt.PointingHandCursor)
        self._boost_btn.setMinimumHeight(52)
        self._boost_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #8B5CF6, stop:1 #6D28D9);
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 14px;
                font-weight: 700;
                letter-spacing: 1px;
                padding: 12px 40px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #A78BFA, stop:1 #8B5CF6);
            }
            QPushButton:pressed {
                background: #6D28D9;
            }
        """)
        self._boost_btn.clicked.connect(self._toggle_boost)

        bf_layout.addWidget(self._boost_icon)
        bf_layout.addWidget(self._boost_title)
        bf_layout.addWidget(self._boost_desc)
        bf_layout.addSpacing(8)
        bf_layout.addWidget(self._boost_btn, alignment=Qt.AlignCenter)

        layout.addWidget(boost_frame)

        # ── Quick Action Buttons ──────────────────────────────────
        layout.addWidget(SectionTitle("Quick Actions"))
        actions_row = QHBoxLayout()
        actions_row.setSpacing(10)

        actions = [
            ("🧹  Free RAM",           "#10B981", self._free_ram),
            ("⬆  High CPU Priority",  "#00D4FF", self._set_high_priority),
            ("🔄  Refresh Processes",  "#8B5CF6", self._refresh_procs),
        ]
        for txt, color, fn in actions:
            btn = GlowButton(txt, color)
            btn.clicked.connect(fn)
            actions_row.addWidget(btn)
        layout.addLayout(actions_row)

        # ── Process Table ─────────────────────────────────────────
        layout.addWidget(SectionTitle("Running Processes"))

        table_frame = QFrame()
        table_frame.setStyleSheet("""
            QFrame {
                background: #111827;
                border: 1px solid #1E293B;
                border-radius: 12px;
            }
        """)
        tf_layout = QVBoxLayout(table_frame)
        tf_layout.setContentsMargins(0, 0, 0, 0)

        self._table = QTableWidget()
        self._table.setColumnCount(4)
        self._table.setHorizontalHeaderLabels(["Process", "PID", "CPU %", "MEM %"])
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self._table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self._table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self._table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._table.setAlternatingRowColors(True)
        self._table.verticalHeader().setVisible(False)
        self._table.setMinimumHeight(260)
        self._table.setStyleSheet("""
            QTableWidget {
                background: transparent;
                color: #E2E8F0;
                font-size: 12px;
                border: none;
                gridline-color: #1E293B;
            }
            QTableWidget::item:selected {
                background: #00D4FF22;
            }
            QHeaderView::section {
                background: #0F1526;
                color: #94A3B8;
                font-weight: 600;
                font-size: 11px;
                letter-spacing: 0.5px;
                padding: 6px;
                border: none;
                border-bottom: 1px solid #1E293B;
            }
            QTableWidget::item:alternate {
                background: #0F1526;
            }
        """)

        kill_btn = GlowButton("🗑  Kill Selected Process", "#EF4444")
        kill_btn.clicked.connect(self._kill_selected)

        tf_layout.addWidget(self._table)

        kill_row = QHBoxLayout()
        kill_row.setContentsMargins(12, 8, 12, 12)
        kill_row.addStretch()
        kill_row.addWidget(kill_btn)
        tf_layout.addLayout(kill_row)

        layout.addWidget(table_frame)
        layout.addStretch()

        scroll.setWidget(container)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

        self._refresh_procs()

    # ─────────────────────────────────────────────────────────────
    def _toggle_boost(self):
        self._boosted = not self._boosted
        if self._boosted:
            self._boost_btn.setText("✅  BOOST ACTIVE — Click to Deactivate")
            self._boost_btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #059669, stop:1 #10B981);
                    color: white; border: none; border-radius: 10px;
                    font-size: 14px; font-weight: 700;
                    letter-spacing: 1px; padding: 12px 40px;
                }
                QPushButton:hover { background: #10B981; }
            """)
            self._free_ram()
            self.notification.emit("Gaming Boost activated! Background tasks cleaned.", "success")
        else:
            self._boost_btn.setText("⚡  ACTIVATE BOOST")
            self._boost_btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #8B5CF6, stop:1 #6D28D9);
                    color: white; border: none; border-radius: 10px;
                    font-size: 14px; font-weight: 700;
                    letter-spacing: 1px; padding: 12px 40px;
                }
                QPushButton:hover { background: #8B5CF6; }
            """)
            self.notification.emit("Gaming Boost deactivated.", "info")

    def _free_ram(self):
        msg = self._proc_monitor.free_ram()
        self._refresh_procs()
        self.notification.emit(msg, "success")

    def _set_high_priority(self):
        import os
        try:
            p = psutil.Process(os.getpid())
            p.nice(psutil.HIGH_PRIORITY_CLASS)
            self.notification.emit("ThermaX set to High CPU priority.", "success")
        except Exception as e:
            self.notification.emit(f"Could not set priority: {e}", "warning")

    def _refresh_procs(self):
        procs = self._proc_monitor.get_top_processes(25)
        self._table.setRowCount(len(procs))
        for row, p in enumerate(procs):
            name_item = QTableWidgetItem(p["name"])
            pid_item  = QTableWidgetItem(str(p["pid"]))
            cpu_item  = QTableWidgetItem(f"{p['cpu']:.1f}%")
            mem_item  = QTableWidgetItem(f"{p['mem']:.1f}%")

            # Color CPU cells
            if p["cpu"] > 20:
                cpu_item.setForeground(QColor("#EF4444"))
            elif p["cpu"] > 5:
                cpu_item.setForeground(QColor("#F59E0B"))
            else:
                cpu_item.setForeground(QColor("#94A3B8"))

            for item in (name_item, pid_item, cpu_item, mem_item):
                item.setTextAlignment(Qt.AlignCenter)
            name_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)

            self._table.setItem(row, 0, name_item)
            self._table.setItem(row, 1, pid_item)
            self._table.setItem(row, 2, cpu_item)
            self._table.setItem(row, 3, mem_item)
            self._table.setRowHeight(row, 32)

    def _kill_selected(self):
        rows = self._table.selectedItems()
        if not rows:
            return
        row = self._table.currentRow()
        pid_item = self._table.item(row, 1)
        name_item = self._table.item(row, 0)
        if pid_item:
            pid  = int(pid_item.text())
            name = name_item.text() if name_item else "process"
            ok   = self._proc_monitor.kill_process(pid)
            if ok:
                self.notification.emit(f"Killed {name} (PID {pid})", "success")
                self._refresh_procs()
            else:
                self.notification.emit(f"Could not kill {name}. Insufficient permissions.", "warning")

    def update_data(self, data: dict):
        pass   # process table auto-refreshes via timer
