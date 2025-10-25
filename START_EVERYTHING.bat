@echo off
REM Start Everything - Activity Logger + Chat Interface
REM Edit .env.logger file to configure settings

echo.
echo ========================================
echo   Stream Activity Logger Setup
echo ========================================
echo.
echo This will start TWO windows:
echo   1. Activity Logger (captures frames)
echo   2. Chat Interface (ask questions)
echo.
echo Make sure you've edited .env.logger with your API key!
echo.
pause

REM Start activity logger in a new window
start "Activity Logger" cmd /k "python stream_activity_logger.py"

REM Wait for logger to start and capture first frame
echo.
echo Waiting for logger to capture first frame...
echo This may take 15-30 seconds depending on your settings...
echo.
timeout /t 20 /nobreak >nul

REM Start chat interface in current window
echo.
echo ========================================
echo   Chat with Activity Log
echo ========================================
echo.
echo The logger is running in another window.
echo You can now ask questions about the stream!
echo.
echo (If the log is empty, wait a bit longer for captures)
echo.
echo Type your questions, or 'quit' to exit
echo.

python chat_with_activity_log.py

echo.
echo Chat closed. The logger is still running in the other window.
echo Close that window when you're done logging.
pause
