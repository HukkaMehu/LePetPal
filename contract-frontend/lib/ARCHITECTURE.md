# SSEClient Architecture

## Component Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         React App                                │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                      SSEProvider                            │ │
│  │  (Context Provider + useSSEClient hook)                     │ │
│  │                                                              │ │
│  │  ┌────────────────────────────────────────────────────┐   │ │
│  │  │              SSEClient Instance                     │   │ │
│  │  │                                                      │   │ │
│  │  │  ┌──────────────┐      ┌──────────────┐           │   │ │
│  │  │  │ EventSource  │      │   Polling    │           │   │ │
│  │  │  │   (SSE)      │      │   Interval   │           │   │ │
│  │  │  └──────┬───────┘      └──────┬───────┘           │   │ │
│  │  │         │                     │                     │   │ │
│  │  │         └─────────┬───────────┘                     │   │ │
│  │  │                   │                                 │   │ │
│  │  │                   ▼                                 │   │ │
│  │  │         ┌──────────────────┐                       │   │ │
│  │  │         │  onUpdate()      │                       │   │ │
│  │  │         │  Callback        │                       │   │ │
│  │  │         └────────┬─────────┘                       │   │ │
│  │  └──────────────────┼─────────────────────────────────┘   │ │
│  │                     │                                      │ │
│  │                     ▼                                      │ │
│  │           ┌──────────────────┐                            │ │
│  │           │ setCurrentCommand│                            │ │
│  │           │  (AppContext)    │                            │ │
│  │           └──────────────────┘                            │ │
│  └────────────────────┬───────────────────────────────────────┘ │
│                       │                                          │
│                       ▼                                          │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                    UI Components                            │ │
│  │                                                              │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │ │
│  │  │ CommandBar   │  │StatusDisplay │  │ ConfigPanel  │    │ │
│  │  │              │  │              │  │              │    │ │
│  │  │ - Execute    │  │ - Show state │  │ - Set config │    │ │
│  │  │   commands   │  │ - Show phase │  │ - Test conn  │    │ │
│  │  │ - Set req ID │  │ - Show conf  │  │              │    │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘    │ │
│  └────────────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────────────┘
```

## Data Flow

### SSE Mode (Primary)

```
1. User clicks command button
   │
   ▼
2. CommandBar.executeCommand()
   │
   ├─► POST /command → Backend
   │   │
   │   ▼
   │   Response: { request_id: "uuid" }
   │
   ├─► setCurrentCommand({ state: 'executing', ... })
   │
   └─► setRequestId("uuid") → SSEClient
       │
       ▼
3. Backend processes command
   │
   ├─► Phase: detect
   ├─► Phase: approach
   ├─► Phase: grasp
   └─► Phase: completed
       │
       ▼
4. Backend emits SSE events
   │
   ▼
5. EventSource receives events
   │
   ▼
6. SSEClient.onUpdate() callback
   │
   ▼
7. setCurrentCommand() → AppContext
   │
   ▼
8. React re-renders UI components
   │
   ▼
9. StatusDisplay shows updated state
```

### Polling Mode (Fallback)

```
1. SSE connection fails 3 times
   │
   ▼
2. SSEClient.startPolling()
   │
   ▼
3. setInterval(() => pollStatus(), 500ms)
   │
   ▼
4. Every 500ms:
   │
   ├─► GET /status/{request_id} → Backend
   │   │
   │   ▼
   │   Response: { state, phase, confidence, ... }
   │
   ├─► SSEClient.onUpdate() callback
   │
   ├─► setCurrentCommand() → AppContext
   │
   └─► React re-renders UI
       │
       ▼
5. Stop polling when state is final
   (completed, failed, timeout, interrupted)
```

## State Machine

### SSEClient Connection States

```
┌─────────────┐
│ Disconnected│
└──────┬──────┘
       │ connect()
       ▼
┌─────────────┐
│  Connecting │
└──────┬──────┘
       │
       ├─► SSE Success ──────┐
       │                     ▼
       │              ┌──────────────┐
       │              │  Connected   │
       │              │  (SSE Mode)  │
       │              └──────┬───────┘
       │                     │
       │                     │ onerror
       │                     ▼
       │              ┌──────────────┐
       │              │ Reconnecting │
       │              │ (Backoff)    │
       │              └──────┬───────┘
       │                     │
       │                     ├─► Retry < 3 ──► SSE Success
       │                     │
       │                     └─► Retry ≥ 3
       │                           │
       └─► SSE Failure ────────────┘
                 │
                 ▼
          ┌──────────────┐
          │  Connected   │
          │(Polling Mode)│
          └──────────────┘
```

### Command Execution States

```
┌──────┐
│ Idle │
└───┬──┘
    │ POST /command
    ▼
