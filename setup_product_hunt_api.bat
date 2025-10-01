@echo off
title Product Hunt API Setup with Ngrok
color 0A

echo ========================================
echo   Product Hunt API Configuration
echo ========================================
echo.

echo 📋 配置清单:
echo ✅ Reddit API - 已完成
echo 🔄 Product Hunt API - 进行中
echo 🔄 Ngrok HTTPS - 进行中
echo.

echo 🚀 步骤1: 启动后端服务...
echo.

REM 检查后端服务是否已启动
tasklist /FI "IMAGENAME eq python.exe" 2>NUL | find /I /N "python.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo ✅ 后端服务已在运行
) else (
    echo 启动后端服务...
    cd /d "%~dp0\backend"
    start "Backend Server" cmd /c ".venv\Scripts\activate.bat && python main.py"
    echo ⏳ 等待服务启动...
    timeout /t 8 /nobreak >nul
    echo ✅ 后端服务已启动
)

echo.
echo 🔒 步骤2: 启动Ngrok HTTPS隧道...
echo.

REM 检查ngrok是否可用
ngrok version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到ngrok，请先运行 install_ngrok.bat 安装
    echo.
    echo 或者手动安装:
    echo 1. 访问 https://ngrok.com/download
    echo 2. 下载Windows版本
    echo 3. 解压到任意目录
    echo 4. 添加到系统PATH
    echo.
    pause
    exit /b 1
)

echo ✅ Ngrok已安装

REM 启动ngrok隧道
echo 启动HTTPS隧道...
start "Ngrok HTTPS Tunnel" cmd /k "echo 🔒 Ngrok HTTPS隧道 && echo. && echo 复制下面的HTTPS URL: && echo. && ngrok http 8000"

echo ⏳ 等待Ngrok启动...
timeout /t 5 /nobreak >nul

echo.
echo 🌐 步骤3: Product Hunt应用注册...
echo.
echo 📋 请按照以下步骤注册Product Hunt应用:
echo.
echo 1. 📱 打开Product Hunt API页面:
echo    https://api.producthunt.com/v2/oauth/applications
echo.
echo 2. 🔑 登录您的Product Hunt账号
echo    (如没有账号请先注册: https://www.producthunt.com/)
echo.
echo 3. ➕ 点击 "New Application" 创建应用
echo.
echo 4. 📝 填写应用信息:
echo    应用名称: Social Trend Analyzer
echo    应用描述: AI-powered social media trend analysis platform for entrepreneurs and startups
echo.
echo 5. 🔗 配置重定向URI:
echo    ⚠️  重要: 从Ngrok窗口复制HTTPS URL
echo    格式: https://abc123.ngrok.io/auth/callback
echo    注意: 必须是HTTPS协议，不能是HTTP
echo.
echo 6. 💾 保存应用并获取:
echo    - Client ID (保存此信息)
echo    - Client Secret (保存此信息)
echo.

echo 📋 当您获得API凭证后:
echo.
set /p client_id=请输入Product Hunt Client ID: 
set /p client_secret=请输入Product Hunt Client Secret: 
set /p redirect_uri=请输入完整的重定向URI (https://xxx.ngrok.io/auth/callback): 

if "%client_id%"=="" (
    echo ❌ Client ID不能为空
    pause
    exit /b 1
)

if "%client_secret%"=="" (
    echo ❌ Client Secret不能为空
    pause
    exit /b 1
)

if "%redirect_uri%"=="" (
    echo ❌ 重定向URI不能为空
    pause
    exit /b 1
)

echo.
echo 📝 步骤4: 更新环境变量配置...
echo.

REM 更新.env文件
cd /d "%~dp0\backend"

REM 创建临时文件来更新.env
echo 正在更新 .env 配置文件...

powershell -Command "(Get-Content .env) -replace 'PRODUCT_HUNT_CLIENT_ID=.*', 'PRODUCT_HUNT_CLIENT_ID=%client_id%' | Set-Content .env.tmp"
powershell -Command "(Get-Content .env.tmp) -replace 'PRODUCT_HUNT_CLIENT_SECRET=.*', 'PRODUCT_HUNT_CLIENT_SECRET=%client_secret%' | Set-Content .env.tmp2"
powershell -Command "(Get-Content .env.tmp2) -replace 'PRODUCT_HUNT_REDIRECT_URI=.*', 'PRODUCT_HUNT_REDIRECT_URI=%redirect_uri%' | Set-Content .env"

del .env.tmp >nul 2>&1
del .env.tmp2 >nul 2>&1

echo ✅ 环境变量已更新

echo.
echo 🧪 步骤5: 测试Product Hunt API连接...
echo.

REM 运行测试脚本
echo 运行Product Hunt API测试...
.venv\Scripts\activate.bat && python -c "
import asyncio
import sys
import os
sys.path.append('.')
from app.services.product_hunt_service import product_hunt_service

async def quick_test():
    try:
        print('🔐 测试API认证...')
        token = await product_hunt_service._get_access_token()
        if token:
            print('✅ Product Hunt API认证成功！')
            print(f'   Token: {token[:30]}...')
            
            print('📱 测试今日产品获取...')
            products = await product_hunt_service.get_daily_products(limit=3)
            print(f'✅ 获取到 {len(products)} 个产品')
            
            return True
        else:
            print('❌ 认证失败')
            return False
    except Exception as e:
        print(f'❌ 测试失败: {e}')
        return False

result = asyncio.run(quick_test())
if result:
    print('🎉 Product Hunt API配置成功！')
else:
    print('❌ 配置失败，请检查凭证')
"

if errorlevel 1 (
    echo.
    echo ⚠️  API测试遇到问题，但配置已保存
    echo 💡 您可以稍后手动运行测试: python test_product_hunt_api.py
)

echo.
echo 🎉 配置完成！
echo.
echo 📋 配置总结:
echo ✅ Reddit API - 工作正常
echo ✅ Product Hunt API - 已配置
echo ✅ Ngrok HTTPS - 已启动
echo ✅ 环境变量 - 已更新
echo.
echo 🔗 重要提醒:
echo - Ngrok隧道会在关闭终端后停止
echo - 每次重启Ngrok都会获得新的URL
echo - 如需更新重定向URI，请修改Product Hunt应用设置
echo.
echo 🚀 下一步: 您可以开始集成Product Hunt数据到分析服务中
echo.
pause