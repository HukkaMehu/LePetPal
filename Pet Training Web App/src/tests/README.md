# Integration Tests

This directory contains comprehensive integration tests for the Pet Training Web App frontend migration.

## Test Suites

### 1. API Integration Tests (`api.integration.test.ts`)
Tests all REST API endpoints to verify:
- Events API (GET)
- Routines API (GET, CREATE, UPDATE, DELETE)
- Analytics API (Daily Metrics, Streaks, Summary)
- Media API (Clips, Snapshots)
- System Status API
- Models API
- Error handling for 404 and network failures
- Retry logic configuration

**Requirements Covered:** 1.1, 1.2, 1.3, 1.4, 1.5

### 2. WebSocket Integration Tests (`websocket.integration.test.ts`)
Tests WebSocket functionality to verify:
- Connection establishment
- Event subscription/unsubscription
- Multiple simultaneous subscriptions
- Connection state management
- Automatic reconnection after disconnect
- Error handling for invalid URLs
- Message format validation

**Requirements Covered:** 2.1, 2.2, 2.3, 2.4, 2.5

### 3. Video Streaming Tests (`video.integration.test.ts`)
Tests video streaming functionality to verify:
- MJPEG stream URL accessibility
- Video stream content type
- Video element creation and loading
- Video metrics endpoint
- Stream performance monitoring
- WebRTC browser support
- Stream error handling
- Multiple stream instances

**Requirements Covered:** 3.1, 3.2, 3.3, 3.4

### 4. User Workflows Tests (`workflows.integration.test.ts`)
Tests complete end-to-end user workflows:
- View live stream and take snapshots
- Create, update, and delete routines
- View analytics and charts
- Browse gallery and view media with pagination
- Chat with AI coach
- Change settings and switch models
- Real-time updates via WebSocket
- Error recovery scenarios

**Requirements Covered:** All requirements

## Running Tests

### Option 1: Via UI (Recommended)
1. Start the development server: `npm run dev`
2. Navigate to the "Tests" page in the sidebar
3. Click "Run All Tests" or run individual test suites
4. View results in real-time

### Option 2: Via Browser Console
1. Start the development server: `npm run dev`
2. Open browser developer console
3. Run: `runAllTests()`
4. View results in console

### Option 3: Programmatically
```typescript
import runAllTests from './tests/runAllTests';

// Run all tests
await runAllTests();

// Or run individual test suites
import runAPIIntegrationTests from './tests/api.integration.test';
await runAPIIntegrationTests();
```

## Prerequisites

Before running tests, ensure:

1. **Backend Server** is running on `http://localhost:8000` (or configured URL)
2. **AI Service** is running on `http://localhost:8001` (or configured URL)
3. **WebSocket Server** is accessible at `ws://localhost:8000/ws` (or configured URL)
4. **Database** is populated with test data (optional, but recommended)

## Test Configuration

Tests use environment variables from `.env`:
- `VITE_API_BASE_URL` - Backend API URL
- `VITE_AI_SERVICE_URL` - AI Service URL
- `VITE_WS_URL` - WebSocket URL

## Test Results

Each test suite provides:
- ✅ Number of passed tests
- ❌ Number of failed tests
- Detailed error messages for failures
- Execution time

## Notes

- Tests are designed to be **non-destructive** - they clean up after themselves
- Some tests may show warnings if backend services are not available
- Tests use real API calls (not mocked) to verify actual integration
- WebSocket tests may take longer due to connection timeouts
- Video streaming tests require an active video stream

## Troubleshooting

### Tests Fail with Connection Errors
- Verify backend server is running
- Check environment variables in `.env`
- Ensure CORS is configured correctly on backend

### WebSocket Tests Timeout
- Verify WebSocket server is running
- Check firewall settings
- Ensure WebSocket URL is correct

### Video Streaming Tests Fail
- Verify video stream endpoint is accessible
- Check if camera/video source is connected
- Ensure MJPEG stream is enabled on backend

### AI Coach Tests Fail
- Verify AI service is running
- Check AI service URL configuration
- Ensure AI models are loaded

## Future Enhancements

- Add automated test runner with CI/CD integration
- Add performance benchmarking
- Add visual regression testing
- Add accessibility testing
- Add load testing for WebSocket connections
