import threading
import time
import uuid
from typing import Dict, Optional

from status_store import StatusStore
from model_runner import ModelRunner
from adapters.arm_adapter import ArmAdapter
from adapters.servo_adapter import ServoAdapter
from adapters.tts import TTSSpeaker
from safety import SafetyManager


class BusyError(Exception):
    pass


class CommandManager:
    def __init__(self, status_store: StatusStore, arm: ArmAdapter, servo: ServoAdapter, tts: TTSSpeaker, model: ModelRunner, safety: SafetyManager):
        self.status = status_store
        self.arm = arm
        self.servo = servo
        self.tts = tts
        self.model = model
        self.safety = safety

        self._active_lock = threading.Lock()
        self._active_req_id: Optional[str] = None
        self._cancel_event = threading.Event()

    def start(self, prompt: str, options: dict) -> str:
        # Single active guard
        with self._active_lock:
            if self._active_req_id is not None:
                raise BusyError()
            req_id = str(uuid.uuid4())
            self._active_req_id = req_id
            self._cancel_event.clear()

        self.status.create(req_id, {"state": "planning", "phase": None, "message": f"Accepted: {prompt}"})

        t = threading.Thread(target=self._run_job, args=(req_id, prompt, options), daemon=True)
        t.start()
        return req_id

    def interrupt_and_home(self) -> str:
        # Always preempt
        self._cancel_event.set()
        # Start a new short job to go home even if active exists
        req_id = str(uuid.uuid4())
        self.status.create(req_id, {"state": "executing", "phase": None, "message": "Go home"})
        t = threading.Thread(target=self._run_home, args=(req_id,), daemon=True)
        t.start()
        return req_id

    def _run_home(self, req_id: str):
        try:
            self.arm.home()
            self.status.update(req_id, {"state": "succeeded", "message": "At home pose"})
        except Exception as e:
            self.status.update(req_id, {"state": "failed", "message": f"home error: {e}"})
        finally:
            # Clear active if any
            with self._active_lock:
                self._active_req_id = None
            self._cancel_event.clear()

    def _run_job(self, req_id: str, prompt: str, options: dict):
        t0 = time.time()
        try:
            self.status.update(req_id, {"state": "executing", "phase": "detect", "message": "Detecting"})
            # Mocked loop using ModelRunner stub
            for chunk in self.model.infer(prompt):
                if self._cancel_event.is_set():
                    self.arm.home()
                    self.status.update(req_id, {"state": "aborted", "message": "Interrupted by Go Home"})
                    return
                if not self.safety.validate_targets(chunk):
                    self.status.update(req_id, {"state": "failed", "message": "safety check failed"})
                    return
                # Send to arm (mock)
                self.arm.send_joint_targets(chunk)
                # Update status with phase/confidence if provided
                phase = chunk.get("phase")
                conf = chunk.get("confidence")
                self.status.update(req_id, {"phase": phase, "confidence": conf, "message": phase or "executing"})
                time.sleep(1.0 / max(1, self.model.rate_hz))

            # Throw macro guard
            if prompt == "pick up the ball" and self.safety.ready_to_throw(self.arm.get_joint_angles()) and self.safety.workspace_clear():
                self.arm.throw_macro()
                self.status.update(req_id, {"state": "handoff_macro", "message": "throwing"})
                time.sleep(0.5)

            self.status.update(req_id, {"state": "succeeded", "message": "Completed", "duration_ms": int((time.time() - t0) * 1000)})
        except Exception as e:
            self.status.update(req_id, {"state": "failed", "message": str(e)})
        finally:
            with self._active_lock:
                self._active_req_id = None
            self._cancel_event.clear()
