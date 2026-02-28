@echo off
echo =========================================
echo ====== News Push Backend API Server ======
echo =========================================
echo.

if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment 'venv' not found.
    echo Please create it using: python -m venv venv and install requirements.
    pause
    exit /b 1
)

echo Activate virtual environment...
call venv\Scripts\activate.bat

echo.
echo Starting FastAPI with Uvicorn on http://127.0.0.1:8010 ...
echo [Tip] Press Ctrl+C to stop the server.
echo.

python -m uvicorn src.api.server:app --reload --host 127.0.0.1 --port 8010

pause
