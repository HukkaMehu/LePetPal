"""Test if H.264 codec is available"""
import cv2
import numpy as np
import tempfile

# Test different codecs
codecs_to_test = [
    ('avc1', 'H.264'),
    ('h264', 'H.264 alt'),
    ('x264', 'x264'),
    ('H264', 'H264 caps'),
    ('mp4v', 'MPEG-4'),
]

print("Testing codec availability:\n")

for fourcc_str, name in codecs_to_test:
    try:
        fourcc = cv2.VideoWriter_fourcc(*fourcc_str)
        temp_file = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
        temp_path = temp_file.name
        temp_file.close()
        
        out = cv2.VideoWriter(temp_path, fourcc, 30, (640, 480))
        
        if out.isOpened():
            # Try to write a frame
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            out.write(frame)
            out.release()
            
            # Try to read it back
            cap = cv2.VideoCapture(temp_path)
            if cap.isOpened():
                ret, _ = cap.read()
                cap.release()
                if ret:
                    print(f"✅ {fourcc_str:6s} ({name:15s}) - WORKS")
                else:
                    print(f"⚠️  {fourcc_str:6s} ({name:15s}) - Can write but not read")
            else:
                print(f"⚠️  {fourcc_str:6s} ({name:15s}) - Can write but not open")
        else:
            print(f"❌ {fourcc_str:6s} ({name:15s}) - Cannot open writer")
            
        import os
        try:
            os.unlink(temp_path)
        except:
            pass
            
    except Exception as e:
        print(f"❌ {fourcc_str:6s} ({name:15s}) - Error: {e}")

print("\nNote: For web playback, we need H.264 (avc1) codec")
