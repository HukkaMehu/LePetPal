# Integration Point (frozen)

- **Contract v1.0-lite**
  - Endpoints: `/health`, `/video_feed`, `/command`, `/status/{id}`, `/dispense_treat`, `/speak`.
  - Rules: single active command; `409 busy`; `go home` always interrupts.
  - Status: frontend polls `/status/{id}` until `succeeded|failed|aborted`.
  - Errors: `400 invalid`, `409 busy`, `500 internal`.

# Engineer A — Backend/Robotics (AI-first priorities)

- **[highest] Implement command loop + inference wrapper**
  - `POST /command` → enqueue job → controlled loop with phases and `timeout_ms`.
  - Integrate SmolVLA wrapper with confidence gating; abort on low-confidence/timeouts.

- **Data + calibration**
  - Record 30–50 demos per behavior (ball, treat, home) with fixed camera.
  - Persist camera config, ROI/bowl/treat zones.

- **Hardware adapters**
  - `LerobotArm`: `home()`, `send_joint_targets(seq)`.
  - `ServoController.dispense(ms)`, `TTS.speak(text)`; provide mocks first.

- **Safety + throw**
  - Throw macro only from `ready_to_throw`; check joint limits and workspace clear.
  - `go home` interrupt must preempt any state fast.

- **Video**
  - MJPEG with simple overlays (ball/treat boxes, status banner).
  - Config via `.env` (camera index, resolution).

- **Optional**
  - Minimal Sentry (color-threshold) OFF by default.

# Engineer B — Frontend/Cloud (AI-first UI)

- **Scaffold + config**
  - Next.js + Tailwind. Config panel for base URL (and optional token later). Persist in localStorage.

- **Video + commands**
  - Render `<img>` from `/video_feed`.
  - CommandBar sends `POST /command`, then polls `/status/{id}` every 1s.

- **Presets + UX**
  - Play with Ball → `POST /command`.
  - Give Treat → `POST /dispense_treat` → delay → `POST /command "get the treat"`.
  - Go Home → `POST /command "go home"`.
  - Speak → `POST /speak`.
  - UI states: disable buttons while executing (except Go Home); toasts on error; status chip.

- **Resilience**
  - Backoff on `409` (0.5s → 2s with jitter).
  - Clear final-state banners (success/fail).

# Integration Handshake (no timelines)

- **Handshake tests**
  - H1: Frontend can see `/health`, render `/video_feed`.
  - H2: `POST /command` returns `request_id`; polling transitions to a final state.
  - H3: `Give Treat` preset: dispense returns ok; follow-on command reaches final.
  - H4: `409 busy` path handled by frontend with backoff.
  - H5: `go home` interrupts within ~1s from any state.

# Risks and Mitigations

- **Model not ready**: Use fallback scripted pick-up sequence behind a flag.
- **Camera drift**: Fix mount; don’t change after data collection. Persist calibration.
- **Over-scoping**: Keep Sentry and auth off until core flows stable.

# Recommended Actions

- **[confirm]** This Lite plan meets “AI coding first, no timelines” with clear roles and tasks.
- **[assign]** Name Engineer A/B so I can pin owners on the todo list.
- **[ok to proceed]** I can draft `contracts/api_v1_lite.md` content next for the repo to lock the contract.

# Status

- Plan validated for AI-first goals with clear tasks and a frozen integration contract. Todo plan updated to Lite scope and prioritized.