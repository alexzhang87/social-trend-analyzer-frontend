@echo off
REM Environment Configuration Management Script
REM ========================================

echo IdeaEden Environment Configuration Tool
echo ========================================

if "%1"=="" (
    echo Usage: setup-env.bat [development^|testing^|production]
    echo.
    echo Available environments:
    echo   development  - Development environment
    echo   testing      - Testing environment  
    echo   production   - Production environment
    echo.
    goto :end
)

set ENV=%1

echo Configuring %ENV% environment...

REM Check if environment config file exists
if not exist ".env.%ENV%" (
    echo Error: .env.%ENV% file not found
    goto :end
)

REM Copy environment config file
echo Copying environment config file...
copy ".env.%ENV%" ".env" >nul
if %errorlevel% neq 0 (
    echo Failed to copy environment config file
    goto :end
)

REM Copy frontend environment config
if exist "frontend\.env.%ENV%" (
    echo Copying frontend environment config file...
    copy "frontend\.env.%ENV%" "frontend\.env" >nul
)

REM Copy backend environment config
if exist "backend\.env.%ENV%" (
    echo Copying backend environment config file...
    copy "backend\.env.%ENV%" "backend\.env" >nul
)

echo %ENV% environment configuration completed!

REM Display current configuration info
echo.
echo Current Environment Configuration:
echo ========================================

if "%ENV%"=="development" (
    echo Development Environment
    echo   Frontend Port: 3001
    echo   Backend Port: 8001
    echo   Redis Port: 6380
    echo   Database: SQLite
    echo   Debug Mode: Enabled
) else if "%ENV%"=="testing" (
    echo Testing Environment
    echo   Frontend Port: 3001
    echo   Backend Port: 8001
    echo   Redis Port: 6380 ^(DB 1^)
    echo   Database: SQLite ^(test.db^)
    echo   Debug Mode: Enabled
) else if "%ENV%"=="production" (
    echo Production Environment
    echo   Frontend Port: 80
    echo   Backend Port: 8000
    echo   Redis Port: 6379
    echo   Database: PostgreSQL
    echo   Debug Mode: Disabled
)

echo.
echo Tips:
echo   - Use 'docker-compose -f docker-compose.%ENV%.yml up' to start services
echo   - Use 'start_system.bat' to start local development environment

:end
pause