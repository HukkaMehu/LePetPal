@echo off
REM Start Celery worker for processing background tasks (clips, events, etc.)

echo Starting Celery worker...
echo.

REM Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

REM Start Celery worker
celery -A app.core.celery_app worker --loglevel=info --pool=solo

pause
