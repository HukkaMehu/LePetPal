
import time
from lerobot.robots import SO101Follower, SO101FollowerConfig

print("--- LeRobot Simple Connection Test ---")
robot = None
try:
    # 1. Configure the robot (follower arm)
    print("1. Configuring robot for COM7...")
    robot_config = SO101FollowerConfig(port="COM7")

    # 2. Instantiate the robot object
    robot = SO101Follower(robot_config)

    # 3. Connect to the robot
    print("2. Connecting to robot...")
    robot.connect()
    print("   SUCCESS: Connected to robot.")

    # 4. Command the robot to its home position
    print("3. Commanding robot to home position...")
    robot.home()
    time.sleep(2) # Give it time to move
    print("   Home command sent.")

    print("4. Test complete.")

except Exception as e:
    print(f"   ERROR: An error occurred: {e}")

finally:
    if robot is not None and robot.is_connected:
        print("5. Disconnecting robot...")
        robot.disconnect()
        print("   Disconnected.")
