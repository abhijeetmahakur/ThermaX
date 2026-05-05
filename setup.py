"""
ThermaX Setup Script — install & run helper
"""
import subprocess
import sys
import os


def run(cmd):
    print(f"\n>> {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=False)
    if result.returncode != 0:
        print(f"[WARNING] Command exited with code {result.returncode}")
    return result.returncode


def main():
    print("=" * 54)
    print("  ThermaX — Performance Control Center — Setup")
    print("=" * 54)

    python = sys.executable

    print("\n[1/3] Upgrading pip…")
    run([python, "-m", "pip", "install", "--upgrade", "pip"])

    print("\n[2/3] Installing dependencies…")
    req = os.path.join(os.path.dirname(__file__), "requirements.txt")
    run([python, "-m", "pip", "install", "-r", req])

    print("\n[3/3] Done!\n")
    print("  Run the app with:")
    print(f"      python main.py")
    print()


if __name__ == "__main__":
    main()
