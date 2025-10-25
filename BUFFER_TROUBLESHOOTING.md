# Video Buffer Troubleshooting

## Why You're Still Seeing Circles

The buffer code is working, but there are a few possible issues:

### Issue 1: Celery Worker Not Restarted ⚠️

**Most Likely Cause**: The Celery worker was started BEFORE the code changes.

**Fix**:
1. Stop the Celery worker (Ctrl+C)
2. Restart it:
   ```bash
   cd backend
   celery -A app.core.celery_app worker --loglevel=info --pool=solo
   ```

### Issue 2: Backend Not Restarted

**Fix**:
1. Stop backend (Ctrl+C)
2. Restart it:
   ```bash
   cd backend
   python -m uvicorn app.main:app --reload --port 8000
   ```

### Issue 3: Buffer Not Filled Yet

**Fix**: Wait 10-15 seconds after starting backend before recording

## Diagnostic Steps

### 1. Check Buffer Status
```bash
curl http://localhost:8000/video/buffer/status
```

Should show:
```json
{
  "frame_count": 400+,
  "duration_seconds": 20+,
  "oldest_frame": "...",
  "newest_frame": "..."
}
```

If `frame_count` is 0:
- Backend not running
- Video stream not active (open Live page)
- Buffer code not loaded

### 2. Test Buffer Extraction
```bash
cd backend
python scripts/test_buffer_extraction.py
```

This will:
- Show buffer status
- Try extracting frames
- Verify the buffer is working

### 3. Check Celery Logs

When you record a clip, Celery should log:
```
[INFO] Processing clip xxx
[INFO] Buffer status: {'frame_count': 488, ...}
[INFO] Requesting frames from 2025-10-25 16:50:59 to 2025-10-25 16:51:02
[INFO] Extracted 99 frames from buffer  ← THIS IS KEY
[INFO] First frame: 2025-10-25 16:50:59, Last frame: 2025-10-25 16:51:02
```

If you see:
```
[WARNING] No frames in buffer for time range, creating placeholder
```

Then the buffer doesn't have frames for that time.

## Common Issues

### "No frames in buffer"

**Causes**:
1. **Timing**: You recorded before buffer filled
2. **Timezone**: Mismatch between frontend and backend times
3. **Code not loaded**: Celery worker using old code

**Fixes**:
1. Wait 15 seconds after starting backend
2. Check system time is correct
3. Restart Celery worker

### Buffer has frames but extraction fails

**Cause**: Timezone mismatch

**Check**:
```bash
python -c "from datetime import datetime; print('System:', datetime.now()); print('UTC:', datetime.utcnow())"
```

Should show 3-hour difference (Helsinki = UTC+3).

**Fix**: The code should handle this automatically, but if not:
- Make sure backend uses `datetime.utcnow()`
- Make sure frontend uses `.toISOString()` (already does)

### High memory usage

**Cause**: Buffer storing many frames

**Fix**: Reduce buffer size in `backend/app/core/video_buffer.py`:
```python
video_buffer = VideoFrameBuffer(max_duration_seconds=120)  # 2 minutes instead of 5
```

## Step-by-Step Test

1. **Stop everything**
   - Stop Celery worker (Ctrl+C)
   - Stop backend (Ctrl+C)

2. **Start backend**
   ```bash
   cd backend
   python -m uvicorn app.main:app --reload --port 8000
   ```

3. **Start Celery**
   ```bash
   cd backend
   celery -A app.core.celery_app worker --loglevel=info --pool=solo
   ```

4. **Open Live page** in browser
   - This starts the video stream
   - Frames start filling the buffer

5. **Wait 15 seconds**
   - Let buffer fill up

6. **Check buffer**
   ```bash
   curl http://localhost:8000/video/buffer/status
   ```
   Should show 400+ frames

7. **Record a clip**
   - Click "Record Clip"
   - Wait 3-5 seconds
   - Click "Stop Recording"

8. **Watch Celery logs**
   Should see:
   ```
   [INFO] Extracted X frames from buffer
   ```

9. **Check gallery**
   - Video should show real footage
   - Not animated circles

## If Still Not Working

Run the diagnostic:
```bash
cd backend
python scripts/test_buffer_extraction.py
```

And check the Celery logs carefully. The logs will tell you exactly what's happening.

## Quick Fix Checklist

- [ ] Backend restarted
- [ ] Celery worker restarted  
- [ ] Live page opened (video streaming)
- [ ] Waited 15 seconds
- [ ] Buffer has 400+ frames
- [ ] Recorded a new clip
- [ ] Checked Celery logs for "Extracted X frames"

If all checked and still seeing circles, share the Celery logs!
