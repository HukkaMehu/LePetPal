"""
Pydantic models for AI service contracts
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class BoundingBox(BaseModel):
    """Bounding box coordinates"""
    x: float = Field(..., description="X coordinate (normalized 0-1)")
    y: float = Field(..., description="Y coordinate (normalized 0-1)")
    w: float = Field(..., description="Width (normalized 0-1)")
    h: float = Field(..., description="Height (normalized 0-1)")


class Detection(BaseModel):
    """Object detection result"""
    class_name: str = Field(..., alias="class", description="Detected class name")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    box: BoundingBox = Field(..., description="Bounding box")

    class Config:
        populate_by_name = True


class Keypoint(BaseModel):
    """Pose keypoint"""
    name: str = Field(..., description="Keypoint name (e.g., nose, shoulder)")
    x: float = Field(..., description="X coordinate (normalized 0-1)")
    y: float = Field(..., description="Y coordinate (normalized 0-1)")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")


class Action(BaseModel):
    """Action recognition result"""
    label: str = Field(..., description="Action label")
    probability: float = Field(..., ge=0.0, le=1.0, description="Probability score")


class ObjectDetection(BaseModel):
    """Object detection (toys, bowls, etc.)"""
    class_name: str = Field(..., alias="class", description="Object class")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    box: BoundingBox = Field(..., description="Bounding box")

    class Config:
        populate_by_name = True


class SuggestedEvent(BaseModel):
    """Suggested event from AI analysis"""
    type: str = Field(..., description="Event type")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    data: Dict[str, Any] = Field(default_factory=dict, description="Additional event data")


class VisionProcessRequest(BaseModel):
    """Request for vision processing"""
    frameBase64: str = Field(..., description="Base64 encoded frame")
    timestamp: float = Field(..., description="Frame timestamp in milliseconds")
    enabledModels: List[str] = Field(
        default_factory=lambda: ["detector", "pose", "action", "object"],
        description="List of enabled models"
    )


class VisionProcessResponse(BaseModel):
    """Response from vision processing"""
    detections: List[Detection] = Field(default_factory=list, description="Dog detections")
    keypoints: List[Keypoint] = Field(default_factory=list, description="Pose keypoints")
    actions: List[Action] = Field(default_factory=list, description="Recognized actions")
    objects: List[ObjectDetection] = Field(default_factory=list, description="Object detections")
    suggestedEvents: List[SuggestedEvent] = Field(
        default_factory=list,
        description="Suggested events based on analysis"
    )


class Event(BaseModel):
    """Event data for coach context"""
    id: str
    timestamp: str
    type: str
    data: Dict[str, Any] = Field(default_factory=dict)


class SessionMetrics(BaseModel):
    """Session metrics for coach summary"""
    sitCount: int = 0
    standCount: int = 0
    lieCount: int = 0
    fetchAttempts: int = 0
    fetchSuccesses: int = 0
    barks: int = 0
    timeInFrameMin: int = 0


class CoachTipsRequest(BaseModel):
    """Request for coaching tips"""
    currentAction: str = Field(..., description="Current detected action")
    recentEvents: List[Event] = Field(default_factory=list, description="Recent events")
    sessionContext: Dict[str, Any] = Field(default_factory=dict, description="Session context")


class CoachTipsResponse(BaseModel):
    """Response with coaching tip"""
    tip: str = Field(..., description="Coaching tip text")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in tip relevance")


class CoachSummaryRequest(BaseModel):
    """Request for session summary"""
    sessionStart: str = Field(..., description="Session start timestamp")
    sessionEnd: str = Field(..., description="Session end timestamp")
    events: List[Event] = Field(default_factory=list, description="Session events")
    metrics: SessionMetrics = Field(..., description="Session metrics")


class CoachSummaryResponse(BaseModel):
    """Response with session summary"""
    summary: str = Field(..., description="Overall session summary")
    wins: List[str] = Field(default_factory=list, description="Session wins")
    setbacks: List[str] = Field(default_factory=list, description="Session setbacks")
    suggestions: List[str] = Field(default_factory=list, description="Suggestions for improvement")
    highlightClips: List[str] = Field(default_factory=list, description="Clip IDs to review")


class CoachChatRequest(BaseModel):
    """Request for coach chat"""
    question: str = Field(..., description="User question")
    context: Dict[str, Any] = Field(
        default_factory=dict,
        description="Context including events and metrics"
    )


class CoachChatResponse(BaseModel):
    """Response from coach chat"""
    answer: str = Field(..., description="Answer to user question")
    relevantTimestamps: List[float] = Field(
        default_factory=list,
        description="Relevant video timestamps in milliseconds"
    )
