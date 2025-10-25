# Implementation Plan

- [ ] 1. Set up backend project structure and core interfaces
  - Create Flask application scaffold with blueprint organization
  - Define hardware adapter interfaces (LerobotArm, ServoController, TTS, Camera)
  - Implement mock versions of all hardware adapters for development
  - Set up environment variable loading from .env file
  - Configure JSON logging with timestamp, level, and request_id fields
  - _Requirements: 8.2, 8.3_

- [ ] 2. Implement command state machine and in-memory storage
  - Create CommandState class with state, phase, confidence, message, duration_ms fields
  - Implement state transition methods (idle→executing, executing→completed/failed/timeout/interrupted)
  - Add single-active-command guard that returns 409 when command already executing
  - Implement Go Home preemption logic that interrupts any active command
  - Add timeout tracking with configurable timeout_ms per command
  - _Requirements: 2.2, 2.3, 4.2_

- [ ] 3. Implement REST API endpoints
  - [ ] 3.1 Create /health endpoint returning status, api version, and system version
    - Return JSON with status:"ok", api:1, version:"v0.1"
    - Add optional X-LePetPal-API header validation
    - _Requirements: 8.1, 8.5_

  - [ ] 3.2 Create /command POST endpoint with request_id generation
    - Validate command type against whitelist (pick up the ball, get the treat, go home, throw ball)
    - Check single-active-command guard, return 409 if busy
    - Generate UUID v4 request_id and initialize command state
    - Return 202 Accepted with request_id
    - _Requirements: 2.1, 2.2, 7.1, 7.2_

  - [ ] 3.3 Create /status/{request_id} GET endpoint for polling fallback
    - Look up command state by request_id
    - Return 404 if request_id not found
    - Return current state, phase, confidence, message, duration_ms
    - _Requirements: 2.5_

  - [ ] 3.4 Create /dispense_treat POST endpoint
    - Validate duration_ms parameter (positive integer, max 5000ms)
    - Call ServoController.dispense(duration_ms)
    - Return 200 with status:"ok"
    - _Requirements: 3.1, 3.2_

  - [ ] 3.5 Create /speak POST endpoint
    - Validate text parameter (max 200 characters)
    - Call TTS.speak(text) asynchronously
    - Return 200 with status:"ok" immediately
    - _Requirements: 9.1, 9.2, 9.4_

- [ ] 4. Implement SSE /events endpoint and broadcast mechanism
  - Create /events endpoint returning text/event-stream content type
  - Implement SSE client registry for managing multiple connected clients
  - Create broadcast_event function that emits command_update events to all clients
  - Format events with "event: command_update" and JSON data payload
  - Integrate broadcast calls into state machine transitions (emit within 100ms)
  - _Requirements: 2.4, 5.1, 5.2_

- [ ] 5. Implement MJPEG video streaming with overlays
  - [ ] 5.1 Create /video_feed GET endpoint with query parameters
    - Parse width, height, overlays parameters with defaults (1280, 720, 1)
    - Set response content-type to multipart/x-mixed-replace
    - _Requirements: 1.1_

  - [ ] 5.2 Implement frame capture loop from Camera adapter
    - Capture frames at configured FPS (target 15+)
    - Resize frames to requested width/height
    - _Requirements: 1.3_

  - [ ] 5.3 Implement overlay renderer for detection zones and markers
    - Draw bounding boxes for detected objects with confidence scores
    - Draw zone markers (bowl, treat dispenser) from calibration
    - Add phase indicator text in corner
    - Only render overlays when overlays=1 parameter
    - _Requirements: 1.2_

  - [ ] 5.4 Implement MJPEG encoder and streaming
    - Encode frames as JPEG with quality 85
    - Stream frames with multipart boundary format
    - Handle client disconnections gracefully
    - _Requirements: 1.1, 1.3_

