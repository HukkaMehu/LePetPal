import sys
import time

from serial.tools import list_ports
from lerobot.robots.so101_follower.so101_follower import SO101Follower, SO101FollowerConfig


def try_port(dev: str) -> bool:
    robot = None
    try:
        cfg = SO101FollowerConfig(port=dev)
        robot = SO101Follower(cfg)
        robot.connect()
        print(f"CONNECTED: {dev}")
        try:
            robot.disconnect()
        except Exception:
            pass
        return True
    except Exception as e:
        print(f"FAILED: {dev} -> {e}")
        try:
            if robot is not None and getattr(robot, "is_connected", False):
                robot.disconnect()
        except Exception:
            pass
        return False


def main() -> int:
    ports = list(list_ports.comports())
    if not ports:
        print("No serial ports found.")
        return 2
    print("Found ports:")
    for p in ports:
        print(" -", p.device, p.description)
    for p in ports:
        if try_port(p.device):
            print(f"BEST_PORT={p.device}")
            return 0
    print("No working SO-101 follower port detected.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
