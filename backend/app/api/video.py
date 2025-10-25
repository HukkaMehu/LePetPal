import asyncio
import time
import json
import uuid
from typing import AsyncGenerator, Dict, Optional
from pathlib import Path
from fastapi import APIRouter, Response, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import cv2
import numpy as np
from aiortc import RTCPeerConnection, RTCSessionDescription, VideoStreamTrack, RTCConfiguration, RTCIceServer
from aiortc.contrib.media import MediaRelay
from av import VideoFrame

router = APIRouter(prefix="/video", tags=["video"])

# Store active peer connections
peer_connections: Dict[str, RTCPeerConnection] = {}
ice_candidates_queues: Dict[str, asyncio.Queue] = {}

# Demo mode video path
DEMO_VIDEO_PATH = Path(__file__).parent.parent.parent / "mock_media" / "clips" / "sample_clip.mp4"

# Global webcam capture (shared across connections)
webcam_capture: Optional[cv2.VideoCapture] = None
webcam_lock = asyncio.Lock()


def generate_test_pattern(width: int = 640, height: int = 480, frame_number: int = 0) -> np.ndarray:
    """Generate a test pattern frame with moving elements."""
    # Create a gradient background
    frame = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Add gradient
    for i in range(height):
        frame[i, :] = [int(255 * i / height), 50, int(255 * (1 - i / height))]
    
    # Add moving circle
    center_x = int(width / 2 + 150 * np.sin(frame_number * 0.05))
    center_y = int(height / 2 + 100 * np.cos(frame_number * 0.05))
    cv2.circle(frame, (center_x, center_y), 30, (0, 255, 0), -1)
    
    # Add frame counter text
    cv2.putText(
        frame,
        f"Frame: {frame_number}",
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (255, 255, 255),
        2
    )
    
    # Add timestamp
    timestamp = time.strftime("%H:%M:%S")
    cv2.putText(
        frame,
        timestamp,
        (10, height - 20),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2
    )
    
    return frame


