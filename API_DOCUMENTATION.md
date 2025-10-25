# LePetPal Backend API Documentation

Base URL: `http://localhost:5000` (local) or `https://your-ngrok-url.ngrok-free.app` (public)

---

## Endpoints

### 1. Health Check

**GET** `/health`

Check if the backend is running.

**Response:**
```json
{
  "status": "ok",
  "api": 1,
  "version": "v0.1"
}
```

**Status Codes:**
- `200 OK` - Backend is healthy

**Example:**
```bash
curl https://your-url/health
```

---

### 2. Main Camera Feed (Recommended)

**GET** `/camera`

MJPEG video stream from the main camera (camera 0). This is a **persistent endpoint** that always shows the primary camera with automatic reconnection.

**Query Parameters:**

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `quality` | int | 50 | 1-100 | JPEG quality (lower = faster) |
| `scale` | float | 0.5 | 0.1-1.0 | Scale factor (lower = faster) |
| `fps` | int | 10 | 1-30 | Target frames per second |
| `overlays` | int | 1 | 0 or 1 | Show timestamp overlay |

**Response:**
- Content-Type: `multipart/x-mixed-replace; boundary=frame`
- MJPEG video stream

**Features:**
- ✅ Always shows camera 0 (main camera)
- ✅ Automatic reconnection if camera disconnects
- ✅ Shows last frame if camera temporarily unavailable
- ✅ No synthetic fallback - real camera only

**Examples:**
```bash
# Default (optimized for internet)
curl https://lepetpal.verkkoventure.com/camera

# Ultra-low bandwidth
curl https://lepetpal.verkkoventure.com/camera?quality=30&scale=0.3&fps=5

# High quality
curl https://lepetpal.verkkoventure.com/camera?quality=80&scale=1.0&fps=30
```

**HTML/React:**
```html
<img src="https://lepetpal.verkkoventure.com/camera?quality=50&scale=0.5&fps=10" />
```

---

### 3. Video Feed (Legacy)

**GET** `/video_feed`

MJPEG video stream with camera switching support. **Use `/camera` instead for the main camera.**

**Query Parameters:**

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `camera` | int | 0 | 0-4 | Camera index |
| `width` | int | 1280 | 320-1920 | Camera capture width |
| `height` | int | 720 | 240-1080 | Camera capture height |
| `quality` | int | 50 | 1-100 | JPEG quality (lower = faster) |
| `scale` | float | 0.5 | 0.1-1.0 | Scale factor (lower = faster) |
| `fps` | int | 10 | 1-30 | Target frames per second |
| `overlays` | int | 1 | 0 or 1 | Show timestamp overlay |

**Response:**
- Content-Type: `multipart/x-mixed-replace; boundary=frame`
- MJPEG video stream

**Examples:**
```bash
# Default (optimized for internet)
curl https://your-url/video_feed

# Switch to camera 1
curl https://your-url/video_feed?camera=1

# Ultra-low bandwidth
curl https://your-url/video_feed?quality=30&scale=0.3&fps=5

# High quality (local network)
curl https://your-url/video_feed?quality=80&scale=1.0&fps=30

# No timestamp
curl https://your-url/video_feed?overlays=0
```

**HTML/React:**
```html
<img src="https://your-url/video_feed?quality=50&scale=0.5&fps=10" />
```

---

### 4. Send Command

**POST** `/command`

Send a command to the robot.

**Request Body:**
```json
{
  "prompt": "pick up the ball",
  "options": {}
}
```

**Allowed Prompts:**
- `"pick up the ball"`
- `"get the treat"`
- `"go home"`

**Response (Success):**
```json
{
  "request_id": "uuid-here",
  "status": "accepted"
}
```

**Response (Busy):**
```json
{
  "error": {
    "code": "busy",
    "http": 409,
    "message": "Another command is in progress"
  }
}
```

**Response (Invalid Prompt):**
```json
{
  "error": {
    "code": "invalid",
    "http": 400,
    "message": "Invalid prompt"
  }
}
```

**Status Codes:**
- `202 Accepted` - Command accepted
- `400 Bad Request` - Invalid prompt
- `409 Conflict` - Robot is busy

