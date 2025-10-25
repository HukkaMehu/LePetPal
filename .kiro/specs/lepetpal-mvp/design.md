# Design Document

## Overview

LePetPal MVP is architected as a distributed system with clear separation between backend robotics services and frontend web client. The design prioritizes parallel development through a frozen REST API contract, real-time state synchronization via Server-Sent Events, and safety-first command execution. The system supports two core workflows: treat dispensing (servo actuation + vision-guided retrieval) and ball play (multi-phase arm manipulation), with Go Home interrupt capability at any point.

### Key Design Principles

- **Contract-First Integration**: Frozen API specification enables independent parallel development
- **Single Active Command**: State machine enforces one command at a time with busy rejection
- **Real-Time Feedback**: SSE primary, polling fallback for universal client support
- **Safety First**: Go Home preempts all operations; throw macro gated by state validation
- **Minimal Dependencies**: MJPEG over WebRTC, in-memory state over database, mock adapters for hardware

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend Client                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Config Panel │  │ Video Panel  │  │ Command Bar  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────────────────────────────────────────┐      │
│  │         SSE Client (with polling fallback)        │      │
│  └──────────────────────────────────────────────────┘      │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/SSE
                         │
┌────────────────────────┴────────────────────────────────────┐
│                      Backend Service                         │
│  ┌──────────────────────────────────────────────────┐      │
│  │              Flask REST API Server                │      │
│  │  /health  /video_feed  /command  /events         │      │
│  │  /status/{id}  /dispense_treat  /speak           │      │
│  └─────────┬────────────────────────────────────────┘      │
│            │                                                 │
│  ┌─────────┴──────────┐  ┌──────────────────────┐         │
│  │ Command State      │  │  MJPEG Stream        │         │
│  │ Machine            │  │  Generator           │         │
│  │ (In-Memory)        │  │  (with overlays)     │         │
│  └─────────┬──────────┘  └──────────┬───────────┘         │
│            │                         │                      │
│  ┌─────────┴─────────────────────────┴───────────┐        │
│  │          Command Loop + Inference              │        │
│  │  (Vision Model, Phase Execution, Timeouts)     │        │
│  └─────────┬──────────────────────────────────────┘        │
│            │                                                 │
│  ┌─────────┴──────────────────────────────────────┐        │
│  │           Hardware Adapter Layer                │        │
│  │  LerobotArm  ServoController  TTS  Camera      │        │
│  └────────────────────────────────────────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

### Communication Flow

**Command Execution Flow:**
1. Frontend sends POST `/command` with command type
2. Backend validates, assigns request_id, returns 202 Accepted
3. Command State Machine transitions through phases
4. Each transition emits SSE event to `/events` stream
5. Frontend receives events, updates UI in real-time
6. Final state (success/failed/timeout) closes command lifecycle

**Video Streaming Flow:**
1. Frontend renders `<img>` tag pointing to `/video_feed?width=1280&height=720&overlays=1`
2. Backend captures frames from camera at 15+ FPS
3. Overlay renderer adds detection boxes, zones, confidence scores
4. MJPEG encoder streams multipart/x-mixed-replace response
5. Browser continuously updates image element

**SSE with Polling Fallback:**
1. Frontend attempts SSE connection to `/events` on mount
2. If successful, listens for `command_update` events
3. If SSE fails/unsupported, falls back to polling `/status/{request_id}` every 500ms
4. Exponential backoff on SSE reconnection (500ms → 1s → 2s → 4s)

## Components and Interfaces

### Backend Service

#### REST API Endpoints

**GET /health**
```json
Response 200:
{
  "status": "ok",
  "api": 1,
  "version": "v0.1"
}
```

**GET /video_feed**
```
Query Parameters:
  - width: int (default 1280)
  - height: int (default 720)
  - overlays: int (0 or 1, default 1)

Response: multipart/x-mixed-replace; boundary=frame
Content-Type: image/jpeg (per frame)
```