- [ ] 6. Implement command execution loop with phase management
  - [ ] 6.1 Create command loop thread that processes active command
    - Start thread when command transitions to executing state
    - Poll command state for interrupt or timeout conditions
    - Transition to appropriate final state when loop completes
    - _Requirements: 2.3_

  - [ ] 6.2 Implement detect phase with vision model integration
    - Capture frame from camera
    - Run object detection model (ball or treat based on command)
    - Check confidence against threshold (default 0.7)
    - Transition to failed if confidence too low after retries
    - Update state with phase:"detect" and confidence value
    - _Requirements: 2.3, 2.4_

  - [ ] 6.3 Implement approach phase with arm movement
    - Calculate target joint positions from detection coordinates
    - Validate joint positions against limits
    - Send joint targets to LerobotArm
    - Wait for position reached with 5 second timeout
    - Update state with phase:"approach"
    - _Requirements: 2.3, 4.4_

  - [ ] 6.4 Implement grasp, lift, drop phases
    - Grasp: Close gripper, validate pressure sensor feedback
    - Lift: Move arm to lift position, check object still grasped
    - Drop: Move to bowl zone, open gripper, return to ready
    - Update state with appropriate phase after each step
    - _Requirements: 2.3_

  - [ ] 6.5 Implement ready_to_throw phase and throw macro
    - Transition to ready_to_throw after successful drop
    - Implement throw macro that only executes from ready_to_throw state
    - Validate throw guards (object in gripper, safe trajectory)
    - Execute throw motion sequence
    - _Requirements: 4.4_

  - [ ] 6.6 Implement timeout enforcement
    - Track elapsed time since command start
    - Check against timeout_ms on each loop iteration
    - Transition to timeout state if exceeded
    - Broadcast timeout event via SSE
    - _Requirements: 2.3_

- [ ] 7. Implement Go Home interrupt and safety features
  - [ ] 7.1 Implement Go Home command preemption logic
    - Set interrupt flag when go home command received
    - Check interrupt flag in command loop on each iteration
    - Immediately stop current phase and call LerobotArm.home()
    - Transition active command to interrupted state
    - Start new command for go home with high priority
    - _Requirements: 4.1, 4.2, 4.3_

  - [ ] 7.2 Implement joint limit validation
    - Define safe joint angle ranges in configuration
    - Validate all joint targets before sending to arm
    - Return error if any joint exceeds limits
    - _Requirements: 4.5_

  - [ ] 7.3 Ensure Go Home completes within 1 second
    - Use direct joint trajectory (no path planning)
    - Set high velocity limits for home motion
    - Add timeout guard (fail if >1s)
    - _Requirements: 4.2_

- [ ] 8. Implement Give Treat two-step workflow
  - Create give_treat_flow function that orchestrates dispense + command
  - Step 1: POST to /dispense_treat with configured duration
  - Step 2: POST to /command with "get the treat"
  - Return combined request_id for tracking
  - Handle errors in either step gracefully
  - _Requirements: 3.3_

- [ ] 9. Implement configuration and calibration persistence
  - [ ] 9.1 Load configuration from environment variables
    - Parse PORT, CAMERA_INDEX, STREAM_WIDTH, STREAM_HEIGHT, STREAM_FPS
    - Parse CONFIDENCE_THRESHOLD, DETECTION_TIMEOUT_MS
    - Parse USE_MOCK_HARDWARE flag
    - Set defaults for all optional variables
    - _Requirements: 8.2_

  - [ ] 9.2 Implement calibration file loading and saving
    - Load calibration.json on startup if exists
    - Parse camera ROI, zone coordinates, arm positions
    - Provide defaults if calibration file missing
    - _Requirements: Design - Calibration Persistence_

- [ ] 10. Implement error handling and logging
  - [ ] 10.1 Create error response helper functions
    - invalid_request(message) returns 400 with error:"invalid"
    - busy_response() returns 409 with error:"busy"
    - internal_error(exception) returns 500 with error:"internal"
    - _Requirements: 7.1, 7.2, 7.4_

  - [ ] 10.2 Add structured JSON logging for state transitions
    - Log every state transition with timestamp, request_id, from_state, to_state
    - Log phase transitions with confidence and duration
    - Log errors with stack traces
    - _Requirements: 8.3_

  - [ ] 10.3 Add exception handling to all endpoints
    - Wrap endpoint logic in try-except blocks
    - Return appropriate error responses
    - Log exceptions before returning 500
    - _Requirements: 7.4_

