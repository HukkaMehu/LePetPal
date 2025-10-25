# Database Models

This directory contains SQLAlchemy ORM models for the Dog Monitor application.

## Models Overview

### User
- Primary user entity for the application
- Contains email, role, and timestamps
- Has relationships to all other user-owned entities

### Device
- Represents connected devices (cameras, future robot hardware)
- Tracks device status, capabilities, and last seen timestamp
- Belongs to a user

### Event
- Time-series data for detected behaviors and occurrences
- Stored in TimescaleDB hypertable for efficient time-based queries
- Contains event type, timestamp, data payload, and optional video timestamp
- Indexed for fast queries by user, type, and timestamp

### Clip
- Saved video segments with start timestamp and duration
- Stored in S3/MinIO with metadata in database
- Supports labels, preview images, and share tokens
- Indexed by user and start timestamp

### Snapshot
- Single frame captures from video stream
- Stored in S3/MinIO with metadata in database
- Supports labels and notes
- Indexed by user and timestamp

### Routine
- Scheduled training sequences
- Contains cron schedule and step definitions (JSONB)
- Can be enabled/disabled
- Belongs to a user

### AIMetricsDaily
- Daily aggregated metrics from AI detections
- Tracks behavior counts (sit, stand, lie, fetch, etc.)
- Tracks time in frame, calm minutes, and vocalizations
- Unique constraint on user_id + date
- Indexed for efficient date range queries

### Model
- AI model registry for detector, action, pose, and policy models
- Tracks model artifacts, versions, and status
- Unique constraint on name + version

## Running Migrations

### Apply migrations
```bash
cd backend
alembic upgrade head
```

### Create a new migration
```bash
alembic revision --autogenerate -m "description"
```

### Rollback one migration
```bash
alembic downgrade -1
```

### View migration history
```bash
alembic history
```

## TimescaleDB

The `events` table is configured as a TimescaleDB hypertable for efficient time-series queries. This provides:
- Automatic partitioning by time
- Optimized time-based queries
- Compression for older data
- Better performance for large event datasets

The TimescaleDB extension is automatically enabled during the initial migration.