**POST /command**
```json
Request:
{
  "command": "pick up the ball" | "get the treat" | "go home" | "throw ball"
}

Response 202:
{
  "request_id": "uuid-v4",
  "status": "accepted"
}

Response 409:
{
  "error": "busy",
  "message": "Another command is currently executing"
}

Response 400:
{
  "error": "invalid",
  "message": "Unknown command type"
}
```

**GET /events**
```
Response: text/event-stream

Event Format:
event: command_update
data: {
  "request_id": "uuid",
  "state": "executing" | "completed" | "failed" | "timeout" | "interrupted",
  "phase": "detect" | "approach" | "grasp" | "lift" | "drop" | "ready_to_throw" | null,
  "confidence": 0.0-1.0,
  "message": "Human-readable status",
  "duration_ms": 1234
}
```

**GET /status/{request_id}**
```json
Response 200:
{
  "state": "executing" | "completed" | "failed" | "timeout" | "interrupted",
  "phase": "detect" | null,
  "confidence": 0.85,
  "message": "Approaching ball",
  "duration_ms": 1234
}

Response 404:
{
  "error": "not_found",
  "message": "Request ID not found"
}
```

**POST /dispense_treat**
```json
Request:
{
  "duration_ms": 1000
}

Response 200:
{
  "status": "ok"
}
```

**POST /speak**
```json
Request:
{
  "text": "Good dog!"
}

Response 200:
{
  "status": "ok"
}
```

#### Command State Machine

**States:**
- `idle`: No active command
- `executing`: Command in progress
- `completed`: Command succeeded
- `failed`: Command failed (detection, grasp, etc.)
- `timeout`: Command exceeded timeout threshold
- `interrupted`: Command preempted by Go Home

**Phases (for ball manipulation):**
- `detect`: Vision model locating ball
- `approach`: Arm moving toward ball
- `grasp`: Gripper closing on ball
- `lift`: Arm lifting ball
- `drop`: Arm moving to bowl and releasing
- `ready_to_throw`: Arm positioned for throw (optional)

**Transitions:**
```
idle → executing (on command acceptance)
executing → completed (phase sequence success)
executing → failed (detection/grasp failure)
executing → timeout (exceeds timeout_ms)
executing → interrupted (Go Home received)
any_state → executing (Go Home preempts)
```

**State Storage:**
```python
{
  "request_id": str,
  "command": str,
  "state": str,
  "phase": str | None,
  "confidence": float,
  "message": str,
  "start_time": float,
  "timeout_ms": int,
  "phases_completed": List[str]
}
```

#### Hardware Adapter Layer

**LerobotArm Interface:**
```python
class LerobotArm:
    def home(self) -> None:
        """Move arm to home position"""
    
    def send_joint_targets(self, positions: List[float]) -> None:
        """Send joint angle targets"""
    
    def get_current_position(self) -> List[float]:
        """Read current joint angles"""
    
    def check_joint_limits(self, positions: List[float]) -> bool:
        """Validate positions within safe ranges"""
```

**ServoController Interface:**
```python
class ServoController:
    def dispense(self, duration_ms: int) -> None:
        """Actuate SG90 servo for specified duration"""
    
    def calibrate(self) -> None:
        """Set servo to neutral position"""
```

**TTS Interface:**
```python
class TTS:
    def speak(self, text: str) -> None:
        """Synthesize and play speech"""
```

**Camera Interface:**
```python
class Camera:
    def get_frame(self) -> np.ndarray:
        """Capture single frame"""
    
    def set_resolution(self, width: int, height: int) -> None:
        """Configure capture resolution"""
```

**Mock Implementations:**
- All adapters have mock versions for development without hardware
- Mocks return synthetic data and log operations
- Configurable via `USE_MOCK_HARDWARE` environment variable

#### Command Loop

**Execution Thread:**
```python
while command_active:
    current_phase = get_next_phase()
    
    if current_phase == "detect":
        result = vision_model.detect_object(frame)
        if result.confidence < CONFIDENCE_THRESHOLD:
            transition_to_failed("Detection confidence too low")
            break
        update_state(phase="detect", confidence=result.confidence)
    
    elif current_phase == "approach":
        target_position = calculate_approach_position(detection)
        arm.send_joint_targets(target_position)
        wait_for_position_reached(timeout=5.0)
        update_state(phase="approach")
    
    # ... other phases
    
    if elapsed_time > timeout_ms:
        transition_to_timeout()
        break
    
    if interrupt_requested:
        transition_to_interrupted()
        break
```

