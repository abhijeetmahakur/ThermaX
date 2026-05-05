"""
Dashboard Panel — main overview with gauges, stat cards, and quick graphs.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                              QLabel, QScrollArea, QFrame, QSizePolicy)
from PyQt5.QtCore    import Qt
from PyQt5.QtGui     import QFont

from src.widgets.circular_gauge import CircularGauge
from src.widgets.graph_widget   import MiniGraph, DualGraph
from src.widgets.stat_card      import StatCard, SectionTitle


class DashboardPanel(QWidget):
    """
    Main dashboard: circular gauges + stat cards + mini graphs.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        # Outer scroll area
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        container = QWidget()
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(24, 20, 24, 24)
        main_layout.setSpacing(20)

        # ── Header ──────────────────────────────────────────────
        header = QHBoxLayout()
        title  = QLabel("System Overview")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setStyleSheet("color: #E2E8F0;")
        subtitle = QLabel("Real-time performance monitoring")
        subtitle.setStyleSheet("color: #475569; font-size: 13px;")

        vbox = QVBoxLayout()
        vbox.addWidget(title)
        vbox.addWidget(subtitle)
        header.addLayout(vbox)
        header.addStretch()

        # Live indicator
        live_dot = QLabel("● LIVE")
        live_dot.setStyleSheet("color: #10B981; font-size: 11px; font-weight: 700; letter-spacing: 1px;")
        header.addWidget(live_dot)
        main_layout.addLayout(header)

        # ── Circular Gauges row ──────────────────────────────────
        main_layout.addWidget(SectionTitle("Core Metrics"))
        gauges_row = QHBoxLayout()
        gauges_row.setSpacing(20)

        self.cpu_gauge  = CircularGauge("CPU",  "%",  "#00D4FF", size=170)
        self.gpu_gauge  = CircularGauge("GPU",  "%",  "#8B5CF6", size=170)
        self.ram_gauge  = CircularGauge("RAM",  "%",  "#10B981", size=170)
        self.disk_gauge = CircularGauge("DISK", "%",  "#F59E0B", size=170)

        for g in (self.cpu_gauge, self.gpu_gauge, self.ram_gauge, self.disk_gauge):
            wrapper = QWidget()
            wrapper.setStyleSheet("""
                background: #111827;
                border: 1px solid #1E293B;
                border-radius: 14px;
            """)
            wl = QVBoxLayout(wrapper)
            wl.setContentsMargins(16, 16, 16, 16)
            wl.setAlignment(Qt.AlignCenter)
            wl.addWidget(g, alignment=Qt.AlignCenter)
            gauges_row.addWidget(wrapper)

        main_layout.addLayout(gauges_row)

        # ── Stat Cards grid ──────────────────────────────────────
        main_layout.addWidget(SectionTitle("Detailed Stats"))
        cards_grid = QGridLayout()
        cards_grid.setSpacing(12)

        self.card_cpu_temp  = StatCard("CPU TEMP",   "🌡", "#EF4444")
        self.card_cpu_freq  = StatCard("CPU CLOCK",  "⚡", "#00D4FF")
        self.card_gpu_temp  = StatCard("GPU TEMP",   "🌡", "#8B5CF6")
        self.card_vram      = StatCard("VRAM",       "📦", "#8B5CF6")
        self.card_ram_used  = StatCard("RAM USED",   "🧠",  "#10B981")
        self.card_disk_io   = StatCard("DISK I/O",   "💾", "#F59E0B")
        self.card_net_dl    = StatCard("DOWNLOAD",   "⬇",  "#F472B6")
        self.card_net_ul    = StatCard("UPLOAD",     "⬆",  "#F472B6")

        cards = [self.card_cpu_temp, self.card_cpu_freq,
                 self.card_gpu_temp, self.card_vram,
                 self.card_ram_used, self.card_disk_io,
                 self.card_net_dl,   self.card_net_ul]

        for i, card in enumerate(cards):
            cards_grid.addWidget(card, i // 4, i % 4)

        main_layout.addLayout(cards_grid)

        # ── Mini Graphs ──────────────────────────────────────────
        main_layout.addWidget(SectionTitle("Activity Graphs"))
        graphs_row = QHBoxLayout()
        graphs_row.setSpacing(12)

        graph_specs = [
            ("CPU Usage",     "#00D4FF"),
            ("GPU Usage",     "#8B5CF6"),
            ("RAM Usage",     "#10B981"),
            ("Network",       "#F472B6"),
        ]

        self._graphs = {}
        for label, color in graph_specs:
            frame = QFrame()
            frame.setStyleSheet("""
                QFrame {
                    background: #111827;
                    border: 1px solid #1E293B;
                    border-radius: 10px;
                }
            """)
            fl = QVBoxLayout(frame)
            fl.setContentsMargins(12, 10, 12, 10)
            fl.setSpacing(6)

            lbl = QLabel(label)
            lbl.setStyleSheet(f"color: {color}; font-size: 11px; font-weight: 600; letter-spacing: 1px;")

            if label == "Network":
                graph = DualGraph(color1="#00D4FF", color2="#F472B6", y_max=10)
            else:
                graph = MiniGraph(color=color, y_max=100)

            graph.setMinimumHeight(90)
            fl.addWidget(lbl)
            fl.addWidget(graph)

            graphs_row.addWidget(frame)
            self._graphs[label] = graph

        main_layout.addLayout(graphs_row)
        main_layout.addStretch()

        scroll.setWidget(container)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    # ── Data update ───────────────────────────────────────────────
    def update_data(self, data: dict):
        cpu  = data.get("cpu",  {})
        gpu  = data.get("gpu",  {})
        ram  = data.get("ram",  {})
        disk = data.get("disk", {})
        net  = data.get("net",  {})

        # Gauges
        cpu_temp = cpu.get("temp", 0)
        self.cpu_gauge.set_value(cpu.get("usage", 0),
                                  f"{cpu.get('freq_ghz', 0):.1f} GHz")
        self.gpu_gauge.set_value(gpu.get("usage", 0),
                                  f"{gpu.get('temp', 0):.0f}°C")
        self.ram_gauge.set_value(ram.get("percent", 0),
                                  f"{ram.get('used_gb', 0):.1f} GB")

        # Disk: use first partition's percent
        disk_pct = 0
        parts = disk.get("partitions", [])
        if parts:
            disk_pct = parts[0].get("percent", 0)
        self.disk_gauge.set_value(disk_pct,
                                   f"{disk.get('read_mbps', 0):.1f} MB/s")

        # Stat cards
        self.card_cpu_temp.set_value(
            f"{cpu_temp:.0f}°C" if cpu_temp else "N/A",
            "Temperature")
        self.card_cpu_freq.set_value(
            f"{cpu.get('freq_ghz', 0):.2f} GHz",
            f"{cpu.get('usage', 0):.0f}% load")
        self.card_gpu_temp.set_value(
            f"{gpu.get('temp', 0):.0f}°C",
            "GPU Temperature")
        self.card_vram.set_value(
            f"{gpu.get('vram_pct', 0):.0f}%",
            f"{gpu.get('vram_used_gb', 0):.1f} / {gpu.get('vram_total_gb', 0):.1f} GB")
        self.card_ram_used.set_value(
            f"{ram.get('used_gb', 0):.1f} GB",
            f"of {ram.get('total_gb', 0):.1f} GB")
        self.card_disk_io.set_value(
            f"R: {disk.get('read_mbps', 0):.1f} MB/s",
            f"W: {disk.get('write_mbps', 0):.1f} MB/s")
        self.card_net_dl.set_value(
            f"{net.get('dl_mbps', 0)*1000:.0f} KB/s",
            "Download speed")
        self.card_net_ul.set_value(
            f"{net.get('ul_mbps', 0)*1000:.0f} KB/s",
            "Upload speed")

        # Graphs
        self._graphs["CPU Usage"].update_data(cpu.get("usage_hist", []))
        self._graphs["GPU Usage"].update_data(gpu.get("usage_hist", []))
        self._graphs["RAM Usage"].update_data(ram.get("usage_hist", []))
        self._graphs["Network"].update_data(
            net.get("dl_hist", []),
            net.get("ul_hist", []))
