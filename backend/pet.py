import os
import time
from lerobot.datasets.lerobot_dataset import LeRobotDataset
from lerobot.robots.so100_follower.config_so100_follower import SO100FollowerConfig
from lerobot.robots.so100_follower.so100_follower import SO100Follower
from lerobot.utils.robot_utils import busy_wait
from lerobot.utils.utils import log_say

# Get episode index from environment variable or default to 0
episode_idx = int(os.getenv("LEROBOT_EPISODE_IDX", "0"))
print("RUNNING")
robot_config = SO100FollowerConfig(
    port="/dev/tty.usbmodem5A460836061",
    id="my_awesome_follower_arm10"
)
robot = SO100Follower(robot_config)

# Retry connect to handle motor initialization
for attempt in range(3):
    try:
        robot.connect()
        break
    except RuntimeError as e:
        log_say(f"Motor init failed: {e}, retry {attempt + 1}/3")
        time.sleep(1)

dataset = LeRobotDataset("Shrek0/pet_main", episodes=[episode_idx])
actions = dataset.hf_dataset.select_columns("action")

# Run the episode once
log_say(f"Replaying episode {episode_idx}")
for idx in range(dataset.num_frames):
    t0 = time.perf_counter()
    action = {
        name: float(actions[idx]["action"][i])
        for i, name in enumerate(dataset.features["action"]["names"])
    }
    robot.send_action(action)
    busy_wait(max(0, 1.0 / dataset.fps - (time.perf_counter() - t0)))

# Move arm to neutral pose before disconnect
robot.send_action({name: 0.0 for name in dataset.features["action"]["names"]})
time.sleep(1)  # wait for motors to settle

# Disconnect
try:
    robot.disconnect()
except Exception as e:
    log_say(f"Warning during disconnect: {e}")

log_say("Episode finished.")
