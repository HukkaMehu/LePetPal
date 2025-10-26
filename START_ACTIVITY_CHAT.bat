@echo off
REM Start Activity Chat System
REM Starts activity logger in background and opens frontend

echo.
echo ========================================
echo   Activity Chat System
echo ========================================
echo.
echo This will start:
echo   1. Activity Logger (captures frames)
echo   2. Backend API (if not running)
echo   3. Frontend (if not running)
echo.
echo Make sure you've set OPENAI_API_KEY in .env.logger!
echo.
pause

REM Check if .env.logger exists
if not exist .env.logger (
    echo.
    echo ERROR: .env.logger not found!
    echo Please create .env.logger with your OPENAI_API_KEY
    echo.
    pause
    exit /b 1
)

REM Start activity logger in a new window
echo.
echo Starting Activity Logger...
start "Activity Logger" cmd /k "python stream_activity_logger.py"

REM Wait a moment
timeout /t 2 /nobreak >nul

echo.
echo ========================================
echo   Activity Chat Started!
echo ========================================
echo.
echo The activity logger is running in another window.
echo.
echo NEXT STEPS:
echo   1. Make sure backend is running (port 8000)
echo   2. Make sure frontend is running (port 3000)
echo   3. Open http://localhost:3000
echo   4. Click "AI Chat" in the sidebar
echo   5. Wait 15-30 seconds for first capture
echo   6. Start asking questions!
echo.
echo EXAMPLE QUESTIONS:
echo   - What's my dog doing?
echo   - Has anyone been in the room?
echo   - Is my dog active or calm?
echo   - What happened in the last 5 minutes?
echo.
echo The activity logger will capture frames every 15 seconds.
echo Close the Activity Logger window when you're done.
echo.
pause
