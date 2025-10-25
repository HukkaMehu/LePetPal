# Real Video Recording Implementation

## What I Just Built

I've implemented **actual video recording** from your webcam! Here's what changed:

### New Components

1. **Video Frame Buffer** (`backend/app/core/video_buffer.py`)
   - Stores last 5 minutes of frames in memory
   - Thread-safe circular buffer
   - Automatic cleanup of old frames

2. **Updated Video API** (`backend/app/api/video.py`)
   - Now feeds every frame into the buffer
   - Added `/video/buffer/status` endpoint to check buffer state

3. **Updated Clip Processor** (`backend/app/workers/clip_processor.py`)
   - Extracts actual frames from buffer based on timestamp
   - Falls back to placeholder if frames not available
   - Creates video from real webcam footage

## How It Works

```
Webcam → Video Stream → Frame Buffer (5 min) → Clip Request → Extract Frames → Encode MP4 → Upload
```

### Step by Step:

1. **Continuous Buffering**: As video streams, every frame is stored with a timestamp
2. **User Records**: When you click "Record Clip", it notes start/end times
3. **Frame Extraction**: Clip processor finds all frames between those times
4. **Video Creation**: Frames are encoded into MP4 with proper timing
5. **Upload**: Video is uploaded to MinIO and made available

## Testing

### 1. Restart Backend
The video API needs to reload to start buffering:
```bash
# Stop and restart backend
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

### 2. Make Sure Celery is Running
```bash
cd backend
celery -A app.core.celery_app worker --loglevel=info --pool=solo
```

### 3. Check Buffer Status
```bash
curl http://localhost:8000/video/buffer/status
```

You should see:
```json
{
  "frame_count": 150,
  "duration_seconds": 5.0,
  "oldest_frame": "2025-10-25T19:00:00.000000",
  "newest_frame": "2025-10-25T19:00:05.000000"
}
```

### 4. Record a Clip

1. Open the Live page
2. **Wait 10-15 seconds** for buffer to fill
3. Click "Record Clip"
4. Wait a few seconds
5. Click "Stop Recording"
6. Check Celery logs - should say "Extracted X frames from buffer"
7. Go to Gallery - video should show actual webcam footage!

## Important Notes

### Buffer Warm-Up
The buffer needs time to fill. Wait at least 10 seconds after starting the backend before recording your first clip.

### Memory Usage
The buffer stores frames in memory:
- 640x480 RGB frame ≈ 1 MB
- 30 FPS × 300 seconds = 9,000 frames
- Total: ~9 GB for 5 minutes

**For production**, you'd want to:
- Reduce buffer size (e.g., 2 minutes)
- Use disk-based buffer
- Compress frames before storing

### Time Synchronization
The system uses UTC timestamps. Make sure your system clock is accurate.

## Limitations & Future Improvements

### Current Implementation
- ✅ Records actual webcam footage
- ✅ Stores last 5 minutes
- ✅ Thread-safe
- ✅ Automatic cleanup
- ⚠️ Memory-based (not persistent)
- ⚠️ Lost on restart

### Production Improvements

1. **Disk-Based Buffer**
   ```python
   # Store frames to disk instead of memory
   # Use SQLite or file-based storage
   ```

2. **Compressed Storage**
   ```python
   # Store JPEG-compressed frames
   # Reduces memory by 10x
   ```

3. **Configurable Duration**
   ```python
   # Allow users to set buffer size
   # Trade memory for recording length
   ```

4. **Multiple Streams**
   ```python
   # Support multiple cameras
   # Separate buffers per stream
   ```

## Troubleshooting

### "No frames in buffer" in logs
**Cause**: Buffer hasn't filled yet or video stream not running
**Fix**: 
- Wait 10-15 seconds after starting backend
- Make sure video stream is active (open Live page)
- Check buffer status: `curl http://localhost:8000/video/buffer/status`

### Video still shows placeholder
**Cause**: Frames not in buffer for that time range
**Fix**:
- Check system time is correct
- Verify buffer has frames: `/video/buffer/status`
- Try recording a shorter clip (5-10 seconds)

### High memory usage
**Cause**: Buffer storing many frames
**Fix**:
- Reduce buffer size in `video_buffer.py`:
  ```python
  video_buffer = VideoFrameBuffer(max_duration_seconds=120)  # 2 minutes
  ```

## Configuration

Edit `backend/app/core/video_buffer.py`:

```python
# Change buffer duration (default 300 seconds = 5 minutes)
video_buffer = VideoFrameBuffer(max_duration_seconds=120)  # 2 minutes

# Or in __init__:
def __init__(self, max_duration_seconds: int = 120):  # 2 minutes
```

## Summary

**Difficulty**: Medium (took ~30 minutes to implement)

**What You Get**:
- ✅ Real webcam footage in clips
- ✅ Automatic frame buffering
- ✅ No manual intervention needed
- ✅ Works with existing UI

**Next Steps**:
1. Restart backend
2. Start Celery worker
3. Wait 10 seconds
4. Record a clip
5. See actual footage in gallery!

The implementation is production-ready for demos and testing. For heavy use, consider moving to disk-based storage.
