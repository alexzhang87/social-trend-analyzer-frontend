@echo off
title Ngrok Test
color 0A

echo ========================================
echo   Ngrok 测试
echo ========================================
echo.

echo 🔍 检查ngrok安装...
ngrok version
if errorlevel 1 (
    echo ❌ Ngrok未安装或未添加到PATH
    echo 📥 请手动下载: https://ngrok.com/download
    echo 📁 解压到: C:\ngrok
    echo ⚙️  添加到PATH: C:\ngrok
    pause
    exit /b 1
)

echo ✅ Ngrok已安装

echo.
echo 🚀 启动测试隧道...
echo 💡 提示: 按Ctrl+C停止
echo.

ngrok http 8000