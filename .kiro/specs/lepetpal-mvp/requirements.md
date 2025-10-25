# Requirements Document

## Introduction

LePetPal is an AI-first robotics system designed for interactive pet engagement through camera-based commands. The system enables two core interactions: "Give Treat" (dispensing treats via servo control) and "Play with Ball" (robotic arm manipulation). The MVP targets hackathon-ready deployment with a frozen integration contract between backend robotics services and frontend web interface, supporting real-time command execution with SSE-based state updates and safety-first interrupt capabilities.

## Glossary

- **LePetPal System**: The complete robotics platform including backend server, robotic arm, camera, servo dispenser, and web frontend
- **Backend Service**: Python-based server managing hardware control, computer vision inference, and API endpoints
- **Frontend Client**: Next.js web application providing user interface and command controls
- **Command State Machine**: Single-active-command execution engine managing command lifecycle and phase transitions
- **SSE Stream**: Server-Sent Events real-time broadcast channel for command state updates
- **Robotic Arm**: LeRobot-compatible arm hardware for ball manipulation tasks
- **Servo Controller**: SG90 servo mechanism for treat dispensing
- **MJPEG Stream**: Motion JPEG video feed with overlay annotations
- **Go Home Command**: Safety interrupt command that preempts all other operations

## Requirements

### Requirement 1: Video Streaming

**User Story:** As a user, I want to view a live video feed with visual overlays, so that I can monitor the robot's environment and command execution in real-time.

#### Acceptance Criteria

1. THE Backend Service SHALL provide an MJPEG video stream at the `/video_feed` endpoint with configurable width and height parameters
2. WHEN overlays parameter equals 1, THE Backend Service SHALL render visual annotations on the video stream including detection zones and object markers
3. THE Backend Service SHALL maintain video stream frame rate at 15 frames per second or higher
4. THE Frontend Client SHALL display the video stream by rendering the MJPEG feed from the configured base URL
5. WHEN the video stream is unavailable, THE Frontend Client SHALL display an error message indicating connection failure

### Requirement 2: Command Execution

**User Story:** As a user, I want to execute predefined commands like "Play with Ball" and "Give Treat", so that I can interact with my pet through the robotic system.

#### Acceptance Criteria

1. THE Backend Service SHALL accept command requests via POST to `/command` endpoint and return a unique request identifier
2. THE Command State Machine SHALL enforce single active command execution and return HTTP 409 status code when a command is already executing
3. WHEN a command is accepted, THE Backend Service SHALL transition through defined phases including detect, approach, grasp, lift, drop, and ready_to_throw for ball manipulation
4. THE Backend Service SHALL broadcast command state transitions via SSE stream at `/events` endpoint with latency under 100 milliseconds
5. THE Backend Service SHALL provide command status via GET `/status/{request_id}` endpoint as a polling fallback for clients without SSE support

### Requirement 3: Treat Dispensing

**User Story:** As a user, I want to dispense treats to my pet on command, so that I can reward positive behavior remotely.

#### Acceptance Criteria

1. THE Backend Service SHALL accept treat dispense requests via POST to `/dispense_treat` endpoint with duration parameter in milliseconds
2. WHEN a dispense request is received, THE Servo Controller SHALL actuate the SG90 servo for the specified duration
3. THE Backend Service SHALL execute the two-step "Give Treat" flow by first dispensing the treat, then executing the "get the treat" command
4. THE Backend Service SHALL complete treat dispensing operations within 2 seconds of request acceptance
5. WHEN treat dispensing succeeds, THE Backend Service SHALL return HTTP 200 status with confirmation message

### Requirement 4: Safety and Interrupts

**User Story:** As a user, I want an emergency stop capability, so that I can immediately halt robot operations if something goes wrong.

#### Acceptance Criteria

1. THE Backend Service SHALL accept Go Home Command via POST to `/command` endpoint at any time regardless of current command state
2. WHEN Go Home Command is received, THE Command State Machine SHALL preempt the active command and transition to home position within 1 second
3. THE Backend Service SHALL broadcast interrupt event via SSE stream immediately upon Go Home Command acceptance
4. THE Robotic Arm SHALL execute throw macro only when Command State Machine is in ready_to_throw phase
5. THE Backend Service SHALL enforce joint limit checks before executing any arm movement commands

