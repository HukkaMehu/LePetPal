# How to See the AI Detection Boxes

## What I Just Added

I created a **real AI overlay system** that draws bounding boxes on your video stream based on actual YOLOv8 detections!

## How It Works

```
Video Stream (shows video)
    +
WebSocket (receives AI detections)
    +
AIOverlay Component (draws boxes)
    =
Video with visible bounding boxes! ✨
```

## Files Created/Modified

### New File
**`Pet Training Web App/src/components/AIOverlay.tsx`**
- Connects to WebSocket
- Listens for `ai_detections` messages
- Draws bounding boxes with labels
- Blue boxes for persons, green boxes for dogs

### Modified File
**`Pet Training Web App/src/components/VideoPlayer.tsx`**
- Imports AIOverlay component
- Tracks video dimensions
- Passes dimensions to AIOverlay
- Replaces mock overlay with real AI overlay

## How to See the Boxes

### Step 1: Start Everything
```bash
START_EVERYTHING.bat
```

Wait for:
- AI Service: `[Vision] YOLOv8 model loaded successfully`
- Backend: `[FrameProcessor] Started`
- Frontend: `Ready on http://localhost:3000`

### Step 2: Open the App
```
http://localhost:3000
```

### Step 3: Go to Live Page
Click "Live" in the navigation

### Step 4: Enable AI Overlays
Toggle the "Dog Detection" overlay switch (should be on by default)

### Step 5: Stand in Front of Camera
You should see:
- **Blue bounding box** around you
- **Label:** "person 92%" (or similar)
- **Box follows you** as you move

## What You'll See

### Person Detection
```
┌─────────────────────────────────┐
│                                 │
│  ┌──────────────────────┐       │
│  │ person 92%           │       │
│  │                      │       │
│  │        👤            │       │
│  │                      │       │
│  │                      │       │
│  └──────────────────────┘       │
│                                 │
└─────────────────────────────────┘
```

### Dog Detection
```
┌─────────────────────────────────┐
│                                 │
│     ┌──────────────┐            │
│     │ dog 89%      │            │
│     │              │            │
│     │     🐕       │            │
│     │              │            │
│     └──────────────┘            │
│                                 │
└─────────────────────────────────┘
```

### Both in Frame
```
┌─────────────────────────────────┐
│  ┌──────────────┐               │
│  │ person 92%   │               │
│  │              │               │
│  │     👤       │               │
│  │              │               │
│  └──────────────┘               │
│                    ┌──────────┐ │
│                    │ dog 89%  │ │
│                    │          │ │
│                    │   🐕     │ │
│                    │          │ │
│                    └──────────┘ │
└─────────────────────────────────┘
```

## Colors

- **Blue boxes** = Person (human)
- **Green boxes** = Dog
- **Semi-transparent fill** = Detection area
- **Label** = Class name + confidence %

## Troubleshooting

### No Boxes Appearing

**Check 1: AI Service Running**
```bash
curl http://localhost:8001/health
```

**Check 2: Frame Processor Running**
```bash
curl http://localhost:8000/api/debug/frame-processor-stats
```
Should show `"running": true` and frames being processed.

**Check 3: WebSocket Connected**
Open browser console (F12) and look for:
```
[AIOverlay] WebSocket connected
[AIOverlay] Received detections: [...]
```

**Check 4: Overlay Enabled**
Make sure the "Dog Detection" toggle is ON in the Live page.

**Check 5: Video Dimensions**
Check console for:
```
[VideoPlayer] Video metadata loaded, dimensions: 640 x 480
```

### Boxes in Wrong Position

**Issue:** Video dimensions not detected correctly

**Solution:** Check browser console for video dimensions. If they're 0x0, the video hasn't loaded yet.

### WebSocket Not Connecting

**Check backend WebSocket endpoint:**
```bash
# Should be accessible
curl http://localhost:8000/ws
```

**Check CORS settings** in `backend/app/main.py`:
```python
allow_origins=settings.CORS_ORIGINS
```

### Boxes Flickering

**Normal behavior** - boxes update every frame as AI processes new detections.

**To smooth:** Add temporal filtering (average last 3-5 detections).

## Testing Without Camera

### Option 1: Use Test Pattern
Backend generates a test pattern if no camera is available.

### Option 2: Use Demo Video
Place a video in `backend/mock_media/clips/sample_clip.mp4` and use:
```
http://localhost:8000/video/mjpeg?demo=true
```

### Option 3: Use Remote Camera
Use your ngrok URL:
```
http://localhost:8000/remote-video/stream?url=https://skyla-nonpercussive-odette.ngrok-free.dev/video_feed&ai=true
```

## Browser Console Messages

### Successful Connection
```
[AIOverlay] Connecting to WebSocket: ws://localhost:8000/ws
[AIOverlay] WebSocket connected
[AIOverlay] Received detections: [{class_name: "person", confidence: 0.92, ...}]
```

### Detection Updates
```
[AIOverlay] Received detections: [
  {
    class_name: "person",
    confidence: 0.92,
    box: {x: 0.3, y: 0.1, w: 0.4, h: 0.7}
  }
]
```

## Performance

### Expected
- **Box updates:** 10-30 per second (matches AI processing rate)
- **Latency:** 100-200ms from detection to display
- **Smooth tracking:** Boxes follow movement with minimal lag

### If Laggy
1. **Reduce AI processing rate** (process every 3rd frame)
2. **Increase frame processor queue size**
3. **Check CPU usage** (should be 30-60%)

## Advanced: Customize Appearance

Edit `Pet Training Web App/src/components/AIOverlay.tsx`:

### Change Colors
```typescript
const color = detection.class_name === 'person' 
  ? 'rgb(255, 0, 0)'    // Red for person
  : 'rgb(0, 255, 0)';   // Green for dog
```

### Change Border Width
```typescript
border: `3px solid ${color}`,  // Was 2px
```

### Add Confidence Threshold
```typescript
// Only show high-confidence detections
if (detection.confidence < 0.8) return null;
```

### Add Animation
```typescript
className="absolute pointer-events-none transition-all duration-100"
```

## Next Steps

### 1. Test It
- Start services
- Open Live page
- Stand in front of camera
- Watch the blue box track you!

### 2. Demo It
- Show real-time detection
- Move around to show tracking
- Point out confidence scores
- Explain the technology

### 3. Enhance It (Optional)
- Add pose keypoints overlay
- Add action labels
- Add object detection boxes
- Add heatmap visualization

---

**The boxes are now real and connected to actual AI!** 🎨✨

Just start the services, open the Live page, and you'll see bounding boxes appear around you (or any dog) in real-time!
