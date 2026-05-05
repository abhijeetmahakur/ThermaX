"""
System monitors: CPU, RAM, Disk, Network, Battery
Uses psutil for cross-platform data collection
"""

import psutil
import platform
import subprocess
from datetime import datetime


# ─────────────────────────── CPU ─────────────────────────────
class CPUMonitor:
    """Collects CPU usage, frequency, temperature"""

    def __init__(self, history_len: int = 60):
        self.history_len = history_len
        self.usage_history = [0.0] * history_len
        self.freq_history  = [0.0] * history_len
        self._info = self._get_static_info()

    def _get_static_info(self) -> dict:
        freq = psutil.cpu_freq()
        return {
            "name":         platform.processor() or "Unknown CPU",
            "cores_physical": psutil.cpu_count(logical=False) or 0,
            "cores_logical":  psutil.cpu_count(logical=True)  or 0,
            "max_freq":     round(freq.max / 1000, 1) if freq else 0.0,  # GHz
        }

    @property
    def info(self) -> dict:
        return self._info

    def update(self) -> dict:
        """Poll latest CPU stats. Returns snapshot dict."""
        usage     = psutil.cpu_percent(interval=None)
        per_core  = psutil.cpu_percent(interval=None, percpu=True)
        freq      = psutil.cpu_freq()
        cur_freq  = round(freq.current / 1000, 2) if freq else 0.0  # GHz
        temp      = self._get_temperature()

        # Update rolling history
        self.usage_history.append(usage)
        self.usage_history = self.usage_history[-self.history_len:]
        self.freq_history.append(cur_freq)
        self.freq_history = self.freq_history[-self.history_len:]

        return {
            "usage":      usage,
            "per_core":   per_core,
            "freq_ghz":   cur_freq,
            "temp":       temp,
            "usage_hist": list(self.usage_history),
            "freq_hist":  list(self.freq_history),
        }

    def _get_temperature(self) -> float:
        """Try multiple methods to get CPU temperature on Windows"""
        # Method 1: psutil (Linux/macOS mainly)
        try:
            temps = psutil.sensors_temperatures()
            if temps:
                for key in ("coretemp", "cpu_thermal", "k10temp", "acpitz"):
                    if key in temps:
                        readings = temps[key]
                        if readings:
                            return round(sum(r.current for r in readings) / len(readings), 1)
        except (AttributeError, Exception):
            pass

        # Method 2: WMI (Windows)
        try:
            import wmi
            w = wmi.WMI(namespace="root\\wmi")
            temps = w.MSAcpi_ThermalZoneTemperature()
            if temps:
                # Convert from tenths of Kelvin to Celsius
                return round((temps[0].CurrentTemperature / 10.0) - 273.15, 1)
        except Exception:
            pass

        # Method 3: OpenHardwareMonitor via WMI (if installed)
        try:
            import wmi
            w = wmi.WMI(namespace="root\\OpenHardwareMonitor")
            sensors = w.Sensor()
            for sensor in sensors:
                if sensor.SensorType == "Temperature" and "CPU" in sensor.Name:
                    return round(float(sensor.Value), 1)
        except Exception:
            pass

        return 0.0  # Unavailable


# ─────────────────────────── RAM ─────────────────────────────
class RAMMonitor:
    """Collects RAM and swap usage"""

    def __init__(self, history_len: int = 60):
        self.history_len = history_len
        self.usage_history = [0.0] * history_len
        vm = psutil.virtual_memory()
        self._total_gb = round(vm.total / (1024 ** 3), 1)

    @property
    def total_gb(self) -> float:
        return self._total_gb

    def update(self) -> dict:
        vm   = psutil.virtual_memory()
        swap = psutil.swap_memory()

        used_gb  = round(vm.used  / (1024 ** 3), 2)
        total_gb = round(vm.total / (1024 ** 3), 2)
        pct      = vm.percent

        self.usage_history.append(pct)
        self.usage_history = self.usage_history[-self.history_len:]

        return {
            "percent":    pct,
            "used_gb":    used_gb,
            "total_gb":   total_gb,
            "avail_gb":   round(vm.available / (1024 ** 3), 2),
            "swap_pct":   swap.percent,
            "swap_used":  round(swap.used  / (1024 ** 3), 2),
            "swap_total": round(swap.total / (1024 ** 3), 2),
            "usage_hist": list(self.usage_history),
        }


