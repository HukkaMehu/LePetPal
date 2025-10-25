# Implementation Plan

- [x] 1. Set up project infrastructure and configuration





  - Create environment configuration files (.env, .env.example)
  - Create config module to read environment variables
  - Set up TypeScript type definitions directory structure
  - Install additional dependencies (axios for HTTP, if needed)
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_

- [x] 2. Create core service layer





- [x] 2.1 Implement API client service


  - Create APIClient class with methods for all backend endpoints
  - Implement error handling and retry logic
  - Add request/response interceptors for logging
  - _Requirements: 1.1, 1.2, 10.1, 10.2_


- [x] 2.2 Implement WebSocket service

  - Create WebSocketService class with connection management
  - Implement event subscription/unsubscription system
  - Add automatic reconnection logic with exponential backoff
  - Handle connection state changes and errors
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_


- [x] 2.3 Create data adapter functions

  - Write adapter functions to transform backend events to frontend format
  - Write adapter functions for analytics data transformation
  - Write adapter functions for routine data transformation
  - Write adapter functions for media (clips/snapshots) transformation
  - Write adapter functions for system status transformation
  - _Requirements: 1.4, 1.5_

- [x] 3. Create TypeScript type definitions






- [x] 3.1 Define frontend data types

  - Create Event, MediaItem, AnalyticsData types
  - Create Routine, RoutineStep types
  - Create SystemStatus, TelemetryData types
  - _Requirements: 1.1, 1.2, 1.3, 1.4_

- [x] 3.2 Define backend API response types


  - Create BackendEvent, BackendRoutine types
  - Create BackendDailyMetrics, BackendStreaksResponse types
  - Create BackendClip, BackendSnapshot types
  - Create BackendSystemStatus types
  - _Requirements: 1.1, 1.2, 1.3, 1.4_

- [x] 4. Create custom React hooks for data management





- [x] 4.1 Implement useEvents hook


  - Fetch events from backend API
  - Subscribe to WebSocket for real-time event updates
  - Handle loading and error states
  - _Requirements: 1.1, 1.2, 2.1, 2.2, 7.1, 7.2, 7.3, 7.4_


- [x] 4.2 Implement useAnalytics hook

  - Fetch daily metrics, streaks, and summary data
  - Transform data using adapters
  - Handle loading and error states
  - _Requirements: 6.1, 6.2, 6.3, 6.4_

- [x] 4.3 Implement useRoutines hook


  - Fetch routines list from backend
  - Implement CRUD operations (create, update, delete)
  - Implement trigger routine functionality
  - Subscribe to WebSocket for routine notifications
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [x] 4.4 Implement useSystemStatus hook


  - Fetch system status from backend
  - Subscribe to WebSocket for telemetry updates
  - Update status in real-time
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [x] 4.5 Implement useMedia hook


  - Fetch clips and snapshots from backend
  - Implement pagination
  - Handle loading and error states
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_


- [x] 4.6 Implement useCoach hook

  - Send messages to AI service coach endpoint
  - Handle streaming responses
  - Maintain chat history
  - Handle errors when AI service is unavailable
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

- [x] 5. Update LivePage component






- [x] 5.1 Integrate real video streaming

  - Replace mock video with backend video stream URL
  - Support both MJPEG and WebRTC streaming
  - Display connection status and video metrics (FPS, latency)
  - _Requirements: 3.1, 3.2, 3.3, 3.4_


- [x] 5.2 Implement action buttons functionality

  - Connect Pet, Treat, Fetch buttons to robot control API
  - Display success/error feedback using toast notifications
  - Handle API errors gracefully
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_


- [x] 5.3 Implement snapshot functionality

  - Capture current video frame
  - Send snapshot to backend API
  - Display success notification
  - _Requirements: 3.1, 3.2, 3.3_

- [x] 5.4 Implement recording functionality


  - Start/stop clip recording via backend API
  - Display recording status indicator
  - Handle recording errors
  - _Requirements: 3.1, 3.2, 3.3_

- [x] 6. Update Timeline/EventFeed component





- [x] 6.1 Replace mock data with real events


  - Use useEvents hook to fetch events
  - Display events in chronological order
  - Transform backend event types to frontend format
  - _Requirements: 7.1, 7.2, 7.3_

- [x] 6.2 Implement real-time event updates


  - Subscribe to WebSocket event stream
  - Add new events to timeline as they arrive
  - Update UI smoothly without flickering
  - _Requirements: 7.4, 7.5_


- [x] 6.3 Implement event filtering and pagination

  - Add date range filtering
  - Add event type filtering
  - Implement infinite scroll or pagination
  - _Requirements: 7.1, 7.2, 7.5_

- [x] 7. Update AnalyticsPage component





- [x] 7.1 Replace mock analytics with real data


  - Use useAnalytics hook to fetch data
  - Transform backend analytics to chart format
  - Display daily metrics, streaks, and badges
  - _Requirements: 6.1, 6.2, 6.3_

- [x] 7.2 Update all charts with real data


  - Update Activity Level chart
  - Update Time in Frame chart
  - Update Fetch Success Rate chart
  - Update Bark Frequency chart
  - Update Skill Progress bars
  - _Requirements: 6.1, 6.2, 6.3, 6.4_

- [x] 7.3 Implement date range selector


  - Add controls to select date range (7 days, 30 days, custom)
  - Refetch analytics data when range changes
  - _Requirements: 6.1, 6.4_

- [x] 8. Update RoutinesPage component






