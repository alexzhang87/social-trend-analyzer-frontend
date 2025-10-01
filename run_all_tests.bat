@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo    Comprehensive Test Suite Runner
echo ========================================
echo.

set "SCRIPT_DIR=%~dp0"
set "BACKEND_DIR=%SCRIPT_DIR%backend"
set "FRONTEND_DIR=%SCRIPT_DIR%frontend"
set "RESULTS_DIR=%SCRIPT_DIR%test_results"
set "TIMESTAMP=%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%"
set "TIMESTAMP=%TIMESTAMP: =0%"

REM Create results directory
if not exist "%RESULTS_DIR%" mkdir "%RESULTS_DIR%"

echo [INFO] Starting comprehensive test suite...
echo [INFO] Timestamp: %TIMESTAMP%
echo [INFO] Results will be saved to: %RESULTS_DIR%
echo.

REM ===========================================
REM Check Prerequisites
REM ===========================================
echo [STEP 1] Checking prerequisites...

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo [INFO] Please install Python 3.7+ and add it to PATH
    pause
    exit /b 1
) else (
    echo [OK] Python is available
)

REM Check Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js is not installed or not in PATH
    echo [INFO] Please install Node.js and add it to PATH
    pause
    exit /b 1
) else (
    echo [OK] Node.js is available
)

REM Check npm
npm --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] npm is not available
    pause
    exit /b 1
) else (
    echo [OK] npm is available
)

echo.

REM ===========================================
REM Install Dependencies
REM ===========================================
echo [STEP 2] Installing dependencies...

REM Install Python dependencies
if exist "%BACKEND_DIR%\requirements.txt" (
    echo [INFO] Installing Python dependencies...
    cd /d "%BACKEND_DIR%"
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [WARNING] Some Python dependencies failed to install
    ) else (
        echo [OK] Python dependencies installed
    )
) else (
    echo [WARNING] Backend requirements.txt not found
)

REM Install Node.js dependencies
if exist "%FRONTEND_DIR%\package.json" (
    echo [INFO] Installing Node.js dependencies...
    cd /d "%FRONTEND_DIR%"
    npm install
    if errorlevel 1 (
        echo [WARNING] Some Node.js dependencies failed to install
    ) else (
        echo [OK] Node.js dependencies installed
    )
) else (
    echo [WARNING] Frontend package.json not found
)

cd /d "%SCRIPT_DIR%"
echo.

REM ===========================================
REM Install Test Dependencies
REM ===========================================
echo [STEP 3] Installing test dependencies...

REM Install requests for API testing
pip install requests >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Failed to install requests
) else (
    echo [OK] requests installed
)

REM Install selenium for E2E testing
pip install selenium >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Failed to install selenium
    echo [INFO] E2E tests may not work without selenium
) else (
    echo [OK] selenium installed
)

REM Install node-fetch for frontend testing
cd /d "%FRONTEND_DIR%"
npm install node-fetch >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Failed to install node-fetch
) else (
    echo [OK] node-fetch installed
)

cd /d "%SCRIPT_DIR%"
echo.

REM ===========================================
REM Run Backend API Tests
REM ===========================================
echo [STEP 4] Running backend API tests...

