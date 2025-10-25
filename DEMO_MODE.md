# Demo Mode Setup Guide

This guide explains how to set up and use the demo mode for the Dog Monitor application. Demo mode allows you to explore the application with pre-loaded sample data and pre-recorded video without needing a live camera feed.

## Overview

Demo mode includes:
- **Sample Database Records**: Events, metrics, clips, snapshots, routines, and AI models
- **Mock Media Files**: Placeholder images and a looping demo video
- **Demo Video Streaming**: Pre-recorded video instead of live camera feed
- **Demo User Account**: Pre-configured user for testing

## Quick Start

### 1. Prerequisites

Ensure you have:
- PostgreSQL database running (via Docker Compose)
- Backend dependencies installed (`pip install -r backend/requirements.txt`)
- Frontend dependencies installed (`npm install` in frontend directory)

### 2. Start Services

```bash
# Start PostgreSQL, Redis, and MinIO
docker-compose up -d

# Verify services are running
docker-compose ps
```

### 3. Run Database Migrations

```bash
cd backend
alembic upgrade head
```

### 4. Seed the Database

```bash
cd backend
python scripts/seed_database.py
```

**Output:**
```
🌱 Starting database seeding...

✓ Created demo user: demo@dogmonitor.com
✓ Created 350 sample events over 7 days
✓ Created sample metrics for 7 days
✓ Created 10 sample clips
✓ Created 15 sample snapshots
✓ Created 3 sample routines
✓ Created sample AI models

✅ Database seeding completed successfully!

Demo user email: demo@dogmonitor.com
Demo user ID: [uuid]
```

### 5. Generate Mock Media

```bash
cd backend
python scripts/generate_mock_media.py
```

**Output:**
```
🎬 Generating mock media files...

Creating mock snapshots...
  ✓ Created backend/mock_media/snapshots/snapshot_1.jpg
  ✓ Created backend/mock_media/snapshots/snapshot_2.jpg
  ...

Creating mock clip previews...
  ✓ Created backend/mock_media/clips/clip_1_preview.jpg
  ...

Creating mock video...
  ✓ Created backend/mock_media/clips/sample_clip.mp4

✅ Mock media generation completed!
   Snapshots: backend/mock_media/snapshots
   Clips: backend/mock_media/clips
```

### 6. Enable Demo Mode

**Option A: Via Settings UI**
1. Start the frontend: `npm run dev` (in frontend directory)
2. Navigate to Settings page: `http://localhost:3000/settings`
3. Scroll to "Video Settings" section
4. Check "Enable Demo Mode"
5. Click "Save Changes"

**Option B: Via Demo Page**
1. Navigate to: `http://localhost:3000/demo`
2. Click "Enable Demo Mode" button

**Option C: Manually**
```javascript
// In browser console
const settings = JSON.parse(localStorage.getItem('videoSettings') || '{}');
settings.demoMode = true;
localStorage.setItem('videoSettings', JSON.stringify(settings));
```

### 7. Start the Application

```bash
# Terminal 1: Backend
cd backend
uvicorn app.main:app --reload

# Terminal 2: Frontend
cd frontend
npm run dev
```

### 8. Access Demo Mode

Visit `http://localhost:3000` and you should see:
- Demo video playing in the video player
- "DEMO MODE" watermark on the video
- Sample events in the event feed
- Historical metrics in analytics charts

## What Gets Created

### Database Records

#### Demo User
- **Email**: `demo@dogmonitor.com`
- **Role**: owner
- **Purpose**: All demo data is associated with this user

#### Events (350+ records)
Sample events over 7 days including:
- Dog detected events with bounding boxes
- Action events: sit, stand, lie, fetch_return
- Audio events: bark, howl, whine
- Activity events: drinking, eating
- Manual events: bookmarks, clips saved
- Person detected events

#### Daily Metrics (7 days)
Aggregated metrics including:
- Sit/stand/lie counts
- Fetch attempts and successes
- Time in frame (minutes)
- Bark/howl/whine counts
- Calm minutes
- Treats dispensed

#### Clips (10 records)
Sample clip metadata with:
- Various labels: fetch, sit, play, treat, bark, zoomies
- Duration: 8-15 seconds
- S3 URIs (placeholder paths)
- Preview images
- Share tokens

#### Snapshots (15 records)
Sample snapshot metadata with:
- Labels: sleeping, playing, sitting, alert, eating, portrait
- Optional notes
- S3 URIs (placeholder paths)
- Timestamps spread over 7 days

#### Routines (3 records)
Pre-configured training routines:
1. **Morning Training** (8 AM daily)
   - Sit drill → Treat → Fetch → Treat
2. **Afternoon Play** (3 PM daily)
   - Play → Fetch → Wait → Treat
3. **Evening Calm** (8 PM daily, disabled)
   - Pet → Sit drill → Treat

#### AI Models (4 records)
Sample model configurations:
- `yolov8n-dog` (detector, active)
- `yolov8s-dog` (detector, available)
- `action-recognizer-v1` (action, active)
- `pose-estimator-lite` (pose, active)

### Mock Media Files

#### Snapshots (8 images)
Located in: `backend/mock_media/snapshots/`
- `snapshot_1.jpg` through `snapshot_8.jpg`
- Each with different labels: Sleeping, Playing, Sitting, etc.
- 640x480 resolution
- Simple dog silhouette illustrations

#### Clip Previews (6 images)
Located in: `backend/mock_media/clips/`
- `clip_1_preview.jpg` through `clip_6_preview.jpg`
- Labels: Fetch Success, Sit Training, Play Time, etc.
- 640x480 resolution
- Motion blur effect with play button overlay

#### Demo Video (1 file)
Located in: `backend/mock_media/clips/sample_clip.mp4`
- Duration: 10 seconds
- Resolution: 640x480
- FPS: 30
- Animated dog moving across screen
- Loops continuously when streamed

## Using Demo Mode

### Video Streaming

When demo mode is enabled, video endpoints use the demo video:

**MJPEG Stream:**
```
GET http://localhost:8000/video/mjpeg?demo=true
```

**WebRTC Offer:**
```
POST http://localhost:8000/video/webrtc/offer?demo=true
```

The frontend automatically adds the `demo=true` parameter when demo mode is enabled in settings.

### Features to Test

1. **Live View**
   - Video player with demo video
   - Overlay controls (detection, pose, heatmap)
   - Playback controls (play, pause, fullscreen, PiP)

2. **Event Feed**
   - Real-time event display
   - Event type filtering
   - Click to jump to timestamp

3. **Timeline**
   - Scrubber with event markers
   - Clip in/out handles
   - Zoom and pan controls

4. **Analytics Dashboard**
   - Time-series charts with 7 days of data
   - Sit/stand/lie counts
   - Fetch success rates
   - Bark frequency

5. **Progress Page**
   - 7-day trends
   - Best training hours
   - Reinforcement ratios
   - Correlation tiles

6. **Streaks and Badges**
   - Training streak calculations
   - Achievement badges
   - Milestone tracking

7. **Gallery**
   - Clip thumbnails (10 items)
   - Snapshot grid (15 items)
   - Share links
   - Delete functionality

8. **Routines**
   - Pre-configured routines
   - Routine builder
   - Schedule management
   - Enable/disable toggles

9. **Coach Chat**
   - AI-powered training tips
   - Session summaries
   - Q&A interface

10. **Robot Integration**
    - Action buttons (disabled)
    - Device status display
    - Policy selector
    - Telemetry strip

## Resetting Demo Data

To reset and regenerate demo data:

```bash
# Option 1: Drop and recreate database
cd backend
alembic downgrade base
alembic upgrade head
python scripts/seed_database.py

# Option 2: Delete demo user data
# Connect to PostgreSQL and run:
DELETE FROM users WHERE email = 'demo@dogmonitor.com';
# Then re-run seed script
python scripts/seed_database.py
```

## Troubleshooting

### Database Connection Error
```
Error: could not connect to server
```
**Solution**: Ensure PostgreSQL is running
```bash
docker-compose up -d postgres
```

### Import Errors
```
ModuleNotFoundError: No module named 'app'
```
**Solution**: Run from backend directory
```bash
cd backend
python scripts/seed_database.py
```

### Mock Media Generation Fails
```
ImportError: No module named 'cv2'
```
**Solution**: Install OpenCV
```bash
pip install opencv-python
```

### Demo Video Not Playing
**Symptoms**: Test pattern shows instead of demo video

**Solutions**:
1. Verify file exists:
   ```bash
   ls backend/mock_media/clips/sample_clip.mp4
   ```

2. Regenerate video:
   ```bash
   cd backend
   python scripts/generate_mock_media.py
   ```

3. Check file permissions:
   ```bash
   chmod 644 backend/mock_media/clips/sample_clip.mp4
   ```

### Demo Mode Not Activating
**Symptoms**: Live test pattern shows even with demo mode enabled

**Solutions**:
1. Clear browser cache and reload
2. Check localStorage:
   ```javascript
   console.log(localStorage.getItem('videoSettings'));
   ```
3. Manually enable:
   ```javascript
   localStorage.setItem('videoSettings', JSON.stringify({demoMode: true}));
   ```

### No Events Showing
**Symptoms**: Event feed is empty

**Solutions**:
1. Verify seeding completed:
   ```sql
   SELECT COUNT(*) FROM events;
   ```
2. Check user ID matches:
   ```sql
   SELECT id FROM users WHERE email = 'demo@dogmonitor.com';
   ```
3. Re-run seed script

## API Endpoints for Demo Data

### Get Demo User Events
```bash
curl "http://localhost:8000/api/events?from=2024-10-18T00:00:00Z&to=2024-10-25T23:59:59Z"
```

### Get Demo Metrics
```bash
curl "http://localhost:8000/api/analytics/daily?from=2024-10-18&to=2024-10-25"
```

### Get Demo Clips
```bash
curl "http://localhost:8000/api/clips"
```

### Get Demo Snapshots
```bash
curl "http://localhost:8000/api/snapshots"
```

### Get Demo Routines
```bash
curl "http://localhost:8000/api/routines"
```

## Notes

- Demo data is randomly generated with realistic variations
- Timestamps are relative to current time for realistic experience
- The seed script is idempotent (safe to run multiple times)
- Demo video loops continuously
- All S3 URIs are placeholder paths (actual files not uploaded)
- Mock media files are generated locally, not uploaded to S3/MinIO

## Next Steps

After exploring demo mode:
1. Disable demo mode in settings
2. Connect a real camera for live streaming
3. Configure AI service for real detections
4. Set up S3/MinIO for actual media storage
5. Create your own user account
6. Start real training sessions!

## Demo Page

Visit `http://localhost:3000/demo` for:
- Demo mode status
- Setup instructions
- Data overview statistics
- Quick links to features
- Troubleshooting tips

---

For more information, see:
- `backend/scripts/README.md` - Detailed script documentation
- `VIDEO_STREAMING_SETUP.md` - Video streaming configuration
- `README.md` - Main project documentation
