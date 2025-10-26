import os
import time

# LeRobot imports (required when running an episode)
from lerobot.datasets.lerobot_dataset import LeRobotDataset
from lerobot.robots.so100_follower.config_so100_follower import SO100FollowerConfig
from lerobot.robots.so100_follower.so100_follower import SO100Follower
from lerobot.utils.robot_utils import busy_wait
from lerobot.utils.utils import log_say


def run_episode(episode_idx: int = 0):
    """Replay a single episode using the SO100 follower, blocking until done.

    Env overrides (optional):
    - LEROBOT_PORT
    - LEROBOT_ID
    - LEROBOT_DATASET
    """

    port = os.getenv("LEROBOT_PORT", "/dev/tty.usbmodem5A460836061")
    rid = os.getenv("LEROBOT_ID", "my_awesome_follower_arm10")
    dataset_id = os.getenv("LEROBOT_DATASET", "Shrek0/pet_main")

    robot_config = SO100FollowerConfig(
        port=port,
        id=rid,
    )
    robot = SO100Follower(robot_config)

    # Retry connect
    for attempt in range(3):
        try:
            robot.connect()
            break
        except RuntimeError as e:
            log_say(f"Motor init failed: {e}, retry {attempt + 1}/3")
            time.sleep(1)

    dataset = LeRobotDataset(dataset_id, episodes=[episode_idx])
    actions = dataset.hf_dataset.select_columns("action")

    log_say(f"Replaying episode {episode_idx}")
    for idx in range(dataset.num_frames):
        t0 = time.perf_counter()
        action = {
            name: float(actions[idx]["action"][i])
            for i, name in enumerate(dataset.features["action"]["names"])
        }
        robot.send_action(action)
        busy_wait(max(0, 1.0 / dataset.fps - (time.perf_counter() - t0)))

    # Neutral pose
    robot.send_action({name: 0.0 for name in dataset.features["action"]["names"]})
    time.sleep(1)

    try:
        robot.disconnect()
    except Exception as e:
        log_say(f"Warning during disconnect: {e}")

    log_say("Episode finished.")
