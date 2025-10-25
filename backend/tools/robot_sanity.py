import os
import time
import sys

from dotenv import load_dotenv

# Ensure package imports work when run from repo root or backend/
try:
    from backend.adapters.arm_adapter import ArmAdapter
except ModuleNotFoundError:
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from adapters.arm_adapter import ArmAdapter


def main():
    load_dotenv()

    use_hardware_env = os.getenv("USE_HARDWARE", "false").lower() in ("1", "true", "yes")
    arm = ArmAdapter(use_hardware=use_hardware_env)

    print("[robot_sanity] connecting...")
    ok = False
    try:
        ok = arm.connect()
    except Exception as e:
        print("[robot_sanity] connect error:", e)
    if not ok:
        print("[robot_sanity] failed to connect. Ensure USE_HARDWARE=true and driver/port are configured.")
        return 1

    try:
        print("[robot_sanity] go home")
        arm.home()
        time.sleep(1.0)

        print("[robot_sanity] reading joints")
        joints = arm.get_joint_angles()
        print("[robot_sanity] joints:", joints)

        def nudge(idx: int, delta: float, hold: float = 0.6):
            base = arm.get_joint_angles()
            if len(base) < 6:
                raise RuntimeError("unexpected joint count")
            targets = list(base)
            targets[idx] = targets[idx] + delta
            arm.send_joint_targets({"targets": targets, "phase": f"nudge_j{idx}", "confidence": 0.9})
            time.sleep(hold)

        print("[robot_sanity] small joint nudges (+/- 0.05 rad)")
        for j in range(3):
            nudge(j, +0.05)
            nudge(j, -0.05)

        print("[robot_sanity] return home")
        arm.home()
        print("[robot_sanity] done")
        return 0
    except KeyboardInterrupt:
        print("[robot_sanity] interrupted, stopping")
        try:
            arm.stop()
        except Exception:
            pass
        return 130
    except Exception as e:
        print("[robot_sanity] error:", e)
        try:
            arm.stop()
        except Exception:
            pass
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
