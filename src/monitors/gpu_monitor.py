"""
GPU Monitor — supports NVIDIA (via GPUtil) with AMD/Intel fallback
"""

import subprocess
import re

try:
    import GPUtil
    GPUTIL_AVAILABLE = True
except ImportError:
    GPUTIL_AVAILABLE = False


class GPUMonitor:
    """
    Real-time GPU monitoring.
    Primary: GPUtil (NVIDIA)
    Fallback: nvidia-smi subprocess / placeholder
    """

    def __init__(self, history_len: int = 60):
        self.history_len   = history_len
        self.usage_history = [0.0] * history_len
        self.vram_history  = [0.0] * history_len
        self.temp_history  = [0.0] * history_len
        self._info         = None
        self._detect_gpu()

    def _detect_gpu(self):
        """Try to detect GPU and set backend"""
        if GPUTIL_AVAILABLE:
            try:
                gpus = GPUtil.getGPUs()
                if gpus:
                    gpu = gpus[0]
                    self._info = {
                        "name":       gpu.name,
                        "vram_total": round(gpu.memoryTotal / 1024, 1),
                        "driver":     gpu.driver,
                        "backend":    "gputil",
                    }
                    return
            except Exception:
                pass

        # Try nvidia-smi fallback
        info = self._nvidia_smi_info()
        if info:
            self._info = info
            self._info["backend"] = "nvidiasmi"
            return

        # Generic unknown GPU
        self._info = {
            "name":       "Unknown GPU",
            "vram_total": 0,
            "driver":     "N/A",
            "backend":    "none",
        }

    def _nvidia_smi_info(self) -> dict:
        """Parse static GPU info from nvidia-smi"""
        try:
            out = subprocess.check_output(
                ["nvidia-smi", "--query-gpu=name,memory.total,driver_version",
                 "--format=csv,noheader,nounits"],
                timeout=4, stderr=subprocess.DEVNULL
            ).decode().strip()
            parts = [p.strip() for p in out.split(",")]
            if len(parts) >= 3:
                return {
                    "name":       parts[0],
                    "vram_total": round(int(parts[1]) / 1024, 1),
                    "driver":     parts[2],
                }
        except Exception:
            pass
        return {}

    @property
    def info(self) -> dict:
        return self._info or {}

    def update(self) -> dict:
        """Poll GPU stats. Returns snapshot dict."""
        if GPUTIL_AVAILABLE and self._info.get("backend") == "gputil":
            return self._update_gputil()
        elif self._info.get("backend") == "nvidiasmi":
            return self._update_nvidiasmi()
        else:
            return self._dummy()

    def _update_gputil(self) -> dict:
        try:
            gpus = GPUtil.getGPUs()
            if not gpus:
                return self._dummy()
            gpu = gpus[0]
            usage    = round(gpu.load * 100, 1)
            vram_pct = round((gpu.memoryUsed / gpu.memoryTotal) * 100, 1) if gpu.memoryTotal else 0
            vram_gb  = round(gpu.memoryUsed / 1024, 2)
            temp     = round(gpu.temperature, 1) if gpu.temperature else 0.0

            self._append(usage, vram_pct, temp)
            return {
                "usage":       usage,
                "vram_pct":    vram_pct,
                "vram_used_gb":vram_gb,
                "vram_total_gb": self._info["vram_total"],
                "temp":        temp,
                "fan_pct":     0,     # GPUtil doesn't expose fan
                "power_w":     0,
                "usage_hist":  list(self.usage_history),
                "vram_hist":   list(self.vram_history),
                "temp_hist":   list(self.temp_history),
                "available":   True,
            }
        except Exception:
            return self._dummy()

    def _update_nvidiasmi(self) -> dict:
        try:
            out = subprocess.check_output(
                ["nvidia-smi",
                 "--query-gpu=utilization.gpu,memory.used,memory.total,temperature.gpu,fan.speed,power.draw",
                 "--format=csv,noheader,nounits"],
                timeout=4, stderr=subprocess.DEVNULL
            ).decode().strip()
            parts = [p.strip() for p in out.split(",")]
            usage    = float(parts[0])
            vram_used = float(parts[1])
            vram_tot  = float(parts[2])
            temp     = float(parts[3])
            fan      = float(parts[4]) if parts[4] != "[N/A]" else 0.0
            power    = float(re.sub(r"[^\d.]", "", parts[5])) if len(parts) > 5 else 0.0
            vram_pct = round((vram_used / vram_tot) * 100, 1) if vram_tot else 0

            self._append(usage, vram_pct, temp)
            return {
                "usage":        usage,
                "vram_pct":     vram_pct,
                "vram_used_gb": round(vram_used / 1024, 2),
                "vram_total_gb":round(vram_tot  / 1024, 2),
                "temp":         temp,
                "fan_pct":      fan,
                "power_w":      power,
                "usage_hist":   list(self.usage_history),
                "vram_hist":    list(self.vram_history),
                "temp_hist":    list(self.temp_history),
                "available":    True,
            }
        except Exception:
            return self._dummy()

    def _dummy(self) -> dict:
        self._append(0, 0, 0)
        return {
            "usage":        0.0,
            "vram_pct":     0.0,
            "vram_used_gb": 0.0,
            "vram_total_gb":self._info.get("vram_total", 0),
            "temp":         0.0,
            "fan_pct":      0.0,
            "power_w":      0.0,
            "usage_hist":   list(self.usage_history),
            "vram_hist":    list(self.vram_history),
            "temp_hist":    list(self.temp_history),
            "available":    False,
        }

    def _append(self, u, v, t):
        self.usage_history.append(u)
        self.usage_history = self.usage_history[-self.history_len:]
        self.vram_history.append(v)
        self.vram_history  = self.vram_history[-self.history_len:]
        self.temp_history.append(t)
        self.temp_history  = self.temp_history[-self.history_len:]
