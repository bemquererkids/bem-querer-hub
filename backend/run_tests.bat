@echo off
REM Run tests for Bem-Querer Hub Backend

echo ========================================
echo Bem-Querer Hub - Running Tests
echo ========================================
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

echo [INFO] Running pytest...
echo.

REM Run pytest
python -m pytest tests/ -v --tb=short

echo.
echo ========================================
echo Tests completed!
echo ========================================
pause
