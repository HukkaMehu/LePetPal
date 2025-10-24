# LePetPal v0.1 Spec Sheet

## Product scope (MVP)
- **Primary outcome**: Remote “Give Treat” and “Play with Ball” interactions that are reliable, safe, and visually obvious on camera.
- **Supported behaviors**: `pick up the ball`, `get the treat`, `go home`, throw macro from “ready-to-throw” pose.
- **Modes**: Owner-in-the-Loop (required). Autonomous Sentry (basic trigger: ball detected).
- **Success metric (demo)**: 3 consecutive successful “Give Treat” sequences under 2 minutes end-to-end, and 1 “Play with Ball” including throw.

## System overview
- **Robot + sensing**: SO-101 arm; fixed single USB webcam covering entire workspace; simple SG90-driven treat chute; speaker.
- **AI control**: SmolVLA fine-tuned on ~100–150 teleop demos for the 3 behaviors.
- **Backend**: Python Flask serving MJPEG stream and action APIs; OpenCV overlays; lerobot hardware interface.
- **Frontend**: Next.js + Tailwind; live video; command buttons; status feed; hosted on Vercel.
- **Remote access**: Cloudflare Tunnel or ngrok HTTPS URL terminating to `http://localhost:5000`.

---

## Hardware specification
- **Robot**: SO-101 follower arm, 6 DOF, USB connected to host.
- **Camera**: 1080p UVC USB webcam, 30 FPS minimum, fixed mount (overhead or ~45°), no movement post-calibration.
- **Treat dispenser**: 3D-printed chute + SG90 servo (PWM or GPIO control via USB/SBC). Treat size consistent, non-crumbly.
- **Compute**: Laptop with Python 3.10+, PyTorch (CPU acceptable for demo if inference < 200 ms/frame) or CUDA if available.
- **Audio**: External speaker or laptop speakers.

## Safety constraints
- **Workspace**: Clearly marked keep-out zone for pet during arm motion; bowl and treat drop-zone fixed.
- **Motion limits**: Joint speed/accel caps; emergency stop method (keybinding or API `POST /command {"prompt":"go home"}`).
- **Throw macro**: Only enabled from verified “ready-to-throw” pose; disable if detection confidence < threshold or occlusion detected.

---

## AI and dataset
- **Base**: SmolVLA pretrained (from `lerobot`).
- **Inputs**: (1) RGB frame (resized to model spec), (2) 6 joint angles, (3) text instruction.
- **Output**: Short sequence of target joint angles (chunks) for closed-loop playback at 10–20 Hz.
- **Behaviors**:
  - `pick up the ball`: detect → approach → grasp → lift → “ready-to-throw” pose.
  - `get the treat`: detect landing → approach → grasp → drop into bowl.
  - `go home`: neutral safe pose, elbow clearance.
- **Data collection**:
  - 100–150 teleop demos total across behaviors; 30–50 per behavior balanced.
  - Label each demo with instruction string; keep camera fixed; consistent object colors; 2–3 positions per object.
  - Store as `LeRobotDataset` (image, state, action, instruction); versioned metadata with camera intrinsics.

---

## Backend (Flask) specification
- **Routes**
  - `GET /video_feed` → MJPEG stream with overlays.
  - `POST /command`
    - Request:
```json
{
  "prompt": "pick up the ball",
  "options": {
    "timeout_ms": 20000,
    "confidence_min": 0.6,
    "stream": true
  }
}
```
    - Response (200):
```json
{
  "request_id": "uuid-123",
  "status": "accepted"
}
```
    - Server-Sent Events (if `stream=true`) at `GET /status/{request_id}`:
```json
{ "ts": 173... , "state": "executing", "phase": "grasp", "confidence": 0.74 }
```
    - Final result:
```json
{ "status": "succeeded", "duration_ms": 8420 }
```
    - Errors: 400 (invalid prompt), 409 (busy), 504 (timeout), with `{"status":"failed","error":"..."}`
  - `POST /dispense_treat`
    - Request: `{ "duration_ms": 600 }`
    - Response: `{ "status":"ok" }` after servo actuation.
  - `POST /speak`
    - Request: `{ "text": "Good dog!" }`
    - Response: `{ "status":"ok" }`
- **States**
  - `idle` → `planning` → `executing` → `handoff_macro` (if applicable) → `succeeded|failed|aborted`
- **Overlays**
  - Bounding boxes: `ball`, `treat`; labels with confidence.
  - Status banner (Idle/Executing/Error), FPS, safety flag.
