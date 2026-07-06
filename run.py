import subprocess
import sys
import time
import os
from pathlib import Path

def print_banner():
    banner = """
    ========================================================================
    🛡️   WELCOME TO THE COMPETITIVE INTELLIGENCE BUREAU CONTROL DECK   🛡️
    ========================================================================
    Starting full-stack application...
    - FastAPI Backend: http://localhost:8000
    - Streamlit Dashboard: http://localhost:8501
    
    Press Ctrl+C to terminate both servers cleanly.
    ========================================================================
    """
    print(banner)

def main():
    print_banner()
    
    # Get current workspace directory
    base_dir = Path(__file__).resolve().parent
    os.environ["PYTHONPATH"] = str(base_dir)

    # Launch Backend (FastAPI on Port 8000)
    # In a production Docker environment, run.py is intended to be a simple entrypoint.
    # The actual services (FastAPI and Streamlit) will be managed by Docker Compose or similar.
    # This script can be simplified to just execute the relevant service directly if not using docker-compose
    # However, for local development convenience with `python run.py`, we retain the subprocess calls.

    # For Docker Compose, the services will be started by their respective commands in docker-compose.yml.
    # This `run.py` is primarily for local development without Docker.
    print("\n💡 For local development, this script launches both backend and frontend.\n")
    print("    For production deployment with Docker, please use `docker-compose up -d`\n")
    print("========================================================================")

    # Original subprocess launching logic for local dev (retained)
    # backend_cmd = [sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
    # For local development using `python run.py`, we'll use Gunicorn
# The corrected line for Windows development
    backend_cmd = [sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
    print(f"🚀 Starting API Backend with command: {" ".join(backend_cmd)}")
    backend_process = subprocess.Popen(
        backend_cmd,
        cwd=str(base_dir),
        stdout=sys.stdout,
        stderr=sys.stderr
    )

    time.sleep(2)

    frontend_cmd = [sys.executable, "-m", "streamlit", "run", "frontend/app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
    print(f"🚀 Starting Streamlit Dashboard with command: {" ".join(frontend_cmd)}")
    frontend_process = subprocess.Popen(
        frontend_cmd,
        cwd=str(base_dir),
        stdout=sys.stdout,
        stderr=sys.stderr
    )

    try:
        while True:
            if backend_process.poll() is not None:
                print("❌ Backend server crashed. Shutting down...")
                break
            if frontend_process.poll() is not None:
                print("❌ Frontend dashboard crashed. Shutting down...")
                break
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Key interrupt detected. Terminating Competitive Intelligence Bureau processes...")
    finally:
        for process, name in [(backend_process, "Backend"), (frontend_process, "Frontend")]:
            if process.poll() is None:
                print(f"🔌 Stopping {name}...")
                process.terminate()
                try:
                    process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    print(f"⚠️ {name} did not exit gracefully, forcing kill...")
                    process.kill()
        print("✅ Clean shutdown complete. Farewell.")

if __name__ == "__main__":
    main()
