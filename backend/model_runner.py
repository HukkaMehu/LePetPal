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
                # Handle DirectML device for Snapdragon GPU
                use_directml = self.device and self.device.startswith('privateuseone')
                dml_device = None
                if use_directml:
                    import torch_directml
                    dml_device = torch_directml.device()
                    print(f"INFO: DirectML device available: {dml_device}")
                
                # Load model on CPU first to avoid CUDA check, then move to DirectML
                print(f"INFO: Loading smolvla policy from {self.model_path} on cpu (will move to DirectML after)...")
                from lerobot.configs.policies import PreTrainedConfig
                from lerobot.policies.factory import get_policy_class
                from lerobot.processor.pipeline import DataProcessorPipeline

                # Load config with CPU device
                self.cfg = PreTrainedConfig.from_pretrained(self.model_path)
                self.cfg.device = "cpu"

                # Load policy class and weights on CPU
                policy_cls = get_policy_class(self.cfg.type)
                self.policy = policy_cls.from_pretrained(self.model_path, config=self.cfg)
                
                # Move to DirectML if available
                if use_directml and dml_device:
                    print(f"INFO: Converting model to float32 (DirectML doesn't support bfloat16)...")
                    import torch
                    self.policy = self.policy.to(torch.float32)
                    print(f"INFO: Moving policy to DirectML device: {dml_device}")
                    self.policy = self.policy.to(dml_device)
                    self.cfg.device = dml_device
                
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
        """Scripted demo mode with visible movements (values in degrees)."""
        if instruction == "get the treat":
            phases = [
                ("detect_1", [0.0, 5.0, 0.0, 0.0, 0.0, 20.0], 0.7),
                ("detect_2", [0.0, 10.0, 5.0, 0.0, 0.0, 20.0], 0.72),
                ("approach_1", [10.0, 15.0, 8.0, -5.0, 0.0, 20.0], 0.75),
                ("approach_2", [15.0, 20.0, 10.0, -10.0, 0.0, 20.0], 0.77),
                ("grasp_1", [15.0, 22.0, 12.0, -12.0, 0.0, 35.0], 0.78),
                ("grasp_2", [15.0, 25.0, 15.0, -15.0, 0.0, 50.0], 0.8),
                ("lift_1", [12.0, 20.0, 17.0, -12.0, 0.0, 50.0], 0.81),
                ("lift_2", [10.0, 15.0, 20.0, -10.0, 0.0, 50.0], 0.82),
                ("drop_1", [7.0, 12.0, 15.0, -5.0, 0.0, 35.0], 0.83),
                ("drop_2", [5.0, 10.0, 10.0, 0.0, 0.0, 20.0], 0.84),
            ]
        else:  # "pick up the ball" or default
            phases = [
                ("detect_1", [0.0, 5.0, 0.0, 0.0, 0.0, 20.0], 0.7),
                ("detect_2", [0.0, 10.0, 5.0, 0.0, 0.0, 20.0], 0.72),
                ("approach_1", [10.0, 15.0, 10.0, -5.0, 2.0, 20.0], 0.74),
                ("approach_2", [15.0, 20.0, 12.0, -8.0, 4.0, 20.0], 0.76),
                ("approach_3", [20.0, 25.0, 15.0, -10.0, 5.0, 20.0], 0.78),
                ("grasp_1", [20.0, 27.0, 17.0, -12.0, 5.0, 35.0], 0.79),
                ("grasp_2", [20.0, 30.0, 20.0, -15.0, 5.0, 50.0], 0.8),
                ("lift_1", [17.0, 25.0, 22.0, -12.0, 2.0, 50.0], 0.81),
                ("lift_2", [15.0, 20.0, 25.0, -10.0, 0.0, 50.0], 0.82),
                ("ready_1", [12.0, 17.0, 27.0, -7.0, 0.0, 50.0], 0.84),
                ("ready_2", [10.0, 15.0, 30.0, -5.0, 0.0, 50.0], 0.85),
            ]
        for phase, targets, conf in phases:
            yield {"phase": phase, "targets": targets, "confidence": conf}
            time.sleep(0.5)  # 0.5 second per step for smoother, slower motion

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
            try:
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
                
                t_trans = time.time()
                transition = create_transition(
                    observation=obs,
                    complementary_data={'task': instruction}
                )
                print(f"DEBUG: create_transition took {(time.time()-t_trans)*1000:.1f}ms")

                # Process the full transition, then extract observation
                t_prep = time.time()
                prepped_transition = self.preproc._forward(transition)
                prepped = prepped_transition[TransitionKey.OBSERVATION]
                print(f"DEBUG: preproc._forward took {(time.time()-t_prep)*1000:.1f}ms")

                # Inference
                t_inf = time.time()
                with torch.no_grad():
                    action = self.policy.select_action(prepped)
                print(f"DEBUG: policy.select_action took {(time.time()-t_inf)*1000:.1f}ms")

                # Postprocess
                t_post = time.time()
                action = self.postproc.process_action(action)
                print(f"DEBUG: postproc took {(time.time()-t_post)*1000:.1f}ms")
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
            except Exception as e:
                print(f"ERROR: Exception in VLA inference loop: {e}")
                import traceback
                traceback.print_exc()
                raise
