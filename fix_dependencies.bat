@echo off
echo ========================================
echo Social Media Trend Analyzer - Dependency Fix
echo ========================================
echo.

set "PROJECT_ROOT=%~dp0"
set "BACKEND_DIR=%PROJECT_ROOT%backend"
set "FRONTEND_DIR=%PROJECT_ROOT%social-trend-analyzer"
set "ERROR_COUNT=0"

echo Project directories:
echo    Backend: %BACKEND_DIR%
echo    Frontend: %FRONTEND_DIR%
echo.

REM Check Python environment
echo Checking Python environment...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not installed or not in PATH
    set /a ERROR_COUNT+=1
    goto :check_node
) else (
    echo OK: Python environment ready
)

REM Check backend dependencies
echo.
echo Checking backend Python dependencies...
cd /d "%BACKEND_DIR%"

REM Activate virtual environment if exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
    echo OK: Virtual environment activated
) else (
    echo WARNING: No virtual environment found, using global Python
)

REM Install backend dependencies
echo.
echo Installing backend dependencies...
echo Upgrading pip...
python -m pip install --upgrade pip

echo Installing from requirements.txt...
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo WARNING: requirements.txt installation failed, trying individual packages...
    
    echo Installing core framework...
    pip install fastapi uvicorn[standard] pydantic sqlalchemy python-dotenv
    
    echo Installing authentication modules...
    pip install "python-jose[cryptography]" "passlib[bcrypt]" email-validator
    
    echo Installing task queue...
    pip install "celery[redis]" redis
    
    echo Installing text analysis...
    pip install vaderSentiment jieba textblob nltk
    
    echo Installing data processing...
    pip install pandas numpy scikit-learn
    
    echo Installing network tools...
    pip install requests aiohttp beautifulsoup4 snscrape
    
    echo Installing other tools...
    pip install zhipuai reportlab stripe emoji pytrends retrying
)

echo.
echo Verifying key dependencies...
python -c "import fastapi; print('OK: FastAPI installed')" 2>nul || echo "ERROR: FastAPI not found"
python -c "import uvicorn; print('OK: Uvicorn installed')" 2>nul || echo "ERROR: Uvicorn not found"
python -c "import email_validator; print('OK: Email-validator installed')" 2>nul || echo "ERROR: Email-validator not found"
python -c "import jose; print('OK: Python-JOSE installed')" 2>nul || echo "ERROR: Python-JOSE not found"
python -c "import passlib; print('OK: Passlib installed')" 2>nul || echo "ERROR: Passlib not found"

:check_node
REM Check Node.js environment
echo.
echo Checking Node.js environment...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js not installed
    echo Please visit https://nodejs.org to download and install Node.js
    set /a ERROR_COUNT+=1
    goto :summary
) else (
    echo OK: Node.js environment ready
)

REM Check frontend dependencies
echo.
echo Checking frontend dependencies...
cd /d "%FRONTEND_DIR%"

REM Check package.json
if not exist "package.json" (
    echo ERROR: package.json file not found
    set /a ERROR_COUNT+=1
    goto :summary
)

REM Install frontend dependencies
echo Installing frontend dependencies...
npm install

if %errorlevel% neq 0 (
    echo WARNING: npm install failed, trying to fix...
    npm cache clean --force
    rmdir /s /q node_modules 2>nul
    del package-lock.json 2>nul
    npm install
    
    if %errorlevel% neq 0 (
        echo ERROR: Frontend dependency installation failed
        set /a ERROR_COUNT+=1
    ) else (
        echo OK: Frontend dependencies installed successfully
    )
) else (
    echo OK: Frontend dependencies installed successfully
)

:summary
echo.
echo ========================================
echo Dependency Check Results
echo ========================================

if %ERROR_COUNT% equ 0 (
    echo SUCCESS: All dependencies are ready!
    echo.
    echo You can now start the services:
    echo    Backend: start_backend_simple.bat
    echo    Frontend: cd social-trend-analyzer && npm run dev
    echo.
    echo Service URLs:
    echo    Backend API: http://localhost:8001
    echo    Frontend UI: http://localhost:5173
) else (
    echo ERROR: Found %ERROR_COUNT% issues that need manual resolution
    echo.
    echo Suggested actions:
    echo    1. Check Python and Node.js installation
    echo    2. Ensure network connection is stable
    echo    3. Check firewall settings
    echo    4. Run install_all_dependencies.bat manually
)

echo.
echo Press any key to continue...
pause >nul
exit /b %ERROR_COUNT%