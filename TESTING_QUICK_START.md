# Testing Quick Start Guide

## Prerequisites

### 1. Start Backend Services

```bash
# Terminal 1: Start main backend
cd backend
python -m uvicorn app.main:app --reload --port 8000

# Terminal 2: Start AI service (optional)
cd ai_service
python main.py
```

### 2. Verify Backend is Running

Open browser to:
- Backend API: http://localhost:8000/docs
- AI Service: http://localhost:8001/docs (if running)

### 3. Generate Test Data (Optional)

```bash
cd backend
python scripts/generate_mock_data.py
```

## Running Integration Tests

### Option 1: Run All Tests via Test Page

1. Start the frontend:
   ```bash
   cd "Pet Training Web App"
   npm run dev
   ```

2. Navigate to: http://localhost:5173/test

3. Click "Run All Tests" button

### Option 2: Run Tests Programmatically

```bash
cd "Pet Training Web App"
npm run test:integration
```

## Expected Results

### With Backend Running

**API Integration Tests**: 10/10 passing
- ✅ Events API
- ✅ Routines API (GET)
- ✅ Analytics API (Daily Metrics)
- ✅ Analytics API (Streaks)
- ✅ Media API (Clips)
- ✅ Media API (Snapshots)
- ✅ System Status API
- ✅ Models API (GET)
- ✅ Error Handling (404)
- ✅ Retry Logic

**WebSocket Tests**: 7/7 passing
- ✅ WebSocket Connection
- ✅ Event Subscription
- ✅ Multiple Subscriptions
- ✅ Connection State
- ✅ Reconnection
- ✅ Error Handling
- ✅ Message Format

**Video Streaming Tests**: 6-8/8 passing
- ⚠️ MJPEG Stream (requires video source)
- ⚠️ Stream Performance (requires video source)
- ✅ Video Metrics Endpoint
- ✅ WebRTC Support
- ✅ Stream Error Handling
- ✅ Multiple Stream Instances

**User Workflow Tests**: 8/8 passing
- ✅ Live Stream & Snapshot
- ✅ Create & Manage Routines
- ✅ View Analytics & Charts
- ✅ Browse Gallery & View Media
- ✅ Chat with AI Coach
- ✅ Change Settings
- ✅ Real-time Updates
- ✅ Error Recovery

### Without Backend Running

Most tests will fail with connection errors. This is expected.

## Troubleshooting

### Backend Connection Errors

**Error**: `Failed to fetch` or `Network error`

**Solution**:
1. Verify backend is running: `curl http://localhost:8000/api/status`
2. Check backend logs for errors
3. Ensure no firewall blocking localhost:8000

### Analytics API Errors

**Error**: `user_id is required` or `422 Unprocessable Entity`

**Solution**: Tests now include default test UUID. If still failing:
1. Check backend logs
2. Verify database is initialized
3. Run database migrations: `cd backend && alembic upgrade head`

### Video Stream 404 Errors

**Error**: `Stream returned status 404`

**Solution**: This is expected if:
1. No camera/video source configured
2. Video streaming service not implemented
3. Running in development without hardware

These tests can be skipped or will show warnings.

### WebSocket Connection Errors

**Error**: `WebSocket connection failed`

**Solution**:
1. Verify WebSocket endpoint: `ws://localhost:8000/ws`
2. Check backend WebSocket implementation
3. Ensure no proxy blocking WebSocket connections

## Test Data

### Default Test User ID
```
00000000-0000-0000-0000-000000000000
```

This UUID is used for all test API calls that require a user_id parameter.

### Creating Test Data

To populate the database with test data:

```bash
cd backend
python scripts/generate_mock_data.py --days 30 --events 100
```

This creates:
- 30 days of daily metrics
- 100 random events
- Sample routines
- Sample clips and snapshots

## Integration Test Coverage

### API Endpoints Tested
- ✅ GET /api/events
- ✅ GET /api/routines
- ✅ GET /api/analytics/daily
- ✅ GET /api/analytics/streaks
- ✅ GET /api/analytics/summary
- ✅ GET /api/clips
- ✅ GET /api/snapshots
- ✅ GET /api/status
- ✅ GET /api/models

### WebSocket Events Tested
- ✅ Connection/Disconnection
- ✅ Event subscriptions
- ✅ Message broadcasting
- ✅ Reconnection logic
- ✅ Error handling

### User Workflows Tested
- ✅ Complete user journeys
- ✅ Multi-step interactions
- ✅ Error recovery
- ✅ Real-time updates

## Next Steps

1. **Run tests** to verify all fixes are working
2. **Review failures** and check backend logs
3. **Add more test data** if needed
4. **Implement missing endpoints** if any tests fail
5. **Update documentation** based on test results

## Support

For issues or questions:
1. Check backend logs: `backend/logs/`
2. Check browser console for frontend errors
3. Review `INTEGRATION_FIXES.md` for recent changes
4. Check `INTEGRATION_SUMMARY.md` for architecture overview
