@echo off
REM Quick test for AI frontend integration
REM This opens the test page in your browser

echo.
echo ========================================
echo   AI Frontend Integration Test
echo ========================================
echo.
echo This will open a test page that shows:
echo   1. Live video stream with AI overlay
echo   2. WebSocket connection status
echo   3. Real-time detection log
echo   4. Performance metrics (FPS, detections)
echo.
echo REQUIREMENTS:
echo   - Backend running on port 8000
echo   - AI service running on port 8001
echo.
echo Starting test page...
echo.

REM Open test page in default browser
start "" "test_frontend_ai.html"

echo.
echo Test page opened in your browser!
echo.
echo WHAT TO EXPECT:
echo   - Video stream should load
echo   - WebSocket should auto-connect
echo   - Bounding boxes appear on detected objects
echo   - Detection log shows real-time detections
echo   - FPS counter shows detection rate
echo.
echo TROUBLESHOOTING:
echo   - No video? Check backend is running
echo   - No detections? Check AI service is running
echo   - No WebSocket? Check backend WebSocket endpoint
echo.
echo Press any key to close this window...
pause >nul
