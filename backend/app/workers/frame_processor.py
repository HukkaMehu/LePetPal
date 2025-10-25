"""
Frame Processor Worker

Continuously processes video frames through AI service for real-time detection.
This worker runs in the background and processes frames asynchronously.
"""
import asyncio
import base64
import httpx
from datetime import datetime
from typing import Optional
from app.core.config import settings
from app.core.websocket import manager


class FrameProcessor:
    """
    Processes video frames through AI service and broadcasts results.
    
    Features:
    - Non-blocking frame submission
    - Automatic frame dropping if AI is slow
    - WebSocket broadcasting of AI results
    - Event creation from AI suggestions
    """
    
    def __init__(self):
        self.running = False
        self.task: Optional[asyncio.Task] = None
        self.frame_queue: asyncio.Queue = asyncio.Queue(maxsize=5)
        self.ai_client: Optional[httpx.AsyncClient] = None
        self.frames_processed = 0
        self.frames_dropped = 0
        
    async def start(self):
        """Start frame processing worker"""
        if self.running:
            return
            
        print("[FrameProcessor] Starting...")
        self.running = True
        self.ai_client = httpx.AsyncClient(
            base_url=settings.AI_SERVICE_URL,
            timeout=5.0
        )
        self.task = asyncio.create_task(self._process_loop())
        print("[FrameProcessor] Started")
        
    async def stop(self):
        """Stop frame processing worker"""
        if not self.running:
            return
            
        print("[FrameProcessor] Stopping...")
        self.running = False
        
        if self.task:
            await self.task
            
        if self.ai_client:
            await self.ai_client.aclose()
            
        print(f"[FrameProcessor] Stopped. Stats: {self.frames_processed} processed, {self.frames_dropped} dropped")
    
    async def submit_frame(self, frame_bytes: bytes, timestamp: float):
        """
        Submit frame for AI processing (non-blocking).
        
        Args:
            frame_bytes: JPEG encoded frame bytes
            timestamp: Frame timestamp in milliseconds
        """
        try:
            self.frame_queue.put_nowait((frame_bytes, timestamp))
        except asyncio.QueueFull:
            # Drop frame if queue is full (AI processing slower than video)
            self.frames_dropped += 1
    
    async def _process_loop(self):
        """Main processing loop - runs continuously"""
        while self.running:
            try:
                # Get frame from queue with timeout
                frame_bytes, timestamp = await asyncio.wait_for(
                    self.frame_queue.get(),
                    timeout=1.0
                )
                
                # Process frame through AI
                await self._process_frame(frame_bytes, timestamp)
                self.frames_processed += 1
                
            except asyncio.TimeoutError:
                # No frames in queue, continue waiting
                continue
            except Exception as e:
                print(f"[FrameProcessor] Error in process loop: {e}")
                await asyncio.sleep(1.0)
    
    async def _process_frame(self, frame_bytes: bytes, timestamp: float):
        """
        Process single frame through AI service.
        
        Args:
            frame_bytes: JPEG encoded frame bytes
            timestamp: Frame timestamp in milliseconds
        """
        try:
            # Encode frame to base64
            frame_base64 = base64.b64encode(frame_bytes).decode('utf-8')
            
            # Call AI service vision processing
            response = await self.ai_client.post(
                "/vision/process",
                json={
                    "frameBase64": frame_base64,
                    "timestamp": timestamp,
                    "enabledModels": ["detector", "pose", "action", "object"]
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Broadcast AI results via WebSocket for real-time overlays
                await manager.broadcast_message({
                    "type": "ai_detections",
                    "timestamp": timestamp,
                    "data": {
                        "detections": result.get("detections", []),
                        "keypoints": result.get("keypoints", []),
                        "actions": result.get("actions", []),
                        "objects": result.get("objects", [])
                    }
                })
                
                # Process suggested events from AI
                suggested_events = result.get("suggestedEvents", [])
                for event in suggested_events:
                    await self._create_event_from_suggestion(event, timestamp)
                    
            else:
                print(f"[FrameProcessor] AI service error: {response.status_code}")
                
        except httpx.TimeoutException:
            print("[FrameProcessor] AI service timeout")
        except Exception as e:
            print(f"[FrameProcessor] Error processing frame: {e}")
    
    async def _create_event_from_suggestion(self, suggestion: dict, timestamp: float):
        """
        Create event from AI suggestion.
        
        Args:
            suggestion: AI suggested event with type, confidence, data
            timestamp: Event timestamp in milliseconds
        """
        try:
            # Import here to avoid circular dependency
            from app.workers.event_processor import event_processor
            
            event_type = suggestion.get("type")
            confidence = suggestion.get("confidence", 0.0)
            
            # Only create events for high-confidence suggestions
            if confidence > 0.7:
                await event_processor.submit_event({
                    "type": event_type,
                    "timestamp": datetime.utcnow().isoformat(),
                    "data": {
                        **suggestion.get("data", {}),
                        "confidence": confidence,
                        "source": "ai_detection"
                    }
                })
                
        except Exception as e:
            print(f"[FrameProcessor] Error creating event: {e}")
    
    def get_stats(self) -> dict:
        """Get processing statistics"""
        return {
            "running": self.running,
            "frames_processed": self.frames_processed,
            "frames_dropped": self.frames_dropped,
            "queue_size": self.frame_queue.qsize()
        }


# Global instance
frame_processor = FrameProcessor()
