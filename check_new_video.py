"""Check the new H.264 video"""
import cv2
import requests

# Download new video
print("Downloading new video...")
url = "http://localhost:9000/dog-monitor/clips/00000000-0000-0000-0000-000000000000/20251026_080003_clip.mp4"
response = requests.get(url)
with open('test_video_new.mp4', 'wb') as f:
    f.write(response.content)

print(f"Downloaded {len(response.content):,} bytes")

# Check with OpenCV
cap = cv2.VideoCapture('test_video_new.mp4')

if not cap.isOpened():
    print("❌ OpenCV cannot open the video file")
else:
    print("✅ OpenCV can open the video")
    
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = int(cap.get(cv2.CAP_PROP_FOURCC))
    fourcc_str = fourcc.to_bytes(4, 'little').decode('ascii', errors='ignore')
    
    print(f"Frame count: {frame_count}")
    print(f"FPS: {fps}")
    print(f"Resolution: {width}x{height}")
    print(f"FourCC: {fourcc_str}")
    print(f"Duration: {frame_count/fps:.1f} seconds")
    
    # Try to read frames
    ret, frame = cap.read()
    if ret:
        print(f"✅ Can read frames")
    else:
        print("❌ Cannot read frames")
    
    cap.release()

# Check file header
with open('test_video_new.mp4', 'rb') as f:
    header = f.read(32)
    print(f"\nFile header: {header[:20]}")
    
    # Look for codec info
    f.seek(0)
    data = f.read(1000)
    if b'avc1' in data:
        print("✅ Contains 'avc1' (H.264) marker")
    if b'mp4v' in data:
        print("⚠️  Contains 'mp4v' marker")
