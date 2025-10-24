# LePetPal — Final Task Split (v1.0-lite)

Goal: AI-first, hackathon-ready split that enables fast parallel work with a frozen integration contract and minimal dependencies.

---

## Objectives
- Deliver reliable “Give Treat” and “Play with Ball” interactions on camera.
- Keep contract and components simple: MJPEG + polling; one active command; Go Home interrupt.
- Preserve a scripted fallback for “pick up the ball” if the model lags.

---

## Integration Contract (Frozen)
- Endpoints
  - `GET /health` → `{status:"ok", api:1, version:"v0.1"}`
  - `GET /video_feed?width=1280&height=720&overlays=1` → MJPEG
  - `POST /command` → `{request_id:"uuid", status:"accepted"}`
  - `GET /status/{request_id}` → `{state, phase|null, confidence?, message?, duration_ms?}` until `succeeded|failed|aborted`
  - `POST /dispense_treat {duration_ms}` → `{status:"ok"}`
  - `POST /speak {text}` → `{status:"ok"}`
- Rules
  - Single active command; `409 busy` if another is running.
  - `go home` can interrupt any state and must preempt fast (~1s).
- Error classes: `400 invalid`, `409 busy`, `500 internal`.
- Versioning: optional `X-LePetPal-API: 1`. Any contract change requires both engineers’ sign-off.

---

## Team Roles & Ownership
- Engineer A — Backend/Robotics
  - Server, command loop + inference, hardware adapters, MJPEG overlays, safety.
- Engineer B — Frontend/Cloud
  - Next.js UI, presets, polling client, config storage, UX resilience.

---

## Workstreams & Tasks

### Engineer A — Backend/Robotics
- Must
  - Implement routes: `/health`, `/video_feed`, `/command`, `/status/{id}`, `/dispense_treat`, `/speak`.
  - In-memory command state machine with single-active-command guard.
  - Command loop: phases (`detect|approach|grasp|lift|drop|ready_to_throw`), `timeout_ms`, final states.
  - MJPEG stream with simple overlays (synthetic first, then camera).
  - Hardware adapters + mocks: `LerobotArm.home/send_joint_targets`, `ServoController.dispense(ms)`, `TTS.speak`.
  - Treat dispensing: actuate SG90 for requested duration.
  - Safety: `go home` interrupt, throw macro only from `ready_to_throw`, joint-limit checks.
  - Config via `.env` (camera index, resolution, thresholds), JSON logs.
- Should
  - Confidence gating thresholds; readable status messages.
  - Persist calibration (ROI, bowl/treat zones).
  - Minimal Sentry (color-threshold), OFF by default.
- Could
  - Token auth and CORS allowlist (only if trivial).
  - SSE upgrade after MVP.
- Definition of Done (A)
  - `/health` returns OK; `/video_feed` renders ≥15 FPS with overlays.
  - `POST /command` returns `request_id`; `/status/{id}` reaches final state.
  - `Give Treat`: `POST /dispense_treat` → delay → `get the treat` command succeeds in staged demo.
  - `Go Home` interrupts within ~1s from any state.
  - Logs show state transitions and durations; errors mapped to 400/409/500.

### Engineer B — Frontend/Cloud
- Must
  - Next.js scaffold; Config Panel for `BASE_URL` (and optional token); persist in localStorage.
  - VideoPanel renders `<img src="<BASE>/video_feed">`.
  - CommandBar with presets: Play with Ball, Give Treat, Go Home, Speak.
  - Polling client: after `POST /command`, poll `/status/{id}` every 1s until final.
  - UX states: global status chip (Idle/Executing/Error); disable buttons while executing except Go Home.
  - Error toasts; backoff on `409 busy` (0.5s→2s with jitter).
- Should
  - Mobile-responsive layout; demo-friendly visuals.
  - Clear final-state banners with success/failure copy.
- Could
  - SSE client (later); typegen from OpenAPI (later).
- Definition of Done (B)
  - Config works; valid `BASE_URL` connects and `/video_feed` renders.
  - Presets execute correct call sequences; Give Treat performs two-step flow.
  - Polling shows transitions and completion; errors surfaced clearly; backoff respected.

