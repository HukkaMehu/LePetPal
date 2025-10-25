import sys
from pathlib import Path

# Add parent directory to path so backend package is importable
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=app.config.get("PORT", 5000), threaded=True)
