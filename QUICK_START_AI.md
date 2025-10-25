# Quick Start: Enable Real AI Processing

## Current State
Your AI service returns **mock data**. Video streams but frames are **never processed** by AI.

## 3 Steps to Enable Real AI (30 minutes)

### Step 1: Start Frame Processor (5 min)

**Edit `backend/app/main.py`:**

```python
# Add import at top
from app.workers.frame_processor import frame_processor

# Update lifespan function
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events."""
    await manager.setup_redis(settings.REDIS_URL)
    await event_processor.start()
    await metrics_aggregator.start()
    await routine_scheduler.start()
    await frame_processor.start()  # ADD THIS LINE
    yield
    await frame_processor.stop()  # ADD THIS LINE
    await event_processor.stop()
    await metrics_aggregator.stop()
    await routine_scheduler.stop()
    await manager.shutdown()
    video.cleanup_webcam()
```

### Step 2: Connect Video to AI (10 min)

**Edit `backend/app/api/video.py`:**

Find your video frame generation function and add frame submission:

```python
from app.workers.frame_processor import frame_processor
import time

# In your video streaming endpoint:
async def generate_frames():
    while True:
        # Your existing frame capture code
        success, frame = cap.read()
        if not success:
            break
            
        # Encode frame to JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        
        # Submit to AI processor (non-blocking)
        timestamp = time.time() * 1000  # milliseconds
        await frame_processor.submit_frame(frame_bytes, timestamp)
        
        # Continue streaming
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
```

### Step 3: Install Real AI Model (15 min)

**Option A: YOLOv8 (Recommended - Fast & Accurate)**

```bash
cd ai_service
pip install ultralytics opencv-python-headless pillow numpy
```

**Replace `ai_service/api/vision.py` detection function:**

```python
from ultralytics import YOLO
import cv2
import numpy as np
from PIL import Image
from io import BytesIO

# Load model at module level (once)
try:
    detector_model = YOLO('yolov8n.pt')  # Downloads automatically first time
    print("[Vision] YOLOv8 model loaded")
except Exception as e:
    print(f"[Vision] Failed to load YOLO: {e}")
    detector_model = None

def generate_real_dog_detection(frame_base64: str) -> List[Detection]:
    """Generate REAL dog detection using YOLOv8"""
    if not detector_model:
        return []  # Fall back to mock if model failed to load
    
    try:
        # Decode base64 to image
        img_bytes = base64.b64decode(frame_base64)
        img = Image.open(BytesIO(img_bytes))
        img_array = np.array(img)
        
        # Run detection (class 16 = dog in COCO dataset)
        results = detector_model(img_array, classes=[16], verbose=False)
        
        detections = []
        for result in results:
            for box in result.boxes:
                if box.cls == 16:  # Dog class
                    # Get normalized coordinates
                    x1, y1, x2, y2 = box.xyxyn[0].tolist()
                    x = x1
                    y = y1
                    w = x2 - x1
                    h = y2 - y1
                    
                    detections.append(Detection(
                        class_name="dog",
                        confidence=round(float(box.conf), 3),
                        box=BoundingBox(x=x, y=y, w=w, h=h)
                    ))
        
        return detections
        
    except Exception as e:
        print(f"[Vision] Detection error: {e}")
        return []

# Update the process_frame endpoint:
@router.post("/process", response_model=VisionProcessResponse)
async def process_frame(request: VisionProcessRequest):
    """Process frame with REAL AI detection"""
    try:
        response = VisionProcessResponse()
        
        # Use REAL detection if detector is enabled
        if "detector" in request.enabledModels:
            detections = generate_real_dog_detection(request.frameBase64)
            response.detections = detections
            
            # Generate pose keypoints if we detected a dog
            if detections and "pose" in request.enabledModels:
                response.keypoints = generate_mock_keypoints(detections[0].box)
        
        # Keep mock for actions and objects (for now)
        if "action" in request.enabledModels:
            response.actions = generate_mock_actions()
        
        if "object" in request.enabledModels:
            response.objects = generate_mock_objects()
        
        # Generate suggested events
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
```

**Option B: Keep Mock (For Testing)**

Skip this step if you want to test the pipeline with mock data first.

---

## Test It Works

### 1. Start Services

```bash
# Terminal 1: AI Service
cd ai_service
python main.py

# Terminal 2: Backend
cd backend
python -m uvicorn app.main:app --reload

# Terminal 3: Frontend
cd "Pet Training Web App"
npm run dev
```

### 2. Check Logs

**Backend should show:**
```
[FrameProcessor] Starting...
[FrameProcessor] Started
```

**AI Service should show:**
```
[Vision] YOLOv8 model loaded  # If using real model
```

### 3. Open Browser

Go to `http://localhost:3000` and check:

1. **Video Player**: Should show live video
2. **Browser Console**: Should see WebSocket messages with AI detections:
   ```json
   {
     "type": "ai_detections",
     "data": {
       "detections": [...],
       "actions": [...]
     }
   }
   ```
3. **Event Feed**: Should populate with AI-detected events

### 4. Monitor Performance

**Check frame processor stats:**
```bash
curl http://localhost:8000/api/debug/frame-processor-stats
```

Should return:
```json
{
  "running": true,
  "frames_processed": 150,
  "frames_dropped": 2,
  "queue_size": 1
}
```

---

## Troubleshooting

### No AI detections in WebSocket

**Check:**
1. Frame processor started: Look for `[FrameProcessor] Starting...` in backend logs
2. AI service reachable: `curl http://localhost:8001/health`
3. Frames being submitted: Add debug print in `submit_frame()`

### YOLOv8 not detecting dogs

**Check:**
1. Model downloaded: Should see `yolov8n.pt` in ai_service folder
2. Image decoding works: Add debug to save decoded image
3. Dog in frame: YOLO needs clear view of dog

### High frame drops

**Solutions:**
1. Reduce video FPS: Process every 2nd or 3rd frame
2. Increase queue size: Change `maxsize=5` to `maxsize=10`
3. Use faster model: `yolov8n.pt` (nano) is fastest

---

## Next Steps

Once basic AI is working:

1. **Add real action recognition** - Train custom model for sit/stand/lie
2. **Improve event detection** - Add temporal logic for fetch sequences
3. **Enable AI coach** - Integrate OpenAI or local LLM
4. **Add analytics** - Process events into training insights

See `AI_ENHANCEMENT_PLAN.md` for full roadmap.

---

## Performance Targets

**Good Performance:**
- Frame processing: 10-30 FPS
- AI latency: 50-200ms per frame
- Frame drops: <5%
- WebSocket latency: <100ms

**If slower:**
- Process every Nth frame (e.g., every 3rd frame = 10 FPS)
- Use smaller model (yolov8n vs yolov8s)
- Reduce video resolution

---

## Cost

**Free Option (Recommended):**
- YOLOv8: Free, runs on CPU
- Mock coach: Free
- Total: $0/month

**Paid Option:**
- OpenAI GPT-4 coach: ~$10-30/month
- Cloud GPU (optional): ~$50-100/month

Start with free option, add paid features later.
