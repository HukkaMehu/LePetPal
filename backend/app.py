import os
import threading
import time
import uuid
from typing import Optional

from flask import Flask, Response, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

from video import CameraCapture, mjpeg_stream
from status_store import StatusStore
from command_manager import CommandManager, BusyError
from adapters.arm_adapter import ArmAdapter
from adapters.servo_adapter import ServoAdapter
from adapters.tts import TTSSpeaker
from model_runner import ModelRunner
from safety import SafetyManager


ALLOWED_PROMPTS = {"pick up the ball", "get the treat", "go home"}


def create_app() -> Flask:
    load_dotenv()

    app = Flask(__name__)

    # CORS configuration
    cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
    CORS(
        app,
        origins=cors_origins,
        methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type"],
    )

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
        try:
            data = request.get_json(force=True, silent=True) or {}
        except Exception:
            return jsonify({"error": {"code": "invalid", "http": 400, "message": "Invalid JSON"}}), 400

        prompt = (data.get("prompt") or "").strip()
        options = data.get("options") or {}

        if prompt not in ALLOWED_PROMPTS:
            return jsonify({"error": {"code": "invalid", "http": 400, "message": "Invalid prompt"}}), 400

        # Special handling: Go Home must preempt
        if prompt == "go home":
            req_id = cmd_mgr.interrupt_and_home()
            return jsonify({"request_id": req_id, "status": "accepted"}), 202

        try:
            req_id = cmd_mgr.start(prompt=prompt, options=options)
        except BusyError:
            return jsonify({"error": {"code": "busy", "http": 409, "message": "Another command is in progress"}}), 409

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
        data = request.get_json(force=True, silent=True) or {}
        duration_ms = int(data.get("duration_ms", 600))
        try:
            servo.dispense(duration_ms)
            return jsonify({"status": "ok"}), 200
        except Exception as e:
            return jsonify({"error": {"code": "hardware_error", "http": 500, "message": str(e)}}), 500

    @app.post("/speak")
    def speak():
        data = request.get_json(force=True, silent=True) or {}
        text = (data.get("text") or "").strip()
        if not text:
            return jsonify({"error": {"code": "invalid", "http": 400, "message": "Missing text"}}), 400
        try:
            tts.speak(text)
            return jsonify({"status": "ok"}), 200
        except Exception as e:
            return jsonify({"error": {"code": "tts_error", "http": 500, "message": str(e)}}), 500

    # Attach components for testing/access if needed
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

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=app.config.get("PORT", 5000), threaded=True)
