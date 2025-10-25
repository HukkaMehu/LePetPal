# SSEClient Library

This directory contains the SSEClient implementation for real-time command status updates in the LePetPal frontend.

## Overview

The SSEClient provides real-time command status updates using Server-Sent Events (SSE) with automatic fallback to polling when SSE is unavailable or fails. It implements exponential backoff for reconnection and integrates seamlessly with React state management.

## Components

### SSEClient.ts

Core SSE client class that manages:
- Connection to `/events` endpoint via EventSource API
- Automatic polling fallback to `/status/{request_id}` endpoint
- Exponential backoff reconnection (500ms → 1s → 2s → 4s → 8s max)
- Connection status tracking
- Request ID management for polling

**Key Features:**
- Detects SSE support and connection failures
- Automatically switches to polling mode after 3 failed SSE reconnection attempts
- Polls every 500ms when in fallback mode
- Stops polling when command reaches final state (completed, failed, timeout, interrupted)
- Handles connection drops gracefully with exponential backoff

### useSSEClient.ts

React hook that integrates SSEClient with AppContext:
- Manages SSEClient lifecycle (creation, connection, cleanup)
- Updates React state within 100ms of receiving events (per requirements)
- Handles configuration changes (reconnects when base URL or token changes)
- Provides `setRequestId` function for polling fallback
- Provides `getConnectionStatus` function for monitoring connection state

### useCommandExecution.ts

Helper hook for command execution with SSE integration:
- Executes commands via POST `/command` endpoint
- Registers request ID with SSEClient for polling fallback
- Handles error responses (400, 409, 500)
- Updates command state in AppContext

## Usage

### Basic Setup

1. Wrap your app with `SSEProvider` (already done in `app/page.tsx`):

```tsx
import SSEProvider from '@/components/SSEProvider';

export default function Home() {
  return (
    <SSEProvider>
      {/* Your app components */}
    </SSEProvider>
  );
}
```

2. Use the `useSSE` hook in components that need SSE functionality:

```tsx
import { useSSE } from '@/components/SSEProvider/SSEProvider';

function MyComponent() {
  const { setRequestId, getConnectionStatus } = useSSE();
  
  // Execute a command and register request ID
  const handleCommand = async () => {
    const response = await fetch(`${baseUrl}/command`, {
      method: 'POST',
      body: JSON.stringify({ command: 'pick up the ball' }),
    });
    const data = await response.json();
    setRequestId(data.request_id); // Enable polling fallback
  };
  
  // Check connection status
  const status = getConnectionStatus();
  console.log(status); // { connected: true, mode: 'sse' | 'polling' }
}
```

### Command Execution Example

See `CommandBar.tsx` for a complete example of executing commands with SSE integration:

```tsx
const { setRequestId } = useSSE();
const { setCurrentCommand } = useApp();

const executeCommand = async (command: string) => {
  const response = await fetch(`${baseUrl}/command`, {
    method: 'POST',
    body: JSON.stringify({ command }),
  });
  
  const data = await response.json();
  const requestId = data.request_id;
  
  // Set initial state
  setCurrentCommand({
    request_id: requestId,
    state: 'executing',
    message: 'Command started',
  });
  
  // Enable polling fallback
  setRequestId(requestId);
};
```

## SSE Event Format

The SSE endpoint emits `command_update` events with the following format:

```
event: command_update
data: {
  "request_id": "uuid",
  "state": "executing" | "completed" | "failed" | "timeout" | "interrupted",
  "phase": "detect" | "approach" | "grasp" | "lift" | "drop" | "ready_to_throw" | null,
  "confidence": 0.85,
  "message": "Approaching ball",
  "duration_ms": 1234
}
```

## Polling Fallback

When SSE is unavailable or fails, the client automatically falls back to polling:

1. **Trigger Conditions:**
   - EventSource not supported by browser
   - SSE connection fails 3 times consecutively
   - User explicitly disables SSE (future feature)

2. **Polling Behavior:**
   - Polls `/status/{request_id}` every 500ms
   - Only polls when `request_id` is set
   - Stops polling when command reaches final state
   - Handles 404 responses gracefully (request ID not found)

3. **Switching Back to SSE:**
   - Client attempts SSE reconnection on next page load
   - Polling continues until SSE connection succeeds

## Connection States

The SSEClient tracks three connection states:

- **disconnected**: No active connection (initial state or after disconnect)
- **connected (SSE mode)**: EventSource connected to `/events` endpoint
- **connected (polling mode)**: Polling `/status/{request_id}` endpoint

## Reconnection Strategy

SSE reconnection uses exponential backoff:

1. First attempt: 500ms delay
2. Second attempt: 1s delay
3. Third attempt: 2s delay
4. Fourth attempt: 4s delay
5. Fifth+ attempts: 8s delay (max)

After 3 failed attempts, switches to polling mode permanently (until page reload).

## Error Handling

The SSEClient handles various error scenarios:

- **SSE connection errors**: Triggers reconnection with backoff
- **SSE parse errors**: Logs error, continues listening
- **Polling errors**: Logs error, continues polling
- **Network errors**: Handled by fetch API, triggers error callback

## Performance Considerations

- **SSE Mode**: Minimal overhead, server pushes updates
- **Polling Mode**: 2 requests/second (500ms interval)
- **Memory**: Single EventSource instance, no memory leaks
- **React Updates**: Batched automatically by React (< 100ms latency)

## Testing

To test SSE functionality:

1. **With Backend Running:**
   ```bash
   # Start backend (see backend README)
   python run_backend.py
   
   # Start frontend
   npm run dev
   
   # Execute commands and observe real-time updates
   ```

2. **SSE Fallback Testing:**
   - Disable SSE in browser DevTools (Network throttling)
   - Observe automatic switch to polling mode
   - Check console for "falling back to polling" message

3. **Reconnection Testing:**
   - Stop backend server during command execution
   - Observe reconnection attempts in console
   - Restart backend and verify reconnection

## Requirements Satisfied

This implementation satisfies the following requirements:

- **5.1**: SSE connection established at `/events` endpoint
- **5.2**: Command state transitions emitted via SSE with request_id, state, phase, confidence, message, duration_ms
- **5.3**: UI updates within 100ms of receiving SSE events
- **5.4**: Polling fallback to `/status/{request_id}` every 500ms when SSE unavailable
- **5.5**: SSE reconnection with exponential backoff (500ms → 8s max)

## Future Enhancements

- WebSocket support for bidirectional communication
- Configurable polling interval
- Manual SSE/polling mode selection
- Connection quality metrics
- Retry limit configuration
