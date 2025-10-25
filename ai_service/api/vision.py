"""
Vision processing endpoints
Provides mock dog detection, pose estimation, action recognition, and object detection
"""
import random
from typing import List
from fastapi import APIRouter, HTTPException
from models import (
    VisionProcessRequest,
    VisionProcessResponse,
    Detection,
    Keypoint,
    Action,
    ObjectDetection,
    SuggestedEvent,
    BoundingBox
)

router = APIRouter()


def generate_mock_dog_detection() -> Detection:
    """Generate a mock dog detection with realistic bounding box"""
    # Random position in frame (centered with some variation)
    x = random.uniform(0.2, 0.5)
    y = random.uniform(0.2, 0.4)
    w = random.uniform(0.3, 0.5)
    h = random.uniform(0.4, 0.6)
    
    confidence = random.uniform(0.75, 0.95)
    
    return Detection(
        class_name="dog",
        confidence=round(confidence, 3),
        box=BoundingBox(x=x, y=y, w=w, h=h)
    )


def generate_mock_keypoints(detection_box: BoundingBox) -> List[Keypoint]:
    """Generate mock pose keypoints relative to detection box"""
    # Calculate keypoint positions relative to the dog bounding box
    center_x = detection_box.x + detection_box.w / 2
    center_y = detection_box.y + detection_box.h / 2
    
    keypoints = [
        Keypoint(
            name="nose",
            x=center_x + random.uniform(-0.05, 0.05),
            y=detection_box.y + detection_box.h * 0.2,
            confidence=random.uniform(0.85, 0.98)
        ),
        Keypoint(
            name="left_shoulder",
            x=center_x - detection_box.w * 0.15,
            y=center_y - detection_box.h * 0.1,
            confidence=random.uniform(0.80, 0.95)
        ),
        Keypoint(
            name="right_shoulder",
            x=center_x + detection_box.w * 0.15,
            y=center_y - detection_box.h * 0.1,
            confidence=random.uniform(0.80, 0.95)
        ),
        Keypoint(
            name="spine_mid",
            x=center_x,
            y=center_y,
            confidence=random.uniform(0.75, 0.92)
        ),
        Keypoint(
            name="spine_rear",
            x=center_x + random.uniform(-0.05, 0.05),
            y=center_y + detection_box.h * 0.2,
            confidence=random.uniform(0.70, 0.90)
        )
    ]
    
    return keypoints


def generate_mock_actions() -> List[Action]:
    """Generate mock action classifications"""
    # Define possible actions with varying probabilities
    action_pool = [
        ("sit", 0.25),
        ("stand", 0.30),
        ("lie", 0.15),
        ("approach", 0.10),
        ("fetch-return", 0.05),
        ("drinking", 0.05),
        ("eating", 0.05),
        ("playing", 0.05)
    ]
    
    # Randomly select 1-3 actions
    num_actions = random.randint(1, 3)
    selected_actions = random.sample(action_pool, num_actions)
    
    # Normalize probabilities to sum to 1
    total_prob = sum(prob for _, prob in selected_actions)
    actions = [
        Action(
            label=label,
            probability=round(prob / total_prob, 3)
        )
        for label, prob in selected_actions
    ]
    
    # Sort by probability descending
    actions.sort(key=lambda a: a.probability, reverse=True)
    
    return actions


def generate_mock_objects() -> List[ObjectDetection]:
    """Generate mock object detections (toys, bowls, etc.)"""
    objects = []
    
    # Randomly include objects
    object_types = [
        ("ball", 0.4),
        ("toy", 0.3),
        ("bowl", 0.5),
        ("treat", 0.2)
    ]
    
    for obj_type, probability in object_types:
        if random.random() < probability:
            # Random position (avoid center where dog is)
            x = random.choice([
                random.uniform(0.05, 0.2),  # Left side
                random.uniform(0.7, 0.85)   # Right side
            ])
            y = random.uniform(0.5, 0.8)
            w = random.uniform(0.05, 0.15)
            h = random.uniform(0.05, 0.15)
            
            objects.append(ObjectDetection(
                class_name=obj_type,
                confidence=round(random.uniform(0.70, 0.92), 3),
                box=BoundingBox(x=x, y=y, w=w, h=h)
            ))
    
    return objects


def generate_suggested_events(actions: List[Action], objects: List[ObjectDetection]) -> List[SuggestedEvent]:
    """Generate suggested events based on detections"""
    events = []
    
    # Check for high-confidence actions
    if actions:
        top_action = actions[0]
        if top_action.probability > 0.6:
            events.append(SuggestedEvent(
                type=top_action.label,
                confidence=top_action.probability,
                data={"action": top_action.label}
            ))
    
    # Check for fetch-return sequence
    if any(a.label == "fetch-return" for a in actions):
        events.append(SuggestedEvent(
            type="fetch_return",
            confidence=0.85,
            data={"sequence": "complete"}
        ))
    
    # Check for eating/drinking
    for action in actions:
        if action.label in ["eating", "drinking"] and action.probability > 0.5:
            events.append(SuggestedEvent(
                type=f"{action.label}_detected",
                confidence=action.probability,
                data={"action": action.label}
            ))
    
    # Check for ball interaction
    if any(obj.class_name == "ball" for obj in objects):
        if any(a.label in ["approach", "playing"] for a in actions):
            events.append(SuggestedEvent(
                type="ball_interaction",
                confidence=0.75,
                data={"object": "ball"}
            ))
    
    return events


@router.post("/process", response_model=VisionProcessResponse)
async def process_frame(request: VisionProcessRequest):
    """
    Process a video frame and return mock detections
    
    This endpoint simulates AI vision processing by returning realistic mock data:
    - Dog detection with bounding box
    - Pose keypoints (nose, shoulders, spine)
    - Action classifications (sit, stand, lie, etc.)
    - Object detections (ball, toy, bowl)
    - Suggested events based on analysis
    """
    try:
        response = VisionProcessResponse()
        
        # Generate dog detection if detector is enabled
        if "detector" in request.enabledModels:
            dog_detection = generate_mock_dog_detection()
            response.detections.append(dog_detection)
            
            # Generate pose keypoints if pose model is enabled
            if "pose" in request.enabledModels:
                response.keypoints = generate_mock_keypoints(dog_detection.box)
        
        # Generate action classifications if action model is enabled
        if "action" in request.enabledModels:
            response.actions = generate_mock_actions()
        
        # Generate object detections if object model is enabled
        if "object" in request.enabledModels:
            response.objects = generate_mock_objects()
        
        # Generate suggested events based on all detections
        response.suggestedEvents = generate_suggested_events(
            response.actions,
            response.objects
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing frame: {str(e)}"
        )


@router.get("/models")
async def list_models():
    """
    List available vision models
    
    Returns information about available detection, pose, action, and object models
    """
    return {
        "available": [
            {
                "name": "yolov8-dog-detector",
                "type": "detector",
                "version": "1.0.0",
                "status": "available"
            },
            {
                "name": "lightweight-pose-estimator",
                "type": "pose",
                "version": "1.0.0",
                "status": "available"
            },
            {
                "name": "action-recognition-transformer",
                "type": "action",
                "version": "1.0.0",
                "status": "available"
            },
            {
                "name": "object-detector-v2",
                "type": "object",
                "version": "1.0.0",
                "status": "available"
            }
        ],
        "active": {
            "detector": "yolov8-dog-detector",
            "pose": "lightweight-pose-estimator",
            "action": "action-recognition-transformer",
            "object": "object-detector-v2"
        }
    }