**Example:**
```bash
curl -X POST https://your-url/command \
  -H "Content-Type: application/json" \
  -d '{"prompt": "pick up the ball", "options": {}}'
```

**JavaScript:**
```javascript
const response = await fetch('https://your-url/command', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ 
    prompt: 'pick up the ball', 
    options: {} 
  })
});
const data = await response.json();
console.log('Request ID:', data.request_id);
```

---

### 5. Get Command Status

**GET** `/status/:request_id`

Poll the status of a command.

**Path Parameters:**
- `request_id` - UUID returned from `/command`

**Response (Executing):**
```json
{
  "state": "executing",
  "phase": "grasp_2",
  "message": "grasp_2",
  "confidence": 0.8
}
```

**Response (Succeeded):**
```json
{
  "state": "succeeded",
  "phase": "ready_2",
  "message": "Completed",
  "confidence": 0.85,
  "duration_ms": 6248
}
```

**Response (Failed):**
```json
{
  "state": "failed",
  "phase": "approach_1",
  "message": "Error message here"
}
```

**Response (Unknown ID):**
```json
{
  "state": "failed",
  "phase": null,
  "message": "unknown request_id"
}
```

**State Values:**
- `"executing"` - Command is running
- `"succeeded"` - Command completed successfully
- `"failed"` - Command failed
- `"aborted"` - Command was interrupted

**Phase Values (for "pick up the ball"):**
- `"detect_1"`, `"detect_2"` - Detecting object
- `"approach_1"`, `"approach_2"`, `"approach_3"` - Moving toward object
- `"grasp_1"`, `"grasp_2"` - Grasping object
- `"lift_1"`, `"lift_2"` - Lifting object
- `"ready_1"`, `"ready_2"` - Ready to throw

**Status Codes:**
- `200 OK` - Always returns 200 (check `state` field)

**Example:**
```bash
curl https://your-url/status/bf45aa1d-2d34-4c64-810c-b3e469943ff6
```

**JavaScript (Polling):**
```javascript
const requestId = 'bf45aa1d-2d34-4c64-810c-b3e469943ff6';

const interval = setInterval(async () => {
  const response = await fetch(`https://your-url/status/${requestId}`);
  const data = await response.json();
  
  console.log(`State: ${data.state}, Phase: ${data.phase}`);
  
  if (data.state === 'succeeded' || data.state === 'failed') {
    clearInterval(interval);
    console.log('Command finished:', data);
  }
}, 500); // Poll every 500ms
```

---

### 6. Dispense Treat

**POST** `/dispense_treat`

Activate the treat dispenser servo.

**Request Body:**
```json
{
  "duration_ms": 600
}
```

**Parameters:**
- `duration_ms` (optional) - Duration in milliseconds (default: 600)

**Response (Success):**
```json
{
  "status": "ok"
}
```

**Response (Error):**
```json
{
  "error": {
    "code": "hardware_error",
    "http": 500,
    "message": "Error message"
  }
}
```

**Status Codes:**
- `200 OK` - Treat dispensed
- `500 Internal Server Error` - Hardware error

**Example:**
```bash
curl -X POST https://your-url/dispense_treat \
  -H "Content-Type: application/json" \
  -d '{"duration_ms": 600}'
```

**JavaScript:**
```javascript
await fetch('https://your-url/dispense_treat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ duration_ms: 600 })
});
```

---

### 7. Text-to-Speech

**POST** `/speak`

Make the robot speak using text-to-speech.

**Request Body:**
```json
{
  "text": "Good boy!"
}
```

**Parameters:**
- `text` (required) - Text to speak

**Response (Success):**
```json
{
  "status": "ok"
}
```

**Response (Empty Text):**
```json
{
  "error": {
    "code": "invalid",
    "http": 400,
    "message": "Missing text"
  }
}
```

**Response (Error):**
```json
{
  "error": {
    "code": "tts_error",
    "http": 500,
    "message": "Error message"
  }
}
```

**Status Codes:**
- `200 OK` - Speech completed
- `400 Bad Request` - Missing or empty text
- `500 Internal Server Error` - TTS error

**Example:**
```bash
curl -X POST https://your-url/speak \
  -H "Content-Type: application/json" \
  -d '{"text": "Good boy!"}'
