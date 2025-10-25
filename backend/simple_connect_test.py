
import os
import sys
import time
from lerobot.robots.so101_follower.so101_follower import SO101Follower, SO101FollowerConfig

print("--- LeRobot Simple Connection Test ---")
robot = None
try:
    # 1. Configure the robot (follower arm)
    port = sys.argv[1] if len(sys.argv) > 1 else os.getenv("ARM_PORT", "COM8")
    print(f"1. Configuring robot for {port}...")
    robot_config = SO101FollowerConfig(port=port)

    # 2. Instantiate the robot object
    robot = SO101Follower(robot_config)

    # 3. Connect to the robot
    print("2. Connecting to robot...")
    robot.connect()
    print("   SUCCESS: Connected to robot.")

    # 4. Command the robot to a neutral pose via send_action
    print("3. Moving robot to neutral pose (0s)...")
    action = {
        "shoulder_pan.pos": 0.0,
        "shoulder_lift.pos": 0.0,
        "elbow_flex.pos": 0.0,
        "wrist_flex.pos": 0.0,
        "wrist_roll.pos": 0.0,
        # Use a gentle open position for gripper in [0,100] range
        "gripper.pos": 20.0,
    }
    sent = robot.send_action(action)
    print("   Action sent:", sent)
    time.sleep(2)
    print("   Neutral command done.")

    print("4. Test complete.")

except Exception as e:
    print(f"   ERROR: An error occurred: {e}")

finally:
    if robot is not None and robot.is_connected:
        print("5. Disconnecting robot...")
        robot.disconnect()
        print("   Disconnected.")
