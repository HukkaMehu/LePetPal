# LePetPal Frontend Quick Start

## Your API URL

```
https://lepetpal.verkkoventure.com
```

This is a **permanent URL** that never changes! ✅

---

## Main Camera Feed (Use This!)

```tsx
<img src="https://lepetpal.verkkoventure.com/camera?quality=50&scale=0.5&fps=10" />
```

**Features:**
- ✅ Always shows the main camera (camera 0)
- ✅ Automatic reconnection if camera disconnects
- ✅ No synthetic fallback - real camera only
- ✅ Optimized for internet streaming

**Adjust quality:**
```tsx
// Ultra-low bandwidth (slow connection)
<img src="https://lepetpal.verkkoventure.com/camera?quality=30&scale=0.3&fps=5" />

// Balanced (recommended)
<img src="https://lepetpal.verkkoventure.com/camera?quality=50&scale=0.5&fps=10" />

// High quality (fast connection)
<img src="https://lepetpal.verkkoventure.com/camera?quality=70&scale=0.7&fps=15" />
```

---

## Send Commands

```tsx
const sendCommand = async (prompt: string) => {
  const response = await fetch('https://lepetpal.verkkoventure.com/command', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prompt, options: {} })
  });
  
  const data = await response.json();
  return data.request_id; // Use this to poll status
};

// Usage
const requestId = await sendCommand('pick up the ball');
```

**Available commands:**
- `"pick up the ball"`
- `"get the treat"`
- `"go home"`

---

## Poll Command Status

```tsx
const pollStatus = async (requestId: string) => {
  const response = await fetch(`https://lepetpal.verkkoventure.com/status/${requestId}`);
  const data = await response.json();
  
  return {
    state: data.state,        // "executing" | "succeeded" | "failed" | "aborted"
    phase: data.phase,        // "detect_1", "approach_2", "grasp_1", etc.
    message: data.message,
    confidence: data.confidence
  };
};

// Poll every 500ms
const interval = setInterval(async () => {
  const status = await pollStatus(requestId);
  console.log(status.phase, status.state);
  
  if (status.state === 'succeeded' || status.state === 'failed') {
    clearInterval(interval);
  }
}, 500);
```

---

## Other Endpoints

### Dispense Treat
```tsx
await fetch('https://lepetpal.verkkoventure.com/dispense_treat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ duration_ms: 600 })
});
```

### Text-to-Speech
```tsx
await fetch('https://lepetpal.verkkoventure.com/speak', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ text: 'Good boy!' })
});
```

### Health Check
```tsx
const health = await fetch('https://lepetpal.verkkoventure.com/health')
  .then(r => r.json());
// { status: "ok", api: 1, version: "v0.1" }
```

---

## Complete React Component Example

```tsx
'use client';

import { useState, useEffect } from 'react';

const API_BASE = 'https://lepetpal.verkkoventure.com';

export default function RobotControl() {
  const [status, setStatus] = useState<string>('idle');
  const [phase, setPhase] = useState<string>('');
  const [requestId, setRequestId] = useState<string | null>(null);

  // Send command
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
          setRequestId(null);
        }
      } catch (error) {
        console.error('Failed to fetch status:', error);
      }
    }, 500);

    return () => clearInterval(interval);
  }, [requestId]);

  return (
    <div className="p-6 max-w-2xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">LePetPal Robot</h1>
      
      {/* Camera Feed */}
      <div className="mb-6 rounded-lg overflow-hidden bg-black">
        <img 
          src={`${API_BASE}/camera?quality=50&scale=0.5&fps=10`}
          alt="Robot camera"
          className="w-full"
        />
      </div>

      {/* Status */}
      <div className="mb-6 p-4 bg-gray-100 rounded-lg">
        <p className="text-lg">
          Status: <span className="font-bold">{status}</span>
        </p>
        {phase && <p className="text-sm text-gray-600">Phase: {phase}</p>}
      </div>

      {/* Commands */}
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

      {/* Extra Controls */}
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
              body: JSON.stringify({ text: 'Good boy!' })
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

## TypeScript Types

```typescript
interface CommandResponse {
  request_id: string;
  status: 'accepted';
}

interface StatusResponse {
  state: 'executing' | 'succeeded' | 'failed' | 'aborted';
  phase: string | null;
  message: string;
  confidence?: number;
  duration_ms?: number;
}

interface ErrorResponse {
  error: {
    code: string;
    http: number;
    message: string;
  };
}
```

---

## Important Notes

1. **Camera endpoint:** Use `/camera` not `/video_feed` - it's more reliable
2. **No synthetic feed:** You'll always see the real camera
3. **Automatic reconnection:** If camera disconnects, it will reconnect automatically
4. **Persistent URL:** `https://lepetpal.verkkoventure.com` never changes
5. **CORS enabled:** No CORS issues

---

## Full Documentation

See `API_DOCUMENTATION.md` for complete API reference.
