#!/usr/bin/env python3
"""Test a trained LeRobot policy stored in `last/pretrained_model` (single file).

What it does
- Loads policy config and weights from local directory
- Loads saved pre/post processor pipelines
- Runs inference on an image, webcam frame, or live SO-101 robot

Usage (macOS, zsh):
    # Image or webcam
    python test_trained_model.py --image path/to.jpg
    python test_trained_model.py --camera 0

    # Robot (SO-101 follower) with an OpenCV camera
    python test_trained_model.py --robot --robot-port /dev/tty.usbmodemXXXX --robot-camera-index 0
"""

import argparse
import sys
from pathlib import Path

import cv2
import numpy as np
import torch


def _ensure_repo_on_path(repo_root: Path):
        """Add lerobot/src to sys.path to import without install."""
        src = repo_root / "src"
        if str(src) not in sys.path:
                sys.path.insert(0, str(src))
#!/usr/bin/env python3
"""Test a trained LeRobot policy stored in `lerobot/last/pretrained_model`.

This script:
- Loads the policy config and weights from a local directory
- Loads the saved pre/post processor pipelines
- Captures a frame from webcam (or reads an image) and optional robot state
- Runs one forward pass to predict an action

CLI examples:
  python test_trained_model.py \
    --model-dir lerobot/last/pretrained_model \
    --camera 0 \
    --state 0 0 0 0 0 0

  python test_trained_model.py \
    --model-dir lerobot/last/pretrained_model \
    --image sample.jpg \
    --state 0 0 0 0 0 0
"""
from typing import List


def _ensure_repo_on_path(repo_root: Path):
    """Add lerobot src to sys.path so imports work without pip install."""
    src = repo_root / "src"
    if str(src) not in sys.path:
        sys.path.insert(0, str(src))


def load_policy_and_processors(model_ref: str | Path):
    from lerobot.configs.policies import PreTrainedConfig
    from lerobot.policies.factory import get_policy_class
    from lerobot.processor.pipeline import DataProcessorPipeline

    # Load config (auto-adapts device if original device not available)
    cfg = PreTrainedConfig.from_pretrained(model_ref)

    # Load policy class and weights from local directory
    policy_cls = get_policy_class(cfg.type)
    policy = policy_cls.from_pretrained(model_ref, config=cfg)

    # Load saved pre/post pipelines from the model directory
    # Override preprocessor device step to use the current available device (avoids 'cuda' on non-CUDA hosts)
    pre = DataProcessorPipeline.from_pretrained(
        model_ref,
        config_filename="policy_preprocessor.json",
        overrides={"device_processor": {"device": str(cfg.device)}},
    )
    # Postprocessor typically moves back to CPU; don't override by default
    post = DataProcessorPipeline.from_pretrained(
        model_ref,
        config_filename="policy_postprocessor.json",
    )

    return cfg, policy, pre, post


def prepare_observation(
    frame_bgr: np.ndarray,
    state: np.ndarray,
    cfg,
) -> dict:
    """Prepare observation dict to match policy input features.

    - Resizes frame to the expected resolution if needed
    - Converts to CHW and [0,1] float32
    - Builds observation dict with keys from cfg.input_features
    """
    # Determine expected image shape from config (CHW)
    img_key = None
    for k, ft in cfg.input_features.items():
        if getattr(ft, "type", None).name == "VISUAL":
            img_key = k
            expected_chw = tuple(ft.shape)
            break

    obs = {}

    # Image processing
    if img_key is not None:
        # Convert BGR->RGB if you trained on RGB; config uses ImageNet stats (RGB), so use RGB here
        img = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        # Resize to target (H,W) from expected CHW
        exp_c, exp_h, exp_w = expected_chw
        if (img.shape[0], img.shape[1]) != (exp_h, exp_w):
            img = cv2.resize(img, (exp_w, exp_h), interpolation=cv2.INTER_LINEAR)
        # HWC uint8 -> CHW float32 in [0,1]
        img_chw = np.transpose(img, (2, 0, 1)).astype(np.float32) / 255.0
        # Convert to torch tensor here so DeviceProcessorStep can move it to MPS/CPU
        obs[img_key] = torch.from_numpy(img_chw)

    # State processing (expects shape from config)
    for k, ft in cfg.input_features.items():
        if k == img_key:
            continue
        if getattr(ft, "type", None).name == "STATE":
            exp_shape = tuple(ft.shape)
            # Ensure shape matches (L,) where L==exp_shape[0]
            s = state.astype(np.float32)
            if s.shape != tuple(exp_shape):
                raise ValueError(f"State shape mismatch: got {s.shape}, expected {exp_shape}")
            obs[k] = torch.from_numpy(s)

    return obs


