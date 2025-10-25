"""
Quick test script to check if your webcam is accessible.
Run this before starting the backend to verify camera setup.
"""
import cv2
import sys

def test_webcam(camera_index=0):
    """Test if webcam at given index is accessible."""
    print(f"Testing camera index {camera_index}...")
    
    cap = cv2.VideoCapture(camera_index)
    
    if not cap.isOpened():
        print(f"❌ Camera {camera_index} could not be opened")
        return False
    
    print(f"✅ Camera {camera_index} opened successfully")
    
    # Try to read a frame
    ret, frame = cap.read()
    
    if not ret or frame is None:
        print(f"❌ Could not read frame from camera {camera_index}")
        cap.release()
        return False
    
    print(f"✅ Frame captured successfully")
    print(f"   Resolution: {frame.shape[1]}x{frame.shape[0]}")
    print(f"   Channels: {frame.shape[2]}")
    
    # Get camera properties
    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    print(f"   Camera properties:")
    print(f"     - Width: {width}")
    print(f"     - Height: {height}")
    print(f"     - FPS: {fps}")
    
    cap.release()
    return True


def find_all_cameras():
    """Find all available cameras."""
    print("\nScanning for available cameras...")
    available = []
    
    for i in range(10):  # Check first 10 indices
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            ret, _ = cap.read()
            if ret:
                available.append(i)
                print(f"✅ Camera found at index {i}")
            cap.release()
    
    return available


if __name__ == "__main__":
    print("=" * 50)
    print("Webcam Test Script")
    print("=" * 50)
    
    # Find all cameras
    cameras = find_all_cameras()
    
    if not cameras:
        print("\n❌ No cameras found!")
        print("\nTroubleshooting:")
        print("1. Make sure your webcam is connected")
        print("2. Close other apps that might be using the camera")
        print("3. Check camera permissions in your system settings")
        sys.exit(1)
    
    print(f"\n✅ Found {len(cameras)} camera(s): {cameras}")
    
    # Test default camera (index 0)
    print("\n" + "=" * 50)
    print("Testing default camera (index 0)")
    print("=" * 50)
    
    if 0 in cameras:
        success = test_webcam(0)
        if success:
            print("\n✅ Your webcam is ready to use!")
            print("   Start the backend with: uvicorn app.main:app --reload")
        else:
            print("\n❌ Camera 0 failed detailed test")
    else:
        print("\n⚠️  Camera 0 not available")
        if cameras:
            print(f"   Try using camera index {cameras[0]} instead")
            print(f"   Update get_webcam_capture() in backend/app/api/video.py:")
            print(f"   Change: cv2.VideoCapture(0)")
            print(f"   To:     cv2.VideoCapture({cameras[0]})")
