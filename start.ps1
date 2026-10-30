# PowerGuard: Windows PowerShell Startup Script

Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "          PowerGuard: Electrical Load Monitoring Platform            " -ForegroundColor Cyan
Write-Host "                  Local System Startup Utility                       " -ForegroundColor Cyan
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Prerequisites Check
Write-Host "[1/5] Checking environment prerequisites..." -ForegroundColor Yellow
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] Python not found in PATH. Please install Python 3.10+ and add to PATH." -ForegroundColor Red
    exit 1
}
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] Node.js not found in PATH. Please install Node.js 18+ and add to PATH." -ForegroundColor Red
    exit 1
}
if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] npm not found in PATH." -ForegroundColor Red
    exit 1
}
Write-Host "      Python and Node.js detected successfully." -ForegroundColor Green

# 2. Backend Dependencies
Write-Host "`n[2/5] Checking backend dependencies..." -ForegroundColor Yellow
$pyCheck = python -c "import flask, sqlalchemy, sklearn, pandas, numpy; print('OK')" 2>$null
if ($pyCheck -ne "OK") {
    Write-Host "      Installing Python requirements..." -ForegroundColor Yellow
    python -m pip install -r backend/requirements.txt
} else {
    Write-Host "      Backend packages already satisfied." -ForegroundColor Green
}

# 3. Frontend Dependencies
Write-Host "`n[3/5] Checking frontend dependencies..." -ForegroundColor Yellow
if (-not (Test-Path "frontend/node_modules")) {
    Write-Host "      Installing frontend node modules..." -ForegroundColor Yellow
    npm install --prefix frontend
} else {
    Write-Host "      Frontend dependencies already installed." -ForegroundColor Green
}

# 4. Initialize Database
Write-Host "`n[4/5] Initializing PowerGuard SQLite database..." -ForegroundColor Yellow
python -c "import sys; sys.path.insert(0, 'backend'); from database import init_db; init_db()"
Write-Host "      Database schema initialized successfully." -ForegroundColor Green

# 5. Launch Servers
Write-Host "`n[5/5] Launching PowerGuard services..." -ForegroundColor Yellow
Write-Host "      - Backend:  http://127.0.0.1:5000" -ForegroundColor Cyan
Write-Host "      - Frontend: http://localhost:5173" -ForegroundColor Cyan
Write-Host ""

Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; python app.py"
Start-Sleep -Seconds 2
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev"

Start-Sleep -Seconds 3
Start-Process "http://localhost:5173"

Write-Host "PowerGuard launched successfully!" -ForegroundColor Green
