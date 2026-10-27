"""
Convenience launcher to run both FastAPI backend (port 8000)
and Streamlit frontend (port 8501) simultaneously in local development.
"""

import sys
import subprocess
import time
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent


def main():
    print("=" * 70)
    print("Starting TravelResolve Development Services")
    print("=" * 70)

    # 1. Start FastAPI Backend
    print("[1/2] Starting FastAPI Backend on http://127.0.0.1:8000 ...")
    api_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8000"],
        cwd=str(ROOT_DIR)
    )

    # Give backend a moment to bind port
    time.sleep(2)

    # 2. Start Streamlit Frontend
    print("[2/2] Starting Streamlit UI on http://localhost:8501 ...")
    streamlit_process = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "app/ui/streamlit_app.py", "--server.port", "8501"],
        cwd=str(ROOT_DIR)
    )

    print("\n" + "=" * 70)
    print("TravelResolve Services Initialized")
    print("  - Web Interface: http://localhost:8501")
    print("  - API Documentation: http://127.0.0.1:8000/docs")
    print("  - Service Health: http://127.0.0.1:8000/health")
    print("=" * 70)
    print("Press Ctrl+C to terminate both servers.\n")

    try:
        while True:
            time.sleep(1)
            # Check if any process terminated prematurely
            if api_process.poll() is not None:
                print("API process exited unexpectedly.")
                break
            if streamlit_process.poll() is not None:
                print("Streamlit process exited unexpectedly.")
                break
    except KeyboardInterrupt:
        print("\nStopping services...")
    finally:
        api_process.terminate()
        streamlit_process.terminate()
        print("Both services successfully stopped.")


if __name__ == "__main__":
    main()
