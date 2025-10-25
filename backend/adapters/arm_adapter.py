
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
            print("INFO: ArmAdapter successfully connected to hardware.")
            self.home()
            return True
        except Exception as e:
            print(f"ERROR: Failed to connect to arm hardware: {e}")
            self._connected = False
            return False

    def get_joint_angles(self) -> List[float]:
        if self._use_hardware and self._driver is not None:
            joint_positions, _ = self._driver.get_joint_states()
            self._joints = joint_positions.tolist()
        return list(self._joints)

    def send_joint_targets(self, chunk: Dict) -> None:
        """Accepts a chunk with 'targets' and streams them to the arm."""
        targets = chunk.get("targets")
        if targets and len(targets) == 6:
            self._joints = list(targets)
            if self._use_hardware and self._driver is not None:
                action = {
                    "shoulder_pan.pos": float(targets[0]),
                    "shoulder_lift.pos": float(targets[1]),
                    "elbow_flex.pos": float(targets[2]),
                    "wrist_flex.pos": float(targets[3]),
                    "wrist_roll.pos": float(targets[4]),
                    "gripper.pos": float(targets[5]),
                }
                self._driver.send_action(action)

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
