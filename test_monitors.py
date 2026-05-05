import sys, time
sys.path.insert(0, '.')

# Test imports
from src.utils.theme import ThemeManager
from src.monitors.system_monitor import CPUMonitor, RAMMonitor, DiskMonitor, NetworkMonitor, BatteryMonitor
from src.monitors.gpu_monitor import GPUMonitor
from src.monitors.data_worker import DataWorker
print("All imports OK")

# Quick data check
import psutil
psutil.cpu_percent(interval=None)
time.sleep(1)

cpu = CPUMonitor()
ram = RAMMonitor()
d = cpu.update()
r = ram.update()
print(f"CPU: {d['usage']:.1f}%  freq={d['freq_ghz']:.2f}GHz  temp={d['temp']}C")
print(f"RAM: {r['percent']:.1f}%  used={r['used_gb']:.1f}GB of {r['total_gb']:.1f}GB")

gpu = GPUMonitor()
print(f"GPU info: {gpu.info}")
gd = gpu.update()
print(f"GPU: usage={gd['usage']}%  temp={gd['temp']}C  available={gd['available']}")

disk = DiskMonitor()
dk = disk.update()
print(f"Disk partitions: {len(dk['partitions'])}")

bat = BatteryMonitor()
b = bat.update()
print(f"Battery: {b}")

print("\nAll monitors working correctly!")
