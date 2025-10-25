# Video Streaming Debugging Guide

## Issues Found

### 1. **VideoPlayer Component Not Used**
The `VideoPlayer.tsx` component exists but is **NOT being used** in the app. The `LivePage.tsx` component has its own simple video implementation using just an `<img>` tag for MJPEG.

### 2. **API URL Mismatch**
- Frontend `.env` has: `VITE_API_BASE_URL=http://localhost:8000/api`
- Video endpoint is at: `http://localhost:8000/video/mjpeg` (no `/api` prefix)
- The video URL in `.env` is correct: `VITE_VIDEO_STREAM_URL=http://localhost:8000/video/mjpeg`

### 3. **WebRTC Not Implemented in LivePage**
The `LivePage.tsx` shows a placeholder for WebRTC but doesn't actually implement it.

## Logging Added

### Backend (`backend/app/api/video.py`)
Added comprehensive logging to track:
- Webcam initialization attempts (tries index 1, then 0)
- WebRTC offer/answer process
- MJPEG stream requests
- Frame generation

### Frontend (`Pet Training Web App/src/components/VideoPlayer.tsx`)
Added logging to track:
- Component mounting
- WebRTC connection process
- Video track reception
- MJPEG fallback
- Video element state

## How to Debug

### 1. Check Backend Logs
Start the backend and watch for these messages:
```
[VIDEO API] MJPEG stream requested - demo=False, webcam=True
[VIDEO API] Starting MJPEG frame generation - demo_mode=False, use_webcam=True
[VIDEO API] Attempting to open webcam...
[VIDEO API] Webcam opened successfully on index 1
```

### 2. Check Frontend Console
Open browser DevTools Console and look for:
```
[VideoPlayer] Component mounted, backend URL: http://localhost:8000
[VideoPlayer] Starting WebRTC connection...
[VideoPlayer] Switching to MJPEG stream
[VideoPlayer] Loading MJPEG from: http://localhost:8000/video/mjpeg?webcam=true
```

### 3. Test Video Endpoints Directly

#### Test MJPEG Stream
Open in browser: `http://localhost:8000/video/mjpeg?webcam=true`
- Should show live video stream
- If no webcam, shows test pattern with moving circle

#### Test Backend API
```bash
curl http://localhost:8000/video/mjpeg?webcam=true
```

## Quick Fixes

### Option 1: Use the Existing VideoPlayer Component (Recommended)
Replace the video section in `LivePage.tsx` with the `VideoPlayer` component that has full WebRTC support and logging.

### Option 2: Add Logging to Current Implementation
The current `LivePage.tsx` uses a simple `<img>` tag. Add error handling:

```tsx
<img
  src={videoStreamUrl}
  alt="Live stream"
  className="w-full h-full object-cover"
  onError={(e) => {
    console.error('[LivePage] Video stream failed to load:', videoStreamUrl);
    console.error('Error:', e);
  }}
  onLoad={() => {
    console.log('[LivePage] Video stream loaded successfully:', videoStreamUrl);
  }}
/>
```

### Option 3: Enable Debug Mode
In `Pet Training Web App/.env`:
```
VITE_DEBUG=true
```

This will log the configuration on app startup.

## Common Issues

### 1. CORS Errors
If you see CORS errors, check `backend/app/core/config.py`:
```python
CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:3001"]
```

### 2. Webcam Not Found
Backend will try:
1. Index 1 (external USB webcam)
2. Index 0 (built-in webcam)
3. Test pattern (fallback)

### 3. Port Mismatch
- Backend should run on: `http://localhost:8000`
- Frontend should run on: `http://localhost:3000` or `http://localhost:3001`
- Check both are running: `netstat -an | findstr "8000 3000"`

## Testing Steps

1. **Start Backend**
   ```bash
   cd backend
   python -m uvicorn app.main:app --reload
   ```

2. **Check Backend Video Endpoint**
   Open: `http://localhost:8000/video/mjpeg?webcam=true`
   - Should see video or test pattern

3. **Start Frontend**
   ```bash
   cd "Pet Training Web App"
   npm run dev
   ```

4. **Check Browser Console**
   - Open DevTools (F12)
   - Go to Console tab
   - Look for `[LivePage]` or `[VideoPlayer]` messages

5. **Check Network Tab**
   - Open DevTools Network tab
   - Filter by "mjpeg" or "webrtc"
   - Check if requests are being made
   - Check response status codes

## Next Steps

1. **Immediate**: Check browser console for errors
2. **Backend**: Check terminal for video API logs
3. **Network**: Use DevTools Network tab to see if video requests are being made
4. **Test**: Try accessing `http://localhost:8000/video/mjpeg?webcam=true` directly
5. **Integrate**: Consider using the VideoPlayer component instead of the simple img tag
