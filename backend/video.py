import cv2
import numpy as np
import time
import sys
from typing import Generator


class CameraCapture:
    def __init__(self, camera_index: int = 0, width: int = 1280, height: int = 720):
        self.cap = None
        self.synthetic = False
        self.width = width
        self.height = height
        self.index = None
        self._open_with_fallback(camera_index, width, height)
        if self.cap is None or not self.cap.isOpened():
            # auto-scan a few indices
            for i in range(0, 5):
                if self._open_with_fallback(i, width, height):
                    break
        if self.cap is None or not self.cap.isOpened():
            self.synthetic = True
            print(f"WARNING: No camera found. Using synthetic video feed.")
        else:
            print(f"INFO: Camera {self.index} opened successfully ({self.width}x{self.height})")
        self.t0 = time.time()

    def _open_with_fallback(self, index: int, width: int, height: int) -> bool:
        # Try platform-specific backend first on Windows
        cap = None
        if sys.platform.startswith('win'):
            try:
                cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
            except Exception:
                cap = cv2.VideoCapture(index)
        else:
            cap = cv2.VideoCapture(index)
        if cap is not None and cap.isOpened():
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            # Replace existing
            if self.cap is not None:
                try:
                    self.cap.release()
                except Exception:
                    pass
            self.cap = cap
            self.index = index
            self.synthetic = False
            self.width = width
            self.height = height
            return True
        return False

    def switch_camera(self, index: int, width: int, height: int) -> bool:
        return self._open_with_fallback(index, width, height)

    def read(self):
        if self.synthetic:
            t = time.time() - self.t0
            img = np.zeros((self.height, self.width, 3), dtype=np.uint8)
            cv2.putText(img, f"LePetPal - synthetic ({t:.1f}s)", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 200, 255), 2)
            x = int((np.sin(t) * 0.4 + 0.5) * (self.width - 120))
            y = int((np.cos(t * 0.7) * 0.3 + 0.5) * (self.height - 80))
            cv2.rectangle(img, (x, y), (x + 120, y + 80), (0, 255, 0), 2)
            return True, img
        ret, frame = self.cap.read() if self.cap is not None else (False, None)
        if not ret or frame is None:
            # fallback to synthetic if camera drops
            self.synthetic = True
            try:
                self.width = int((self.cap and self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or self.width)
                self.height = int((self.cap and self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or self.height)
            except Exception:
                pass
            return self.read()
        return True, frame


def mjpeg_stream(camera: CameraCapture, overlays: bool = True, quality: int = 50, scale: float = 0.5, fps: int = 10) -> Generator[bytes, None, None]:
    """
    Optimized MJPEG stream for internet streaming.
    
    Args:
        camera: Camera capture object
        overlays: Show timestamp overlay
        quality: JPEG quality (1-100, lower = smaller file, faster)
        scale: Scale factor (0.5 = half size, faster)
        fps: Target frames per second (lower = less bandwidth)
    """
    boundary = b"--frame"
    frame_delay = 1.0 / fps
    last_frame_time = 0
    
    while True:
        # Frame rate limiting
        current_time = time.time()
        if current_time - last_frame_time < frame_delay:
            time.sleep(0.01)
            continue
        last_frame_time = current_time
        
        ok, frame = camera.read()
        if not ok:
            time.sleep(0.05)
            continue
        
        # Resize frame for lower bandwidth
        if scale != 1.0:
            new_width = int(frame.shape[1] * scale)
            new_height = int(frame.shape[0] * scale)
            frame = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_AREA)
        
        if overlays:
            ts = time.strftime("%H:%M:%S")
            cv2.putText(frame, f"{ts}", (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Encode with lower quality for faster transmission
        encode_params = [cv2.IMWRITE_JPEG_QUALITY, quality]
        ret, jpeg = cv2.imencode('.jpg', frame, encode_params)
        if not ret:
            continue
        
        buf = jpeg.tobytes()
        yield boundary + b"\r\n" + b"Content-Type: image/jpeg\r\n\r\n" + buf + b"\r\n"
