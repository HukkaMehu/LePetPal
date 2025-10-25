"""
Event processing pipeline for AI detections.

This worker processes AI detections into events, implements auto-bookmark logic
for significant motion, and auto-clip logic for fetch-return and treat-eaten sequences.

Requirements: 4.1, 4.2, 11.1, 11.2, 11.3
"""
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from collections import deque
from sqlalchemy.orm import Session
from uuid import uuid4

from app.db.base import SessionLocal
from app.models.event import Event
from app.core.events import broadcast_event, broadcast_clip_saved, broadcast_bookmark_created


class EventProcessor:
    """
    Background worker that processes AI detections into events.
    Implements auto-bookmark and auto-clip logic.
    """
    
    def __init__(self):
        self.event_buffer: List[Dict[str, Any]] = []
        self.motion_history = deque(maxlen=100)  # Track last 100 frames for motion detection
        self.action_sequence = deque(maxlen=30)  # Track last 30 actions for sequence detection
        self.last_flush_time = datetime.utcnow()
        self.flush_interval = 1.0  # Flush every 1 second
        self.running = False
        
    async def start(self):
        """Start the event processor."""
        self.running = True
        asyncio.create_task(self._process_loop())
        
    async def stop(self):
        """Stop the event processor."""
        self.running = False
        await self._flush_events()
        
    async def _process_loop(self):
        """Main processing loop that flushes events every second."""
        while self.running:
            await asyncio.sleep(self.flush_interval)
            await self._flush_events()
            
    async def process_detection(self, detection: Dict[str, Any], user_id: str, video_ts_ms: Optional[int] = None):
        """
        Process a single AI detection and generate events.
        
        Args:
            detection: Detection data from AI service
            user_id: User ID for the event
            video_ts_ms: Video timestamp in milliseconds
        """
        timestamp = datetime.utcnow()
        
        # Process dog detection
        if detection.get("detections"):
            for det in detection["detections"]:
                if det.get("class") == "dog" and det.get("confidence", 0) > 0.5:
                    self._add_event(
                        user_id=user_id,
                        event_type="dog_detected",
                        data=det,
                        timestamp=timestamp,
                        video_ts_ms=video_ts_ms
                    )
        
        # Process actions
        if detection.get("actions"):
            for action in detection["actions"]:
                action_label = action.get("label")
                probability = action.get("probability", 0)
                
                if probability > 0.6:  # Confidence threshold
                    self._add_event(
                        user_id=user_id,
                        event_type=action_label,
                        data={"confidence": probability, "action": action_label},
                        timestamp=timestamp,
                        video_ts_ms=video_ts_ms
                    )
                    
                    # Track action sequence for auto-clip detection
                    self.action_sequence.append({
                        "action": action_label,
                        "timestamp": timestamp,
                        "video_ts_ms": video_ts_ms
                    })
        
        # Process objects
        if detection.get("objects"):
            for obj in detection["objects"]:
                if obj.get("confidence", 0) > 0.5:
                    self._add_event(
                        user_id=user_id,
                        event_type=f"object_detected_{obj.get('class')}",
                        data=obj,
                        timestamp=timestamp,
                        video_ts_ms=video_ts_ms
                    )
        
        # Check for significant motion (auto-bookmark logic)
        await self._check_significant_motion(detection, user_id, timestamp, video_ts_ms)
        
        # Check for action sequences (auto-clip logic)
        await self._check_action_sequences(user_id)
        
    def _add_event(
        self,
        user_id: str,
        event_type: str,
        data: Dict[str, Any],
        timestamp: datetime,
        video_ts_ms: Optional[int] = None
    ):
        """Add an event to the buffer for batch insertion."""
        self.event_buffer.append({
            "user_id": user_id,
            "type": event_type,
            "data": data,
            "ts": timestamp,
            "video_ts_ms": video_ts_ms
        })
        
    async def _check_significant_motion(
        self,
        detection: Dict[str, Any],
        user_id: str,
        timestamp: datetime,
        video_ts_ms: Optional[int]
    ):
        """
        Check for significant motion and create auto-bookmarks.
        
        Significant motion is detected when:
        - Dog moves rapidly (large bounding box changes)
        - Multiple objects detected simultaneously
        - High-confidence action detected
        """
        # Track motion metrics
        motion_score = 0.0
        
        # Check for multiple detections
        num_detections = len(detection.get("detections", []))
        if num_detections > 0:
            motion_score += num_detections * 0.2
        
        # Check for high-confidence actions
        actions = detection.get("actions", [])
        if actions:
            max_confidence = max([a.get("probability", 0) for a in actions])
            motion_score += max_confidence
        
        # Check for object interactions
        num_objects = len(detection.get("objects", []))
        if num_objects > 0:
            motion_score += num_objects * 0.3
        
        self.motion_history.append(motion_score)
        
        # Create auto-bookmark if motion is significant
        if motion_score > 1.5 and len(self.motion_history) > 10:
            # Check if motion is sustained (not just a spike)
            recent_avg = sum(list(self.motion_history)[-10:]) / 10
            if recent_avg > 0.8:
                # Create bookmark
                bookmark_data = {
                    "label": "Significant activity detected",
                    "motion_score": motion_score,
                    "auto_generated": True
                }
                
                self._add_event(
                    user_id=user_id,
                    event_type="bookmark",
                    data=bookmark_data,
                    timestamp=timestamp,
                    video_ts_ms=video_ts_ms
                )
                
                # Broadcast bookmark immediately
                await broadcast_bookmark_created(bookmark_data)
                
                # Clear motion history to avoid duplicate bookmarks
                self.motion_history.clear()
    
    async def _check_action_sequences(self, user_id: str):
        """
        Check for action sequences that should trigger auto-clips.
        
        Sequences:
        - Fetch-return: approach -> fetch_return (within 10 seconds)
        - Treat-eaten: approach -> eating (within 5 seconds)
        """
        if len(self.action_sequence) < 2:
            return
        
        # Convert to list for easier processing
        actions = list(self.action_sequence)
        
        # Check for fetch-return sequence
        for i in range(len(actions) - 1):
            current = actions[i]
            next_action = actions[i + 1]
            
            time_diff = (next_action["timestamp"] - current["timestamp"]).total_seconds()
            
            # Fetch-return sequence
            if (current["action"] == "approach" and 
                next_action["action"] == "fetch_return" and 
                time_diff <= 10):
                
                await self._create_auto_clip(
                    user_id=user_id,
                    start_ts=current["timestamp"],
                    end_ts=next_action["timestamp"],
                    labels=["fetch", "auto_clip"],
                    start_video_ts_ms=current.get("video_ts_ms"),
                    end_video_ts_ms=next_action.get("video_ts_ms")
                )
                
                # Remove processed actions
                for _ in range(i + 2):
                    if self.action_sequence:
                        self.action_sequence.popleft()
                return
            
            # Treat-eaten sequence
            if (current["action"] == "approach" and 
                next_action["action"] == "eating" and 
                time_diff <= 5):
                
                await self._create_auto_clip(
                    user_id=user_id,
                    start_ts=current["timestamp"],
                    end_ts=next_action["timestamp"],
                    labels=["treat", "eating", "auto_clip"],
                    start_video_ts_ms=current.get("video_ts_ms"),
                    end_video_ts_ms=next_action.get("video_ts_ms")
                )
                
                # Remove processed actions
                for _ in range(i + 2):
                    if self.action_sequence:
                        self.action_sequence.popleft()
                return
    
    async def _create_auto_clip(
        self,
        user_id: str,
        start_ts: datetime,
        end_ts: datetime,
        labels: List[str],
        start_video_ts_ms: Optional[int] = None,
        end_video_ts_ms: Optional[int] = None
    ):
        """
        Create an auto-clip event.
        
        Note: This creates a clip_requested event. The actual clip creation
        is handled by the media management system (task 8).
        """
        duration_ms = int((end_ts - start_ts).total_seconds() * 1000)
        
        # Extend clip duration to 8-12 seconds as per requirements
        if duration_ms < 8000:
            # Add padding to reach 8 seconds
            padding_ms = (8000 - duration_ms) // 2
            start_ts = start_ts - timedelta(milliseconds=padding_ms)
            if start_video_ts_ms:
                start_video_ts_ms -= padding_ms
        elif duration_ms > 12000:
            # Trim to 12 seconds
            end_ts = start_ts + timedelta(milliseconds=12000)
            if start_video_ts_ms and end_video_ts_ms:
                end_video_ts_ms = start_video_ts_ms + 12000
        
        clip_data = {
            "start_ts": start_ts.isoformat(),
            "end_ts": end_ts.isoformat(),
            "duration_ms": int((end_ts - start_ts).total_seconds() * 1000),
            "labels": labels,
            "auto_generated": True,
            "start_video_ts_ms": start_video_ts_ms,
            "end_video_ts_ms": end_video_ts_ms
        }
        
        self._add_event(
            user_id=user_id,
            event_type="clip_requested",
            data=clip_data,
            timestamp=datetime.utcnow(),
            video_ts_ms=start_video_ts_ms
        )
        
        # Broadcast clip request
        await broadcast_event("clip_requested", clip_data)
    
    async def _flush_events(self):
        """Batch insert events to database."""
        if not self.event_buffer:
            return
        
        db = SessionLocal()
        try:
            # Create Event objects
            events = [
                Event(
                    id=uuid4(),
                    user_id=event_data["user_id"],
                    ts=event_data["ts"],
                    type=event_data["type"],
                    data=event_data["data"],
                    video_ts_ms=event_data.get("video_ts_ms")
                )
                for event_data in self.event_buffer
            ]
            
            # Batch insert
            db.bulk_save_objects(events)
            db.commit()
            
            # Clear buffer
            self.event_buffer.clear()
            self.last_flush_time = datetime.utcnow()
            
        except Exception as e:
            db.rollback()
            print(f"Error flushing events: {e}")
        finally:
            db.close()


# Global event processor instance
event_processor = EventProcessor()
