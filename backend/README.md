# LePetPal Backend

AI-first robotics system for interactive pet engagement through camera-based commands.

## Quick Start

### Prerequisites

- Python 3.9 or higher
- pip package manager
- (Optional) Physical hardware: Camera, LeRobot-compatible arm, SG90 servo

### Installation

1. **Clone the repository and navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   ```bash
   # Copy the example configuration
   cp .env.example .env
   
   # Edit .env with your settings
   # For development, USE_MOCK_HARDWARE=true is recommended
   ```

5. **Run the server:**
   ```bash
   python run_backend.py
   ```

6. **Verify the server is running:**
   ```bash
   curl http://localhost:5000/health
   ```
   
   Expected response:
   ```json
   {
     "status": "ok",
     "api": 1,
     "version": "v0.1"
   }
   ```

## Configuration

All configuration is managed through environment variables in the `.env` file. See `.env.example` for a complete list of available options.

### Key Configuration Options

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | 5000 | Server port |
| `USE_MOCK_HARDWARE` | true | Use mock adapters for development |
| `CAMERA_INDEX` | 0 | Camera device index |
| `STREAM_WIDTH` | 1280 | Video stream width |
| `STREAM_HEIGHT` | 720 | Video stream height |
| `CONFIDENCE_THRESHOLD` | 0.7 | Object detection confidence threshold |

## API Endpoints

### Health Check

**GET** `/health`

Returns server status and version information.

**Response:**
```json
{
  "status": "ok",
  "api": 1,
  "version": "v0.1"
}
```

---

### Video Feed

**GET** `/video_feed`

Returns MJPEG video stream with optional overlays.

**Query Parameters:**
- `width` (int, optional): Frame width in pixels (default: 1280)
- `height` (int, optional): Frame height in pixels (default: 720)
- `overlays` (int, optional): Enable overlays (0=off, 1=on, default: 1)

**Response:**
- Content-Type: `multipart/x-mixed-replace; boundary=frame`
- Continuous MJPEG stream

**Example:**
```
http://localhost:5000/video_feed?width=1280&height=720&overlays=1
```

---

### Execute Command

**POST** `/command`

Execute a predefined robot command.

**Request Body:**
```json
{
  "command": "pick up the ball" | "get the treat" | "go home" | "throw ball"
}
```

**Response (202 Accepted):**
```json
{
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "accepted"
}
```

**Response (409 Busy):**
```json
{
  "error": "busy",
  "message": "Another command is currently executing"
}
```

**Response (400 Invalid):**
```json
{
  "error": "invalid",
  "message": "Unknown command type"
}
```

---

### Command Status

**GET** `/status/{request_id}`

Get the current status of a command (polling fallback for SSE).

**Response (200 OK):**
```json
{
  "state": "executing",
  "phase": "detect",
  "confidence": 0.85,
  "message": "Detecting ball...",
  "duration_ms": 1234
}
```

**Response (404 Not Found):**
```json
{
  "error": "not_found",
  "message": "Request ID not found"
}
```

**State Values:**
- `executing`: Command in progress
- `completed`: Command succeeded
- `failed`: Command failed
- `timeout`: Command exceeded timeout
- `interrupted`: Command preempted by Go Home

**Phase Values (for ball manipulation):**
- `detect`: Locating object with vision model
- `approach`: Moving arm toward object
- `grasp`: Closing gripper
- `lift`: Lifting object
- `drop`: Releasing object in bowl
- `ready_to_throw`: Ready for throw macro (optional)

---

### Server-Sent Events

**GET** `/events`

Real-time command state updates via Server-Sent Events.

**Response:**
- Content-Type: `text/event-stream`
- Continuous event stream

**Event Format:**
```
event: command_update
data: {
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "state": "executing",
  "phase": "approach",
  "confidence": 0.92,
  "message": "Approaching ball",
  "duration_ms": 2500
}
```

---

### Dispense Treat

**POST** `/dispense_treat`

Actuate servo to dispense a treat.

**Request Body:**
```json
{
  "duration_ms": 1000
}
```

**Response (200 OK):**
```json
{
  "status": "ok"
}
```

**Constraints:**
- `duration_ms` must be a positive integer
- Maximum duration: 5000ms

---

### Speak

**POST** `/speak`

Synthesize and play speech through TTS engine.

**Request Body:**
```json
{
  "text": "Good dog!"
}
```

**Response (200 OK):**
```json
{
  "status": "ok"
}
```

**Constraints:**
- `text` maximum length: 200 characters

---

## Hardware Setup

### Camera

**Requirements:**
- USB camera or Raspberry Pi Camera Module
- Minimum resolution: 640x480
- Recommended: 1280x720 or higher

