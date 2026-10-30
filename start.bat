@echo off
setlocal enabledelayedexpansion

echo =====================================================================
echo           PowerGuard: Electrical Load Monitoring Platform
echo                   Local System Startup Utility
echo =====================================================================
echo.

:: 1. Verify Prerequisites
echo [1/5] Checking environment prerequisites...
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python is not found in PATH. Please install Python 3.10+ and add it to PATH.
    pause
    exit /b 1
)

where node >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Node.js is not found in PATH. Please install Node.js 18+ and add it to PATH.
    pause
    exit /b 1
)

where npm >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] npm is not found in PATH.
    pause
    exit /b 1
)
echo       Python and Node.js detected successfully.

:: 2. Check Backend Dependencies
echo.
echo [2/5] Checking backend dependencies...
python -c "import flask, sqlalchemy, sklearn, pandas, numpy" >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo       Installing missing backend packages from backend\requirements.txt...
    python -m pip install -r backend\requirements.txt
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Failed to install backend dependencies.
        pause
        exit /b 1
    )
) else (
    echo       Backend packages already satisfied.
)

:: 3. Check Frontend Dependencies
echo.
echo [3/5] Checking frontend dependencies...
if not exist "frontend\node_modules\" (
    echo       Installing frontend npm packages...
    cd frontend
    call npm install
    cd ..
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Failed to install frontend npm packages.
        pause
        exit /b 1
    )
) else (
    echo       Frontend dependencies already installed.
)

:: 4. Initialize Database
echo.
echo [4/5] Initializing PowerGuard SQLite database...
python -c "import sys; sys.path.insert(0, 'backend'); from database import init_db; init_db()"
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Database initialization failed.
    pause
    exit /b 1
)
echo       Database verified and schema initialized.

:: 5. Launch Servers
echo.
echo [5/5] Launching PowerGuard Backend and Frontend...
echo.
echo       - Backend starting at:  http://127.0.0.1:5000
echo       - Frontend starting at: http://localhost:5173
echo.

start "PowerGuard Backend API" cmd /k "cd backend && python app.py"
timeout /t 2 /nobreak >nul
start "PowerGuard Frontend UI" cmd /k "cd frontend && npm run dev"

echo =====================================================================
echo  PowerGuard is launching in your default browser...
echo  To shut down, close the two terminal windows.
echo =====================================================================
timeout /t 3 /nobreak >nul
start http://localhost:5173

exit /b 0
