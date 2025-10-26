import os
import threading
import time
from queue import Queue
from typing import Optional


class LeRobotWorker:
    """Queue-based worker to replay episodes on demand.

    Use enqueue_replay(status_store) to trigger a run. All heavy init is
    deferred to the first task so /command returns 202 even if deps are
    missing; in that case, the task will fail with a clear message instead
    of returning 503 at accept time.
    """

    def __init__(
        self,
        logger: Optional[object],
        serial_port: str,
        robot_id: str,
        dataset_id: str,
        episode_idx: int,
    ):
        self.logger = logger
        self.serial_port = serial_port
        self.robot_id = robot_id
        self.dataset_id = dataset_id
        self.episode_idx = episode_idx

        # Lazy fields (populated in _ensure_initialized)
        self._initialized = False
        self._init_lock = threading.Lock()
        self.LeRobotDataset = None
        self.SO100FollowerConfig = None
        self.SO100Follower = None
        self.busy_wait = None
        self.log_say = None
        self.robot = None
        self.dataset = None
        self.actions = None

        # Queue + thread
        self.queue: Queue = Queue()
        self.thread = threading.Thread(target=self._loop, name="lerobot-worker", daemon=True)
        self.thread.start()

    def _ensure_initialized(self):
        if self._initialized:
            return
        with self._init_lock:
            if self._initialized:
                return
            # Import optional deps lazily
            try:
                from lerobot.datasets.lerobot_dataset import LeRobotDataset  # type: ignore
                from lerobot.robots.so100_follower.config_so100_follower import (  # type: ignore
                    SO100FollowerConfig,
                )
                from lerobot.robots.so100_follower.so100_follower import (  # type: ignore
                    SO100Follower,
                )
                from lerobot.utils.robot_utils import busy_wait  # type: ignore
                from lerobot.utils.utils import log_say  # type: ignore
            except Exception as e:
                raise RuntimeError(
                    f"LeRobot optional deps not available: {e}. Install lerobot to use this feature."
                )

            self.LeRobotDataset = LeRobotDataset
            self.SO100FollowerConfig = SO100FollowerConfig
            self.SO100Follower = SO100Follower
            self.busy_wait = busy_wait
            self.log_say = log_say

            # Connect robot with retries
            self.robot = self.SO100Follower(self.SO100FollowerConfig(port=self.serial_port, id=self.robot_id))
            for attempt in range(3):
                try:
                    self.robot.connect()
                    break
                except RuntimeError as e:
                    self.log_say(f"Motor init failed: {e}, retry {attempt + 1}/3")
                    time.sleep(1)

            # Load dataset
            self.dataset = self.LeRobotDataset(self.dataset_id, episodes=[self.episode_idx])
            self.actions = self.dataset.hf_dataset.select_columns("action")
            self._initialized = True

    def _loop(self):
        while True:
            item = self.queue.get()
            if item is None:
                break
            req_id, status_store = item
            try:
                # Ensure heavy setup is done
                self._ensure_initialized()
                status_store.update(req_id, {"state": "executing", "phase": "replay", "message": "Replaying episode"})
                self.log_say("Replaying episode")
                for idx in range(self.dataset.num_frames):
                    t0 = time.perf_counter()
                    action = {
                        name: float(self.actions[idx]["action"][i])
                        for i, name in enumerate(self.dataset.features["action"]["names"])
                    }
                    self.robot.send_action(action)
                    self.busy_wait(max(0, 1.0 / self.dataset.fps - (time.perf_counter() - t0)))

                # Move to neutral
                self.robot.send_action({name: 0.0 for name in self.dataset.features["action"]["names"]})
                time.sleep(1)
                status_store.update(req_id, {"state": "succeeded", "message": "Episode finished"})
            except Exception as e:  # best-effort
                if hasattr(status_store, "update"):
                    status_store.update(req_id, {"state": "failed", "message": str(e)})
                if self.logger:
                    try:
                        self.logger.exception("LeRobot worker task failed: %s", e)
                    except Exception:
                        self.logger.error("LeRobot worker task failed: %s", e)
            finally:
                self.queue.task_done()

    def enqueue_replay(self, status_store):
        import uuid
        req_id = str(uuid.uuid4())
        status_store.create(req_id, {"state": "queued", "phase": None, "message": "LeRobot replay queued"})
        self.queue.put((req_id, status_store))
        return req_id


def _build_or_get_worker(app) -> Optional[LeRobotWorker]:
    # Return existing worker if any
    worker = app.config.get("LEROBOT_WORKER")
    if worker:
        return worker

    # Read env and try to create
    serial_port = os.getenv("LEROBOT_PORT", "/dev/tty.usbmodem5A460836061")
    robot_id = os.getenv("LEROBOT_ID", "my_awesome_follower_arm10")
    dataset_id = os.getenv("LEROBOT_DATASET", "Shrek0/pet_main")
    try:
        episode_idx = int(os.getenv("LEROBOT_EPISODE_IDX", "0"))
    except ValueError:
        episode_idx = 0

    try:
        worker = LeRobotWorker(app.logger, serial_port, robot_id, dataset_id, episode_idx)
    except Exception as e:
        if app.logger:
            app.logger.warning("LeRobot worker not started: %s", e)
        else:
            print(f"LeRobot worker not started: {e}")
        return None

    app.config["LEROBOT_WORKER"] = worker
    return worker


def maybe_start_lerobot_worker(app) -> bool:
    """Initialize the LeRobot worker if env LEROBOT_ENABLED is truthy.

    Safe no-op if disabled or if deps missing.
    """
    enabled = os.getenv("LEROBOT_ENABLED", "false").lower() in ("1", "true", "yes")
    if not enabled:
        return False
    return _build_or_get_worker(app) is not None


def request_lerobot_replay(app, status_store) -> Optional[str]:
    """Ensure worker exists and enqueue a replay task; return request_id or None if unavailable."""
    worker = _build_or_get_worker(app)
    if not worker:
        return None
    return worker.enqueue_replay(status_store)
