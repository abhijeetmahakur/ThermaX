# ThermaX — Performance Control Center

> A futuristic JARVIS-style system monitoring and performance optimization desktop app for Windows, built with Python + PyQt5.

![ThermaX Banner](https://img.shields.io/badge/ThermaX-Performance%20Control%20Center-00D4FF?style=for-the-badge&logo=windows)

---

## ✨ Features

| Feature | Description |
|---|---|
| 📊 Dashboard | Real-time CPU, GPU, RAM, Disk gauges + live graphs |
| ⚡ Performance Modes | Quiet / Balanced / Performance / Turbo |
| 🌡 Cooling Control | Fan modes (Auto / Max / Manual / Silent) + temp bars |
| 🎮 Gaming Boost | Kill background tasks, free RAM, elevate priority |
| 🤖 AI Optimizer | App detection + intelligent performance suggestions |
| 💚 System Health | Health score, battery, disk partitions, alert log |
| 🔔 Alert System | Overtemp, high-RAM, full-disk notifications |

---

## Quick Start

### Requirements
- Python 3.8 or newer
- Windows 10 / 11

### Install and run

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

The project also includes `test_monitors.py`, a manual hardware-dependent smoke script. It is not a platform-independent automated test suite.

No packaging build or CI workflow is configured.

---

## 📦 Required Libraries

| Library | Purpose |
|---|---|
| `PyQt5` | GUI framework |
| `psutil` | CPU, RAM, Disk, Network, Battery stats |
| `pyqtgraph` | Real-time graphs |
| `GPUtil` | NVIDIA GPU monitoring |
| `wmi` | Windows Management (CPU temp fallback) |
| `numpy` | Numerical operations |

---

## 📁 Project Structure

```
ThermaX/
├── main.py                      # Entry point
├── setup.py                     # Dependency installer
├── requirements.txt             # Python requirements
│
└── src/
    ├── app.py                   # Main window, header, sidebar
    │
    ├── monitors/
    │   ├── system_monitor.py    # CPU, RAM, Disk, Network, Battery
    │   ├── gpu_monitor.py       # NVIDIA GPU (GPUtil + nvidia-smi)
    │   └── data_worker.py       # Background polling thread
    │
    ├── panels/
    │   ├── dashboard.py         # Main overview panel
    │   ├── performance.py       # Power mode selection
    │   ├── cooling.py           # Fan control + temperature
    │   ├── gaming.py            # Gaming boost + process manager
    │   ├── ai_optimizer.py      # AI suggestions
    │   └── system_health.py     # Health score + alerts
    │
    ├── widgets/
    │   ├── circular_gauge.py    # Animated arc gauge
    │   ├── graph_widget.py      # PyQtGraph mini graphs
    │   └── stat_card.py         # Cards, buttons, alerts
    │
    └── utils/
        └── theme.py             # Dark / Light theme system
```

---

## 🎨 UI Design

- **Dark Mode** (default): Deep navy + neon blue/purple glow
- **Light Mode**: Clean slate with accent colours
- **Frameless window** with custom drag-to-move title bar
- **60 FPS-smooth** circular gauges with animation
- **Real-time graphs** powered by PyQtGraph

---

## 🔧 GPU Support

| GPU | Support |
|---|---|
| NVIDIA | ✅ Full (usage, VRAM, temp, power, fan) |
| AMD / Intel | ⚠ Partial via WMI (temp only) |
| No GPU | ✅ Graceful fallback, shows zeros |

For best results with NVIDIA, ensure **nvidia-smi** is available in PATH (bundled with drivers).

---

## ⚠️ Notes

- **CPU temperature** requires WMI or OpenHardwareMonitor on Windows.  
  Install [LibreHardwareMonitor](https://github.com/LibreHardwareMonitor/LibreHardwareMonitor) for accurate readings.
- **Fan speed control** is a software indicator only; actual fan curve hardware control requires vendor-specific tools.
- **Kill process** and **High Priority** features may require running as Administrator.

---

## 🛡 Run as Administrator (recommended)

Right-click `main.py` → "Run as Administrator" for full access to process control and priority settings.

---

## License

No project-level `LICENSE` file is present. The existing MIT statement has been removed pending confirmation of project ownership and third-party code/assets. No license is being added in this change.
