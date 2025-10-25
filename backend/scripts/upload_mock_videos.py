"""
Upload mock video files to MinIO for seeded clips.
This script creates simple video files and uploads them to match the seeded clip URIs.
"""
import sys
import os
from pathlib import Path
from datetime import datetime
import io

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.storage import storage_service
from app.db.base import SessionLocal
from app.models.clip import Clip
from sqlalchemy import select

try:
    import cv2
    import numpy as np
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False
    print("⚠️  OpenCV not installed. Will create minimal placeholder files.")


def create_simple_video_bytes(duration_sec: int = 10) -> bytes:
    """Create a simple video file as bytes."""
    if HAS_CV2:
        # Create actual video with OpenCV
        width, height = 640, 480
        fps = 30
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        
        # Write to memory buffer
        temp_path = "temp_video.mp4"
        out = cv2.VideoWriter(temp_path, fourcc, fps, (width, height))
        
        total_frames = duration_sec * fps
        for frame_num in range(total_frames):
            # Create simple animated frame
            img = np.zeros((height, width, 3), dtype=np.uint8)
            
            # Gradient background
            for i in range(height):
                img[i, :] = [int(100 + 155 * i / height), 80, int(200 - 100 * i / height)]
            
            # Moving circle
            progress = frame_num / total_frames
            center_x = int(width * 0.2 + width * 0.6 * progress)
            center_y = height // 2
            cv2.circle(img, (center_x, center_y), 50, (139, 69, 19), -1)
            
            # Frame counter
            cv2.putText(img, f"{frame_num}/{total_frames}", (20, 40),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            out.write(img)
        
        out.release()
        
        # Read file and delete
        with open(temp_path, 'rb') as f:
            video_bytes = f.read()
        os.remove(temp_path)
        
        return video_bytes
    else:
        # Create minimal MP4 placeholder
        # This is a minimal valid MP4 file structure
        return b'\x00\x00\x00\x20ftypisom\x00\x00\x02\x00isomiso2mp41\x00\x00\x00\x08free'


def create_simple_preview_bytes() -> bytes:
    """Create a simple preview image as bytes."""
    if HAS_CV2:
        # Create actual image with OpenCV
        width, height = 640, 480
        img = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Gradient background
        for i in range(height):
            img[i, :] = [int(100 + 155 * i / height), 80, int(200 - 100 * i / height)]
        
        # Add text
        cv2.putText(img, "Demo Clip Preview", (width//2 - 150, height//2),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # Encode to JPEG
        _, buffer = cv2.imencode('.jpg', img)
        return buffer.tobytes()
    else:
        # Create minimal JPEG placeholder (1x1 pixel)
        return b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xc4\x00\xb5\x10\x00\x02\x01\x03\x03\x02\x04\x03\x05\x05\x04\x04\x00\x00\x01}\x01\x02\x03\x00\x04\x11\x05\x12!1A\x06\x13Qa\x07"q\x142\x81\x91\xa1\x08#B\xb1\xc1\x15R\xd1\xf0$3br\x82\t\n\x16\x17\x18\x19\x1a%&\'()*456789:CDEFGHIJSTUVWXYZcdefghijstuvwxyz\x83\x84\x85\x86\x87\x88\x89\x8a\x92\x93\x94\x95\x96\x97\x98\x99\x9a\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xff\xda\x00\x08\x01\x01\x00\x00?\x00\xfe\xfe\x8a(\xa0\x0f\xff\xd9'


def upload_mock_videos_for_clips():
    """Upload mock videos for all seeded clips in the database."""
    print("\n🎬 Uploading mock videos for seeded clips...\n")
    
    db = SessionLocal()
    try:
        # Get all clips from database
        clips = db.query(Clip).all()
        
        if not clips:
            print("No clips found in database. Run seed_database.py first.")
            return
        
        print(f"Found {len(clips)} clips in database")
        
        uploaded_count = 0
        skipped_count = 0
        
        for clip in clips:
            # Extract object key from S3 URI
            if not clip.s3_uri or clip.s3_uri == "pending":
                print(f"  ⏭️  Skipping clip {clip.id} (no S3 URI)")
                skipped_count += 1
                continue
            
            video_key = clip.s3_uri.replace(f"s3://{storage_service.bucket_name}/", "")
            
            # Check if file already exists (optional - comment out to always upload)
            # try:
            #     storage_service.s3_client.head_object(Bucket=storage_service.bucket_name, Key=video_key)
            #     print(f"  ✓ Video already exists: {video_key}")
            #     skipped_count += 1
            #     continue
            # except:
            #     pass
            
            # Create and upload video
            duration_sec = max(5, min(15, clip.duration_ms // 1000))  # 5-15 seconds
            video_bytes = create_simple_video_bytes(duration_sec)
            
            try:
                storage_service.upload_file(
                    file_data=video_bytes,
                    object_key=video_key,
                    content_type="video/mp4"
                )
                print(f"  ✓ Uploaded video: {video_key}")
                uploaded_count += 1
            except Exception as e:
                print(f"  ❌ Failed to upload {video_key}: {e}")
            
            # Upload preview if it doesn't exist
            if clip.preview_png:
                preview_key = clip.preview_png.replace(f"s3://{storage_service.bucket_name}/", "")
                preview_bytes = create_simple_preview_bytes()
                
                try:
                    storage_service.upload_file(
                        file_data=preview_bytes,
                        object_key=preview_key,
                        content_type="image/jpeg"
                    )
                    print(f"  ✓ Uploaded preview: {preview_key}")
                except Exception as e:
                    print(f"  ❌ Failed to upload preview {preview_key}: {e}")
        
        print(f"\n✅ Upload complete!")
        print(f"   Uploaded: {uploaded_count} videos")
        print(f"   Skipped: {skipped_count} clips")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    upload_mock_videos_for_clips()
