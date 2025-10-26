import os
import threading
import time
import uuid
from typing import Optional
import subprocess 

from flask import Flask, Response, jsonify, request
from dotenv import load_dotenv

from backend.video import CameraCapture, mjpeg_stream
from backend.status_store import StatusStore
from backend.command_manager import CommandManager, BusyError
from backend.adapters.arm_adapter import ArmAdapter
from backend.adapters.servo_adapter import ServoAdapter
from backend.adapters.tts import TTSSpeaker
from backend.model_runner import ModelRunner
from backend.safety import SafetyManager
from backend.lerobot_worker import maybe_start_lerobot_worker


ALLOWED_PROMPTS = {"pick up the ball", "get the treat", "go home"}


def create_app() -> Flask:
    load_dotenv()

    app = Flask(__name__)

    # Config
    port = int(os.getenv("PORT", 5000))
    camera_index = int(os.getenv("CAMERA_INDEX", 0))
    stream_res = os.getenv("STREAM_RES", "1280x720")
    use_hardware = os.getenv("USE_HARDWARE", "false").lower() in ("1", "true", "yes")
    model_mode = os.getenv("MODEL_MODE", "scripted").lower()  # 'scripted' | 'smolvla'
    calibration_path = os.getenv("CALIBRATION_PATH", "")
    width, height = [int(x) for x in stream_res.split("x")] if "x" in stream_res else (1280, 720)

    # Singletons
    camera = CameraCapture(camera_index=camera_index, width=width, height=height)
    status_store = StatusStore()

    arm = ArmAdapter(use_hardware=use_hardware)  # real or mock decided inside adapter
    servo = ServoAdapter()
    tts = TTSSpeaker()
    model = ModelRunner(os.getenv("MODEL_PATH", ""), rate_hz=int(os.getenv("INFERENCE_RATE_HZ", 15)), mode=model_mode)
    safety = SafetyManager(calibration_path=calibration_path if calibration_path else None)

    if use_hardware:
        try:
            arm.connect()
        except Exception:
            # keep going with mock if connect fails
            pass

    cmd_mgr = CommandManager(status_store=status_store, arm=arm, servo=servo, tts=tts, model=model, safety=safety)

    @app.get("/health")
    def health():
        return jsonify({"status": "ok", "api": 1, "version": "v0.1"}), 200

    @app.get("/video_feed")
    def video_feed():
        overlays = request.args.get("overlays", "1") == "1"
        cam_param = request.args.get("camera")
        w_param = request.args.get("width")
        h_param = request.args.get("height")
        try:
            new_w = int(w_param) if w_param else None
            new_h = int(h_param) if h_param else None
            new_idx = int(cam_param) if cam_param is not None else None
        except ValueError:
            new_w = new_h = new_idx = None

        if new_idx is not None or new_w is not None or new_h is not None:
            # Switch camera or resolution on-the-fly
            target_idx = new_idx if new_idx is not None else (getattr(camera, 'index', 0) or 0)
            target_w = new_w if new_w is not None else getattr(camera, 'width', 1280)
            target_h = new_h if new_h is not None else getattr(camera, 'height', 720)
            camera.switch_camera(target_idx, target_w, target_h)
        return Response(mjpeg_stream(camera, overlays=overlays), mimetype="multipart/x-mixed-replace; boundary=frame")

    @app.post("/command")
    def command():
        # Parse request body to determine which dataset to use
        body = request.get_json(silent=True) or {}
        command_value = body if isinstance(body, int) else body.get("command")
        
        # Convert to integer if it's a string or other type
        try:
            command_value = int(command_value) if command_value is not None else 0
        except (ValueError, TypeError):
            command_value = 0
        
        # Debug logging
        print(f"DEBUG: Received body: {body}")
        print(f"DEBUG: Parsed command_value: {command_value} (type: {type(command_value)})")
        
        # Map command values to datasets
        # 0 = pet_main (default), 1 = throw_main
        if command_value == 1:
            dataset_id = "Shrek0/throw_main"
            task_name = "throw"
        else:
            dataset_id = "Shrek0/pet_main"
            task_name = "pet"
        
        # Ending position (same for both)
        ending_position = {
            "shoulder_pan": 0.0,
            "shoulder_lift": 0.0,
            "elbow_flex": 0.0,
            "wrist_flex": 0.0,
            "wrist_roll": 0.0,
            "gripper": 0.0,
        }
        
        # Run the LeRobot one-shot episode inline (background thread), return a request id
        req_id = str(uuid.uuid4())
        status_store.create(req_id, {"state": "queued", "phase": None, "message": f"robot episode queued ({task_name})"})

        def _run_robot_episode():
            try:
                # Workaround for Python 3.14: Force multiprocess to use dill's pickle
                import multiprocess
                import dill
                multiprocess.reduction.ForkingPickler = dill.Pickler
                
                # Import heavy deps lazily so server can start without them
                from lerobot.datasets.lerobot_dataset import LeRobotDataset
                from lerobot.robots.so100_follower.config_so100_follower import SO100FollowerConfig
                from lerobot.robots.so100_follower.so100_follower import SO100Follower
                from lerobot.utils.robot_utils import busy_wait
                from lerobot.utils.utils import log_say
            except Exception as e:
                status_store.update(req_id, {"state": "failed", "message": f"Import error: {e}"})
                return

            # Config: force episode 0, use dataset from command
            episode_idx = 0
            robot_port = os.getenv("ROBOT_PORT", os.getenv("LEROBOT_PORT", "/dev/tty.usbmodem5A460836061"))
            robot_id = os.getenv("ROBOT_ID", os.getenv("LEROBOT_ID", "full_new"))

            robot = None
            try:
                # Disable multiprocessing to avoid Python 3.14 pickle issues
                os.environ["HF_DATASETS_IN_MEMORY_MAX_SIZE"] = "0"
                os.environ["TOKENIZERS_PARALLELISM"] = "false"
                
                status_store.update(req_id, {"state": "executing", "phase": "connect", "message": f"Connecting robot at {robot_port}"})
                robot_config = SO100FollowerConfig(port=robot_port, id=robot_id)
                robot = SO100Follower(robot_config)
                # Retry connect, handle "already connected" gracefully
                for attempt in range(3):
                    try:
                        robot.connect()
                        break
                    except RuntimeError as e:
                        error_msg = str(e)
                        if "already connected" in error_msg.lower():
                            log_say(f"Robot already connected, attempting disconnect and reconnect...")
                            try:
                                robot.disconnect()
                                time.sleep(0.5)
                                robot.connect()
                                break
                            except Exception as reconnect_err:
                                log_say(f"Reconnect failed: {reconnect_err}")
                                if attempt == 2:
                                    raise
                        else:
                            log_say(f"Motor init failed: {e}, retry {attempt + 1}/3")
                            time.sleep(1)
                            if attempt == 2:
                                raise

                status_store.update(req_id, {"state": "executing", "phase": "load", "message": f"Loading dataset {dataset_id} ep {episode_idx}"})
                dataset = LeRobotDataset(dataset_id, episodes=[episode_idx])
                actions = dataset.hf_dataset.select_columns("action")

                status_store.update(req_id, {"state": "executing", "phase": "replay", "message": f"Replaying episode {episode_idx}"})
                for idx in range(dataset.num_frames):
                    t0 = time.perf_counter()
                    action = {
                        name: float(actions[idx]["action"][i])
                        for i, name in enumerate(dataset.features["action"]["names"])
                    }
                    robot.send_action(action)
                    busy_wait(max(0, 1.0 / dataset.fps - (time.perf_counter() - t0)))
                    # occasional progress update
                    if idx % max(1, dataset.fps // 2) == 0:
                        pct = int((idx + 1) * 100 / max(1, dataset.num_frames))
                        status_store.update(req_id, {"phase": "replay", "progress": pct, "message": f"Replaying {pct}%"})

                # Move to ending position and cleanup
                robot.send_action(ending_position)
                time.sleep(1)
                
                status_store.update(req_id, {"state": "succeeded", "message": "Episode finished and robot disconnected."})
            except Exception as e:
                status_store.update(req_id, {"state": "failed", "message": str(e)})
            finally:
                # Always disconnect robot, even on error
                if robot is not None:
                    try:
                        robot.disconnect()
                        log_say("Robot disconnected successfully")
                    except Exception as disc_err:
                        log_say(f"Warning: Disconnect failed: {disc_err}")

        threading.Thread(target=_run_robot_episode, name="run-robot-episode", daemon=True).start()
        return jsonify({"request_id": req_id, "status": "accepted"}), 202

    @app.get("/status/<request_id>")
    def status(request_id: str):
        st = status_store.get(request_id)
        if not st:
            # Keep 200 per lite contract; indicate unknown id in message
            return jsonify({"state": "failed", "phase": None, "message": "unknown request_id"}), 200
        return jsonify(st), 200

    @app.post("/dispense_treat")
    def dispense():
        # Always run the LeRobot one-shot episode inline (background thread)
        req_id = str(uuid.uuid4())
        status_store.create(req_id, {"state": "queued", "phase": None, "message": "robot episode queued"})

        def _run_robot_episode():
            try:
                # Import heavy deps lazily so server can start without them
                from lerobot.datasets.lerobot_dataset import LeRobotDataset
                from lerobot.robots.so100_follower.config_so100_follower import SO100FollowerConfig
                from lerobot.robots.so100_follower.so100_follower import SO100Follower
                from lerobot.utils.robot_utils import busy_wait
                from lerobot.utils.utils import log_say
            except Exception as e:
                status_store.update(req_id, {"state": "failed", "message": f"Import error: {e}"})
                return

            # Config (allow env overrides)
            try:
                episode_idx = int(os.getenv("EPISODE_IDX", os.getenv("LEROBOT_EPISODE_IDX", "0")))
            except Exception:
                episode_idx = 0
            dataset_id = os.getenv("HF_DATASET_ID", os.getenv("LEROBOT_DATASET", "Shrek0/pet_main"))
            robot_port = os.getenv("ROBOT_PORT", os.getenv("LEROBOT_PORT", "/dev/tty.usbmodem5A460836061"))
            robot_id = os.getenv("ROBOT_ID", os.getenv("LEROBOT_ID", "full_new"))

            try:
                status_store.update(req_id, {"state": "executing", "phase": "connect", "message": f"Connecting robot at {robot_port}"})
                robot_config = SO100FollowerConfig(port=robot_port, id=robot_id)
                robot = SO100Follower(robot_config)
                # Retry connect
                for attempt in range(3):
                    try:
                        robot.connect()
                        break
                    except RuntimeError as e:
                        log_say(f"Motor init failed: {e}, retry {attempt + 1}/3")
                        time.sleep(1)

                status_store.update(req_id, {"state": "executing", "phase": "load", "message": f"Loading dataset {dataset_id} ep {episode_idx}"})
                dataset = LeRobotDataset(dataset_id, episodes=[episode_idx])
                actions = dataset.hf_dataset.select_columns("action")

                status_store.update(req_id, {"state": "executing", "phase": "replay", "message": f"Replaying episode {episode_idx}"})
                for idx in range(dataset.num_frames):
                    t0 = time.perf_counter()
                    action = {
                        name: float(actions[idx]["action"][i])
                        for i, name in enumerate(dataset.features["action"]["names"])
                    }
                    robot.send_action(action)
                    busy_wait(max(0, 1.0 / dataset.fps - (time.perf_counter() - t0)))
                    # occasional progress update
                    if idx % max(1, dataset.fps // 2) == 0:
                        pct = int((idx + 1) * 100 / max(1, dataset.num_frames))
                        status_store.update(req_id, {"phase": "replay", "progress": pct, "message": f"Replaying {pct}%"})

                # Neutral pose and cleanup
                robot.send_action({name: 0.0 for name in dataset.features["action"]["names"]})
                time.sleep(1)
                try:
                    robot.disconnect()
                except Exception:
                    pass
                status_store.update(req_id, {"state": "succeeded", "message": "Episode finished and robot disconnected."})
            except Exception as e:
                status_store.update(req_id, {"state": "failed", "message": str(e)})

        threading.Thread(target=_run_robot_episode, name="run-robot-episode", daemon=True).start()
        return jsonify({"request_id": req_id, "status": "accepted"}), 202

    @app.post("/connect_to_watch")
    def connect_to_watch():
        """
        Start watch control mode - runs watch_control_so101.py using conda lerobot environment.
        This enables manual control of the robot via Apple Watch gestures.
        """
        req_id = str(uuid.uuid4())
        status_store.create(req_id, {"state": "queued", "phase": None, "message": "watch control starting"})

        def _run_watch_control():
            try:
                status_store.update(req_id, {"state": "executing", "phase": "start", "message": "Starting watch control"})
                
                # Path to the watch control script
                watch_script_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "robotics-hackathon", "watch_control_so101.py")
                
                # Use the direct python path from the lerobot conda environment
                # This avoids conda activation issues
                conda_python = "/opt/anaconda3/envs/lerobot/bin/python"
                
                process = subprocess.Popen(
                    [conda_python, watch_script_path],
                    cwd=os.path.dirname(watch_script_path),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                status_store.update(req_id, {
                    "state": "executing", 
                    "phase": "running", 
                    "message": f"Watch control running (PID: {process.pid}). Move your watch to control the robot. Tap to toggle gripper.",
                    "pid": process.pid
                })
                
                # Don't wait for process to complete - let it run in background
                # Just check if it started successfully after a brief moment
                time.sleep(2)
                
                if process.poll() is not None:
                    # Process already exited - something went wrong
                    stdout, stderr = process.communicate()
                    status_store.update(req_id, {
                        "state": "failed", 
                        "message": f"Watch control exited immediately with code {process.returncode}",
                        "stderr": stderr[:500] if stderr else None,  # Limit stderr size
                        "stdout": stdout[:500] if stdout else None
                    })
                else:
                    # Process is still running - success!
                    status_store.update(req_id, {
                        "state": "running", 
                        "phase": "active",
                        "message": f"Watch control is active (PID: {process.pid}). Control robot with watch gestures.",
                        "pid": process.pid
                    })
                    
            except Exception as e:
                import traceback
                status_store.update(req_id, {
                    "state": "failed", 
                    "message": f"Watch control error: {str(e)}",
                    "traceback": traceback.format_exc()[:500]
                })

        threading.Thread(target=_run_watch_control, name="watch-control", daemon=True).start()
        return jsonify({"request_id": req_id, "status": "accepted", "message": "Watch control starting. Check status for updates."}), 202

    # Expose key components and settings on app.config for debugging/introspection
    app.config.update({
        "camera": camera,
        "status_store": status_store,
        "command_manager": cmd_mgr,
        "arm": arm,
        "servo": servo,
        "tts": tts,
        "model": model,
        "safety": safety,
        "PORT": port,
        "USE_HARDWARE": use_hardware,
        "MODEL_MODE": model_mode,
        "CALIBRATION_PATH": calibration_path, 
    })

    # Optional: start LeRobot background worker on a second thread if enabled
    try:
        maybe_start_lerobot_worker(app)
    except Exception:
        # Never block server startup due to optional worker issues
        pass

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=app.config.get("PORT", 5000), threaded=True)
