# Implementation Plan

- [x] 1. Add CORS support to backend









  - Install flask-cors package in backend requirements.txt
  - Import and configure CORS in backend/app.py with environment-based origins
  - Add CORS_ORIGINS to backend/.env.example with default value http://localhost:5173
  - Test CORS headers with OPTIONS preflight requests
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [x] 2. Create API service layer for frontend





  - [x] 2.1 Create TypeScript types and interfaces


    - Create Pet Training Web App/src/types/api.ts with ApiConfig, CommandResponse, StatusResponse, HealthResponse interfaces
    - Define error types for network and API errors
    - _Requirements: 2.4, 8.4_
  
  - [x] 2.2 Implement BackendApiService class


    - Create Pet Training Web App/src/services/api.ts with BackendApiService class
    - Implement constructor that reads VITE_API_BASE_URL from import.meta.env
    - Implement health() method for GET /health endpoint
    - Implement sendCommand() method for POST /command endpoint
    - Implement getStatus() method for GET /status/{id} endpoint
    - Implement dispenseTreat() method for POST /dispense_treat endpoint
    - Implement speak() method for POST /speak endpoint
    - Implement getVideoFeedUrl() method that returns constructed URL
    - Add error handling with try-catch and typed error responses
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 8.1, 8.2, 8.3, 8.4, 8.5_

- [x] 3. Create Backend Context for state management





  - [x] 3.1 Implement BackendContext and Provider


    - Create Pet Training Web App/src/contexts/BackendContext.tsx
    - Define BackendState and BackendContextValue interfaces
    - Implement BackendProvider component with useState for connection state
    - Initialize BackendApiService instance in provider
    - Implement useBackend custom hook with context validation
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_
  
  - [x] 3.2 Implement command execution logic

    - Add sendCommand method that calls API service and stores request_id
    - Implement status polling with setInterval (500ms)
    - Add cleanup logic to clear intervals on unmount
    - Update state when command completes or fails
    - _Requirements: 5.1, 5.2, 5.3, 5.5, 6.1, 6.2, 6.3, 6.4, 6.5_
  
  - [x] 3.3 Implement connection management

    - Add testConnection method that calls health endpoint
    - Add updateBackendUrl method that updates API service config
    - Persist backend URL to localStorage on update
    - Load saved URL from localStorage on initialization
    - _Requirements: 8.5_

- [x] 4. Add environment configuration





  - Create Pet Training Web App/.env.example with VITE_API_BASE_URL=http://localhost:5000
  - Update Pet Training Web App/README.md with backend integration setup instructions
  - Document environment variable usage and configuration steps
  - _Requirements: 8.1, 8.2, 8.3, 8.4_

- [x] 5. Integrate BackendContext into application





  - Update Pet Training Web App/src/main.tsx to wrap App with BackendProvider
  - Verify context is accessible throughout component tree
  - _Requirements: 3.5_

- [x] 6. Connect LivePage to backend




  - [x] 6.1 Wire video feed URL


    - Import useBackend hook in Pet Training Web App/src/components/LivePage.tsx
    - Replace hardcoded videoUrl with state.videoFeedUrl from context
    - Add fallback to placeholder image if videoFeedUrl is empty
    - Add onError handler to img element for stream failures
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_
  
  - [x] 6.2 Connect command buttons to backend


    - Update handleAction function to call sendCommand from context
    - Map button actions to backend prompts: Pet→"pick up the ball", Treat→"get the treat", Fetch→"go home"
    - Add error handling with toast notifications for failed commands
    - Preserve existing toast.success behavior for successful commands
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [x] 7. Enhance SettingsPage with backend configuration






  - [x] 7.1 Add Backend Connection card component

    - Import useBackend hook in Pet Training Web App/src/components/SettingsPage.tsx
    - Add new Card component with "Backend Connection" heading matching existing style
    - Add Server icon from lucide-react to match other setting cards
    - Add Input field for backend URL with state management
    - Add "Test Connection" Button that calls testConnection from context
    - Display connection status Badge (connected/disconnected/error) with appropriate variant
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_
  
  - [x] 7.2 Implement connection test and URL persistence


    - Wire Test Connection button to context.testConnection method
    - Update context state based on connection test result
    - Call context.updateBackendUrl when user changes URL
    - Display success/error toast based on connection test result
    - _Requirements: 7.5, 8.5_

- [ ]* 8. Testing and validation
  - [ ]* 8.1 Test backend CORS configuration
    - Start backend server and verify CORS headers in browser DevTools
    - Test OPTIONS preflight requests from frontend origin
    - Verify all endpoints accept requests from http://localhost:5173
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_
  
  - [ ]* 8.2 Test API service methods
    - Test health endpoint returns correct response
    - Test sendCommand with each prompt type
    - Test getStatus polling behavior
    - Test error handling for network failures
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_
  
  - [ ]* 8.3 Test end-to-end command execution
    - Click each button in LivePage and verify command is sent
    - Verify status polling starts and updates correctly
    - Verify toast notifications appear on success/failure
    - Test command execution with backend offline
    - _Requirements: 5.1, 5.2, 5.3, 6.1, 6.2, 6.3, 6.4, 6.5_
  
  - [ ]* 8.4 Test video streaming
    - Verify MJPEG stream loads in LivePage
    - Test fallback behavior when stream fails
    - Test video feed with different backend URLs
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_
  
  - [ ]* 8.5 Test Settings page integration
    - Test backend URL input and validation
    - Test connection test button functionality
    - Verify URL persistence to localStorage
    - Test URL changes reflect in video feed and commands
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 8.5_

- [ ]* 9. Documentation updates
  - Update Pet Training Web App/README.md with backend setup instructions
  - Update backend/README.md with CORS configuration details
  - Add troubleshooting section for common integration issues
  - Document environment variables and their usage
  - _Requirements: 8.1, 8.2, 8.3_
