# Complete Gallery Fix Guide

## Issues Fixed in Code

### ✅ 1. Delete Functionality
- Added `deleteClip()` and `deleteSnapshot()` methods to API client
- Implemented actual delete handler in GalleryPage
- Gallery now refreshes after deletion

### ✅ 2. Video Duration Display
- Fixed duration showing 1000x too large (was showing milliseconds as seconds)
- Now correctly converts milliseconds to seconds: `Math.round(duration / 1000)`

### ✅ 3. Video URL Generation
- Backend now generates presigned URLs in `video_url` field
- Frontend uses `video_url` instead of `s3_uri` for playback and downloads

## Remaining Issue: Video Files Don't Exist

The main issue is that **seeded clips have fake S3 URIs** - the files don't actually exist in MinIO.

### Quick Fix Steps

#### Step 1: Check MinIO Status
```bash
python backend/scripts/check_minio_status.py
```

This will show:
- If MinIO is running
- What files are currently stored
- How many clips/snapshots exist

#### Step 2: Upload Mock Videos
```bash
python backend/scripts/upload_mock_videos.py
```

This will:
- Find all clips in the database
- Create simple mock video files
- Upload them to MinIO with the correct URIs
- Create preview images

**Note**: This script works even without OpenCV (creates minimal placeholders).

#### Step 3: Restart Backend
After uploading videos, restart your backend server to ensure fresh presigned URLs are generated.

#### Step 4: Test in Frontend
1. Open the Gallery page
2. Videos should now play correctly
3. Downloads should work with proper .mp4 extension
4. Delete should remove items from gallery

## Timezone Issue

The timestamps are stored in UTC (best practice) but should display in your local timezone.

### Option 1: Browser Automatic (Recommended)
The browser should automatically convert to your local timezone. Check:
1. Your Windows timezone settings
2. Browser timezone (should match system)

### Option 2: Explicit Helsinki Time
If you need to force Helsinki timezone, install `date-fns-tz`:

```bash
cd "Pet Training Web App"
npm install date-fns-tz
```

Then update the timestamp display in GalleryPage.tsx:

```typescript
import { formatInTimeZone } from 'date-fns-tz';

// Replace timestamp display with:
{formatInTimeZone(selectedItem.timestamp, 'Europe/Helsinki', 'yyyy-MM-dd HH:mm:ss')}
```

## Alternative: Create Real Clips

Instead of using mock data, you can create real clips through the API:

```bash
curl -X POST http://localhost:8000/clips \
  -H "Content-Type: application/json" \
  -d '{
    "start_ts": "2024-10-25T10:00:00Z",
    "duration_ms": 10000,
    "labels": ["test", "demo"]
  }'
```

This will:
1. Create a clip record
2. Queue a background job to process it
3. Upload actual video data to MinIO

## Troubleshooting

### Videos Still Download as .htm
**Cause**: Video files don't exist in MinIO
**Fix**: Run `upload_mock_videos.py` script

### Delete Doesn't Work
**Cause**: Backend API might be returning an error
**Fix**: Check browser console for error messages

### Duration Still Wrong
**Cause**: Frontend code not updated
**Fix**: Make sure you've reloaded the frontend (Ctrl+F5)

### Timezone Still Wrong
**Cause**: Browser timezone settings
**Fix**: 
1. Check Windows timezone: Settings → Time & Language → Date & Time
2. Ensure "Set time zone automatically" is enabled
3. Or use explicit timezone conversion (see above)

## Files Modified

### Backend
- `backend/app/api/clips.py` - Added video_url generation
- `backend/scripts/upload_mock_videos.py` - NEW: Upload mock videos
- `backend/scripts/check_minio_status.py` - NEW: Check MinIO status

### Frontend
- `Pet Training Web App/src/components/GalleryPage.tsx` - Fixed delete, duration display
- `Pet Training Web App/src/services/api.ts` - Added delete methods
- `Pet Training Web App/src/types/backend.ts` - Added video_url field
- `Pet Training Web App/src/services/adapters.ts` - Use video_url for clips

## Summary

The code fixes are complete. To get videos working:

1. **Run**: `python backend/scripts/check_minio_status.py`
2. **Run**: `python backend/scripts/upload_mock_videos.py`
3. **Restart** backend server
4. **Test** in frontend

All videos should now play, download, and delete correctly!
