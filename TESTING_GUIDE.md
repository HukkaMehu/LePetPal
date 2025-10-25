# LePetPal Backend Testing Guide

## Quick Start

### 1. Start the Backend
```bash
cd backend
python run_backend.py
```

Wait for:
```
INFO: Camera 0 opened successfully (1280x720)
INFO: ArmAdapter successfully connected to hardware. is_connected=True
 * Running on http://127.0.0.1:5000
```

---

## Test Scripts

### Quick Test (30 seconds)
Fast sanity check of all features:
```bash
python backend/tools/quick_test.py
```

**Tests:**
- ✅ Health endpoint
- ✅ Video feed streaming
- ✅ Command execution
- ✅ Status polling
- ✅ Dispense treat
- ✅ Text-to-speech

---

### Comprehensive Test Suite (2-3 minutes)
Full feature validation:
```bash
python backend/tools/test_all_features.py
```

**Tests:**
1. Health Check
2. Video Feed
3. Invalid Command Rejection
4. Pick Up Ball Command
5. Busy State Handling
6. Go Home (Interrupt)
7. Dispense Treat
8. Text-to-Speech
9. TTS Validation
10. Get Treat Command

---

### Smoke Test (Simple)
Original basic test:
```bash
python backend/tools/smoke.py
```

---

## Manual Testing

### Test Video Feed
Open in browser:
```
http://localhost:5000/video_feed
```

You should see live camera feed.

---

### Test with cURL

#### Health Check
```bash
curl http://localhost:5000/health
```

#### Send Command
```bash
curl -X POST http://localhost:5000/command \
  -H "Content-Type: application/json" \
  -d '{"prompt": "pick up the ball", "options": {}}'
```

Response:
```json
{"request_id": "uuid-here", "status": "accepted"}
```

#### Check Status
```bash
curl http://localhost:5000/status/YOUR-REQUEST-ID
```

Response:
```json
{
  "state": "executing",
  "phase": "grasp_2",
  "message": "grasp_2",
  "confidence": 0.8
}
```

#### Dispense Treat
```bash
curl -X POST http://localhost:5000/dispense_treat \
  -H "Content-Type: application/json" \
  -d '{"duration_ms": 600}'
```

#### Speak
```bash
curl -X POST http://localhost:5000/speak \
  -H "Content-Type: application/json" \
  -d '{"text": "Good boy!"}'
```

---

## Expected Results

### ✅ Successful Test Output

**Quick Test:**
```
🤖 LePetPal Quick Test

1️⃣  Testing health endpoint...
   ✓ Health: {'api': 1, 'status': 'ok', 'version': 'v0.1'}

2️⃣  Testing video feed...
   ✓ Video streaming (1024 bytes received)

3️⃣  Sending 'pick up the ball' command...
   ✓ Command accepted: bf45aa1d-2d34-4c64-810c-b3e469943ff6

4️⃣  Polling status...
   [1] State: executing    Phase: approach_3
   [2] State: executing    Phase: lift_2
   [3] State: succeeded    Phase: ready_2

   ✓ Final state: succeeded
   ✓ Duration: 6248ms

5️⃣  Testing dispense treat...
   ✓ Dispense: {'status': 'ok'}

6️⃣  Testing TTS...
   ✓ Speak: {'status': 'ok'}

✅ All quick tests passed!
🚀 Backend is ready!
```

**Comprehensive Test:**
```
============================================================
TEST SUMMARY
============================================================
  PASS - Health Check
  PASS - Video Feed
  PASS - Invalid Command Rejection
  PASS - Pick Up Ball Command
  PASS - Busy State Handling
  PASS - Go Home (Interrupt)
  PASS - Dispense Treat
  PASS - Text-to-Speech
  PASS - TTS Validation
  PASS - Get Treat Command

============================================================
ALL TESTS PASSED! (10/10)
✓ Backend is ready for frontend integration!
============================================================
```

---

## Troubleshooting

### Backend Not Starting
```bash
# Check if port 5000 is in use
netstat -ano | findstr :5000

# Kill process if needed
taskkill /PID <PID> /F
```

### Robot Not Moving
1. Check COM port: `lerobot-find-port`
2. Update `.env`: `ARM_PORT=COM7` (or correct port)
3. Verify connection in backend logs:
   ```
   INFO: ArmAdapter successfully connected to hardware. is_connected=True
   ```

### Camera Not Working
Check backend logs for:
```
INFO: Camera 0 opened successfully (1280x720)
```

If you see:
```
WARNING: No camera found. Using synthetic video feed.
```

Then no camera is detected. Video feed will show synthetic frames.

### Tests Timing Out
- Increase timeout in test scripts
- Check if backend is responding: `curl http://localhost:5000/health`
- Restart backend

---

## What Each Test Validates

| Test | Validates |
|------|-----------|
| **Health Check** | Backend is running and responding |
| **Video Feed** | Camera is working and streaming |
| **Invalid Command** | Input validation works |
| **Pick Up Ball** | Full command execution pipeline |
| **Busy State** | Concurrent command handling |
| **Go Home** | Interrupt/preempt functionality |
| **Dispense Treat** | Servo control works |
| **TTS** | Text-to-speech works |
| **TTS Validation** | TTS input validation |
| **Get Treat** | Alternative command works |

---

## Ready for Frontend?

If all tests pass, you can:
1. ✅ Connect Next.js frontend
2. ✅ Integrate with mobile app
3. ✅ Build custom UI
4. ✅ Demo the system

See `FRONTEND_INTEGRATION.md` for Next.js integration guide.
