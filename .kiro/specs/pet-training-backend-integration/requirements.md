# Requirements Document

## Introduction

This document specifies the requirements for integrating the Pet Training Web App (React/Vite frontend) with the LePetPal backend (Flask API) **without modifying the frontend code**. The Pet Training Web App is a complete, polished UI that currently uses placeholder data. The integration strategy is to create a minimal adapter layer that connects the existing frontend components to the backend API, preserving the frontend's perfect design and functionality. The backend will be enhanced with CORS support to enable browser-based communication.

## Glossary

- **Pet Training Web App**: The React-based frontend application built with Vite, featuring a sidebar navigation and multiple pages (Live, Gallery, Analytics, Routines, Settings) for pet training management
- **LePetPal Backend**: The Flask-based API server that controls robotic hardware, provides video streaming via MJPEG, and executes pet training commands
- **API Service Layer**: A new TypeScript module that will be added to connect frontend components to backend endpoints without modifying existing component code
- **CORS**: Cross-Origin Resource Sharing - HTTP headers that allow the backend to accept requests from the frontend running on a different port
- **MJPEG Stream**: Motion JPEG video stream format used for real-time camera feed transmission from backend /video_feed endpoint
- **React Context**: A React pattern for sharing state across components without prop drilling, used to provide backend connectivity to all pages
- **Environment Variables**: Configuration values (like backend URL) stored in .env file for the Vite application

## Requirements

### Requirement 1

**User Story:** As a developer, I want to add CORS support to the backend, so that the Pet Training Web App can make API requests from the browser.

#### Acceptance Criteria

1. THE LePetPal Backend SHALL install and configure flask-cors library
2. THE LePetPal Backend SHALL allow requests from http://localhost:5173 origin during development
3. THE LePetPal Backend SHALL allow requests from configurable origins via environment variable for production deployment
4. THE LePetPal Backend SHALL include appropriate CORS headers in all API responses
5. THE LePetPal Backend SHALL support preflight OPTIONS requests for POST endpoints

### Requirement 2

**User Story:** As a developer, I want to create an API service layer, so that frontend components can communicate with the backend without code changes.

#### Acceptance Criteria

1. THE Pet Training Web App SHALL include a new services/api.ts module that encapsulates all backend HTTP requests
2. THE API Service SHALL read the backend base URL from environment variable VITE_API_BASE_URL with default value http://localhost:5000
3. THE API Service SHALL provide typed methods for health check, command execution, status polling, treat dispensing, and TTS
4. THE API Service SHALL return Promise-based responses with proper TypeScript types
5. THE API Service SHALL handle network errors and return user-friendly error messages

### Requirement 3

**User Story:** As a developer, I want to create a React Context for backend connectivity, so that all components can access API functionality.

#### Acceptance Criteria

1. THE Pet Training Web App SHALL include a new contexts/BackendContext.tsx module that provides backend state management
2. THE Backend Context SHALL maintain connection status (connected, disconnected, error)
3. THE Backend Context SHALL provide methods for sending commands and polling status
4. THE Backend Context SHALL expose the current command execution state to consuming components
5. THE Backend Context SHALL wrap the App component to make backend functionality available throughout the application

### Requirement 4

**User Story:** As a pet owner, I want to see live video from my pet camera, so that I can monitor my pet in real-time.

#### Acceptance Criteria

1. WHEN the LivePage component mounts, THE Pet Training Web App SHALL replace the placeholder image URL with the backend MJPEG stream URL
2. THE Pet Training Web App SHALL construct the video feed URL as {VITE_API_BASE_URL}/video_feed
3. WHEN the video stream fails to load, THE Pet Training Web App SHALL display the existing error UI without modification
4. THE Pet Training Web App SHALL use the existing img element to display the MJPEG stream
5. THE Pet Training Web App SHALL preserve all existing video player controls and overlay functionality

### Requirement 5

**User Story:** As a pet owner, I want to send training commands by clicking buttons, so that I can interact with my pet remotely.

#### Acceptance Criteria

1. WHEN the user clicks the "Pet" button, THE Pet Training Web App SHALL call the backend /command endpoint with prompt "pick up the ball"
2. WHEN the user clicks the "Treat" button, THE Pet Training Web App SHALL call the backend /command endpoint with prompt "get the treat"
3. WHEN the user clicks the "Fetch" button, THE Pet Training Web App SHALL call the backend /command endpoint with prompt "go home"
4. THE Pet Training Web App SHALL preserve the existing toast notification behavior for command feedback
5. THE Pet Training Web App SHALL use the Backend Context to execute commands without modifying LivePage component structure

### Requirement 6

**User Story:** As a pet owner, I want to see command execution status, so that I know what the robot is doing.

#### Acceptance Criteria

1. WHEN a command is sent successfully, THE Backend Context SHALL begin polling the /status/{request_id} endpoint every 500 milliseconds
2. WHEN the command state changes to "completed", THE Backend Context SHALL stop polling and update the state
3. WHEN the command state changes to "failed", THE Backend Context SHALL stop polling and expose the error message
4. THE Backend Context SHALL track the current phase, confidence, and duration from status responses
5. THE Backend Context SHALL automatically clean up polling intervals when components unmount

### Requirement 7

**User Story:** As a pet owner, I want the Settings page to include backend configuration, so that I can connect to my device.

#### Acceptance Criteria

1. THE Pet Training Web App SHALL add a new "Backend Connection" card to the existing SettingsPage component
2. THE Backend Connection card SHALL include an input field for backend URL with default value from environment
3. THE Backend Connection card SHALL include a "Test Connection" button that calls the /health endpoint
4. THE Backend Connection card SHALL display connection status (connected, disconnected, error) with appropriate styling
5. THE Backend Connection card SHALL match the existing Settings page design patterns and styling

### Requirement 8

**User Story:** As a developer, I want environment-based configuration, so that the app works in development and production.

#### Acceptance Criteria

1. THE Pet Training Web App SHALL include a .env.example file with VITE_API_BASE_URL=http://localhost:5000
2. THE Pet Training Web App SHALL read VITE_API_BASE_URL at build time using Vite's environment variable system
3. THE Pet Training Web App SHALL document the environment variable in the README.md file
4. THE Pet Training Web App SHALL allow runtime URL override through the Settings page
5. THE Pet Training Web App SHALL persist the user-configured backend URL to localStorage
