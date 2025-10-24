# Design Document — Part 2: AI, Data, and Operations

## AI Service Contracts

### Vision Processing
```python
# gRPC or HTTP endpoint
POST /vision/process
Request: {
  frameBase64: string,
  timestamp: number,
  enabledModels: string[]
}
Response: {
  detections: Detection[],
  keypoints: Keypoint[],
  actions: Action[],
  objects: ObjectDetection[],
  suggestedEvents: SuggestedEvent[]
}

interface Detection {
  class: string,
  confidence: number,
  box: { x: number, y: number, w: number, h: number }
}

interface Keypoint {
  name: string,
  x: number,
  y: number,
  confidence: number
}

interface Action {
  label: string,
  probability: number
}

interface ObjectDetection {
  class: string,
  confidence: number,
  box: BoundingBox
}

interface SuggestedEvent {
  type: string,
  confidence: number,
  data: any
}
```

### Clip Processing
```python
POST /clipper/create
Request: {
  videoSource: string,
  startTimestamp: string,
  endTimestamp: string,
  labels: string[]
}
Response: {
  jobId: string,
  estimatedDuration: number
}

GET /clipper/status/{jobId}
Response: {
  status: "queued" | "processing" | "complete" | "failed",
  progress: number,
  s3Uri?: string,
  error?: string
}
```

### AI Coach
```python
POST /coach/tips
Request: {
  currentAction: string,
  recentEvents: Event[],
  sessionContext: any
}
Response: {
  tip: string,
  confidence: number
}

POST /coach/summary
Request: {
  sessionStart: string,
  sessionEnd: string,
  events: Event[],
  metrics: SessionMetrics
}
Response: {
  summary: string,
  wins: string[],
  setbacks: string[],
  suggestions: string[],
  highlightClips: string[]
}

POST /coach/chat
Request: {
  question: string,
  context: {
    events: Event[],
    metrics: any
  }
}
Response: {
  answer: string,
  relevantTimestamps: number[]
}
```

## Data Models

### PostgreSQL Schema

```sql
-- Users table
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) UNIQUE NOT NULL,
  role VARCHAR(50) NOT NULL DEFAULT 'owner',
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Devices table (for future robot integration)
CREATE TABLE devices (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  name VARCHAR(255) NOT NULL,
  status VARCHAR(50) NOT NULL DEFAULT 'offline',
  last_seen_at TIMESTAMP,
  capabilities JSONB,
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Events table (using TimescaleDB hypertable)
CREATE TABLE events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  ts TIMESTAMP NOT NULL,
  type VARCHAR(100) NOT NULL,
  data JSONB,
  video_ts_ms BIGINT,
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Convert to hypertable for time-series optimization
SELECT create_hypertable('events', 'ts');

-- Create index for common queries
CREATE INDEX idx_events_user_type_ts ON events(user_id, type, ts DESC);
CREATE INDEX idx_events_video_ts ON events(video_ts_ms) WHERE video_ts_ms IS NOT NULL;

-- Clips table
CREATE TABLE clips (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  start_ts TIMESTAMP NOT NULL,
  duration_ms INTEGER NOT NULL,
  s3_uri VARCHAR(500) NOT NULL,
  labels TEXT[],
  preview_png VARCHAR(500),
  share_token VARCHAR(100) UNIQUE,
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_clips_user_start ON clips(user_id, start_ts DESC);

-- Snapshots table
CREATE TABLE snapshots (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  ts TIMESTAMP NOT NULL,
  s3_uri VARCHAR(500) NOT NULL,
  labels TEXT[],
  note TEXT,
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_snapshots_user_ts ON snapshots(user_id, ts DESC);

-- Routines table
CREATE TABLE routines (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  name VARCHAR(255) NOT NULL,
  cron VARCHAR(100) NOT NULL,
  steps JSONB NOT NULL,
  enabled BOOLEAN NOT NULL DEFAULT true,
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- AI metrics daily aggregation
CREATE TABLE ai_metrics_daily (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  date DATE NOT NULL,
  sit_count INTEGER DEFAULT 0,
  stand_count INTEGER DEFAULT 0,
  lie_count INTEGER DEFAULT 0,
  fetch_count INTEGER DEFAULT 0,
  fetch_success_count INTEGER DEFAULT 0,
  treats_dispensed INTEGER DEFAULT 0,
  time_in_frame_min INTEGER DEFAULT 0,
  barks INTEGER DEFAULT 0,
  howls INTEGER DEFAULT 0,
  whines INTEGER DEFAULT 0,
  calm_minutes INTEGER DEFAULT 0,
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
  UNIQUE(user_id, date)
);

CREATE INDEX idx_metrics_user_date ON ai_metrics_daily(user_id, date DESC);

-- Models table
CREATE TABLE models (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) NOT NULL,
  type VARCHAR(50) NOT NULL, -- 'detector', 'action', 'pose', 'policy'
  artifact_uri VARCHAR(500) NOT NULL,
  version VARCHAR(50) NOT NULL,
  status VARCHAR(50) NOT NULL DEFAULT 'available',
  metadata JSONB,
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  UNIQUE(name, version)
);
```

### State Management (Zustand)

