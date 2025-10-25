# Implementation Plan

- [x] 1. Set up project structure and core configuration













  - Initialize Next.js 14 project with TypeScript and App Router
  - Configure Tailwind CSS and shadcn/ui components
  - Set up FastAPI backend with Uvicorn
  - Create Docker Compose configuration for local development (Postgres, Redis, MinIO)
  - Configure environment variables for both frontend and backend
  - _Requirements: All_





- [x] 2. Implement database schema and migrations







  - Create SQLAlchemy models for users, devices, events, clips, snapshots, routines, ai_metrics_daily, and models tables
  - Write Alembic migration scripts for initial schema
  - Configure TimescaleDB extension and create hypertable for events

  - Add database indexes for optimized queries

  - _Requirements: 3.1, 4.4, 7.1, 7.2, 8.2, 11.3_

- [x] 3. Build video streaming infrastructure





  - [x] 3.1 Implement MJPEG streaming endpoint in FastAPI



    - Create `/video/mjpeg` endpoint that streams multipart/x-mixed-replace
    - Set up mock camera source (test pattern or sample video file)
    - _Requirements: 1.2_

  - [x] 3.2 Implement WebRTC signaling endpoints


    - Create `/video/webrtc/offer` POST endpoint for SDP exchange
    - Create `/video/webrtc/ice-candidates` GET endpoint for ICE candidate streaming
    - Implement aiortc peer connection handling
    - _Requirements: 1.1_

  - [x] 3.3 Build frontend video player component


    - Create VideoPlayer React component with WebRTC connection logic

    - Implement automatic fallback to MJPEG on WebRTC failure
    - Add playback controls (play, pause, PiP, fullscreen)
    - Implement latency slider control
    - _Requirements: 1.1, 1.2, 1.4_

- [x] 4. Implement WebSocket hub for real-time events







  - Create WebSocket endpoint `/ws/ui` using Starlette
  - Implement connection manager for multiple clients
  - Create message broadcasting system for events, overlays, and telemetry
  - Add Redis pub/sub for multi-instance support
  - _Requirements: 2.5, 11.5_

- [ ] 5. Create AI service stub with mock detections





  - [x] 5.1 Set up AI service Python project structure


    - Create separate Python service with gRPC or HTTP endpoints
    - Define protobuf schemas or Pydantic models for vision contracts
    - _Requirements: 3.1, 3.2_

  - [x] 5.2 Implement mock vision processing endpoint


    - Create `/vision/process` endpoint that returns fake detections
    - Generate mock dog bounding boxes, keypoints, and action labels
    - Return mock object detections (ball, toy, bowl)
    - _Requirements: 2.1, 2.2, 3.1, 3.2, 3.3_



  - [x] 5.3 Implement mock coach endpoints


    - Create `/coach/tips` endpoint with hardcoded training tips
    - Create `/coach/summary` endpoint with template-based summaries
    - Create `/coach/chat` endpoint with simple Q&A responses
    - _Requirements: 5.1, 5.2, 5.3, 5.4_

- [x] 6. Build overlay rendering system






  - [x] 6.1 Create canvas overlay layer in video player


    - Add HTML canvas element positioned over video
    - Implement overlay rendering loop synchronized with video frames
    - _Requirements: 2.1, 2.2, 2.3_

  - [x] 6.2 Implement detection box overlay


    - Draw bounding boxes with labels and confidence scores
    - Style boxes with colors based on detection type
    - _Requirements: 2.1_

  - [x] 6.3 Implement pose keypoints overlay

    - Draw keypoints for nose, shoulders, spine
    - Connect keypoints with skeleton lines
    - _Requirements: 2.2_

  - [x] 6.4 Implement heatmap overlay

    - Create motion accumulation buffer (10-minute window)
    - Render heatmap using color gradient
    - _Requirements: 2.3_

  - [x] 6.5 Add zone drawing and annotation tools


    - Implement lasso tool for region selection
    - Add virtual cone/target placement
    - Store zones in component state
    - _Requirements: 2.5_

  - [x] 6.6 Create overlay toggle controls


    - Add UI controls to enable/disable each overlay type
    - Persist overlay preferences in local storage
    - _Requirements: 2.4_

