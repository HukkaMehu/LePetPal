"""
Quick test for camera index 1 (external USB webcam)
"""
import cv2
import time

print("Testing Camera 1 (External USB Webcam)")
print("=" * 50)

# Open camera 1
cap = cv2.VideoCapture(1)

if not cap.isOpened():
    print("❌ Camera 1 could not be opened!")
    print("\nTroubleshooting:")
    print("1. Make sure your external USB webcam is plugged in")
    print("2. Try unplugging and replugging the USB cable")
    print("3. Check if another app is using the camera")
    exit(1)

print("✅ Camera 1 opened successfully!")

# Get camera properties
width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
fps = cap.get(cv2.CAP_PROP_FPS)

print(f"\nCamera Properties:")
print(f"  Resolution: {int(width)}x{int(height)}")
print(f"  FPS: {fps}")

# Try to capture 5 frames
print(f"\nCapturing 5 test frames...")
success_count = 0

for i in range(5):
    ret, frame = cap.read()
    if ret and frame is not None:
        success_count += 1
        print(f"  Frame {i+1}: ✅ Captured ({frame.shape[1]}x{frame.shape[0]})")
    else:
        print(f"  Frame {i+1}: ❌ Failed")
    time.sleep(0.1)

cap.release()

print(f"\nResult: {success_count}/5 frames captured successfully")

if success_count == 5:
    print("\n✅ Camera 1 is working perfectly!")
    print("   Your external USB webcam is ready to stream.")
else:
    print("\n⚠️  Camera 1 has issues capturing frames")
    print("   Try using camera index 0 instead")
