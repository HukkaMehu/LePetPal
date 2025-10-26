# Backend Architecture Spec (v1.0-lite)

Scope: Minimal, hackathon-ready backend for LePetPal using LeRobot SO-101 and SmolVLA (VLA). Retains the frozen polling contract and prioritizes safety and reliability.

---

## High-Level

- API Server (Flask)
- CommandManager (single-active state machine)
- ModelRunner (SmolVLA wrapper)
- Hardware adapters: ArmAdapter(SO-101), ServoAdapter(SG90), TTSSpeaker
- SafetyManager (limits, ROI, throw guards)
- VideoPipeline: CameraCapture → OverlayRenderer → MJPEGStreamer
- StatusStore (thread-safe status for polling)
- Optional Sentry (OFF by default)

```
Frontend  -->  /command  -->  CommandManager  -->  ModelRunner  -->  ArmAdapter(SO-101)
             <-- /status/{id}  ^      |               |                 ^
                               |      |               |                 |
                               |   SafetyManager <----+-----------+     |
                               |                                  |     |
             /dispense_treat --> ServoAdapter (SG90)               |     |
             /speak          --> TTSSpeaker                        |     |
             /video_feed     <-- MJPEGStreamer <- OverlayRenderer <-+-- CameraCapture
```

---

## API Contract (frozen)
- `GET /health` → 200 `{"status":"ok","api":1,"version":"v0.1"}`
- `GET /video_feed?width&height&overlays` → 200 `multipart/x-mixed-replace; boundary=frame`
- `POST /command {prompt, options}` → 202 accepted; 400 invalid; 409 busy
- `GET /status/{id}` → 200 JSON with `state|phase|confidence|message|duration_ms`
- `POST /dispense_treat {duration_ms}` → 200 `{status:"ok"}`
- `POST /speak {text}` → 200 `{status:"ok"}`

---

## Components & Interfaces

### CommandManager
- Responsibilities: single-active job; state transitions; timeout; cancel.
- API:
  - `start(prompt: str, options: dict) -> request_id`
  - `get_status(request_id: str) -> Status`
  - `cancel_active() -> None`
- Status:
  - `state: planning|executing|handoff_macro|succeeded|failed|aborted`
  - `phase: detect|approach|grasp|lift|drop|ready_to_throw|null`
  - `confidence?: float`, `message?: str`, `duration_ms?: int`

### ModelRunner (SmolVLA)
- Inputs: `frame: np.ndarray`, `joints: np.ndarray[6]`, `instruction: str`
- Output: iterable of `Chunk` with target joint angles at 10–20 Hz and optional per-chunk confidence.
- API:
  - `load(model_path: str) -> None`
  - `infer(instruction: str, frame, joints) -> Iterable[Chunk]`

### ArmAdapter (SO-101 via lerobot)
- Responsibilities: connect, read joints, stream targets, home, stop.
- API:
  - `connect() -> None`
  - `get_joint_angles() -> np.ndarray[6]`
  - `send_joint_targets(seq: Iterable[np.ndarray[6]], rate_hz: int) -> None`
  - `home() -> None`
  - `stop() -> None`

### ServoAdapter (SG90 treat dispenser)
- `dispense(duration_ms: int) -> None`

### TTSSpeaker
- `speak(text: str) -> None`

### SafetyManager
- Checks: joint limits, ROI mask, workspace-clear flag, ready-to-throw verification.
- API:
  - `validate_targets(targets) -> bool`
  - `ready_to_throw(joints) -> bool`
  - `workspace_clear() -> bool`

### VideoPipeline
- `CameraCapture`: background thread, fixed `CAMERA_INDEX`, `STREAM_RES`.
- `OverlayRenderer`: optional boxes/labels + status banner, FPS.
- `MJPEGStreamer`: generator yielding JPEG frames with `--frame` boundary.

### StatusStore (thread-safe)
- `create(request_id)`, `update(request_id, status)`, `get(request_id)`

### Sentry (optional, OFF)
- Color-threshold ball detection; cooldown; disabled on owner command.

