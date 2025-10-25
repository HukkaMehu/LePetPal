# Gallery Issues - Complete Fix

## Issues Fixed

### 1. ✅ Video Downloads as .htm Files
**Problem**: Videos were downloading as HTML files because the backend was returning S3 URIs instead of presigned URLs.

**Solution**: 
- Added `video_url` field to `ClipResponse` model in backend
- Backend now generates presigned URLs for video files
- Frontend adapter updated to use `video_url` instead of `s3_uri`

**Files Changed**:
- `backend/app/api/clips.py` - Added video_url generation
- `Pet Training Web App/src/types/backend.ts` - Added video_url field
- `Pet Training Web App/src/services/adapters.ts` - Use video_url for playback

### 2. ✅ Delete Functionality Not Working
**Problem**: Delete button was a TODO stub that didn't actually delete media.

**Solution**:
- Implemented `deleteClip()` and `deleteSnapshot()` methods in API client
- Updated `handleDelete()` in GalleryPage to call the appropriate API
- Added refetch after successful deletion to update the gallery

**Files Changed**:
- `Pet Training Web App/src/services/api.ts` - Added delete methods
- `Pet Training Web App/src/components/GalleryPage.tsx` - Implemented delete handler

### 3. ✅ Video Duration Display Wrong
**Problem**: Duration was showing 1000x the actual length (e.g., 10000s instead of 10s).

**Root Cause**: Backend stores duration in milliseconds (`duration_ms`) but frontend was displaying it directly as seconds.

**Solution**: Convert milliseconds to seconds by dividing by 1000:
```typescript
{Math.round(selectedItem.duration / 1000)}s
```

**Files Changed**:
- `Pet Training Web App/src/components/GalleryPage.tsx` - Fixed duration display in 2 places

### 4. ⚠️ Timezone Issue (Helsinki Time)
**Problem**: Timestamps are showing UTC time instead of Helsinki time (UTC+2/+3).

**Current Status**: The backend stores timestamps in UTC (best practice). The frontend displays them using the browser's local timezone.

**Recommended Solution**: 
The browser should automatically display times in your local timezone. If it's not:
1. Check your system timezone settings
2. Or explicitly format dates in Helsinki timezone using `date-fns-tz`:

```typescript
import { formatInTimeZone } from 'date-fns-tz';

formatInTimeZone(timestamp, 'Europe/Helsinki', 'yyyy-MM-dd HH:mm:ss')
```

### 5. ⚠️ Mock Data Issue
**Problem**: Seeded clips have fake S3 URIs that don't exist in MinIO.

**Current Status**: The seed script creates clips with URIs like `s3://dog-monitor/clips/demo_xxx.mp4` but these files don't actually exist in MinIO.

**Temporary Workaround**: 
- The presigned URLs will be generated but will return 404 when accessed
- For demo purposes, you can either:
  1. Upload actual video files to MinIO matching the seeded URIs
  2. Create new clips through the UI which will properly upload files
  3. Update the seed script to upload actual mock videos

**Recommended Fix**: Update `backend/scripts/seed_database.py` to upload actual mock video files to MinIO when seeding.

## Testing Checklist

- [x] Video duration displays correctly (in seconds, not milliseconds)
- [x] Delete button calls API and removes items from gallery
- [x] Gallery refreshes after deletion
- [ ] Videos play correctly in modal (requires actual video files in MinIO)
- [ ] Videos download with correct file extension (requires actual video files)
- [ ] Timestamps display in correct timezone

## Next Steps

1. **For Real Video Files**: Run the clip creation through the UI or API with actual video data
2. **For Mock Data**: Update seed script to upload actual video files to MinIO
3. **For Timezone**: Verify browser timezone settings or implement explicit timezone conversion

## API Endpoints Used

- `GET /clips` - List clips with presigned URLs
- `DELETE /clips/{id}` - Delete a clip
- `DELETE /snapshots/{id}` - Delete a snapshot
