# Event Logging and Storage Implementation

This document describes the implementation of Task 7: Event logging and storage system.

## Overview

The event logging system provides:
1. REST API endpoints for manual event creation and retrieval
2. Background event processing pipeline for AI detections
3. Real-time event feed component with WebSocket updates

## Backend Implementation

### 1. Event API Endpoints (`backend/app/api/events.py`)

#### POST `/api/events`
Creates a manual event and stores it in the database. Also broadcasts the event to all connected WebSocket clients.

**Request Body:**
```json
{
  "type": "sit",
  "data": {
    "confidence": 0.95,
    "action": "sit"
  },
  "video_ts_ms": 12345,
  "ts": "2025-10-24T10:30:00Z"  // optional
}
```

**Response:**
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "ts": "2025-10-24T10:30:00Z",
  "type": "sit",
  "data": {...},
  "video_ts_ms": 12345,
  "created_at": "2025-10-24T10:30:00Z"
}
```

#### GET `/api/events`
Retrieves events with optional filtering by date range and type.

**Query Parameters:**
- `from_ts`: Filter events from this timestamp (ISO format)
- `to_ts`: Filter events to this timestamp (ISO format)
- `type`: Filter by event type (e.g., "sit", "bark", "bookmark")
- `limit`: Maximum number of events to return (default: 100, max: 1000)
- `offset`: Number of events to skip (default: 0)

**Response:**
```json
{
  "events": [...],
  "total": 150,
  "limit": 100,
  "offset": 0
}
```

#### POST `/api/events/process-detection`
Processes AI detection data through the event processing pipeline.

**Request Body:**
```json
{
  "timestamp": 12345,
  "detections": [...],
  "actions": [...],
  "objects": [...]
}
```

### 2. Event Processing Pipeline (`backend/app/workers/event_processor.py`)

The `EventProcessor` class is a background worker that:

#### Features:
- **Batch Event Insertion**: Buffers events and flushes to database every 1 second
- **Auto-Bookmark Logic**: Creates bookmarks for significant motion based on:
  - Multiple simultaneous detections
  - High-confidence actions
  - Object interactions
  - Sustained motion over time
- **Auto-Clip Logic**: Detects action sequences and creates clip requests:
  - Fetch-return: approach → fetch_return (within 10 seconds)
  - Treat-eaten: approach → eating (within 5 seconds)
  - Clips are automatically adjusted to 8-12 seconds duration

#### Usage:
The event processor is automatically started when the application starts (see `backend/app/main.py`).

To process a detection:
```python
await event_processor.process_detection(
    detection={
        "detections": [...],
        "actions": [...],
        "objects": [...]
    },
    user_id="user-uuid",
    video_ts_ms=12345
)
```

### 3. Integration with Main Application

The event processor is integrated into the FastAPI application lifecycle in `backend/app/main.py`:
- Started on application startup
- Stopped on application shutdown
- Automatically flushes buffered events

## Frontend Implementation

### 1. Event Types (`frontend/src/types/event.ts`)

Defines TypeScript types for events:
- `Event`: Main event interface
- `EventType`: Union type of all event types
- `EVENT_EMOJIS`: Emoji markers for each event type
- `EVENT_LABELS`: Human-readable labels for event types

### 2. WebSocket Hook (`frontend/src/hooks/useWebSocket.ts`)

Custom React hook for WebSocket connections:
- Automatic reconnection on disconnect
- Handles event, overlay, and telemetry messages
- Connection status tracking

**Usage:**
```typescript
const { isConnected, error } = useWebSocket({
  url: 'ws://localhost:8000/ws/ui',
  onEvent: (event) => console.log('Event received:', event),
  reconnectInterval: 3000
});
```

### 3. EventFeed Component (`frontend/src/components/EventFeed.tsx`)

React component that displays a real-time event feed:

**Features:**
- Real-time updates via WebSocket
- Event type filtering
- Click-to-jump-to-timestamp functionality
- Emoji markers for different event types
- Auto-generated event badges
- Connection status indicator
- Pagination (shows most recent N events)

**Props:**
```typescript
interface EventFeedProps {
  wsUrl?: string;              // WebSocket URL
  onEventClick?: (event: Event) => void;  // Callback for event clicks
  maxEvents?: number;          // Max events to display (default: 50)
  className?: string;          // CSS class name
}
```

**Usage:**
```tsx
<EventFeed
  wsUrl="ws://localhost:8000/ws/ui"
  onEventClick={(event) => {
    // Jump to video timestamp
    if (event.video_ts_ms) {
      videoPlayer.seek(event.video_ts_ms);
    }
  }}
  maxEvents={100}
