"""
Remote Video Proxy
Fetches video from external camera feed and processes through AI
"""
import asyncio
import time
import httpx
from typing import AsyncGenerator
from datetime import datetime
from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import StreamingResponse
import cv2
import numpy as np
from app.core.video_buffer import video_buffer
from app.workers.frame_processor import frame_processor

router = APIRouter(prefix="/remote-video", tags=["remote-video"])

# Global client for remote camera
remote_client: httpx.AsyncClient = None


async def get_remote_client():
    """Get or create remote camera client"""
    global remote_client
    if remote_client is None:
        remote_client = httpx.AsyncClient(timeout=30.0)
    return remote_client


async def fetch_and_process_remote_stream(
    remote_url: str,
    process_ai: bool = True
) -> AsyncGenerator[bytes, None]:
    """
    Fetch frames from remote camera and optionally process through AI.
    
    Args:
        remote_url: URL of remote MJPEG stream
        process_ai: Whether to process frames through AI
    """
    client = await get_remote_client()
    frame_number = 0
    
    print(f"[RemoteVideo] Connecting to {remote_url}")
    
    try:
        async with client.stream('GET', remote_url) as response:
            if response.status_code != 200:
                raise HTTPException(
                    status_code=502,
                    detail=f"Remote camera returned status {response.status_code}"
                )
            
            print(f"[RemoteVideo] Connected successfully")
            
            # Buffer for accumulating MJPEG data
            buffer = b''
            
            async for chunk in response.aiter_bytes():
                buffer += chunk
                
                # Look for JPEG boundaries
                start = buffer.find(b'\xff\xd8')  # JPEG start
                end = buffer.find(b'\xff\xd9')    # JPEG end
                
                if start != -1 and end != -1 and end > start:
                    # Extract JPEG frame
                    frame_bytes = buffer[start:end+2]
                    buffer = buffer[end+2:]
                    
                    try:
                        # Decode JPEG to numpy array
                        nparr = np.frombuffer(frame_bytes, np.uint8)
                        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                        
                        if frame is not None:
                            # Add to video buffer for clip extraction
                            video_buffer.add_frame(frame, datetime.utcnow())
                            
                            # Process through AI if enabled
                            if process_ai:
                                timestamp_ms = time.time() * 1000
                                await frame_processor.submit_frame(frame_bytes, timestamp_ms)
                            
                            # Re-encode and yield frame
                            _, buffer_encoded = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                            frame_bytes = buffer_encoded.tobytes()
                            
                            yield (
                                b'--frame\r\n'
                                b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n'
                            )
                            
                            frame_number += 1
                            
                            # Control frame rate (30 fps)
                            await asyncio.sleep(1 / 30)
                    
                    except Exception as e:
                        print(f"[RemoteVideo] Error processing frame: {e}")
                        continue
    
    except httpx.HTTPError as e:
        print(f"[RemoteVideo] HTTP error: {e}")
        raise HTTPException(status_code=502, detail=f"Failed to connect to remote camera: {str(e)}")
    except Exception as e:
        print(f"[RemoteVideo] Error: {e}")
        raise HTTPException(status_code=500, detail=f"Error streaming remote video: {str(e)}")


@router.get("/stream")
async def stream_remote_video(
    url: str = Query(..., description="Remote camera MJPEG stream URL"),
    ai: bool = Query(True, description="Enable AI processing")
):
    """
    Stream video from remote camera with optional AI processing.
    
    This endpoint:
    1. Fetches frames from remote MJPEG stream
    2. Adds frames to video buffer (for clip extraction)
    3. Processes frames through AI (if enabled)
    4. Re-streams to frontend
    
    Example:
        /remote-video/stream?url=https://skyla-nonpercussive-odette.ngrok-free.dev/video_feed&ai=true
    """
    print(f"[RemoteVideo] Stream requested - url={url}, ai={ai}")
    
    return StreamingResponse(
        fetch_and_process_remote_stream(url, process_ai=ai),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )


@router.get("/test")
async def test_remote_connection(
    url: str = Query(..., description="Remote camera URL to test")
):
    """
    Test connection to remote camera.
    
    Returns status and basic info about the remote stream.
    """
    client = await get_remote_client()
    
    try:
        # Try to fetch first frame
        response = await client.get(url, timeout=10.0)
        
        if response.status_code == 200:
            return {
                "status": "connected",
                "url": url,
                "content_type": response.headers.get("content-type"),
                "message": "Remote camera is accessible"
            }
        else:
            return {
                "status": "error",
                "url": url,
                "status_code": response.status_code,
                "message": f"Remote camera returned status {response.status_code}"
            }
    
    except Exception as e:
        return {
            "status": "error",
            "url": url,
            "message": f"Failed to connect: {str(e)}"
        }


async def cleanup_remote_client():
    """Cleanup remote client on shutdown"""
    global remote_client
    if remote_client is not None:
        await remote_client.aclose()
        remote_client = None
