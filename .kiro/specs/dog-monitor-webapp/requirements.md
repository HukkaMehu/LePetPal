# Requirements Document

## Introduction

A live dog-monitoring web application that provides real-time video streaming with AI-powered overlays, training analytics, and owner tools. The system enables low-latency webcam viewing with intelligent detection, automated logging, and training insights while maintaining clean integration points for future robotic hardware (SO-101) without requiring refactoring.

## Glossary

- **System**: The dog-monitoring web application
- **Owner**: A user who monitors and trains their dog using the application
- **Robot Arm**: The SO-101 robotic hardware that will execute physical training actions (future integration)
- **AI Service**: The backend service that processes video frames for detection and analysis
- **WebRTC Stream**: Real-time video streaming protocol for low-latency viewing
- **Overlay**: Visual elements displayed on top of the video stream (detection boxes, keypoints, heatmaps)
- **Event**: A logged occurrence detected by the system (sit, fetch, bark, etc.)
- **Clip**: A saved video segment with defined start and end timestamps
- **Routine**: A scheduled sequence of training steps
- **Device**: The camera or future robotic hardware connected to the system
- **Coach**: The AI-powered assistant that provides training tips and summaries

## Requirements

### Requirement 1

**User Story:** As an Owner, I want to view a live video stream of my dog with minimal delay, so that I can monitor their behavior in real-time.

#### Acceptance Criteria

1. WHEN the Owner navigates to the live view, THE System SHALL establish a WebRTC connection within 2 seconds
2. IF WebRTC connection fails, THEN THE System SHALL fall back to MJPEG streaming within 1 second
3. WHILE streaming video, THE System SHALL maintain latency below 500 milliseconds for WebRTC
4. THE System SHALL provide playback controls including play, pause, picture-in-picture, and fullscreen
5. THE System SHALL allow the Owner to adjust latency settings via a slider control

### Requirement 2

**User Story:** As an Owner, I want AI-powered overlays on the video stream, so that I can see what the system detects about my dog's behavior.

#### Acceptance Criteria

1. WHEN the AI Service detects a dog in frame, THE System SHALL display a bounding box with confidence percentage
2. WHEN pose detection is active, THE System SHALL render keypoints for nose, shoulders, and spine
3. THE System SHALL generate an attention heatmap showing motion concentration over the previous 10 minutes
4. THE System SHALL allow the Owner to toggle each overlay layer independently
5. WHERE the Owner draws a region, THE System SHALL monitor that zone and generate events when the dog enters it

### Requirement 3

**User Story:** As an Owner, I want the system to automatically detect and classify my dog's actions, so that I can track training progress without manual logging.

#### Acceptance Criteria

1. WHEN the AI Service processes video frames, THE System SHALL classify actions including sit, stand, lie, approach, fetch-return, drinking, and eating
2. THE System SHALL detect objects including ping-pong balls, toys, and bowls with confidence scores
3. WHEN a person enters the frame, THE System SHALL log a person-present event with timestamp
4. WHEN audio is available, THE System SHALL classify sounds as bark, howl, or whine with volume trends
5. THE System SHALL process frames at 30 frames per second on GPU or 10 frames per second on CPU

### Requirement 4

**User Story:** As an Owner, I want automatic bookmarks and clips created during interesting moments, so that I can review key training events later.

#### Acceptance Criteria

1. WHEN the AI Service detects significant motion, THE System SHALL create an auto-bookmark with a descriptive label
2. WHEN the System detects a fetch-return or treat-eaten action, THE System SHALL save a clip of 8 to 12 seconds duration
3. IF the dog leaves the frame for more than 30 seconds, THEN THE System SHALL display a mini-map showing the last known path
4. THE System SHALL store clips with metadata including start timestamp, duration, labels, and preview image
5. THE System SHALL provide a gallery view with share links for saved clips and snapshots

### Requirement 5

**User Story:** As an Owner, I want an AI coach to provide training tips and session summaries, so that I can improve my dog's training outcomes.

#### Acceptance Criteria

1. WHILE the dog performs a trained behavior, THE System SHALL display a tips card suggesting reinforcement opportunities
2. WHEN a training session ends, THE System SHALL generate a summary including wins, setbacks, and suggested next routines
3. THE System SHALL identify clip highlights from the session for Owner review
4. WHERE the Owner asks a question via coach chat, THE System SHALL provide natural-language answers with timestamp references
5. THE System SHALL analyze daily events to generate training insights and correlations

