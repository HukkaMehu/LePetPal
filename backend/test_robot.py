#!/usr/bin/env python3
"""Test script to run robot episode directly - bypasses Flask server"""
import os
import time

# Use your provided example code exactly as-is
from lerobot.datasets.lerobot_dataset import LeRobotDataset
from lerobot.robots.so100_follower.config_so100_follower import SO100FollowerConfig
from lerobot.robots.so100_follower.so100_follower import SO100Follower
from lerobot.utils.robot_utils import busy_wait
from lerobot.utils.utils import log_say

episode_idx = 0
dataset_id = os.getenv("HF_DATASET_ID", "Shrek0/pet_main")
robot_port = os.getenv("ROBOT_PORT", "/dev/tty.usbmodem5A460836061")
robot_id = os.getenv("ROBOT_ID", "my_awesome_follower_arm10")

print(f"Connecting to robot at {robot_port}...")
robot_config = SO100FollowerConfig(port=robot_port, id=robot_id)
robot = SO100Follower(robot_config)
robot.connect()

print(f"Loading dataset {dataset_id}, episode {episode_idx}...")
dataset = LeRobotDataset(dataset_id, episodes=[episode_idx])
actions = dataset.hf_dataset.select_columns("action")

log_say(f"Replaying episode {episode_idx}")
for idx in range(dataset.num_frames):
    t0 = time.perf_counter()

    action = {
        name: float(actions[idx]["action"][i]) for i, name in enumerate(dataset.features["action"]["names"])
    }
    robot.send_action(action)

    busy_wait(1.0 / dataset.fps - (time.perf_counter() - t0))
    
    # Progress update
    if idx % max(1, dataset.fps // 2) == 0:
        pct = int((idx + 1) * 100 / dataset.num_frames)
        print(f"Progress: {pct}%")

print("Episode complete, disconnecting...")
robot.disconnect()
print("Done!")
