# Integration plan for your SmolVLA policy on SO-101

You have two practical paths. I recommend validating the model with the official LeRobot control script first (A), then integrating into this backend (B).

## A) Sanity-check with the official LeRobot control script
- **Find robot COM port**
  - Windows PowerShell:
    - `python -m lerobot.scripts.find_motors_bus_port`
  - Or use the helper already in this repo:
    - `python backend/tools/find_so101_port.py`
- **Run the policy on hardware**
  - Replace values as needed (COM port and camera index):
  - PowerShell:
    ```
    python -m lerobot.scripts.control_robot `
      --robot.type="so101_follower" `
      --control.policy.path="Shrek0/my_vla_policy" `
      --control.single_task="pick up the ball" `
      --robot.port="COM8" `
      --robot.cameras="{'images0': {'type': 'opencv', 'index_or_path': 0, 'width': 320, 'height': 240, 'fps': 30}}"
    ```
- Expected: robot connects, camera grabs frames, policy runs an action loop. This verifies the model + hardware stack is good before backend integration.

## B) Integrate into this Flask backend

### 1) Environment/config
- Add to `.env` at repo root:
  - `USE_HARDWARE=true`
  - `ARM_PORT=COM8`  (update after detection)
  - `MODEL_MODE=smolvla`
  - `MODEL_PATH=Shrek0/my_vla_policy`
  - `INFERENCE_RATE_HZ=15`
  - Optional: `DEVICE=cpu` or `cuda`
  - Optional: `HF_HUB_ENABLE_HF_TRANSFER=1` for faster downloads

### 2) Model loading strategy
- Prefer using LeRobot’s policy loader API if available (to avoid re-implementing pre/post-processing). If it’s accessible, we’ll:
  - Download assets with `huggingface_hub.snapshot_download(MODEL_PATH)`.
  - Load the policy and its processors via LeRobot’s public API (preprocessor/postprocessor + model).
- Fallback (if no direct loader API):
  - Pull from HF with `snapshot_download`.
  - Load `model.safetensors` into a policy module.
  - Parse `policy_preprocessor.json` / `policy_postprocessor.json` and associated `.safetensors` to build transforms.
  - Keep transforms minimal: BGR→RGB, resize to model size (from config.json), normalize as specified, tensor to device.

### 3) Extend [ModelRunner](cci:2://file:///c:/Users/henri/Documents/hackathon/LePetPal/backend/model_runner.py:4:0-51:54) to a real smolvla path
- Pass `camera` into [ModelRunner](cci:2://file:///c:/Users/henri/Documents/hackathon/LePetPal/backend/model_runner.py:4:0-51:54) (from [app.py](cci:7://file:///c:/Users/henri/Documents/hackathon/LePetPal/backend/app.py:0:0-0:0)).
- In [ModelRunner(mode='smolvla')](cci:2://file:///c:/Users/henri/Documents/hackathon/LePetPal/backend/model_runner.py:4:0-51:54):
  - On init: download/load policy and processors, set to `eval()` on chosen device, enable `torch.inference_mode()`.
  - On each tick:
    - Grab latest frame (from [video.CameraCapture](cci:2://file:///c:/Users/henri/Documents/hackathon/LePetPal/backend/video.py:7:0-73:26)).
    - Preprocess → forward → postprocess to a 6D action vector:
      - `[shoulder_pan, shoulder_lift, elbow_flex, wrist_flex, wrist_roll, gripper]`
    - Map to targets in our chunk: `{"targets": [...], "phase": "...", "confidence": ...}`
    - Yield at `INFERENCE_RATE_HZ`.

### 4) Map actions to robot and enforce safety
- Our [ArmAdapter](cci:2://file:///c:/Users/henri/Documents/hackathon/LePetPal/backend/adapters/arm_adapter.py:12:0-110:23) now uses `send_action` with correct fields:
  - `shoulder_pan.pos`, `shoulder_lift.pos`, `elbow_flex.pos`, `wrist_flex.pos`, `wrist_roll.pos`, `gripper.pos`
- Ensure:
  - Units are radians for joints; clamp to [SafetyManager](cci:2://file:///c:/Users/henri/Documents/hackathon/LePetPal/backend/safety.py:5:0-43:19) limits.
  - Gripper mapped to 0–100 range (already used in adapter).
- Keep the “throw macro” gated by safety checks.

### 5) Testing and validation
- Local dry-run without hardware:
  - Add `DRY_RUN=1` to `.env` so [ModelRunner](cci:2://file:///c:/Users/henri/Documents/hackathon/LePetPal/backend/model_runner.py:4:0-51:54) logs first N actions and doesn’t call `send_action`.
- Hardware test via backend:
  - Restart backend: `python -m backend.run_backend`
  - Run smoke: `python -m backend.tools.smoke "http://localhost:5000" "pick up the ball"`
- If actions look good, remove `DRY_RUN` and test on the arm.

### 6) Performance tips
- Use smaller camera resolution (e.g., 320x240) to keep the inference loop smooth.
- Use `cuda` with autocast if you have a GPU and the policy supports half precision.
- Log inference latency per tick.

### 7) Fallbacks and failure handling
- If policy load fails:
  - Return a descriptive error and fall back to `scripted` mode.
- If camera fails:
  - Use the existing synthetic frame fallback; still run policy for integration sanity.

### 8) Documentation
- Update README:
  - New `.env` keys.
  - First-run behavior (HF model download).
  - Dry-run instructions.
  - Hardware checklist and troubleshooting.

# Immediate next steps
- Find and set the correct COM port:
  - `python backend/tools/find_so101_port.py`
  - Then set `ARM_PORT=COMx` in `.env`.
- Choose path:
  - Quick verify (A): run the `lerobot.scripts.control_robot` command against `Shrek0/my_vla_policy`.
  - Integration (B): I can implement the [ModelRunner](cci:2://file:///c:/Users/henri/Documents/hackathon/LePetPal/backend/model_runner.py:4:0-51:54) smolvla path, loaders, and wiring as above.

# What I need from you
- Do you want CPU or CUDA for inference?
- Confirm `Shrek0/my_vla_policy` is public; if private, set `HUGGING_FACE_HUB_TOKEN`.
- Preference: use LeRobot’s internal loader if available, or go with a light custom loader from the HF artifacts?

# Status
- Provided a concrete, step-by-step plan with both a quick validation route and full backend integration path. Ready to implement once you confirm preferences and the COM port.