@echo off
echo ========================================
echo Setting up AI Features
echo ========================================
echo.

echo Installing AI service dependencies...
cd ai_service
pip install -r requirements.txt
echo.

echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo The AI service will now use real YOLOv8 detection.
echo YOLOv8 model will download automatically on first run.
echo.
echo To start the services:
echo 1. Terminal 1: cd ai_service ^&^& python main.py
echo 2. Terminal 2: cd backend ^&^& python -m uvicorn app.main:app --reload
echo 3. Terminal 3: cd "Pet Training Web App" ^&^& npm run dev
echo.
pause