**Confidence Gating:**
- Detection phase requires confidence ≥ 0.7 (configurable)
- Grasp validation checks gripper pressure sensor
- Each phase has retry limit (default 2 attempts)

**Timeout Management:**
- Default timeout: 30 seconds per command
- Per-phase timeouts: detect (10s), approach (5s), grasp (5s)
- Timeout triggers state transition and SSE event

### Frontend Client

#### Component Structure

**ConfigPanel:**
- Input field for base URL (e.g., `http://192.168.1.100:5000`)
- Optional token input for authentication
- Save button persists to `localStorage`
- Connection test button validates `/health` endpoint

**VideoPanel:**
- `<img>` element with `src={baseUrl}/video_feed?width=1280&height=720&overlays=1`
- Error overlay when stream unavailable
- Loading spinner during initial connection
- Responsive sizing with aspect ratio preservation

**CommandBar:**
- Preset buttons: "Play with Ball", "Give Treat", "Go Home", "Speak"
- Button states: enabled, disabled (during execution), loading
- Go Home always enabled (interrupt capability)
- Custom command input (optional, for advanced users)

**StatusDisplay:**
- Global status chip: Idle (green), Executing (blue), Error (red)
- Phase indicator during execution (e.g., "Detecting ball...")
- Confidence meter (progress bar, 0-100%)
- Duration counter (elapsed time in seconds)
- Final state banner (success/failure with message)

**SSEClient:**
```typescript
class SSEClient {
  private eventSource: EventSource | null;
  private fallbackInterval: NodeJS.Timeout | null;
  
  connect(baseUrl: string): void {
    try {
      this.eventSource = new EventSource(`${baseUrl}/events`);
      this.eventSource.addEventListener('command_update', this.handleUpdate);
      this.eventSource.onerror = this.handleError;
    } catch (error) {
      this.startPollingFallback();
    }
  }
  
  private startPollingFallback(): void {
    this.fallbackInterval = setInterval(() => {
      if (this.currentRequestId) {
        fetch(`${baseUrl}/status/${this.currentRequestId}`)
          .then(res => res.json())
          .then(this.handleUpdate);
      }
    }, 500);
  }
  
  private handleUpdate(data: CommandUpdate): void {
    // Update UI state
    // Stop polling if final state reached
  }
  
  reconnect(): void {
    // Exponential backoff: 500ms, 1s, 2s, 4s, 8s (max)
  }
}
```

#### State Management

**React Context:**
```typescript
interface AppState {
  config: {
    baseUrl: string;
    token?: string;
  };
  connection: {
    status: 'disconnected' | 'connected' | 'error';
    sseSupported: boolean;
  };
  command: {
    active: boolean;
    requestId?: string;
    state: CommandState;
    phase?: string;
    confidence?: number;
    message?: string;
    durationMs?: number;
  };
  errors: Array<{
    id: string;
    message: string;
    timestamp: number;
  }>;
}
```

**Actions:**
- `setConfig(baseUrl, token)`: Update and persist configuration
- `executeCommand(command)`: POST to `/command`, handle response
- `updateCommandState(data)`: Process SSE/polling updates
- `interruptCommand()`: Send Go Home command
- `addError(message)`: Display error toast
- `clearError(id)`: Dismiss error notification

#### Error Handling

**Retry Logic:**
```typescript
async function executeCommandWithRetry(command: string): Promise<void> {
  let attempt = 0;
  let delay = 500;
  
  while (attempt < 5) {
    try {
      const response = await fetch(`${baseUrl}/command`, {
        method: 'POST',
        body: JSON.stringify({ command }),
        headers: { 'Content-Type': 'application/json' }
      });
      
      if (response.status === 409) {
        // Busy - retry with backoff
        await sleep(delay + Math.random() * 200); // jitter
        delay = Math.min(delay * 2, 2000);
        attempt++;
        continue;
      }
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      if (attempt === 4) throw error;
      attempt++;
    }
  }
}
```

