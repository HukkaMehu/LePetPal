import cv2
import numpy as np
import time
from typing import Generator


class CameraCapture:
    def __init__(self, camera_index: int = 0, width: int = 1280, height: int = 720):
        self.cap = cv2.VideoCapture(camera_index)
        self.synthetic = False
        if self.cap.isOpened():
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        else:
            self.synthetic = True
            self.width = width
            self.height = height
        self.t0 = time.time()

    def read(self):
        if self.synthetic:
            t = time.time() - self.t0
            img = np.zeros((self.height, self.width, 3), dtype=np.uint8)
            cv2.putText(img, f"LePetPal - synthetic ({t:.1f}s)", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 200, 255), 2)
            x = int((np.sin(t) * 0.4 + 0.5) * (self.width - 120))
            y = int((np.cos(t * 0.7) * 0.3 + 0.5) * (self.height - 80))
            cv2.rectangle(img, (x, y), (x + 120, y + 80), (0, 255, 0), 2)
            return True, img
        ret, frame = self.cap.read()
        if not ret or frame is None:
            # fallback to synthetic if camera drops
            self.synthetic = True
            self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 1280)
            self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 720)
            return self.read()
        return True, frame


def mjpeg_stream(camera: CameraCapture, overlays: bool = True) -> Generator[bytes, None, None]:
    boundary = b"--frame"
    while True:
        ok, frame = camera.read()
        if not ok:
            time.sleep(0.05)
            continue
        if overlays:
            ts = time.strftime("%H:%M:%S")
            cv2.putText(frame, f"{ts}", (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        ret, jpeg = cv2.imencode('.jpg', frame)
        if not ret:
            continue
        buf = jpeg.tobytes()
        yield boundary + b"\r\n" + b"Content-Type: image/jpeg\r\n\r\n" + buf + b"\r\n"
