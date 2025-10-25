"""
Clips API endpoints for creating and managing video clips.
Requirements: 4.2, 6.2
"""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from uuid import UUID, uuid4
import secrets

from app.db.base import get_db
from app.models.clip import Clip
from app.models.user import User
from app.core.storage import storage_service
from app.core.events import broadcast_clip_saved
from app.workers.clip_processor import process_clip_task, process_clip_sync

router = APIRouter(prefix="/api/clips", tags=["clips"])


class ClipCreateRequest(BaseModel):
    """Model for creating a clip."""
    start_ts: datetime
    duration_ms: int
    labels: Optional[List[str]] = None


class ClipResponse(BaseModel):
    """Model for clip response."""
    id: str
    user_id: str
    start_ts: datetime
    duration_ms: int
    s3_uri: Optional[str]
    video_url: Optional[str]  # Presigned URL for video download
    preview_url: Optional[str]
    labels: Optional[List[str]]
    share_token: Optional[str]
    share_url: Optional[str]
    status: str  # "pending", "processing", "completed", "error"
    created_at: datetime

    class Config:
        from_attributes = True


@router.post("", response_model=ClipResponse, status_code=202)
async def create_clip(
    clip_request: ClipCreateRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Create a video clip by queuing a background job.
    
    The clip will be processed asynchronously. Use GET /api/clips/{id}
    to check the status and retrieve the completed clip.
    
    Requirements: 4.2, 6.2
    """
    try:
        # For demo purposes, get or create a default demo user
        # In production, get from authenticated user session
        demo_user = db.query(User).filter(User.email == "demo@dogmonitor.com").first()
        
        if not demo_user:
            # Create demo user if it doesn't exist
            demo_user = User(
                id=UUID('00000000-0000-0000-0000-000000000000'),
                email="demo@dogmonitor.com",
                role="owner"
            )
            db.add(demo_user)
            db.flush()  # Flush to get the user in the session before creating clip
        
        user_id = demo_user.id
        
        # Validate duration
        if clip_request.duration_ms <= 0 or clip_request.duration_ms > 300000:  # Max 5 minutes
            raise HTTPException(
                status_code=400,
                detail="Duration must be between 1ms and 300000ms (5 minutes)"
            )
        
        # Create clip record with pending status
        db_clip = Clip(
            user_id=user_id,
            start_ts=clip_request.start_ts,
            duration_ms=clip_request.duration_ms,
            s3_uri="pending",  # Will be updated by worker
            labels=clip_request.labels
        )
        db.add(db_clip)
        db.commit()
        db.refresh(db_clip)
        
        # Process clip in background using FastAPI BackgroundTasks
        # This runs in the same process and has access to video buffer
        background_tasks.add_task(
            process_clip_sync,
            clip_id=str(db_clip.id),
            user_id=str(user_id),
            start_ts=clip_request.start_ts.isoformat(),
            duration_ms=clip_request.duration_ms,
            labels=clip_request.labels
        )
        
        return ClipResponse(
            id=str(db_clip.id),
            user_id=str(db_clip.user_id),
            start_ts=db_clip.start_ts,
            duration_ms=db_clip.duration_ms,
            s3_uri=None,
            video_url=None,
            preview_url=None,
            labels=db_clip.labels,
            share_token=db_clip.share_token,
            share_url=None,
            status="pending",
            created_at=db_clip.created_at
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{clip_id}", response_model=ClipResponse)
async def get_clip(
    clip_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get a specific clip by ID, including its processing status.
    
    Requirements: 4.2, 6.2
    """
    try:
        clip = db.query(Clip).filter(Clip.id == clip_id).first()
        
        if not clip:
            raise HTTPException(status_code=404, detail="Clip not found")
        
        # Determine status based on s3_uri
        if clip.s3_uri == "pending":
            status = "processing"
        elif clip.s3_uri and clip.s3_uri != "pending":
            status = "completed"
        else:
            status = "error"
        
        # Generate video URL if available
        video_url = None
        if clip.s3_uri and status == "completed":
            video_object_key = clip.s3_uri.replace(f"s3://{storage_service.bucket_name}/", "")
            video_url = storage_service.get_presigned_url(video_object_key)
        
        # Generate preview URL if available
        preview_url = None
        if clip.preview_png and status == "completed":
            object_key = clip.preview_png.replace(f"s3://{storage_service.bucket_name}/", "")
            preview_url = storage_service.get_presigned_url(object_key)
        
        # Generate share URL if share token exists
        share_url = None
        if clip.share_token:
            # In production, this would be your actual domain
            share_url = f"http://localhost:3000/share/clip/{clip.share_token}"
        
        return ClipResponse(
            id=str(clip.id),
            user_id=str(clip.user_id),
            start_ts=clip.start_ts,
            duration_ms=clip.duration_ms,
            s3_uri=clip.s3_uri if status == "completed" else None,
            video_url=video_url,
            preview_url=preview_url,
            labels=clip.labels,
            share_token=clip.share_token,
            share_url=share_url,
            status=status,
            created_at=clip.created_at
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=Dict[str, Any])
async def get_clips(
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    Get all clips with pagination.
    """
    try:
        # Build query
        query = db.query(Clip)
        
        # Get total count
        total = query.count()
        
        # Apply pagination and ordering
        clips = query.order_by(Clip.start_ts.desc()).offset(offset).limit(limit).all()
        
        # Convert to response format
        clips_data = []
        for clip in clips:
            # Determine status
            if clip.s3_uri == "pending":
                status = "processing"
            elif clip.s3_uri and clip.s3_uri != "pending":
                status = "completed"
            else:
                status = "error"
            
            # Generate video URL if available
            video_url = None
            if clip.s3_uri and status == "completed":
                video_object_key = clip.s3_uri.replace(f"s3://{storage_service.bucket_name}/", "")
                video_url = storage_service.get_presigned_url(video_object_key)
            
            # Generate preview URL if available
            preview_url = None
            if clip.preview_png and status == "completed":
                object_key = clip.preview_png.replace(f"s3://{storage_service.bucket_name}/", "")
                preview_url = storage_service.get_presigned_url(object_key)
            
            # Generate share URL if share token exists
            share_url = None
            if clip.share_token:
                share_url = f"http://localhost:3000/share/clip/{clip.share_token}"
            
            clips_data.append(
                ClipResponse(
                    id=str(clip.id),
                    user_id=str(clip.user_id),
                    start_ts=clip.start_ts,
                    duration_ms=clip.duration_ms,
                    s3_uri=clip.s3_uri if status == "completed" else None,
                    video_url=video_url,
                    preview_url=preview_url,
                    labels=clip.labels,
                    share_token=clip.share_token,
                    share_url=share_url,
                    status=status,
                    created_at=clip.created_at
                )
            )
        
        return {
            "clips": clips_data,
            "total": total,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{clip_id}/share")
async def create_share_link(
    clip_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Generate a share link for a clip.
    """
    try:
        clip = db.query(Clip).filter(Clip.id == clip_id).first()
        
        if not clip:
            raise HTTPException(status_code=404, detail="Clip not found")
        
        # Generate share token if it doesn't exist
        if not clip.share_token:
            clip.share_token = secrets.token_urlsafe(32)
            db.commit()
            db.refresh(clip)
        
        share_url = f"http://localhost:3000/share/clip/{clip.share_token}"
        
        return {
            "share_token": clip.share_token,
            "share_url": share_url
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{clip_id}")
async def delete_clip(
    clip_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Delete a clip.
    """
    try:
        clip = db.query(Clip).filter(Clip.id == clip_id).first()
        
        if not clip:
            raise HTTPException(status_code=404, detail="Clip not found")
        
        # Delete from S3 if exists
        if clip.s3_uri and clip.s3_uri != "pending":
            object_key = clip.s3_uri.replace(f"s3://{storage_service.bucket_name}/", "")
            storage_service.delete_file(object_key)
        
        # Delete preview from S3 if exists
        if clip.preview_png:
            preview_key = clip.preview_png.replace(f"s3://{storage_service.bucket_name}/", "")
            storage_service.delete_file(preview_key)
        
        # Delete from database
        db.delete(clip)
        db.commit()
        
        return {"success": True, "message": "Clip deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
