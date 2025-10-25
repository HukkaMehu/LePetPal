"""
Event broadcasting utilities for sending real-time updates to WebSocket clients.
"""
from typing import Any, Dict
from app.core.websocket import manager
from datetime import datetime


async def broadcast_event(event_type: str, data: Dict[str, Any]):
    """
    Broadcast an event to all connected WebSocket clients.
    
    Args:
        event_type: Type of event (e.g., 'dog_detected', 'sit', 'bark', 'clip_saved')
        data: Event data dictionary
    """
    await manager.broadcast_event(event_type, data)


async def broadcast_overlay_update(overlay_type: str, data: Any):
    """
    Broadcast overlay data to all connected WebSocket clients.
    
    Args:
        overlay_type: Type of overlay ('detection', 'pose', 'heatmap', 'zone', 'annotation')
        data: Overlay data (bounding boxes, keypoints, heatmap data, etc.)
    """
    await manager.broadcast_overlay(overlay_type, data)


async def broadcast_telemetry(telemetry_data: Dict[str, Any]):
    """
    Broadcast telemetry data to all connected WebSocket clients.
    
    Args:
        telemetry_data: Dictionary containing telemetry information
            (fps, latency, temperature, battery, etc.)
    """
    await manager.broadcast_telemetry(telemetry_data)


async def broadcast_dog_detection(detection: Dict[str, Any]):
    """
    Broadcast dog detection event.
    
    Args:
        detection: Detection data with bounding box, confidence, etc.
    """
    await broadcast_event("dog_detected", {
        "timestamp": datetime.utcnow().isoformat(),
        "detection": detection
    })


async def broadcast_action(action: str, confidence: float, metadata: Dict[str, Any] = None):
    """
    Broadcast dog action event (sit, stand, lie, fetch, etc.).
    
    Args:
        action: Action type ('sit', 'stand', 'lie', 'fetch_return', etc.)
        confidence: Confidence score (0-1)
        metadata: Additional metadata about the action
    """
    await broadcast_event(action, {
        "timestamp": datetime.utcnow().isoformat(),
        "confidence": confidence,
        "metadata": metadata or {}
    })


async def broadcast_clip_saved(clip_id: str, clip_data: Dict[str, Any]):
    """
    Broadcast clip saved event.
    
    Args:
        clip_id: ID of the saved clip
        clip_data: Clip metadata (start_time, duration, labels, etc.)
    """
    await broadcast_event("clip_saved", {
        "timestamp": datetime.utcnow().isoformat(),
        "clip_id": clip_id,
        "clip_data": clip_data
    })


async def broadcast_snapshot_saved(snapshot_id: str, snapshot_data: Dict[str, Any]):
    """
    Broadcast snapshot saved event.
    
    Args:
        snapshot_id: ID of the saved snapshot
        snapshot_data: Snapshot metadata (timestamp, labels, preview_url, etc.)
    """
    await broadcast_event("snapshot_saved", {
        "timestamp": datetime.utcnow().isoformat(),
        "snapshot_id": snapshot_id,
        "snapshot_data": snapshot_data
    })


async def broadcast_bookmark_created(bookmark_data: Dict[str, Any]):
    """
    Broadcast bookmark created event.
    
    Args:
        bookmark_data: Bookmark metadata (timestamp, label, etc.)
    """
    await broadcast_event("bookmark", {
        "timestamp": datetime.utcnow().isoformat(),
        "bookmark_data": bookmark_data
    })
