@echo off
title Social Trend Analyzer - HTTPS Development Setup
color 0A

echo ========================================
echo   Social Trend Analyzer - HTTPS Setup
echo ========================================
echo.

echo 🚀 步骤1: 启动后端服务...
cd /d "%~dp0\backend"
start "Backend Server" cmd /c "python main.py & pause"

echo ⏳ 等待后端服务启动...
timeout /t 8 /nobreak >nul

echo 🔒 步骤2: 启动Ngrok HTTPS隧道...
start "Ngrok HTTPS Tunnel" cmd /c "ngrok http 8000 & pause"

echo.
echo ✅ 服务启动完成！
echo.
echo 📋 接下来的步骤：
echo 1. 在Ngrok窗口中复制HTTPS URL (如: https://abc123.ngrok.io)
echo 2. 在Product Hunt中使用该URL创建应用:
echo    - 应用网站: https://abc123.ngrok.io  
echo    - 回调URL: https://abc123.ngrok.io/auth/callback
echo 3. 更新 backend\.env 文件中的 PRODUCT_HUNT_REDIRECT_URI
echo 4. 运行 python test_product_hunt_api.py 测试连接
echo.
echo 🌐 Web界面:
echo - 后端API: http://localhost:8000 (或使用ngrok URL)
echo - Ngrok管理: http://localhost:4040
echo.

pause