```

**JavaScript:**
```javascript
await fetch('https://your-url/speak', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ text: 'Good boy!' })
});
```

---

## Complete Workflow Example

### 1. Check Health
```javascript
const health = await fetch('https://your-url/health').then(r => r.json());
console.log('Backend status:', health.status);
```

### 2. Send Command
```javascript
const response = await fetch('https://your-url/command', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ prompt: 'pick up the ball', options: {} })
});
const { request_id } = await response.json();
```

### 3. Poll Status
```javascript
const pollStatus = async (requestId) => {
  const interval = setInterval(async () => {
    const status = await fetch(`https://your-url/status/${requestId}`)
      .then(r => r.json());
    
    console.log(`Phase: ${status.phase}, State: ${status.state}`);
    
    if (status.state === 'succeeded') {
      clearInterval(interval);
      console.log('Command completed!');
      
      // Celebrate!
      await fetch('https://your-url/speak', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: 'Good job!' })
      });
      
      await fetch('https://your-url/dispense_treat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ duration_ms: 600 })
      });
    }
  }, 500);
};

pollStatus(request_id);
```

### 4. Display Video Feed
```html
<img src="https://lepetpal.verkkoventure.com/camera?quality=50&scale=0.5&fps=10" />
```

---

## Error Handling

All endpoints may return errors in this format:
```json
{
  "error": {
    "code": "error_code",
    "http": 400,
    "message": "Human-readable error message"
  }
}
```

**Common Error Codes:**
- `invalid` - Invalid input (400)
- `busy` - Robot is busy (409)
- `hardware_error` - Hardware failure (500)
- `tts_error` - Text-to-speech error (500)

---

## CORS

CORS is enabled for all origins. All endpoints accept:
- `GET`, `POST`, `OPTIONS` methods
- `Content-Type: application/json` header

---

## Rate Limiting

No rate limiting currently implemented (hackathon/demo mode).

For production, consider:
- Max 10 commands per minute
- Max 1 concurrent command
- Video feed bandwidth throttling

---

## Quick Reference

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Health check |
| `/camera` | GET | Main camera stream (recommended) |
| `/video_feed` | GET | Video stream with camera switching |
| `/command` | POST | Send robot command |
| `/status/:id` | GET | Get command status |
| `/dispense_treat` | POST | Dispense treat |
| `/speak` | POST | Text-to-speech |

---

## Testing with cURL

```bash
# Health
curl https://your-url/health

# Video (save to file)
curl https://your-url/video_feed > video.mjpeg

# Command
curl -X POST https://your-url/command \
  -H "Content-Type: application/json" \
  -d '{"prompt": "pick up the ball", "options": {}}'

# Status
curl https://your-url/status/YOUR-REQUEST-ID

# Dispense
curl -X POST https://your-url/dispense_treat \
  -H "Content-Type: application/json" \
  -d '{"duration_ms": 600}'

# Speak
curl -X POST https://your-url/speak \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world!"}'
```

---

## TypeScript Types

```typescript
// Health Response
interface HealthResponse {
  status: 'ok';
  api: number;
  version: string;
}

// Command Request
interface CommandRequest {
  prompt: 'pick up the ball' | 'get the treat' | 'go home';
  options: Record<string, any>;
}

// Command Response
interface CommandResponse {
  request_id: string;
  status: 'accepted';
}

// Status Response
interface StatusResponse {
  state: 'executing' | 'succeeded' | 'failed' | 'aborted';
  phase: string | null;
  message: string;
  confidence?: number;
  duration_ms?: number;
}

// Dispense Request
interface DispenseRequest {
  duration_ms?: number;
}

// Speak Request
interface SpeakRequest {
  text: string;
}

// Generic Success
interface SuccessResponse {
  status: 'ok';
}

// Error Response
interface ErrorResponse {
  error: {
    code: string;
    http: number;
    message: string;
  };
}
```

---

## Support

For issues or questions, check:
- `FRONTEND_INTEGRATION.md` - Next.js integration guide
- `VIDEO_OPTIMIZATION.md` - Video streaming optimization
- `TESTING_GUIDE.md` - Backend testing guide
- `EXPOSE_API.md` - ngrok/Cloudflare setup
