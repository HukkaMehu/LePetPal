# Design Document: Frontend Migration

## Overview

This document outlines the design for migrating from the existing Next.js frontend to the Pet Training Web App (Vite + React) frontend while maintaining all backend functionality. The migration will preserve the beautiful UI/UX of the Pet Training Web App without any layout changes, while connecting it to the existing FastAPI backend, PostgreSQL database, AI service, and WebSocket infrastructure.

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  Pet Training Web App (Vite + React)        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Pages      │  │  Components  │  │   Services   │     │
│  │  - Live      │  │  - VideoPlayer│  │  - API Client│     │
│  │  - Gallery   │  │  - Timeline  │  │  - WebSocket │     │
│  │  - Analytics │  │  - CoachTips │  │  - Storage   │     │
│  │  - Routines  │  │  - ActionPanel│  │              │     │
│  │  - Settings  │  │  - EventFeed │  │              │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ HTTP/WebSocket
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Backend Services                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   FastAPI    │  │  PostgreSQL  │  │  AI Service  │     │
│  │   Backend    │  │   Database   │  │   (Coach)    │     │
│  │              │  │              │  │              │     │
│  │  - REST APIs │  │  - Events    │  │  - Vision    │     │
│  │  - WebSocket │  │  - Routines  │  │  - Models    │     │
│  │  - Video     │  │  - Analytics │  │              │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

**Frontend (Pet Training Web App)**
- **Framework**: Vite + React 18
- **UI Components**: Radix UI primitives
- **Styling**: Tailwind CSS
- **Charts**: Recharts
- **State Management**: React hooks (useState, useEffect, useContext)
- **HTTP Client**: Fetch API / Axios
- **WebSocket**: Native WebSocket API
- **Build Tool**: Vite

**Backend (Existing)**
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **WebSocket**: FastAPI WebSocket + Redis pub/sub
- **Video Streaming**: MJPEG / WebRTC
- **AI Service**: Separate FastAPI service
- **Storage**: S3/MinIO for media files

## Components and Interfaces

### 1. API Service Layer

Create a centralized API service to handle all backend communication.

**File**: `src/services/api.ts`

```typescript
interface APIConfig {
  baseURL: string;
  aiServiceURL: string;
  wsURL: string;
}

class APIClient {
  private config: APIConfig;
  
  constructor(config: APIConfig);
  
  // Events API
  getEvents(params: EventQueryParams): Promise<EventsResponse>;
  createEvent(event: EventCreate): Promise<Event>;
  
  // Routines API
  getRoutines(): Promise<Routine[]>;
  createRoutine(routine: RoutineCreate): Promise<Routine>;
  updateRoutine(id: string, routine: RoutineUpdate): Promise<Routine>;
  deleteRoutine(id: string): Promise<void>;
  triggerRoutine(id: string): Promise<void>;
  
  // Analytics API
  getDailyMetrics(params: MetricsQuery): Promise<DailyMetrics[]>;
  getStreaks(userId: string): Promise<StreaksResponse>;
  getAnalyticsSummary(days: number): Promise<AnalyticsSummary>;
  
  // Media API
  getClips(params: MediaQuery): Promise<ClipsResponse>;
  getSnapshots(params: MediaQuery): Promise<SnapshotsResponse>;
  createSnapshot(data: SnapshotCreate): Promise<Snapshot>;
  
  // Status API
  getSystemStatus(): Promise<SystemStatus>;
  
  // Models API
  getModels(): Promise<ModelsListResponse>;
  switchModels(request: ModelSwitchRequest): Promise<ModelSwitchResponse>;
  
  // Coach API (AI Service)
  sendCoachMessage(message: string): Promise<CoachResponse>;
  streamCoachMessage(message: string): AsyncGenerator<string>;
}
```

### 2. WebSocket Service

Handle real-time updates from the backend.

**File**: `src/services/websocket.ts`

```typescript
interface WebSocketMessage {
  type: 'event' | 'overlay' | 'telemetry';
  event_type?: string;
  overlay_type?: string;
  data: any;
}

class WebSocketService {
  private ws: WebSocket | null;
  private reconnectAttempts: number;
  private listeners: Map<string, Set<Function>>;
  
  connect(url: string): void;
  disconnect(): void;
  subscribe(eventType: string, callback: Function): () => void;
  unsubscribe(eventType: string, callback: Function): void;
  
  // Event handlers
  private handleMessage(message: WebSocketMessage): void;
  private handleError(error: Event): void;
  private handleClose(): void;
  private reconnect(): void;
}
```

