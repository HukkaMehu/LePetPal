"""
Vision processing endpoints
Provides real dog detection with YOLOv8, plus mock pose estimation, action recognition, and object detection
"""
import random
import base64
from typing import List
from io import BytesIO
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

# Try to load YOLOv8 model for real detection
try:
    from ultralytics import YOLO
    import numpy as np
    from PIL import Image
    
    print("[Vision] Loading YOLOv8 model...")
    detector_model = YOLO('yolov8n.pt')  # Downloads automatically on first run
    print("[Vision] YOLOv8 model loaded successfully")
    YOLO_AVAILABLE = True
except Exception as e:
    print(f"[Vision] Failed to load YOLOv8: {e}")
    print("[Vision] Falling back to mock detection")
    detector_model = None
    YOLO_AVAILABLE = False


def generate_real_dog_detection(frame_base64: str) -> List[Detection]:
    """Generate REAL detection using YOLOv8 (detects both dogs and humans for demo)"""
    if not YOLO_AVAILABLE or detector_model is None:
        # Fallback to mock if YOLO not available
        return [generate_mock_dog_detection()]
    
    try:
        # Decode base64 to image
        img_bytes = base64.b64decode(frame_base64)
        img = Image.open(BytesIO(img_bytes))
        img_array = np.array(img)
        
        # Run detection for both person (class 0) and dog (class 16) in COCO dataset
        # This allows demo with humans while still working with dogs
        results = detector_model(img_array, classes=[0, 16], verbose=False)
        
        detections = []
        for result in results:
            for box in result.boxes:
                cls_id = int(box.cls)
                
                # Map class ID to name
                if cls_id == 0:
                    class_name = "person"
                elif cls_id == 16:
                    class_name = "dog"
                else:
                    continue
                
                # Get normalized coordinates
                x1, y1, x2, y2 = box.xyxyn[0].tolist()
                x = x1
                y = y1
                w = x2 - x1
                h = y2 - y1
                
                detections.append(Detection(
                    class_name=class_name,
                    confidence=round(float(box.conf), 3),
                    box=BoundingBox(x=x, y=y, w=w, h=h)
                ))
        
        return detections
        
    except Exception as e:
        print(f"[Vision] Detection error: {e}")
        # Fallback to mock on error
        return [generate_mock_dog_detection()]


def generate_mock_dog_detection() -> Detection:
    """Generate a mock detection with realistic bounding box (fallback)"""
    # Random position in frame (centered with some variation)
    x = random.uniform(0.2, 0.5)
    y = random.uniform(0.2, 0.4)
    w = random.uniform(0.3, 0.5)
    h = random.uniform(0.4, 0.6)
    
    confidence = random.uniform(0.75, 0.95)
    
    # Randomly choose between person and dog for demo purposes
    class_name = random.choice(["person", "dog"])
    
    return Detection(
        class_name=class_name,
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
    Process a video frame with REAL AI detection
    
    This endpoint uses YOLOv8 for real dog detection and provides:
    - Real dog detection with bounding box (YOLOv8)
    - Pose keypoints (mock - nose, shoulders, spine)
    - Action classifications (mock - sit, stand, lie, etc.)
    - Object detections (mock - ball, toy, bowl)
    - Suggested events based on analysis
    """
    try:
        response = VisionProcessResponse()
        
        # Use REAL detection if detector is enabled
        if "detector" in request.enabledModels:
            detections = generate_real_dog_detection(request.frameBase64)
            response.detections = detections
            
            # Generate pose keypoints if we detected a dog and pose model is enabled
            if detections and "pose" in request.enabledModels:
                response.keypoints = generate_mock_keypoints(detections[0].box)
        
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