if exist "%SCRIPT_DIR%\backend\automated_api_tests.py" (
    echo [INFO] Starting backend API tests...
    python "%SCRIPT_DIR%\backend\automated_api_tests.py"
    set "BACKEND_TEST_RESULT=!errorlevel!"
    
    REM Move results to results directory
    if exist "api_test_results.json" (
        move "api_test_results.json" "%RESULTS_DIR%\api_test_results_%TIMESTAMP%.json" >nul
        echo [OK] Backend test results saved
    )
    
    if !BACKEND_TEST_RESULT! equ 0 (
        echo [OK] Backend API tests passed
    ) else (
        echo [WARNING] Backend API tests failed
    )
else (
    echo [WARNING] Backend API test script not found
    set "BACKEND_TEST_RESULT=1"
)

echo.

REM ===========================================
REM Run Frontend Tests
REM ===========================================
echo [STEP 5] Running frontend tests...

if exist "%FRONTEND_DIR%\automated_frontend_tests.js" (
    echo [INFO] Starting frontend tests...
    cd /d "%FRONTEND_DIR%"
    node automated_frontend_tests.js
    set "FRONTEND_TEST_RESULT=!errorlevel!"
    
    REM Move results to results directory
    if exist "frontend_test_results.json" (
        move "frontend_test_results.json" "%RESULTS_DIR%\frontend_test_results_%TIMESTAMP%.json" >nul
        echo [OK] Frontend test results saved
    )
    
    if !FRONTEND_TEST_RESULT! equ 0 (
        echo [OK] Frontend tests passed
    ) else (
        echo [WARNING] Frontend tests failed
    )
else (
    echo [WARNING] Frontend test script not found
    set "FRONTEND_TEST_RESULT=1"
)

cd /d "%SCRIPT_DIR%"
echo.

REM ===========================================
REM Run End-to-End Tests
REM ===========================================
echo [STEP 6] Running end-to-end tests...

if exist "%SCRIPT_DIR%\e2e_tests.py" (
    echo [INFO] Starting end-to-end tests...
    echo [INFO] This may take several minutes...
    python "%SCRIPT_DIR%\e2e_tests.py"
    set "E2E_TEST_RESULT=!errorlevel!"
    
    REM Move results to results directory
    if exist "e2e_test_results.json" (
        move "e2e_test_results.json" "%RESULTS_DIR%\e2e_test_results_%TIMESTAMP%.json" >nul
        echo [OK] E2E test results saved
    )
    
    if !E2E_TEST_RESULT! equ 0 (
        echo [OK] End-to-end tests passed
    ) else (
        echo [WARNING] End-to-end tests failed
    )
else (
    echo [WARNING] End-to-end test script not found
    set "E2E_TEST_RESULT=1"
)

echo.

REM ===========================================
REM Generate Summary Report
REM ===========================================
echo [STEP 7] Generating summary report...

set "SUMMARY_FILE=%RESULTS_DIR%\test_summary_%TIMESTAMP%.txt"

echo ======================================== > "%SUMMARY_FILE%"
echo    Comprehensive Test Suite Summary >> "%SUMMARY_FILE%"
echo ======================================== >> "%SUMMARY_FILE%"
echo. >> "%SUMMARY_FILE%"
echo Timestamp: %TIMESTAMP% >> "%SUMMARY_FILE%"
echo Test Date: %date% %time% >> "%SUMMARY_FILE%"
echo. >> "%SUMMARY_FILE%"
echo Test Results: >> "%SUMMARY_FILE%"
echo. >> "%SUMMARY_FILE%"

if !BACKEND_TEST_RESULT! equ 0 (
    echo [PASS] Backend API Tests >> "%SUMMARY_FILE%"
) else (
    echo [FAIL] Backend API Tests >> "%SUMMARY_FILE%"
)

if !FRONTEND_TEST_RESULT! equ 0 (
    echo [PASS] Frontend Tests >> "%SUMMARY_FILE%"
) else (
    echo [FAIL] Frontend Tests >> "%SUMMARY_FILE%"
)

if !E2E_TEST_RESULT! equ 0 (
    echo [PASS] End-to-End Tests >> "%SUMMARY_FILE%"
) else (
    echo [FAIL] End-to-End Tests >> "%SUMMARY_FILE%"
)

echo. >> "%SUMMARY_FILE%"

set /a "TOTAL_TESTS=3"
set /a "PASSED_TESTS=0"

if !BACKEND_TEST_RESULT! equ 0 set /a "PASSED_TESTS+=1"
if !FRONTEND_TEST_RESULT! equ 0 set /a "PASSED_TESTS+=1"
if !E2E_TEST_RESULT! equ 0 set /a "PASSED_TESTS+=1"

set /a "FAILED_TESTS=TOTAL_TESTS-PASSED_TESTS"
set /a "SUCCESS_RATE=PASSED_TESTS*100/TOTAL_TESTS"

echo Overall Statistics: >> "%SUMMARY_FILE%"
echo   Total Test Suites: !TOTAL_TESTS! >> "%SUMMARY_FILE%"
echo   Passed: !PASSED_TESTS! >> "%SUMMARY_FILE%"
echo   Failed: !FAILED_TESTS! >> "%SUMMARY_FILE%"
echo   Success Rate: !SUCCESS_RATE!%% >> "%SUMMARY_FILE%"
echo. >> "%SUMMARY_FILE%"

if !PASSED_TESTS! equ !TOTAL_TESTS! (
    echo Status: ALL TESTS PASSED >> "%SUMMARY_FILE%"
    echo The application is ready for deployment. >> "%SUMMARY_FILE%"
) else (
    echo Status: SOME TESTS FAILED >> "%SUMMARY_FILE%"
    echo Please review the failed tests before deployment. >> "%SUMMARY_FILE%"
)

echo. >> "%SUMMARY_FILE%"
echo Detailed results can be found in: >> "%SUMMARY_FILE%"
echo   - %RESULTS_DIR%\api_test_results_%TIMESTAMP%.json >> "%SUMMARY_FILE%"
echo   - %RESULTS_DIR%\frontend_test_results_%TIMESTAMP%.json >> "%SUMMARY_FILE%"
echo   - %RESULTS_DIR%\e2e_test_results_%TIMESTAMP%.json >> "%SUMMARY_FILE%"

echo [OK] Summary report generated: %SUMMARY_FILE%
echo.

REM ===========================================
REM Display Final Results
REM ===========================================
echo ========================================
echo           FINAL TEST RESULTS
echo ========================================
echo.
echo Backend API Tests:     %BACKEND_TEST_RESULT:0=PASS% %BACKEND_TEST_RESULT:1=FAIL%
echo Frontend Tests:         %FRONTEND_TEST_RESULT:0=PASS% %FRONTEND_TEST_RESULT:1=FAIL%
echo End-to-End Tests:       %E2E_TEST_RESULT:0=PASS% %E2E_TEST_RESULT:1=FAIL%
echo.
echo Overall Success Rate:  !SUCCESS_RATE!%% (!PASSED_TESTS!/!TOTAL_TESTS!)
echo.

if !PASSED_TESTS! equ !TOTAL_TESTS! (
    echo 🎉 ALL TESTS PASSED!
    echo    Your application is ready for deployment.
    set "FINAL_RESULT=0"
) else (
    echo ⚠️  SOME TESTS FAILED
    echo    Please review the failed tests before deployment.
    echo    Check the detailed results in: %RESULTS_DIR%
    set "FINAL_RESULT=1"
)

echo.
echo Test results saved to: %RESULTS_DIR%
echo Summary report: %SUMMARY_FILE%
echo.

REM ===========================================
REM Cleanup and Exit
REM ===========================================
echo [INFO] Test suite completed.
echo [INFO] Press any key to exit...
pause >nul

exit /b !FINAL_RESULT!