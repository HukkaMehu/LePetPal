"""
Events API endpoints for manual event creation and testing WebSocket broadcasting.
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_
from uuid import UUID
from app.core.events import (
    broadcast_event,
    broadcast_action,
    broadcast_dog_detection,
    broadcast_clip_saved,
    broadcast_snapshot_saved,
    broadcast_bookmark_created,
    broadcast_overlay_update,
    broadcast_telemetry
)
from app.db.base import get_db
from app.models.event import Event
from app.workers.event_processor import event_processor

router = APIRouter(prefix="/api/events", tags=["events"])


class EventCreate(BaseModel):
    """Model for creating a manual event."""
    event_type: str
    data: Dict[str, Any]


class ActionEvent(BaseModel):
    """Model for action events."""
    action: str
    confidence: float
    metadata: Optional[Dict[str, Any]] = None


class DetectionEvent(BaseModel):
    """Model for detection events."""
    detection: Dict[str, Any]


class OverlayUpdate(BaseModel):
    """Model for overlay updates."""
    overlay_type: str
    data: Any


class TelemetryUpdate(BaseModel):
    """Model for telemetry updates."""
    data: Dict[str, Any]


class EventCreateRequest(BaseModel):
    """Model for creating a new event."""
    type: str
    data: Optional[Dict[str, Any]] = None
    video_ts_ms: Optional[int] = None
    ts: Optional[datetime] = None


class EventResponse(BaseModel):
    """Model for event response."""
    id: str
    user_id: str
    ts: datetime
    type: str
    data: Optional[Dict[str, Any]]
    video_ts_ms: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


@router.post("/broadcast")
async def broadcast_custom_event(event: EventCreate):
    """
    Broadcast a custom event to all connected WebSocket clients.
    Useful for testing and manual event triggering.
    """
    try:
        await broadcast_event(event.event_type, event.data)
        return {
            "success": True,
            "message": f"Event '{event.event_type}' broadcasted successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/broadcast/action")
async def broadcast_action_event(action_event: ActionEvent):
    """
    Broadcast a dog action event (sit, stand, lie, fetch, etc.).
    """
    try:
        await broadcast_action(
            action_event.action,
            action_event.confidence,
            action_event.metadata
        )
        return {
            "success": True,
            "message": f"Action '{action_event.action}' broadcasted successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/broadcast/detection")
async def broadcast_detection_event(detection_event: DetectionEvent):
    """
    Broadcast a dog detection event.
    """
    try:
        await broadcast_dog_detection(detection_event.detection)
        return {
            "success": True,
            "message": "Detection broadcasted successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/broadcast/overlay")
async def broadcast_overlay(overlay: OverlayUpdate):
    """
    Broadcast overlay data to all connected clients.
    """
    try:
        await broadcast_overlay_update(overlay.overlay_type, overlay.data)
        return {
            "success": True,
            "message": f"Overlay '{overlay.overlay_type}' broadcasted successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/broadcast/telemetry")
async def broadcast_telemetry_data(telemetry: TelemetryUpdate):
    """
    Broadcast telemetry data to all connected clients.
    """
    try:
        await broadcast_telemetry(telemetry.data)
        return {
            "success": True,
            "message": "Telemetry broadcasted successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("", response_model=EventResponse, status_code=201)
async def create_event(
    event: EventCreateRequest,
    db: Session = Depends(get_db)
):
    """
    Create a manual event and store it in the database.
    Also broadcasts the event to all connected WebSocket clients.
    
    Requirements: 4.1, 11.1, 11.2
    """
    try:
        # Use provided timestamp or current time
        timestamp = event.ts or datetime.utcnow()
        
        # For now, use a hardcoded user_id (in production, get from auth)
        # TODO: Replace with actual authenticated user_id
        from uuid import uuid4
        user_id = uuid4()  # Placeholder
        
        # Create event in database
        db_event = Event(
            user_id=user_id,
            ts=timestamp,
            type=event.type,
            data=event.data,
            video_ts_ms=event.video_ts_ms
        )
        db.add(db_event)
        db.commit()
        db.refresh(db_event)
        
        # Broadcast event to WebSocket clients
        await broadcast_event(event.type, {
            "id": str(db_event.id),
            "timestamp": timestamp.isoformat(),
            "data": event.data,
            "video_ts_ms": event.video_ts_ms
        })
        
        return EventResponse(
            id=str(db_event.id),
            user_id=str(db_event.user_id),
            ts=db_event.ts,
            type=db_event.type,
            data=db_event.data,
            video_ts_ms=db_event.video_ts_ms,
            created_at=db_event.created_at
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=Dict[str, Any])
async def get_events(
    from_ts: Optional[datetime] = Query(None, description="Filter events from this timestamp"),
    to_ts: Optional[datetime] = Query(None, description="Filter events to this timestamp"),
    type: Optional[str] = Query(None, description="Filter by event type"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of events to return"),
    offset: int = Query(0, ge=0, description="Number of events to skip"),
    db: Session = Depends(get_db)
):
    """
    Get events with optional filtering by date range and type.
    
    Requirements: 4.1, 11.1, 11.2
    """
    try:
        # Build query
        query = db.query(Event)
        
        # Apply filters
        filters = []
        if from_ts:
            filters.append(Event.ts >= from_ts)
        if to_ts:
            filters.append(Event.ts <= to_ts)
        if type:
            filters.append(Event.type == type)
        
        if filters:
            query = query.filter(and_(*filters))
        
        # Get total count
        total = query.count()
        
        # Apply pagination and ordering
        events = query.order_by(Event.ts.desc()).offset(offset).limit(limit).all()
        
        # Convert to response format
        events_data = [
            EventResponse(
                id=str(event.id),
                user_id=str(event.user_id),
                ts=event.ts,
                type=event.type,
                data=event.data,
                video_ts_ms=event.video_ts_ms,
                created_at=event.created_at
            )
            for event in events
        ]
        
        return {
            "events": events_data,
            "total": total,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/process-detection")
async def process_ai_detection(detection: Dict[str, Any]):
    """
    Process AI detection data through the event processing pipeline.
    This endpoint receives detections from the AI service and generates events.
    
    Requirements: 4.1, 4.2, 11.1, 11.2, 11.3
    """
    try:
        # TODO: Get actual user_id from authentication
        from uuid import uuid4
        user_id = str(uuid4())  # Placeholder
        
        # Get video timestamp if provided
        video_ts_ms = detection.get("timestamp")
        
        # Process detection through event processor
        await event_processor.process_detection(detection, user_id, video_ts_ms)
        
        return {
            "success": True,
            "message": "Detection processed successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
