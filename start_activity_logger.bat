@echo off
REM Stream Activity Logger Startup Script
REM Edit .env.logger file to configure settings

echo.
echo ========================================
echo   Stream Activity Logger
echo ========================================
echo.
echo Configuration loaded from .env.logger
echo.
echo Starting logger...
echo Press Ctrl+C to stop
echo.

python stream_activity_logger.py

pause