```typescript
// Frontend global state
interface AppState {
  // Video state
  videoStream: {
    type: 'webrtc' | 'mjpeg';
    status: 'connecting' | 'connected' | 'disconnected';
    latencyMs: number;
    fps: number;
  };
  
  // Overlay state
  overlays: {
    detection: boolean;
    pose: boolean;
    heatmap: boolean;
    zones: boolean;
    annotations: boolean;
  };
  
  // Device state
  device: {
    status: 'connected' | 'offline';
    capabilities: string[];
  };
  
  // Events
  recentEvents: Event[];
  
  // UI state
  activeView: 'live' | 'gallery' | 'analytics' | 'routines' | 'settings';
  sidebarOpen: boolean;
  
  // Actions
  setVideoStream: (stream: Partial<VideoStream>) => void;
  toggleOverlay: (overlay: keyof Overlays) => void;
  addEvent: (event: Event) => void;
  setActiveView: (view: string) => void;
}
```

## Error Handling

### Frontend Error Handling

Video Stream Errors:
- WebRTC connection failure → Automatic fallback to MJPEG within 1 second
- MJPEG stream failure → Display reconnection banner with retry button
- Network interruption → Show "Reconnecting..." overlay, attempt reconnection every 3 seconds

API Errors:
- 4xx errors → Display toast notification with error message
- 5xx errors → Display generic error message, log to console
- Network timeout → Retry with exponential backoff (max 3 attempts)

WebSocket Errors:
- Connection lost → Attempt reconnection with exponential backoff
- Message parsing error → Log error, continue processing other messages

### Backend Error Handling

Video Processing Errors:
- Frame processing timeout → Skip frame, log warning
- AI service unavailable → Return empty detections, log error
- Model loading failure → Fall back to lighter model or disable feature

Database Errors:
- Connection pool exhausted → Return 503 Service Unavailable
- Query timeout → Return 504 Gateway Timeout
- Constraint violation → Return 400 Bad Request with details

Background Job Errors:
- Clip creation failure → Mark job as failed, store error message
- S3 upload failure → Retry up to 3 times with exponential backoff
- Task timeout → Cancel task, log error, notify user

API Error Responses:
```python
{
  "error": {
    "code": "CLIP_CREATION_FAILED",
    "message": "Failed to create clip",
    "details": "Video segment not found",
    "timestamp": "2025-10-24T10:30:00Z"
  }
}
```

## Testing Strategy

### Frontend Testing

Unit Tests:
- Component rendering with various props
- State management actions and selectors
- Utility functions (time formatting, validation)
- Overlay calculation logic

Integration Tests:
- Video player with overlay rendering
- WebSocket event handling and state updates
- API client with mock responses
- Routing and navigation

E2E Tests (Playwright):
- Complete user flow: view stream → capture snapshot → view gallery
- Routine creation and scheduling
- Analytics dashboard interaction
- Keyboard shortcuts

### Backend Testing

Unit Tests:
- API endpoint handlers
- Database models and queries
- Validation logic
- Utility functions

Integration Tests:
- WebSocket connection and message broadcasting
- Background job execution
- Database transactions
- S3 upload/download

Load Tests:
- WebSocket concurrent connections (target: 100 simultaneous)
- API throughput (target: 1000 req/s)
- Video stream handling (target: 10 concurrent streams)

### AI Service Testing

Unit Tests:
- Model inference with sample frames
- Detection post-processing
- Event suggestion logic

Integration Tests:
- End-to-end frame processing pipeline
- Model hot-swapping
- gRPC/HTTP endpoint responses

Performance Tests:
- Frame processing latency (target: <100ms on GPU, <200ms on CPU)
- Batch processing throughput
- Memory usage under load

## Future Robot Integration

### Integration Points

The system is designed with clean seams for robot integration:

1. Command Dispatch: The `/api/commands` endpoint currently returns 501. When robot is connected, it will:
   - Validate command against device capabilities
   - Dispatch to robot worker via message queue
   - Return command execution status

2. Telemetry Stream: The WebSocket hub has a telemetry message type. When robot is connected:
   - Stream joint positions, servo temperatures, battery level
   - Display in telemetry strip component
   - Log to events table for diagnostics

3. Routine Execution: Routines currently only schedule notifications. When robot is connected:
   - Backend dispatches routine steps to robot worker
   - Robot executes physical actions (pet, treat, fetch)
   - Results logged as events

4. Policy Selection: The policy selector dropdown is disabled. When robot is connected:
   - Enable dropdown with available policies (replay, act, smolvla)
   - Switch policy via `/api/models/switch` endpoint
   - Track policy performance in analytics

### Migration Path

Phase 1 (Current): Web app with AI monitoring, mock robot UI
Phase 2: Add robot worker service, enable command endpoint
Phase 3: Wire routine execution to robot actions
Phase 4: Add policy training and evaluation tools

No refactoring required - just enable existing endpoints and add robot worker service.

## Performance Considerations

### Video Streaming
- WebRTC target latency: <500ms
- MJPEG fallback acceptable latency: <2s
- Frame rate: 30 fps (GPU) or 15 fps (CPU)

### AI Processing
- Detection inference: <100ms per frame (GPU)
- Action recognition window: 2-3 seconds of frames
- Heatmap update: Every 10 seconds

### Database
- Event insertion: Batch writes every 1 second
- Analytics queries: Use materialized views for daily aggregations
- TimescaleDB compression: Compress events older than 7 days

### Caching
- Active models cached in memory
- Recent events cached in Redis (last 100)
- Analytics dashboard data cached for 5 minutes

### Scalability
- Horizontal scaling: Backend API is stateless (except WebSocket connections)
- WebSocket connections: Use Redis pub/sub for multi-instance broadcasting
- Background jobs: Scale Celery workers independently
- AI service: Can run multiple instances behind load balancer
