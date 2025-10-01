@echo off
echo ========================================
echo 版本恢复脚本
echo ========================================
echo.
echo 警告：此操作将覆盖当前版本的所有文件！
echo 请确保您已经备份了当前的修改。
echo.
set /p confirm="确定要恢复到备份版本吗？(y/N): "
if /i "%confirm%" neq "y" (
    echo 操作已取消。
    pause
    exit /b
)

echo.
echo 正在恢复备份版本...
echo.

REM 停止可能运行的服务
echo 停止运行中的服务...
taskkill /f /im node.exe 2>nul
taskkill /f /im python.exe 2>nul

REM 备份当前版本（以防万一）
echo 创建当前版本的临时备份...
if exist "..\current_version_temp_backup" rmdir /s /q "..\current_version_temp_backup"
mkdir "..\current_version_temp_backup"
xcopy "..\social-trend-analyzer" "..\current_version_temp_backup\social-trend-analyzer\" /e /i /h /y 2>nul
xcopy "..\backend" "..\current_version_temp_backup\backend\" /e /i /h /y 2>nul
copy "..\PRODUCT_MODIFICATION_PLAN.md" "..\current_version_temp_backup\" 2>nul

REM 恢复备份文件
echo 恢复前端代码...
if exist "..\social-trend-analyzer" rmdir /s /q "..\social-trend-analyzer"
xcopy "social-trend-analyzer" "..\social-trend-analyzer\" /e /i /h /y

echo 恢复后端代码...
if exist "..\backend" rmdir /s /q "..\backend"
xcopy "backend" "..\backend\" /e /i /h /y

echo 恢复配置文件...
copy "package.json" "..\package.json" /y
copy "package-lock.json" "..\package-lock.json" /y
copy ".gitignore" "..\gitignore" /y
copy "railway.toml" "..\railway.toml" /y

echo 恢复文档文件...
copy "PRODUCT_MODIFICATION_PLAN.md" "..\PRODUCT_MODIFICATION_PLAN.md" /y
copy "BUSINESS_STRATEGY_REDESIGN.md" "..\BUSINESS_STRATEGY_REDESIGN.md" /y
copy "product_value_upgrade_plan.md" "..\product_value_upgrade_plan.md" /y
copy "DEVELOPMENT_PROGRESS.md" "..\DEVELOPMENT_PROGRESS.md" /y

echo 恢复启动脚本...
copy "start_*.bat" "..\" /y

echo.
echo ========================================
echo 恢复完成！
echo ========================================
echo.
echo 注意事项：
echo 1. 请重新安装依赖：cd social-trend-analyzer && npm install
echo 2. 请重新安装后端依赖：cd backend && pip install -r requirements.txt
echo 3. 检查环境配置文件是否正确
echo 4. 当前版本的临时备份保存在：current_version_temp_backup 文件夹
echo.
echo 恢复完成后，您可以使用以下命令启动服务：
echo - 启动前端：cd social-trend-analyzer && npm run dev
echo - 启动后端：cd backend && python app/main.py
echo.
pause