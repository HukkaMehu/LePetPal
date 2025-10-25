import threading
from typing import Dict, Optional


class StatusStore:
    def __init__(self):
        self._lock = threading.Lock()
        self._data: Dict[str, dict] = {}

    def create(self, request_id: str, initial: dict):
        with self._lock:
            self._data[request_id] = dict(initial)

    def update(self, request_id: str, patch: dict):
        with self._lock:
            if request_id in self._data:
                self._data[request_id].update(patch)

    def get(self, request_id: str) -> Optional[dict]:
        with self._lock:
            return dict(self._data.get(request_id)) if request_id in self._data else None
