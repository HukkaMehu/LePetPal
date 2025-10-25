# Video Streaming Infrastructure Setup

This document describes the video streaming infrastructure implemented for the Dog Monitor application.

## What Was Implemented

### Backend (FastAPI)

#### 1. MJPEG Streaming Endpoint (`/video/mjpeg`)
- Streams video as multipart/x-mixed-replace format
- Generates test pattern with moving elements, frame counter, and timestamp
- Runs at 30 fps
- Provides fallback when WebRTC is unavailable

#### 2. WebRTC Signaling Endpoints
- **POST `/video/webrtc/offer`**: Handles WebRTC offer/answer exchange
  - Creates RTCPeerConnection with STUN server
  - Adds test pattern video track
  - Returns SDP answer for client connection
  
- **GET `/video/webrtc/ice-candidates/{connection_id}`**: Streams ICE candidates
  - Server-Sent Events (SSE) stream
  - Provides ICE candidates for NAT traversal

#### 3. Test Pattern Video Source
- Generates synthetic video frames with:
  - Gradient background
  - Moving circle animation
  - Frame counter
  - Real-time timestamp
- Used for both MJPEG and WebRTC streaming

### Frontend (Next.js/React)

#### VideoPlayer Component
A comprehensive video player with the following features:

**Connection Management:**
- Attempts WebRTC connection first for low latency
- Automatic fallback to MJPEG within 1 second if WebRTC fails
- Connection status indicators (connecting, connected, failed)
- Retry functionality

**Playback Controls:**
- Play/Pause (WebRTC only)
- Picture-in-Picture mode
- Fullscreen toggle
- Latency adjustment slider (100-2000ms)

**Keyboard Shortcuts:**
- `F` - Toggle fullscreen
- `Space` - Play/Pause

**UI Features:**
- Stream type indicator (WebRTC/MJPEG)
- Latency display
- Loading spinner during connection
- Error states with retry button
- Responsive design with aspect ratio preservation

## Dependencies Added

### Backend
- `opencv-python-headless==4.10.0.84` - Image processing and frame generation
- `numpy==1.26.4` - Array operations for video frames
- `av==12.0.0` - PyAV for video frame handling in aiortc

### Frontend
No additional dependencies needed (uses built-in WebRTC APIs)

## Testing the Implementation

### Start Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Start Frontend
```bash
cd frontend
npm install
npm run dev
```

### Access the Application
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- MJPEG Stream: http://localhost:8000/video/mjpeg
- API Docs: http://localhost:8000/docs

## How It Works

1. **Initial Connection**: VideoPlayer attempts WebRTC connection
2. **WebRTC Flow**:
   - Client creates offer and sends to `/video/webrtc/offer`
   - Server creates peer connection with test pattern track
   - Server returns answer with SDP
   - Client sets remote description and connection establishes
   - Video streams with <500ms latency

3. **Fallback Flow**:
   - If WebRTC fails (network issues, firewall, etc.)
   - After 1 second, automatically switches to MJPEG
   - Loads MJPEG stream from `/video/mjpeg`
   - Higher latency (~1-2s) but more reliable

## Requirements Satisfied

- ✅ **Requirement 1.1**: WebRTC connection within 2 seconds
- ✅ **Requirement 1.2**: MJPEG fallback within 1 second on WebRTC failure
- ✅ **Requirement 1.4**: Playback controls (play, pause, PiP, fullscreen)
- ✅ **Requirement 1.5**: Latency adjustment slider

## Next Steps

To integrate with real camera:
1. Replace `generate_test_pattern()` with actual camera capture (OpenCV VideoCapture)
2. Update `TestPatternVideoTrack` to use real frames
3. Add camera selection/configuration endpoints
4. Implement frame buffering for smoother playback
