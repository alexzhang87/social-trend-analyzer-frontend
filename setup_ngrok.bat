@echo off
title Ngrok 快速配置
color 0A

echo ========================================
echo   Ngrok 快速配置和测试
echo ========================================
echo.

echo 📁 检查ngrok.exe位置...

REM 检查是否在C:\ngrok目录
if exist "C:\ngrok\ngrok.exe" (
    echo ✅ 找到: C:\ngrok\ngrok.exe
    goto :test_version
)

REM 检查当前目录
if exist "ngrok.exe" (
    echo ✅ 找到: %cd%\ngrok.exe
    echo 📦 移动到标准位置...
    if not exist "C:\ngrok" mkdir C:\ngrok
    copy "ngrok.exe" "C:\ngrok\ngrok.exe" >nul
    if exist "C:\ngrok\ngrok.exe" (
        echo ✅ 已移动到 C:\ngrok\
        goto :test_version
    ) else (
        echo ❌ 移动失败
        goto :manual_instruction
    )
)

echo ❌ 未找到ngrok.exe文件

:manual_instruction
echo.
echo 📋 请完成以下步骤:
echo 1. 确保已下载ngrok.exe文件
echo 2. 将ngrok.exe复制到 C:\ngrok\ 目录
echo 3. 重新运行此脚本
echo.
pause
exit /b 1

:test_version
echo.
echo 🔍 测试ngrok版本...
C:\ngrok\ngrok.exe version
if errorlevel 1 (
    echo ❌ ngrok运行失败
    goto :manual_instruction
)

echo.
echo ✅ ngrok运行正常！

echo.
echo 🔗 现在需要获取认证token:
echo 1. 访问: https://ngrok.com/signup
echo 2. 注册免费账号
echo 3. 登录后访问: https://dashboard.ngrok.com/get-started/your-authtoken
echo 4. 复制authtoken
echo.

set /p token=请粘贴您的authtoken: 

if "%token%"=="" (
    echo ❌ Token不能为空
    echo 💡 您可以稍后运行: C:\ngrok\ngrok.exe authtoken YOUR_TOKEN
    goto :start_tunnel
)

echo.
echo 🔑 配置authtoken...
C:\ngrok\ngrok.exe authtoken %token%
if errorlevel 1 (
    echo ❌ Token配置失败
    echo 💡 您可以稍后手动配置
) else (
    echo ✅ Token配置成功
)

:start_tunnel
echo.
echo 🚀 现在可以启动HTTPS隧道了！
echo.
echo 💡 使用方法:
echo 1. 确保后端服务运行: cd backend ^&^& python main.py
echo 2. 启动隧道: C:\ngrok\ngrok.exe http 8000
echo 3. 复制显示的HTTPS URL用于Product Hunt配置
echo.

set /p choice=是否现在启动隧道? (y/n): 
if /i "%choice%"=="y" (
    echo.
    echo 🔒 启动HTTPS隧道...
    echo 💡 按Ctrl+C停止隧道
    echo.
    C:\ngrok\ngrok.exe http 8000
) else (
    echo.
    echo 📋 稍后手动启动隧道:
    echo C:\ngrok\ngrok.exe http 8000
    echo.
)

pause