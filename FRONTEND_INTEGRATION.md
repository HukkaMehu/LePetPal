# Frontend Integration Guide

## Backend API Endpoints

The Flask backend exposes these REST endpoints:

### 1. **GET /health**
Check if backend is running
```typescript
const response = await fetch('http://localhost:5000/health');
const data = await response.json();
// { status: "ok", api: 1, version: "v0.1" }
```

### 2. **GET /video_feed**
MJPEG video stream from camera
```tsx
<img src="http://localhost:5000/video_feed" alt="Robot camera" />
```

### 3. **POST /command**
Send a command to the robot
```typescript
const response = await fetch('http://localhost:5000/command', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    prompt: "pick up the ball",  // or "get the treat", "go home"
    options: {}
  })
});
const data = await response.json();
// { request_id: "uuid-here", status: "accepted" }
```

### 4. **GET /status/:request_id**
Poll for command status
```typescript
const response = await fetch(`http://localhost:5000/status/${requestId}`);
const data = await response.json();
// {
//   state: "executing" | "succeeded" | "failed" | "aborted",
//   phase: "detect" | "approach" | "grasp" | "lift" | "ready_to_throw",
//   message: "Detecting",
//   confidence: 0.85,
//   duration_ms: 1500
// }
```

### 5. **POST /dispense_treat**
Dispense a treat (servo control)
```typescript
await fetch('http://localhost:5000/dispense_treat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ duration_ms: 600 })
});
```

### 6. **POST /speak**
Text-to-speech
```typescript
await fetch('http://localhost:5000/speak', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ text: "Good boy!" })
});
```

---

## Next.js Example Component

```tsx
// app/components/RobotControl.tsx
'use client';

import { useState, useEffect } from 'react';

const API_BASE = 'http://localhost:5000';

export default function RobotControl() {
  const [status, setStatus] = useState<string>('idle');
  const [phase, setPhase] = useState<string>('');
  const [requestId, setRequestId] = useState<string | null>(null);

  // Send command to robot
  const sendCommand = async (prompt: string) => {
    try {
      const response = await fetch(`${API_BASE}/command`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt, options: {} })
      });
      
      if (response.status === 409) {
        alert('Robot is busy!');
        return;
      }
      
      const data = await response.json();
      setRequestId(data.request_id);
      setStatus('executing');
    } catch (error) {
      console.error('Failed to send command:', error);
    }
  };

  // Poll status
  useEffect(() => {
    if (!requestId) return;

    const interval = setInterval(async () => {
      try {
        const response = await fetch(`${API_BASE}/status/${requestId}`);
        const data = await response.json();
        
        setStatus(data.state);
        setPhase(data.phase || '');
        
        if (data.state === 'succeeded' || data.state === 'failed') {
          setRequestId(null); // Stop polling
        }
      } catch (error) {
        console.error('Failed to fetch status:', error);
      }
    }, 500); // Poll every 500ms

    return () => clearInterval(interval);
  }, [requestId]);

  return (
    <div className="p-6 max-w-2xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">LePetPal Robot Control</h1>
      
      {/* Video Feed */}
      <div className="mb-6 rounded-lg overflow-hidden">
        <img 
          src={`${API_BASE}/video_feed`} 
          alt="Robot camera"
          className="w-full"
        />
      </div>

      {/* Status Display */}
      <div className="mb-6 p-4 bg-gray-100 rounded-lg">
        <p className="text-lg">
          Status: <span className="font-bold">{status}</span>
        </p>
        {phase && (
          <p className="text-sm text-gray-600">
            Phase: {phase}
          </p>
        )}
      </div>

      {/* Command Buttons */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <button
          onClick={() => sendCommand('pick up the ball')}
          disabled={status === 'executing'}
          className="px-4 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-400"
        >
          Pick Up Ball
        </button>
        
        <button
          onClick={() => sendCommand('get the treat')}
          disabled={status === 'executing'}
          className="px-4 py-3 bg-green-500 text-white rounded-lg hover:bg-green-600 disabled:bg-gray-400"
        >
          Get Treat
        </button>
        
        <button
          onClick={() => sendCommand('go home')}
          className="px-4 py-3 bg-red-500 text-white rounded-lg hover:bg-red-600"
        >
          Go Home
        </button>
      </div>

      {/* Additional Controls */}
      <div className="grid grid-cols-2 gap-4">
        <button
          onClick={async () => {
            await fetch(`${API_BASE}/dispense_treat`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ duration_ms: 600 })
            });
          }}
          className="px-4 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600"
        >
          Dispense Treat
        </button>
        
        <button
          onClick={async () => {
            await fetch(`${API_BASE}/speak`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ text: "Good boy!" })
            });
          }}
          className="px-4 py-2 bg-yellow-500 text-white rounded-lg hover:bg-yellow-600"
        >
          Say "Good Boy!"
        </button>
      </div>
    </div>
  );
}
```

---

## Running Both Together

### Terminal 1: Backend
```bash
cd backend
python run_backend.py
# Backend runs on http://localhost:5000
```

### Terminal 2: Frontend
```bash
cd frontend  # your Next.js app
npm run dev
# Frontend runs on http://localhost:3000
```

---

## CORS Configuration (if needed)

If you get CORS errors, add this to `backend/app.py`:

```python
from flask_cors import CORS

def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app)  # Enable CORS for all routes
    # ... rest of code
```

Install flask-cors:
```bash
pip install flask-cors
```

---

## WebSocket Alternative (Advanced)

For real-time updates instead of polling, you could use Socket.IO:

**Backend:**
```python
from flask_socketio import SocketIO, emit

socketio = SocketIO(app, cors_allowed_origins="*")

@socketio.on('send_command')
def handle_command(data):
    req_id = cmd_mgr.start(prompt=data['prompt'], options={})
    emit('command_started', {'request_id': req_id})
    
    # Emit status updates in real-time
    # (would need to modify CommandManager to emit events)
```

**Frontend:**
```typescript
import { io } from 'socket.io-client';

const socket = io('http://localhost:5000');

socket.on('command_started', (data) => {
  console.log('Command started:', data.request_id);
});

socket.emit('send_command', { prompt: 'pick up the ball' });
```

---

## Summary

**Data Flow:**
1. User clicks button in Next.js UI
2. Frontend sends POST to `/command`
3. Backend returns `request_id`
4. Frontend polls `/status/:request_id` every 500ms
5. Backend updates status as robot moves
6. Frontend displays current phase/status
7. When `state === 'succeeded'`, stop polling

**Key Points:**
- Backend is stateless (except for in-memory status store)
- Frontend handles all UI state
- Video feed is a simple `<img>` tag with MJPEG stream
- Commands are async (202 Accepted, then poll for status)
