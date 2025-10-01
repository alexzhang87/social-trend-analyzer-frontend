@echo off
echo ========================================
echo 🚀 启动后端服务
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
echo 📦 检查并安装依赖...
pip install -r requirements.txt > nul 2>&1

echo.
echo 🌐 启动后端服务 (端口8001)...
echo 访问地址: http://localhost:8001
echo API文档: http://localhost:8001/docs
echo 按 Ctrl+C 停止服务
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload