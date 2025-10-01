@echo off
title Ngrok Installation Script
color 0A

echo ========================================
echo   Ngrok HTTPS Tunnel Installation
echo ========================================
echo.

echo 📥 步骤1: 检查并下载Ngrok...
echo.

REM 创建ngrok目录
if not exist "c:\ngrok" mkdir c:\ngrok
cd /d c:\ngrok

REM 检查是否已存在ngrok.exe
if exist "ngrok.exe" (
    echo ✅ Ngrok已存在，跳过下载
    goto :setup
)

echo 正在下载Ngrok for Windows...
echo 下载地址: https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip
echo.
echo 请手动完成以下步骤:
echo 1. 访问 https://ngrok.com/download
echo 2. 选择 Windows (64-bit)
echo 3. 下载zip文件到 c:\ngrok 目录
echo 4. 解压ngrok.exe到当前目录
echo 5. 按任意键继续...
pause >nul

:setup
echo.
echo 📋 步骤2: 配置Ngrok...
echo.

REM 检查ngrok.exe是否存在
if not exist "ngrok.exe" (
    echo ❌ 未找到ngrok.exe，请确保已正确下载并解压
    echo 请将ngrok.exe放置在 c:\ngrok 目录下
    pause
    exit /b 1
)

echo ✅ 找到ngrok.exe

REM 添加到PATH环境变量
setx PATH "%PATH%;c:\ngrok" >nul 2>&1
echo ✅ 已添加到系统PATH

echo.
echo 🔑 步骤3: 获取Ngrok认证Token
echo.
echo 请完成以下步骤获取认证token:
echo 1. 访问: https://ngrok.com/signup
echo 2. 注册免费账号
echo 3. 登录后访问: https://dashboard.ngrok.com/get-started/your-authtoken
echo 4. 复制您的authtoken
echo.
set /p token=请输入您的authtoken: 

if "%token%"=="" (
    echo ❌ Token不能为空
    pause
    exit /b 1
)

REM 配置authtoken
ngrok authtoken %token%
if errorlevel 1 (
    echo ❌ Token配置失败，请检查token是否正确
    pause
    exit /b 1
)

echo ✅ Authtoken配置成功

echo.
echo 🎉 Ngrok安装配置完成！
echo.
echo 📋 使用说明:
echo 1. 启动后端服务: cd backend ^&^& python main.py
echo 2. 启动ngrok隧道: ngrok http 8000
echo 3. 复制HTTPS URL用于Product Hunt配置
echo.
echo 💡 提示: 您也可以使用 start_with_ngrok.bat 一键启动
echo.
pause