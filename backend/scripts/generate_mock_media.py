"""
Generate mock media files for demo mode.
Creates placeholder images for snapshots and clips.
"""
import sys
import os
from pathlib import Path
import cv2
import numpy as np
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def create_mock_snapshot(output_path: str, label: str = "Demo Snapshot"):
    """Create a mock snapshot image."""
    # Create a 640x480 image
    width, height = 640, 480
    img = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Create gradient background
    for i in range(height):
        img[i, :] = [int(100 + 155 * i / height), 80, int(200 - 100 * i / height)]
    
    # Add a "dog" silhouette (simple oval)
    center_x, center_y = width // 2, height // 2 + 50
    cv2.ellipse(img, (center_x, center_y), (120, 80), 0, 0, 360, (139, 69, 19), -1)
    
    # Add "head"
    cv2.circle(img, (center_x, center_y - 60), 50, (139, 69, 19), -1)
    
    # Add "ears"
    cv2.ellipse(img, (center_x - 40, center_y - 80), (20, 30), -30, 0, 360, (101, 67, 33), -1)
    cv2.ellipse(img, (center_x + 40, center_y - 80), (20, 30), 30, 0, 360, (101, 67, 33), -1)
    
    # Add label text
    cv2.putText(
        img,
        label,
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (255, 255, 255),
        2
    )
    
    # Add timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cv2.putText(
        img,
        timestamp,
        (20, height - 20),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        1
    )
    
    # Save image
    cv2.imwrite(output_path, img)


def create_mock_clip_preview(output_path: str, label: str = "Demo Clip"):
    """Create a mock clip preview image."""
    # Create a 640x480 image
    width, height = 640, 480
    img = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Create gradient background
    for i in range(height):
        img[i, :] = [int(50 + 100 * i / height), int(100 + 50 * i / height), 150]
    
    # Add a "dog in motion" representation
    center_x, center_y = width // 2 + 50, height // 2
    
    # Draw motion blur effect (multiple overlapping shapes)
    for offset in range(0, 60, 15):
        alpha = 0.3 + (offset / 60) * 0.7
        color = tuple(int(c * alpha) for c in (139, 69, 19))
        cv2.ellipse(img, (center_x - offset, center_y), (100, 60), 0, 0, 360, color, -1)
    
    # Add play button overlay
    play_center = (width // 2, height // 2)
    cv2.circle(img, play_center, 50, (255, 255, 255), 3)
    
    # Draw triangle (play icon)
    triangle_pts = np.array([
        [play_center[0] - 15, play_center[1] - 25],
        [play_center[0] - 15, play_center[1] + 25],
        [play_center[0] + 25, play_center[1]]
    ], np.int32)
    cv2.fillPoly(img, [triangle_pts], (255, 255, 255))
    
    # Add label text
    cv2.putText(
        img,
        label,
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (255, 255, 255),
        2
    )
    
    # Add duration
    cv2.putText(
        img,
        "10s",
        (width - 80, height - 20),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 255),
        2
    )
    
    # Save image
    cv2.imwrite(output_path, img)


def create_mock_video(output_path: str, duration_sec: int = 10, fps: int = 30):
    """Create a mock video file."""
    width, height = 640, 480
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    total_frames = duration_sec * fps
    
    for frame_num in range(total_frames):
        # Create frame
        img = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Gradient background
        for i in range(height):
            img[i, :] = [int(100 + 155 * i / height), 80, int(200 - 100 * i / height)]
        
        # Animated dog position
        progress = frame_num / total_frames
        center_x = int(width * 0.3 + width * 0.4 * progress)
        center_y = height // 2 + int(30 * np.sin(progress * 4 * np.pi))
        
        # Draw dog
        cv2.ellipse(img, (center_x, center_y), (100, 60), 0, 0, 360, (139, 69, 19), -1)
        cv2.circle(img, (center_x, center_y - 50), 40, (139, 69, 19), -1)
        
        # Add frame counter
        cv2.putText(
            img,
            f"Frame {frame_num}/{total_frames}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )
        
        out.write(img)
    
    out.release()


def generate_mock_media():
    """Generate all mock media files."""
    print("\n🎬 Generating mock media files...\n")
    
    # Create output directories
    base_dir = Path(__file__).parent.parent / "mock_media"
    snapshots_dir = base_dir / "snapshots"
    clips_dir = base_dir / "clips"
    
    snapshots_dir.mkdir(parents=True, exist_ok=True)
    clips_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate snapshots
    snapshot_labels = [
        "Sleeping",
        "Playing",
        "Sitting",
        "Alert",
        "Eating",
        "Portrait",
        "Good Boy!",
        "Training",
    ]
    
    print("Creating mock snapshots...")
    for i, label in enumerate(snapshot_labels):
        output_path = str(snapshots_dir / f"snapshot_{i+1}.jpg")
        create_mock_snapshot(output_path, label)
        print(f"  ✓ Created {output_path}")
    
    # Generate clip previews
    clip_labels = [
        "Fetch Success",
        "Sit Training",
        "Play Time",
        "Treat Reward",
        "Bark Alert",
        "Zoomies!",
    ]
    
    print("\nCreating mock clip previews...")
    for i, label in enumerate(clip_labels):
        output_path = str(clips_dir / f"clip_{i+1}_preview.jpg")
        create_mock_clip_preview(output_path, label)
        print(f"  ✓ Created {output_path}")
    
    # Generate a sample video
    print("\nCreating mock video...")
    video_path = str(clips_dir / "sample_clip.mp4")
    create_mock_video(video_path, duration_sec=10, fps=30)
    print(f"  ✓ Created {video_path}")
    
    print(f"\n✅ Mock media generation completed!")
    print(f"   Snapshots: {snapshots_dir}")
    print(f"   Clips: {clips_dir}\n")


if __name__ == "__main__":
    generate_mock_media()