- **Config**
  - `.env`: model path, camera index, stream resolution, joint limits, tunnel base URL.
- **Security**
  - Single bearer token header `Authorization: Bearer <token>` for all POSTs (configurable).
  - CORS: allow frontend origin only.

---

## Frontend (Next.js + Tailwind)
- **Pages/components**
  - `/`: main console
    - `VideoPanel`: `<img src="<TUNNEL>/video_feed">`
    - `StatusFeed`: subscribes to `GET /status/{request_id}` via EventSource
    - `CommandBar`:
      - Presets: [Play with Ball], [Give Treat], [Go Home], [Speak “Good Dog!”]
      - Custom prompt input + Send
    - `SpeakBox`: text input + Speak button
  - `ConfigPanel` (optional): server URL, token
- **Preset logic**
  - Play with Ball: `POST /command {"prompt":"pick up the ball"}`
  - Give Treat: `POST /dispense_treat` → wait 1.5s → `POST /command {"prompt":"get the treat"}`
  - Go Home: `POST /command {"prompt":"go home"}`
  - Speak: `POST /speak`
- **UI states**
  - Global status chip: Idle / Executing / Error
  - Disable buttons while `executing` unless `Go Home` (always enabled)
  - Toasts for errors and final result
- **Performance**
  - Display latency < 500 ms; commands acknowledge < 200 ms.

---

## Autonomous Sentry (basic)
- **Trigger**: Ball detected for > 1s at confidence ≥ 0.7; system is `idle`; pet present not required.
- **Action**: Auto `POST /command {"prompt":"pick up the ball"}`; show “AI ACTIVE” overlay.
- **Rate limits**: Max 1 autonomous action every 60s; abort if owner sends a command.

---

## Throw macro
- **Handoff**: Only from verified “ready-to-throw” pose returned by `pick up the ball`.
- **Motion**: Predefined joint sequence with timestamps; total duration < 1s.
- **Guards**: Check joint limits, no self-collision segment, workspace clear flag.

---

## Logging and telemetry
- **Structured logs**: JSON lines with `ts`, `req_id`, `state`, `phase`, `confidence`, `latency_ms`.
- **Artifacts**: Optional frame snapshots on `failed` with overlay.
- **Metrics**: Success rate per behavior, avg duration, detection precision/recall (simple counters).

---

## Non-functional requirements
- **Latency**: Inference loop 10–20 Hz; end-to-end command < 15s for treat workflow.
- **Reliability**: ≥ 80% success on “Give Treat” in demo conditions.
- **Security**: Token required; tunnel URL not publicly posted.
- **Privacy**: No cloud upload of video; local-only processing.
- **Operability**: Single `run_backend.py` starts camera, model, server.

---

## Acceptance tests
- **AT-1 Video**: `/video_feed` reachable at tunnel URL; overlays visible; FPS ≥ 15.
- **AT-2 Speak**: `POST /speak` plays audio within 1s.
- **AT-3 Dispense**: `POST /dispense_treat` rotates SG90 for requested duration.
- **AT-4 Pick ball**: From 3 start positions, succeeds ≥ 2/3.
- **AT-5 Give treat**: End-to-end sequence succeeds 3 times in a row.
- **AT-6 Safety**: Emergency `go home` interrupts any behavior within 1s.
- **AT-7 Sentry**: Ball placed → auto “pick up the ball” triggers once; respects 60s cooldown.

---

## Demo script (5–6 minutes)
- **Step 1**: Show live “Robot Vision” overlays; speak “Good dog!”
- **Step 2**: Tap “Play with Ball” → grasp → ready pose → throw macro
- **Step 3**: Tap “Give Treat” → dispense → model picks and drops into bowl
- **Step 4**: Show Autonomous Sentry trigger with ball
- **Step 5**: Trigger “Go Home”; show status feed and metrics

---

## Open questions
- **Auth level**: Token only vs. simple PIN UI?
- **Pet interaction**: Any audio cues during motion?
- **Compute**: CPU-only acceptable or require CUDA for smoother control?

# Recommended Actions
- **[confirm MVP]** Approve the 3 behaviors and the acceptance tests list.
- **[risk checks]** Confirm camera placement and treat dimensions for dataset plan.
- **[security]** Decide on bearer token vs. PIN UI.

# Status
- Produced a detailed, implementation-ready spec without going deep into code. Ready to prioritize tasks or convert this into a build plan.