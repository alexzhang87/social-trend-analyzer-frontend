@echo off
echo ========================================
echo 版本对比工具
echo ========================================
echo.
echo 此工具将帮助您对比当前版本与备份版本的差异
echo.

REM 检查关键文件的差异
echo 正在检查关键文件差异...
echo.

echo [1] 产品修改方案对比：
if exist "..\PRODUCT_MODIFICATION_PLAN.md" (
    if exist "PRODUCT_MODIFICATION_PLAN.md" (
        fc "..\PRODUCT_MODIFICATION_PLAN.md" "PRODUCT_MODIFICATION_PLAN.md" >nul
        if errorlevel 1 (
            echo    ✗ 文件有差异
        ) else (
            echo    ✓ 文件相同
        )
    ) else (
        echo    ✗ 备份文件不存在
    )
) else (
    echo    ✗ 当前文件不存在
)

echo.
echo [2] 前端主要组件对比：
if exist "..\social-trend-analyzer\src\components\hero-section.tsx" (
    if exist "social-trend-analyzer\src\components\hero-section.tsx" (
        fc "..\social-trend-analyzer\src\components\hero-section.tsx" "social-trend-analyzer\src\components\hero-section.tsx" >nul
        if errorlevel 1 (
            echo    ✗ hero-section.tsx 有差异
        ) else (
            echo    ✓ hero-section.tsx 相同
        )
    ) else (
        echo    ✗ 备份中的 hero-section.tsx 不存在
    )
) else (
    echo    ✗ 当前 hero-section.tsx 不存在
)

if exist "..\social-trend-analyzer\src\components\pricing-page.tsx" (
    if exist "social-trend-analyzer\src\components\pricing-page.tsx" (
        fc "..\social-trend-analyzer\src\components\pricing-page.tsx" "social-trend-analyzer\src\components\pricing-page.tsx" >nul
        if errorlevel 1 (
            echo    ✗ pricing-page.tsx 有差异
        ) else (
            echo    ✓ pricing-page.tsx 相同
        )
    ) else (
        echo    ✗ 备份中的 pricing-page.tsx 不存在
    )
) else (
    echo    ✗ 当前 pricing-page.tsx 不存在
)

echo.
echo [3] 配置文件对比：
if exist "..\package.json" (
    if exist "package.json" (
        fc "..\package.json" "package.json" >nul
        if errorlevel 1 (
            echo    ✗ package.json 有差异
        ) else (
            echo    ✓ package.json 相同
        )
    ) else (
        echo    ✗ 备份中的 package.json 不存在
    )
) else (
    echo    ✗ 当前 package.json 不存在
)

echo.
echo ========================================
echo 对比完成
echo ========================================
echo.
echo 如需查看详细差异，可以使用以下工具：
echo - VS Code: 打开两个文件夹进行对比
echo - WinMerge: 专业的文件对比工具
echo - Git: 如果使用版本控制，可以用 git diff
echo.
echo 如需恢复到备份版本，请运行：restore_backup.bat
echo.
pause