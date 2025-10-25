# Database Seeding and Demo Mode Scripts

This directory contains scripts for setting up demo data and generating mock media files.

## Scripts

### 1. `seed_database.py`

Seeds the database with sample data for demo purposes.

**What it creates:**
- Demo user account (`demo@dogmonitor.com`)
- 7 days of sample events (sits, stands, barks, fetch attempts, etc.)
- Daily metrics aggregations
- 10 sample clip records
- 15 sample snapshot records
- 3 sample training routines
- AI model records

**Usage:**
```bash
cd backend
python scripts/seed_database.py
```

**Requirements:**
- Database must be running and migrated
- Environment variables must be configured (`.env` file)

### 2. `generate_mock_media.py`

Generates placeholder images and videos for the demo mode.

**What it creates:**
- Mock snapshot images (8 different scenarios)
- Mock clip preview images (6 different scenarios)
- Sample video file (10 seconds, looping animation)

**Usage:**
```bash
cd backend
python scripts/generate_mock_media.py
```

**Output:**
Files are created in `backend/mock_media/`:
- `snapshots/` - Snapshot images
- `clips/` - Clip previews and sample video

**Requirements:**
- OpenCV (`cv2`) must be installed
- NumPy must be installed

## Demo Mode

### Backend API

The video streaming endpoints support a `demo` query parameter:

**MJPEG Stream:**
```
GET /video/mjpeg?demo=true
```

**WebRTC Offer:**
```
POST /video/webrtc/offer?demo=true
```

When `demo=true`, the API streams the pre-recorded video from `mock_media/clips/sample_clip.mp4` instead of the live test pattern.

### Frontend Integration

To enable demo mode in the frontend, add the `demo=true` query parameter to video stream URLs:

```typescript
// MJPEG
const streamUrl = `${API_URL}/video/mjpeg?demo=true`;

// WebRTC
const response = await fetch(`${API_URL}/video/webrtc/offer?demo=true`, {
  method: 'POST',
  body: JSON.stringify(offer)
});
```

## Setup Instructions

### Complete Demo Setup

1. **Start services** (PostgreSQL, Redis, MinIO):
   ```bash
   docker-compose up -d
   ```

2. **Run database migrations**:
   ```bash
   cd backend
   alembic upgrade head
   ```

3. **Seed the database**:
   ```bash
   python scripts/seed_database.py
   ```

4. **Generate mock media**:
   ```bash
   python scripts/generate_mock_media.py
   ```

5. **Start the backend**:
   ```bash
   uvicorn app.main:app --reload
   ```

6. **Start the frontend** with demo mode:
   ```bash
   cd frontend
   npm run dev
   ```

### Verifying Demo Data

After seeding, you can verify the data:

```sql
-- Check demo user
SELECT * FROM users WHERE email = 'demo@dogmonitor.com';

-- Check events count
SELECT COUNT(*) FROM events;

-- Check metrics
SELECT * FROM ai_metrics_daily ORDER BY date DESC;

-- Check clips
SELECT COUNT(*) FROM clips;

-- Check snapshots
SELECT COUNT(*) FROM snapshots;
```

## Notes

- The seed script is idempotent - it won't create duplicate data if run multiple times
- Demo user ID is printed after seeding for reference
- Mock media files are generated with OpenCV and don't require actual dog footage
- The demo video loops continuously when streamed
- All timestamps are relative to the current time for realistic demo experience

## Troubleshooting

**Database connection error:**
- Ensure PostgreSQL is running
- Check `.env` file for correct database credentials

**Import errors:**
- Make sure you're running from the `backend` directory
- Ensure all dependencies are installed: `pip install -r requirements.txt`

**Mock media generation fails:**
- Verify OpenCV is installed: `pip install opencv-python`
- Check write permissions for `backend/mock_media/` directory

**Demo video not playing:**
- Ensure `generate_mock_media.py` completed successfully
- Check that `backend/mock_media/clips/sample_clip.mp4` exists
- Verify the file is not corrupted (try opening with a video player)
