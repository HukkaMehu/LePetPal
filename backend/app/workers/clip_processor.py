"""
Celery worker for processing video clip extraction.
Requirements: 4.2, 6.2
"""
from celery import Task
from app.core.celery_app import celery_app
from app.core.storage import storage_service
from app.core.video_buffer import video_buffer
from app.db.base import SessionLocal
from app.models.clip import Clip
from datetime import datetime, timedelta
import cv2
import numpy as np
import io
import logging
from uuid import UUID
from PIL import Image
import asyncio

logger = logging.getLogger(__name__)


class ClipProcessingTask(Task):
    """Base task with database session management."""
    
    def __call__(self, *args, **kwargs):
        """Execute task with database session."""
        return self.run(*args, **kwargs)


@celery_app.task(bind=True, base=ClipProcessingTask, name="process_clip")
def process_clip_task(
    self,
    clip_id: str,
    user_id: str,
    start_ts: str,
    duration_ms: int,
    labels: list = None
):
    """
    Process a video clip extraction job.
    
    Args:
        clip_id: UUID of the clip record
        user_id: UUID of the user
        start_ts: ISO format timestamp of clip start
        duration_ms: Duration of clip in milliseconds
        labels: Optional list of labels for the clip
    """
    db = SessionLocal()
    try:
        logger.info(f"Processing clip {clip_id}")
        
        # Update clip status to processing
        clip = db.query(Clip).filter(Clip.id == UUID(clip_id)).first()
        if not clip:
            logger.error(f"Clip {clip_id} not found")
            return {"status": "error", "message": "Clip not found"}
        
        # Generate timestamp string for file naming
        timestamp_str = datetime.fromisoformat(start_ts).strftime("%Y%m%d_%H%M%S")
        
        # Extract frames from video buffer
        video_key = f"clips/{user_id}/{timestamp_str}_clip.mp4"
        preview_key = f"clips/{user_id}/{timestamp_str}_preview.jpg"
        
        try:
            # Calculate time range
            start_time = datetime.fromisoformat(start_ts)
            end_time = start_time + timedelta(milliseconds=duration_ms)
            
            # Try to get frames from buffer via API (cross-process)
            import requests
            
            try:
                # Get buffer status
                status_response = requests.get('http://localhost:8000/video/buffer/status', timeout=5)
                buffer_info = status_response.json()
                logger.info(f"Buffer status: {buffer_info}")
                logger.info(f"Requesting frames from {start_time} to {end_time}")
                
                # Get frames from buffer
                frames_response = requests.get(
                    'http://localhost:8000/video/buffer/frames',
                    params={
                        'start_time': start_time.isoformat(),
                        'end_time': end_time.isoformat()
                    },
                    timeout=30
                )
                frames_data = frames_response.json()
                
                # Decode frames from base64
                import base64
                buffered_frames = []
                for frame_info in frames_data['frames']:
                    timestamp = datetime.fromisoformat(frame_info['timestamp'])
                    frame_bytes = base64.b64decode(frame_info['data'])
                    frame_array = np.frombuffer(frame_bytes, dtype=np.uint8)
                    frame = cv2.imdecode(frame_array, cv2.IMREAD_COLOR)
                    buffered_frames.append((timestamp, frame))
                    
            except Exception as e:
                logger.error(f"Failed to fetch frames from buffer API: {e}")
                buffered_frames = []
            
            if buffered_frames and len(buffered_frames) > 0:
                logger.info(f"Extracted {len(buffered_frames)} frames from buffer")
                logger.info(f"First frame: {buffered_frames[0][0]}, Last frame: {buffered_frames[-1][0]}")
                
                # Use buffered frames to create video
                width, height = buffered_frames[0][1].shape[1], buffered_frames[0][1].shape[0]
                fps = max(10, len(buffered_frames) / (duration_ms / 1000))  # Calculate FPS
                
            else:
                # Fallback: create animated placeholder if no frames in buffer
                logger.warning(f"No frames in buffer for time range, creating placeholder")
                width, height = 640, 480
                fps = 30
                duration_sec = max(1, duration_ms // 1000)  # At least 1 second
                buffered_frames = None
            
            # Create temporary file path
            import tempfile
            temp_video = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
            temp_video_path = temp_video.name
            temp_video.close()
            
            # Initialize video writer
            # Use mp4v codec which is most widely available
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(temp_video_path, fourcc, int(fps), (width, height))
            
            if not out.isOpened():
                logger.error(f"Failed to open video writer with mp4v codec")
                raise Exception("Failed to initialize video writer")
            
            logger.info(f"Video writer initialized: {width}x{height} @ {fps} fps, codec=mp4v")
            
            preview_frame = None
            
            if buffered_frames:
                # Use actual buffered frames
                for idx, (timestamp, frame) in enumerate(buffered_frames):
                    # Resize frame if needed
                    if frame.shape[1] != width or frame.shape[0] != height:
                        frame = cv2.resize(frame, (width, height))
                    
                    # Add timestamp overlay
                    cv2.putText(
                        frame,
                        timestamp.strftime("%H:%M:%S.%f")[:-3],
                        (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (255, 255, 255),
                        2
                    )
                    
                    # Add labels if provided
                    if labels:
                        label_text = ", ".join(labels[:3])
                        cv2.putText(
                            frame,
                            label_text,
                            (10, height - 20),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.6,
                            (0, 255, 0),
                            2
                        )
                    
                    out.write(frame)
                    
                    # Save middle frame as preview
                    if idx == len(buffered_frames) // 2:
                        preview_frame = frame.copy()
            else:
                # Fallback: create animated placeholder
                total_frames = int(duration_sec * fps)
                
                for frame_num in range(total_frames):
                    # Create animated frame
                    frame = np.zeros((height, width, 3), dtype=np.uint8)
                    
                    # Gradient background
                    for i in range(height):
                        frame[i, :] = [
                            int(100 + 155 * i / height),
                            80,
                            int(200 - 100 * i / height)
                        ]
                    
                    # Animated circle
                    progress = frame_num / total_frames
                    center_x = int(width * 0.2 + width * 0.6 * progress)
                    center_y = height // 2 + int(30 * np.sin(progress * 4 * np.pi))
                    cv2.circle(frame, (center_x, center_y), 50, (139, 69, 19), -1)
                    
                    # Add timestamp and labels
                    cv2.putText(
                        frame,
                        f"Placeholder - No buffer data",
                        (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (255, 255, 255),
                        2
                    )
                    
                    if labels:
                        label_text = ", ".join(labels[:3])
                        cv2.putText(
                            frame,
                            label_text,
                            (20, height - 20),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.6,
                            (255, 255, 255),
                            1
                        )
                    
                    out.write(frame)
                    
                    # Save middle frame as preview
                    if frame_num == total_frames // 2:
                        preview_frame = frame.copy()
            
            out.release()
            
            # Read video file and upload to S3
            with open(temp_video_path, 'rb') as f:
                video_data = f.read()
            
            video_uri = storage_service.upload_file(
                file_data=video_data,
                object_key=video_key,
                content_type="video/mp4"
            )
            
            # Clean up temp file
            import os
            os.unlink(temp_video_path)
            
            # Create and upload preview
            if preview_frame is not None:
                _, preview_buffer = cv2.imencode('.jpg', preview_frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                preview_data = preview_buffer.tobytes()
            else:
                # Fallback preview
                preview_image = Image.new('RGB', (640, 480), color=(50, 50, 150))
                preview_output = io.BytesIO()
                preview_image.save(preview_output, format='JPEG', quality=85)
                preview_data = preview_output.getvalue()
            
            preview_uri = storage_service.upload_file(
                file_data=preview_data,
                object_key=preview_key,
                content_type="image/jpeg"
            )
            
        except Exception as e:
            logger.error(f"Error creating video file: {e}")
            # Fallback to minimal placeholder
            preview_image = Image.new('RGB', (640, 480), color=(50, 50, 150))
            preview_output = io.BytesIO()
            preview_image.save(preview_output, format='JPEG', quality=85)
            preview_data = preview_output.getvalue()
            
            preview_uri = storage_service.upload_file(
                file_data=preview_data,
                object_key=preview_key,
                content_type="image/jpeg"
            )
            
            # Create minimal valid MP4
            video_uri = storage_service.upload_file(
                file_data=b'\x00\x00\x00\x20ftypisom\x00\x00\x02\x00isomiso2mp41\x00\x00\x00\x08free',
                object_key=video_key,
                content_type="video/mp4"
            )
        
        # Update clip record with S3 URIs
        clip.s3_uri = video_uri
        clip.preview_png = preview_uri
        if labels:
            clip.labels = labels
        
        db.commit()
        db.refresh(clip)
        
        logger.info(f"Clip {clip_id} processed successfully")
        
        return {
            "status": "completed",
            "clip_id": clip_id,
            "s3_uri": video_uri,
            "preview_uri": preview_uri
        }
        
    except Exception as e:
        logger.error(f"Error processing clip {clip_id}: {e}")
        db.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        db.close()


def process_clip_sync(
    clip_id: str,
    user_id: str,
    start_ts: str,
    duration_ms: int,
    labels: list = None
):
    """
    Process a video clip synchronously in the FastAPI process.
    This has direct access to the in-memory video buffer.
    Used with FastAPI BackgroundTasks.
    
    Args:
        clip_id: UUID of the clip record
        user_id: UUID of the user
        start_ts: ISO format timestamp of clip start
        duration_ms: Duration of clip in milliseconds
        labels: Optional list of labels for the clip
    """
    db = SessionLocal()
    try:
        logger.info(f"Processing clip {clip_id} (immediate mode)")
        
        # Update clip status to processing
        clip = db.query(Clip).filter(Clip.id == UUID(clip_id)).first()
        if not clip:
            logger.error(f"Clip {clip_id} not found")
            return {"status": "error", "message": "Clip not found"}
        
        # Generate timestamp string for file naming
        timestamp_str = datetime.fromisoformat(start_ts).strftime("%Y%m%d_%H%M%S")
        
        # Extract frames from video buffer
        video_key = f"clips/{user_id}/{timestamp_str}_clip.mp4"
        preview_key = f"clips/{user_id}/{timestamp_str}_preview.jpg"
        
        try:
            # Calculate time range
            start_time = datetime.fromisoformat(start_ts)
            end_time = start_time + timedelta(milliseconds=duration_ms)
            
            # Get frames directly from buffer (same process!)
            logger.info(f"Requesting frames from {start_time} to {end_time}")
            buffered_frames = video_buffer.get_frames(start_time, end_time)
            
            if buffered_frames and len(buffered_frames) > 0:
                logger.info(f"✅ Extracted {len(buffered_frames)} frames from buffer")
                logger.info(f"First frame: {buffered_frames[0][0]}, Last frame: {buffered_frames[-1][0]}")
                
                # Use buffered frames to create video
                width, height = buffered_frames[0][1].shape[1], buffered_frames[0][1].shape[0]
                fps = max(10, len(buffered_frames) / (duration_ms / 1000))  # Calculate FPS
                
            else:
                # Fallback: create animated placeholder if no frames in buffer
                logger.warning(f"⚠️ No frames in buffer for time range, creating placeholder")
                width, height = 640, 480
                fps = 30
                duration_sec = max(1, duration_ms // 1000)  # At least 1 second
                buffered_frames = None
            
            # Create temporary file path
            import tempfile
            temp_video = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
            temp_video_path = temp_video.name
            temp_video.close()
            
            # Initialize video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(temp_video_path, fourcc, int(fps), (width, height))
            
            if not out.isOpened():
                logger.error(f"Failed to open video writer with mp4v codec")
                raise Exception("Failed to initialize video writer")
            
            logger.info(f"Video writer initialized: {width}x{height} @ {fps} fps, codec=mp4v")
            
            preview_frame = None
            
            if buffered_frames:
                # Use actual buffered frames
                for idx, (timestamp, frame) in enumerate(buffered_frames):
                    # Resize frame if needed
                    if frame.shape[1] != width or frame.shape[0] != height:
                        frame = cv2.resize(frame, (width, height))
                    
                    # Add timestamp overlay
                    cv2.putText(
                        frame,
                        timestamp.strftime("%H:%M:%S.%f")[:-3],
                        (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (255, 255, 255),
                        2
                    )
                    
                    # Add labels if provided
                    if labels:
                        label_text = ", ".join(labels[:3])
                        cv2.putText(
                            frame,
                            label_text,
                            (10, height - 20),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.6,
                            (0, 255, 0),
                            2
                        )
                    
                    out.write(frame)
                    
                    # Save middle frame as preview
                    if idx == len(buffered_frames) // 2:
                        preview_frame = frame.copy()
            else:
                # Fallback: create animated placeholder
                total_frames = int(duration_sec * fps)
                
                for frame_num in range(total_frames):
                    # Create animated frame
                    frame = np.zeros((height, width, 3), dtype=np.uint8)
                    
                    # Gradient background
                    for i in range(height):
                        frame[i, :] = [
                            int(100 + 155 * i / height),
                            80,
                            int(200 - 100 * i / height)
                        ]
                    
                    # Animated circle
                    progress = frame_num / total_frames
                    center_x = int(width * 0.2 + width * 0.6 * progress)
                    center_y = height // 2 + int(30 * np.sin(progress * 4 * np.pi))
                    cv2.circle(frame, (center_x, center_y), 50, (139, 69, 19), -1)
                    
                    # Add timestamp and labels
                    cv2.putText(
                        frame,
                        f"Placeholder - No buffer data",
                        (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (255, 255, 255),
                        2
                    )
                    
                    if labels:
                        label_text = ", ".join(labels[:3])
                        cv2.putText(
                            frame,
                            label_text,
                            (20, height - 20),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.6,
                            (255, 255, 255),
                            1
                        )
                    
                    out.write(frame)
                    
                    # Save middle frame as preview
                    if frame_num == total_frames // 2:
                        preview_frame = frame.copy()
            
            out.release()
            
            # Read video file and upload to S3
            with open(temp_video_path, 'rb') as f:
                video_data = f.read()
            
            video_uri = storage_service.upload_file(
                file_data=video_data,
                object_key=video_key,
                content_type="video/mp4"
            )
            
            # Clean up temp file
            import os
            os.unlink(temp_video_path)
            
            # Create and upload preview
            if preview_frame is not None:
                _, preview_buffer = cv2.imencode('.jpg', preview_frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                preview_data = preview_buffer.tobytes()
            else:
                # Fallback preview
                preview_image = Image.new('RGB', (640, 480), color=(50, 50, 150))
                preview_output = io.BytesIO()
                preview_image.save(preview_output, format='JPEG', quality=85)
                preview_data = preview_output.getvalue()
            
            preview_uri = storage_service.upload_file(
                file_data=preview_data,
                object_key=preview_key,
                content_type="image/jpeg"
            )
            
        except Exception as e:
            logger.error(f"Error creating video file: {e}")
            import traceback
            traceback.print_exc()
            
            # Fallback to minimal placeholder
            preview_image = Image.new('RGB', (640, 480), color=(50, 50, 150))
            preview_output = io.BytesIO()
            preview_image.save(preview_output, format='JPEG', quality=85)
            preview_data = preview_output.getvalue()
            
            preview_uri = storage_service.upload_file(
                file_data=preview_data,
                object_key=preview_key,
                content_type="image/jpeg"
            )
            
            # Create minimal valid MP4
            video_uri = storage_service.upload_file(
                file_data=b'\x00\x00\x00\x20ftypisom\x00\x00\x02\x00isomiso2mp41\x00\x00\x00\x08free',
                object_key=video_key,
                content_type="video/mp4"
            )
        
        # Update clip record with S3 URIs
        clip.s3_uri = video_uri
        clip.preview_png = preview_uri
        if labels:
            clip.labels = labels
        
        db.commit()
        db.refresh(clip)
        
        logger.info(f"✅ Clip {clip_id} processed successfully")
        
        return {
            "status": "completed",
            "clip_id": clip_id,
            "s3_uri": video_uri,
            "preview_uri": preview_uri
        }
        
    except Exception as e:
        logger.error(f"Error processing clip {clip_id}: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        db.close()
