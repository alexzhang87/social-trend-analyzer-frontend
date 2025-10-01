@echo off
title Backend Service - Trend Analyzer
echo ========================================
echo 🚀 启动后端服务 (简化版)
echo ========================================

echo.
echo 📁 切换到backend目录...
cd /d "%~dp0backend"

echo.
echo 🔧 检查虚拟环境...
if not exist ".venv" (
    echo ⚠️  虚拟环境未找到
    echo 请先运行 setup_backend.bat 创建虚拟环境并安装依赖项
    pause
    exit /b 1
)

echo.
echo 🔧 激活虚拟环境...
call .venv\Scripts\activate.bat

echo.
echo 📦 检查并更新依赖...
pip install -r requirements.txt > nul 2>&1

echo.
echo 🌐 启动后端服务...
echo 访问地址: http://localhost:8001
echo API文档: http://localhost:8001/docs
echo 按 Ctrl+C 停止服务
echo.

python -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload --log-level info