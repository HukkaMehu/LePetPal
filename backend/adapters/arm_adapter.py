import time
from typing import Iterable, List, Dict


class ArmAdapter:
    """Stub adapter for LeRobot SO-101 follower arm.
    Replace internals with real lerobot driver calls when hardware is present.
    """
    def __init__(self):
        self._joints: List[float] = [0.0] * 6
        self._connected = False

    def connect(self) -> bool:
        # TODO: integrate lerobot SO-101 connect
        self._connected = True
        return True

    def get_joint_angles(self) -> List[float]:
        # TODO: read from hardware
        return list(self._joints)

    def send_joint_targets(self, chunk: Dict) -> None:
        """Accepts a chunk with optional 'targets' list[6].
        In real impl, stream targets at fixed rate.
        """
        targets = chunk.get("targets")
        if targets and len(targets) == 6:
            self._joints = list(targets)
        time.sleep(0.005)

    def home(self) -> None:
        # Move to neutral pose (stub)
        self._joints = [0.0] * 6
        time.sleep(0.3)

    def stop(self) -> None:
        # Emergency stop (stub)
        pass

    def throw_macro(self) -> None:
        # Hard-coded quick motion (stub)
        time.sleep(0.5)
