# WebSocket Hub Usage Guide

## Overview

The WebSocket hub provides real-time event broadcasting to all connected UI clients. It supports multiple simultaneous connections and uses Redis pub/sub for multi-instance deployments.

## WebSocket Endpoint

**Endpoint:** `ws://localhost:8000/ws/ui`

## Message Types

All messages follow this structure:

```json
{
  "type": "event" | "overlay" | "telemetry" | "connection",
  "event_type": "string (for events)",
  "overlay_type": "string (for overlays)",
  "data": {}
}
```

### Event Messages

Events represent detected behaviors or system actions:

```json
{
  "type": "event",
  "event_type": "sit",
  "data": {
    "timestamp": "2025-10-24T10:30:00Z",
    "confidence": 0.95,
    "metadata": {}
  }
}
```

**Event Types:**
- `dog_detected` - Dog detected in frame
- `sit`, `stand`, `lie` - Dog posture actions
- `fetch_return` - Fetch sequence completed
- `bark`, `howl`, `whine` - Audio events
- `person_entered` - Person detected in frame
- `clip_saved` - Video clip saved
- `snapshot_saved` - Snapshot captured
- `bookmark` - Manual bookmark created

### Overlay Messages

Overlay messages contain visual data to render on top of the video:

```json
{
  "type": "overlay",
  "overlay_type": "detection",
  "data": {
    "boxes": [
      {
        "x": 100,
        "y": 150,
        "w": 200,
        "h": 300,
        "label": "dog",
        "confidence": 0.95
      }
    ]
  }
}
```

**Overlay Types:**
- `detection` - Bounding boxes with labels
- `pose` - Keypoints and skeleton
- `heatmap` - Motion heatmap data
- `zone` - Zone boundaries
- `annotation` - User annotations

### Telemetry Messages

Telemetry messages contain system metrics:

```json
{
  "type": "telemetry",
  "data": {
    "fps": 30,
    "latency_ms": 120,
    "temperature": 45.5,
    "battery": 85
  }
}
```

## Broadcasting from Backend Code

### Using Event Utilities

```python
from app.core.events import (
    broadcast_event,
    broadcast_action,
    broadcast_dog_detection,
    broadcast_overlay_update,
    broadcast_telemetry
)

# Broadcast a dog action
await broadcast_action("sit", confidence=0.95, metadata={"duration": 5.2})

# Broadcast a detection
await broadcast_dog_detection({
    "box": {"x": 100, "y": 150, "w": 200, "h": 300},
    "confidence": 0.95
})

# Broadcast overlay data
await broadcast_overlay_update("detection", {
    "boxes": [{"x": 100, "y": 150, "w": 200, "h": 300, "label": "dog"}]
})

# Broadcast telemetry
await broadcast_telemetry({
    "fps": 30,
    "latency_ms": 120
})
```

### Using Connection Manager Directly

```python
from app.core.websocket import manager

# Broadcast custom message
await manager.broadcast({
    "type": "custom",
    "data": {"message": "Hello"}
})

# Broadcast to specific connection
await manager.send_personal_message(
    {"type": "notification", "message": "Welcome!"},
    websocket
)
```

## Testing the WebSocket

### 1. Start the Backend Server

```bash
cd backend
uvicorn app.main:app --reload
```

### 2. Connect with Test Client

```bash
python test_websocket.py
```

### 3. Test Broadcasting via API

```bash
# Broadcast a custom event
curl -X POST http://localhost:8000/api/events/broadcast \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "test_event",
    "data": {"message": "Hello WebSocket"}
  }'

# Broadcast an action
curl -X POST http://localhost:8000/api/events/broadcast/action \
  -H "Content-Type: application/json" \
  -d '{
    "action": "sit",
    "confidence": 0.95,
    "metadata": {"duration": 5.2}
  }'

# Broadcast overlay data
curl -X POST http://localhost:8000/api/events/broadcast/overlay \
  -H "Content-Type: application/json" \
  -d '{
    "overlay_type": "detection",
    "data": {
      "boxes": [
        {"x": 100, "y": 150, "w": 200, "h": 300, "label": "dog", "confidence": 0.95}
      ]
    }
  }'

# Broadcast telemetry
curl -X POST http://localhost:8000/api/events/broadcast/telemetry \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "fps": 30,
      "latency_ms": 120,
      "temperature": 45.5
    }
  }'
```

