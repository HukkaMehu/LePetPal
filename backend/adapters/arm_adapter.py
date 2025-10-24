import time
from typing import Iterable, List, Dict, Optional


class ArmAdapter:
    """Adapter for LeRobot SO-101 follower arm.
    When use_hardware=False, operates in mock mode.
    """
    def __init__(self, use_hardware: bool = False):
        self._joints: List[float] = [0.0] * 6
        self._connected = False
        self._use_hardware = use_hardware
        self._driver = None  # placeholder for real lerobot driver instance

    def connect(self) -> bool:
        if not self._use_hardware:
            self._connected = True
            return True
        # TODO: integrate lerobot SO-101 connect and assign self._driver
        # Example:
        # from lerobot.so101 import SO101
        # self._driver = SO101(port=...)
        # self._driver.connect()
        # self._connected = True
        self._connected = True
        return True

    def get_joint_angles(self) -> List[float]:
        if self._use_hardware and self._driver is not None:
            # TODO: read from hardware driver
            pass
        return list(self._joints)

    def send_joint_targets(self, chunk: Dict) -> None:
        """Accepts a chunk with optional 'targets' list[6].
        In real impl, stream targets at fixed rate.
        """
        targets = chunk.get("targets")
        if targets and len(targets) == 6:
            self._joints = list(targets)
            if self._use_hardware and self._driver is not None:
                # TODO: send to hardware at fixed rate
                pass
        time.sleep(0.005)

    def home(self) -> None:
        # Move to neutral pose (stub)
        self._joints = [0.0] * 6
        if self._use_hardware and self._driver is not None:
            # TODO: send home to hardware
            pass
        time.sleep(0.3)

    def stop(self) -> None:
        # Emergency stop (stub)
        if self._use_hardware and self._driver is not None:
            # TODO: e-stop hardware
            pass

    def throw_macro(self) -> None:
        # Hard-coded quick motion (stub)
        if self._use_hardware and self._driver is not None:
            # TODO: execute throw macro via waypoints
            pass
        time.sleep(0.5)
