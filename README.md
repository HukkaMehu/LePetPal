# Dog Monitor Web Application

AI-powered dog monitoring and training assistant with real-time video streaming, behavior detection, and training analytics.

## Project Structure

```
.
├── frontend/          # Next.js 14 frontend application
├── backend/           # FastAPI backend service
├── docker-compose.yml # Local development infrastructure
└── README.md
```

## Prerequisites

- Node.js 18+ and npm/yarn
- Python 3.11+
- Docker and Docker Compose

## Quick Start

### 1. Start Infrastructure Services

Start PostgreSQL, Redis, and MinIO using Docker Compose:

```bash
docker-compose up -d
```

Verify services are running:
```bash
docker-compose ps
```

### 2. Setup Backend

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
copy .env.example .env

# Run database migrations
alembic upgrade head

# Start backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at http://localhost:8000

### 3. Setup Frontend

```bash
cd frontend

# Install dependencies
npm install

# Copy environment file
copy .env.local.example .env.local

# Start development server
npm run dev
```

Frontend will be available at http://localhost:3000

## Services

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379
- **MinIO Console**: http://localhost:9001 (minioadmin/minioadmin)
- **MinIO API**: http://localhost:9000

## Environment Variables

### Backend (.env)

See `backend/.env.example` for all available configuration options.

### Frontend (.env.local)

See `frontend/.env.local.example` for all available configuration options.

## Development

### Backend

The backend uses FastAPI with:
- SQLAlchemy for ORM
- Alembic for migrations
- Pydantic for validation
- Uvicorn as ASGI server

### Frontend

The frontend uses Next.js 14 with:
- App Router
- TypeScript
- Tailwind CSS
- shadcn/ui components
- Zustand for state management
- React Query for API calls

## Database Migrations

Create a new migration:
```bash
cd backend
alembic revision --autogenerate -m "description"
```

Apply migrations:
```bash
alembic upgrade head
```

Rollback migration:
```bash
alembic downgrade -1
```

## Stopping Services

Stop infrastructure:
```bash
docker-compose down
```

Stop with data cleanup:
```bash
docker-compose down -v
```

## Features Implemented

### Video Streaming
- WebRTC and MJPEG streaming support
- Automatic fallback to MJPEG on WebRTC failure
- Playback controls (play, pause, PiP, fullscreen)
- Latency adjustment slider

### AI Overlays
- Detection boxes with confidence scores
- Pose keypoints visualization
- Motion heatmap
- Zone drawing and annotations
- Toggle controls for each overlay type

### Event System
- Real-time event feed via WebSocket
- Event filtering by type
- Emoji markers for different event types
- Click-to-jump-to-timestamp functionality

### Media Management
- Snapshot capture (keyboard shortcut: S)
- Clip creation with background processing
- Gallery view with thumbnails
- Share links for media items

### Timeline Component
- Interactive scrubber for seeking
- Event markers with emoji indicators
- Clip in/out handles for creating clips
- Zoom (1x to 10x) and pan controls
- Keyboard shortcuts (I for in, O for out)

### Keyboard Shortcuts
- **S** - Capture snapshot
- **C** - Mark clip
- **B** - Create bookmark
- **F** - Toggle fullscreen
- **I** - Set clip in point
- **O** - Set clip out point
- **Space** - Play/Pause

## Demo Mode

The application includes a comprehensive demo mode with pre-loaded sample data and pre-recorded video. This is perfect for testing, demonstrations, and exploring features without a live camera.

### Quick Demo Setup

1. **Seed the database** with sample data:
   ```bash
   cd backend
   python scripts/seed_database.py
   ```

2. **Generate mock media** files:
   ```bash
   python scripts/generate_mock_media.py
   ```

3. **Enable demo mode** in the application:
   - Visit `http://localhost:3000/demo`
   - Click "Enable Demo Mode"
   - Or go to Settings and check "Enable Demo Mode"

4. **Explore the features** with 7 days of sample events, metrics, clips, and snapshots!

For detailed instructions, see [DEMO_MODE.md](DEMO_MODE.md).

## Demo Pages

- `/` - Main video player with overlays
- `/demo` - Demo mode setup and information
- `/overlay-demo` - Overlay system demonstration
- `/events-demo` - Event feed demonstration
- `/timeline-demo` - Timeline component demonstration
- `/keyboard-test` - Keyboard shortcuts testing

## Next Steps

Follow the implementation tasks in `.kiro/specs/dog-monitor-webapp/tasks.md` to build out the features.

## Troubleshooting

### Integration Tests Failing with 404 Errors

If you're getting 404 errors when running integration tests, ensure:

1. **Backend API URL includes `/api` prefix**:
   - Check `Pet Training Web App/.env`
   - Should be: `VITE_API_BASE_URL=http://localhost:8000/api`

2. **WebSocket URL uses correct endpoint**:
   - Check `Pet Training Web App/.env`
   - Should be: `VITE_WS_URL=ws://localhost:8000/ws/ui`

3. **All services are running**:
   ```bash
   # Check backend
   curl http://localhost:8000/api/status
   
   # Check AI service
   curl http://localhost:8001/health
   
   # Check frontend
   # Open http://localhost:3000 or http://localhost:3001
   ```

4. **AI Service is started**:
   ```bash
   cd ai_service
   venv\Scripts\activate
   uvicorn main:app --reload --port 8001
   ```

### Quick Start All Services

Use the provided start script:
```bash
# Windows
start-dev.bat

# Linux/macOS
./start-dev.sh
```

This will start:
- Docker infrastructure (PostgreSQL, Redis, MinIO)
- Backend API (port 8000)
- AI Service (port 8001)
- Frontend (port 3000/3001)

### Running Integration Tests

Integration tests run in the browser:

1. Open http://localhost:3000 (or 3001)
2. Navigate to the Test Page
3. Or open browser console and run:
   ```javascript
   runAllTests()
   ```

See `INTEGRATION_FIX.md` for detailed troubleshooting information.
