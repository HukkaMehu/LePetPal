# Video Not Playing - Codec Issue

## Progress So Far

✅ Buffer is working (has frames)
✅ Frames are being extracted
✅ Video file is created (3MB)
✅ No more animated circles
❌ Video won't play in browser

## The Problem

The video is encoded with `mp4v` codec which browsers don't support well. We need H.264 codec.

## The Fix

I've updated the code to try H.264 codecs first. Now you need to:

### 1. Restart Celery Worker
```bash
# Stop it (Ctrl+C), then:
cd backend
.\start_celery_worker.bat
```

### 2. Record a New Clip
- Open Live page
- Wait 15 seconds
- Record a clip

### 3. Check Celery Logs
Should see:
```
[INFO] Using H.264 codec
```

Or:
```
[WARNING] H.264 codec not available, falling back to mp4v
```

## If H.264 Not Available

You might need to install OpenCV with H.264 support:

```bash
cd backend
pip uninstall opencv-python
pip install opencv-python-headless
```

Or install ffmpeg:
```bash
# Using chocolatey (if you have it)
choco install ffmpeg

# Or download from: https://ffmpeg.org/download.html
```

## Quick Test

1. Try playing the downloaded `test_clip.mp4` in:
   - Windows Media Player
   - VLC Player
   - Chrome browser (drag file into browser)

2. If it plays in VLC but not browser → codec issue
3. If it doesn't play anywhere → file corruption

## Alternative: Use Browser's MediaRecorder

Instead of OpenCV encoding, we could use the browser's built-in MediaRecorder API to capture video directly. This would:
- ✅ Always use browser-compatible codecs
- ✅ Better quality
- ✅ No codec issues
- ❌ Requires frontend changes

## Current Status

The video file exists and has content (3MB). The issue is just the codec compatibility with browsers.

After restarting Celery with the new codec code, new clips should work!
