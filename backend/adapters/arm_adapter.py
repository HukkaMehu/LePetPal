import time
import os
import importlib
from typing import Iterable, List, Dict, Optional
import numpy as np

# Attempt to import the real hardware driver
try:
    from lerobot.real_world.interbotix_sdk_driver import InterbotixSDKDriver
except ImportError:
    InterbotixSDKDriver = None

class ArmAdapter:
    """Adapter for LeRobot SO-101 follower arm."""
    def __init__(self, use_hardware: bool = False):
        self._joints: List[float] = [0.0] * 6
        self._connected = False
        self._use_hardware = use_hardware
        self._driver = None  # real driver instance when available
        # Dynamic driver config via env
        self._drv_module = os.getenv("ARM_DRIVER_MODULE", "")
        self._drv_class = os.getenv("ARM_DRIVER_CLASS", "")
        self._drv_port = os.getenv("ARM_PORT", "")
        self._drv_baud = int(os.getenv("ARM_BAUD", "0") or 0)
        self._joint_units = os.getenv("JOINT_UNITS", "rad")  # 'rad' or 'deg'

    def connect(self) -> bool:
        if not self._use_hardware:
            self._connected = True
            return True
        # Dynamic import based on env configuration
        try:
            if self._drv_module and self._drv_class:
                mod = importlib.import_module(self._drv_module)
                cls = getattr(mod, self._drv_class)
                kwargs = {}
                if self._drv_port:
                    kwargs["port"] = self._drv_port
                if self._drv_baud:
                    kwargs["baud"] = self._drv_baud
                self._driver = cls(**kwargs)
                # optional explicit connect()
                if hasattr(self._driver, "connect"):
                    self._driver.connect()
                self._connected = True
                return True
        except Exception:
            # Fall back to mock if any failure
            self._driver = None
            self._connected = False
            return False
        # If no driver info provided, remain disconnected in hardware mode
        self._connected = False
        return False

    def get_joint_angles(self) -> List[float]:
        if self._use_hardware and self._driver is not None:
            try:
                for name in ("get_joint_angles", "read_joints", "get_joints", "get_positions"):
                    if hasattr(self._driver, name):
                        vals = getattr(self._driver, name)()
                        arr = list(vals)
                        if self._joint_units == "deg":
                            # convert degrees to radians conservatively
                            arr = [v * 3.141592653589793 / 180.0 for v in arr]
                        self._joints = arr
                        return list(self._joints)
            except Exception:
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
                try:
                    out = list(targets)
                    if self._joint_units == "deg":
                        out = [v * 180.0 / 3.141592653589793 for v in out]
                    for name in ("send_joint_targets", "send_joints", "set_positions", "command_joints"):
                        if hasattr(self._driver, name):
                            getattr(self._driver, name)(out)
                            break
                except Exception:
                    pass
        time.sleep(0.005)

    def home(self) -> None:
        # Move to neutral pose (stub)
        self._joints = [0.0] * 6
        if self._use_hardware and self._driver is not None:
            try:
                for name in ("home", "go_home", "move_home"):
                    if hasattr(self._driver, name):
                        getattr(self._driver, name)()
                        break
            except Exception:
                pass
        time.sleep(0.3)

    def stop(self) -> None:
        # Emergency stop (stub)
        if self._use_hardware and self._driver is not None:
            try:
                for name in ("stop", "estop", "halt"):
                    if hasattr(self._driver, name):
                        getattr(self._driver, name)()
                        break
            except Exception:
                pass

    def throw_macro(self) -> None:
        # This should be a carefully tuned sequence of joint angles
        if self._use_hardware and self._driver is not None:
            # Example: A quick, hard-coded throw motion
            ready_pose = self.get_joint_angles()
            throw_pose_1 = ready_pose.copy()
            throw_pose_1[1] -= 0.5 # Example adjustment
            throw_pose_2 = throw_pose_1.copy()
            throw_pose_2[2] += 1.0 # Example adjustment

            self._driver.set_joint_positions(np.array(throw_pose_1), blocking=True, moving_time=0.2)
            self._driver.set_joint_positions(np.array(throw_pose_2), blocking=True, moving_time=0.1)
        time.sleep(0.5)