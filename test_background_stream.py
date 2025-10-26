"""
Test the background stream functionality
Run this after restarting the backend with the new background stream code
"""
import requests
import time

print("Testing Background Stream Manager")
print("=" * 50)

# Wait a moment for backend to start
print("\nWaiting 5 seconds for background stream to initialize...")
time.sleep(5)

# Check background stream status
print("\nChecking background stream status...")
try:
    response = requests.get('http://localhost:8000/api/debug/background-stream-status')
    status = response.json()
    
    print(f"Stream running: {status['stream_running']}")
    print(f"Buffer frames: {status['buffer']['frame_count']}")
    print(f"Buffer duration: {status['buffer']['duration_seconds']:.1f}s")
    
    if status['stream_running'] and status['buffer']['frame_count'] > 0:
        print("\n✅ Background stream is working!")
    elif status['stream_running']:
        print("\n⚠️  Stream is running but buffer is still filling...")
    else:
        print("\n❌ Background stream is not running")
        
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("Make sure the backend is running with the updated code")

# Wait and check again
print("\nWaiting 10 more seconds...")
time.sleep(10)

print("\nChecking buffer again...")
try:
    response = requests.get('http://localhost:8000/video/buffer/status')
    buffer = response.json()
    
    print(f"Buffer frames: {buffer['frame_count']}")
    print(f"Buffer duration: {buffer['duration_seconds']:.1f}s")
    print(f"Oldest frame: {buffer['oldest_frame']}")
    print(f"Newest frame: {buffer['newest_frame']}")
    
    if buffer['frame_count'] > 100:
        print("\n✅ Buffer is filling nicely!")
        
        # Try creating a clip
        print("\nTesting clip creation...")
        from datetime import datetime, timedelta
        
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(seconds=5)
        
        clip_data = {
            'start_ts': start_time.isoformat() + 'Z',
            'duration_ms': 5000,
            'labels': ['background_stream_test']
        }
        
        response = requests.post('http://localhost:8000/api/clips', json=clip_data)
        clip = response.json()
        print(f"Clip created: {clip['id']}")
        
        # Wait for processing
        time.sleep(8)
        
        # Check result
        response = requests.get(f"http://localhost:8000/api/clips/{clip['id']}")
        clip_status = response.json()
        
        # Check video size
        video_response = requests.head(clip_status['video_url'])
        video_size = int(video_response.headers.get('Content-Length', 0))
        
        print(f"Video size: {video_size:,} bytes")
        
        if video_size > 100000:  # > 100KB means real content
            print("✅ SUCCESS: Clip has real video content!")
        else:
            print("❌ FAILED: Clip is still a placeholder")
    else:
        print("\n⚠️  Buffer needs more time to fill")
        
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 50)
print("Test complete!")
print("\nTo use this feature:")
print("1. Restart the backend server")
print("2. The background stream will start automatically")
print("3. The buffer will stay filled even when not viewing the stream")
print("4. Clips will contain real video content")