def generate_demo_frame(cap: cv2.VideoCapture, frame_number: int) -> Optional[np.ndarray]:
    """Generate a frame from demo video, looping if necessary."""
    # Get total frames
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    if total_frames == 0:
        return None
    
    # Loop video
    frame_pos = frame_number % total_frames
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos)
    
    ret, frame = cap.read()
    if not ret:
        # Reset to beginning if read fails
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        ret, frame = cap.read()
    
    if ret:
        # Add "DEMO MODE" watermark
        cv2.putText(
            frame,
            "DEMO MODE",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 255),
            2
        )
        
        # Add timestamp
        timestamp = time.strftime("%H:%M:%S")
        cv2.putText(
            frame,
            timestamp,
            (10, frame.shape[0] - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )
    
    return frame if ret else None


def get_webcam_capture() -> Optional[cv2.VideoCapture]:
    """Get or initialize the webcam capture."""
    global webcam_capture
    
    if webcam_capture is None or not webcam_capture.isOpened():
        print(f"[VIDEO API] Attempting to open webcam...")
        # Try to open webcam (1 is the external USB webcam)
        webcam_capture = cv2.VideoCapture(1)
        
        if webcam_capture.isOpened():
            print(f"[VIDEO API] Webcam opened successfully on index 1")
            # Set camera properties for better performance
            webcam_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            webcam_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            webcam_capture.set(cv2.CAP_PROP_FPS, 30)
        else:
            print(f"[VIDEO API] Failed to open webcam on index 1, trying index 0...")
            webcam_capture = cv2.VideoCapture(0)
            if webcam_capture.isOpened():
                print(f"[VIDEO API] Webcam opened successfully on index 0")
                webcam_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                webcam_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                webcam_capture.set(cv2.CAP_PROP_FPS, 30)
            else:
                print(f"[VIDEO API] Failed to open webcam on both indices")
                webcam_capture = None
    
    return webcam_capture if webcam_capture and webcam_capture.isOpened() else None


async def generate_mjpeg_frames(demo_mode: bool = False, use_webcam: bool = True) -> AsyncGenerator[bytes, None]:
    """Generate MJPEG frames from webcam, demo video, or test pattern."""
    frame_number = 0
    cap = None
    
    print(f"[VIDEO API] Starting MJPEG frame generation - demo_mode={demo_mode}, use_webcam={use_webcam}")
    
    # Priority: webcam > demo video > test pattern
    if use_webcam:
        cap = get_webcam_capture()
        if cap:
            print(f"[VIDEO API] Using webcam for MJPEG")
        else:
            print(f"[VIDEO API] Webcam not available")
    
    # Fallback to demo video if webcam unavailable and demo mode enabled
    if cap is None and demo_mode and DEMO_VIDEO_PATH.exists():
        cap = cv2.VideoCapture(str(DEMO_VIDEO_PATH))
        print(f"[VIDEO API] Using demo video for MJPEG: {DEMO_VIDEO_PATH}")
    
    try:
        while True:
            frame = None
            
            # Try to read from webcam or demo video
            if cap is not None and cap.isOpened():
                async with webcam_lock:
                    ret, frame = cap.read()
                
                if ret and frame is not None:
                    # Add timestamp overlay
                    timestamp = time.strftime("%H:%M:%S")
                    cv2.putText(
                        frame,
                        timestamp,
                        (10, frame.shape[0] - 20),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (255, 255, 255),
                        2
                    )
                    
                    # Add "LIVE" indicator for webcam
                    if use_webcam and cap == webcam_capture:
                        cv2.circle(frame, (frame.shape[1] - 30, 30), 10, (0, 0, 255), -1)
                        cv2.putText(
                            frame,
                            "LIVE",
                            (frame.shape[1] - 80, 35),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.7,
                            (0, 0, 255),
                            2
                        )
                else:
                    frame = None
            
            # Fallback to test pattern if no frame available
            if frame is None:
                frame = generate_test_pattern(frame_number=frame_number)
            
            # Encode frame as JPEG
            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            frame_bytes = buffer.tobytes()
            
            # Yield frame in multipart format
            yield (
                b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n'
            )
            
            frame_number += 1
            
            # Control frame rate (30 fps)
            await asyncio.sleep(1 / 30)
    finally:
        # Don't release webcam_capture as it's shared
        if cap is not None and cap != webcam_capture:
            cap.release()


@router.get("/mjpeg")
async def stream_mjpeg(
    demo: bool = Query(False, description="Enable demo mode with pre-recorded video"),
    webcam: bool = Query(True, description="Use webcam if available")
):
    """
    Stream video as MJPEG (multipart/x-mixed-replace).
    This endpoint provides a fallback streaming option when WebRTC is unavailable.
    
    Query Parameters:
    - demo: If true, streams pre-recorded demo video instead of live feed
    - webcam: If true (default), attempts to use webcam before falling back to demo/test pattern
    """
    print(f"[VIDEO API] MJPEG stream requested - demo={demo}, webcam={webcam}")
    return StreamingResponse(
        generate_mjpeg_frames(demo_mode=demo, use_webcam=webcam),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )


# WebRTC Models
class WebRTCOffer(BaseModel):
    sdp: str
    type: str


class WebRTCAnswer(BaseModel):
    sdp: str
    type: str


class TestPatternVideoTrack(VideoStreamTrack):
    """
    A video track that generates frames from webcam, demo video, or test pattern for WebRTC streaming.
    """
    
    def __init__(self, demo_mode: bool = False, use_webcam: bool = True):
        super().__init__()
        self.frame_number = 0
        self.demo_mode = demo_mode
        self.use_webcam = use_webcam
        self.cap = None
        
        # Priority: webcam > demo video > test pattern
        if self.use_webcam:
            self.cap = get_webcam_capture()
        
        # Fallback to demo video if webcam unavailable and demo mode enabled
        if self.cap is None and self.demo_mode and DEMO_VIDEO_PATH.exists():
            self.cap = cv2.VideoCapture(str(DEMO_VIDEO_PATH))
    
    async def recv(self):
        """Generate and return the next video frame."""
        pts, time_base = await self.next_timestamp()
        
        frame_np = None
        
        # Try to read from webcam or demo video
        if self.cap is not None and self.cap.isOpened():
            async with webcam_lock:
                ret, frame_np = self.cap.read()
            
            if ret and frame_np is not None:
                # Add timestamp overlay
                timestamp = time.strftime("%H:%M:%S")
                cv2.putText(
                    frame_np,
                    timestamp,
                    (10, frame_np.shape[0] - 20),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 255, 255),
                    2
                )
                
                # Add "LIVE" indicator for webcam
                if self.use_webcam and self.cap == webcam_capture:
                    cv2.circle(frame_np, (frame_np.shape[1] - 30, 30), 10, (0, 0, 255), -1)
                    cv2.putText(
                        frame_np,
                        "LIVE",
                        (frame_np.shape[1] - 80, 35),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 0, 255),
                        2
                    )
            else:
                frame_np = None
        
        # Fallback to test pattern if no frame available
        if frame_np is None:
            frame_np = generate_test_pattern(frame_number=self.frame_number)
        
        self.frame_number += 1
        
        # Convert to VideoFrame
        frame = VideoFrame.from_ndarray(frame_np, format="bgr24")
        frame.pts = pts
        frame.time_base = time_base
        
        return frame
    
    def __del__(self):
        """Clean up video capture."""
        # Don't release webcam_capture as it's shared
        if self.cap is not None and self.cap != webcam_capture:
            self.cap.release()


