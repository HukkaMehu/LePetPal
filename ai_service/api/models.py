"""
Models API - Model hot-swapping and management

This module handles runtime model switching with minimal interruption.
Requirements: 12.2, 12.3, 12.4
"""
from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
import asyncio
from datetime import datetime

router = APIRouter()


# Pydantic models
class ModelConfig(BaseModel):
    """Configuration for a single model"""
    name: str
    version: str
    artifact_uri: str
    metadata: Optional[Dict[str, Any]] = None


class ModelSwitchRequest(BaseModel):
    """Request to switch models"""
    detector: Optional[ModelConfig] = None
    action: Optional[ModelConfig] = None
    pose: Optional[ModelConfig] = None
    policy: Optional[ModelConfig] = None


class ModelSwitchResponse(BaseModel):
    """Response after model switch"""
    success: bool
    message: str
    active_models: Dict[str, str]
    errors: Optional[List[str]] = None
    switch_duration_ms: Optional[float] = None


# Global state for active models (in production, this would be a proper model manager)
class ModelManager:
    """Manages loaded AI models and handles hot-swapping"""
    
    def __init__(self):
        self.active_models = {
            "detector": "yolo-v8-nano@1.0",
            "action": "action-transformer-lite@1.0",
            "pose": "pose-lite@1.0",
            "policy": None
        }
        self.model_instances = {}
        self.switching_lock = asyncio.Lock()
    
    async def validate_model(self, model_type: str, config: ModelConfig) -> tuple[bool, Optional[str]]:
        """
        Validate that a model is compatible and can be loaded.
        
        Returns: (is_valid, error_message)
        """
        # Mock validation - in production, this would check:
        # - Model file exists at artifact_uri
        # - Model format is compatible
        # - Required dependencies are available
        # - Model size fits in memory
        
        valid_types = ["detector", "action", "pose", "policy"]
        if model_type not in valid_types:
            return False, f"Invalid model type: {model_type}"
        
        # Simulate validation delay
        await asyncio.sleep(0.1)
        
        # Mock validation logic
        if not config.artifact_uri:
            return False, "artifact_uri is required"
        
        if not config.name or not config.version:
            return False, "name and version are required"
        
        return True, None
    
    async def load_model(self, model_type: str, config: ModelConfig):
        """
        Load a model into memory.
        
        In production, this would:
        - Download model from artifact_uri if needed
        - Load model weights into memory
        - Initialize model for inference
        - Warm up model with dummy input
        """
        # Simulate model loading time
        await asyncio.sleep(0.5)
        
        # Store mock model instance
        model_key = f"{config.name}@{config.version}"
        self.model_instances[model_type] = {
            "config": config,
            "loaded_at": datetime.utcnow(),
            "key": model_key
        }
        
        return model_key
    
    async def unload_model(self, model_type: str):
        """
        Unload a model from memory.
        
        In production, this would:
        - Release GPU memory
        - Clear model weights
        - Clean up resources
        """
        if model_type in self.model_instances:
            # Simulate unload time
            await asyncio.sleep(0.1)
            del self.model_instances[model_type]
    
    async def switch_models(self, switch_request: ModelSwitchRequest) -> ModelSwitchResponse:
        """
        Perform hot-swap of models with minimal interruption.
        
        Strategy:
        1. Validate all requested models first
        2. Load new models in parallel
        3. Atomically switch active models
        4. Unload old models
        
        This maintains detection continuity with <2s interruption.
        """
        start_time = datetime.utcnow()
        errors = []
        models_to_switch = {}
        
        # Collect models to switch
        for model_type, config in [
            ("detector", switch_request.detector),
            ("action", switch_request.action),
            ("pose", switch_request.pose),
            ("policy", switch_request.policy)
        ]:
            if config:
                models_to_switch[model_type] = config
        
        if not models_to_switch:
            return ModelSwitchResponse(
                success=False,
                message="No models specified for switching",
                active_models=self.active_models,
                errors=["At least one model must be specified"]
            )
        
        # Acquire lock to prevent concurrent switches
        async with self.switching_lock:
            # Phase 1: Validate all models
            validation_tasks = []
            for model_type, config in models_to_switch.items():
                validation_tasks.append(self.validate_model(model_type, config))
            
            validation_results = await asyncio.gather(*validation_tasks)
            
            for (model_type, config), (is_valid, error) in zip(models_to_switch.items(), validation_results):
                if not is_valid:
                    errors.append(f"{model_type}: {error}")
            
            if errors:
                return ModelSwitchResponse(
                    success=False,
                    message="Model validation failed",
                    active_models=self.active_models,
                    errors=errors
                )
            
            # Phase 2: Load new models in parallel
            load_tasks = []
            for model_type, config in models_to_switch.items():
                load_tasks.append(self.load_model(model_type, config))
            
            try:
                loaded_keys = await asyncio.gather(*load_tasks)
            except Exception as e:
                errors.append(f"Failed to load models: {str(e)}")
                return ModelSwitchResponse(
                    success=False,
                    message="Model loading failed",
                    active_models=self.active_models,
                    errors=errors
                )
            
            # Phase 3: Atomically switch active models
            old_models = {}
            for model_type, model_key in zip(models_to_switch.keys(), loaded_keys):
                old_models[model_type] = self.active_models.get(model_type)
                self.active_models[model_type] = model_key
            
            # Phase 4: Unload old models (non-blocking)
            # In production, this would be done in background to not block response
            for model_type, old_key in old_models.items():
                if old_key and old_key != self.active_models[model_type]:
                    # Schedule unload in background
                    asyncio.create_task(self.unload_model(model_type))
        
        end_time = datetime.utcnow()
        duration_ms = (end_time - start_time).total_seconds() * 1000
        
        return ModelSwitchResponse(
            success=True,
            message=f"Successfully switched {len(models_to_switch)} model(s)",
            active_models=self.active_models.copy(),
            switch_duration_ms=duration_ms
        )
    
    def get_active_models(self) -> Dict[str, str]:
        """Get currently active models"""
        return self.active_models.copy()


# Global model manager instance
model_manager = ModelManager()


@router.post("/switch", response_model=ModelSwitchResponse)
async def switch_models(
    request: ModelSwitchRequest = Body(...)
):
    """
    Hot-swap AI models at runtime.
    
    This endpoint:
    1. Validates requested models for compatibility
    2. Loads new models in parallel
    3. Atomically switches active models
    4. Maintains detection continuity with <2s interruption
    
    Requirements: 12.2, 12.3, 12.4
    """
    try:
        result = await model_manager.switch_models(request)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Model switch failed: {str(e)}"
        )


@router.get("/active")
async def get_active_models():
    """
    Get currently active models.
    
    Returns a dictionary of model types to active model names.
    """
    return {
        "active_models": model_manager.get_active_models()
    }


@router.get("/status")
async def get_model_status():
    """
    Get detailed status of all loaded models.
    
    Returns information about loaded models including:
    - Active model for each type
    - Load time
    - Memory usage (mock)
    """
    status = {}
    
    for model_type, model_key in model_manager.active_models.items():
        if model_key and model_type in model_manager.model_instances:
            instance = model_manager.model_instances[model_type]
            status[model_type] = {
                "active": model_key,
                "loaded_at": instance["loaded_at"].isoformat(),
                "status": "ready"
            }
        else:
            status[model_type] = {
                "active": model_key,
                "status": "not_loaded" if model_key else "none"
            }
    
    return {
        "models": status,
        "switching_in_progress": model_manager.switching_lock.locked()
    }
