@echo off
echo ========================================
echo 📦 安装后端依赖
echo ========================================

echo.
echo 📁 切换到backend目录...
cd /d "%~dp0backend"

echo.
echo 🔧 检查虚拟环境...
if not exist ".venv" (
    echo 🛠️ 创建虚拟环境...
    python -m venv .venv
)

echo.
echo 🔧 激活虚拟环境...
call .venv\Scripts\activate.bat

echo.
echo 📦 安装依赖...
pip install -r requirements.txt

echo.
echo ✅ 依赖安装完成!
pause