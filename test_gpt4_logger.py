"""
Test if the GPT-4 Vision logger can fetch frames from the remote camera
"""
import cv2
import httpx
import numpy as np

camera_url = "https://lepetpal.verkkoventure.com/camera"

print(f"Testing GPT-4 logger frame capture from: {camera_url}\n")

# Test the capture_frame logic
try:
    print("Fetching frame using httpx...")
    with httpx.Client(timeout=10.0) as client:
        response = client.get(camera_url, follow_redirects=True)
        
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type')}")
        
        if response.status_code == 200:
            content = response.content
            print(f"Content length: {len(content)} bytes")
            
            # Look for JPEG boundaries
            start = content.find(b'\xff\xd8')  # JPEG start
            end = content.find(b'\xff\xd9')    # JPEG end
            
            print(f"JPEG start marker at: {start}")
            print(f"JPEG end marker at: {end}")
            
            if start != -1 and end != -1:
                frame_bytes = content[start:end+2]
                print(f"Extracted frame: {len(frame_bytes)} bytes")
                
                nparr = np.frombuffer(frame_bytes, np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                if frame is not None:
                    print(f"✅ Successfully decoded frame: {frame.shape}")
                    cv2.imwrite("gpt4_test_frame.jpg", frame)
                    print("✅ Saved to gpt4_test_frame.jpg")
                    
                    # Check if frame is black
                    mean_brightness = frame.mean()
                    print(f"Frame mean brightness: {mean_brightness:.2f}")
                    
                    if mean_brightness < 10:
                        print("⚠️  Frame appears to be black!")
                    else:
                        print("✅ Frame has content!")
                else:
                    print("❌ Failed to decode frame")
            else:
                print("❌ Could not find JPEG boundaries")
                print(f"First 100 bytes: {content[:100]}")
        else:
            print(f"❌ Bad status code: {response.status_code}")
            
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("If this works, the stream_activity_logger should work too.")
print("Run: python stream_activity_logger.py")