- [x] 7. Implement event logging and storage





  - [x] 7.1 Create event API endpoints


    - Implement `POST /api/events` for manual event creation
    - Implement `GET /api/events` with filtering by date range and type
    - _Requirements: 4.1, 11.1, 11.2_

  - [x] 7.2 Build event processing pipeline


    - Create background worker that processes AI detections into events
    - Implement auto-bookmark logic for significant motion
    - Implement auto-clip logic for fetch-return and treat-eaten sequences
    - Batch insert events to database every 1 second

    - _Requirements: 4.1, 4.2, 11.1, 11.2, 11.3_

  - [x] 7.3 Create event feed component


    - Build EventFeed React component with real-time WebSocket updates
    - Add emoji markers for different event types
    - Implement click-to-jump-to-timestamp functionality
    - Add event type filtering
    - _Requirements: 4.1, 4.2_

- [x] 8. Build media management system






  - [x] 8.1 Implement snapshot capture


    - Create `POST /api/snapshots` endpoint
    - Capture current video frame and upload to S3/MinIO
    - Store snapshot metadata in database
    - _Requirements: 6.1_

  - [x] 8.2 Implement clip creation with background jobs



    - Create `POST /api/clips` endpoint that queues clip job
    - Set up Celery or ARQ worker for clip processing
    - Implement video segment extraction and upload to S3

    - Create `GET /api/clips/{id}` endpoint for status and retrieval
    - _Requirements: 4.2, 6.2_

  - [x] 8.3 Build gallery component



    - Create Gallery page with grid view of snapshots and clips
    - Implement thumbnail loading with lazy loading

    - Add delete functionality for media items
    - Generate and display share links
    - _Requirements: 4.5, 6.2_
- [x] 9. Implement keyboard shortcuts














- [x] 9. Implement keyboard shortcuts


  - Create global keyboard event handler
  - Implement 's' for snapshot, 'c' for clip mark, 'b' for bookmark, 'f' for fullscreen
  - Display keyboard shortcut hints in UI
  - _Requirements: 6.1, 6.2, 6.3, 6.4_

- [x] 10. Build timeline component with markers






  - Create Timeline component with scrubber
  - Display emoji markers for events on timeline
  - Implement clip in/out handle controls
  - Add zoom and pan controls for timeline
  - _Requirements: 6.5_

- [x] 11. Implement training analytics and charts





  - [x] 11.1 Create daily metrics aggregation


    - Implement background job that aggregates events into ai_metrics_daily table
    - Calculate sit/stand/lie counts, fetch attempts/successes, time in frame, calm minutes
    - Run aggregation job every hour for current day
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 11.1, 11.2, 11.3, 11.4_

  - [x] 11.2 Build analytics API endpoints


    - Create `GET /api/analytics/daily` with date range filtering
    - Create `GET /api/analytics/streaks` for badge calculations
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

  - [x] 11.3 Create analytics dashboard component


    - Build AnalyticsDashboard with Recharts time-series visualizations
    - Display time-in-frame vs off-frame chart
    - Display sit/stand/lie counts with hourly buckets
    - Display fetch attempts vs successes chart
    - Display bark frequency over time


    - _Requirements: 7.1, 7.2, 7.3, 7.4_

  - [x] 11.4 Implement progress page with trends


    - Create 7-day trendlines for key metrics
    - Calculate and display best training hour
    - Calculate reinforcement ratio (cues vs correct responses)
    - Display correlation tiles
    - _Requirements: 7.5_

  - [x] 11.5 Implement streaks and badges


    - Calculate training streaks (consecutive days)
    - Award badges for milestones (7-day sit streak, 5 perfect recall days)
    - Display badges and current streaks on analytics page
    - _Requirements: 9.1, 9.2, 9.3, 9.4_