- [x] 8.1 Replace mock routines with real data

  - Use useRoutines hook to fetch routines
  - Display routines list with schedule and status
  - Transform backend routine format to frontend format
  - _Requirements: 5.1, 5.2_

- [x] 8.2 Implement routine creation

  - Create form for new routine
  - Validate routine data (name, cron, steps)
  - Send create request to backend
  - Update UI with new routine
  - _Requirements: 5.1, 5.2_


- [ ] 8.3 Implement routine editing
  - Create edit form for existing routine
  - Populate form with current routine data
  - Send update request to backend
  - Update UI with modified routine
  - _Requirements: 5.1, 5.2_


- [ ] 8.4 Implement routine deletion
  - Add delete confirmation dialog
  - Send delete request to backend
  - Remove routine from UI

  - _Requirements: 5.1, 5.2_

- [ ] 8.5 Implement manual routine trigger
  - Add trigger button for each routine
  - Send trigger request to backend

  - Display success/error notification
  - _Requirements: 5.1, 5.2, 5.5_

- [ ] 8.6 Display routine notifications
  - Subscribe to WebSocket for routine notifications
  - Display toast notification when routine starts/completes
  - _Requirements: 5.3, 5.4, 5.5_
-

- [x] 9. Update GalleryPage component



- [x] 9.1 Replace mock media with real data


  - Use useMedia hook to fetch clips and snapshots
  - Display media items in grid layout
  - Show thumbnails with metadata (timestamp, tags)
  - _Requirements: 3.1, 3.2, 3.3, 3.5_

- [x] 9.2 Implement media filtering


  - Add filter by type (clips vs snapshots)
  - Add filter by date range
  - Add filter by tags
  - _Requirements: 3.1, 3.2_

- [x] 9.3 Implement media pagination


  - Implement infinite scroll or load more button
  - Fetch additional media as user scrolls
  - _Requirements: 3.5_

- [x] 9.4 Implement media preview


  - Open modal/dialog to view full-size media
  - Display media metadata and events
  - Add download button
  - _Requirements: 3.1, 3.2, 3.3_

- [ ] 10. Update CoachTips component
- [ ] 10.1 Replace mock coach with AI service
  - Use useCoach hook to send messages
  - Display AI responses in chat interface
  - Handle streaming responses for real-time chat
  - _Requirements: 4.1, 4.2, 4.3_
-

- [x] 10.2 Implement chat history




  - Store chat messages in component state
  - Display conversation history
  - Clear history on user request
  - _Requirements: 4.4_

- [ ] 10.3 Handle AI service errors
  - Display error message when AI service is unavailable
  - Provide retry option
  - Show loading indicator while waiting for response
  - _Requirements: 4.5_

- [x] 11. Update SettingsPage component







- [x] 11.1 Implement model selection

  - Fetch available models from backend
  - Display current active models
  - Allow user to switch models
  - Display success/error feedback
  - _Requirements: 8.1, 8.2, 8.3, 8.4_



- [x] 11.2 Implement device status display

  - Display device connection status
  - Show device information (if available)
  - _Requirements: 8.1, 8.2_




- [ ] 11.3 Implement video streaming settings
  - Allow user to select streaming type (MJPEG vs WebRTC)
  - Display current video metrics (FPS, latency)
  - _Requirements: 3.1, 3.2, 3.4_

- [x] 12. Add global error handling and UI polish





- [x] 12.1 Create ErrorBoundary component


  - Catch React errors
  - Display fallback UI
  - Log errors to console
  - _Requirements: 10.5_

- [x] 12.2 Create ConnectionStatusBanner component


  - Monitor backend connection status
  - Display banner when connection is lost
  - Show reconnection attempts
  - _Requirements: 2.5, 10.4_

- [x] 12.3 Add loading states to all components


  - Display skeleton loaders while fetching data
  - Show spinners for async operations
  - Disable buttons during API calls
  - _Requirements: 10.1, 10.2, 10.3_

- [x] 12.4 Add error messages and user feedback


  - Display toast notifications for errors
  - Show inline error messages in forms
  - Provide clear error descriptions
  - _Requirements: 10.1, 10.2, 10.3, 10.4_
-

- [x] 13. Integration and testing




- [x] 13.1 Test all API integrations


  - Verify all API endpoints are called correctly
  - Test error handling for failed requests
  - Test retry logic
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_



- [x] 13.2 Test WebSocket functionality

  - Verify WebSocket connection establishes correctly
  - Test real-time event updates
  - Test reconnection after disconnect
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_




- [ ] 13.3 Test video streaming
  - Verify MJPEG stream displays correctly
  - Test WebRTC streaming (if implemented)
  - Test video metrics display
  - _Requirements: 3.1, 3.2, 3.3, 3.4_


- [x] 13.4 Test all user workflows

  - Test viewing live stream and taking snapshots
  - Test creating and managing routines
  - Test viewing analytics and charts
  - Test browsing gallery and viewing media
  - Test chatting with AI coach
  - Test changing settings
  - _Requirements: All requirements_

- [x] 14. Build and deployment preparation





- [x] 14.1 Create production build


  - Run Vite build command
  - Verify build output
  - Test production build locally
  - _Requirements: 9.1, 9.2, 9.3_

- [x] 14.2 Create deployment documentation


  - Document environment variables needed
  - Document build and deployment steps
  - Document backend configuration requirements
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_

- [x] 14.3 Configure production environment


  - Set up production environment variables
  - Configure CORS on backend for production domain
  - Test production deployment
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_
