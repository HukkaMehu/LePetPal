# LePetPal

Backend service for the LePetPal robot. Provides a simple HTTP API to:

- Stream camera video as MJPEG.
- Accept high-level commands (e.g., "pick up the ball", "get the treat", "go home").
- Execute robot motions via an adapter that can run in mock mode or control real hardware (LeRobot SO-101 follower).
- Speak and dispense treat via simple adapters.

The backend is written in Flask and designed to be hardware-toggleable with environment variables.

## Quick Start

1) Create and activate a virtual environment (Windows PowerShell)

```pwsh
py -3 -m venv .venv
./.venv/Scripts/Activate.ps1
```

2) Install backend dependencies

```pwsh
pip install -r backend/requirements.txt
```

Optional dev tools (pytest, requests):

```pwsh
pip install -r backend/requirements-dev.txt
```

3) Configure environment

Create a .env file at the repository root:

```env
PORT=5000
USE_HARDWARE=false
MODEL_MODE=scripted
MODEL_PATH=
CAMERA_INDEX=0
STREAM_RES=1280x720
INFERENCE_RATE_HZ=15
CALIBRATION_PATH=
# If using real hardware (LeRobot), set your COM port, e.g. COM7
ARM_PORT=COM7
```

4) Run the backend (run from the repo root)

```pwsh
python -m backend.run_backend
```

Open:

- Health: http://localhost:5000/health
- Video: http://localhost:5000/video_feed

## API Endpoints

- GET `/health`
  - Returns service health information.

- GET `/video_feed`
  - MJPEG stream of the camera with optional overlays.
  - Query params: `camera`, `width`, `height`, `overlays=1|0`.

- POST `/command`
  - Body: `{ "prompt": "pick up the ball" | "get the treat" | "go home", "options": {} }`
  - Returns `request_id` and accepts the command.

- GET `/status/<request_id>`
  - Poll the status of a previously accepted command.

- POST `/dispense_treat`
  - Body: `{ "duration_ms": 600 }`
  - Simulates/controls the treat dispenser.

- POST `/speak`
  - Body: `{ "text": "Good dog!" }`
  - Text-to-speech via a stub adapter.

## Repository Structure

- `backend/app.py`
  - Flask app factory. Wires camera, status store, command manager, adapters, model, safety. Loads env via `python-dotenv`.

- `backend/run_backend.py`
  - Entrypoint to run the Flask server using the app factory.

- `backend/command_manager.py`
  - Orchestrates command execution in a worker thread. Handles interrupts ("go home") and busy states.

- `backend/status_store.py`
  - In-memory status tracking keyed by `request_id`.

- `backend/model_runner.py`
  - Produces control chunks at a fixed rate. `scripted` mode is the default demo; `smolvla` is a placeholder for model integration.

- `backend/video.py`
  - Camera capture and MJPEG streaming. Falls back to a synthetic feed if no camera is available.

- `backend/adapters/arm_adapter.py`
  - Robot arm adapter. Mock by default; intended to integrate LeRobot (SO-101 follower) when `USE_HARDWARE=true`.

- `backend/adapters/servo_adapter.py`
  - Stub servo/treat dispenser.

- `backend/adapters/tts.py`
  - Simple TTS stub.

- `backend/tools/smoke.py`
  - Quick script to hit `/health`, submit a `/command`, poll `/status`, and try `/dispense_treat` and `/speak`.

- `backend/tests/test_contract_smoke.py`
  - Contract-level smoke tests using Flask test client.

- `contracts/fixtures/*`
  - Example contract payloads returned by endpoints.

## Hardware (LeRobot) Integration

The backend supports a hardware path via `ArmAdapter`. To use a real SO-101 follower with LeRobot:

1) Install LeRobot and its prerequisites following official docs (Python version and FFmpeg may be required):

```pwsh
pip install lerobot
# If needed, install extras and PyTorch per LeRobot instructions
```

2) Set environment for hardware mode in `.env`:

```env
USE_HARDWARE=true
ARM_PORT=COM7   # or your detected COM port
MODEL_MODE=scripted
```

3) (Planned) Update `backend/adapters/arm_adapter.py` to:

- Instantiate `SO101Follower(SO101FollowerConfig(port=ARM_PORT))` in `connect()` and call `connect()`.
- Map 6D joint target arrays to driver action fields:
  - `shoulder_pan.pos`, `shoulder_lift.pos`, `elbow_flex.pos`, `wrist_flex.pos`, `wrist_roll.pos`, `gripper.pos` (0–100 range for gripper).
- Implement `home()` to send a safe neutral pose.
- Fall back to mock mode if connection fails (server should still run).

You can validate connectivity independently with:

```pwsh
python backend/simple_connect_test.py  # uses ARM_PORT or COM7 by default
```

## Testing

- Smoke test script against a running server:

```pwsh
python -m backend.tools.smoke  # optional BASE URL arg, defaults to http://localhost:5000
```

- Pytest contract tests:

```pwsh
pip install -r backend/requirements-dev.txt
python -m pytest backend/tests -q
```

## Troubleshooting

- `ModuleNotFoundError: No module named 'backend'`
  - Make sure you run from the repository root: `python -m backend.run_backend` (not from the `backend/` folder).

- `ModuleNotFoundError: No module named 'flask'`
  - Install dependencies: `pip install -r backend/requirements.txt`.

- Video stream black / camera not found
  - The service falls back to a synthetic feed. Adjust `CAMERA_INDEX`, check permissions, and ensure the camera isn’t in use by another app.

- Port already in use
  - Change `PORT` in `.env` or stop the other process using it.

- Hardware doesn’t move
  - Confirm `USE_HARDWARE=true`, set `ARM_PORT`, and verify the simple connect test works. Ensure appropriate drivers and power.
