@echo off

REM Start infrastructure services
echo Starting infrastructure services...
docker-compose up -d

REM Wait for services to be ready
echo Waiting for services to be ready...
timeout /t 10 /nobreak > nul

echo.
echo Infrastructure services started!
echo.
echo Starting Backend API...
start "Backend API" cmd /k "cd /d backend && call venv\Scripts\activate.bat && uvicorn app.main:app --reload"

echo Starting AI Service...
start "AI Service" cmd /k "cd /d ai_service && call venv\Scripts\activate.bat && uvicorn main:app --reload --port 8001"

echo Starting Frontend...
start "Frontend" cmd /k cd /d "Pet Training Web App" ^&^& npm run dev

echo.
echo All services starting...
echo.
echo Services:
echo - Frontend: http://localhost:3000 (or http://localhost:3001 if 3000 is in use)
echo - Backend API: http://localhost:8000/api
echo - AI Service: http://localhost:8001
echo - API Docs: http://localhost:8000/docs
echo - MinIO Console: http://localhost:9001
echo - WebSocket: ws://localhost:8000/ws/ui
echo.
echo Press any key to stop all services...
pause > nul
