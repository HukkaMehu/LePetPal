# Requirements Document

## Introduction

This document outlines the requirements for migrating from the existing Next.js frontend to the Pet Training Web App frontend (Vite + React), while preserving all backend functionality and maintaining the beautiful UI design of the Pet Training Web App without any layout changes.

## Glossary

- **Pet Training Web App**: The Vite + React frontend application with the desired UI/UX design
- **Legacy Frontend**: The existing Next.js frontend application to be replaced
- **Backend System**: The FastAPI backend with database, WebSocket support, and API endpoints
- **AI Service**: The separate AI service providing coach chat and vision capabilities
- **Integration Layer**: The code that connects the Pet Training Web App to the Backend System and AI Service

## Requirements

### Requirement 1

**User Story:** As a developer, I want to integrate the Pet Training Web App with the existing backend APIs, so that all functionality works without changing the UI layout

#### Acceptance Criteria

1. WHEN the Pet Training Web App starts, THE Integration Layer SHALL establish connection to the Backend System API endpoints
2. THE Integration Layer SHALL replace all mock data calls in the Pet Training Web App with real API calls to the Backend System
3. THE Integration Layer SHALL maintain the exact component structure and styling of the Pet Training Web App
4. THE Integration Layer SHALL handle API response data transformation to match the Pet Training Web App's expected data formats
5. WHERE the Backend System returns different data structures, THE Integration Layer SHALL create adapter functions to transform the data

### Requirement 2

**User Story:** As a user, I want real-time updates through WebSocket connections, so that I can see live events and notifications

#### Acceptance Criteria

1. WHEN the Pet Training Web App loads, THE Integration Layer SHALL establish WebSocket connection to the Backend System
2. WHEN a WebSocket message is received, THE Integration Layer SHALL update the appropriate React components with new data
3. THE Integration Layer SHALL handle WebSocket reconnection when connection is lost
4. THE Integration Layer SHALL subscribe to event streams for timeline updates, routine notifications, and robot status changes
5. IF the WebSocket connection fails, THEN THE Integration Layer SHALL display connection status to the user

### Requirement 3

**User Story:** As a user, I want to view live video streams and recorded media, so that I can monitor my pet's training

#### Acceptance Criteria

1. THE VideoPlayer component SHALL connect to the Backend System video streaming endpoints
2. THE GalleryPage component SHALL fetch and display clips and snapshots from the Backend System
3. WHEN a user requests a video clip, THE Integration Layer SHALL retrieve the media from the Backend System storage
4. THE Integration Layer SHALL handle video format compatibility between the Backend System and the VideoPlayer component
5. THE Integration Layer SHALL implement lazy loading for gallery media to optimize performance

### Requirement 4

**User Story:** As a user, I want to interact with the AI coach, so that I can get training advice and tips

#### Acceptance Criteria

1. THE CoachTips component SHALL connect to the AI Service coach API endpoints
2. WHEN a user sends a message, THE Integration Layer SHALL transmit the message to the AI Service and display the response
3. THE Integration Layer SHALL handle streaming responses from the AI Service for real-time chat experience
4. THE Integration Layer SHALL maintain chat history within the user session
5. IF the AI Service is unavailable, THEN THE Integration Layer SHALL display an appropriate error message

### Requirement 5

**User Story:** As a user, I want to manage training routines, so that I can schedule and track my pet's training activities

#### Acceptance Criteria

1. THE RoutinesPage component SHALL fetch routine data from the Backend System routines API
2. WHEN a user creates or modifies a routine, THE Integration Layer SHALL send the changes to the Backend System
3. THE Integration Layer SHALL receive routine notifications through WebSocket connections
4. THE Integration Layer SHALL display routine execution status and history from the Backend System
5. THE Integration Layer SHALL handle routine scheduling and trigger notifications

### Requirement 6

**User Story:** As a user, I want to view analytics and progress tracking, so that I can monitor my pet's training improvements

#### Acceptance Criteria

1. THE AnalyticsPage component SHALL fetch analytics data from the Backend System analytics API
2. THE Integration Layer SHALL transform analytics data to match the chart format expected by the AnalyticsPage component
3. THE Integration Layer SHALL fetch streaks, badges, and progress metrics from the Backend System
4. WHEN analytics data updates, THE Integration Layer SHALL refresh the displayed metrics
5. THE Integration Layer SHALL handle date range filtering for analytics queries

### Requirement 7

**User Story:** As a user, I want to view the event timeline, so that I can see a chronological history of training events

#### Acceptance Criteria

1. THE Timeline component SHALL fetch event data from the Backend System events API
2. THE Integration Layer SHALL receive real-time event updates through WebSocket connections
3. THE Integration Layer SHALL transform event data to match the Timeline component's expected format
4. WHEN a new event occurs, THE Integration Layer SHALL update the Timeline component in real-time
5. THE Integration Layer SHALL implement pagination or infinite scroll for historical events

### Requirement 8

**User Story:** As a user, I want to control robot actions and view device status, so that I can interact with connected hardware

#### Acceptance Criteria

1. THE ActionPanel component SHALL connect to the Backend System robot control API
2. WHEN a user triggers a robot action, THE Integration Layer SHALL send the command to the Backend System
3. THE Integration Layer SHALL display real-time device status from the Backend System
4. THE Integration Layer SHALL handle policy selection and model configuration through the Backend System
5. IF a robot command fails, THEN THE Integration Layer SHALL display an error message to the user

### Requirement 9

**User Story:** As a developer, I want to configure environment variables and API endpoints, so that the application can connect to different environments

#### Acceptance Criteria

1. THE Integration Layer SHALL read API endpoint URLs from environment configuration files
2. THE Integration Layer SHALL support configuration for Backend System URL, AI Service URL, and WebSocket URL
3. THE Integration Layer SHALL provide default values for development environment
4. THE Integration Layer SHALL validate required environment variables on application startup
5. WHERE environment variables are missing, THE Integration Layer SHALL display clear error messages

### Requirement 10

**User Story:** As a user, I want the application to handle errors gracefully, so that I have a smooth experience even when issues occur

#### Acceptance Criteria

1. WHEN an API call fails, THE Integration Layer SHALL display user-friendly error messages
2. THE Integration Layer SHALL implement retry logic for failed network requests
3. THE Integration Layer SHALL log errors for debugging purposes
4. IF the Backend System is unavailable, THEN THE Integration Layer SHALL display a connection status banner
5. THE Integration Layer SHALL prevent UI crashes by implementing error boundaries in React components
