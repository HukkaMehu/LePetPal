
import os
import time
from typing import List, Dict
import numpy as np

try:
    from lerobot.robots.so101_follower.so101_follower import SO101Follower, SO101FollowerConfig
except ImportError:
    SO101Follower = None
    SO101FollowerConfig = None

class ArmAdapter:
    """Adapter for LeRobot SO-101 follower arm."""
    def __init__(self, use_hardware: bool = False):
        self._joints: List[float] = [0.0] * 6
        self._connected = False
        self._use_hardware = use_hardware
        self._driver: SO101Follower | None = None

    @property
    def is_connected(self) -> bool:
        """Check if the robot is currently connected."""
        if not self._use_hardware:
            return self._connected
        if self._driver is None:
            return False
        return self._driver.is_connected

    def connect(self) -> bool:
        if not self._use_hardware or SO101Follower is None:
            print("INFO: ArmAdapter running in MOCK mode.")
            self._connected = True
            return True

        try:
            port = os.getenv("ARM_PORT", "COM7")
            print(f"INFO: ArmAdapter connecting to hardware on {port}...")
            robot_config = SO101FollowerConfig(port=port)
            self._driver = SO101Follower(robot_config)
            self._driver.connect()
            self._connected = True
            print(f"INFO: ArmAdapter successfully connected to hardware. is_connected={self.is_connected}")
            self.home()
            print(f"INFO: ArmAdapter homed. is_connected={self.is_connected}")
            return True
        except Exception as e:
            print(f"ERROR: Failed to connect to arm hardware: {e}")
            self._connected = False
            return False

    def get_joint_angles(self) -> List[float]:
        # Return the last commanded joints. For now, we don't query hardware feedback.
        # These values are updated by send_joint_targets() and home().
        return list(self._joints)

    def send_joint_targets(self, chunk: Dict) -> None:
        """Accepts a chunk with 'targets' and streams them to the arm."""
        targets = chunk.get("targets")
        if targets and len(targets) == 6:
            self._joints = list(targets)
            if self._use_hardware and self._driver is not None:
                if not self._driver.is_connected:
                    print(f"WARNING: Robot not connected (is_connected={self.is_connected}), skipping action send")
                    return
                print(f"DEBUG: Sending action to robot (is_connected={self.is_connected})")
                action = {
                    "shoulder_pan.pos": float(targets[0]),
                    "shoulder_lift.pos": float(targets[1]),
                    "elbow_flex.pos": float(targets[2]),
                    "wrist_flex.pos": float(targets[3]),
                    "wrist_roll.pos": float(targets[4]),
                    "gripper.pos": float(targets[5]),
                }
                try:
                    self._driver.send_action(action)
                except Exception as e:
                    print(f"ERROR: Failed to send action: {e}")
                    raise

    def home(self) -> None:
        """Move to a neutral, safe home pose."""
        home_pose = [0.0] * 6
        if self._use_hardware and self._driver is not None:
            action = {
                "shoulder_pan.pos": 0.0,
                "shoulder_lift.pos": 0.0,
                "elbow_flex.pos": 0.0,
                "wrist_flex.pos": 0.0,
                "wrist_roll.pos": 0.0,
                "gripper.pos": 20.0,
            }
            self._driver.send_action(action)
            time.sleep(1.5)
        self._joints = home_pose

    def stop(self) -> None:
        if self._use_hardware and self._driver is not None:
            self._driver.disconnect()

    def throw_macro(self) -> None:
        if self._use_hardware and self._driver is not None:
            ready_pose = self.get_joint_angles()
            throw_pose_1 = np.array(ready_pose.copy())
            throw_pose_1[1] -= 0.5
            throw_pose_2 = throw_pose_1.copy()
            throw_pose_2[2] += 1.0

            action1 = {
                "shoulder_pan.pos": float(throw_pose_1[0]),
                "shoulder_lift.pos": float(throw_pose_1[1]),
                "elbow_flex.pos": float(throw_pose_1[2]),
                "wrist_flex.pos": float(throw_pose_1[3]),
                "wrist_roll.pos": float(throw_pose_1[4]),
                "gripper.pos": float(throw_pose_1[5]),
            }
            action2 = {
                "shoulder_pan.pos": float(throw_pose_2[0]),
                "shoulder_lift.pos": float(throw_pose_2[1]),
                "elbow_flex.pos": float(throw_pose_2[2]),
                "wrist_flex.pos": float(throw_pose_2[3]),
                "wrist_roll.pos": float(throw_pose_2[4]),
                "gripper.pos": float(throw_pose_2[5]),
            }
            self._driver.send_action(action1)
            time.sleep(0.2)
            self._driver.send_action(action2)
            time.sleep(0.1)
        time.sleep(0.5)