- [x] 12. Build routine builder and scheduler






  - [x] 12.1 Create routine API endpoints


    - Implement `GET /api/routines` to list all routines
    - Implement `POST /api/routines` to create new routine
    - Implement `PUT /api/routines/{id}` to update routine
    - Implement `DELETE /api/routines/{id}` to delete routine
    - _Requirements: 8.2, 8.3_

  - [x] 12.2 Build routine builder UI component


    - Create RoutineBuilder with drag-and-drop step ordering
    - Implement step type selector (pet, treat, play, sit drill, fetch, wait)
    - Add cron expression builder with validation
    - Add enable/disable toggle
    - _Requirements: 8.1, 8.2_

  - [x] 12.3 Implement routine scheduler


    - Create background worker that checks for scheduled routines
    - Send notification when routine time arrives
    - Store routine execution history
    - _Requirements: 8.4_

- [x] 13. Implement robot integration placeholders






  - [x] 13.1 Create robot action bar component


    - Build RobotActionBar with pet, treat, fetch buttons
    - Display "not connected" state when device offline
    - Show tooltips explaining future functionality
    - Disable buttons when device unavailable


    - _Requirements: 10.1, 10.4_

  - [x] 13.2 Implement device status display


    - Create device status pill showing "offline"
    - Add telemetry strip with mock FPS and temperature
    - _Requirements: 10.2, 10.3_

  - [x] 13.3 Create command API stub


    - Implement `POST /api/commands` endpoint returning 501 status
    - Return "Robot not connected" message
    - _Requirements: 10.1_

  - [x] 13.4 Add policy selector UI


    - Create policy dropdown with options (replay, act, smolvla)
    - Disable dropdown until device connected
    - _Requirements: 10.4_


- [x] 14. Implement AI model management





  - [x] 14.1 Create models API endpoints


    - Implement `GET /api/models` to list available and active models
    - Implement `POST /api/models/switch` for runtime model switching
    - _Requirements: 12.1, 12.2, 12.5_


  - [x] 14.2 Build model switching UI


    - Create settings page with model selector dropdowns
    - Display current active models
    - Show model switch confirmation and status
    - _Requirements: 12.2, 12.5_

  - [x] 14.3 Implement model hot-swap in AI service


    - Add model loading and unloading logic
    - Validate model compatibility before switching
    - Maintain detection continuity during switch
    - _Requirements: 12.2, 12.3, 12.4_

- [x] 15. Add status and telemetry endpoints








  - Implement `GET /api/status` endpoint
  - Return device status, video type, FPS, latency, active AI models
  - Update status in real-time via WebSocket
  - _Requirements: 1.5, 10.2, 10.3_

- [x] 16. Implement coach chat interface






  - Create CoachChat component with message history
  - Implement chat input and send functionality
  - Call `/coach/chat` endpoint with question and context
  - Display answers with timestamp links
  - _Requirements: 5.4_

- [x] 17. Polish UI and add final features







  - [x] 17.1 Implement reconnection handling


    - Display reconnection banner when WebSocket disconnects
    - Implement exponential backoff retry logic
    - Show connection status indicator
    - _Requirements: 1.1, 1.2_

  - [x] 17.2 Add toast notifications


    - Integrate toast library (sonner or react-hot-toast)
    - Show toasts for snapshot saved, clip created, errors
    - _Requirements: 6.1, 6.2_

  - [x] 17.3 Create settings modal


    - Build settings page with video quality, overlay, and notification preferences
    - Persist settings in local storage
    - _Requirements: 1.5, 2.4_

  - [x] 17.4 Implement responsive layout


    - Ensure all pages work on tablet and desktop
    - Adjust video player for different screen sizes
    - _Requirements: All_

- [x] 18. Add seed data and demo mode










  - Create database seed script with sample events and metrics
  - Generate mock clips and snapshots for gallery
  - Add demo mode toggle that uses pre-recorded video
  - _Requirements: All_

- [ ]* 19. Write integration tests
  - Write tests for video streaming endpoints
  - Write tests for WebSocket event broadcasting
  - Write tests for clip creation workflow
  - Write tests for analytics aggregation
  - _Requirements: All_

- [ ]* 20. Create deployment documentation
  - Document Docker Compose setup
  - Document environment variable configuration
  - Create README with setup instructions
  - _Requirements: All_
