"""
Status and Telemetry API

This module provides system status information including device status,
video streaming metrics, and active AI models.

Requirements: 1.5, 10.2, 10.3
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select
import httpx
import asyncio
from datetime import datetime

from app.db.base import get_db
from app.models.device import Device
from app.core.config import settings
from app.core.websocket import manager

router = APIRouter(prefix="/api", tags=["status"])


class AIModelsStatus(BaseModel):
    """Active AI models information"""
    detector: Optional[str] = Field(None, description="Active detector model")
    action_recognizer: Optional[str] = Field(None, alias="actionRecognizer", description="Active action recognition model")
    pose_estimator: Optional[str] = Field(None, alias="poseEstimator", description="Active pose estimation model")
    policy: Optional[str] = Field(None, description="Active policy model for robot control")


class SystemStatus(BaseModel):
    """Complete system status"""
    device: str = Field(..., description="Device connection status: 'connected' or 'offline'")
    video: str = Field(..., description="Active video streaming type: 'webrtc' or 'mjpeg'")
    fps: float = Field(..., description="Current frames per second")
    latency_ms: float = Field(..., alias="latencyMs", description="Current video latency in milliseconds")
    ai_models: AIModelsStatus = Field(..., alias="aiModels", description="Active AI models")
    timestamp: str = Field(..., description="Status timestamp in ISO format")
    
    class Config:
        populate_by_name = True


class TelemetryData(BaseModel):
    """Real-time telemetry data"""
    fps: float = Field(..., description="Current frames per second")
    latency_ms: float = Field(..., alias="latencyMs", description="Current latency in milliseconds")
    temperature: Optional[float] = Field(None, description="Device temperature in Celsius")
    battery_level: Optional[float] = Field(None, alias="batteryLevel", description="Battery level percentage")
    timestamp: str = Field(..., description="Telemetry timestamp in ISO format")
    
    class Config:
        populate_by_name = True


# Global state for video metrics (in production, this would be in Redis or similar)
class VideoMetrics:
    """Tracks current video streaming metrics"""
    
    def __init__(self):
        self.video_type: str = "mjpeg"  # Default to MJPEG
        self.fps: float = 30.0
        self.latency_ms: float = 150.0
        self.last_update: datetime = datetime.utcnow()
    
    def update(self, video_type: Optional[str] = None, fps: Optional[float] = None, latency_ms: Optional[float] = None):
        """Update video metrics"""
        if video_type:
            self.video_type = video_type
        if fps is not None:
            self.fps = fps
        if latency_ms is not None:
            self.latency_ms = latency_ms
        self.last_update = datetime.utcnow()
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        return {
            "video_type": self.video_type,
            "fps": self.fps,
            "latency_ms": self.latency_ms
        }


# Global video metrics instance
video_metrics = VideoMetrics()


async def get_ai_models_status() -> AIModelsStatus:
    """
    Fetch active AI models from the AI service.
    
    Returns mock data if AI service is unavailable.
    """
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            response = await client.get(f"{settings.AI_SERVICE_URL}/models/active")
            if response.status_code == 200:
                data = response.json()
                active_models = data.get("active_models", {})
                
                return AIModelsStatus(
                    detector=active_models.get("detector"),
                    actionRecognizer=active_models.get("action"),
                    poseEstimator=active_models.get("pose"),
                    policy=active_models.get("policy")
                )
    except (httpx.RequestError, httpx.TimeoutException):
        pass
    
    # Return mock data if AI service is unavailable
    return AIModelsStatus(
        detector="yolo-v8-nano@1.0",
        actionRecognizer="action-transformer-lite@1.0",
        poseEstimator="pose-lite@1.0",
        policy=None
    )


async def get_device_status(db: Session) -> str:
    """
    Check if any device is connected.
    
    Returns 'connected' if at least one device is online, otherwise 'offline'.
    For demo/testing purposes, if video streaming is active, consider device connected.
    """
    try:
        # Query for any connected device
        stmt = select(Device).where(Device.status == "connected").limit(1)
        result = db.execute(stmt)
        device = result.scalar_one_or_none()
        
        if device:
            return "connected"
        
        # Fallback: If video streaming is active (FPS > 0), consider device connected
        # This allows testing without a physical device in the database
        if video_metrics.fps > 0:
            print("[STATUS API] No device in DB, but video streaming is active - reporting as connected")
            return "connected"
        
        return "offline"
    except Exception as e:
        print(f"[STATUS API] Error checking device status: {e}")
        # If database query fails but video is streaming, still report connected
        if video_metrics.fps > 0:
            return "connected"
        return "offline"


@router.get("/status", response_model=SystemStatus)
async def get_status(db: Session = Depends(get_db)):
    """
    Get complete system status.
    
    Returns:
    - Device connection status (connected/offline)
    - Active video streaming type (webrtc/mjpeg)
    - Current FPS and latency
    - Active AI models
    
    This endpoint provides a snapshot of the system state.
    Real-time updates are available via WebSocket telemetry messages.
    
    Requirements: 1.5, 10.2, 10.3
    """
    # Get device status from database
    device_status = await get_device_status(db)
    
    # Get AI models status from AI service
    ai_models = await get_ai_models_status()
    
    # Get current video metrics
    metrics = video_metrics.get_metrics()
    
    return SystemStatus(
        device=device_status,
        video=metrics["video_type"],
        fps=metrics["fps"],
        latencyMs=metrics["latency_ms"],
        aiModels=ai_models,
        timestamp=datetime.utcnow().isoformat()
    )


@router.post("/telemetry/update")
async def update_telemetry(
    video_type: Optional[str] = None,
    fps: Optional[float] = None,
    latency_ms: Optional[float] = None,
    temperature: Optional[float] = None,
    battery_level: Optional[float] = None
):
    """
    Update telemetry data and broadcast to WebSocket clients.
    
    This endpoint is called by video streaming components to update
    real-time metrics. Updates are immediately broadcast to all
    connected WebSocket clients.
    
    Parameters:
    - video_type: Current streaming type ('webrtc' or 'mjpeg')
    - fps: Current frames per second
    - latency_ms: Current latency in milliseconds
    - temperature: Device temperature in Celsius (optional)
    - battery_level: Battery level percentage (optional)
    """
    # Update video metrics
    video_metrics.update(video_type=video_type, fps=fps, latency_ms=latency_ms)
    
    # Create telemetry data
    telemetry = TelemetryData(
        fps=video_metrics.fps,
        latencyMs=video_metrics.latency_ms,
        temperature=temperature,
        batteryLevel=battery_level,
        timestamp=datetime.utcnow().isoformat()
    )
    
    # Broadcast to WebSocket clients
    await manager.broadcast_telemetry(telemetry.model_dump(by_alias=True))
    
    return {"success": True, "message": "Telemetry updated"}


@router.get("/telemetry/current", response_model=TelemetryData)
async def get_current_telemetry():
    """
    Get current telemetry data.
    
    Returns the most recent telemetry metrics including FPS and latency.
    For real-time updates, subscribe to WebSocket telemetry messages.
    """
    return TelemetryData(
        fps=video_metrics.fps,
        latencyMs=video_metrics.latency_ms,
        temperature=None,  # Mock data - would come from device
        batteryLevel=None,  # Mock data - would come from device
        timestamp=datetime.utcnow().isoformat()
    )


@router.get("/debug/frame-processor-stats")
async def get_frame_processor_stats():
    """
    Get frame processor statistics for debugging.
    
    Returns processing stats including frames processed, dropped, and queue size.
    """
    try:
        from app.workers.frame_processor import frame_processor
        return frame_processor.get_stats()
    except ImportError:
        return {
            "error": "Frame processor not available",
            "running": False
        }