---

## Integration Checkpoints (No Timelines)
- IC-0: Contract sign-off. Frontend uses only frozen endpoints and shapes above.
- IC-1: LAN with stubs. Frontend renders video; `POST /command` accepted; polling reaches final (mock phases).
- IC-2: Servo + Speak. `dispense_treat` and `speak` functional; Give Treat end-to-end without model.
- IC-3: Model-in-loop. `pick up the ball` and `get the treat` via inference wrapper; `go home` interrupt verified.
- IC-4: Demo script dry run. Optional throw macro if guards pass; tune delays/thresholds.

---

## Handoffs & Artifacts
- Config
  - Backend: `.env.example` (PORT, CAMERA_INDEX, STREAM_RES, thresholds).
  - Frontend: `NEXT_PUBLIC_API_BASE` in `.env.local.example`.
- Samples
  - Example API responses (accepted, busy, failed, timeout) as JSON fixtures for QA/manual tests.
- Scripts
  - Backend `run_backend.py` (start camera, model, server).
  - Frontend `dev` and `build` scripts; README quick-start.

---

## Change Control
- Contract changes (endpoints, fields, states, errors) require A+B agreement and a version bump (`X-LePetPal-API`).
- Any non-backward-compatible change must include a short migration note in this file and the spec sheet.

---

## Risks & Mitigations
- Model reliability → Scripted fallback flag for “pick up the ball”; reduce scope to 2 behaviors if needed.
- Camera drift/lighting → Fixed mount; persist calibration; high-contrast ball/treat.
- Latency/throughput → Prefer MJPEG; limit overlay cost; keep inference loop 10–20 Hz.
- Busy pipeline → Frontend backoff on 409; clear user messaging.
- Safety → Throw only from `ready_to_throw`; joint-limit checks; `go home` always available.

---

## Acceptance Mapping (from Spec Sheet)
- AT-1 Video stream reachable with overlays (≥15 FPS).
- AT-2 Speak responds within ~1s.
- AT-3 Dispense actuates servo for duration.
- AT-4 Pick ball ≥ 2/3 from 3 positions (or fallback script proven).
- AT-5 Give treat succeeds 3× consecutively.
- AT-6 Safety: `go home` interrupts within ~1s.
- AT-7 Optional Sentry: single auto trigger with cooldown (OFF by default in MVP).

---

## Out-of-Scope (MVP)
- WebRTC, WebSockets, database, S3, analytics, routines, AI coach, CI/OpenAPI/SSE.
- Token auth unless trivial.

---

## Communication & PR Rules
- Keep PRs small and focused; reference endpoint or UI piece.
- Include testing notes (manual steps) and screenshots for UI changes.
- Flag any contract-related changes in the PR description explicitly.

---

Status: FINAL task split for v1.0-lite. Any edits must keep the integration contract intact unless both engineers agree to a version bump.

---

## BONUS FEATURES (Optional / Low Priority)
- UI polish
  - Animated overlays, sound cues, dark mode toggle.
  - Demo mode banner with quick tips.
- Frontend
  - SSE upgrade for live status (replace polling) once stable.
  - Type-safe client from OpenAPI (post-hackathon), centralized fetch wrapper.
  - Keyboard shortcuts for presets (P: Play, T: Treat, H: Home, S: Speak).
- Backend
  - Token auth (Bearer) and CORS allowlist; rate limiting on POSTs.
  - Minimal Sentry (color-threshold) auto-trigger with cooldown, toggle in config.
  - Structured metrics endpoint `/metrics` with basic counters.
- AI/Robotics
  - Additional behaviors: “place ball to zone”, “nudge object”, “stay”.
  - Simple vision assist (color mask) to stabilize detections.
  - Throw macro variants (short/long); safety playbook (auto-home on error).
- Ops
  - One-click tunnel scripts (ngrok/Cloudflare) with env injection.
  - Basic log viewer page in frontend.
  - Demo recorder (save GIF/short MP4 of last action).