### 3. Data Transformation Layer

Transform backend data formats to match Pet Training Web App expectations.

**File**: `src/services/adapters.ts`

```typescript
// Transform backend event to frontend event format
function adaptEvent(backendEvent: BackendEvent): Event {
  return {
    id: backendEvent.id,
    type: mapEventType(backendEvent.type),
    timestamp: new Date(backendEvent.ts),
    confidence: backendEvent.data?.confidence,
    duration: backendEvent.data?.duration,
  };
}

// Transform backend analytics to frontend format
function adaptAnalytics(backendData: BackendAnalytics): AnalyticsData {
  return {
    timeInFrame: adaptTimeInFrame(backendData.hourly_data),
    activityLevel: adaptActivityLevel(backendData.daily_metrics),
    behaviors: adaptBehaviors(backendData.summary),
    fetchSuccess: adaptFetchSuccess(backendData.daily_metrics),
    barkFrequency: adaptBarkFrequency(backendData.hourly_data),
    skillProgress: adaptSkillProgress(backendData.streaks),
  };
}

// Transform backend routine to frontend format
function adaptRoutine(backendRoutine: BackendRoutine): Routine {
  return {
    id: backendRoutine.id,
    name: backendRoutine.name,
    steps: backendRoutine.steps.map(adaptRoutineStep),
    schedule: backendRoutine.cron,
    enabled: backendRoutine.enabled,
    lastRun: backendRoutine.last_run ? new Date(backendRoutine.last_run) : undefined,
  };
}

// Transform backend media to frontend format
function adaptMediaItem(backendItem: BackendClip | BackendSnapshot): MediaItem {
  return {
    id: backendItem.id,
    type: 'clip' in backendItem ? 'clip' : 'snapshot',
    url: backendItem.preview_url || backendItem.s3_uri,
    thumbnail: backendItem.preview_url,
    timestamp: new Date(backendItem.start_ts || backendItem.ts),
    duration: backendItem.duration_ms,
    tags: backendItem.labels || [],
    events: [], // Fetch separately if needed
  };
}
```

### 4. React Hooks for Data Fetching

Create custom hooks for data management.

**File**: `src/hooks/useBackendData.ts`

```typescript
// Hook for fetching events with real-time updates
function useEvents(params?: EventQueryParams) {
  const [events, setEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  
  useEffect(() => {
    // Fetch initial events
    // Subscribe to WebSocket updates
    // Cleanup on unmount
  }, [params]);
  
  return { events, loading, error };
}

// Hook for analytics data
function useAnalytics(days: number = 7) {
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    // Fetch analytics data
  }, [days]);
  
  return { data, loading };
}

// Hook for routines
function useRoutines() {
  const [routines, setRoutines] = useState<Routine[]>([]);
  const [loading, setLoading] = useState(true);
  
  const createRoutine = async (routine: RoutineCreate) => { /* ... */ };
  const updateRoutine = async (id: string, routine: RoutineUpdate) => { /* ... */ };
  const deleteRoutine = async (id: string) => { /* ... */ };
  const triggerRoutine = async (id: string) => { /* ... */ };
  
  return { routines, loading, createRoutine, updateRoutine, deleteRoutine, triggerRoutine };
}

// Hook for system status
function useSystemStatus() {
  const [status, setStatus] = useState<SystemStatus | null>(null);
  
  useEffect(() => {
    // Fetch status
    // Subscribe to telemetry updates
  }, []);
  
  return status;
}
```

### 5. Environment Configuration

**File**: `.env`

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_AI_SERVICE_URL=http://localhost:8001
VITE_WS_URL=ws://localhost:8000/ws
VITE_VIDEO_STREAM_URL=http://localhost:8000/video/mjpeg
```

**File**: `src/config/env.ts`

```typescript
export const config = {
  apiBaseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  aiServiceURL: import.meta.env.VITE_AI_SERVICE_URL || 'http://localhost:8001',
  wsURL: import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws',
  videoStreamURL: import.meta.env.VITE_VIDEO_STREAM_URL || 'http://localhost:8000/video/mjpeg',
};
```

## Data Models

### Frontend Type Definitions

**File**: `src/types/index.ts`

```typescript
// Event types
export interface Event {
  id: string;
  type: 'sit' | 'fetch' | 'treat' | 'bark' | 'pet' | 'active' | 'calm' | 'stand' | 'lie';
  timestamp: Date;
  thumbnail?: string;
  confidence?: number;
  duration?: number;
}

