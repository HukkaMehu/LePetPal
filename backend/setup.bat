@echo off
REM LePetPal Backend Setup Script for Windows
REM This script automates the initial setup process

echo ==========================================
echo LePetPal Backend Setup
echo ==========================================
echo.

REM Check Python version
echo Checking Python version...
python --version
echo.

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo.
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo.
echo Installing dependencies...
pip install -r requirements.txt

REM Create .env from example
if not exist .env (
    echo.
    echo Creating .env file from .env.example...
    copy .env.example .env
    echo [OK] .env file created
    echo     Please edit .env to customize your configuration
) else (
    echo.
    echo [OK] .env file already exists
)

REM Create calibration.json from example
if not exist calibration.json (
    echo.
    echo Creating calibration.json from calibration.json.example...
    copy calibration.json.example calibration.json
    echo [OK] calibration.json created
    echo     Please edit calibration.json to match your hardware setup
) else (
    echo.
    echo [OK] calibration.json already exists
)

echo.
echo ==========================================
echo Setup Complete!
echo ==========================================
echo.
echo Next steps:
echo 1. Edit .env to configure your deployment
echo 2. Edit calibration.json to match your hardware
echo 3. Run the server: python run_backend.py
echo 4. Test health check: curl http://localhost:5000/health
echo.
echo For development without hardware, ensure USE_MOCK_HARDWARE=true in .env
echo.
pause