---

## Concurrency Model
- Camera thread: continuously updates latest frame.
- Single command worker thread: runs current job; interruptible via cancel token.
- MJPEG stream: non-blocking generator reading last frame; independent of command.
- Shared state protected by lightweight locks (or atomics) in `StatusStore` and frame buffer.

---

## Control Flows

### Command execution
1) API validates prompt, ensures no active job → `request_id`, spawn worker.
2) Worker loop:
   - Read `frame` + `joints`.
   - `for chunk in ModelRunner.infer(instruction, frame, joints):`
     - SafetyManager `validate_targets(chunk)`; if false → fail and home.
     - ArmAdapter `send_joint_targets(chunk, rate_hz)`.
     - Update `phase/confidence/message` in StatusStore.
   - If instruction == `pick up the ball` and `ready_to_throw` and `workspace_clear` → ThrowMacro.
   - Finalize status (success/fail/aborted) with duration.

### Go Home interrupt
- `cancel_active()` sets cancel flag; worker breaks loop and calls `ArmAdapter.home()`; status → `succeeded`.

---

## Safety & Performance
- Rate: 10–20 Hz target; adjust if CPU-bound.
- Timeout: default 20s per command; on timeout → `failed` then `home()`.
- ThrowMacro: deterministic 0.5–1.0s sequence; pre-check joint limits and ROI; only from `ready_to_throw`.

---

## Configuration (.env)
- `PORT=5000`
- `CAMERA_INDEX=0`
- `STREAM_RES=1280x720`
- `MODEL_PATH=/path/to/smolvla.ckpt`
- `INFERENCE_RATE_HZ=15`
- `JOINT_LIMITS=...`
- `ROI_MASK_PATH=...` (optional)
- `SENTRY_ENABLED=false`
- `SENTRY_COOLDOWN_SEC=60`

---

## Implementation Plan

1) Project skeleton
- Flask app, `.env` loader, structured logging, `/health` route.

2) Video pipeline
- `CameraCapture` with synthetic frames → real camera.
- `MJPEGStreamer` with `multipart/x-mixed-replace`; optional `OverlayRenderer`.

3) StatusStore + CommandManager skeleton
- In-memory store; single-active guard; `/status/{id}` route.

4) `/command` job thread
- Phase updates, timeout handling, cancel token for `go home`.

5) Hardware adapters (mocks first)
- `ArmAdapter` mock returning static joints; `ServoAdapter.dispense`; `TTSSpeaker.speak`.

6) SafetyManager
- Joint limits; ROI check; `ready_to_throw`; emergency home path.

7) ModelRunner integration
- Load SmolVLA; implement `infer()` yielding chunks at `INFERENCE_RATE_HZ` with confidence gating.
- Fallback scripted behavior flag if model unavailable.

8) ThrowMacro
- Guarded by `ready_to_throw` + `workspace_clear`; verify joint limits.

9) Dispense/Speak
- Wire routes to adapters; log outcomes and errors.

10) Contract smoke tests
- `/health`, `/video_feed` content-type, `/command` accept + 409 busy, `/status` finalization, `/dispense_treat`, `/speak`.

11) Calibration persistence
- Store camera config, ROI mask, bowl/treat zones.

12) Optional Sentry (OFF)
- Simple color-threshold ball detection with cooldown.

---

## Definition of Done (Backend)
- All endpoints respond per contract; `202/409/400` semantics verified.
- Video stream shows overlays at ≥15 FPS.
- Command loop executes with safety checks; `Go Home` preempts (~1s).
- Treat dispense works; Speak plays audio.
- Logs include state transitions, durations, and errors.

---

## Risks & Mitigations
- Model underperforms → enable scripted fallback; reduce behaviors.
- Camera drift/lighting → fixed mount; use high-contrast objects; persist calibration.
- Timing/latency → cap overlay work; tune rate to stable 10–20 Hz.
- Safety → throw guards; emergency home always available; joint-limit checks everywhere.
