import os
import sys
from pprint import pprint

from lerobot.robots.so101_follower.so101_follower import SO101Follower, SO101FollowerConfig

port = sys.argv[1] if len(sys.argv) > 1 else os.getenv("ARM_PORT", "COM8")
print("Port:", port)

cfg = SO101FollowerConfig(port=port)
robot = SO101Follower(cfg)

names = dir(robot)
interesting = [
    n for n in names
    if any(k in n.lower() for k in [
        "home", "reset", "zero", "mid", "center", "pose", "position", "joint", "target", "move", "goto", "disconnect", "connect"
    ])
]
print("Interesting attributes (name -> callable?):")
for n in interesting:
    try:
        attr = getattr(robot, n)
        print(f" - {n} : {'callable' if callable(attr) else type(attr).__name__}")
    except Exception as e:
        print(f" - {n} : <error {e}>")
