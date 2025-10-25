# AI Features - Quick Reference Card

## 🚀 Setup (One Time)
```bash
setup_ai.bat
```

## ▶️ Start Services
```bash
# Terminal 1
cd ai_service && python main.py

# Terminal 2
cd backend && python -m uvicorn app.main:app --reload

# Terminal 3
cd "Pet Training Web App" && npm run dev
```

## ✅ Verify Working
```bash
python test_ai_integration.py
```

## 📊 Check Stats
```bash
# Frame processor
curl http://localhost:8000/api/debug/frame-processor-stats

# AI service
curl http://localhost:8001/health
```

## 🔍 What to Look For

### Backend Logs
```
[FrameProcessor] Started ✓
```

### AI Service Logs
```
[Vision] YOLOv8 model loaded successfully ✓
```

### Browser Console (F12)
```json
{
  "type": "ai_detections",
  "data": {
    "detections": [...]
  }
}
```

## 🎯 Key Features

| Feature | Status | Description |
|---------|--------|-------------|
| YOLOv8 Detection | ✅ Active | Real dog detection with bounding boxes |
| Frame Processing | ✅ Active | 10-30 FPS real-time processing |
| WebSocket Broadcast | ✅ Active | Live AI results to frontend |
| Auto Events | ✅ Active | Creates events from AI analysis |
| Mock Fallback | ✅ Active | Falls back if YOLO fails |

## 🐛 Quick Fixes

### No Detections?
1. Check AI service: `curl http://localhost:8001/health`
2. Check frame processor: Look for `[FrameProcessor] Started`
3. Check video stream: Verify video player works

### Slow Performance?
Edit `backend/app/api/video.py`:
```python
# Process every 3rd frame
if frame_number % 3 == 0:
    await frame_processor.submit_frame(...)
```

### YOLOv8 Not Loading?
```bash
cd ai_service
pip install ultralytics opencv-python-headless pillow numpy
```

## 📁 Key Files

| File | Purpose |
|------|---------|
| `backend/app/main.py` | Starts frame processor |
| `backend/app/api/video.py` | Submits frames to AI |
| `backend/app/workers/frame_processor.py` | Processes frames |
| `ai_service/api/vision.py` | YOLOv8 detection |
| `ai_service/requirements.txt` | AI dependencies |

## 🎮 Demo Mode
```
http://localhost:3000/live?demo=true
```

## 📚 Full Docs
- **Setup:** [START_WITH_AI.md](START_WITH_AI.md)
- **Details:** [AI_FEATURES_SUMMARY.md](AI_FEATURES_SUMMARY.md)
- **Roadmap:** [AI_ENHANCEMENT_PLAN.md](AI_ENHANCEMENT_PLAN.md)

## 💡 Performance Targets

| Metric | Target | Typical |
|--------|--------|---------|
| Frame Rate | 10-30 FPS | 20 FPS |
| AI Latency | <200ms | 100ms |
| Frame Drops | <5% | 2% |
| CPU Usage | 30-60% | 45% |

## 🔧 Configuration

### Frame Queue Size
`backend/app/workers/frame_processor.py`:
```python
maxsize=5  # Increase to 10 if dropping frames
```

### AI Timeout
`backend/app/workers/frame_processor.py`:
```python
timeout=5.0  # Increase if AI is slow
```

### Video Resolution
`backend/app/api/video.py`:
```python
width=640, height=480  # Reduce to 320x240 for speed
```

---

**Need Help?** Run `python test_ai_integration.py` for diagnostics
