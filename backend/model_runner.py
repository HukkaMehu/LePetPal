import time
import os
from typing import Dict, Iterable, List, Optional
import numpy as np
import torch
import cv2


class ModelRunner:
    def __init__(self, model_path: str, rate_hz: int = 15, mode: str = "scripted", camera=None, device: str = "cpu"):
        self.model_path = model_path
        self.rate_hz = rate_hz
        self.mode = mode
        self.camera = camera
        self.device = device
        self.loaded = False
        self.policy = None
        self.preproc = None
        self.postproc = None
        self.cfg = None
        self._load()

    def _load(self):
        if self.mode == "smolvla":
            if not self.model_path:
                print("WARNING: MODEL_PATH not set for smolvla mode. Falling back to scripted.")
                self.mode = "scripted"
                self.loaded = True
                return
            try:
                print(f"INFO: Loading smolvla policy from {self.model_path} on device={self.device}...")
                from lerobot.configs.policies import PreTrainedConfig
                from lerobot.policies.factory import get_policy_class
                from lerobot.processor.pipeline import DataProcessorPipeline

                # Load config (auto-adapts device if original device not available)
                self.cfg = PreTrainedConfig.from_pretrained(self.model_path)
                # Override device if specified
                if self.device:
                    self.cfg.device = self.device

                # Load policy class and weights
                policy_cls = get_policy_class(self.cfg.type)
                self.policy = policy_cls.from_pretrained(self.model_path, config=self.cfg)
                self.policy.eval()

                # Load pre/post pipelines
                self.preproc = DataProcessorPipeline.from_pretrained(
                    self.model_path,
                    config_filename="policy_preprocessor.json",
                    overrides={"device_processor": {"device": str(self.cfg.device)}},
                )
                self.postproc = DataProcessorPipeline.from_pretrained(
                    self.model_path,
                    config_filename="policy_postprocessor.json",
                )
                self.loaded = True
                print(f"INFO: smolvla policy loaded successfully.")
                print(f"DEBUG: Policy input features: {list(self.cfg.input_features.keys())}")
            except Exception as e:
                print(f"ERROR: Failed to load smolvla policy: {e}")
                print("INFO: Falling back to scripted mode.")
                self.mode = "scripted"
                self.loaded = True
        else:
            # scripted mode
            self.loaded = True

    def infer(self, instruction: str) -> Iterable[Dict]:
        """Yield control chunks.
        - scripted: deterministic phases for demo flow.
        - smolvla: real-time policy inference from camera frames.
        """
        if self.mode == "smolvla":
            yield from self._infer_smolvla(instruction)
        else:
            yield from self._infer_scripted(instruction)

    def _infer_scripted(self, instruction: str) -> Iterable[Dict]:
        """Scripted demo mode."""
        if instruction == "get the treat":
            phases = [
                ("detect", [0.1, 0.1, 0.0, 0.0, 0.0, 0.0], 0.7),
                ("approach", [0.2, 0.1, 0.0, 0.1, 0.0, 0.0], 0.75),
                ("grasp", [0.3, 0.1, 0.0, 0.1, 0.0, 0.0], 0.8),
                ("lift", [0.2, 0.2, 0.0, 0.1, 0.0, 0.0], 0.82),
                ("drop", [0.1, 0.2, 0.0, 0.1, 0.0, 0.0], 0.84),
            ]
        else:
            phases = [
                ("detect", [0.0, 0.1, 0.0, 0.0, 0.0, 0.0], 0.7),
                ("approach", [0.1, 0.2, 0.0, 0.0, 0.0, 0.0], 0.75),
                ("grasp", [0.2, 0.3, 0.0, 0.1, 0.0, 0.0], 0.8),
                ("lift", [0.2, 0.2, 0.1, 0.1, 0.0, 0.0], 0.82),
                ("ready_to_throw", [0.2, 0.2, 0.2, 0.1, 0.0, 0.0], 0.85),
            ]
        for phase, targets, conf in phases:
            yield {"phase": phase, "targets": targets, "confidence": conf}
            time.sleep(1.0 / max(1, self.rate_hz))

    def _infer_smolvla(self, instruction: str) -> Iterable[Dict]:
        """Real-time VLA policy inference from camera frames."""
        if not self.loaded or self.policy is None:
            print("ERROR: smolvla policy not loaded. Yielding no actions.")
            return

        if self.camera is None:
            print("ERROR: No camera provided to ModelRunner for smolvla mode.")
            return

        # Determine expected image shape from config (preprocessor expects 256x256 based on config)
        exp_h = exp_w = 256
        
        # Check if policy has visual and state features
        has_visual = any(getattr(ft, "type", None).name == "VISUAL" for ft in self.cfg.input_features.values())
        has_state = any(getattr(ft, "type", None).name == "STATE" for ft in self.cfg.input_features.values())
        
        if not has_visual:
            print("ERROR: Policy has no VISUAL input feature.")
            return

        print(f"INFO: Running smolvla inference loop at {self.rate_hz} Hz. Instruction: '{instruction}'")
        step_count = 0
        while True:
            t0 = time.time()

            # Capture frame from camera
            ok, frame_bgr = self.camera.read()
            if not ok or frame_bgr is None:
                print("WARNING: Failed to read camera frame. Skipping step.")
                time.sleep(1.0 / max(1, self.rate_hz))
                continue

            # Prepare observation dict with correct structure
            # Preprocessor expects: observation.images.camera1, observation.images.camera2, observation.images.camera3, observation.state
            obs = {}

            # Image: BGR->RGB, resize to 256x256, HWC->CHW, [0,1] float32
            img_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
            if (img_rgb.shape[0], img_rgb.shape[1]) != (exp_h, exp_w):
                img_rgb = cv2.resize(img_rgb, (exp_w, exp_h), interpolation=cv2.INTER_LINEAR)
            img_chw = np.transpose(img_rgb, (2, 0, 1)).astype(np.float32) / 255.0
            img_tensor = torch.from_numpy(img_chw)
            
            # Use same image for all 3 camera views (we only have 1 camera)
            obs["observation.images.camera1"] = img_tensor
            obs["observation.images.camera2"] = img_tensor
            obs["observation.images.camera3"] = img_tensor

            # State: use zeros for now (6D state expected)
            if has_state:
                state_vec = np.zeros((6,), dtype=np.float32)
                obs["observation.state"] = torch.from_numpy(state_vec)

            # Create full transition with complementary_data for task instruction
            # The tokenizer processor needs this structure
            from lerobot.processor.converters import create_transition
            from lerobot.processor.core import TransitionKey
            
            transition = create_transition(
                observation=obs,
                complementary_data={'task': instruction}
            )

            # Process the full transition, then extract observation
            prepped_transition = self.preproc._forward(transition)
            prepped = prepped_transition[TransitionKey.OBSERVATION]

            # Inference
            with torch.no_grad():
                action = self.policy.select_action(prepped)

            # Postprocess
            action = self.postproc.process_action(action)
            if isinstance(action, torch.Tensor):
                action_np = action.detach().cpu().numpy()
            else:
                action_np = np.asarray(action)
            # Remove batch dim if present
            if action_np.ndim > 1:
                action_np = action_np[0]

            # Map to 6D targets (assumes action_np is [shoulder_pan, shoulder_lift, elbow_flex, wrist_flex, wrist_roll, gripper])
            if action_np.shape[0] != 6:
                print(f"WARNING: Expected 6D action, got shape {action_np.shape}. Padding/truncating.")
                if action_np.shape[0] < 6:
                    action_np = np.pad(action_np, (0, 6 - action_np.shape[0]), constant_values=0.0)
                else:
                    action_np = action_np[:6]

            targets = action_np.tolist()
            step_count += 1
            phase = f"step_{step_count}"
            confidence = 0.9  # placeholder

            yield {"phase": phase, "targets": targets, "confidence": confidence}

            # Rate limiting
            elapsed = time.time() - t0
            sleep_time = max(0, (1.0 / self.rate_hz) - elapsed)
            if sleep_time > 0:
                time.sleep(sleep_time)
