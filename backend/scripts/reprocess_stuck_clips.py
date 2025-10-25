"""
Reprocess clips that are stuck in 'processing' status.
This script finds clips with s3_uri='pending' and requeues them for processing.
"""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.base import SessionLocal
from app.models.clip import Clip
from app.workers.clip_processor import process_clip_task


def reprocess_stuck_clips():
    """Find and reprocess clips stuck in processing status."""
    print("\n🔄 Reprocessing stuck clips...\n")
    
    db = SessionLocal()
    try:
        # Find clips with pending status
        stuck_clips = db.query(Clip).filter(Clip.s3_uri == "pending").all()
        
        if not stuck_clips:
            print("✅ No stuck clips found. All clips are processed!")
            return
        
        print(f"Found {len(stuck_clips)} stuck clips\n")
        
        requeued_count = 0
        
        for clip in stuck_clips:
            print(f"📹 Clip {clip.id}")
            print(f"   Start: {clip.start_ts}")
            print(f"   Duration: {clip.duration_ms}ms")
            print(f"   Labels: {clip.labels}")
            
            try:
                # Requeue the clip for processing
                task = process_clip_task.delay(
                    clip_id=str(clip.id),
                    user_id=str(clip.user_id),
                    start_ts=clip.start_ts.isoformat(),
                    duration_ms=clip.duration_ms,
                    labels=clip.labels
                )
                
                print(f"   ✓ Requeued (task ID: {task.id})")
                requeued_count += 1
                
            except Exception as e:
                print(f"   ❌ Failed to requeue: {e}")
            
            print()
        
        print(f"\n✅ Requeued {requeued_count} clips for processing")
        print("\nMake sure Celery worker is running:")
        print("  celery -A app.core.celery_app worker --loglevel=info --pool=solo")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    reprocess_stuck_clips()
