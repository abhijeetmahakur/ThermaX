"""
ThermaX — Entry Point
Performance Control Center for Windows
"""

import sys
import os

# Ensure the project root is in the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication, QSplashScreen, QLabel
from PyQt5.QtCore    import Qt, QTimer
from PyQt5.QtGui     import QFont, QColor, QPixmap, QPainter, QLinearGradient

from src.app import MainWindow


def create_splash() -> QSplashScreen:
    """Create a futuristic splash screen"""
    pixmap = QPixmap(600, 340)
    pixmap.fill(QColor("#0A0E1A"))

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    # Gradient background
    grad = QLinearGradient(0, 0, 600, 340)
    grad.setColorAt(0.0, QColor("#0A0E1A"))
    grad.setColorAt(0.5, QColor("#0F1526"))
    grad.setColorAt(1.0, QColor("#080C18"))
    painter.fillRect(0, 0, 600, 340, grad)

    # Logo icon
    painter.setFont(QFont("Segoe UI", 52))
    painter.setPen(QColor("#00D4FF"))
    painter.drawText(0, 80, 600, 80, Qt.AlignCenter, "⬡")

    # App name
    painter.setFont(QFont("Segoe UI", 28, QFont.Bold))
    painter.setPen(QColor("#E2E8F0"))
    painter.drawText(0, 150, 600, 50, Qt.AlignCenter, "ThermaX")

    # Tagline
    painter.setFont(QFont("Segoe UI", 13))
    painter.setPen(QColor("#475569"))
    painter.drawText(0, 200, 600, 30, Qt.AlignCenter, "Performance Control Center")

    # Loading text
    painter.setFont(QFont("Segoe UI", 10))
    painter.setPen(QColor("#334155"))
    painter.drawText(0, 290, 600, 24, Qt.AlignCenter, "Loading system monitors…")

    painter.end()

    splash = QSplashScreen(pixmap, Qt.WindowStaysOnTopHint)
    splash.setWindowFlags(Qt.SplashScreen | Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
    return splash


def main():
    # High-DPI support
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps,    True)

    app = QApplication(sys.argv)
    app.setApplicationName("ThermaX")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("ThermaX")

    # Set global font
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    # Show splash
    splash = create_splash()
    splash.show()
    app.processEvents()

    # Small delay so splash is visible
    QTimer.singleShot(1800, splash.close)

    # Build main window
    window = MainWindow()

    def show_main():
        splash.close()
        window.show()
        window.raise_()

    QTimer.singleShot(1800, show_main)

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