def run_once(policy, preproc, postproc, observation: dict):
    """Run a single inference pass and return the unnormalized action as numpy."""
    # Pre-process observation into model-ready batch dict
    prepped = preproc.process_observation(observation)

    # Model expects dict[str, torch.Tensor]
    # preproc already moved tensors to device and added batch dim
    with torch.no_grad():
        action = policy.select_action(prepped)

    # Post-process back to CPU and unnormalize
    action = postproc.process_action(action)
    # Convert to numpy
    if isinstance(action, torch.Tensor):
        action_np = action.detach().cpu().numpy()
    else:
        action_np = np.asarray(action)
    # Remove batch dim if present
    if action_np.ndim > 1:
        action_np = action_np[0]
    return action_np


def action_vector_to_robot_dict(action_vec: np.ndarray, motor_order: List[str]) -> dict:
    """Map a 1D action vector to a robot action dict using the provided motor order.

    Assumes action vector is absolute target positions for each motor in the same units
    used during training (e.g., degrees if `use_degrees=True`, or normalized ranges otherwise).
    """
    if action_vec.ndim != 1:
        raise ValueError(f"Expected 1D action vector, got shape {action_vec.shape}")
    if len(action_vec) != len(motor_order):
        raise ValueError(f"Action length {len(action_vec)} != motor count {len(motor_order)}")
    return {f"{m}.pos": float(v) for m, v in zip(motor_order, action_vec.tolist())}


def build_robot_observation(obs_robot: dict, cfg) -> dict:
    """Convert raw robot observation to the policy observation dict required by preprocessor.

    - Looks for 'observation.images.*' visual key in cfg and maps from the robot camera frame
    - If 'observation.state' is expected, builds it from individual motor positions in bus order
    """
    obs_policy: dict = {}

    # Visual feature key (e.g., observation.images.front)
    img_key = None
    expected_chw = None
    for k, ft in cfg.input_features.items():
        if getattr(ft, "type", None).name == "VISUAL":
            img_key = k
            expected_chw = tuple(ft.shape)
            break

    if img_key is not None:
        if img_key in obs_robot:
            rgb = obs_robot[img_key]
        else:
            # Prefer a camera named 'front' if present, else pick the first 3-channel image found
            rgb = None
            if 'front' in obs_robot and isinstance(obs_robot['front'], np.ndarray) and obs_robot['front'].ndim == 3:
                rgb = obs_robot['front']
            if rgb is None:
                for cand, val in obs_robot.items():
                    if isinstance(val, np.ndarray) and val.ndim == 3 and val.shape[2] == 3:
                        rgb = val
                        break
            if rgb is None:
                raise KeyError(
                    f"No image found in robot observation for expected policy key '{img_key}'. "
                    f"Available keys: {list(obs_robot.keys())}"
                )

        # Ensure RGB and correct size
        if rgb.dtype != np.uint8:
            rgb = np.clip(rgb, 0, 255).astype(np.uint8)
        exp_c, exp_h, exp_w = expected_chw  # type: ignore[misc]
        if (rgb.shape[0], rgb.shape[1]) != (exp_h, exp_w):
            rgb = cv2.resize(rgb, (exp_w, exp_h), interpolation=cv2.INTER_LINEAR)
        # HWC -> CHW float32 [0,1]
        img_chw = np.transpose(rgb, (2, 0, 1)).astype(np.float32) / 255.0
        obs_policy[img_key] = torch.from_numpy(img_chw)

    # State vector feature
    for k, ft in cfg.input_features.items():
        if getattr(ft, "type", None).name == "STATE":
            # Build from robot joint positions in standard order
            # We'll import robot class lazily to get motor order if available in obs
            motor_vals = []
            # Try typical SO101 motor order
            default_motor_order = [
                "shoulder_pan",
                "shoulder_lift",
                "elbow_flex",
                "wrist_flex",
                "wrist_roll",
                "gripper",
            ]
            for m in default_motor_order:
                key = f"{m}.pos"
                if key not in obs_robot:
                    raise KeyError(f"Expected '{key}' in robot observation, available: {list(obs_robot.keys())}")
                motor_vals.append(float(obs_robot[key]))
            state_np = np.array(motor_vals, dtype=np.float32)
            exp_shape = tuple(ft.shape)
            if state_np.shape != exp_shape:
                raise ValueError(f"State shape mismatch from robot: got {state_np.shape}, expected {exp_shape}")
            obs_policy[k] = torch.from_numpy(state_np)

    return obs_policy


