@echo off
echo ========================================
echo 🛠️ 设置后端环境
echo ========================================

echo.
echo 📁 切换到backend目录...
cd /d "%~dp0backend"

echo.
echo 🔧 检查并创建虚拟环境...
if not exist ".venv" (
    echo 🛠️ 创建虚拟环境...
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo ❌ 创建虚拟环境失败
        pause
        exit /b %errorlevel%
    )
)

echo.
echo 🔧 激活虚拟环境...
call .venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ❌ 激活虚拟环境失败
    pause
    exit /b %errorlevel%
)

echo.
echo 📦 升级pip...
python -m pip install --upgrade pip
if %errorlevel% neq 0 (
    echo ❌ 升级pip失败
    pause
    exit /b %errorlevel%
)

echo.
echo 📦 安装依赖项...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ 安装依赖项失败
    pause
    exit /b %errorlevel%
)

echo.
echo ✅ 后端环境设置完成！
echo.
echo 现在你可以运行 start_backend_simple.bat 来启动后端服务
echo 或者手动运行:
echo cd backend
echo .venv\Scripts\activate.bat
echo python -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload
echo.
pause