### Requirement 6

**User Story:** As an Owner, I want to capture snapshots and create clips manually, so that I can save specific moments during monitoring.

#### Acceptance Criteria

1. WHEN the Owner presses the 's' key, THE System SHALL capture a snapshot with timestamp and save to storage
2. WHEN the Owner presses the 'c' key, THE System SHALL create a clip using the current timeline selection
3. WHEN the Owner presses the 'b' key, THE System SHALL create a bookmark at the current video timestamp
4. THE System SHALL provide a timeline with emoji markers representing different event types
5. THE System SHALL support keyboard shortcuts for fullscreen toggle using the 'f' key

### Requirement 7

**User Story:** As an Owner, I want to view training analytics and progress charts, so that I can understand patterns and measure improvement over time.

#### Acceptance Criteria

1. THE System SHALL display time-in-frame versus off-frame metrics on the live dashboard
2. THE System SHALL show sit, stand, and lie counts with hourly bucket aggregation
3. THE System SHALL calculate and display fetch attempts versus successful returns
4. THE System SHALL track bark frequency over time with visual trend lines
5. THE System SHALL provide 7-day trend analysis including best training hours and reinforcement ratios

### Requirement 8

**User Story:** As an Owner, I want to create and schedule training routines, so that I can maintain consistent training sessions.

#### Acceptance Criteria

1. THE System SHALL allow the Owner to create routines by dragging steps including pet, treat, play, and sit drill
2. WHEN the Owner saves a routine, THE System SHALL validate the cron schedule format
3. THE System SHALL store routine steps in a structured format for future execution
4. WHEN a scheduled routine time arrives, THE System SHALL send a notification to the Owner
5. THE System SHALL display enabled and disabled routines with their next execution time

### Requirement 9

**User Story:** As an Owner, I want training streaks and achievement badges, so that I stay motivated to maintain consistent training.

#### Acceptance Criteria

1. WHEN the Owner completes 7 consecutive days of sit training, THE System SHALL award a 7-day sit streak badge
2. WHEN the Owner achieves 5 perfect recall days, THE System SHALL award a recall achievement badge
3. THE System SHALL display current streak counts on the analytics page
4. THE System SHALL track daily training metrics including sit count, fetch count, and treats dispensed
5. THE System SHALL calculate calm minutes based on low-motion periods in frame

### Requirement 10

**User Story:** As an Owner, I want robot command placeholders in the interface, so that I can understand future capabilities without breaking current functionality.

#### Acceptance Criteria

1. THE System SHALL display action buttons for pet, treat, and fetch commands with "not connected" status
2. THE System SHALL show a device status pill indicating "offline" when no robot is connected
3. THE System SHALL display a telemetry strip with mock FPS and temperature values
4. WHERE a policy selector dropdown exists, THE System SHALL disable it until a device appears
5. WHEN the Owner clicks a disabled robot command, THE System SHALL display a tooltip explaining future functionality

### Requirement 11

**User Story:** As an Owner, I want AI-detected behaviors automatically logged and visualized in training charts, so that I can track my dog's progress without manual data entry.

#### Acceptance Criteria

1. WHEN the AI Service detects a sit, stand, or lie action, THE System SHALL increment the corresponding daily counter
2. WHEN the AI Service detects a fetch-return sequence, THE System SHALL log both the attempt and success status
3. THE System SHALL aggregate detected behaviors into hourly buckets for time-series visualization
4. THE System SHALL calculate training metrics including calm minutes based on detected low-activity periods
5. THE System SHALL update analytics charts in real-time as behaviors are detected during live monitoring

### Requirement 12

**User Story:** As an Owner, I want the application to support runtime model switching, so that I can optimize AI performance for my hardware.

#### Acceptance Criteria

1. THE System SHALL expose an API endpoint listing available detector and action recognition models
2. WHEN the Owner requests a model switch, THE System SHALL hot-swap the model without restarting services
3. THE System SHALL validate model compatibility before switching
4. THE System SHALL maintain detection continuity during model transitions with less than 2 seconds of interruption
5. THE System SHALL display current active models in the settings interface