def main():
    parser = argparse.ArgumentParser()
    # Default relative to this file's directory (the repo root)
    parser.add_argument(
        "--model-dir",
        type=str,
        default="last/pretrained_model",
        help="Model path (local dir) or Hub repo id (e.g., Shrek0/my_vla_policy)",
    )
    parser.add_argument("--camera", type=int, default=0, help="Webcam index (default: 0)")
    parser.add_argument("--image", type=str, default=None, help="Optional path to a single image to run once")
    parser.add_argument(
        "--state",
        type=float,
        nargs="*",
        default=None,
        help="Optional robot state vector values (e.g., 6 floats). Defaults to zeros if omitted.",
    )
    # Robot mode flags
    parser.add_argument("--robot", action="store_true", help="Enable SO-101 follower robot mode")
    parser.add_argument("--robot-port", type=str, default=None, help="Serial port for SO-101 (e.g., /dev/tty.usbmodemXXXXX)")
    parser.add_argument("--robot-camera-index", type=int, default=None, help="OpenCV camera index for robot camera")
    parser.add_argument("--robot-camera-fps", type=int, default=30, help="FPS for robot camera (required by robot config)")
    parser.add_argument("--robot-id", type=str, default=None, help="Optional robot ID used for calibration file association")
    parser.add_argument("--use-degrees", action="store_true", help="Interpret actions/state in degrees (matches some datasets)")
    parser.add_argument("--max-relative-target", type=float, default=None, help="Safety cap on per-step target delta (units match use-degrees)")
    parser.add_argument("--no-calibrate", action="store_true", help="Skip calibration on connect if motors are already calibrated")
    args = parser.parse_args()

    # This file sits at the repo root `.../lerobot/`
    repo_root = Path(__file__).resolve().parent
    # Ensure we can import lerobot from the local repo
    _ensure_repo_on_path(repo_root)

    # Resolve model dir relative to this file if not absolute
    # Accept either a local directory (absolute or relative to repo root) or a Hugging Face repo id
    raw_ref = args.model_dir
    local_candidate = (repo_root / raw_ref).resolve()
    if Path(raw_ref).is_absolute() and Path(raw_ref).exists():
        model_ref: str | Path = Path(raw_ref)
    elif local_candidate.exists():
        model_ref = local_candidate
    else:
        # treat as Hub repo id (e.g., "Shrek0/my_vla_policy")
        model_ref = raw_ref

    cfg, policy, preproc, postproc = load_policy_and_processors(model_ref)

    # If robot mode: connect and run policy loop on the real arm
    if args.robot:
        # Lazy import robot and camera configs now that sys.path is set
        from lerobot.cameras.opencv.configuration_opencv import OpenCVCameraConfig as CvCamCfg
        from lerobot.cameras.configs import ColorMode
        from lerobot.robots.so101_follower.config_so101_follower import SO101FollowerConfig
        from lerobot.robots.so101_follower.so101_follower import SO101Follower

        if args.robot_port is None:
            raise ValueError("--robot-port is required in --robot mode. See 'lerobot/port' for examples.")

        # Determine the expected image key and shape
        img_key = None
        exp_h = exp_w = None
        for k, ft in cfg.input_features.items():
            if getattr(ft, "type", None).name == "VISUAL":
                img_key = k
                _, exp_h, exp_w = ft.shape
                break
        if img_key is None:
            raise ValueError("This policy has no VISUAL input; robot mode requires a camera input.")

        cam_index = args.robot_camera_index if args.robot_camera_index is not None else args.camera
        cam_cfg = CvCamCfg(
            index_or_path=int(cam_index),
            width=int(exp_w),
            height=int(exp_h),
            fps=int(args.robot_camera_fps),
            color_mode=ColorMode.RGB,
        )

        # Use a simple camera key like 'front' (policy mapper will pull it and map to the expected key)
        robot_cfg = SO101FollowerConfig(
            port=args.robot_port,
            cameras={"front": cam_cfg},
            max_relative_target=args.max_relative_target,
            use_degrees=bool(args.use_degrees),
            id=args.robot_id,
        )

        robot = SO101Follower(robot_cfg)
        robot.connect(calibrate=not args.no_calibrate)

        motor_order = ["shoulder_pan", "shoulder_lift", "elbow_flex", "wrist_flex", "wrist_roll", "gripper"]
        print("Robot mode started. Ctrl+C to stop.")
        try:
            while True:
                obs_robot = robot.get_observation()
                obs_policy = build_robot_observation(obs_robot, cfg)
                action_vec = run_once(policy, preproc, postproc, obs_policy)
                action_dict = action_vector_to_robot_dict(action_vec, motor_order)
                sent = robot.send_action(action_dict)
                # Print a compact action preview
                txt = ", ".join([f"{k}:{v:.2f}" for k, v in sent.items()])
                print(f"sent: {txt}")
        except KeyboardInterrupt:
            print("\nStopping robot loop...")
        finally:
            try:
                robot.disconnect()
            except Exception:
                pass
        return

    # Prepare state vector
    # Infer required length from cfg.output_features or cfg.input_features
    state_len = None
    for k, ft in cfg.input_features.items():
        if getattr(ft, "type", None).name == "STATE":
            state_len = int(ft.shape[0])
            break
    if state_len is None:
        state_len = 0

    if args.state is not None and len(args.state) > 0:
        state_vec = np.array(args.state, dtype=np.float32)
    else:
        state_vec = np.zeros((state_len,), dtype=np.float32)

    if args.image:
        frame_bgr = cv2.imread(args.image, cv2.IMREAD_COLOR)
        if frame_bgr is None:
            raise FileNotFoundError(f"Failed to load image: {args.image}")
        observation = prepare_observation(frame_bgr, state_vec, cfg)
        action = run_once(policy, preproc, postproc, observation)
        print("Predicted action:", action)
        return

    # Live webcam mode (default when not in --robot and no --image)
    cap = cv2.VideoCapture(args.camera)
    if not cap.isOpened():
        raise RuntimeError(f"Unable to open camera index {args.camera}")

    print("Live mode started. Press 'q' to quit.")
    try:
        while True:
            ok, frame_bgr = cap.read()
            if not ok:
                print("Failed to read frame")
                break

            observation = prepare_observation(frame_bgr, state_vec, cfg)
            action = run_once(policy, preproc, postproc, observation)

            # Display frame and action values
            disp = frame_bgr.copy()
            h = 20
            txt = ", ".join([f"{v:.3f}" for v in action.tolist()])
            cv2.rectangle(disp, (0, 0), (disp.shape[1], h + 10), (0, 0, 0), -1)
            cv2.putText(disp, f"action: [{txt}]", (10, h), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            cv2.imshow("policy_inference", disp)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
