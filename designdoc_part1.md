# Design Document — Part 1: System Overview and Architecture

## Overview

The dog-monitoring web application is a full-stack system that delivers real-time video streaming with AI-powered overlays, automated behavior logging, and training analytics. The architecture is designed to ship immediately with mock robot integration points that can be activated later without refactoring.

The system consists of three main services:
1. Frontend - Next.js web application with real-time video player and interactive UI
2. Backend API - FastAPI service handling WebSocket connections, REST endpoints, and background jobs
3. AI Service - Separate Python service for vision models and LLM-based coaching

## Architecture

### High-Level System Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend                             │
│  Next.js + React + Tailwind + Zustand + shadcn/ui          │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Video Player │  │  Analytics   │  │   Routines   │     │
│  │  + Overlays  │  │    Charts    │  │    Builder   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
         │                    │                    │
         │ WebRTC/MJPEG      │ REST API          │ WebSocket
         │                    │                    │
┌─────────────────────────────────────────────────────────────┐
│                      Backend API                             │
│              FastAPI + Uvicorn + Starlette                  │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   WebSocket  │  │  REST Routes │  │   Background │     │
│  │      Hub     │  │   (Events,   │  │    Workers   │     │
│  │              │  │  Media, etc) │  │ (Celery/ARQ) │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
         │                    │                    │
         │                    │                    │
         ├────────────────────┴────────────────────┤
         │                                          │
         │ gRPC/HTTP                                │ SQL
         │                                          │
┌────────────────────────┐              ┌──────────────────┐
│     AI Service         │              │    PostgreSQL    │
│  Vision + LLM Models   │              │   + TimescaleDB  │
│                        │              │                  │
│  ┌──────────────────┐ │              │  ┌────────────┐  │
│  │ Dog Detection    │ │              │  │   Events   │  │
│  │ Pose Estimation  │ │              │  │   Clips    │  │
│  │ Action Recognition│ │              │  │  Routines  │  │
│  │ Object Detection │ │              │  │  Metrics   │  │
│  │ Coach LLM        │ │              │  └────────────┘  │
│  └──────────────────┘ │              └──────────────────┘
└────────────────────────┘                       │
                                                 │
                                      ┌──────────────────┐
                                      │   S3 / MinIO     │
                                      │                  │
                                      │  Clips, Snapshots│
                                      │  Model Artifacts │
                                      └──────────────────┘
```

### Technology Stack

Frontend:
- Next.js 14 (App Router)
- React 18 with TypeScript
- Tailwind CSS for styling
- Zustand for state management
- shadcn/ui for component library
- React Query (TanStack Query) for API calls
- WebRTC with aiortc for video streaming
- Recharts for analytics visualization

Backend:
- FastAPI with Uvicorn ASGI server
- Starlette for WebSocket support
- Celery or ARQ for background task queue
- Redis for task broker and caching
- SQLAlchemy ORM with Alembic migrations
- Pydantic for data validation

AI Service:
- Python with gRPC or HTTP endpoints
- YOLO or similar for dog detection
- Lightweight pose estimation model
- Transformer-based action recognition
- LLM integration (OpenAI API or local model)
- OpenCV for image processing

Storage:
- PostgreSQL 15+ with TimescaleDB extension
- S3-compatible storage (MinIO for local, AWS S3 for production)

Infrastructure:
- Docker Compose for local development
- Environment-based configuration

## Components and Interfaces

### Frontend Components

#### Video Player Component
```typescript
interface VideoPlayerProps {
  streamUrl: string;
  streamType: 'webrtc' | 'mjpeg';
  overlays: OverlayConfig[];
  onSnapshot: () => void;
  onClipMark: (timestamp: number) => void;
}

interface OverlayConfig {
  type: 'detection' | 'pose' | 'heatmap' | 'zone' | 'annotation';
  enabled: boolean;
  data: any;
}
```

Responsibilities:
- Establish WebRTC connection with fallback to MJPEG
- Render video with canvas overlay layer
- Handle keyboard shortcuts (s, c, b, f)
- Manage playback controls (play, pause, PiP, fullscreen)
- Display latency slider and connection status

#### Analytics Dashboard Component
```typescript
interface AnalyticsDashboardProps {
  dateRange: DateRange;
  metrics: DailyMetrics[];
}

interface DailyMetrics {
  date: string;
  sitCount: number;
  standCount: number;
  lieCount: number;
  fetchAttempts: number;
  fetchSuccesses: number;
  timeInFrameMin: number;
  calmMinutes: number;
  barks: number;
}
```

Responsibilities:
- Display time-series charts for behavior counts
- Show hourly bucket aggregations
- Calculate and display training streaks
- Render correlation tiles
- Provide date range selector

#### Routine Builder Component
```typescript
interface RoutineBuilderProps {
  routine?: Routine;
  onSave: (routine: Routine) => void;
}

