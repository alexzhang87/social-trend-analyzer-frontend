@echo off
title Frontend Service - Trend Analyzer
echo ========================================
echo 🚀 启动前端服务
echo ========================================

echo.
echo 📁 切换到前端目录...
cd /d "%~dp0social-trend-analyzer"

echo.
echo 🔧 检查并安装依赖...
call npm install

echo.
echo 🌐 启动前端开发服务器...
echo 访问地址: http://localhost:5173
echo 按 Ctrl+C 停止服务
echo.

npm run dev