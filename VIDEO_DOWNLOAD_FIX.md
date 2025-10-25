# Video Download Fix

## Problem
Video clips were being downloaded as `.htm` files instead of proper video files. The issue occurred because:

1. The backend API was returning `s3_uri` (e.g., `s3://bucket/path/file.mp4`) as the video URL
2. The frontend was using this S3 URI directly for downloads
3. Browsers couldn't access S3 URIs directly, resulting in HTML error pages being downloaded

## Solution
Updated the clips API to generate presigned URLs for video downloads:

### Backend Changes (`backend/app/api/clips.py`)
1. Added `video_url` field to `ClipResponse` model
2. Generate presigned URLs for video files using `storage_service.get_presigned_url()`
3. Return both `s3_uri` (for internal reference) and `video_url` (for downloads)

### Frontend Changes
1. Updated `BackendClip` type to include `video_url` field (`Pet Training Web App/src/types/backend.ts`)
2. Modified `adaptClip()` function to use `video_url` instead of `s3_uri` (`Pet Training Web App/src/services/adapters.ts`)

## How It Works Now
1. Backend generates temporary presigned URLs that allow direct HTTP access to S3/MinIO objects
2. Frontend uses these presigned URLs for video playback and downloads
3. Downloads now work correctly with proper video file extensions and content

## Testing
After restarting the backend, video clips should:
- Play correctly in the gallery modal
- Download as proper `.mp4` files (or whatever format they were saved as)
- Have the correct MIME type and file extension