**Error Display:**
- Toast notifications for transient errors (auto-dismiss after 5s)
- Persistent banner for connection errors (manual dismiss)
- Inline validation for config panel
- Error codes mapped to user-friendly messages

## Data Models

### Command Request
```typescript
interface CommandRequest {
  command: 'pick up the ball' | 'get the treat' | 'go home' | 'throw ball';
}
```

### Command Response
```typescript
interface CommandResponse {
  request_id: string;
  status: 'accepted';
}
```

### Command Update Event
```typescript
interface CommandUpdate {
  request_id: string;
  state: 'executing' | 'completed' | 'failed' | 'timeout' | 'interrupted';
  phase?: 'detect' | 'approach' | 'grasp' | 'lift' | 'drop' | 'ready_to_throw';
  confidence?: number; // 0.0 - 1.0
  message?: string;
  duration_ms?: number;
}
```

### Health Response
```typescript
interface HealthResponse {
  status: 'ok';
  api: number;
  version: string;
}
```

### Error Response
```typescript
interface ErrorResponse {
  error: 'invalid' | 'busy' | 'not_found' | 'internal';
  message: string;
}
```

## Error Handling

### Backend Error Classification

**400 Invalid Request:**
- Unknown command type
- Missing required parameters
- Invalid parameter values (e.g., negative duration_ms)
- Malformed JSON body

**409 Busy:**
- Command submitted while another is executing
- Exception: Go Home always accepted (preempts current command)

**500 Internal Error:**
- Hardware adapter failure
- Vision model crash
- Unexpected exception in command loop
- File system errors (logging, calibration)

**Error Response Format:**
```json
{
  "error": "error_code",
  "message": "Human-readable description",
  "request_id": "uuid (if applicable)"
}
```

### Frontend Error Handling

**Network Errors:**
- Connection timeout: Retry with exponential backoff
- DNS failure: Display "Cannot reach server" message
- CORS error: Prompt user to check backend CORS configuration

**API Errors:**
- 400: Display validation error inline
- 409: Automatic retry with backoff (transparent to user)
- 500: Display "Server error, please try again" toast