// Media types
export interface MediaItem {
  id: string;
  type: 'snapshot' | 'clip';
  url: string;
  thumbnail: string;
  timestamp: Date;
  duration?: number;
  tags: string[];
  events: Event[];
}

// Analytics types
export interface AnalyticsData {
  timeInFrame: { hour: string; minutes: number }[];
  activityLevel: { date: string; calm: number; active: number }[];
  behaviors: { name: string; count: number }[];
  fetchSuccess: { date: string; success: number; total: number }[];
  barkFrequency: { hour: string; count: number }[];
  skillProgress: { skill: string; success: number; total: number }[];
}

// Routine types
export interface Routine {
  id: string;
  name: string;
  steps: RoutineStep[];
  schedule?: string;
  enabled: boolean;
  lastRun?: Date;
}

export interface RoutineStep {
  id: string;
  action: 'pet' | 'treat' | 'play' | 'sit-drill' | 'wait' | 'fetch';
  duration?: number;
  repeat?: number;
}

// System status types
export interface SystemStatus {
  device: 'connected' | 'offline';
  video: 'webrtc' | 'mjpeg';
  fps: number;
  latencyMs: number;
  aiModels: {
    detector?: string;
    actionRecognizer?: string;
    poseEstimator?: string;
    policy?: string;
  };
  timestamp: string;
}
```

### Backend API Response Types

**File**: `src/types/backend.ts`

```typescript
// Backend event response
export interface BackendEvent {
  id: string;
  user_id: string;
  ts: string;
  type: string;
  data: Record<string, any> | null;
  video_ts_ms: number | null;
  created_at: string;
}

// Backend routine response
export interface BackendRoutine {
  id: string;
  user_id: string;
  name: string;
  cron: string;
  steps: Array<{
    type: string;
    duration?: number;
    params?: Record<string, any>;
  }>;
  enabled: boolean;
  created_at: string;
  updated_at: string;
}

// Backend analytics responses
export interface BackendDailyMetrics {
  date: string;
  sit_count: number;
  stand_count: number;
  lie_count: number;
  fetch_count: number;
  fetch_success_count: number;
  treats_dispensed: number;
  time_in_frame_min: number;
  barks: number;
  howls: number;
  whines: number;
  calm_minutes: number;
}

export interface BackendStreaksResponse {
  sit_streak: number;
  recall_streak: number;
  training_streak: number;
  badges: Array<{
    id: string;
    name: string;
    description: string;
    earned_date: string;
    icon: string;
  }>;
}

// Backend media responses
export interface BackendClip {
  id: string;
  user_id: string;
  start_ts: string;
  duration_ms: number;
  s3_uri: string | null;
  preview_url: string | null;
  labels: string[] | null;
  share_token: string | null;
  share_url: string | null;
  status: 'pending' | 'processing' | 'completed' | 'error';
  created_at: string;
}

export interface BackendSnapshot {
  id: string;
  user_id: string;
  ts: string;
  s3_uri: string;
  preview_url: string;
  labels: string[] | null;
  note: string | null;
  created_at: string;
}
```

## Error Handling

### Error Boundary Component

**File**: `src/components/ErrorBoundary.tsx`

```typescript
class ErrorBoundary extends React.Component<Props, State> {
  // Catch React errors and display fallback UI
  // Log errors to console or error tracking service
}
```

### API Error Handling

```typescript
class APIError extends Error {
  constructor(
    public status: number,
    public message: string,
    public details?: any
  ) {
    super(message);
  }
}

