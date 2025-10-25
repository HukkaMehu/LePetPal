# Design Document

## Overview

This design document outlines the technical approach for integrating the Pet Training Web App with the LePetPal backend. The core principle is **zero frontend modification** - we preserve the existing, polished UI completely. Integration is achieved through:

1. **Backend Enhancement**: Adding CORS support to the Flask backend
2. **Minimal Frontend Additions**: Creating new service/context modules that existing components can consume
3. **Configuration Layer**: Environment variables and settings UI for backend connectivity

The design leverages React Context to inject backend functionality into existing components without modifying their code structure.

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────┐
│     Pet Training Web App (React)        │
│                                         │
│  ┌───────────────────────────────────┐ │
│  │   Existing Components             │ │
│  │   (LivePage, SettingsPage, etc.)  │ │
│  │   *** NO MODIFICATIONS ***        │ │
│  └───────────┬───────────────────────┘ │
│              │ consumes                │
│  ┌───────────▼───────────────────────┐ │
│  │   NEW: BackendContext             │ │
│  │   - Connection state              │ │
│  │   - Command execution             │ │
│  │   - Status polling                │ │
│  └───────────┬───────────────────────┘ │
│              │ uses                    │
│  ┌───────────▼───────────────────────┐ │
│  │   NEW: API Service (api.ts)       │ │
│  │   - HTTP client wrapper           │ │
│  │   - Typed endpoints               │ │
│  └───────────┬───────────────────────┘ │
└──────────────┼─────────────────────────┘
               │ HTTP/CORS
┌──────────────▼─────────────────────────┐
│     LePetPal Backend (Flask)           │
│                                         │
│  ┌───────────────────────────────────┐ │
│  │   ENHANCED: CORS Middleware       │ │
│  └───────────────────────────────────┘ │
│  ┌───────────────────────────────────┐ │
│  │   Existing Endpoints              │ │
│  │   /health, /video_feed,           │ │
│  │   /command, /status, etc.         │ │
│  └───────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

### Component Interaction Flow

```
User clicks "Pet" button in LivePage
    ↓
LivePage.handleAction('Pet') - existing code
    ↓
BackendContext.sendCommand('pick up the ball')
    ↓
API Service POST /command
    ↓
Backend returns {request_id: "abc123"}
    ↓
BackendContext starts polling /status/abc123
    ↓
Status updates flow back to context state
    ↓
LivePage shows toast notification - existing code
```

## Components and Interfaces

### 1. Backend API Service (NEW)

**File**: `Pet Training Web App/src/services/api.ts`

**Purpose**: Encapsulate all HTTP communication with the backend.

**Interface**:
```typescript
interface ApiConfig {
  baseUrl: string;
  authToken?: string;
}

interface CommandResponse {
  request_id: string;
  status: 'accepted';
}

interface StatusResponse {
  state: 'idle' | 'executing' | 'completed' | 'failed';
  phase?: string;
  confidence?: number;
  duration_ms?: number;
  message?: string;
}

interface HealthResponse {
  status: 'ok';
  api: number;
  version: string;
}

class BackendApiService {
  private config: ApiConfig;
  
  constructor(config: ApiConfig);
  
  async health(): Promise<HealthResponse>;
  async sendCommand(prompt: string, options?: any): Promise<CommandResponse>;
  async getStatus(requestId: string): Promise<StatusResponse>;
  async dispenseTreat(durationMs?: number): Promise<{status: string}>;
  async speak(text: string): Promise<{status: string}>;
  
  getVideoFeedUrl(): string;
  updateConfig(config: Partial<ApiConfig>): void;
}
```

**Implementation Details**:
- Uses native `fetch` API for HTTP requests
- Reads `VITE_API_BASE_URL` from `import.meta.env`
- Includes error handling with try-catch
- Returns typed responses using TypeScript interfaces
- Constructs video feed URL as `${baseUrl}/video_feed`

### 2. Backend Context (NEW)

**File**: `Pet Training Web App/src/contexts/BackendContext.tsx`

**Purpose**: Provide global state management for backend connectivity and command execution.

**Interface**:
```typescript
interface BackendState {
  isConnected: boolean;
  connectionError?: string;
  currentCommand?: {
    requestId: string;
    prompt: string;
    state: 'executing' | 'completed' | 'failed';
    phase?: string;
    confidence?: number;
    duration_ms?: number;
  };
  videoFeedUrl: string;
}

interface BackendContextValue {
  state: BackendState;
  sendCommand: (prompt: string) => Promise<void>;
  testConnection: () => Promise<boolean>;
  updateBackendUrl: (url: string) => void;
}

const BackendContext = React.createContext<BackendContextValue | undefined>(undefined);

export function BackendProvider({ children }: { children: React.ReactNode });
export function useBackend(): BackendContextValue;
```

