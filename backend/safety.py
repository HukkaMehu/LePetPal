from typing import Dict, List


class SafetyManager:
    def __init__(self):
        # Default joint limits (radians) – placeholder conservative bounds
        self.joint_min: List[float] = [-2.5, -2.5, -2.5, -2.5, -2.5, -2.5]
        self.joint_max: List[float] = [ 2.5,  2.5,  2.5,  2.5,  2.5,  2.5]

    def validate_targets(self, chunk: Dict) -> bool:
        targets = chunk.get("targets")
        if not targets or len(targets) != 6:
            return False
        for i, v in enumerate(targets):
            if v < self.joint_min[i] or v > self.joint_max[i]:
                return False
        return True

    def ready_to_throw(self, joints: List[float]) -> bool:
        # Placeholder: check joints roughly near a pose
        return len(joints) == 6 and abs(joints[2]) < 0.25

    def workspace_clear(self) -> bool:
        # Placeholder: assume clear; in real impl consult ROI mask or detection
        return True
