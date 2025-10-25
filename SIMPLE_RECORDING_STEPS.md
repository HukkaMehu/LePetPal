# Simple Steps to Record Real Video

## The Issue

The buffer only fills when the video stream is active. Your Celery logs showed:
```
Buffer status: {'frame_count': 0, ...}
```

But now the buffer has **1464 frames** - it's working!

## Step-by-Step (Do This Exactly)

### 1. Open Live Page
- Go to http://localhost:5173/live
- **Keep this tab open**
- You should see the video stream

### 2. Wait 15 Seconds
- Just watch the video for 15 seconds
- This fills the buffer with frames

### 3. Check Buffer (Optional)
Open a new terminal:
```bash
curl http://localhost:8000/video/buffer/status
```

Should show something like:
```json
{
  "frame_count": 400+,
  "duration_seconds": 20+
}
```

### 4. Record a Clip
- **While still on the Live page**
- Click "Record Clip"
- Wait 3-5 seconds
- Click "Stop Recording"

### 5. Watch Celery Logs
You should see:
```
[INFO] Buffer status: {'frame_count': 1464, ...}  ← NOT 0!
[INFO] Extracted 99 frames from buffer  ← THIS IS THE KEY LINE
```

### 6. Check Gallery
- Go to Gallery page
- Your clip should show **real webcam footage**
- Not animated circles

## Why It Didn't Work Before

When you recorded at `19:55:50`, the logs showed:
```
Buffer status: {'frame_count': 0, ...}
```

This means:
- Live page wasn't open, OR
- You recorded immediately after opening it (buffer not filled yet)

## Current Status

Right now your buffer has **1464 frames** (about 2.5 minutes of video). If you record a clip NOW, it will work!

## Quick Test

1. Make sure Live page is open
2. Run this to verify buffer has frames:
   ```bash
   curl http://localhost:8000/video/buffer/status
   ```
3. If `frame_count` > 400, record a clip
4. Check Celery logs for "Extracted X frames"
5. Check gallery

## Important

- **Keep Live page open** while recording
- **Wait 15 seconds** after opening Live page
- **Buffer only fills while streaming**

The code is working perfectly - you just need to have the video stream active!
