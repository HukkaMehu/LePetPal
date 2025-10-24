# LePetPal Backend (v1.0-lite)

Minimal Flask backend for LePetPal, tailored to LeRobot SO-101 + SmolVLA.

## Quick start

1) Create and activate a virtual environment (recommended)
2) Install deps
3) Run the server

```bash
# Windows PowerShell
python -m venv .venv
. .venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
$env:PYTHONPATH = "backend"
python backend/run_backend.py
```

Then open:
- Health: http://localhost:5000/health
- Video:  http://localhost:5000/video_feed

## Endpoints (frozen contract)
- GET /health → {status, api, version}
- GET /video_feed → MJPEG stream (use <img> tag)
- POST /command {prompt, options} → 202 accepted; 400 invalid; 409 busy
- GET /status/{id} → state/phase/confidence/duration_ms
- POST /dispense_treat {duration_ms} → {status: ok}
- POST /speak {text} → {status: ok}

## Configuration (.env)
Copy `.env.example` to `.env` and adjust values.

```ini
PORT=5000
CAMERA_INDEX=0
STREAM_RES=1280x720
MODEL_PATH=
INFERENCE_RATE_HZ=15
SENTRY_ENABLED=false
SENTRY_COOLDOWN_SEC=60
```

## Notes
- Camera: falls back to synthetic frames if not available.
- Adapters and model are stubbed; integrate real lerobot + SmolVLA later.
- Safety checks include joint limit validation and guarded throw macro.
