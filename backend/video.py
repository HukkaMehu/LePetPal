import cv2
import numpy as np
import time
import sys
from typing import Generator


class CameraCapture:
    def __init__(self, camera_index: int = 0, width: int = 1280, height: int = 720):
        self.cap = None
        self.width = width
        self.height = height
        self.index = camera_index
        self.last_frame = None
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5
        
        # Try to open camera
        if not self._open_camera(camera_index, width, height):
            raise RuntimeError(f"Failed to open camera {camera_index}. Please check camera connection.")
        
        print(f"INFO: Camera {self.index} opened successfully ({self.width}x{self.height})")

    def _open_camera(self, index: int, width: int, height: int) -> bool:
        """Open camera with platform-specific backend."""
        # Release existing camera if any
        if self.cap is not None:
            try:
                self.cap.release()
            except Exception:
                pass
        
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
            # Set buffer size to 1 for lower latency
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            self.cap = cap
            self.index = index
            self.width = width
            self.height = height
            self.reconnect_attempts = 0
            return True
        return False
    
    def _reconnect(self) -> bool:
        """Attempt to reconnect to camera."""
        if self.reconnect_attempts >= self.max_reconnect_attempts:
            print(f"ERROR: Camera {self.index} failed after {self.max_reconnect_attempts} reconnection attempts.")
            return False
        
        self.reconnect_attempts += 1
        print(f"WARNING: Camera {self.index} disconnected. Reconnecting... (attempt {self.reconnect_attempts}/{self.max_reconnect_attempts})")
        time.sleep(0.5)
        return self._open_camera(self.index, self.width, self.height)

    def switch_camera(self, index: int, width: int, height: int) -> bool:
        """Switch to a different camera."""
        return self._open_camera(index, width, height)

    def read(self):
        """Read frame from camera with automatic reconnection."""
        if self.cap is None or not self.cap.isOpened():
            if not self._reconnect():
                # Return last known good frame if available
                if self.last_frame is not None:
                    return True, self.last_frame.copy()
                # Create error frame
                error_frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
                cv2.putText(error_frame, "Camera Disconnected", (50, self.height // 2), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)
                return False, error_frame
        
        ret, frame = self.cap.read()
        if not ret or frame is None:
            # Try to reconnect
            if self._reconnect():
                ret, frame = self.cap.read()
                if ret and frame is not None:
                    self.last_frame = frame.copy()
                    return True, frame
            
            # Return last known good frame
            if self.last_frame is not None:
                return True, self.last_frame.copy()
            
            # Create error frame
            error_frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
            cv2.putText(error_frame, "Camera Error", (50, self.height // 2), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)
            return False, error_frame
        
        # Store last good frame
        self.last_frame = frame.copy()
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