**Implementation Details**:
- Wraps the entire App component in `main.tsx`
- Manages polling interval for status updates (500ms)
- Cleans up intervals on unmount or command completion
- Persists backend URL to localStorage
- Initializes API service with environment variable default

### 3. Backend CORS Configuration (ENHANCED)

**File**: `backend/app.py`

**Changes**:
```python
from flask_cors import CORS

def create_app() -> Flask:
    load_dotenv()
    app = Flask(__name__)
    
    # NEW: CORS configuration
    cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
    CORS(app, origins=cors_origins, supports_credentials=True)
    
    # ... rest of existing code
```

**Environment Variable**:
```ini
# .env
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

### 4. Settings Page Enhancement (MINIMAL ADDITION)

**File**: `Pet Training Web App/src/components/SettingsPage.tsx`

**Addition**: New card component inserted into existing layout

```tsx
{/* NEW: Backend Connection Card */}
<Card className="p-6">
  <div className="flex items-center gap-3 mb-6">
    <div className="w-10 h-10 rounded-lg bg-muted flex items-center justify-center">
      <Server className="w-5 h-5 text-muted-foreground" />
    </div>
    <div>
      <h3>Backend Connection</h3>
      <p className="text-sm text-muted-foreground">Configure API endpoint</p>
    </div>
  </div>

  <div className="space-y-4">
    <div className="space-y-2">
      <Label>Backend URL</Label>
      <Input 
        value={backendUrl} 
        onChange={(e) => setBackendUrl(e.target.value)}
        placeholder="http://localhost:5000"
      />
    </div>
    
    <div className="flex items-center gap-2">
      <Button onClick={handleTestConnection} variant="outline">
        Test Connection
      </Button>
      {connectionStatus && (
        <Badge variant={connectionStatus === 'connected' ? 'default' : 'destructive'}>
          {connectionStatus}
        </Badge>
      )}
    </div>
  </div>
</Card>
```

**Integration**: Uses `useBackend()` hook to access context methods

### 5. LivePage Integration (MINIMAL MODIFICATION)

**File**: `Pet Training Web App/src/components/LivePage.tsx`

**Changes**:
1. Import and use BackendContext
2. Replace hardcoded videoUrl with context value
3. Wire button handlers to context methods

```tsx
// At top of component
const { state, sendCommand } = useBackend();

// Replace videoUrl
const videoUrl = state.videoFeedUrl || 'https://images.unsplash.com/photo-1560807707-8cc77767d783?w=1600&h=900&fit=crop';

// Update handleAction
const handleAction = async (action: string) => {
  const promptMap = {
    'Pet': 'pick up the ball',
    'Treat': 'get the treat',
    'Fetch': 'go home'
  };
  
  try {
    await sendCommand(promptMap[action]);
    toast.success(`${action} command sent`);
  } catch (error) {
    toast.error(`Failed to send ${action} command`);
  }
};
```

## Data Models

### Environment Configuration

```typescript
// .env.example
VITE_API_BASE_URL=http://localhost:5000
```

### LocalStorage Schema

```typescript
interface StoredConfig {
  backendUrl: string;
  lastConnected?: string; // ISO timestamp
}

// Key: 'pet-training-backend-config'
```

### Backend API Contracts

All backend endpoints remain unchanged. The frontend adapts to the existing contract:

**POST /command**
```json
Request: {
  "prompt": "pick up the ball",
  "options": {}
}

Response: {
  "request_id": "uuid-string",
  "status": "accepted"
}
```

**GET /status/{request_id}**
```json
Response: {
  "state": "executing",
  "phase": "reaching",
  "confidence": 0.87,
  "duration_ms": 1234
}
```

**GET /video_feed**
- Returns MJPEG stream
- Content-Type: multipart/x-mixed-replace; boundary=frame

## Error Handling

### Network Errors

**Strategy**: Graceful degradation with user feedback

```typescript
try {
  await api.sendCommand(prompt);
} catch (error) {
  if (error instanceof NetworkError) {
    toast.error('Cannot reach backend. Check connection settings.');
  } else if (error instanceof ApiError) {
    toast.error(`Backend error: ${error.message}`);
  } else {
    toast.error('Unexpected error occurred');
  }
}
```

### Video Stream Failures

**Strategy**: Fallback to placeholder image

```tsx
<img 
  src={videoFeedUrl}
  alt="Live stream"
  onError={(e) => {
    e.currentTarget.src = PLACEHOLDER_IMAGE;
    toast.error('Video stream unavailable');
  }}
