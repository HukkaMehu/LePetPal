# Using Remote Camera with AI Features

## Your Setup

You have a remote camera streaming via ngrok:
```
https://skyla-nonpercussive-odette.ngrok-free.dev/video_feed
```

## How It Works

```
Remote Camera (Phone/Laptop)
    ↓
Flask Server (remote_camera_server.py)
    ↓
Ngrok Tunnel
    ↓
Your Backend (remote_video.py proxy)
    ↓
AI Processing (YOLOv8)
    ↓
WebSocket Broadcast
    ↓
Frontend (with AI overlays)
```

## Quick Start

### 1. Install AI Dependencies
```bash
setup_ai.bat
```

### 2. Start Services

**Terminal 1 - AI Service:**
```bash
cd ai_service
python main.py
```

**Terminal 2 - Backend:**
```bash
cd backend
python -m uvicorn app.main:app --reload
```

**Terminal 3 - Frontend:**
```bash
cd "Pet Training Web App"
npm run dev
```

### 3. Use Remote Camera Stream

Your backend now has a proxy endpoint that:
1. Fetches frames from your ngrok URL
2. Processes them through AI
3. Broadcasts detections via WebSocket
4. Re-streams to frontend

**Endpoint:**
```
http://localhost:8000/remote-video/stream?url=https://skyla-nonpercussive-odette.ngrok-free.dev/video_feed&ai=true
```

## Frontend Integration

Update your frontend to use the remote video proxy:

**Option 1: Update VideoPlayer component**

Edit `Pet Training Web App/src/components/VideoPlayer.tsx`:

```typescript
// Use remote video proxy instead of direct backend stream
const videoUrl = `http://localhost:8000/remote-video/stream?url=${encodeURIComponent('https://skyla-nonpercussive-odette.ngrok-free.dev/video_feed')}&ai=true`;
```

**Option 2: Add as environment variable**

Edit `Pet Training Web App/.env.local`:
```
NEXT_PUBLIC_REMOTE_CAMERA_URL=https://skyla-nonpercussive-odette.ngrok-free.dev/video_feed
```

Then in your component:
```typescript
const remoteCameraUrl = process.env.NEXT_PUBLIC_REMOTE_CAMERA_URL;
const videoUrl = `http://localhost:8000/remote-video/stream?url=${encodeURIComponent(remoteCameraUrl)}&ai=true`;
```

## Test Connection

Test if your remote camera is accessible:

```bash
curl "http://localhost:8000/remote-video/test?url=https://skyla-nonpercussive-odette.ngrok-free.dev/video_feed"
```

Should return:
```json
{
  "status": "connected",
  "url": "https://skyla-nonpercussive-odette.ngrok-free.dev/video_feed",
  "content_type": "multipart/x-mixed-replace; boundary=frame",
  "message": "Remote camera is accessible"
}
```

## What You'll Get

### 1. Real-Time AI Detection
- YOLOv8 processes frames from your remote camera
- Detects dogs with bounding boxes
- Confidence scores
- Pose keypoints

### 2. WebSocket Updates
Browser console will show:
```json
{
  "type": "ai_detections",
  "data": {
    "detections": [
      {
        "class_name": "dog",
        "confidence": 0.89,
        "box": {"x": 0.3, "y": 0.2, "w": 0.4, "h": 0.5}
      }
    ]
  }
}
```

### 3. Automatic Events
AI creates events when detecting:
- Sit commands
- Fetch sequences
- Object interactions
- Distractions

### 4. Video Buffer
Frames are buffered for clip extraction, so you can:
- Create clips from recent footage
- Save training moments
- Review past events

## Direct Browser Test

Open in browser:
```
http://localhost:8000/remote-video/stream?url=https://skyla-nonpercussive-odette.ngrok-free.dev/video_feed&ai=true
```

You should see your remote camera feed streaming through the backend.

## Troubleshooting

### Remote Camera Not Accessible

**Check ngrok tunnel:**
```bash
curl https://skyla-nonpercussive-odette.ngrok-free.dev/video_feed
```

If it fails, restart your ngrok tunnel:
```bash
ngrok http 5000
```

**Check remote camera server:**
Make sure `remote_camera_server.py` is running:
```bash
python remote_camera_server.py
```

### No AI Detections

**Check AI service:**
```bash
curl http://localhost:8001/health
```

**Check frame processor:**
```bash
curl http://localhost:8000/api/debug/frame-processor-stats
```

Should show frames being processed.

### Slow Performance

**Option 1: Process fewer frames**

Edit `backend/app/api/remote_video.py`:
```python
# Only process every 3rd frame
if frame_number % 3 == 0:
    await frame_processor.submit_frame(frame_bytes, timestamp_ms)
