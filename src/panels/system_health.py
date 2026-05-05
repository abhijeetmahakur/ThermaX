"""
System Health Panel — battery, alerts, disk health, network stats
"""

import psutil
import subprocess
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QScrollArea, QFrame, QProgressBar, QListWidget,
                              QListWidgetItem, QGridLayout)
from PyQt5.QtCore    import Qt, QTimer
from PyQt5.QtGui     import QFont, QColor

from src.widgets.stat_card   import SectionTitle, StatCard, GlowButton


class HealthBar(QFrame):
    """A labelled horizontal health bar widget"""
    def __init__(self, label: str, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        self._lbl = QLabel(label)
        self._lbl.setStyleSheet("color: #94A3B8; font-size: 12px; min-width: 110px;")
        self._bar = QProgressBar()
        self._bar.setRange(0, 100)
        self._bar.setTextVisible(False)
        self._bar.setFixedHeight(6)
        self._bar.setStyleSheet("""
            QProgressBar { background: #1E293B; border-radius: 3px; }
            QProgressBar::chunk { background: #10B981; border-radius: 3px; }
        """)
        self._val = QLabel("—")
        self._val.setStyleSheet("color: #E2E8F0; font-size: 12px; font-weight: 600; min-width: 50px;")
        self._val.setAlignment(Qt.AlignRight)

        layout.addWidget(self._lbl)
        layout.addWidget(self._bar, 1)
        layout.addWidget(self._val)

    def set_value(self, pct: float, label: str = "", color: str = "#10B981"):
        self._bar.setValue(int(pct))
        self._val.setText(label or f"{pct:.0f}%")
        self._bar.setStyleSheet(f"""
            QProgressBar {{ background: #1E293B; border-radius: 3px; }}
            QProgressBar::chunk {{ background: {color}; border-radius: 3px; }}
        """)


class SystemHealthPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._alert_log  = []
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

        # ── Header ────────────────────────────────────────────────
        title = QLabel("System Health")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setStyleSheet("color: #E2E8F0;")
        sub = QLabel("Overall system condition at a glance")
        sub.setStyleSheet("color: #475569; font-size: 13px;")
        layout.addWidget(title)
        layout.addWidget(sub)

        # ── Overall Health Score ──────────────────────────────────
        health_frame = QFrame()
        health_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0a1628, stop:1 #0d1117);
                border: 1px solid #10B98144;
                border-radius: 16px;
            }
        """)
        hf = QHBoxLayout(health_frame)
        hf.setContentsMargins(24, 20, 24, 20)
        hf.setSpacing(20)

        self._health_icon   = QLabel("💚")
        self._health_icon.setStyleSheet("font-size: 52px;")
        self._health_status = QLabel("GOOD")
        self._health_status.setStyleSheet("color: #10B981; font-size: 28px; font-weight: 700;")
        self._health_msg    = QLabel("All systems nominal")
        self._health_msg.setStyleSheet("color: #94A3B8; font-size: 13px;")

        hf_text = QVBoxLayout()
        hf_text.addWidget(self._health_status)
        hf_text.addWidget(self._health_msg)
        hf.addWidget(self._health_icon)
        hf.addLayout(hf_text, 1)
        layout.addWidget(health_frame)

        # ── Stat Cards Row ────────────────────────────────────────
        cards_grid = QGridLayout()
        cards_grid.setSpacing(12)
        self.card_uptime   = StatCard("UPTIME",       "⏱",  "#00D4FF")
        self.card_procs    = StatCard("PROCESSES",    "🔄", "#8B5CF6")
        self.card_bat      = StatCard("BATTERY",      "🔋", "#10B981")
        self.card_power_w  = StatCard("GPU POWER",    "⚡", "#F59E0B")

        cards_grid.addWidget(self.card_uptime,  0, 0)
        cards_grid.addWidget(self.card_procs,   0, 1)
        cards_grid.addWidget(self.card_bat,     0, 2)
        cards_grid.addWidget(self.card_power_w, 0, 3)
        layout.addLayout(cards_grid)

        # ── Resource Health Bars ──────────────────────────────────
        layout.addWidget(SectionTitle("Resource Utilisation"))
        bars_frame = QFrame()
        bars_frame.setStyleSheet("""
            QFrame {
                background: #111827;
                border: 1px solid #1E293B;
                border-radius: 12px;
            }
        """)
        bfl = QVBoxLayout(bars_frame)
        bfl.setContentsMargins(20, 16, 20, 16)
        bfl.setSpacing(12)

        self._bar_cpu  = HealthBar("CPU Usage")
        self._bar_gpu  = HealthBar("GPU Usage")
        self._bar_ram  = HealthBar("RAM Usage")
        self._bar_disk = HealthBar("Disk Usage")
        self._bar_bat  = HealthBar("Battery Level")

        for b in (self._bar_cpu, self._bar_gpu, self._bar_ram,
                  self._bar_disk, self._bar_bat):
            bfl.addWidget(b)
        layout.addWidget(bars_frame)

        # ── Disk Partitions ───────────────────────────────────────
        layout.addWidget(SectionTitle("Storage Partitions"))
        self._disk_frame = QFrame()
        self._disk_frame.setStyleSheet("""
            QFrame {
                background: #111827;
                border: 1px solid #1E293B;
                border-radius: 12px;
            }
        """)
        self._disk_layout = QVBoxLayout(self._disk_frame)
        self._disk_layout.setContentsMargins(18, 14, 18, 14)
        self._disk_layout.setSpacing(10)
        layout.addWidget(self._disk_frame)

        # ── Alert Log ────────────────────────────────────────────
        layout.addWidget(SectionTitle("Alert Log"))
        alert_frame = QFrame()
        alert_frame.setStyleSheet("""
            QFrame {
                background: #111827;
                border: 1px solid #1E293B;
                border-radius: 12px;
            }
        """)
        af_layout = QVBoxLayout(alert_frame)
        af_layout.setContentsMargins(0, 0, 0, 0)

        self._alert_list = QListWidget()
        self._alert_list.setMaximumHeight(180)
        self._alert_list.setStyleSheet("""
            QListWidget {
                background: transparent;
                border: none;
                color: #94A3B8;
                font-size: 12px;
                padding: 8px;
            }
            QListWidget::item {
                padding: 4px 8px;
                border-bottom: 1px solid #1E293B;
            }
        """)
        self._alert_list.addItem("⸻  No alerts recorded  ⸻")
        af_layout.addWidget(self._alert_list)
        layout.addWidget(alert_frame)

        layout.addStretch()
        scroll.setWidget(container)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    # ──────────────────────────────────────────────────────────────
    def add_alert(self, message: str):
        from datetime import datetime
        ts = datetime.now().strftime("%H:%M:%S")
        item = QListWidgetItem(f"[{ts}]  {message}")
        self._alert_list.insertItem(0, item)
        while self._alert_list.count() > 100:
            self._alert_list.takeItem(self._alert_list.count() - 1)

    def update_data(self, data: dict):
        cpu  = data.get("cpu",  {})
        gpu  = data.get("gpu",  {})
        ram  = data.get("ram",  {})
        disk = data.get("disk", {})
        bat  = data.get("battery", {})

        cpu_pct = cpu.get("usage",   0)
        gpu_pct = gpu.get("usage",   0)
        ram_pct = ram.get("percent", 0)
        cpu_t   = cpu.get("temp",    0)
        gpu_t   = gpu.get("temp",    0)

        # Health score
        issues = []
        if cpu_t > 90 or gpu_t > 90:
            issues.append("Overheating!")
        if ram_pct > 90:
            issues.append("RAM critically high")
        parts = disk.get("partitions", [])
        for p in parts:
            if p.get("percent", 0) > 90:
                issues.append(f"Disk {p['mountpoint']} full")

        if issues:
            self._health_icon.setText("🔴")
            self._health_status.setText("CRITICAL")
            self._health_status.setStyleSheet("color: #EF4444; font-size: 28px; font-weight: 700;")
            self._health_msg.setText("  •  ".join(issues))
        elif cpu_pct > 80 or ram_pct > 75 or cpu_t > 80:
            self._health_icon.setText("🟡")
            self._health_status.setText("MODERATE")
            self._health_status.setStyleSheet("color: #F59E0B; font-size: 28px; font-weight: 700;")
            self._health_msg.setText("Some resources under pressure")
        else:
            self._health_icon.setText("💚")
            self._health_status.setText("GOOD")
            self._health_status.setStyleSheet("color: #10B981; font-size: 28px; font-weight: 700;")
            self._health_msg.setText("All systems nominal")

        # Uptime
        boot_time = psutil.boot_time()
        import time
        secs = int(time.time() - boot_time)
        h, rem = divmod(secs, 3600)
        m, s   = divmod(rem, 60)
        self.card_uptime.set_value(f"{h}h {m}m", f"{s}s")

        # Processes
        try:
            pc = len(list(psutil.process_iter()))
        except Exception:
            pc = 0
        self.card_procs.set_value(str(pc), "processes")

        # Battery
        if bat.get("available"):
            pct_bat = bat.get("percent", 0)
            plug    = "🔌" if bat.get("plugged_in") else "🔋"
            self.card_bat.set_value(f"{plug} {pct_bat:.0f}%", bat.get("time_left", ""))
        else:
            self.card_bat.set_value("Desktop", "No battery")

        # GPU Power
        self.card_power_w.set_value(
            f"{gpu.get('power_w', 0):.0f}W",
            "GPU power draw")

        # Health bars
        def bar_color(pct):
            if pct < 60: return "#10B981"
            if pct < 80: return "#F59E0B"
            return "#EF4444"

        self._bar_cpu.set_value(cpu_pct, f"{cpu_pct:.0f}%",  bar_color(cpu_pct))
        self._bar_gpu.set_value(gpu_pct, f"{gpu_pct:.0f}%",  bar_color(gpu_pct))
        self._bar_ram.set_value(ram_pct, f"{ram_pct:.0f}%",  bar_color(ram_pct))

        disk_pct = parts[0].get("percent", 0) if parts else 0
        self._bar_disk.set_value(disk_pct, f"{disk_pct:.0f}%", bar_color(disk_pct))

        bat_pct = bat.get("percent", 0) if bat.get("available") else 100
        bat_color = "#EF4444" if bat_pct < 20 else "#F59E0B" if bat_pct < 50 else "#10B981"
        self._bar_bat.set_value(bat_pct, f"{bat_pct:.0f}%",  bat_color)

        # Disk Partitions
        while self._disk_layout.count():
            item = self._disk_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for p in parts[:6]:
            row = QHBoxLayout()
            dev  = QLabel(f"💾  {p['device']}  ({p['mountpoint']})")
            dev.setStyleSheet("color: #94A3B8; font-size: 12px; min-width: 180px;")
            info = QLabel(f"{p['used_gb']:.1f} / {p['total_gb']:.1f} GB  —  {p['percent']:.0f}%")
            info.setStyleSheet("color: #E2E8F0; font-size: 12px;")
            row.addWidget(dev)
            row.addStretch()
            row.addWidget(info)
            w = QWidget()
            w.setLayout(row)
            self._disk_layout.addWidget(w)
