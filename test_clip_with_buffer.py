"""
Test clip creation with active video buffer
"""
import requests
import time
from datetime import datetime, timedelta
import threading

def stream_video():
    """Keep video stream active to fill buffer"""
    try:
        response = requests.get('http://localhost:8000/video/mjpeg', stream=True, timeout=60)
        for chunk in response.iter_content(chunk_size=8192):
            pass
    except:
        pass

# Start video stream in background
print("Starting video stream...")
stream_thread = threading.Thread(target=stream_video, daemon=True)
stream_thread.start()

# Wait for buffer to fill
print("Waiting 10 seconds for buffer to fill...")
time.sleep(10)

# Check buffer status
buffer_status = requests.get('http://localhost:8000/video/buffer/status').json()
print(f"\nBuffer status:")
print(f"  Frames: {buffer_status['frame_count']}")
print(f"  Duration: {buffer_status['duration_seconds']:.1f} seconds")
print(f"  Oldest: {buffer_status['oldest_frame']}")
print(f"  Newest: {buffer_status['newest_frame']}")

# Create clip for last 5 seconds (should be in buffer)
end_time = datetime.utcnow()
start_time = end_time - timedelta(seconds=5)

clip_data = {
    'start_ts': start_time.isoformat() + 'Z',
    'duration_ms': 5000,
    'labels': ['buffer_test']
}

print(f"\nCreating 5-second clip from {start_time.strftime('%H:%M:%S')} to {end_time.strftime('%H:%M:%S')}...")
response = requests.post('http://localhost:8000/api/clips', json=clip_data)
clip = response.json()
print(f"Clip ID: {clip['id']}")
print(f"Status: {clip['status']}")

# Wait for processing
print("\nWaiting for clip processing...")
time.sleep(8)

# Check clip
clip_status = requests.get(f"http://localhost:8000/api/clips/{clip['id']}").json()
print(f"\nClip status: {clip_status['status']}")
print(f"Video URL: {clip_status['video_url']}")

# Check video size
video_response = requests.head(clip_status['video_url'])
video_size = int(video_response.headers.get('Content-Length', 0))
print(f"Video size: {video_size:,} bytes")

if video_size > 1000:
    print("✅ SUCCESS: Video has real content!")
else:
    print("❌ FAILED: Video is just a placeholder")

print("\nTest complete!")
