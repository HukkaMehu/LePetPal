# Quick Fix Reference Card

## What Was Broken

### Before Fixes ❌
```typescript
// Events API - Expected array, got object
const events = await apiClient.getEvents();
// events was {events: [], total: 10} but code expected []

// Analytics API - Missing userId
const metrics = await apiClient.getDailyMetrics({
  startDate: '2024-01-01',
  endDate: '2024-01-07'
});
// Backend returned 422: user_id is required

// Routines API - Backend returns array directly
const routines = await apiClient.getRoutines();
// routines is [] (array directly)
```

### After Fixes ✅
```typescript
// Events API - Correctly handle response object
const response = await apiClient.getEvents();
const events = response.events; // ✅

// Analytics API - Include userId
const metrics = await apiClient.getDailyMetrics({
  startDate: '2024-01-01',
  endDate: '2024-01-07',
  userId: '00000000-0000-0000-0000-000000000000'
}); // ✅

// Routines API - Backend returns array directly
const routines = await apiClient.getRoutines();
// routines is already an array ✅
```

## Key Changes

### 1. Response Structures
```typescript
// OLD (Wrong)
const events = await apiClient.getEvents();
events.forEach(...) // ❌ events is not an array

// NEW (Correct)
const response = await apiClient.getEvents();
response.events.forEach(...) // ✅ response.events is an array
```

### 2. Analytics Parameters
```typescript
// OLD (Wrong)
await apiClient.getDailyMetrics({
  startDate: '2024-01-01',
  endDate: '2024-01-07'
}); // ❌ Missing userId

// NEW (Correct)
await apiClient.getDailyMetrics({
  startDate: '2024-01-01',
  endDate: '2024-01-07',
  userId: '00000000-0000-0000-0000-000000000000'
}); // ✅ Includes userId
```

### 3. Hook Usage (Already Correct)
```typescript
// Hooks handle response structures automatically
const { events, loading, error } = useEvents();
// events is already an array ✅

const { routines, loading, error } = useRoutines();
// routines is already an array ✅

const { data, loading, error } = useAnalytics({ userId: 'xxx' });
// data is already transformed ✅
```

## Files Changed

| File | What Changed |
|------|-------------|
| `types/index.ts` | Added `userId?: string` to `MetricsQueryParams` |
| `services/api.ts` | Updated analytics methods to include userId |
| `hooks/useAnalytics.ts` | Added userId option with default |
| `tests/api.integration.test.ts` | Fixed all response structure checks |
| `tests/workflows.integration.test.ts` | Fixed response structures and added userId |

## Test User ID

For all testing, use this UUID:
```
00000000-0000-0000-0000-000000000000
```

## Quick Test Commands

```bash
# Start backend
cd backend && python -m uvicorn app.main:app --reload --port 8000

# Start frontend
cd "Pet Training Web App" && npm run dev

# Open test page
# Navigate to: http://localhost:5173/test
```

## Expected Results

| Test Suite | Expected | Notes |
|-----------|----------|-------|
| API Integration | 10/10 ✅ | All should pass |
| WebSocket | 7/7 ✅ | All should pass |
| Video Streaming | 6/8 ⚠️ | 2 failures OK (no hardware) |
| User Workflows | 8/8 ✅ | All should pass |
| **Total** | **31/33** | **94% pass rate** |

## Common Errors Fixed

### Error 1: "Events API returned invalid data structure"
**Cause**: Expected array, got object
**Fix**: Use `response.events` instead of `response`

### Error 2: "user_id is required" (422 error)
**Cause**: Analytics endpoints need userId
**Fix**: Added userId parameter to all analytics calls

### Error 3: "apiClient.makeRequest is not a function"
**Cause**: Method doesn't exist
**Fix**: Changed to use `request()` method

### Error 4: "Not Found" for streaks endpoint
**Cause**: Used string 'test-user' instead of UUID
**Fix**: Changed to UUID format

## Backend Endpoints

```
GET  /api/events              → {events: [], total, limit, offset}
GET  /api/routines            → [] (array directly, NOT wrapped)
GET  /api/analytics/daily     → [] (array of metrics)
GET  /api/analytics/streaks   → {sit_streak, recall_streak, ...}
GET  /api/analytics/summary   → {total_sits, trends, ...}
GET  /api/clips               → {clips: [], total, limit, offset}
GET  /api/snapshots           → {snapshots: [], total, limit, offset}
GET  /api/status              → {device_connected, fps, ...}
GET  /api/models              → {available_models, active_models}
```

## Quick Verification

```bash
# Check backend is running
curl http://localhost:8000/api/status

# Check events endpoint
curl http://localhost:8000/api/events?limit=5

# Check analytics endpoint (requires userId)
curl "http://localhost:8000/api/analytics/daily?from_date=2024-01-01&to_date=2024-01-07&user_id=00000000-0000-0000-0000-000000000000"
```

## Status

✅ **ALL FIXES APPLIED**
✅ **READY FOR TESTING**
✅ **94% EXPECTED PASS RATE**

---

For detailed information, see:
- `INTEGRATION_FIXES.md` - Technical details
- `TESTING_QUICK_START.md` - Setup guide
- `INTEGRATION_COMPLETE.md` - Full summary