### Requirement 5: Real-Time State Updates

**User Story:** As a user, I want to see command execution progress in real-time, so that I understand what the robot is doing and when operations complete.

#### Acceptance Criteria

1. THE Backend Service SHALL establish SSE connection at `/events` endpoint when Frontend Client connects
2. WHEN Command State Machine transitions between phases, THE Backend Service SHALL emit command_update event via SSE stream containing request_id, state, phase, confidence, message, and duration_ms
3. THE Frontend Client SHALL update user interface within 100 milliseconds of receiving SSE command_update events
4. WHEN SSE connection fails or is unsupported, THE Frontend Client SHALL poll `/status/{request_id}` endpoint every 500 milliseconds until command reaches final state
5. WHEN SSE connection drops, THE Frontend Client SHALL attempt reconnection with exponential backoff starting at 500 milliseconds

### Requirement 6: User Interface Controls

**User Story:** As a user, I want a simple web interface with preset commands, so that I can easily control the robot without technical knowledge.

#### Acceptance Criteria

1. THE Frontend Client SHALL provide configuration panel for setting base URL and optional authentication token with persistence in browser localStorage
2. THE Frontend Client SHALL display command presets including Play with Ball, Give Treat, Go Home, and Speak as clickable buttons
3. WHILE a command is executing, THE Frontend Client SHALL disable all command buttons except Go Home
4. THE Frontend Client SHALL display global status indicator showing Idle, Executing, or Error states
5. WHEN command execution completes, THE Frontend Client SHALL display success or failure banner with descriptive message

### Requirement 7: Error Handling and Resilience

**User Story:** As a user, I want clear error messages and automatic retry logic, so that temporary issues don't prevent me from using the system.

#### Acceptance Criteria

1. THE Backend Service SHALL return HTTP 400 status code for invalid command parameters with descriptive error message
2. THE Backend Service SHALL return HTTP 409 status code when command is rejected due to busy state
3. WHEN Frontend Client receives HTTP 409 response, THE Frontend Client SHALL retry request with exponential backoff from 500 milliseconds to 2 seconds with jitter
4. THE Backend Service SHALL return HTTP 500 status code for internal errors with logged stack trace
5. THE Frontend Client SHALL display error toast notifications for all failed operations with user-friendly error descriptions

### Requirement 8: System Health and Configuration

**User Story:** As a developer, I want health check endpoints and environment-based configuration, so that I can verify system status and customize deployment settings.

#### Acceptance Criteria

1. THE Backend Service SHALL provide health check at `/health` endpoint returning status, API version, and system version
2. THE Backend Service SHALL load configuration from environment variables including PORT, CAMERA_INDEX, STREAM_RES, and detection thresholds
3. THE Backend Service SHALL log all command state transitions and durations in JSON format
4. THE Frontend Client SHALL load API base URL from NEXT_PUBLIC_API_BASE environment variable
5. THE Backend Service SHALL validate API version via optional X-LePetPal-API header with value 1

### Requirement 9: Speech Output

**User Story:** As a user, I want the robot to speak text messages, so that I can provide audio feedback to my pet.

#### Acceptance Criteria

1. THE Backend Service SHALL accept speech requests via POST to `/speak` endpoint with text parameter
2. WHEN a speak request is received, THE Backend Service SHALL invoke TTS engine with provided text
3. THE Backend Service SHALL complete speech output within 1 second of request acceptance for messages under 50 characters
4. THE Backend Service SHALL return HTTP 200 status with confirmation when speech synthesis begins
5. THE Frontend Client SHALL provide Speak preset button that sends predefined encouragement messages

### Requirement 10: Mobile Responsiveness

**User Story:** As a mobile user, I want the web interface to work on my phone, so that I can control the robot from anywhere in my home.

#### Acceptance Criteria

1. THE Frontend Client SHALL render responsive layout that adapts to screen widths from 320 pixels to 1920 pixels
2. THE Frontend Client SHALL display video feed with aspect ratio preservation on mobile devices
3. THE Frontend Client SHALL provide touch-friendly button targets with minimum 44 pixel tap areas
4. THE Frontend Client SHALL maintain command control functionality on mobile browsers supporting ES2020
5. THE Frontend Client SHALL display status indicators and error messages without horizontal scrolling on mobile viewports
