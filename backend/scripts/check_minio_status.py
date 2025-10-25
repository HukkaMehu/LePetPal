"""
Check MinIO status and list stored files.
"""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.storage import storage_service
from botocore.exceptions import ClientError


def check_minio_status():
    """Check MinIO connection and list files."""
    print("\n🔍 Checking MinIO Status...\n")
    
    # Check connection
    try:
        storage_service.s3_client.head_bucket(Bucket=storage_service.bucket_name)
        print(f"✅ Connected to MinIO")
        print(f"   Bucket: {storage_service.bucket_name}")
        print(f"   Endpoint: {storage_service.s3_client.meta.endpoint_url}")
    except ClientError as e:
        print(f"❌ Cannot connect to MinIO: {e}")
        print("\nMake sure MinIO is running:")
        print("  docker-compose up -d minio")
        return
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # List objects
    print(f"\n📁 Files in bucket '{storage_service.bucket_name}':\n")
    
    try:
        response = storage_service.s3_client.list_objects_v2(
            Bucket=storage_service.bucket_name
        )
        
        if 'Contents' not in response or len(response['Contents']) == 0:
            print("   (empty - no files uploaded yet)")
            print("\n💡 To upload mock videos, run:")
            print("   python backend/scripts/upload_mock_videos.py")
            return
        
        # Group by type
        clips = []
        snapshots = []
        other = []
        
        for obj in response['Contents']:
            key = obj['Key']
            size = obj['Size']
            modified = obj['LastModified']
            
            if 'clips/' in key:
                clips.append((key, size, modified))
            elif 'snapshots/' in key:
                snapshots.append((key, size, modified))
            else:
                other.append((key, size, modified))
        
        # Display clips
        if clips:
            print(f"📹 Clips ({len(clips)}):")
            for key, size, modified in clips[:10]:  # Show first 10
                size_kb = size / 1024
                print(f"   • {key} ({size_kb:.1f} KB) - {modified}")
            if len(clips) > 10:
                print(f"   ... and {len(clips) - 10} more")
        
        # Display snapshots
        if snapshots:
            print(f"\n📸 Snapshots ({len(snapshots)}):")
            for key, size, modified in snapshots[:10]:  # Show first 10
                size_kb = size / 1024
                print(f"   • {key} ({size_kb:.1f} KB) - {modified}")
            if len(snapshots) > 10:
                print(f"   ... and {len(snapshots) - 10} more")
        
        # Display other
        if other:
            print(f"\n📄 Other ({len(other)}):")
            for key, size, modified in other:
                size_kb = size / 1024
                print(f"   • {key} ({size_kb:.1f} KB) - {modified}")
        
        total_size = sum(obj['Size'] for obj in response['Contents'])
        print(f"\n📊 Total: {len(response['Contents'])} files, {total_size / 1024 / 1024:.2f} MB")
        
    except ClientError as e:
        print(f"❌ Error listing objects: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    check_minio_status()
