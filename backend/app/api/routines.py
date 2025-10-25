"""
Routines API endpoints for creating, listing, updating, and deleting training routines.
Requirements: 8.2, 8.3
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from uuid import UUID, uuid4
from croniter import croniter

from app.db.base import get_db
from app.models.routine import Routine
from app.workers.routine_scheduler import routine_scheduler

router = APIRouter(prefix="/api/routines", tags=["routines"])

# Default user ID for single-user setup
DEFAULT_USER_ID = UUID("e6bca6a4-5e3b-4877-837b-750a55f1e527")


class RoutineStep(BaseModel):
    """Model for a single routine step."""
    type: str = Field(..., description="Step type: pet, treat, play, sit_drill, fetch, wait")
    duration: Optional[int] = Field(None, description="Duration in seconds")
    params: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional parameters")

    @validator('type')
    def validate_step_type(cls, v):
        valid_types = ['pet', 'treat', 'play', 'sit_drill', 'fetch', 'wait']
        if v not in valid_types:
            raise ValueError(f"Step type must be one of: {', '.join(valid_types)}")
        return v


class RoutineCreate(BaseModel):
    """Model for creating a new routine."""
    name: str = Field(..., min_length=1, max_length=255, description="Routine name")
    cron: str = Field(..., description="Cron expression for scheduling")
    steps: List[RoutineStep] = Field(..., min_items=1, description="List of routine steps")
    enabled: bool = Field(default=True, description="Whether routine is enabled")

    @validator('cron')
    def validate_cron(cls, v):
        """Validate cron expression format."""
        try:
            croniter(v)
        except Exception as e:
            raise ValueError(f"Invalid cron expression: {str(e)}")
        return v


class RoutineUpdate(BaseModel):
    """Model for updating an existing routine."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    cron: Optional[str] = None
    steps: Optional[List[RoutineStep]] = None
    enabled: Optional[bool] = None

    @validator('cron')
    def validate_cron(cls, v):
        """Validate cron expression format."""
        if v is not None:
            try:
                croniter(v)
            except Exception as e:
                raise ValueError(f"Invalid cron expression: {str(e)}")
        return v


class RoutineResponse(BaseModel):
    """Model for routine response."""
    id: str
    user_id: str
    name: str
    cron: str
    steps: List[Dict[str, Any]]
    enabled: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


@router.get("", response_model=List[RoutineResponse])
async def list_routines(
    enabled: Optional[bool] = Query(None, description="Filter by enabled status"),
    db: Session = Depends(get_db)
):
    """
    List all routines with optional filtering.
    
    Requirements: 8.2, 8.3
    """
    try:
        # TODO: Replace with actual authenticated user_id
        # For now, get all routines (in production, filter by user_id)
        query = db.query(Routine)
        
        if enabled is not None:
            query = query.filter(Routine.enabled == enabled)
        
        routines = query.order_by(Routine.created_at.desc()).all()
        
        return [
            RoutineResponse(
                id=str(routine.id),
                user_id=str(routine.user_id),
                name=routine.name,
                cron=routine.cron,
                steps=routine.steps,
                enabled=routine.enabled,
                created_at=routine.created_at,
                updated_at=routine.updated_at
            )
            for routine in routines
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("", response_model=RoutineResponse, status_code=201)
async def create_routine(
    routine: RoutineCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new routine.
    
    Requirements: 8.2, 8.3
    """
    try:
        # Use default user ID for single-user setup
        user_id = DEFAULT_USER_ID
        
        # Convert steps to dict format for JSONB storage
        steps_data = [step.dict() for step in routine.steps]
        
        # Create routine in database
        db_routine = Routine(
            user_id=user_id,
            name=routine.name,
            cron=routine.cron,
            steps=steps_data,
            enabled=routine.enabled
        )
        db.add(db_routine)
        db.commit()
        db.refresh(db_routine)
        
        return RoutineResponse(
            id=str(db_routine.id),
            user_id=str(db_routine.user_id),
            name=db_routine.name,
            cron=db_routine.cron,
            steps=db_routine.steps,
            enabled=db_routine.enabled,
            created_at=db_routine.created_at,
            updated_at=db_routine.updated_at
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{routine_id}", response_model=RoutineResponse)
async def get_routine(
    routine_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get a specific routine by ID.
    
    Requirements: 8.2, 8.3
    """
    try:
        routine = db.query(Routine).filter(Routine.id == routine_id).first()
        
        if not routine:
            raise HTTPException(status_code=404, detail="Routine not found")
        
        return RoutineResponse(
            id=str(routine.id),
            user_id=str(routine.user_id),
            name=routine.name,
            cron=routine.cron,
            steps=routine.steps,
            enabled=routine.enabled,
            created_at=routine.created_at,
            updated_at=routine.updated_at
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{routine_id}", response_model=RoutineResponse)
async def update_routine(
    routine_id: UUID,
    routine_update: RoutineUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing routine.
    
    Requirements: 8.2, 8.3
    """
    try:
        db_routine = db.query(Routine).filter(Routine.id == routine_id).first()
        
        if not db_routine:
            raise HTTPException(status_code=404, detail="Routine not found")
        
        # Update fields if provided
        if routine_update.name is not None:
            db_routine.name = routine_update.name
        if routine_update.cron is not None:
            db_routine.cron = routine_update.cron
        if routine_update.steps is not None:
            db_routine.steps = [step.dict() for step in routine_update.steps]
        if routine_update.enabled is not None:
            db_routine.enabled = routine_update.enabled
        
        # Update timestamp
        db_routine.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(db_routine)
        
        return RoutineResponse(
            id=str(db_routine.id),
            user_id=str(db_routine.user_id),
            name=db_routine.name,
            cron=db_routine.cron,
            steps=db_routine.steps,
            enabled=db_routine.enabled,
            created_at=db_routine.created_at,
            updated_at=db_routine.updated_at
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{routine_id}")
async def delete_routine(
    routine_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Delete a routine.
    
    Requirements: 8.2, 8.3
    """
    try:
        db_routine = db.query(Routine).filter(Routine.id == routine_id).first()
        
        if not db_routine:
            raise HTTPException(status_code=404, detail="Routine not found")
        
        db.delete(db_routine)
        db.commit()
        
        return {"success": True, "message": "Routine deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/schedule", response_model=List[Dict[str, Any]])
async def get_routine_schedule(
    limit: int = Query(5, ge=1, le=20, description="Number of upcoming runs per routine")
):
    """
    Get next scheduled run times for all enabled routines.
    
    Requirements: 8.4
    """
    try:
        schedule = await routine_scheduler.get_next_run_times(limit)
        return schedule
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{routine_id}/trigger")
async def trigger_routine(routine_id: UUID):
    """
    Manually trigger a routine immediately (for testing or immediate execution).
    
    Requirements: 8.4
    """
    try:
        await routine_scheduler.trigger_routine_manually(routine_id)
        return {
            "success": True,
            "message": f"Routine {routine_id} triggered successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