**Setup:**
1. Connect camera to USB port or CSI connector
2. Verify camera is detected:
   ```bash
   # Linux
   ls /dev/video*
   
   # Should show /dev/video0 (or higher number)
   ```
3. Set `CAMERA_INDEX` in `.env` to the appropriate device number

**Troubleshooting:**
- If camera not detected, check USB connection and drivers
- Try different `CAMERA_INDEX` values (0, 1, 2, etc.)
- Ensure camera is not in use by another application

---

### Servo Controller (SG90)

**Requirements:**
- SG90 micro servo motor
- GPIO-capable board (Raspberry Pi recommended)
- 5V power supply for servo

**Wiring:**
- Red wire: 5V power
- Brown/Black wire: Ground
- Orange/Yellow wire: GPIO pin (default: BCM 18)

**Setup:**
1. Connect servo to GPIO pin specified in `SERVO_PIN` environment variable
2. Ensure proper power supply (servos can draw significant current)
3. Test servo actuation:
   ```bash
   # With USE_MOCK_HARDWARE=false
   curl -X POST http://localhost:5000/dispense_treat \
     -H "Content-Type: application/json" \
     -d '{"duration_ms": 1000}'
   ```

**Safety Notes:**
- Never connect servo signal wire directly to 3.3V
- Use external 5V power supply for servo, not GPIO 5V pin
- Add a flyback diode to protect against voltage spikes

---

### Robotic Arm (LeRobot-Compatible)

**Requirements:**
- LeRobot-compatible robotic arm
- USB connection or appropriate interface
- LeRobot SDK installed

**Setup:**
1. Install LeRobot SDK:
   ```bash
   pip install lerobot
   ```
2. Connect arm via USB
3. Verify arm connection:
   ```bash
   # Test command (specific to your arm model)
   lerobot-cli list-devices
   ```
4. Set `USE_MOCK_HARDWARE=false` in `.env`
5. Configure joint limits in `calibration.json`

**Calibration:**
Create a `calibration.json` file with arm positions:
```json
{
  "arm": {
    "home_position": [0.0, -1.57, 1.57, 0.0, 0.0, 0.0],
    "ready_to_throw_position": [0.5, -0.8, 1.2, 0.0, 0.0, 0.0]
  },
  "zones": {
    "bowl": {"x": 640, "y": 360, "radius": 100},
    "treat_dispenser": {"x": 200, "y": 100}
  }
}
```

**Safety:**
- Always test arm movements in mock mode first
- Ensure adequate clearance around arm workspace
- Use Go Home command to immediately stop any operation
- Joint limits are enforced with configurable margin

---

### Text-to-Speech (TTS)

**Requirements:**
- System TTS engine (pyttsx3 or espeak)

**Setup:**
1. Install TTS dependencies:
   ```bash
   # Linux
   sudo apt-get install espeak
   
   # macOS (uses built-in TTS)
   # No additional installation needed
   
   # Windows (uses built-in SAPI)
   # No additional installation needed
   ```
2. Test TTS:
   ```bash
   curl -X POST http://localhost:5000/speak \
     -H "Content-Type: application/json" \
     -d '{"text": "Hello, this is a test"}'
   ```

---

## Development Mode

For development without physical hardware, use mock adapters:

1. Set `USE_MOCK_HARDWARE=true` in `.env`
2. Mock adapters will simulate hardware behavior
3. Video feed will show synthetic frames
4. Commands will execute with simulated delays and responses

This allows full API testing and frontend development without hardware.

---

## Command Execution Flow

### Single Active Command

The system enforces **one command at a time**:
- New commands return `409 Busy` if another is executing
- Exception: **Go Home** always accepted (preempts current command)

### Command Lifecycle

1. **Idle** → Command submitted via POST `/command`
2. **Executing** → Transitions through phases (detect, approach, grasp, etc.)
3. **Final State** → Completed, Failed, Timeout, or Interrupted

### Phase Transitions

For "pick up the ball" command:
```
detect → approach → grasp → lift → drop → ready_to_throw → completed
```

Each phase transition emits an SSE event within 100ms.

### Timeout Enforcement

- Default command timeout: 30 seconds
- Per-phase timeouts configurable in `.env`
- Timeout triggers automatic transition to `timeout` state

### Go Home Interrupt

- Accepted at any time, regardless of current state
- Preempts active command (transitions to `interrupted`)
- Arm returns to home position within 1 second
- Always enabled in frontend (safety feature)

---

## Error Handling

### HTTP Status Codes

| Code | Meaning | Action |
|------|---------|--------|
| 200 | Success | Request completed successfully |
| 202 | Accepted | Command accepted, check status via SSE or polling |
| 400 | Invalid Request | Check request parameters |
| 409 | Busy | Another command executing, retry with backoff |
| 500 | Internal Error | Check server logs |

