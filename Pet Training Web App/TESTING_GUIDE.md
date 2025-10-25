# Testing Guide

## Overview

This guide explains how to run the comprehensive integration tests for the Pet Training Web App frontend migration.

## Quick Start

### Option 1: Using the Test UI (Recommended)

1. Start the development server:
   ```bash
   npm run dev
   ```

2. Open the application in your browser (usually `http://localhost:5173`)

3. Click on "Tests" in the sidebar navigation

4. Click "Run All Tests" to execute the complete test suite

5. View real-time results and detailed logs

### Option 2: Browser Console

1. Start the development server:
   ```bash
   npm run dev
   ```

2. Open browser developer tools (F12)

3. In the console, run:
   ```javascript
   runAllTests()
   ```

4. View results in the console output

## Test Suites

### 1. API Integration Tests
- **File**: `src/tests/api.integration.test.ts`
- **Coverage**: All REST API endpoints
- **Tests**: 10 tests covering events, routines, analytics, media, status, models, and error handling

### 2. WebSocket Integration Tests
- **File**: `src/tests/websocket.integration.test.ts`
- **Coverage**: Real-time WebSocket functionality
- **Tests**: 7 tests covering connection, subscriptions, reconnection, and error handling

### 3. Video Streaming Tests
- **File**: `src/tests/video.integration.test.ts`
- **Coverage**: Video streaming functionality
- **Tests**: 8 tests covering MJPEG streams, metrics, performance, and WebRTC support

### 4. User Workflow Tests
- **File**: `src/tests/workflows.integration.test.ts`
- **Coverage**: End-to-end user scenarios
- **Tests**: 8 complete workflows covering all major features

## Prerequisites

Before running tests, ensure:

1. **Backend Server** is running:
   ```bash
   cd backend
   # Start backend server
   ```

2. **AI Service** is running (optional):
   ```bash
   cd ai_service
   # Start AI service
   ```

3. **Environment Variables** are configured in `.env`:
   ```env
   VITE_API_BASE_URL=http://localhost:8000
   VITE_AI_SERVICE_URL=http://localhost:8001
   VITE_WS_URL=ws://localhost:8000/ws
   ```

## Test Results

Each test suite provides:
- ✅ Number of passed tests
- ❌ Number of failed tests
- Detailed error messages
- Execution time

## Expected Behavior

### When Backend is Running
- All API tests should pass
- WebSocket tests should pass
- Video streaming tests should pass
- User workflow tests should pass

### When Backend is Offline
- Tests will show connection errors
- Some tests may be marked as warnings (⚠️)
- This is expected behavior

## Troubleshooting

### Connection Errors
**Problem**: Tests fail with "Connection refused" or "Network error"

**Solution**:
1. Verify backend server is running on port 8000
2. Check `.env` file has correct URLs
3. Ensure no firewall is blocking connections

### WebSocket Timeout
**Problem**: WebSocket tests timeout

**Solution**:
1. Verify WebSocket server is running
2. Check WebSocket URL in `.env`
3. Try increasing timeout in test files

### Video Stream Errors
**Problem**: Video streaming tests fail

**Solution**:
1. Verify video stream endpoint is accessible
2. Check if camera/video source is connected
3. Ensure MJPEG stream is enabled on backend

### AI Service Errors
**Problem**: Coach chat tests fail

**Solution**:
1. AI service is optional - tests will show warnings if unavailable
2. Start AI service if you want to test coach functionality
3. Check AI service URL in `.env`

## Test Coverage

The test suite covers all requirements from the frontend migration spec:

- ✅ Requirement 1.1-1.5: API Integration
- ✅ Requirement 2.1-2.5: WebSocket Functionality
- ✅ Requirement 3.1-3.4: Video Streaming
- ✅ Requirement 4.1-4.5: AI Coach Integration
- ✅ Requirement 5.1-5.5: Routines Management
- ✅ Requirement 6.1-6.4: Analytics
- ✅ Requirement 7.1-7.5: Event Timeline
- ✅ Requirement 8.1-8.5: Robot Control
- ✅ Requirement 9.1-9.5: Configuration
- ✅ Requirement 10.1-10.5: Error Handling

## Adding New Tests

To add new tests:

1. Create a new test file in `src/tests/`
2. Follow the existing test structure
3. Export a test function that returns `Promise<void>`
4. Add the test to `runAllTests.ts`
5. Update the TestPage component to include the new test

## CI/CD Integration

For automated testing in CI/CD pipelines:

1. Install dependencies: `npm install`
2. Start backend services
3. Run tests programmatically:
   ```javascript
   import runAllTests from './src/tests/runAllTests';
   await runAllTests();
   ```

## Notes

- Tests use real API calls (not mocked) for accurate integration testing
- Tests are designed to be non-destructive and clean up after themselves
- Some tests may take longer due to network latency and timeouts
- Tests can be run individually or as a complete suite

## Support

For issues or questions about testing:
1. Check the test README: `src/tests/README.md`
2. Review test output for specific error messages
3. Verify all prerequisites are met
4. Check backend logs for API errors