/>
```

### 4. Demo Page (`frontend/src/app/events-demo/page.tsx`)

A demo page showcasing the EventFeed component with:
- Event feed display
- Selected event details panel
- Test controls to create sample events
- Instructions for usage

**Access:** Navigate to `/events-demo` in the frontend application.

## Event Types

The system supports the following event types:

| Type | Emoji | Description |
|------|-------|-------------|
| `dog_detected` | 🐕 | Dog detected in frame |
| `sit` | 🪑 | Dog sitting |
| `stand` | 🧍 | Dog standing |
| `lie` | 🛏️ | Dog lying down |
| `approach` | 👣 | Dog approaching |
| `fetch_return` | 🎾 | Dog returning with fetch item |
| `drinking` | 💧 | Dog drinking |
| `eating` | 🍖 | Dog eating |
| `bark` | 🔊 | Dog barking |
| `howl` | 🌙 | Dog howling |
| `whine` | 😢 | Dog whining |
| `person_entered` | 👤 | Person entered frame |
| `clip_saved` | 🎬 | Video clip saved |
| `clip_requested` | 📹 | Video clip requested |
| `snapshot_saved` | 📸 | Snapshot saved |
| `bookmark` | 🔖 | Bookmark created |
| `object_detected_*` | ⚽🧸🥣 | Object detected (ball, toy, bowl) |

## Database Schema

Events are stored in the `events` table (TimescaleDB hypertable):

```sql
CREATE TABLE events (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  ts TIMESTAMP NOT NULL,
  type VARCHAR(100) NOT NULL,
  data JSONB,
  video_ts_ms BIGINT,
  created_at TIMESTAMP NOT NULL
);
```

Indexes:
- `idx_events_user_type_ts` on (user_id, type, ts)
- `idx_events_video_ts` on (video_ts_ms) where video_ts_ms IS NOT NULL

## Testing

### Backend Testing

Test event creation:
```bash
curl -X POST http://localhost:8000/api/events \
  -H "Content-Type: application/json" \
  -d '{
    "type": "sit",
    "data": {"confidence": 0.95},
    "video_ts_ms": 12345
  }'
```

Test event retrieval:
```bash
curl "http://localhost:8000/api/events?type=sit&limit=10"
```

Test detection processing:
```bash
curl -X POST http://localhost:8000/api/events/process-detection \
  -H "Content-Type: application/json" \
  -d '{
    "timestamp": 12345,
    "detections": [{"class": "dog", "confidence": 0.95}],
    "actions": [{"label": "sit", "probability": 0.9}]
  }'
```

### Frontend Testing

1. Start the frontend development server
2. Navigate to `/events-demo`
3. Use the test buttons to create sample events
4. Verify events appear in real-time
5. Click events to see details
6. Test filtering by event type

## Requirements Satisfied

### Requirement 4.1
✅ Manual event creation via POST `/api/events`
✅ Event retrieval with filtering via GET `/api/events`

### Requirement 4.2
✅ Auto-bookmark logic for significant motion
✅ Auto-clip logic for fetch-return and treat-eaten sequences

### Requirement 11.1, 11.2, 11.3
✅ AI detections automatically logged as events
✅ Events stored in database for analytics
✅ Real-time event broadcasting via WebSocket

## Next Steps

To integrate with the full application:

1. **Authentication**: Replace placeholder user_id with actual authenticated user
2. **Video Player Integration**: Connect EventFeed's `onEventClick` to video player seek functionality
3. **AI Service Integration**: Connect AI service to `/api/events/process-detection` endpoint
4. **Analytics**: Use stored events for training analytics (Task 11)
5. **Media Management**: Implement clip creation based on `clip_requested` events (Task 8)

## Files Created/Modified

### Backend
- `backend/app/api/events.py` - Event API endpoints (modified)
- `backend/app/workers/__init__.py` - Workers module (created)
- `backend/app/workers/event_processor.py` - Event processing pipeline (created)
- `backend/app/main.py` - Integrated event processor (modified)

### Frontend
- `frontend/src/types/event.ts` - Event type definitions (created)
- `frontend/src/hooks/useWebSocket.ts` - WebSocket hook (created)
- `frontend/src/components/EventFeed.tsx` - Event feed component (created)
- `frontend/src/app/events-demo/page.tsx` - Demo page (created)
