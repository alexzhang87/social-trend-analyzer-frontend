# Comprehensive Test Suite Runner
# 自动化前后端功能测试套件

Param(
    [switch]$SkipE2E = $false
)

# 设置编码
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# 测试配置
$ScriptDir = $PSScriptRoot
$BackendDir = Join-Path $ScriptDir "backend"
$FrontendDir = Join-Path $ScriptDir "frontend"
$ResultsDir = Join-Path $ScriptDir "test_results"
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"

# 创建结果目录
if (-not (Test-Path $ResultsDir)) {
    New-Item -ItemType Directory -Path $ResultsDir -Force | Out-Null
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Comprehensive Test Suite Runner" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "[INFO] Starting comprehensive test suite..." -ForegroundColor Green
Write-Host "[INFO] Timestamp: $Timestamp" -ForegroundColor Green
Write-Host "[INFO] Results will be saved to: $ResultsDir" -ForegroundColor Green
Write-Host ""

# 测试结果跟踪
$BackendResult = 1
$FrontendResult = 1
$E2EResult = 1
$TotalTests = 3
$PassedTests = 0

# 检查先决条件
Write-Host "[STEP 1] Checking prerequisites..." -ForegroundColor Yellow

# 检查Python
try {
    $pythonCheck = python --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Python is available: $pythonCheck" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] Python is not installed or not in PATH" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "[ERROR] Python check failed" -ForegroundColor Red
    exit 1
}

# 检查Node.js
try {
    $nodeCheck = node --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Node.js is available: $nodeCheck" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] Node.js is not installed or not in PATH" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "[ERROR] Node.js check failed" -ForegroundColor Red
    exit 1
}

Write-Host ""

# 安装测试依赖
Write-Host "[STEP 2] Installing test dependencies..." -ForegroundColor Yellow

# 安装requests
try {
    pip install requests 2>&1 | Out-Null
    Write-Host "[OK] requests installed" -ForegroundColor Green
} catch {
    Write-Host "[WARNING] Failed to install requests" -ForegroundColor Yellow
}

# 安装selenium (如果不跳过E2E测试)
if (-not $SkipE2E) {
    try {
        pip install selenium 2>&1 | Out-Null
        Write-Host "[OK] selenium installed" -ForegroundColor Green
    } catch {
        Write-Host "[WARNING] Failed to install selenium" -ForegroundColor Yellow
    }
}

Write-Host ""

# 运行后端API测试
Write-Host "[STEP 3] Running backend API tests..." -ForegroundColor Yellow

$backendTestScript = Join-Path $BackendDir "automated_api_tests.py"
if (Test-Path $backendTestScript) {
    Write-Host "[INFO] Starting backend API tests..." -ForegroundColor White
    try {
        python $backendTestScript
        $BackendResult = $LASTEXITCODE
        
        # 移动结果文件
        $resultFile = "api_test_results.json"
        if (Test-Path $resultFile) {
            $newPath = Join-Path $ResultsDir "api_test_results_$Timestamp.json"
            Move-Item $resultFile $newPath -Force
            Write-Host "[OK] Backend test results saved" -ForegroundColor Green
        }
        
        if ($BackendResult -eq 0) {
            Write-Host "[OK] Backend API tests passed" -ForegroundColor Green
            $PassedTests++
        } else {
            Write-Host "[WARNING] Backend API tests failed" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "[ERROR] Backend test execution failed" -ForegroundColor Red
        $BackendResult = 1
    }
} else {
    Write-Host "[WARNING] Backend API test script not found" -ForegroundColor Yellow
    $BackendResult = 1
}

Write-Host ""

# 运行前端测试
Write-Host "[STEP 4] Running frontend tests..." -ForegroundColor Yellow

$frontendTestScript = Join-Path $FrontendDir "automated_frontend_tests.js"
if (Test-Path $frontendTestScript) {
    Write-Host "[INFO] Starting frontend tests..." -ForegroundColor White
    Push-Location $FrontendDir
    try {
        node automated_frontend_tests.js
        $FrontendResult = $LASTEXITCODE
        
        # 移动结果文件
        $resultFile = "frontend_test_results.json"
        if (Test-Path $resultFile) {
            $newPath = Join-Path $ResultsDir "frontend_test_results_$Timestamp.json"
            Move-Item $resultFile $newPath -Force
            Write-Host "[OK] Frontend test results saved" -ForegroundColor Green
        }
        
        if ($FrontendResult -eq 0) {
            Write-Host "[OK] Frontend tests passed" -ForegroundColor Green
            $PassedTests++
        } else {
            Write-Host "[WARNING] Frontend tests failed" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "[ERROR] Frontend test execution failed" -ForegroundColor Red
        $FrontendResult = 1
    }
    Pop-Location
} else {
    Write-Host "[WARNING] Frontend test script not found" -ForegroundColor Yellow
    $FrontendResult = 1
}

Write-Host ""

# 运行端到端测试
if ($SkipE2E) {
    Write-Host "[STEP 5] Skipping end-to-end tests..." -ForegroundColor Yellow
    $E2EResult = 0
    $PassedTests++
    $TotalTests--
} else {
    Write-Host "[STEP 5] Running end-to-end tests..." -ForegroundColor Yellow
    
    $e2eTestScript = Join-Path $ScriptDir "e2e_tests.py"
    if (Test-Path $e2eTestScript) {
        Write-Host "[INFO] Starting end-to-end tests..." -ForegroundColor White
        Write-Host "[INFO] This may take several minutes..." -ForegroundColor White
        try {
            python $e2eTestScript
            $E2EResult = $LASTEXITCODE
            
            # 移动结果文件
            $resultFile = "e2e_test_results.json"
            if (Test-Path $resultFile) {
                $newPath = Join-Path $ResultsDir "e2e_test_results_$Timestamp.json"
                Move-Item $resultFile $newPath -Force
                Write-Host "[OK] E2E test results saved" -ForegroundColor Green
            }
            
            if ($E2EResult -eq 0) {
                Write-Host "[OK] End-to-end tests passed" -ForegroundColor Green
                $PassedTests++
            } else {
                Write-Host "[WARNING] End-to-end tests failed" -ForegroundColor Yellow
            }
        } catch {
            Write-Host "[ERROR] E2E test execution failed" -ForegroundColor Red
            $E2EResult = 1
        }
    } else {
        Write-Host "[WARNING] End-to-end test script not found" -ForegroundColor Yellow
        $E2EResult = 1
    }
}

Write-Host ""

# 生成摘要报告
Write-Host "[STEP 6] Generating summary report..." -ForegroundColor Yellow

$summaryFile = Join-Path $ResultsDir "test_summary_$Timestamp.txt"

$summary = "========================================`n"
$summary += "   Comprehensive Test Suite Summary`n"
$summary += "========================================`n`n"
$summary += "Timestamp: $Timestamp`n"
$summary += "Test Date: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')`n`n"
$summary += "Test Results:`n`n"

if ($BackendResult -eq 0) {
    $summary += "[PASS] Backend API Tests`n"
} else {
    $summary += "[FAIL] Backend API Tests`n"
}

if ($FrontendResult -eq 0) {
    $summary += "[PASS] Frontend Tests`n"
} else {
    $summary += "[FAIL] Frontend Tests`n"
}

if (-not $SkipE2E) {
    if ($E2EResult -eq 0) {
        $summary += "[PASS] End-to-End Tests`n"
    } else {
        $summary += "[FAIL] End-to-End Tests`n"
    }
} else {
    $summary += "[SKIP] End-to-End Tests`n"
}

$failedTests = $TotalTests - $PassedTests
$successRate = [math]::Round(($PassedTests / $TotalTests) * 100, 1)

$summary += "`nOverall Statistics:`n"
$summary += "  Total Test Suites: $TotalTests`n"
$summary += "  Passed: $PassedTests`n"
$summary += "  Failed: $failedTests`n"
$summary += "  Success Rate: $successRate%`n`n"

if ($PassedTests -eq $TotalTests) {
    $summary += "Status: ALL TESTS PASSED`n"
    $summary += "The application is ready for deployment.`n"
} else {
    $summary += "Status: SOME TESTS FAILED`n"
    $summary += "Please review the failed tests before deployment.`n"
}

$summary += "`nDetailed results can be found in:`n"
$summary += "  - $ResultsDir\api_test_results_$Timestamp.json`n"
$summary += "  - $ResultsDir\frontend_test_results_$Timestamp.json`n"

if (-not $SkipE2E) {
    $summary += "  - $ResultsDir\e2e_test_results_$Timestamp.json`n"
}

$summary | Out-File -FilePath $summaryFile -Encoding UTF8
Write-Host "[OK] Summary report generated: $summaryFile" -ForegroundColor Green
Write-Host ""

# 显示最终结果
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "           FINAL TEST RESULTS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$backendStatus = if ($BackendResult -eq 0) { "PASS" } else { "FAIL" }
$frontendStatus = if ($FrontendResult -eq 0) { "PASS" } else { "FAIL" }
$e2eStatus = if ($SkipE2E) { "SKIP" } elseif ($E2EResult -eq 0) { "PASS" } else { "FAIL" }

Write-Host "Backend API Tests:     $backendStatus" -ForegroundColor $(if ($BackendResult -eq 0) { "Green" } else { "Red" })
Write-Host "Frontend Tests:        $frontendStatus" -ForegroundColor $(if ($FrontendResult -eq 0) { "Green" } else { "Red" })
Write-Host "End-to-End Tests:      $e2eStatus" -ForegroundColor $(if ($SkipE2E) { "Yellow" } elseif ($E2EResult -eq 0) { "Green" } else { "Red" })
Write-Host ""
Write-Host "Overall Success Rate:  $successRate% ($PassedTests/$TotalTests)" -ForegroundColor White
Write-Host ""

if ($PassedTests -eq $TotalTests) {
    Write-Host "🎉 ALL TESTS PASSED!" -ForegroundColor Green
    Write-Host "   Your application is ready for deployment." -ForegroundColor Green
    $exitCode = 0
} else {
    Write-Host "⚠️  SOME TESTS FAILED" -ForegroundColor Yellow
    Write-Host "   Please review the failed tests before deployment." -ForegroundColor Yellow
    Write-Host "   Check the detailed results in: $ResultsDir" -ForegroundColor Yellow
    $exitCode = 1
}

Write-Host ""
Write-Host "Test results saved to: $ResultsDir" -ForegroundColor White
Write-Host "Summary report: $summaryFile" -ForegroundColor White
Write-Host ""

Write-Host "[INFO] Test suite completed." -ForegroundColor Green
exit $exitCode