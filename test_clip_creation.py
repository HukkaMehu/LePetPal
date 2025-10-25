"""Test clip creation directly"""
import requests
from datetime import datetime, timedelta

# Get buffer status first
print("1. Checking buffer status...")
try:
    response = requests.get('http://localhost:8000/video/buffer/status', timeout=10)
    buffer_info = response.json()
    print(f"   Buffer has {buffer_info['frame_count']} frames")
    print(f"   Duration: {buffer_info['duration_seconds']:.1f} seconds")
    
    if buffer_info['frame_count'] == 0:
        print("   ❌ Buffer is empty! Open Live page first.")
        exit(1)
    
    # Calculate a time range for the clip (last 3 seconds)
    newest = datetime.fromisoformat(buffer_info['newest_frame'])
    start_time = newest - timedelta(seconds=3)
    
    print(f"\n2. Creating clip...")
    print(f"   Start: {start_time.isoformat()}")
    print(f"   Duration: 3000ms")
    
    # Create clip
    clip_response = requests.post(
        'http://localhost:8000/api/clips',
        json={
            'start_ts': start_time.isoformat(),
            'duration_ms': 3000,
            'labels': ['test']
        },
        timeout=10
    )
    
    if clip_response.status_code == 202:
        clip_data = clip_response.json()
        clip_id = clip_data['id']
        print(f"   ✅ Clip created: {clip_id}")
        print(f"   Status: {clip_data['status']}")
        
        # Wait a moment for processing
        import time
        print("\n3. Waiting 5 seconds for processing...")
        time.sleep(5)
        
        # Check clip status
        print("\n4. Checking clip status...")
        status_response = requests.get(f'http://localhost:8000/api/clips/{clip_id}')
        status_data = status_response.json()
        print(f"   Status: {status_data['status']}")
        print(f"   Video URL: {status_data.get('video_url', 'None')}")
        
        if status_data['status'] == 'completed':
            print("\n   ✅ SUCCESS! Clip processed with real frames!")
        else:
            print("\n   ⚠️ Still processing or failed")
    else:
        print(f"   ❌ Failed to create clip: {clip_response.status_code}")
        print(f"   Response: {clip_response.text}")
        
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()
