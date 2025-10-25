"""
Test frame extraction via HTTP API (same way Celery worker does it).
"""
import requests
from datetime import datetime, timedelta

def test_frame_api():
    """Test the frame extraction API endpoint."""
    print("\n🔍 Testing Frame Extraction API\n")
    
    # Get buffer status
    try:
        status_response = requests.get('http://localhost:8000/video/buffer/status', timeout=5)
        buffer_info = status_response.json()
        print("Buffer Status:")
        print(f"  Frame count: {buffer_info['frame_count']}")
        print(f"  Duration: {buffer_info['duration_seconds']:.2f} seconds")
        print(f"  Oldest: {buffer_info['oldest_frame']}")
        print(f"  Newest: {buffer_info['newest_frame']}")
    except Exception as e:
        print(f"❌ Failed to get buffer status: {e}")
        return
    
    if buffer_info['frame_count'] == 0:
        print("\n❌ Buffer is empty!")
        return
    
    # Calculate a time range (last 3 seconds)
    newest = datetime.fromisoformat(buffer_info['newest_frame'])
    start_time = newest - timedelta(seconds=3)
    end_time = newest
    
    print(f"\n📹 Requesting frames:")
    print(f"  Start: {start_time.isoformat()}")
    print(f"  End: {end_time.isoformat()}")
    
    # Request frames
    try:
        frames_response = requests.get(
            'http://localhost:8000/video/buffer/frames',
            params={
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat()
            },
            timeout=30
        )
        
        if frames_response.status_code == 200:
            frames_data = frames_response.json()
            frame_count = frames_data['count']
            
            print(f"\n✅ API returned {frame_count} frames!")
            
            if frame_count > 0:
                print(f"  First frame timestamp: {frames_data['frames'][0]['timestamp']}")
                print(f"  Last frame timestamp: {frames_data['frames'][-1]['timestamp']}")
                print(f"  Frame data size: {len(frames_data['frames'][0]['data'])} bytes (base64)")
            else:
                print("\n⚠️ API returned 0 frames!")
                print("This is the problem - Celery worker gets no frames and creates placeholders")
        else:
            print(f"\n❌ API error: {frames_response.status_code}")
            print(f"  Response: {frames_response.text}")
    except Exception as e:
        print(f"\n❌ Failed to fetch frames: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_frame_api()
