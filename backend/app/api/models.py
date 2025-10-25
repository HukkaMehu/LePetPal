"""
Models API endpoints.

Provides endpoints for listing available AI models and switching active models at runtime.

Requirements: 12.1, 12.2, 12.5
"""
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from uuid import UUID
import httpx

from app.db.base import get_db
from app.models.model import Model
from app.core.config import settings


router = APIRouter(prefix="/api/models", tags=["models"])


# Pydantic models for request/response
class ModelInfo(BaseModel):
    """Information about an AI model"""
    id: UUID
    name: str
    type: str  # 'detector', 'action', 'pose', 'policy'
    version: str
    status: str  # 'available', 'active', 'loading', 'error'
    artifact_uri: str
    metadata: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True


class ActiveModels(BaseModel):
    """Currently active models"""
    detector: Optional[str] = None
    action_recognizer: Optional[str] = None
    pose_estimator: Optional[str] = None
    policy: Optional[str] = None


class ModelsListResponse(BaseModel):
    """Response for listing models"""
    available: List[ModelInfo]
    active: ActiveModels


class ModelSwitchRequest(BaseModel):
    """Request to switch models"""
    detector: Optional[str] = Field(None, description="Detector model name")
    action_recognizer: Optional[str] = Field(None, description="Action recognizer model name")
    pose_estimator: Optional[str] = Field(None, description="Pose estimator model name")
    policy: Optional[str] = Field(None, description="Policy model name")


class ModelSwitchResponse(BaseModel):
    """Response after switching models"""
    success: bool
    message: str
    active: ActiveModels
    errors: Optional[List[str]] = None


@router.get("", response_model=ModelsListResponse)
async def list_models(
    db: Session = Depends(get_db)
):
    """
    List all available AI models and currently active models.
    
    Returns:
    - available: List of all models in the database
    - active: Currently active model for each type
    """
    # Get all available models
    models = db.query(Model).order_by(Model.type, Model.name, Model.version).all()
    
    # Get active models (those with status='active')
    active_models = db.query(Model).filter(Model.status == "active").all()
    
    # Build active models dict
    active = ActiveModels()
    for model in active_models:
        if model.type == "detector":
            active.detector = f"{model.name}@{model.version}"
        elif model.type == "action":
            active.action_recognizer = f"{model.name}@{model.version}"
        elif model.type == "pose":
            active.pose_estimator = f"{model.name}@{model.version}"
        elif model.type == "policy":
            active.policy = f"{model.name}@{model.version}"
    
    return ModelsListResponse(
        available=[ModelInfo.model_validate(m) for m in models],
        active=active
    )


@router.post("/switch", response_model=ModelSwitchResponse)
async def switch_models(
    request: ModelSwitchRequest = Body(...),
    db: Session = Depends(get_db)
):
    """
    Switch active AI models at runtime.
    
    This endpoint:
    1. Validates that requested models exist and are available
    2. Calls the AI service to perform hot-swap
    3. Updates model status in database
    4. Returns new active model configuration
    
    The AI service maintains detection continuity during the switch.
    """
    errors = []
    models_to_switch = {}
    
    # Validate and prepare models to switch
    for model_type, model_name in [
        ("detector", request.detector),
        ("action", request.action_recognizer),
        ("pose", request.pose_estimator),
        ("policy", request.policy)
    ]:
        if model_name:
            # Parse name@version format
            if "@" in model_name:
                name, version = model_name.split("@", 1)
            else:
                name = model_name
                version = None
            
            # Find model in database
            query = db.query(Model).filter(
                and_(
                    Model.name == name,
                    Model.type == model_type
                )
            )
            
            if version:
                query = query.filter(Model.version == version)
            else:
                # Get latest version if not specified
                query = query.order_by(Model.version.desc())
            
            model = query.first()
            
            if not model:
                errors.append(f"Model not found: {model_name} (type: {model_type})")
                continue
            
            if model.status == "error":
                errors.append(f"Model in error state: {model_name}")
                continue
            
            models_to_switch[model_type] = model
    
    # If validation errors, return early
    if errors:
        return ModelSwitchResponse(
            success=False,
            message="Model validation failed",
            active=ActiveModels(),
            errors=errors
        )
    
    # Call AI service to perform hot-swap
    ai_service_url = getattr(settings, "AI_SERVICE_URL", "http://localhost:8001")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Prepare request payload for AI service
            switch_payload = {}
            for model_type, model in models_to_switch.items():
                switch_payload[model_type] = {
                    "name": model.name,
                    "version": model.version,
                    "artifact_uri": model.artifact_uri,
                    "metadata": model.model_metadata
                }
            
            # Call AI service switch endpoint
            response = await client.post(
                f"{ai_service_url}/models/switch",
                json=switch_payload,
                timeout=30.0
            )
            
            if response.status_code != 200:
                error_detail = response.json().get("detail", "Unknown error")
                return ModelSwitchResponse(
                    success=False,
                    message=f"AI service error: {error_detail}",
                    active=ActiveModels(),
                    errors=[error_detail]
                )
            
            ai_response = response.json()
            
            # If AI service switch was successful, update database
            if ai_response.get("success"):
                # Deactivate all models of the types being switched
                for model_type in models_to_switch.keys():
                    db.query(Model).filter(
                        and_(
                            Model.type == model_type,
                            Model.status == "active"
                        )
                    ).update({"status": "available"})
                
                # Activate new models
                for model_type, model in models_to_switch.items():
                    model.status = "active"
                    db.add(model)
                
                db.commit()
                
                # Get updated active models
                active_models = db.query(Model).filter(Model.status == "active").all()
                active = ActiveModels()
                for model in active_models:
                    if model.type == "detector":
                        active.detector = f"{model.name}@{model.version}"
                    elif model.type == "action":
                        active.action_recognizer = f"{model.name}@{model.version}"
                    elif model.type == "pose":
                        active.pose_estimator = f"{model.name}@{model.version}"
                    elif model.type == "policy":
                        active.policy = f"{model.name}@{model.version}"
                
                return ModelSwitchResponse(
                    success=True,
                    message="Models switched successfully",
                    active=active
                )
            else:
                return ModelSwitchResponse(
                    success=False,
                    message="AI service failed to switch models",
                    active=ActiveModels(),
                    errors=ai_response.get("errors", [])
                )
    
    except httpx.TimeoutException:
        return ModelSwitchResponse(
            success=False,
            message="AI service timeout",
            active=ActiveModels(),
            errors=["Request to AI service timed out after 30 seconds"]
        )
    except httpx.RequestError as e:
        return ModelSwitchResponse(
            success=False,
            message="AI service connection error",
            active=ActiveModels(),
            errors=[f"Could not connect to AI service: {str(e)}"]
        )
    except Exception as e:
        db.rollback()
        return ModelSwitchResponse(
            success=False,
            message="Internal server error",
            active=ActiveModels(),
            errors=[str(e)]
        )
