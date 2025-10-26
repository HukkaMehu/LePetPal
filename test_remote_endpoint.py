"""
Quick test to verify the remote video endpoint works
"""
import requests
import time

# Test the remote video endpoint
remote_url = "http://localhost:8000/api/remote-video/stream?url=https://lepetpal.verkkoventure.com/camera&ai=true"

print(f"Testing remote video endpoint: {remote_url}")
print("This should stream frames from the remote camera...")
print("Press Ctrl+C to stop\n")

try:
    response = requests.get(remote_url, stream=True, timeout=10)
    
    if response.status_code == 200:
        print("✅ Connected successfully!")
        print(f"Content-Type: {response.headers.get('content-type')}")
        
        # Read first few frames
        frame_count = 0
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                frame_count += 1
                if frame_count % 10 == 0:
                    print(f"Received {frame_count} frame chunks...")
                if frame_count >= 30:  # Stop after ~1 second
                    break
        
        print(f"\n✅ Successfully received {frame_count} frame chunks from remote camera!")
        print("The remote video endpoint is working correctly.")
    else:
        print(f"❌ Error: Status code {response.status_code}")
        print(f"Response: {response.text}")

except requests.exceptions.Timeout:
    print("❌ Connection timeout - is the backend running?")
except requests.exceptions.ConnectionError:
    print("❌ Connection error - is the backend running on localhost:8000?")
except KeyboardInterrupt:
    print("\n\nTest stopped by user")
except Exception as e:
    print(f"❌ Error: {e}")
