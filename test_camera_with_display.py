"""
Test if the remote camera is actually streaming video
This will try to display the first frame
"""
import cv2
import numpy as np
from PIL import Image
import io

camera_url = "https://lepetpal.verkkoventure.com/camera"

print(f"Testing camera: {camera_url}")
print("Attempting to open video stream...\n")

# Try with OpenCV
cap = cv2.VideoCapture(camera_url)

if not cap.isOpened():
    print("❌ OpenCV failed to open the stream")
    print("This is expected for HTTPS MJPEG streams\n")
else:
    print("✅ OpenCV opened the stream")
    ret, frame = cap.read()
    if ret:
        print(f"✅ Successfully read frame: {frame.shape}")
        cv2.imwrite("test_frame.jpg", frame)
        print("✅ Saved frame to test_frame.jpg")
    else:
        print("❌ Failed to read frame")
    cap.release()

# Try with httpx (better for HTTPS)
print("\n" + "="*50)
print("Testing with httpx (better for HTTPS streams)...\n")

import httpx
import asyncio

async def test_with_httpx():
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            print(f"Connecting to {camera_url}...")
            async with client.stream('GET', camera_url) as response:
                print(f"Status: {response.status_code}")
                print(f"Content-Type: {response.headers.get('content-type')}")
                
                if response.status_code != 200:
                    print(f"❌ Bad status code: {response.status_code}")
                    return
                
                print("\n✅ Connected! Reading frames...\n")
                
                # Buffer for MJPEG parsing
                buffer = b''
                frame_count = 0
                
                async for chunk in response.aiter_bytes():
                    buffer += chunk
                    
                    # Look for JPEG boundaries
                    start = buffer.find(b'\xff\xd8')  # JPEG start
                    end = buffer.find(b'\xff\xd9')    # JPEG end
                    
                    if start != -1 and end != -1 and end > start:
                        # Extract JPEG frame
                        frame_bytes = buffer[start:end+2]
                        buffer = buffer[end+2:]
                        
                        frame_count += 1
                        print(f"Frame {frame_count}: {len(frame_bytes)} bytes")
                        
                        # Try to decode and save first frame
                        if frame_count == 1:
                            try:
                                nparr = np.frombuffer(frame_bytes, np.uint8)
                                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                                if frame is not None:
                                    cv2.imwrite("test_frame_httpx.jpg", frame)
                                    print(f"✅ Saved first frame to test_frame_httpx.jpg")
                                    print(f"   Frame size: {frame.shape}")
                                else:
                                    print("❌ Failed to decode frame")
                            except Exception as e:
                                print(f"❌ Error decoding frame: {e}")
                        
                        # Stop after 5 frames
                        if frame_count >= 5:
                            print(f"\n✅ Successfully received {frame_count} frames!")
                            print("The camera stream is working.")
                            break
                            
        except httpx.HTTPError as e:
            print(f"❌ HTTP Error: {e}")
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

asyncio.run(test_with_httpx())