# ─────────────────────────── DISK ─────────────────────────────
class DiskMonitor:
    """Collects disk usage and I/O stats"""

    def __init__(self, history_len: int = 60):
        self.history_len  = history_len
        self.read_history  = [0.0] * history_len
        self.write_history = [0.0] * history_len
        self._prev_io     = psutil.disk_io_counters()
        self._prev_time   = datetime.now()
        self.partitions   = self._get_partitions()

    def _get_partitions(self) -> list:
        parts = []
        for p in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(p.mountpoint)
                parts.append({
                    "device":     p.device,
                    "mountpoint": p.mountpoint,
                    "fstype":     p.fstype,
                    "total_gb":   round(usage.total / (1024 ** 3), 1),
                    "used_gb":    round(usage.used  / (1024 ** 3), 1),
                    "free_gb":    round(usage.free  / (1024 ** 3), 1),
                    "percent":    usage.percent,
                })
            except PermissionError:
                continue
        return parts

    def update(self) -> dict:
        # Refresh partition usage
        self.partitions = self._get_partitions()

        # I/O speed
        now     = datetime.now()
        cur_io  = psutil.disk_io_counters()
        elapsed = (now - self._prev_time).total_seconds()

        read_speed  = 0.0
        write_speed = 0.0
        if elapsed > 0 and self._prev_io:
            read_speed  = round((cur_io.read_bytes  - self._prev_io.read_bytes)  / elapsed / (1024 ** 2), 2)
            write_speed = round((cur_io.write_bytes - self._prev_io.write_bytes) / elapsed / (1024 ** 2), 2)

        self._prev_io   = cur_io
        self._prev_time = now

        self.read_history.append(read_speed)
        self.read_history = self.read_history[-self.history_len:]
        self.write_history.append(write_speed)
        self.write_history = self.write_history[-self.history_len:]

        return {
            "partitions":   self.partitions,
            "read_mbps":    max(0, read_speed),
            "write_mbps":   max(0, write_speed),
            "read_hist":    list(self.read_history),
            "write_hist":   list(self.write_history),
        }


# ─────────────────────────── NETWORK ─────────────────────────────
class NetworkMonitor:
    """Collects network speed and interface data"""

    def __init__(self, history_len: int = 60):
        self.history_len   = history_len
        self.dl_history    = [0.0] * history_len
        self.ul_history    = [0.0] * history_len
        self._prev_net     = psutil.net_io_counters()
        self._prev_time    = datetime.now()

    def update(self) -> dict:
        now      = datetime.now()
        cur_net  = psutil.net_io_counters()
        elapsed  = (now - self._prev_time).total_seconds()

        dl_mbps = ul_mbps = 0.0
        if elapsed > 0:
            dl_mbps = round((cur_net.bytes_recv - self._prev_net.bytes_recv) / elapsed / (1024 ** 2), 3)
            ul_mbps = round((cur_net.bytes_sent - self._prev_net.bytes_sent) / elapsed / (1024 ** 2), 3)

        self._prev_net  = cur_net
        self._prev_time = now

        self.dl_history.append(max(0, dl_mbps))
        self.dl_history = self.dl_history[-self.history_len:]
        self.ul_history.append(max(0, ul_mbps))
        self.ul_history = self.ul_history[-self.history_len:]

        # Interface list
        ifaces = []
        for name, addrs in psutil.net_if_addrs().items():
            for addr in addrs:
                if addr.family.name in ("AF_INET",):
                    ifaces.append({"name": name, "ip": addr.address})
                    break

        return {
            "dl_mbps":   max(0, dl_mbps),
            "ul_mbps":   max(0, ul_mbps),
            "dl_hist":   list(self.dl_history),
            "ul_hist":   list(self.ul_history),
            "total_sent": round(cur_net.bytes_sent / (1024 ** 3), 3),
            "total_recv": round(cur_net.bytes_recv / (1024 ** 3), 3),
            "interfaces": ifaces,
        }


# ─────────────────────────── BATTERY ─────────────────────────────
class BatteryMonitor:
    """Collects battery status"""

    def update(self) -> dict:
        bat = psutil.sensors_battery()
        if bat is None:
            return {"available": False}

        secs_left = bat.secsleft
        if secs_left == psutil.POWER_TIME_UNLIMITED:
            time_str = "Charging (plugged in)"
        elif secs_left == psutil.POWER_TIME_UNKNOWN:
            time_str = "Calculating…"
        else:
            h, m = divmod(secs_left // 60, 60)
            time_str = f"{h}h {m}m remaining"

        return {
            "available":  True,
            "percent":    round(bat.percent, 1),
            "plugged_in": bat.power_plugged,
            "time_left":  time_str,
        }


# ─────────────────────────── PROCESSES ─────────────────────────────
class ProcessMonitor:
    """Lists running processes and supports termination"""

    def get_top_processes(self, n: int = 20) -> list:
        procs = []
        for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent", "status"]):
            try:
                info = proc.info
                procs.append({
                    "pid":    info["pid"],
                    "name":   info["name"],
                    "cpu":    round(info["cpu_percent"] or 0, 1),
                    "mem":    round(info["memory_percent"] or 0, 1),
                    "status": info["status"],
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        procs.sort(key=lambda x: x["cpu"] + x["mem"], reverse=True)
        return procs[:n]

    def kill_process(self, pid: int) -> bool:
        try:
            p = psutil.Process(pid)
            p.kill()
            return True
        except Exception:
            return False

    def free_ram(self) -> str:
        """Kill non-essential background processes"""
        killed = 0
        skip   = {"System", "svchost.exe", "lsass.exe", "csrss.exe",
                   "winlogon.exe", "explorer.exe", "python.exe",
                   "pythonw.exe", "ThermaX.exe", "dwm.exe"}
        for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
            try:
                info = proc.info
                if info["name"] in skip:
                    continue
                if (info["cpu_percent"] or 0) < 0.5 and (info["memory_percent"] or 0) < 0.2:
                    proc.kill()
                    killed += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return f"Freed memory by ending {killed} background processes"

    def set_high_priority(self, pid: int) -> bool:
        try:
            p = psutil.Process(pid)
            p.nice(psutil.HIGH_PRIORITY_CLASS)
            return True
        except Exception:
            return False