```

**Option 2: Disable AI temporarily**
```
http://localhost:8000/remote-video/stream?url=...&ai=false
```

**Option 3: Reduce remote camera quality**

Edit `remote_camera_server.py`:
```python
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 320)   # Was 640
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)  # Was 480
```

### CORS Issues

If frontend can't access the stream, add CORS headers.

Backend already has CORS enabled, but if you see errors, check:
```python
# backend/app/main.py
allow_origins=settings.CORS_ORIGINS  # Should include your frontend URL
```

## Architecture

```
┌─────────────────────┐
│  Remote Camera      │ (Phone/Laptop with webcam)
│  Flask Server       │
│  Port 5000          │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Ngrok Tunnel       │
│  Public HTTPS URL   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Backend Proxy      │
│  /remote-video/     │
│  • Fetches frames   │
│  • Buffers video    │
│  • Submits to AI    │
└──────────┬──────────┘
           │
           ├──────────────────┐
           │                  │
           ▼                  ▼
┌─────────────────┐  ┌─────────────────┐
│  AI Service     │  │  Video Buffer   │
│  YOLOv8         │  │  (for clips)    │
└────────┬────────┘  └─────────────────┘
         │
         ▼
┌─────────────────────┐
│  WebSocket          │
│  Broadcast          │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Frontend           │
│  • Video player     │
│  • AI overlays      │
│  • Event feed       │
└─────────────────────┘
```

## Performance

### Expected Latency
- Remote camera → Backend: 50-200ms (depends on network)
- AI processing: 50-150ms
- WebSocket broadcast: 1-5ms
- **Total:** 100-350ms end-to-end

### Bandwidth Usage
- Remote camera stream: ~1-2 Mbps
- Backend → Frontend: ~1-2 Mbps
- WebSocket (AI data): ~10-50 Kbps

### Optimization Tips
1. **Reduce remote camera resolution** (320x240 instead of 640x480)
2. **Lower JPEG quality** (60 instead of 80)
3. **Process fewer frames** (every 3rd frame = 10 FPS)
4. **Use local network** instead of ngrok when possible

## Alternative: Direct Frontend Connection

If you want the frontend to connect directly to your remote camera (without AI):

```typescript
// In VideoPlayer.tsx
const videoUrl = 'https://skyla-nonpercussive-odette.ngrok-free.dev/video_feed';
```

**Pros:**
- Lower latency
- Less bandwidth through backend

**Cons:**
- No AI processing
- No video buffering
- No clip extraction
- No automatic events

## Recommended Setup

**For Development:**
Use the proxy endpoint with AI enabled:
```
/remote-video/stream?url=...&ai=true
```

**For Production:**
Consider:
1. Running AI on edge device (Jetson Nano, Coral)
2. Using WebRTC for lower latency
3. Deploying backend closer to camera
4. Using dedicated streaming server (like MediaMTX)

## Next Steps

1. **Test the connection:**
   ```bash
   curl "http://localhost:8000/remote-video/test?url=https://skyla-nonpercussive-odette.ngrok-free.dev/video_feed"
   ```

2. **Start services and verify AI:**
   ```bash
   python test_ai_integration.py
   ```

3. **Update frontend to use proxy endpoint**

4. **Check browser console for AI detections**

5. **Watch Event Feed for automatic events**

---

**Your remote camera is now AI-powered!** 🎥🤖
