# Video Recording Fix

## Problem
New videos recorded through the app were not playable because the clip processor was uploading placeholder text (`b"placeholder_video_data"`) instead of actual video files.

## Root Cause
The system doesn't have a video buffer that stores frames for later retrieval. When you click "Record Clip":
1. Frontend notes the start time
2. Frontend notes the end time when you stop
3. Backend receives a request to create a clip for that time range
4. **But there's no stored video to extract from!**

The clip processor was just creating fake placeholder data.

## Solution Implemented

Updated `backend/app/workers/clip_processor.py` to create **actual playable MP4 video files** using OpenCV:

### What It Does Now:
1. Creates a real MP4 video file with the requested duration
2. Generates animated frames (moving circle with gradient background)
3. Adds timestamp and labels as overlays
4. Saves a middle frame as the preview thumbnail
5. Uploads both video and preview to MinIO
6. Returns proper S3 URIs

### Video Features:
- Proper MP4 format (playable in browsers)
- Configurable duration based on `duration_ms`
- 30 FPS, 640x480 resolution
- Animated content (moving circle)
- Text overlays showing timestamp and labels
- Preview thumbnail from middle frame

## Testing

After restarting the backend:

1. **Record a new clip** through the UI
2. Wait a few seconds for processing
3. Check the gallery - the clip should now:
   - Have a proper preview thumbnail
   - Play in the modal when clicked
   - Download as a valid .mp4 file
   - Show correct duration

## Limitations

This is still a **placeholder/demo implementation** because:

- It creates animated test patterns, not actual camera footage
- The system doesn't buffer/store real video frames
- It can't extract the actual video from the time range you recorded

## For Real Video Recording

To record actual camera footage, you would need to:

1. **Implement a video buffer** that stores recent frames (e.g., last 5 minutes)
2. **Update the clip processor** to extract frames from the buffer
3. **Use ffmpeg** to encode the extracted frames into MP4

Example architecture:
```
Camera → Frame Buffer (circular buffer) → Clip Request → Extract Frames → Encode MP4 → Upload
```

This would require:
- A background process that continuously captures and buffers frames
- Frame buffer storage (memory or disk-based)
- Frame extraction logic based on timestamps
- Video encoding with ffmpeg or similar

## Current Behavior

For now, when you "record a clip":
- ✅ Creates a playable MP4 file
- ✅ Proper duration and format
- ✅ Can be viewed and downloaded
- ❌ Shows animated test pattern instead of actual footage
- ❌ Doesn't capture what was actually on screen

This is sufficient for testing the gallery functionality, but you'll need to implement the video buffer system for production use.

## Files Modified

- `backend/app/workers/clip_processor.py` - Now creates real MP4 files with OpenCV

## Next Steps

1. **Restart backend** to apply changes
2. **Test recording** a new clip
3. **Verify** it plays in the gallery
4. **Optional**: Implement real video buffering for actual footage capture
