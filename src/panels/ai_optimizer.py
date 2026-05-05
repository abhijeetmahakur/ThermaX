"""
AI Smart Optimization Panel
Detects running apps, auto-adjusts performance, suggests optimizations
"""

import psutil
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QScrollArea, QFrame, QListWidget, QListWidgetItem)
from PyQt5.QtCore    import Qt, QTimer
from PyQt5.QtGui     import QFont, QColor

from src.widgets.stat_card import SectionTitle, FilledButton, GlowButton


# ── Known App Categories & Intelligence ───────────────────────────────────────
APP_INTELLIGENCE = {
    # Games
    "csgo.exe":          ("🎮 Game",       "performance", "High CPU priority recommended"),
    "valorant.exe":      ("🎮 Game",       "performance", "Close browser for +5 FPS"),
    "minecraft.exe":     ("🎮 Game",       "balanced",    "Allocate more RAM via launcher"),
    "robloxplayerbeta.exe":("🎮 Game",     "performance", "Close Discord overlay for FPS"),
    "fortnite.exe":      ("🎮 Game",       "turbo",       "Turbo Mode for best FPS"),
    "gta5.exe":          ("🎮 Game",       "turbo",       "High VRAM workload detected"),
    "cyberpunk2077.exe": ("🎮 Game",       "turbo",       "Close all background apps"),
    # Browsers
    "chrome.exe":        ("🌐 Browser",    "balanced",    "Multiple tabs consume RAM"),
    "firefox.exe":       ("🌐 Browser",    "balanced",    "High memory usage detected"),
    "msedge.exe":        ("🌐 Browser",    "balanced",    "Close unused tabs to free RAM"),
    # Creative
    "premiere.exe":      ("🎬 Editing",    "performance", "Raise render queue priority"),
    "resolve.exe":       ("🎬 Editing",    "turbo",       "GPU-intensive — Turbo Mode best"),
    "photoshop.exe":     ("🎨 Design",     "performance", "Increase scratch disk priority"),
    "blender.exe":       ("🎨 3D Render",  "turbo",       "GPU/CPU render detected"),
    # Dev
    "code.exe":          ("💻 Dev",        "balanced",    "Extensions may use CPU"),
    "pycharm64.exe":     ("💻 Dev",        "balanced",    "Heavier IDE — close unused tabs"),
    # Streaming
    "obs64.exe":         ("📹 Stream",     "performance", "Reduce encoding preset if lagging"),
    "discord.exe":       ("💬 Chat",       "quiet",       "Disable hardware accel in settings"),
    "spotify.exe":       ("🎵 Music",      "quiet",       "Runs fine on Quiet mode"),
    # System
    "python.exe":        ("🐍 Script",     "balanced",    "Script running"),
    "pythonw.exe":       ("🐍 Script",     "balanced",    "Script running"),
}

DEFAULT_SUGGESTIONS = [
    "🔍 No heavy apps detected. System is idle.",
    "✅  CPU and RAM usage are nominal.",
    "💤 Consider switching to Quiet mode to save power.",
]


class SuggestionCard(QFrame):
    """Single AI suggestion card"""

    def __init__(self, icon: str, text: str,
                 level: str = "info", parent=None):
        super().__init__(parent)
        colors = {"info": "#00D4FF", "warning": "#F59E0B", "critical": "#EF4444", "success": "#10B981"}
        color  = colors.get(level, "#00D4FF")

        self.setStyleSheet(f"""
            QFrame {{
                background: {color}0E;
                border: 1px solid {color}44;
                border-left: 3px solid {color};
                border-radius: 8px;
            }}
        """)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(12)

        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet(f"font-size: 18px; color: {color};")
        icon_lbl.setFixedWidth(26)

        text_lbl = QLabel(text)
        text_lbl.setStyleSheet("color: #E2E8F0; font-size: 12px;")
        text_lbl.setWordWrap(True)

        layout.addWidget(icon_lbl)
        layout.addWidget(text_lbl, 1)


class AIPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._last_data = {}
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
        title = QLabel("AI Smart Optimizer")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setStyleSheet("color: #E2E8F0;")
        sub = QLabel("Intelligent app detection & performance recommendations")
        sub.setStyleSheet("color: #475569; font-size: 13px;")
        layout.addWidget(title)
        layout.addWidget(sub)

        # ── AI Status Card ────────────────────────────────────────
        self._status_frame = QFrame()
        self._status_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0d1117, stop:1 #1a0a2e);
                border: 1px solid #8B5CF655;
                border-radius: 14px;
            }
        """)
        sf_layout = QHBoxLayout(self._status_frame)
        sf_layout.setContentsMargins(20, 16, 20, 16)
        sf_layout.setSpacing(16)

        ai_icon = QLabel("🤖")
        ai_icon.setStyleSheet("font-size: 40px;")

        txt_col = QVBoxLayout()
        ai_title = QLabel("ThermaX AI Engine")
        ai_title.setStyleSheet("color: #E2E8F0; font-size: 15px; font-weight: 700;")
        self._ai_status_lbl = QLabel("Scanning processes…")
        self._ai_status_lbl.setStyleSheet("color: #8B5CF6; font-size: 12px;")
        txt_col.addWidget(ai_title)
        txt_col.addWidget(self._ai_status_lbl)

        sf_layout.addWidget(ai_icon)
        sf_layout.addLayout(txt_col, 1)

        scan_btn = FilledButton("🔁  Scan Now", "#8B5CF6")
        scan_btn.clicked.connect(self._run_scan)
        sf_layout.addWidget(scan_btn)
        layout.addWidget(self._status_frame)

        # ── Detected Apps ─────────────────────────────────────────
        layout.addWidget(SectionTitle("Detected Applications"))

        self._app_frame = QFrame()
        self._app_frame.setStyleSheet("""
            QFrame {
                background: #111827;
                border: 1px solid #1E293B;
                border-radius: 12px;
            }
        """)
        self._app_layout = QVBoxLayout(self._app_frame)
        self._app_layout.setContentsMargins(16, 14, 16, 14)
        self._app_layout.setSpacing(8)
        layout.addWidget(self._app_frame)

        # ── Suggestions ───────────────────────────────────────────
        layout.addWidget(SectionTitle("AI Recommendations"))

        self._sug_frame = QFrame()
        self._sug_frame.setStyleSheet("""
            QFrame { background: transparent; }
        """)
        self._sug_layout = QVBoxLayout(self._sug_frame)
        self._sug_layout.setContentsMargins(0, 0, 0, 0)
        self._sug_layout.setSpacing(8)
        layout.addWidget(self._sug_frame)

        # ── Resource Summary ──────────────────────────────────────
        layout.addWidget(SectionTitle("System Snapshot"))
        self._snap_frame = QFrame()
        self._snap_frame.setStyleSheet("""
            QFrame {
                background: #111827;
                border: 1px solid #1E293B;
                border-radius: 12px;
            }
        """)
        snap_layout = QVBoxLayout(self._snap_frame)
        snap_layout.setContentsMargins(18, 14, 18, 14)
        snap_layout.setSpacing(6)

        self._snap_rows = {}
        for key in ("CPU Load", "RAM Used", "GPU Load", "Disk Read", "Network"):
            row = QHBoxLayout()
            lbl = QLabel(key)
            lbl.setStyleSheet("color: #94A3B8; font-size: 12px;")
            val = QLabel("—")
            val.setStyleSheet("color: #E2E8F0; font-size: 12px; font-weight: 600;")
            row.addWidget(lbl)
            row.addStretch()
            row.addWidget(val)
            snap_layout.addLayout(row)
            self._snap_rows[key] = val

        layout.addWidget(self._snap_frame)
        layout.addStretch()

        scroll.setWidget(container)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    # ──────────────────────────────────────────────────────────────
    def _run_scan(self):
        self._ai_status_lbl.setText("🔄  Scanning…")
        self.update_data(self._last_data)

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def update_data(self, data: dict):
        self._last_data = data
        cpu  = data.get("cpu",  {})
        gpu  = data.get("gpu",  {})
        ram  = data.get("ram",  {})
        disk = data.get("disk", {})
        net  = data.get("net",  {})

        # ── Snapshot ──────────────────────────────────────────────
        self._snap_rows["CPU Load"].setText(f"{cpu.get('usage', 0):.0f}%")
        self._snap_rows["RAM Used"].setText(
            f"{ram.get('used_gb', 0):.1f} / {ram.get('total_gb', 0):.1f} GB")
        self._snap_rows["GPU Load"].setText(f"{gpu.get('usage', 0):.0f}%")
        parts = disk.get("partitions", [])
        self._snap_rows["Disk Read"].setText(
            f"{disk.get('read_mbps', 0):.1f} MB/s")
        self._snap_rows["Network"].setText(
            f"↓{net.get('dl_mbps', 0)*1000:.0f} KB/s  "
            f"↑{net.get('ul_mbps', 0)*1000:.0f} KB/s")

        # ── Detect Apps ───────────────────────────────────────────
        self._clear_layout(self._app_layout)
        detected = []
        try:
            proc_names = {p.name().lower() for p in psutil.process_iter(["name"])}
        except Exception:
            proc_names = set()

        for proc_name, (category, rec_mode, tip) in APP_INTELLIGENCE.items():
            if proc_name.lower() in proc_names:
                detected.append((proc_name, category, rec_mode, tip))

        if detected:
            for proc_name, category, rec_mode, tip in detected[:8]:
                row = QHBoxLayout()
                cat_lbl  = QLabel(category)
                cat_lbl.setStyleSheet("color: #00D4FF; font-size: 12px; font-weight: 600; min-width: 100px;")
                name_lbl = QLabel(proc_name)
                name_lbl.setStyleSheet("color: #E2E8F0; font-size: 12px;")
                mode_colors = {
                    "quiet": "#06B6D4", "balanced": "#10B981",
                    "performance": "#8B5CF6", "turbo": "#EF4444",
                }
                mc = mode_colors.get(rec_mode, "#94A3B8")
                mode_lbl = QLabel(f"→ {rec_mode.capitalize()}")
                mode_lbl.setStyleSheet(f"color: {mc}; font-size: 11px; font-weight: 700;")
                row.addWidget(cat_lbl)
                row.addWidget(name_lbl, 1)
                row.addWidget(mode_lbl)
                self._app_layout.addLayout(row)
        else:
            no_lbl = QLabel("No known heavy applications detected. System is idle.")
            no_lbl.setStyleSheet("color: #475569; font-size: 12px; font-style: italic;")
            self._app_layout.addWidget(no_lbl)

        # ── AI Suggestions ────────────────────────────────────────
        self._clear_layout(self._sug_layout)
        suggestions = self._generate_suggestions(cpu, gpu, ram, disk, detected)
        for icon, text, level in suggestions:
            self._sug_layout.addWidget(SuggestionCard(icon, text, level))

        self._ai_status_lbl.setText(
            f"✅  Scan complete — {len(detected)} apps monitored")

    def _generate_suggestions(self, cpu, gpu, ram, disk, detected) -> list:
        sug = []
        cpu_pct = cpu.get("usage", 0)
        gpu_pct = gpu.get("usage", 0)
        ram_pct = ram.get("percent", 0)
        cpu_t   = cpu.get("temp", 0)
        gpu_t   = gpu.get("temp", 0)
        parts   = disk.get("partitions", [])

        if cpu_t > 85:
            sug.append(("🔥", f"CPU temperature critical ({cpu_t:.0f}°C). Switch to Max fan speed!", "critical"))
        elif cpu_t > 75:
            sug.append(("⚠", f"CPU is warm ({cpu_t:.0f}°C). Consider increasing fan speed.", "warning"))

        if gpu_t > 85:
            sug.append(("🔥", f"GPU temperature critical ({gpu_t:.0f}°C). Reduce GPU load.", "critical"))

        if ram_pct > 85:
            sug.append(("⚠", f"RAM usage very high ({ram_pct:.0f}%). Use Gaming Boost → Free RAM.", "warning"))
        elif ram_pct > 70:
            sug.append(("💡", f"RAM at {ram_pct:.0f}%. Close unused browser tabs to free memory.", "info"))

        if parts:
            for p in parts:
                if p.get("percent", 0) > 90:
                    sug.append(("💾", f"Disk {p['mountpoint']} nearly full ({p['percent']:.0f}%). Free up space.", "warning"))

        if any(r in ("performance", "turbo") for _, _, r, _ in detected):
            sug.append(("🎮", "Game detected! Switch to Performance or Turbo mode for best FPS.", "success"))

        if cpu_pct > 80:
            sug.append(("⚡", f"CPU load high ({cpu_pct:.0f}%). Close background apps via Gaming panel.", "warning"))

        if not sug:
            sug = [
                ("✅", "System is performing well. No immediate action needed.", "success"),
                ("💤", "CPU/GPU temps are comfortable. Quiet mode saves power while idle.", "info"),
            ]

        return sug
