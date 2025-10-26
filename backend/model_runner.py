import time
from typing import Dict, Iterable, List


class ModelRunner:
    def __init__(self, model_path: str, rate_hz: int = 15, mode: str = "scripted"):
        self.model_path = model_path
        self.rate_hz = rate_hz
        self.mode = mode
        self.loaded = False
        self._load()

    def _load(self):
        # TODO: load SmolVLA checkpoint when mode == 'smolvla'. For skeleton, mark loaded.
        self.loaded = True

    def infer(self, instruction: str) -> Iterable[Dict]:
        """Yield control chunks.
        - scripted: deterministic phases for demo flow.
        - smolvla: placeholder (fallback to scripted until integrated).
        """
        if self.mode != "scripted":
            # Placeholder: fall back to scripted until SmolVLA is integrated
            mode = "scripted"
        else:
            mode = self.mode

        if mode == "scripted":
            if instruction == "get the treat":
                phases = [
                    ("detect", [0.1, 0.1, 0.0, 0.0, 0.0, 0.0], 0.7),
                    ("approach", [0.2, 0.1, 0.0, 0.1, 0.0, 0.0], 0.75),
                    ("grasp", [0.3, 0.1, 0.0, 0.1, 0.0, 0.0], 0.8),
                    ("lift", [0.2, 0.2, 0.0, 0.1, 0.0, 0.0], 0.82),
                    ("drop", [0.1, 0.2, 0.0, 0.1, 0.0, 0.0], 0.84),
                ]
            else:
                phases = [
                    ("detect", [0.0, 0.1, 0.0, 0.0, 0.0, 0.0], 0.7),
                    ("approach", [0.1, 0.2, 0.0, 0.0, 0.0, 0.0], 0.75),
                    ("grasp", [0.2, 0.3, 0.0, 0.1, 0.0, 0.0], 0.8),
                    ("lift", [0.2, 0.2, 0.1, 0.1, 0.0, 0.0], 0.82),
                    ("ready_to_throw", [0.2, 0.2, 0.2, 0.1, 0.0, 0.0], 0.85),
                ]
            for phase, targets, conf in phases:
                yield {"phase": phase, "targets": targets, "confidence": conf}
                time.sleep(1.0 / max(1, self.rate_hz))
        else:
            # smolvla placeholder path (not used until integrated)
            for phase, targets, conf in []:
                yield {"phase": phase, "targets": targets, "confidence": conf}
                time.sleep(1.0 / max(1, self.rate_hz))
