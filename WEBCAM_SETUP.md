# Webcam Setup Guide

This guide explains how to connect your computer's webcam to stream video to the frontend.

## What Changed

The backend video streaming has been updated to support three video sources (in priority order):

1. **Webcam** (default) - Your computer's connected camera
2. **Demo Video** - Pre-recorded sample video
3. **Test Pattern** - Generated animated pattern

## How It Works

### Backend Changes

The video router (`backend/app/api/video.py`) now:

- Uses `cv2.VideoCapture(0)` to access your default webcam
- Shares a single webcam capture across all connections for efficiency
- Automatically falls back to demo video or test pattern if webcam is unavailable
- Adds a red "LIVE" indicator when streaming from webcam
- Properly releases the webcam on app shutdown

### Endpoints

Both streaming endpoints now support webcam:

**MJPEG Stream:**
```
GET /video/mjpeg?webcam=true
```

**WebRTC Stream:**
```
POST /video/webrtc/offer?webcam=true
```

Query parameters:
- `webcam=true` (default) - Use webcam if available
- `webcam=false` - Skip webcam, use demo/test pattern
- `demo=true` - Use demo video as fallback instead of test pattern

## Testing Your Webcam

### 1. Start the Backend

```bash
cd backend
python -m uvicorn app.main:app --reload
```

### 2. Test MJPEG Stream

Open in your browser:
```
http://localhost:8000/video/mjpeg
```

You should see your webcam feed with:
- A red dot and "LIVE" text in the top-right corner
- Timestamp in the bottom-left corner

### 3. Test with Frontend

```bash
cd "Pet Training Web App"
npm run dev
```

Navigate to the live view page. The VideoPlayer component will automatically connect to your webcam via WebRTC (or fall back to MJPEG).

## Troubleshooting

### Webcam Not Detected

If you see the test pattern instead of your webcam:

1. **Check if webcam is connected:**
   - Make sure your webcam is plugged in
   - Check if other apps can access it (close them if they are)

2. **Try different camera index:**
   
   Edit `backend/app/api/video.py`, line with `cv2.VideoCapture(0)`:
   ```python
   # Try 1, 2, or 3 if 0 doesn't work
   webcam_capture = cv2.VideoCapture(1)
   ```

3. **Check permissions:**
   - On Windows: Settings > Privacy > Camera
   - Make sure Python/Terminal has camera access

4. **Test webcam with Python:**
   ```python
   import cv2
   cap = cv2.VideoCapture(0)
   print(f"Webcam opened: {cap.isOpened()}")
   ret, frame = cap.read()
   print(f"Frame captured: {ret}")
   cap.release()
   ```

### Multiple Cameras

If you have multiple cameras and want to use a specific one:

1. List available cameras:
   ```python
   import cv2
   for i in range(5):
       cap = cv2.VideoCapture(i)
       if cap.isOpened():
           print(f"Camera {i} is available")
           cap.release()
   ```

2. Update the camera index in `get_webcam_capture()` function

### Performance Issues

If the stream is laggy:

1. **Lower resolution:**
   ```python
   webcam_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
   webcam_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
   ```

2. **Reduce frame rate:**
   ```python
   webcam_capture.set(cv2.CAP_PROP_FPS, 15)
   ```

3. **Lower JPEG quality:**
   In `generate_mjpeg_frames()`, change:
   ```python
   cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 60])
   ```

## Disable Webcam

To temporarily disable webcam and use test pattern:

**Option 1: Query parameter**
```
http://localhost:8000/video/mjpeg?webcam=false
```

**Option 2: Frontend**

Update the VideoPlayer component to pass `webcam=false` in the API calls.

## Camera Settings

Current default settings (in `get_webcam_capture()`):
- Resolution: 640x480
- Frame rate: 30 fps
- Format: BGR24 (OpenCV default)

You can adjust these in `backend/app/api/video.py` for your specific camera.

## Next Steps

Once your webcam is working:

1. **Add camera selection UI** - Let users choose between multiple cameras
2. **Add camera controls** - Brightness, contrast, zoom, etc.
3. **Add recording** - Save webcam feed to clips
4. **Add motion detection** - Trigger events when motion is detected
5. **Add AI integration** - Connect to the AI service for pet detection

## API Reference

### GET /video/mjpeg

Stream video as MJPEG format.

**Query Parameters:**
- `webcam` (bool, default: true) - Use webcam if available
- `demo` (bool, default: false) - Use demo video as fallback

**Response:** `multipart/x-mixed-replace` stream

### POST /video/webrtc/offer

Establish WebRTC connection for low-latency streaming.

**Query Parameters:**
- `webcam` (bool, default: true) - Use webcam if available
- `demo` (bool, default: false) - Use demo video as fallback

**Request Body:**
```json
{
  "sdp": "...",
  "type": "offer"
}
```

**Response:**
```json
{
  "sdp": "...",
  "type": "answer"
}
```

## Notes

- The webcam capture is shared across all connections for efficiency
- Only one instance of the webcam is opened, even with multiple viewers
- The webcam is automatically released when the backend shuts down
- If the webcam becomes unavailable during streaming, it falls back to test pattern
- The "LIVE" indicator only appears when streaming from the actual webcam