### Logging

All operations are logged in JSON format to `lepetpal.log`:

```json
{
  "timestamp": "2025-10-24T10:30:45.123Z",
  "level": "INFO",
  "message": "Command state transition",
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "from_state": "executing",
  "to_state": "completed",
  "duration_ms": 12345
}
```

Set `LOG_LEVEL=DEBUG` for verbose logging during development.

---

## Testing

### Manual Testing

1. **Health Check:**
   ```bash
   curl http://localhost:5000/health
   ```

2. **Video Feed:**
   Open in browser: `http://localhost:5000/video_feed`

3. **Execute Command:**
   ```bash
   curl -X POST http://localhost:5000/command \
     -H "Content-Type: application/json" \
     -d '{"command": "go home"}'
   ```

4. **Check Status:**
   ```bash
   curl http://localhost:5000/status/{request_id}
   ```

5. **SSE Stream:**
   ```bash
   curl -N http://localhost:5000/events
   ```

### Integration Testing

See `tasks.md` section 23 for integration checkpoint scenarios:
- IC-1: LAN with stubs
- IC-2: Servo + Speak
- IC-3: Model-in-loop
- IC-4: Demo script dry run

---

## Troubleshooting

### Server won't start

- Check Python version: `python --version` (requires 3.9+)
- Verify all dependencies installed: `pip list`
- Check port availability: `netstat -an | grep 5000`
- Review logs in `lepetpal.log`

### Camera not working

- Verify camera index: Try different values (0, 1, 2)
- Check permissions: `sudo usermod -a -G video $USER`
- Test camera independently: `ffplay /dev/video0`

### Servo not responding

- Check GPIO permissions: `sudo usermod -a -G gpio $USER`
- Verify wiring and power supply
- Test with mock mode first: `USE_MOCK_HARDWARE=true`

### Arm movements erratic

- Verify calibration file exists and is valid
- Check joint limits in configuration
- Ensure adequate power supply for arm
- Test Go Home command first

### SSE not working

- Check CORS configuration in `.env`
- Verify frontend is using correct base URL
- Test with curl: `curl -N http://localhost:5000/events`
- Fallback to polling if SSE unsupported

---

## Security Considerations

### LAN Deployment (Default)

- No authentication required
- CORS set to `*` (allow all origins)
- Suitable for local network use only

### Production Deployment

1. **Enable Authentication:**
   ```bash
   # In .env
   API_TOKEN=your-secret-token-here
   ```
   
   Clients must include header:
   ```
   X-LePetPal-Token: your-secret-token-here
   ```

2. **Restrict CORS:**
   ```bash
   # In .env
   CORS_ORIGINS=http://192.168.1.50:3000,https://yourdomain.com
   ```

3. **Use HTTPS:**
   - Deploy behind reverse proxy (nginx, Apache)
   - Configure SSL certificates
   - Update frontend to use `https://` URLs

---

## Performance Optimization

### Video Streaming

- Target: 15 FPS minimum, 30 FPS ideal
- Reduce resolution for lower bandwidth: `STREAM_WIDTH=640&STREAM_HEIGHT=480`
- Disable overlays for better performance: `overlays=0`

### Command Execution

- Inference runs at 10-20 Hz during detect phase
- Adjust `CONFIDENCE_THRESHOLD` to balance accuracy vs speed
- Lower threshold = faster detection, more false positives
- Higher threshold = slower detection, fewer false positives

### Memory Management

- Command history limited to last 100 requests
- Logs rotated automatically (configure in logging setup)
- Frame buffers cleared after each stream

---

## Architecture

```
Backend Service
├── run_backend.py          # Startup script (this file's purpose)
├── app/                    # Flask application
│   ├── __init__.py        # App factory
│   ├── routes.py          # API endpoints
│   └── state_machine.py   # Command state management
├── adapters/              # Hardware abstraction layer
│   ├── camera.py          # Camera interface
│   ├── arm.py             # Robotic arm interface
│   ├── servo.py           # Servo controller interface
│   ├── tts.py             # Text-to-speech interface
│   └── mock/              # Mock implementations
├── models/                # Vision models
├── calibration.json       # Hardware calibration data
├── .env                   # Configuration (not in git)
└── requirements.txt       # Python dependencies
```

---

## Support

For issues, questions, or contributions:
- Review the design document: `.kiro/specs/lepetpal-mvp/design.md`
- Check requirements: `.kiro/specs/lepetpal-mvp/requirements.md`
- See implementation tasks: `.kiro/specs/lepetpal-mvp/tasks.md`

---

## License

[Your License Here]

---

## Version

**API Version:** 1  
**System Version:** v0.1  
**Last Updated:** 2025-10-25
