"""Check video file properties"""
import cv2
import requests

# Download video
print("Downloading video...")
url = "http://localhost:9000/dog-monitor/clips/00000000-0000-0000-0000-000000000000/20251026_074925_clip.mp4"
response = requests.get(url)
with open('test_video.mp4', 'wb') as f:
    f.write(response.content)

print(f"Downloaded {len(response.content)} bytes")

# Try to open with OpenCV
cap = cv2.VideoCapture('test_video.mp4')

if not cap.isOpened():
    print("❌ OpenCV cannot open the video file")
else:
    print("✅ OpenCV can open the video")
    
    # Get video properties
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = int(cap.get(cv2.CAP_PROP_FOURCC))
    
    print(f"Frame count: {frame_count}")
    print(f"FPS: {fps}")
    print(f"Resolution: {width}x{height}")
    print(f"FourCC: {fourcc} ({fourcc.to_bytes(4, 'little').decode('ascii', errors='ignore')})")
    
    # Try to read first frame
    ret, frame = cap.read()
    if ret:
        print(f"✅ Can read frames (first frame shape: {frame.shape})")
    else:
        print("❌ Cannot read frames")
    
    cap.release()

# Check file header
with open('test_video.mp4', 'rb') as f:
    header = f.read(20)
    print(f"\nFile header (hex): {header.hex()}")
    print(f"File header (ascii): {header}")