async function handleAPIError(response: Response): Promise<never> {
  const data = await response.json().catch(() => ({}));
  throw new APIError(
    response.status,
    data.detail || response.statusText,
    data
  );
}
```

### Connection Status Handling

```typescript
// Display connection status banner when backend is unavailable
function ConnectionStatusBanner() {
  const [isOnline, setIsOnline] = useState(true);
  
  useEffect(() => {
    // Poll status endpoint
    // Update connection state
  }, []);
  
  if (isOnline) return null;
  
  return (
    <div className="bg-destructive text-destructive-foreground p-2 text-center">
      Connection lost. Attempting to reconnect...
    </div>
  );
}
```

## Testing Strategy

### Unit Tests

- Test data transformation functions (adapters)
- Test custom hooks with mock data
- Test utility functions

**Tools**: Vitest, React Testing Library

### Integration Tests

- Test API service methods with mock backend
- Test WebSocket service connection and message handling
- Test component integration with hooks

### End-to-End Tests

- Test complete user flows (view live stream, create routine, view analytics)
- Test real-time updates via WebSocket
- Test error scenarios (backend offline, network errors)

**Tools**: Playwright or Cypress

### Manual Testing Checklist

- [ ] Live video stream displays correctly
- [ ] Events appear in timeline in real-time
- [ ] Analytics charts display accurate data
- [ ] Routines can be created, edited, and deleted
- [ ] Coach chat responds to messages
- [ ] Gallery displays clips and snapshots
- [ ] Settings persist correctly
- [ ] WebSocket reconnects after disconnect
- [ ] Error messages display appropriately

## Migration Strategy

### Phase 1: Setup and Configuration

1. Set up environment variables
2. Create API service layer
3. Create WebSocket service
4. Create data adapters
5. Create custom hooks

### Phase 2: Component Integration

1. Update LivePage to use real video stream
2. Update Timeline/EventFeed to use real events
3. Update AnalyticsPage to use real analytics data
4. Update RoutinesPage to use real routines API
5. Update GalleryPage to use real media API
6. Update CoachTips to use AI service
7. Update SettingsPage to use models API

### Phase 3: Real-Time Features

1. Integrate WebSocket for event updates
2. Integrate WebSocket for telemetry updates
3. Integrate WebSocket for routine notifications
4. Add connection status monitoring

### Phase 4: Polish and Testing

1. Add error boundaries
2. Add loading states
3. Add error messages
4. Test all features
5. Fix bugs and edge cases

### Phase 5: Deployment

1. Build production bundle
2. Configure production environment variables
3. Deploy to hosting service
4. Test production deployment
5. Monitor for errors

## Performance Considerations

### Optimization Strategies

1. **Lazy Loading**: Load components on demand
2. **Memoization**: Use React.memo for expensive components
3. **Debouncing**: Debounce API calls for search/filter
4. **Pagination**: Implement pagination for large lists
5. **Image Optimization**: Use appropriate image sizes and formats
6. **WebSocket Throttling**: Throttle high-frequency WebSocket messages
7. **Caching**: Cache API responses where appropriate

### Bundle Size Optimization

1. Use dynamic imports for routes
2. Tree-shake unused dependencies
3. Minimize third-party libraries
4. Use production builds

## Security Considerations

1. **API Authentication**: Add authentication tokens to API requests (future)
2. **CORS Configuration**: Ensure backend CORS is properly configured
3. **Input Validation**: Validate user inputs before sending to backend
4. **XSS Prevention**: Sanitize user-generated content
5. **Secure WebSocket**: Use WSS in production
6. **Environment Variables**: Never commit sensitive data to version control

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Production Environment                    │
│                                                              │
│  ┌──────────────┐         ┌──────────────┐                 │
│  │   Frontend   │         │   Backend    │                 │
│  │   (Vite)     │◄────────┤   (FastAPI)  │                 │
│  │              │  HTTP   │              │                 │
│  │  Served by   │  WS     │  + Database  │                 │
│  │  Nginx/CDN   │         │  + AI Service│                 │
│  └──────────────┘         └──────────────┘                 │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Hosting Options

**Frontend**:
- Vercel
- Netlify
- AWS S3 + CloudFront
- Nginx static hosting

**Backend** (existing):
- Docker containers
- AWS EC2/ECS
- DigitalOcean Droplets
- Heroku

## Future Enhancements

1. **Progressive Web App (PWA)**: Add service worker for offline support
2. **Push Notifications**: Add browser push notifications for routine alerts
3. **Multi-user Support**: Add authentication and user management
4. **Mobile App**: Create React Native version using same backend
5. **Advanced Analytics**: Add more detailed analytics and insights
6. **Video Playback**: Add video player for recorded clips
7. **Sharing**: Implement clip sharing functionality
8. **Themes**: Add dark/light theme toggle
9. **Internationalization**: Add multi-language support
10. **Accessibility**: Enhance keyboard navigation and screen reader support
