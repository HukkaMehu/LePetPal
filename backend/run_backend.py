import sys
import psutil
import os
from pathlib import Path

# Add parent directory to path so backend package is importable
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.app import create_app


def kill_existing_flask_instances():
    """Kill any existing Flask backend processes on the same port."""
    current_pid = os.getpid()
    killed_count = 0
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            # Skip current process
            if proc.info['pid'] == current_pid:
                continue
            
            cmdline = proc.info.get('cmdline', [])
            if not cmdline:
                continue
            
            # Check if it's a Python process running this script or Flask
            cmdline_str = ' '.join(cmdline).lower()
            if ('python' in proc.info['name'].lower() and 
                ('run_backend.py' in cmdline_str or 
                 'flask' in cmdline_str and 'backend' in cmdline_str)):
                print(f"Killing existing Flask backend process (PID: {proc.info['pid']})")
                proc.kill()
                proc.wait(timeout=3)
                killed_count += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
            pass
    
    if killed_count > 0:
        print(f"Killed {killed_count} existing Flask backend instance(s)")
    else:
        print("No existing Flask backend instances found")


app = create_app()

if __name__ == "__main__":
    #kill_existing_flask_instances()
    app.run(host="0.0.0.0", port=app.config.get("PORT", 5000), threaded=True)
