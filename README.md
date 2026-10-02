# ThermaX — Windows Performance Control Center

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows%2010%20%7C%2011-0078D6?logo=windows&logoColor=white)](https://microsoft.com/windows)
[![PyQt5](https://img.shields.io/badge/GUI-PyQt5-41CD52?logo=qt&logoColor=white)](https://pypi.org/project/PyQt5/)
[![CI](https://github.com/abhijeetmahakur/ThermaX/actions/workflows/ci.yml/badge.svg)](https://github.com/abhijeetmahakur/ThermaX/actions)

A futuristic, JARVIS-inspired desktop telemetry HUD and performance tuning suite for Windows. ThermaX gives power users, gamers, and developers real-time insights into system health, GPU metrics, thermal states, and process workloads with low resource footprint.

---

## 💾 Download & Quick Run

### Option 1: Standalone Windows Executable (.exe)
You can download the pre-compiled standalone executable directly without installing Python:
1. Navigate to the **[Latest Release (v1.0.0)](https://github.com/abhijeetmahakur/ThermaX/releases/latest)**.
2. Download `ThermaX.exe`.
3. Double-click `ThermaX.exe` to launch (Run as Administrator for full process priority and telemetry privileges).

### Option 2: Run from Source
```powershell
# Clone the repository
git clone https://github.com/abhijeetmahakur/ThermaX.git
cd ThermaX

# Set up virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Launch application
python main.py
```

---

## 📸 Screenshots & UI Showcase

<!--
  PLACEHOLDER INSTRUCTION:
  1. Launch ThermaX (python main.py) on a Windows 10/11 desktop.
  2. Press Win + Shift + S to take clean window screenshots.
  3. Save the screenshots inside an `assets/` folder as `dashboard.png` and `gaming_boost.png`.
-->

| Real-Time Telemetry Dashboard | Gaming Boost & Tuning |
| :---: | :---: |
| ![ThermaX Dashboard Demo](https://placehold.co/600x380/0A0E1A/00D4FF?text=ThermaX+Dashboard+HUD+Screenshot) | ![ThermaX Boost Mode](https://placehold.co/600x380/0F1526/FF4DC4?text=Gaming+Boost+%26+Fan+Control+Screenshot) |
| *Live CPU, GPU, RAM, Disk arc gauges & dynamic PyQtGraph charts* | *Process manager, power mode switching, and hardware advisory* |

---

## ✨ Key Features

- **Real-Time Telemetry HUD:** High-DPI, 60 FPS animated arc gauges for CPU, GPU, RAM, Disk, and Network bandwidth.
- **Dynamic PyQtGraph Visualizer:** Fluid real-time waveform history tracking processor and memory load over time.
- **Power Mode Switcher:** Rapidly switch between Quiet, Balanced, Performance, and Turbo hardware profiles.
- **Thermal & Fan Status:** Track temperatures with multi-tiered alert thresholds and visual warning indicators.
- **Gaming Boost Engine:** Detects gaming workloads, frees inactive memory buffers, and elevates active process priority.
- **AI Hardware Advisor:** System health scoring algorithm with intelligent recommendations to prevent throttling.
- **Modern Frameless UI:** Dark-mode cyber-aesthetic with custom window controls and smooth title-bar dragging.

---

## 🛠 Tech Stack

| Component | Technology | Description |
| :--- | :--- | :--- |
| **Language** | Python 3.8+ | Core logic & multi-threaded telemetry workers |
| **GUI Framework** | PyQt5 | Custom painted widgets, animations, frameless styling |
| **Plotting Engine** | PyQtGraph | High-performance hardware-accelerated time-series graphing |
| **System Metrics** | `psutil`, `pywin32`, `wmi` | Low-level OS, CPU, RAM, disk, and sensor hooks |
| **GPU Analytics** | `GPUtil` + `nvidia-smi` | Dedicated NVIDIA GPU memory, power, clock, and temp monitor |
| **Packaging** | PyInstaller | Standalone single-file Windows executable generation |

---

## 📦 Building Standalone .exe with PyInstaller

To bundle ThermaX into a portable `.exe` on your Windows machine:

```powershell
# Ensure pyinstaller is installed
pip install pyinstaller

# Build single-file executable with embedded assets
pyinstaller --noconsole --onefile --name "ThermaX" --add-data "src;src" main.py
```

The resulting executable will be created in `dist/ThermaX.exe`.

### Steps to Publish on GitHub Releases:
1. Go to your repository page: `https://github.com/abhijeetmahakur/ThermaX`.
2. Click **Releases** > **Draft a new release**.
3. Set tag version to `v1.0.0` and title to `ThermaX v1.0.0 — Official Windows Release`.
4. Attach `dist/ThermaX.exe` into the binary attachment box.
5. Click **Publish release**.

---

## 📂 Project Structure

```
ThermaX/
├── .github/
│   └── workflows/
│       └── ci.yml               # GitHub Actions build & test workflow
├── src/
│   ├── app.py                   # Main window container, sidebar, and layout
│   ├── monitors/
│   │   ├── system_monitor.py    # CPU, RAM, Disk, Battery telemetry
│   │   ├── gpu_monitor.py       # NVIDIA GPU & WMI sensor monitoring
│   │   └── data_worker.py       # Background QThread for non-blocking polling
│   ├── panels/
│   │   ├── dashboard.py         # Main gauges and live chart view
│   │   ├── performance.py       # Power mode profiles
│   │   ├── cooling.py           # Fan controls & thermal monitoring
│   │   ├── gaming.py            # Process optimizer & memory purge
│   │   ├── ai_optimizer.py      # Automated system diagnostics
│   │   └── system_health.py     # Partition checks and warning logs
│   ├── widgets/
│   │   ├── circular_gauge.py    # Custom animated QPainter circular gauge
│   │   ├── graph_widget.py      # PyQtGraph real-time time-series widget
│   │   └── stat_card.py         # Modern stat cards & badge widgets
│   └── utils/
│       └── theme.py             # Cyberpunk dark & clean slate theme definitions
├── main.py                      # Application launcher with animated splash screen
├── requirements.txt             # Python runtime dependencies
├── setup.py                     # Project configuration script
├── .gitignore                   # Ignored files (pycache, dist, virtual environments)
├── LICENSE                      # MIT License
└── README.md                    # Documentation
```

---

## 🗺 Roadmap & Future Improvements

- [ ] Support for AMD Radeon GPU metrics via ADLX/ROCm wrapper
- [ ] Tray minimization mode with background threshold toast notifications
- [ ] Customizable theme editor (custom neon accent colors)
- [ ] Automated game process detection profiles with launch triggers

---

## 👨‍💻 Author

**Abhijeet Mahakur**
- GitHub: [@abhijeetmahakur](https://github.com/abhijeetmahakur)
- LinkedIn: [Abhijeet Mahakur](https://www.linkedin.com/in/abhijeetmahakur/)
- Location: Bhubaneswar, India

---

## 📄 License

This project is licensed under the [MIT License](LICENSE) - Copyright (c) 2026 Abhijeet Mahakur.
