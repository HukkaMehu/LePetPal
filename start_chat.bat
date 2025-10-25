@echo off
REM Chat with Activity Log Startup Script
REM Edit .env.logger file to configure settings

echo.
echo ========================================
echo   Chat with Activity Log
echo ========================================
echo.
echo Configuration loaded from .env.logger
echo.
echo Type your questions, or 'quit' to exit
echo.

python chat_with_activity_log.py

pause
