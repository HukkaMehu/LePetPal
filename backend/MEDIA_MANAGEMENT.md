# Media Management System

This document describes the media management system implementation for snapshots and clips.

## Overview

The media management system provides:
- **Snapshot capture**: Capture and store video frames
- **Clip creation**: Extract video segments with background processing
- **Gallery view**: Browse, share, and delete media items

## Backend Components

### Storage Service (`app/core/storage.py`)
- S3/MinIO integration for media storage
- Presigned URL generation for secure access
- File upload/delete operations

### Snapshots API (`app/api/snapshots.py`)
- `POST /api/snapshots` - Create snapshot from video frame
- `GET /api/snapshots` - List all snapshots with pagination
- `GET /api/snapshots/{id}` - Get specific snapshot
- `DELETE /api/snapshots/{id}` - Delete snapshot

### Clips API (`app/api/clips.py`)
- `POST /api/clips` - Queue clip creation job (returns 202 Accepted)
- `GET /api/clips/{id}` - Get clip status and details
- `GET /api/clips` - List all clips with pagination
- `POST /api/clips/{id}/share` - Generate share link
- `DELETE /api/clips/{id}` - Delete clip

### Background Processing (`app/workers/clip_processor.py`)
- Celery worker for async clip processing
- Video segment extraction (placeholder implementation)
- Preview frame generation
- S3 upload of processed clips

## Frontend Components

### Gallery Component (`components/Gallery.tsx`)
- Tab-based view for snapshots and clips
- Lazy loading with intersection observer
- Delete functionality
- Share link generation for clips
- Status indicators for clip processing

### Gallery Page (`app/gallery/page.tsx`)
- Full-page gallery view
- Responsive grid layout

## Setup Requirements

### Backend Dependencies
```bash
cd backend
pip install -r requirements.txt
```

Required services:
- PostgreSQL (for metadata storage)
- Redis (for Celery task queue)
- MinIO or S3 (for media storage)

### Environment Variables
Add to `backend/.env`:
```
S3_ENDPOINT_URL=http://localhost:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
S3_BUCKET_NAME=dog-monitor
REDIS_URL=redis://localhost:6379/0
```

### Starting Celery Worker
```bash
cd backend
celery -A app.core.celery_app worker --loglevel=info
```

## Usage Examples

### Create Snapshot
```bash
curl -X POST http://localhost:8000/api/snapshots \
  -H "Content-Type: application/json" \
  -d '{
    "timestamp": "2024-10-24T10:30:00Z",
    "labels": ["sitting", "good-boy"],
    "note": "Training session",
    "frame_data": "data:image/jpeg;base64,/9j/4AAQ..."
  }'
```

### Create Clip
```bash
curl -X POST http://localhost:8000/api/clips \
  -H "Content-Type: application/json" \
  -d '{
    "start_ts": "2024-10-24T10:30:00Z",
    "duration_ms": 5000,
    "labels": ["fetch", "training"]
  }'
```

### Check Clip Status
```bash
curl http://localhost:8000/api/clips/{clip_id}
```

### Generate Share Link
```bash
curl -X POST http://localhost:8000/api/clips/{clip_id}/share
```

## Implementation Notes

### Current Limitations
1. **Video Extraction**: The clip processor currently creates placeholder videos. In production, this should:
   - Connect to a video buffer/recording system
   - Use ffmpeg or similar for actual video extraction
   - Generate proper preview thumbnails

2. **Authentication**: Currently uses placeholder user IDs. Should integrate with actual auth system.

3. **Storage**: Configured for MinIO but works with any S3-compatible storage.

### Future Enhancements
- Real-time progress updates for clip processing via WebSocket
- Video trimming and editing capabilities
- Batch operations (delete multiple items)
- Advanced filtering and search
- Download functionality
- Thumbnail generation optimization

## Requirements Mapping

- **Requirement 6.1**: Snapshot capture endpoint with S3 upload
- **Requirement 4.2**: Clip creation with background job processing
- **Requirement 6.2**: Clip metadata storage and retrieval
- **Requirement 4.5**: Gallery component with grid view and lazy loading
