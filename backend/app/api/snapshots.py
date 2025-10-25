"""
Snapshots API endpoints for capturing and managing video snapshots.
Requirements: 6.1
"""
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from uuid import UUID, uuid4
import base64
import io
from PIL import Image

from app.db.base import get_db
from app.models.snapshot import Snapshot
from app.core.storage import storage_service
from app.core.events import broadcast_snapshot_saved

router = APIRouter(prefix="/api/snapshots", tags=["snapshots"])


class SnapshotCreateRequest(BaseModel):
    """Model for creating a snapshot."""
    timestamp: Optional[datetime] = None
    labels: Optional[List[str]] = None
    note: Optional[str] = None
    frame_data: Optional[str] = None  # Base64 encoded image data


class SnapshotResponse(BaseModel):
    """Model for snapshot response."""
    id: str
    user_id: str
    ts: datetime
    s3_uri: str
    preview_url: str
    labels: Optional[List[str]]
    note: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


@router.post("", response_model=SnapshotResponse, status_code=201)
async def create_snapshot(
    snapshot: SnapshotCreateRequest,
    db: Session = Depends(get_db)
):
    """
    Create a snapshot by capturing the current video frame.
    
    The frame data should be provided as base64-encoded image data.
    If no frame data is provided, a placeholder will be used.
    
    Requirements: 6.1
    """
    try:
        # Use provided timestamp or current time
        timestamp = snapshot.timestamp or datetime.utcnow()
        
        # For now, use a hardcoded user_id (in production, get from auth)
        # TODO: Replace with actual authenticated user_id
        user_id = uuid4()
        
        # Process frame data
        if snapshot.frame_data:
            # Decode base64 image
            try:
                # Remove data URL prefix if present
                if ',' in snapshot.frame_data:
                    snapshot.frame_data = snapshot.frame_data.split(',')[1]
                
                image_data = base64.b64decode(snapshot.frame_data)
                
                # Validate it's a valid image
                img = Image.open(io.BytesIO(image_data))
                
                # Convert to JPEG if needed
                if img.format != 'JPEG':
                    output = io.BytesIO()
                    img.convert('RGB').save(output, format='JPEG', quality=85)
                    image_data = output.getvalue()
                
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid image data: {str(e)}"
                )
        else:
            # Create a placeholder image
            img = Image.new('RGB', (640, 480), color=(100, 100, 100))
            output = io.BytesIO()
            img.save(output, format='JPEG', quality=85)
            image_data = output.getvalue()
        
        # Generate S3 object key
        timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S")
        object_key = f"snapshots/{user_id}/{timestamp_str}_{uuid4().hex[:8]}.jpg"
        
        # Upload to S3/MinIO
        s3_uri = storage_service.upload_file(
            file_data=image_data,
            object_key=object_key,
            content_type="image/jpeg"
        )
        
        # Create snapshot record in database
        db_snapshot = Snapshot(
            user_id=user_id,
            ts=timestamp,
            s3_uri=s3_uri,
            labels=snapshot.labels,
            note=snapshot.note
        )
        db.add(db_snapshot)
        db.commit()
        db.refresh(db_snapshot)
        
        # Generate preview URL
        preview_url = storage_service.get_presigned_url(object_key)
        
        # Broadcast snapshot saved event
        await broadcast_snapshot_saved({
            "id": str(db_snapshot.id),
            "timestamp": timestamp.isoformat(),
            "labels": snapshot.labels,
            "preview_url": preview_url
        })
        
        return SnapshotResponse(
            id=str(db_snapshot.id),
            user_id=str(db_snapshot.user_id),
            ts=db_snapshot.ts,
            s3_uri=db_snapshot.s3_uri,
            preview_url=preview_url or "",
            labels=db_snapshot.labels,
            note=db_snapshot.note,
            created_at=db_snapshot.created_at
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=Dict[str, Any])
async def get_snapshots(
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    Get all snapshots with pagination.
    """
    try:
        # Build query
        query = db.query(Snapshot)
        
        # Get total count
        total = query.count()
        
        # Apply pagination and ordering
        snapshots = query.order_by(Snapshot.ts.desc()).offset(offset).limit(limit).all()
        
        # Convert to response format with preview URLs
        snapshots_data = []
        for snapshot in snapshots:
            # Extract object key from S3 URI
            object_key = snapshot.s3_uri.replace(f"s3://{storage_service.bucket_name}/", "")
            preview_url = storage_service.get_presigned_url(object_key)
            
            snapshots_data.append(
                SnapshotResponse(
                    id=str(snapshot.id),
                    user_id=str(snapshot.user_id),
                    ts=snapshot.ts,
                    s3_uri=snapshot.s3_uri,
                    preview_url=preview_url or "",
                    labels=snapshot.labels,
                    note=snapshot.note,
                    created_at=snapshot.created_at
                )
            )
        
        return {
            "snapshots": snapshots_data,
            "total": total,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{snapshot_id}", response_model=SnapshotResponse)
async def get_snapshot(
    snapshot_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get a specific snapshot by ID.
    """
    try:
        snapshot = db.query(Snapshot).filter(Snapshot.id == snapshot_id).first()
        
        if not snapshot:
            raise HTTPException(status_code=404, detail="Snapshot not found")
        
        # Extract object key from S3 URI
        object_key = snapshot.s3_uri.replace(f"s3://{storage_service.bucket_name}/", "")
        preview_url = storage_service.get_presigned_url(object_key)
        
        return SnapshotResponse(
            id=str(snapshot.id),
            user_id=str(snapshot.user_id),
            ts=snapshot.ts,
            s3_uri=snapshot.s3_uri,
            preview_url=preview_url or "",
            labels=snapshot.labels,
            note=snapshot.note,
            created_at=snapshot.created_at
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{snapshot_id}")
async def delete_snapshot(
    snapshot_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Delete a snapshot.
    """
    try:
        snapshot = db.query(Snapshot).filter(Snapshot.id == snapshot_id).first()
        
        if not snapshot:
            raise HTTPException(status_code=404, detail="Snapshot not found")
        
        # Extract object key from S3 URI
        object_key = snapshot.s3_uri.replace(f"s3://{storage_service.bucket_name}/", "")
        
        # Delete from S3
        storage_service.delete_file(object_key)
        
        # Delete from database
        db.delete(snapshot)
        db.commit()
        
        return {"success": True, "message": "Snapshot deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