- [ ]* 10.4 Write backend unit tests
    - Test command state machine transitions
    - Test single-active-command guard
    - Test Go Home preemption
    - Test timeout enforcement
    - Test confidence gating
    - _Requirements: 2.2, 2.3, 4.2_

- [x] 11. Set up frontend Next.js project structure
  - Initialize Next.js 14 project with TypeScript
  - Set up React Context for global state management
  - Create component directory structure (ConfigPanel, VideoPanel, CommandBar, StatusDisplay)
  - Configure environment variable loading from .env.local
  - Set up CSS modules or Tailwind for styling
  - _Requirements: 6.1_

- [x] 12. Implement ConfigPanel component





  - [x] 12.1 Create base URL input field with validation


    - Text input for base URL (e.g., http://192.168.1.100:5000)
    - Validate URL format on blur
    - Display validation errors inline
    - _Requirements: 6.1_

  - [x] 12.2 Create optional token input field

    - Password-style input for API token
    - Toggle visibility button
    - _Requirements: 6.1_

  - [x] 12.3 Implement localStorage persistence

    - Save config to localStorage on save button click
    - Load config from localStorage on component mount
    - Clear config on reset button click
    - _Requirements: 6.1_

  - [x] 12.4 Implement connection test button

    - Fetch /health endpoint when clicked
    - Display success/failure message
    - Update connection status in global state
    - _Requirements: 6.1_

- [x] 13. Implement VideoPanel component





  - Create img element with src pointing to /video_feed endpoint
  - Append width, height, overlays query parameters from config
  - Implement error overlay when stream unavailable
  - Add loading spinner during initial connection
  - Implement responsive sizing with aspect ratio preservation
  - _Requirements: 1.4, 10.2, 10.3_

- [x] 14. Implement CommandBar component





  - [x] 14.1 Create preset command buttons


    - Buttons for "Play with Ball", "Give Treat", "Go Home", "Speak"
    - Map buttons to correct command strings
    - _Requirements: 6.2_

  - [x] 14.2 Implement button state management

    - Disable all buttons except Go Home while command executing
    - Show loading spinner on active button
    - Enable all buttons when idle
    - _Requirements: 6.3_

  - [x] 14.3 Wire buttons to executeCommand action

    - Call executeCommand with appropriate command string
    - Handle response and update global state
    - _Requirements: 6.2_
-

- [x] 15. Implement StatusDisplay component




  - [x] 15.1 Create global status chip


    - Display Idle (green), Executing (blue), Error (red) states
    - Position in top-right corner
    - _Requirements: 6.4_

  - [x] 15.2 Create phase indicator

    - Display current phase during execution (e.g., "Detecting ball...")
    - Hide when idle
    - _Requirements: 6.4_

  - [x] 15.3 Create confidence meter

    - Progress bar showing 0-100% confidence
    - Only visible during detect phase
    - _Requirements: 6.4_

  - [x] 15.4 Create duration counter

    - Display elapsed time in seconds
    - Update every 100ms during execution
    - _Requirements: 6.4_

  - [x] 15.5 Create final state banner

    - Display success banner with green background when completed
    - Display failure banner with red background when failed/timeout
    - Show descriptive message from command state
    - Auto-dismiss after 5 seconds or manual close
    - _Requirements: 6.5_

- [x] 16. Implement SSEClient with polling fallback





  - [x] 16.1 Create SSEClient class with EventSource


    - Connect to /events endpoint on mount
    - Listen for command_update events
    - Parse JSON data from event
    - _Requirements: 5.1, 5.2_

  - [x] 16.2 Implement event handler that updates React state


    - Call updateCommandState action with parsed data
    - Update UI within 100ms of receiving event
    - _Requirements: 5.3_

  - [x] 16.3 Implement polling fallback for SSE failures

    - Detect SSE connection failure or unsupported browser
    - Start polling /status/{request_id} every 500ms
    - Stop polling when final state reached
    - _Requirements: 5.4_

  - [x] 16.4 Implement SSE reconnection with exponential backoff

    - Detect connection drops via onerror event
    - Retry connection with delays: 500ms, 1s, 2s, 4s, 8s (max)
    - Reset backoff on successful connection
    - _Requirements: 5.5_

- [x] 17. Implement command execution with retry logic








  - [x] 17.1 Create executeCommand function


    - POST to /command endpoint with command string
    - Parse response and extract request_id
    - Update global state with request_id and executing status
    - _Requirements: 6.2_


  - [x] 17.2 Implement 409 busy retry with exponential backoff


    - Detect 409 status code
    - Retry with delays: 500ms, 1s, 2s (with jitter)
    - Max 5 retry attempts
    - Display "System busy, retrying..." message
    - _Requirements: 7.3_


  - [x] 17.3 Implement error handling for other status codes


    - 400: Display validation error message
    - 500: Display "Server error" message
    - Network error: Display "Connection failed" message
    - _Requirements: 7.5_

- [x] 18. Implement error toast notifications





  - Create toast container component in app layout
  - Implement addError action that adds toast to queue
  - Auto-dismiss toasts after 5 seconds
  - Allow manual dismissal via close button
  - Stack multiple toasts vertically
  - _Requirements: 7.5_

- [x] 19. Implement mobile responsive layout





  - [x] 19.1 Create responsive grid layout


    - Stack components vertically on mobile (<768px)
    - Side-by-side layout on desktop (≥768px)
    - _Requirements: 10.1_

  - [x] 19.2 Implement responsive video sizing


    - Full width on mobile with aspect ratio preservation
    - Fixed width on desktop (e.g., 640px)
    - _Requirements: 10.2_

  - [x] 19.3 Implement touch-friendly button sizing


    - Minimum 44px tap targets for all buttons
    - Adequate spacing between buttons (8px minimum)
    - _Requirements: 10.3_

  - [x] 19.4 Test on mobile browsers


    - Verify layout on iOS Safari and Chrome
    - Verify layout on Android Chrome
    - Test touch interactions
    - _Requirements: 10.4_

- [ ]* 20. Write frontend component tests
    - Test ConfigPanel save/load from localStorage
    - Test CommandBar button enable/disable logic
    - Test StatusDisplay state rendering
    - Test SSEClient connection and reconnection
    - Test error toast display and dismissal
    - _Requirements: 6.1, 6.2, 6.3_

- [x] 21. Create backend startup script and documentation





  - Create run_backend.py script that initializes hardware and starts Flask server
  - Create .env.example with all configuration variables and descriptions
  - Write README with quick-start instructions and endpoint documentation
  - Document hardware setup requirements (camera, servo, arm)
  - _Requirements: 8.2_

- [x] 22. Create frontend build and deployment scripts





  - Configure npm scripts for dev, build, start
  - Create .env.local.example with NEXT_PUBLIC_API_BASE
  - Write README with development and production setup instructions
  - Document browser compatibility requirements
  - _Requirements: 8.4_

- [ ] 23. Integration testing and checkpoint validation




  - [ ] 23.1 IC-1: LAN with stubs
    - Start backend with mock hardware
    - Start frontend and configure base URL
    - Verify video feed renders
    - Verify command acceptance and mock SSE events
    - _Requirements: 1.1, 2.1, 2.4_

  - [ ] 23.2 IC-2: Servo + Speak
    - Connect physical servo hardware
    - Test /dispense_treat endpoint actuation
    - Test /speak endpoint audio output
    - Execute Give Treat end-to-end flow
    - _Requirements: 3.2, 9.2_

  - [ ] 23.3 IC-3: Model-in-loop
    - Integrate vision model for detection
    - Test "pick up the ball" command with real inference
    - Test "get the treat" command with real inference
    - Verify Go Home interrupt during execution
    - _Requirements: 2.3, 4.2_

  - [ ] 23.4 IC-4: Demo script dry run
    - Execute full demo scenario: Give Treat 3x, Play with Ball 3x
    - Tune confidence thresholds and timeouts
    - Test optional throw macro if guards pass
    - Verify all acceptance criteria met
    - _Requirements: All_
