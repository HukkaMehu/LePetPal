"""
Test video buffer frame extraction.
"""
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.video_buffer import video_buffer


def test_buffer_extraction():
    """Test extracting frames from the buffer."""
    print("\n🔍 Testing Video Buffer Extraction\n")
    
    # Get buffer info
    info = video_buffer.get_buffer_info()
    print("Buffer Status:")
    print(f"  Frame count: {info['frame_count']}")
    print(f"  Duration: {info['duration_seconds']:.2f} seconds")
    print(f"  Oldest frame: {info['oldest_frame']}")
    print(f"  Newest frame: {info['newest_frame']}")
    
    if info['frame_count'] == 0:
        print("\n❌ Buffer is empty!")
        print("Make sure:")
        print("  1. Backend is running")
        print("  2. Video stream is active (open Live page)")
        print("  3. Wait 10-15 seconds for buffer to fill")
        return
    
    # Try to extract frames from the middle of the buffer
    oldest = datetime.fromisoformat(info['oldest_frame'])
    newest = datetime.fromisoformat(info['newest_frame'])
    
    # Get 5 seconds from the middle
    middle = oldest + (newest - oldest) / 2
    start_time = middle - timedelta(seconds=2.5)
    end_time = middle + timedelta(seconds=2.5)
    
    print(f"\n📹 Extracting frames:")
    print(f"  Start: {start_time}")
    print(f"  End: {end_time}")
    
    frames = video_buffer.get_frames(start_time, end_time)
    
    if frames:
        print(f"\n✅ Extracted {len(frames)} frames!")
        print(f"  First frame: {frames[0][0]}")
        print(f"  Last frame: {frames[-1][0]}")
        print(f"  Frame shape: {frames[0][1].shape}")
        
        # Calculate FPS
        duration = (frames[-1][0] - frames[0][0]).total_seconds()
        fps = len(frames) / duration if duration > 0 else 0
        print(f"  Effective FPS: {fps:.1f}")
    else:
        print(f"\n❌ No frames extracted!")
        print("This shouldn't happen if the time range is within the buffer.")
    
    # Test with a recent time range (last 3 seconds)
    print(f"\n📹 Testing with recent frames (last 3 seconds):")
    recent_start = newest - timedelta(seconds=3)
    recent_end = newest
    
    print(f"  Start: {recent_start}")
    print(f"  End: {recent_end}")
    
    recent_frames = video_buffer.get_frames(recent_start, recent_end)
    
    if recent_frames:
        print(f"\n✅ Extracted {len(recent_frames)} recent frames!")
    else:
        print(f"\n❌ No recent frames extracted!")


if __name__ == "__main__":
    test_buffer_extraction()