/>
```

### Command Execution Failures

**Strategy**: Stop polling and notify user

```typescript
if (status.state === 'failed') {
  clearInterval(pollingInterval);
  toast.error(`Command failed: ${status.message || 'Unknown error'}`);
}
```

### CORS Errors

**Strategy**: Clear error message with setup instructions

```typescript
if (error.message.includes('CORS')) {
  toast.error('Backend CORS not configured. Check backend settings.');
}
```

## Testing Strategy

### Backend Testing

**Unit Tests** (existing):
- Verify CORS headers are present in responses
- Test that OPTIONS requests are handled correctly

**Integration Tests** (existing):
- Verify frontend can successfully call all endpoints
- Test command execution flow end-to-end

### Frontend Testing

**Manual Testing**:
1. Start backend: `python backend/run_backend.py`
2. Start frontend: `npm run dev` in Pet Training Web App
3. Verify video stream loads
4. Test each command button
5. Verify toast notifications appear
6. Test Settings page connection test

**Browser Testing**:
- Chrome (primary)
- Firefox
- Safari
- Edge

### Error Scenario Testing

1. Backend offline → Graceful error messages
2. Invalid backend URL → Validation error
3. Command fails → Error toast with message
4. Network interruption → Automatic retry behavior

## Implementation Phases

### Phase 1: Backend CORS Setup
- Install flask-cors
- Add CORS configuration to app.py
- Add CORS_ORIGINS to .env.example
- Test with curl/Postman

### Phase 2: Frontend Service Layer
- Create api.ts service module
- Implement all endpoint methods
- Add TypeScript types
- Create .env.example with VITE_API_BASE_URL

### Phase 3: Backend Context
- Create BackendContext.tsx
- Implement state management
- Add status polling logic
- Wrap App with provider

### Phase 4: Settings Integration
- Add Backend Connection card to SettingsPage
- Implement connection test
- Add localStorage persistence
- Test URL validation

### Phase 5: LivePage Integration
- Import useBackend hook
- Wire video feed URL
- Connect command buttons
- Test all interactions

### Phase 6: Testing & Refinement
- End-to-end testing
- Error scenario testing
- Performance optimization
- Documentation updates

## Security Considerations

### CORS Configuration
- Use specific origins in production (not wildcard *)
- Validate origin against whitelist
- Consider authentication tokens for production

### API Authentication
- Support optional auth token in headers
- Store tokens securely (not in localStorage for production)
- Implement token refresh if needed

### Input Validation
- Validate backend URL format before saving
- Sanitize user inputs in Settings page
- Validate command prompts against allowed list

## Performance Considerations

### Status Polling
- 500ms interval balances responsiveness and load
- Stop polling immediately on completion/failure
- Clean up intervals on component unmount

### Video Streaming
- MJPEG is efficient for browser display
- No additional processing needed in frontend
- Browser handles frame buffering

### State Management
- Context updates trigger minimal re-renders
- Only LivePage and SettingsPage consume context
- No prop drilling through component tree

## Deployment Considerations

### Development
```bash
# Backend
cd backend
python run_backend.py

# Frontend
cd "Pet Training Web App"
npm run dev
```

### Production Build
```bash
# Frontend
npm run build
# Outputs to dist/

# Serve with any static server
npx serve dist
```

### Environment Configuration
- Development: Use .env with localhost URLs
- Production: Set VITE_API_BASE_URL to actual backend URL
- Backend: Set CORS_ORIGINS to include frontend domain

## Documentation Updates

### README Updates

**Pet Training Web App/README.md**:
```markdown
## Backend Integration

1. Copy `.env.example` to `.env`
2. Set `VITE_API_BASE_URL` to your backend URL (default: http://localhost:5000)
3. Start the backend server (see backend/README.md)
4. Run `npm run dev`
5. Configure backend URL in Settings page if needed
```

**backend/README.md**:
```markdown
## CORS Configuration

For browser-based frontends, configure allowed origins:

```ini
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

Multiple origins can be comma-separated.
```

## Migration Path

This design allows for incremental implementation:

1. **Backend First**: Add CORS, test with curl
2. **Service Layer**: Create API service, test independently
3. **Context Layer**: Add context, verify state management
4. **UI Integration**: Wire up one component at a time
5. **Full Testing**: End-to-end validation

Each phase can be tested independently before moving to the next.
