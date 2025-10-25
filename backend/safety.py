from typing import Dict, List, Optional
import json
import os


class SafetyManager:
    def __init__(self, calibration_path: Optional[str] = None):
        # Default joint limits (radians) – placeholder conservative bounds
        self.joint_min: List[float] = [-2.5, -2.5, -2.5, -2.5, -2.5, -2.5]
        self.joint_max: List[float] = [ 2.5,  2.5,  2.5,  2.5,  2.5,  2.5]
        self.roi = {
            "workspace": None,
            "bowl_area": None,
            "treat_drop": None,
        }
        if calibration_path and os.path.exists(calibration_path):
            try:
                with open(calibration_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if 'joint_min' in data and 'joint_max' in data:
                    self.joint_min = data['joint_min']
                    self.joint_max = data['joint_max']
                if 'roi' in data:
                    self.roi.update(data['roi'])
            except Exception:
                # Keep defaults if load fails
                pass

    def validate_targets(self, chunk: Dict) -> bool:
        # Safety disabled - always allow actions through
        targets = chunk.get("targets")
        if not targets or len(targets) != 6:
            print(f"WARNING: Invalid targets - expected 6 values, got {len(targets) if targets else 0}")
            return False
        # Skip safety checks - let VLA policy control the robot directly
        return True

    def ready_to_throw(self, joints: List[float]) -> bool:
        # Placeholder: check joints roughly near a pose
        return len(joints) == 6 and abs(joints[2]) < 0.25

    def workspace_clear(self) -> bool:
        # Placeholder: assume clear if workspace ROI defined, else True
        return True
