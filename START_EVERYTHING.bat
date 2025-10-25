@echo off
echo ========================================
echo Starting Pet Training App with AI
echo ========================================
echo.
echo This will open 3 terminal windows:
echo 1. AI Service (YOLOv8)
echo 2. Backend (FastAPI)
echo 3. Frontend (Next.js)
echo.
echo Make sure you've run setup_ai.bat first!
echo.
pause

echo Starting AI Service...
start cmd /k "cd ai_service && python main.py"
timeout /t 3

echo Starting Backend...
start cmd /k "cd backend && python -m uvicorn app.main:app --reload"
timeout /t 3

echo Starting Frontend...
start cmd /k "cd Pet Training Web App && npm run dev"

echo.
echo ========================================
echo All services starting!
echo ========================================
echo.
echo Wait for:
echo - AI Service: [Vision] YOLOv8 model loaded successfully
echo - Backend: [FrameProcessor] Started
echo - Frontend: Ready on http://localhost:3000
echo.
echo Then test with:
echo   python test_remote_camera_ai.py
echo.
echo Or open browser:
echo   http://localhost:8000/remote-video/stream?url=https://skyla-nonpercussive-odette.ngrok-free.dev/video_feed^&ai=true
echo.
pause