## Frontend Integration

### React Example with WebSocket Hook

```typescript
import { useEffect, useState } from 'react';

interface WebSocketMessage {
  type: 'event' | 'overlay' | 'telemetry' | 'connection';
  event_type?: string;
  overlay_type?: string;
  data: any;
}

export function useWebSocket(url: string) {
  const [messages, setMessages] = useState<WebSocketMessage[]>([]);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    const ws = new WebSocket(url);

    ws.onopen = () => {
      console.log('WebSocket connected');
      setIsConnected(true);
    };

    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      setMessages((prev) => [...prev, message]);
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
      setIsConnected(false);
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    return () => {
      ws.close();
    };
  }, [url]);

  return { messages, isConnected };
}

// Usage in component
function VideoPlayer() {
  const { messages, isConnected } = useWebSocket('ws://localhost:8000/ws/ui');

  useEffect(() => {
    messages.forEach((msg) => {
      if (msg.type === 'event' && msg.event_type === 'sit') {
        console.log('Dog sat down!', msg.data);
      }
      if (msg.type === 'overlay' && msg.overlay_type === 'detection') {
        // Update overlay rendering
        console.log('Detection boxes:', msg.data);
      }
    });
  }, [messages]);

  return (
    <div>
      <div>Status: {isConnected ? 'Connected' : 'Disconnected'}</div>
      {/* Video player and overlays */}
    </div>
  );
}
```

## Redis Pub/Sub for Multi-Instance Support

The WebSocket hub automatically uses Redis pub/sub when Redis is configured. This allows multiple backend instances to share events:

1. Instance A receives an event and broadcasts to its local WebSocket connections
2. Instance A publishes the event to Redis channel `dogmonitor:events`
3. Instance B receives the Redis message and broadcasts to its local connections
4. All clients across all instances receive the event

**Configuration:**

Set Redis URL in `.env`:
```
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
```

The connection manager will automatically initialize Redis on startup.

## Architecture

```
┌─────────────┐     ┌─────────────┐
│  Client 1   │     │  Client 2   │
└──────┬──────┘     └──────┬──────┘
       │                   │
       │ WebSocket         │ WebSocket
       │                   │
┌──────▼───────────────────▼──────┐
│    Connection Manager            │
│  - Active connections set        │
│  - Local broadcast               │
│  - Redis pub/sub                 │
└──────┬───────────────────┬──────┘
       │                   │
       │ Publish           │ Subscribe
       │                   │
┌──────▼───────────────────▼──────┐
│         Redis Pub/Sub            │
│    Channel: dogmonitor:events    │
└──────────────────────────────────┘
```

## Error Handling

- **Connection Failures:** Clients are automatically removed from the active connections set
- **Redis Failures:** System continues to work with local broadcasting only (logs error)
- **Message Errors:** Individual message failures don't affect other connections
- **Graceful Shutdown:** All connections are closed cleanly on server shutdown

## Performance Considerations

- **Connection Limit:** No hard limit, but monitor memory usage with many connections
- **Message Rate:** Designed for real-time events (30-60 messages/second typical)
- **Redis Overhead:** Minimal latency added (<10ms) for multi-instance support
- **Memory:** Each connection uses ~50KB of memory

## Monitoring

Check active connections:
```python
from app.core.websocket import manager

# Get connection count
connection_count = len(manager.active_connections)
```

## Troubleshooting

**WebSocket won't connect:**
- Check CORS settings in `app/core/config.py`
- Verify server is running on expected port
- Check browser console for errors

**Messages not received:**
- Verify Redis is running if using multi-instance
- Check server logs for broadcasting errors
- Ensure client is properly subscribed

**High latency:**
- Check Redis connection latency
- Monitor server CPU/memory usage
- Consider reducing message frequency
