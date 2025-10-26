"""
Background Video Stream Manager

Keeps the video buffer filled by maintaining a continuous connection
to the video source, even when no clients are actively viewing.
"""
import asyncio
import logging
from datetime import datetime
import cv2
import numpy as np
from app.core.video_buffer import video_buffer
from app.core.config import settings

logger = logging.getLogger(__name__)


class BackgroundStreamManager:
    """Manages a background video stream to keep the buffer filled."""
    
    def __init__(self):
        self.running = False
        self.task = None
        self.cap = None
        
    async def start(self):
        """Start the background stream."""
        if self.running:
            logger.info("Background stream already running")
            return
            
        self.running = True
        self.task = asyncio.create_task(self._stream_loop())
        logger.info("Background stream started")
        
    async def stop(self):
        """Stop the background stream."""
        if not self.running:
            return
            
        self.running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        
        if self.cap:
            self.cap.release()
            self.cap = None
            
        logger.info("Background stream stopped")
        
    async def _stream_loop(self):
        """Main streaming loop."""
        frame_count = 0
        
        try:
            while self.running:
                # Get or initialize video capture
                if self.cap is None or not self.cap.isOpened():
                    self.cap = self._init_capture()
                    if self.cap is None:
                        logger.warning("Failed to initialize video capture, retrying in 5s...")
                        await asyncio.sleep(5)
                        continue
                
                # Read frame
                ret, frame = self.cap.read()
                
                if not ret or frame is None:
                    logger.warning("Failed to read frame, reinitializing capture...")
                    if self.cap:
                        self.cap.release()
                    self.cap = None
                    await asyncio.sleep(1)
                    continue
                
                # Add frame to buffer
                video_buffer.add_frame(frame, datetime.utcnow())
                frame_count += 1
                
                # Log status periodically
                if frame_count % 300 == 0:  # Every 10 seconds at 30fps
                    buffer_info = video_buffer.get_buffer_info()
                    logger.info(
                        f"Background stream: {frame_count} frames processed, "
                        f"buffer has {buffer_info['frame_count']} frames "
                        f"({buffer_info['duration_seconds']:.1f}s)"
                    )
                
                # Control frame rate (30 fps)
                await asyncio.sleep(1 / 30)
                
        except asyncio.CancelledError:
            logger.info("Background stream cancelled")
            raise
        except Exception as e:
            logger.error(f"Error in background stream: {e}")
            self.running = False
        finally:
            if self.cap:
                self.cap.release()
                self.cap = None
    
    def _init_capture(self) -> cv2.VideoCapture:
        """Initialize video capture from configured source."""
        video_source = settings.VIDEO_SOURCE
        logger.info(f"Initializing video capture from: {video_source}")
        
        try:
            # Try to parse as integer (camera index)
            camera_index = int(video_source)
            cap = cv2.VideoCapture(camera_index)
            
            if cap.isOpened():
                # Set camera properties
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                cap.set(cv2.CAP_PROP_FPS, 30)
                logger.info(f"Camera {camera_index} opened successfully")
                return cap
            else:
                logger.warning(f"Failed to open camera {camera_index}")
                return None
                
        except ValueError:
            # Not an integer, treat as URL
            cap = cv2.VideoCapture(video_source)
            
            if cap.isOpened():
                logger.info(f"Remote stream opened successfully: {video_source}")
                return cap
            else:
                logger.warning(f"Failed to open remote stream: {video_source}")
                return None
        except Exception as e:
            logger.error(f"Error initializing capture: {e}")
            return None


# Global instance
background_stream = BackgroundStreamManager()
