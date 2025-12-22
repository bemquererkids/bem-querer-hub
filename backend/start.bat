@echo off
REM Startup script for Bem-Querer Hub Backend

echo ========================================
echo Bem-Querer Hub - Backend Startup
echo ========================================
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Check if .env exists
if not exist .env (
    echo [WARNING] .env file not found!
    echo Please copy .env.example to .env and configure your credentials.
    echo.
    pause
    exit /b 1
)

echo [INFO] Starting FastAPI server...
echo [INFO] Access the API at: http://localhost:8000
echo [INFO] Access the docs at: http://localhost:8000/docs
echo.

REM Start uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
