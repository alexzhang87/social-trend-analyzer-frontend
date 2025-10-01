@echo off
echo ========================================
echo 🔄 更新后端依赖
echo ========================================

echo.
echo 📁 切换到backend目录...
cd /d "%~dp0backend"

echo.
echo 🔧 激活虚拟环境...
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
) else (
    echo ⚠️  虚拟环境未找到，请先运行 setup_backend.bat
    pause
    exit /b 1
)

echo.
echo 📦 更新依赖项...
pip install --upgrade reportlab
if %errorlevel% neq 0 (
    echo ❌ 更新reportlab失败
    pause
    exit /b %errorlevel%
)

pip install -r requirements.txt --upgrade
if %errorlevel% neq 0 (
    echo ❌ 更新依赖项失败
    pause
    exit /b %errorlevel%
)

echo.
echo ✅ 后端依赖更新完成！
echo.
pause