@router.post("/webrtc/offer")
async def webrtc_offer(
    offer: WebRTCOffer,
    demo: bool = Query(False, description="Enable demo mode with pre-recorded video"),
    webcam: bool = Query(True, description="Use webcam if available")
):
    """
    Handle WebRTC offer and return answer with SDP.
    This endpoint establishes a WebRTC peer connection for low-latency streaming.
    
    Query Parameters:
    - demo: If true, streams pre-recorded demo video instead of live feed
    - webcam: If true (default), attempts to use webcam before falling back to demo/test pattern
    """
    try:
        print(f"[VIDEO API] WebRTC offer received - demo={demo}, webcam={webcam}")
        
        # Create a new peer connection
        pc = RTCPeerConnection(
            configuration=RTCConfiguration(
                iceServers=[RTCIceServer(urls=["stun:stun.l.google.com:19302"])]
            )
        )
        print(f"[VIDEO API] RTCPeerConnection created")
        
        # Generate unique ID for this connection
        connection_id = str(uuid.uuid4())
        peer_connections[connection_id] = pc
        ice_candidates_queues[connection_id] = asyncio.Queue()
        print(f"[VIDEO API] Connection ID: {connection_id}")
        
        # Add video track (webcam, demo, or test pattern)
        video_track = TestPatternVideoTrack(demo_mode=demo, use_webcam=webcam)
        pc.addTrack(video_track)
        print(f"[VIDEO API] Video track added")
        
        # Handle ICE candidates
        @pc.on("icecandidate")
        async def on_icecandidate(candidate):
            if candidate:
                await ice_candidates_queues[connection_id].put({
                    "candidate": candidate.candidate,
                    "sdpMid": candidate.sdpMid,
                    "sdpMLineIndex": candidate.sdpMLineIndex
                })
        
        # Handle connection state changes
        @pc.on("connectionstatechange")
        async def on_connectionstatechange():
            if pc.connectionState in ["failed", "closed"]:
                # Clean up
                if connection_id in peer_connections:
                    del peer_connections[connection_id]
                if connection_id in ice_candidates_queues:
                    del ice_candidates_queues[connection_id]
        
        # Set remote description from offer
        print(f"[VIDEO API] Setting remote description")
        await pc.setRemoteDescription(RTCSessionDescription(sdp=offer.sdp, type=offer.type))
        
        # Create answer
        print(f"[VIDEO API] Creating answer")
        answer = await pc.createAnswer()
        await pc.setLocalDescription(answer)
        print(f"[VIDEO API] Answer created and local description set")
        
        return WebRTCAnswer(
            sdp=pc.localDescription.sdp,
            type=pc.localDescription.type
        )
    
    except Exception as e:
        print(f"[VIDEO API] Error processing WebRTC offer: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to process WebRTC offer: {str(e)}")


async def generate_ice_candidates(connection_id: str) -> AsyncGenerator[str, None]:
    """Generate Server-Sent Events stream of ICE candidates."""
    if connection_id not in ice_candidates_queues:
        return
    
    queue = ice_candidates_queues[connection_id]
    
    try:
        while True:
            # Wait for ICE candidate with timeout
            try:
                candidate = await asyncio.wait_for(queue.get(), timeout=30.0)
                yield f"data: {json.dumps(candidate)}\n\n"
            except asyncio.TimeoutError:
                # Send keepalive
                yield f": keepalive\n\n"
    except asyncio.CancelledError:
        pass


@router.get("/webrtc/ice-candidates/{connection_id}")
async def get_ice_candidates(connection_id: str):
    """
    Stream ICE candidates as Server-Sent Events.
    The frontend should connect to this endpoint after receiving the WebRTC answer.
    """
    if connection_id not in ice_candidates_queues:
        raise HTTPException(status_code=404, detail="Connection not found")
    
    return StreamingResponse(
        generate_ice_candidates(connection_id),
        media_type="text/event-stream"
    )


def cleanup_webcam():
    """Release the webcam capture. Call this on app shutdown."""
    global webcam_capture
    if webcam_capture is not None:
        webcam_capture.release()
        webcam_capture = None
