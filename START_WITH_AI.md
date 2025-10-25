# Start Your Pet Training App with AI Features

## Quick Start (3 Steps)

### Step 1: Install AI Dependencies
```bash
setup_ai.bat
```

This installs:
- YOLOv8 for real dog detection
- OpenCV for image processing
- Required Python packages

### Step 2: Start All Services
Open 3 terminals:

**Terminal 1 - AI Service:**
```bash
cd ai_service
python main.py
```
Wait for: `[Vision] YOLOv8 model loaded successfully`

**Terminal 2 - Backend:**
```bash
cd backend
python -m uvicorn app.main:app --reload
```
Wait for: `[FrameProcessor] Started`

**Terminal 3 - Frontend:**
```bash
cd "Pet Training Web App"
npm run dev
```

### Step 3: Test It Works
```bash
python test_ai_integration.py
```

Should show all ✓ checks passing.

## What's Different Now?

### Before (Mock AI)
- Random fake detections
- No real computer vision
- Events created randomly
- No actual frame processing

### After (Real AI)
- **Real dog detection** with YOLOv8
- **Actual bounding boxes** around dogs
- **Confidence scores** (0.0-1.0)
- **Real-time processing** of video frames
- **Smart event creation** based on AI analysis

## How It Works

```
┌─────────────┐
│ Video Stream│ (30 FPS)
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│ Frame Processor │ (Async Queue)
└──────┬──────────┘
       │
       ▼
┌─────────────┐
│ AI Service  │ (YOLOv8)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  WebSocket  │ (Broadcast)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Frontend   │ (Real-time UI)
└─────────────┘
```

## Verify AI is Working

### 1. Check Backend Logs
Look for:
```
[FrameProcessor] Starting...
[FrameProcessor] Started
```

### 2. Check AI Service Logs
Look for:
```
[Vision] Loading YOLOv8 model...
[Vision] YOLOv8 model loaded successfully
```

### 3. Check Browser Console
Open DevTools (F12) and look for:
```json
{
  "type": "ai_detections",
  "data": {
    "detections": [
      {
        "class_name": "dog",
        "confidence": 0.89,
        "box": {...}
      }
    ]
  }
}
```

### 4. Check Frame Processor Stats
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

## Using the AI Features

### 1. Live Detection
- Go to Live page
- Point camera at a dog
- See bounding box appear (if frontend implements overlays)
- Check console for detection data

### 2. Event Feed
- AI automatically creates events when it detects:
  - High-confidence actions (sit, stand, lie)
  - Fetch sequences
  - Object interactions
  - Distractions

### 3. Analytics
- AI-detected events feed into analytics
- Track training patterns
- See behavioral insights

## Performance Tuning

### If Frame Rate is Low

**Option 1: Process Fewer Frames**

Edit `backend/app/api/video.py`:
```python
# Only process every 3rd frame (10 FPS instead of 30 FPS)
if frame_number % 3 == 0:
    await frame_processor.submit_frame(frame_bytes, timestamp_ms)
```

**Option 2: Increase Queue Size**

Edit `backend/app/workers/frame_processor.py`:
```python
self.frame_queue: asyncio.Queue = asyncio.Queue(maxsize=10)  # Was 5
```

**Option 3: Reduce Video Resolution**

Edit `backend/app/api/video.py`:
```python
webcam_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 320)   # Was 640
webcam_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)  # Was 480
```

### If Too Many Frames Dropped

Check stats:
```bash
curl http://localhost:8000/api/debug/frame-processor-stats
```

If `frames_dropped` is high (>10%):
1. Process fewer frames (see above)
2. Increase queue size
3. Check AI service isn't overloaded

## Demo Mode (No Dog Required)

For testing or presentations:

1. **Add demo video:**
   - Place video in `backend/mock_media/clips/sample_clip.mp4`
   - Or use any dog training video

2. **Enable demo mode:**
   ```
   http://localhost:3000/live?demo=true
   ```

3. **AI processes demo video:**
   - Same real-time detection
   - Same event creation
   - Perfect for demos!

## Troubleshooting

### YOLOv8 Model Not Loading

**Symptom:** `[Vision] Failed to load YOLOv8`

**Solution:**
```bash
cd ai_service
pip install ultralytics opencv-python-headless pillow numpy
```

If still failing, download manually:
1. Download: https://github.com/ultralytics/assets/releases/download/v8.2.0/yolov8n.pt
2. Place in `ai_service/` folder

### No AI Detections in Browser

**Check:**
1. ✓ AI service running: `curl http://localhost:8001/health`
2. ✓ Backend running: `curl http://localhost:8000/health`
3. ✓ Frame processor started: Check backend logs
4. ✓ Video streaming: Check video player works
5. ✓ WebSocket connected: Check browser console

### Frame Processor Not Starting

**Symptom:** No `[FrameProcessor] Started` in logs

**Solution:**
1. Check backend logs for errors
2. Verify Redis is running (if using Redis)
3. Check AI service is reachable: `curl http://localhost:8001/health`

### High CPU Usage

**Normal:** YOLOv8 uses CPU for inference
**Expected:** 30-60% CPU usage on modern processors

**To reduce:**
1. Process fewer frames (every 3rd or 5th frame)
2. Reduce video resolution
3. Use GPU if available (requires CUDA setup)

## Advanced: GPU Acceleration (Optional)

For faster processing with NVIDIA GPU:

1. **Install CUDA Toolkit:**
   - Download from NVIDIA website
   - Install CUDA 11.8 or 12.x

2. **Install PyTorch with CUDA:**
   ```bash
   cd ai_service
   pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
   ```

3. **Verify GPU:**
   ```python
   import torch
   print(torch.cuda.is_available())  # Should print True
   ```

4. **YOLOv8 will automatically use GPU**

Expected speedup: 3-5x faster inference

## Next Steps

### 1. Add Frontend Overlays
Display AI detections on video:
- Bounding boxes
- Confidence scores
- Action labels
- Pose keypoints

### 2. Train Custom Models
For better accuracy:
- Collect dog training videos
- Label specific actions (sit, stand, lie)
- Fine-tune YOLOv8 or train action classifier

### 3. Add AI Coach
Integrate LLM for coaching:
- OpenAI GPT-4 (paid)
- Ollama + Llama 3 (free, local)
- Natural language Q&A about training

See `AI_ENHANCEMENT_PLAN.md` for full roadmap.

## Support

### Check Logs
- **Backend:** Look for `[FrameProcessor]` messages
- **AI Service:** Look for `[Vision]` messages
- **Browser:** Open DevTools console (F12)

### Test Integration
```bash
python test_ai_integration.py
```

### Get Stats
```bash
# Frame processor
curl http://localhost:8000/api/debug/frame-processor-stats

# AI service health
curl http://localhost:8001/health

# Backend health
curl http://localhost:8000/health
```

---

**You're ready to go!** Start the services and watch real AI detection in action. 🐕🤖