**SSE Errors:**
- Connection drop: Attempt reconnect with backoff
- Parse error: Log and continue (don't crash UI)
- Fallback to polling if SSE repeatedly fails

### Logging

**Backend:**
```json
{
  "timestamp": "2025-10-24T10:30:45.123Z",
  "level": "INFO",
  "request_id": "uuid",
  "event": "state_transition",
  "from_state": "executing",
  "to_state": "completed",
  "phase": "drop",
  "duration_ms": 12345,
  "confidence": 0.92
}
```

**Frontend:**
- Console logging for development (disabled in production)
- Error tracking via browser console.error
- Optional Sentry integration (out of scope for MVP)

## Testing Strategy

### Backend Testing

**Unit Tests:**
- Command State Machine transitions
- Hardware adapter mock implementations
- API endpoint request/response validation
- Confidence gating logic
- Timeout calculation

**Integration Tests:**
- End-to-end command execution with mocks
- SSE event emission and formatting
- MJPEG stream generation
- Go Home interrupt behavior
- Error response codes

**Manual Testing:**
- Video stream visual inspection (overlays, frame rate)
- Servo actuation with physical hardware
- TTS audio output quality
- Arm movement safety (joint limits, collision avoidance)
- Multi-client SSE broadcast

**Test Fixtures:**
```json
// fixtures/command_responses.json
{
  "accepted": {
    "request_id": "test-uuid-1",
    "status": "accepted"
  },
  "busy": {
    "error": "busy",
    "message": "Another command is currently executing"
  },
  "failed": {
    "request_id": "test-uuid-2",
    "state": "failed",
    "message": "Ball detection confidence too low",
    "duration_ms": 5000
  }
}
```

### Frontend Testing

**Component Tests:**
- ConfigPanel save/load from localStorage
- CommandBar button enable/disable logic
- StatusDisplay state rendering
- SSEClient connection and reconnection
- Error toast display and dismissal

**Integration Tests:**
- Full command execution flow (mock API)
- SSE event handling and UI updates
- Polling fallback activation
- Retry logic with 409 responses
- Video feed error handling

**Manual Testing:**
- Mobile responsive layout (320px - 1920px)
- Touch interaction on mobile devices
- Video stream rendering across browsers
- SSE support detection
- Network interruption recovery

**Test Scenarios:**
```typescript
// tests/scenarios/give-treat-flow.test.ts
test('Give Treat executes two-step flow', async () => {
  // 1. Click "Give Treat" button
  // 2. Verify POST /dispense_treat called
  // 3. Verify POST /command with "get the treat"
  // 4. Mock SSE events: executing → completed
  // 5. Verify success banner displayed
});
```

### Acceptance Testing

**AT-1: Video Stream**
- Start backend with camera
- Open frontend, configure base URL
- Verify video renders at ≥15 FPS
- Verify overlays visible when enabled
- Verify stream recovers after network interruption

**AT-2: Speak**
- Click "Speak" preset
- Verify audio output within 1 second
- Verify success confirmation in UI

**AT-3: Dispense Treat**
- Click "Give Treat" button
- Verify servo actuates for configured duration
- Verify "get the treat" command executes
- Verify success after 3 consecutive attempts

**AT-4: Pick Ball**
- Place ball in 3 different positions
- Execute "Play with Ball" command
- Verify ≥2/3 success rate
- Fallback: Verify scripted sequence works if model unavailable

**AT-5: Give Treat End-to-End**
- Execute "Give Treat" 3 times consecutively
- Verify 100% success rate
- Verify treat dispensed and retrieved each time

**AT-6: Safety Interrupt**
- Start "Play with Ball" command
- Click "Go Home" during execution
- Verify arm returns to home within 1 second
- Verify interrupted state in UI

**AT-7: Optional Sentry**
- Enable Sentry mode (OFF by default)
- Trigger auto-detection
- Verify single execution with cooldown
- Verify manual commands still work

## Configuration

### Backend Environment Variables

```bash
# .env.example
PORT=5000
CAMERA_INDEX=0
STREAM_WIDTH=1280
STREAM_HEIGHT=720
STREAM_FPS=15

# Detection thresholds
CONFIDENCE_THRESHOLD=0.7
DETECTION_TIMEOUT_MS=10000

# Hardware
USE_MOCK_HARDWARE=true
SERVO_PIN=18
SERVO_DISPENSE_DURATION_MS=1000

# Safety
JOINT_LIMIT_MARGIN=0.1
GO_HOME_TIMEOUT_MS=1000

# Logging
LOG_LEVEL=INFO
LOG_FILE=lepetpal.log

# Optional
API_TOKEN=secret-token-here
CORS_ORIGINS=http://localhost:3000,http://192.168.1.50:3000
```

### Frontend Environment Variables

```bash
# .env.local.example
NEXT_PUBLIC_API_BASE=http://localhost:5000
NEXT_PUBLIC_DEFAULT_VIDEO_WIDTH=1280
NEXT_PUBLIC_DEFAULT_VIDEO_HEIGHT=720
NEXT_PUBLIC_SSE_RECONNECT_MAX_DELAY=8000
```

### Calibration Persistence

**Backend Calibration File:**
```json
// calibration.json
{
  "camera": {
    "roi": {
      "x": 100,
      "y": 50,
      "width": 800,
      "height": 600
    }
  },
  "zones": {
    "bowl": {
      "x": 640,
      "y": 360,
      "radius": 100
    },
    "treat_dispenser": {
      "x": 200,
      "y": 100
    }
  },
  "arm": {
    "home_position": [0.0, -1.57, 1.57, 0.0, 0.0, 0.0],
    "ready_to_throw_position": [0.5, -0.8, 1.2, 0.0, 0.0, 0.0]
  }
}
```

## Security Considerations

### Authentication (Optional)

**Token-Based Auth:**
- Optional `X-LePetPal-Token` header
- Validated against `API_TOKEN` environment variable
- Returns 401 Unauthorized if token invalid
- Disabled by default for MVP (LAN deployment)

### CORS Configuration

**Allowed Origins:**
- Configurable via `CORS_ORIGINS` environment variable
- Default: `*` (allow all) for hackathon ease
- Production: Restrict to specific frontend domains

### Input Validation

**Command Validation:**
- Whitelist of allowed command strings
- Parameter type checking (duration_ms must be positive integer)
- Maximum text length for speak (prevent TTS abuse)

**Video Feed:**
- Width/height clamped to reasonable ranges (320-1920)
- Overlays parameter boolean coercion

### Safety Constraints

**Hardware Limits:**
- Joint angle validation before movement
- Velocity limits on arm motion
- Emergency stop via Go Home
- Throw macro only from validated state

**Rate Limiting:**
- Single active command prevents command spam
- Optional: Per-client rate limit (future enhancement)

## Performance Considerations

### Backend Optimization

**Video Streaming:**
- MJPEG chosen over WebRTC for simplicity (acceptable latency for MVP)
- Frame encoding in separate thread to avoid blocking
- Overlay rendering optimized with OpenCV
- Target: 15 FPS minimum, 30 FPS ideal

**Command Loop:**
- Inference at 10-20 Hz (balance accuracy vs latency)
- Non-blocking state updates (async SSE broadcast)
- Timeout enforcement prevents hung commands

**Memory Management:**
- In-memory state (no database for MVP)
- Command history limited to last 100 requests
- Frame buffer size limited to prevent memory leak

### Frontend Optimization

**Rendering:**
- Video feed via native `<img>` tag (browser-optimized)
- React state updates batched for SSE events
- Debounced status polling (500ms minimum)

**Network:**
- SSE preferred over polling (reduces request overhead)
- Exponential backoff prevents thundering herd
- Connection reuse for API calls

**Bundle Size:**
- Next.js code splitting
- Minimal dependencies (no heavy UI libraries)
- Target: <500KB initial bundle

## Deployment

### Backend Deployment

**Requirements:**
- Python 3.9+
- Flask, OpenCV, NumPy
- Hardware drivers (LeRobot SDK, RPi.GPIO for servo)
- Optional: CUDA for GPU-accelerated inference

**Startup:**
```bash
python run_backend.py
# Loads .env, initializes hardware, starts Flask server
```

**Health Check:**
```bash
curl http://localhost:5000/health
# Should return {"status":"ok","api":1,"version":"v0.1"}
```

### Frontend Deployment

**Requirements:**
- Node.js 18+
- Next.js 14

**Development:**
```bash
npm run dev
# Starts dev server on http://localhost:3000
```

**Production:**
```bash
npm run build
npm start
# Or deploy to Vercel/Netlify
```

### Integration Checkpoints

**IC-0: Contract Sign-Off**
- Both engineers review and approve API specification
- No changes allowed without mutual agreement and version bump

**IC-1: LAN with Stubs**
- Backend serves mock video feed and accepts commands
- Frontend renders video and sends commands
- SSE events show mock phase transitions

**IC-2: Servo + Speak**
- Physical servo actuation working
- TTS audio output functional
- Give Treat flow (dispense + command) end-to-end

**IC-3: Model-in-Loop**
- Vision model integrated for ball/treat detection
- Command loop executes phases with real inference
- Go Home interrupt verified

**IC-4: Demo Script**
- Full rehearsal of demo scenarios
- Tune confidence thresholds and timeouts
- Optional throw macro if guards pass

## Future Enhancements (Out of Scope for MVP)

- WebRTC for lower-latency video
- WebSocket for bidirectional communication
- Database for command history and analytics
- Multi-user support with authentication
- Routine scheduling (e.g., "dispense treat every 2 hours")
- AI coach mode (autonomous behavior suggestions)
- Cloud deployment with remote access
- Mobile native apps (iOS/Android)
- CI/CD pipeline with automated testing
- OpenAPI spec generation and client SDK
