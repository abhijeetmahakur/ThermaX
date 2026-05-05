"""
Data Collection Worker — runs in a background QThread
Polls all monitors at regular intervals and emits a signal with fresh data
"""

import psutil
from PyQt5.QtCore import QThread, pyqtSignal, QMutex, QMutexLocker

from src.monitors.system_monitor import (
    CPUMonitor, RAMMonitor, DiskMonitor, NetworkMonitor, BatteryMonitor
)
from src.monitors.gpu_monitor import GPUMonitor


class DataWorker(QThread):
    """
    Background thread that collects all system metrics.
    Emits `data_ready` every `interval_ms` milliseconds.
    """
    data_ready = pyqtSignal(dict)

    def __init__(self, interval_ms: int = 1000, parent=None):
        super().__init__(parent)
        self.interval_ms = interval_ms
        self._running    = True
        self._mutex      = QMutex()

        # Instantiate monitors
        self.cpu     = CPUMonitor()
        self.ram     = RAMMonitor()
        self.disk    = DiskMonitor()
        self.net     = NetworkMonitor()
        self.battery = BatteryMonitor()
        self.gpu     = GPUMonitor()

        # First call to cpu_percent initialises the baseline (returns 0)
        psutil.cpu_percent(interval=None)

    def run(self):
        while self._running:
            with QMutexLocker(self._mutex):
                data = self._collect()
            self.data_ready.emit(data)
            self.msleep(self.interval_ms)

    def _collect(self) -> dict:
        cpu_data = self.cpu.update()
        gpu_data = self.gpu.update()
        ram_data = self.ram.update()
        disk_data= self.disk.update()
        net_data = self.net.update()
        bat_data = self.battery.update()

        return {
            "cpu":     cpu_data,
            "gpu":     gpu_data,
            "ram":     ram_data,
            "disk":    disk_data,
            "net":     net_data,
            "battery": bat_data,
            "cpu_info":self.cpu.info,
            "gpu_info":self.gpu.info,
            "ram_total":self.ram.total_gb,
        }

    def stop(self):
        with QMutexLocker(self._mutex):
            self._running = False
        self.wait()