┌───────────┐
│ Executing │◄─────┐
└─────┬─────┘      │
      │            │ Phase transitions
      │            │ (SSE/polling updates)
      ├────────────┘
      │
      ├─► Success ──► ┌───────────┐
      │               │ Completed │
      │               └───────────┘
      │
      ├─► Failure ──► ┌──────────┐
      │               │  Failed  │
      │               └──────────┘
      │
      ├─► Timeout ──► ┌──────────┐
      │               │ Timeout  │
      │               └──────────┘
      │
      └─► Go Home ──► ┌─────────────┐
                      │ Interrupted │
                      └─────────────┘
```

## Class Structure

### SSEClient

```typescript
class SSEClient {
  // Configuration
  private baseUrl: string
  private authToken?: string
  
  // Callbacks
  private onUpdate: (status: CommandStatus) => void
  private onError?: (error: string) => void
  private onConnectionChange?: (connected: boolean) => void
  
  // SSE
  private eventSource: EventSource | null
  private isSSESupported: boolean
  
  // Polling
  private pollingInterval: NodeJS.Timeout | null
  private currentRequestId: string | null
  private isPollingMode: boolean
  
  // Reconnection
  private reconnectAttempts: number
  private reconnectTimeouts: number[]
  private reconnectTimer: NodeJS.Timeout | null
  
  // State
  private isConnected: boolean
  
  // Public Methods
  + connect(): void
  + disconnect(): void
  + setRequestId(id: string | null): void
  + updateConfig(url: string, token?: string): void
  + getConnectionStatus(): ConnectionStatus
  
  // Private Methods
  - connectSSE(): void
  - disconnectSSE(): void
  - scheduleReconnect(): void
  - startPolling(): void
  - stopPolling(): void
  - pollStatus(id: string): Promise<void>
  - isFinalState(state: string): boolean
}
```

### useSSEClient Hook

```typescript
function useSSEClient() {
  // Dependencies
  const { config, setCurrentCommand, setError, setConnectionStatus } = useApp()
  
  // State
  const sseClientRef = useRef<SSEClient | null>(null)
  
  // Callbacks
  const handleCommandUpdate = useCallback(...)
  const handleError = useCallback(...)
  const handleConnectionChange = useCallback(...)
  
  // Effects
  useEffect(() => {
    // Create and connect SSEClient
    // Cleanup on unmount
  }, [config.baseUrl, config.authToken])
  
  // Return API
  return {
    setRequestId,
    getConnectionStatus,
  }
}
```

## Error Handling

### Error Types and Responses

```
┌─────────────────────┐
│   Error Source      │
└──────────┬──────────┘
           │
           ├─► EventSource.onerror
           │   │
           │   ├─► Network error
           │   ├─► Server error
           │   └─► Connection timeout
           │       │
           │       ▼
           │   scheduleReconnect()
           │
           ├─► JSON.parse() error
           │   │
           │   ▼
           │   Log error, continue
           │
           ├─► fetch() error (polling)
           │   │
           │   ▼
           │   Log error, continue polling
           │
           └─► 404 Not Found (polling)
               │
               ▼
               Ignore, continue polling
```

## Performance Optimization

### SSE Mode
- **Latency**: < 100ms (server push)
- **Bandwidth**: Minimal (only when updates occur)
- **CPU**: Negligible (event-driven)

### Polling Mode
- **Latency**: 0-500ms (depends on timing)
- **Bandwidth**: ~2 requests/second
- **CPU**: Minimal (setTimeout-based)

### React Integration
- **Updates**: Batched by React
- **Re-renders**: Only affected components
- **Memory**: Single SSEClient instance

## Security Considerations

### Authentication
```typescript
// Optional token-based auth
headers['X-LePetPal-Token'] = authToken
```

### CORS
- Backend must allow frontend origin
- Credentials included in requests

### Input Validation
- Request ID format validation
- State transition validation
- JSON parsing error handling

## Browser Compatibility

### SSE Support
- ✅ Chrome 6+
- ✅ Firefox 6+
- ✅ Safari 5+
- ✅ Edge 79+
- ❌ IE (all versions)

### Polling Fallback
- ✅ All browsers (uses fetch API)
- ✅ IE 11+ (with polyfill)

## Testing Strategy

### Unit Tests (Future)
- SSEClient connection lifecycle
- Polling fallback activation
- Exponential backoff calculation
- State transition handling

### Integration Tests (Future)
- End-to-end command execution
- SSE event handling
- Polling fallback behavior
- Reconnection scenarios

### Manual Testing
- See IMPLEMENTATION_SUMMARY.md

## Monitoring and Debugging

### Console Logging
```javascript
// Connection events
"SSE connection error:", error
"SSE reconnection failed multiple times, falling back to polling"

// Polling events
"Polling error:", error

// Parse errors
"Failed to parse SSE event data:", error
```

### Browser DevTools
- **Network Tab**: Monitor SSE connection and polling requests
- **Console Tab**: View connection logs and errors
- **React DevTools**: Inspect state updates

### Connection Status API
```typescript
const status = getConnectionStatus()
// { connected: true, mode: 'sse' | 'polling' | 'disconnected' }
```