interface Routine {
  id: string;
  name: string;
  cron: string;
  steps: RoutineStep[];
  enabled: boolean;
}

interface RoutineStep {
  type: 'pet' | 'treat' | 'play' | 'sit_drill' | 'fetch' | 'wait';
  duration?: number;
  params?: Record<string, any>;
}
```

Responsibilities:
- Drag-and-drop interface for step ordering
- Cron expression builder/validator
- Step parameter configuration
- Save and enable/disable routines

#### Event Feed Component
```typescript
interface EventFeedProps {
  events: Event[];
  onEventClick: (event: Event) => void;
}

interface Event {
  id: string;
  timestamp: Date;
  type: EventType;
  data: Record<string, any>;
  videoTimestampMs?: number;
}

type EventType = 
  | 'dog_detected'
  | 'sit' | 'stand' | 'lie'
  | 'fetch_return'
  | 'bark' | 'howl' | 'whine'
  | 'person_entered'
  | 'clip_saved'
  | 'bookmark';
```

Responsibilities:
- Real-time event stream via WebSocket
- Emoji markers for event types
- Click to jump to video timestamp
- Filter by event type

#### Robot Action Bar Component
```typescript
interface RobotActionBarProps {
  deviceStatus: 'connected' | 'offline';
  onCommand: (command: RobotCommand) => void;
}

interface RobotCommand {
  type: 'pet' | 'treat' | 'fetch';
  params?: Record<string, any>;
}
```

Responsibilities:
- Display action buttons (pet, treat, fetch)
- Show "not connected" state when device offline
- Disable buttons when device unavailable
- Display tooltips explaining future functionality

### Backend API Endpoints

#### Video Streaming
```python
# MJPEG fallback stream
GET /video/mjpeg
Response: multipart/x-mixed-replace stream

# WebRTC signaling
POST /video/webrtc/offer
Request: { sdp: string, type: "offer" }
Response: { sdp: string, type: "answer" }

GET /video/webrtc/ice-candidates
Response: Server-Sent Events stream of ICE candidates
```

#### Status and Telemetry
```python
GET /api/status
Response: {
  device: "offline" | "connected",
  video: "webrtc" | "mjpeg",
  fps: number,
  latencyMs: number,
  aiModels: {
    detector: string,
    actionRecognizer: string,
    poseEstimator: string
  }
}
```

#### Events
```python
# WebSocket for real-time events
WS /ws/ui
Messages: {
  type: "event" | "overlay" | "telemetry",
  data: any
}

# REST endpoint for historical events
GET /api/events?from={iso_timestamp}&to={iso_timestamp}&type={event_type}
Response: {
  events: Event[],
  total: number
}
```

#### Media Management
```python
POST /api/snapshots
Request: {
  timestamp: string,
  labels?: string[],
  note?: string
}
Response: {
  id: string,
  s3Uri: string,
  previewUrl: string
}

POST /api/clips
Request: {
  startTimestamp: string,
  endTimestamp: string,
  labels?: string[]
}
Response: {
  id: string,
  jobId: string,
  status: "queued" | "processing" | "complete"
}

GET /api/clips/{id}
Response: {
  id: string,
  startTimestamp: string,
  durationMs: number,
  s3Uri: string,
  previewPng: string,
  labels: string[],
  shareUrl?: string
}

DELETE /api/clips/{id}
Response: { success: boolean }
```

#### Routines
```python
GET /api/routines
Response: {
  routines: Routine[]
}

POST /api/routines
Request: Routine
Response: Routine

PUT /api/routines/{id}
Request: Partial<Routine>
Response: Routine

DELETE /api/routines/{id}
Response: { success: boolean }
```

#### Robot Commands (Stub)
```python
POST /api/commands
Request: {
  type: "pet" | "treat" | "fetch",
  params?: Record<string, any>
}
Response: {
  status: 501,
  message: "Robot not connected"
}
```

#### AI Models
```python
GET /api/models
Response: {
  available: Model[],
  active: {
    detector: string,
    actionRecognizer: string,
    poseEstimator: string
  }
}

POST /api/models/switch
Request: {
  detector?: string,
  actionRecognizer?: string,
  poseEstimator?: string
}
Response: {
  success: boolean,
  active: ModelConfig
}
```

#### Analytics
```python
GET /api/analytics/daily?from={date}&to={date}
Response: {
  metrics: DailyMetrics[]
}

GET /api/analytics/streaks
Response: {
  sitStreak: number,
  recallStreak: number,
  badges: Badge[]
}
```
