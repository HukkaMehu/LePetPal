"""
Video Frame Buffer

Stores recent video frames in memory for clip extraction.
Implements a circular buffer that keeps the last N minutes of frames.
"""
import asyncio
import cv2
import numpy as np
from collections import deque
from datetime import datetime, timedelta
from typing import Optional, List, Tuple
import threading


class VideoFrameBuffer:
    """
    Circular buffer for storing recent video frames.
    
    Features:
    - Stores frames with timestamps
    - Automatically drops old frames
    - Thread-safe access
    - Configurable buffer size
    """
    
    def __init__(self, max_duration_seconds: int = 300):
        """
        Initialize video buffer.
        
        Args:
            max_duration_seconds: Maximum duration to keep in buffer (default 5 minutes)
        """
        self.max_duration = timedelta(seconds=max_duration_seconds)
        self.frames: deque = deque()  # (timestamp, frame_data)
        self.lock = threading.Lock()
        self._running = False
        
    def add_frame(self, frame: np.ndarray, timestamp: Optional[datetime] = None):
        """
        Add a frame to the buffer.
        
        Args:
            frame: OpenCV frame (numpy array)
            timestamp: Frame timestamp (defaults to now)
        """
        if timestamp is None:
            timestamp = datetime.utcnow()
        
        with self.lock:
            # Add new frame
            self.frames.append((timestamp, frame.copy()))
            
            # Remove old frames
            cutoff_time = datetime.utcnow() - self.max_duration
            while self.frames and self.frames[0][0] < cutoff_time:
                self.frames.popleft()
    
    def get_frames(
        self,
        start_time: datetime,
        end_time: datetime
    ) -> List[Tuple[datetime, np.ndarray]]:
        """
        Extract frames within a time range.
        
        Args:
            start_time: Start of time range
            end_time: End of time range
            
        Returns:
            List of (timestamp, frame) tuples
        """
        with self.lock:
            result = []
            for timestamp, frame in self.frames:
                if start_time <= timestamp <= end_time:
                    result.append((timestamp, frame.copy()))
            return result
    
    def get_buffer_info(self) -> dict:
        """Get information about the buffer state."""
        try:
            with self.lock:
                if not self.frames:
                    return {
                        "frame_count": 0,
                        "duration_seconds": 0,
                        "oldest_frame": None,
                        "newest_frame": None,
                    }
                
                # Quick access to first and last elements
                frame_count = len(self.frames)
                oldest = self.frames[0][0]
                newest = self.frames[-1][0]
                duration = (newest - oldest).total_seconds()
                
                return {
                    "frame_count": frame_count,
                    "duration_seconds": duration,
                    "oldest_frame": oldest.isoformat(),
                    "newest_frame": newest.isoformat(),
                }
        except Exception as e:
            return {
                "frame_count": 0,
                "duration_seconds": 0,
                "oldest_frame": None,
                "newest_frame": None,
                "error": str(e)
            }
    
    def clear(self):
        """Clear all frames from buffer."""
        with self.lock:
            self.frames.clear()


# Global buffer instance - reduced to 60 seconds for better performance
video_buffer = VideoFrameBuffer(max_duration_seconds=60)  # 1 minute
