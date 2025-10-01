@echo off
echo ========================================
echo Railway 自动化部署脚本
echo ========================================

echo 检查Node.js是否已安装...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Node.js 未安装，请先安装Node.js
    echo 请访问 https://nodejs.org/ 下载并安装Node.js
    echo 安装完成后重新运行此脚本
    echo.
    echo 或者使用Chocolatey安装:
    echo choco install nodejs
    echo.
    echo 或者使用winget安装:
    echo winget install OpenJS.NodeJS
    pause
    exit /b 1
)

echo Node.js 已安装: 
node --version

echo.
echo 检查Railway CLI是否已安装...
railway --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Railway CLI 未安装，正在安装...
    npm install -g @railway/cli
    if %errorlevel% neq 0 (
        echo 安装Railway CLI失败，请检查网络连接或手动安装
        echo 运行: npm install -g @railway/cli
        pause
        exit /b 1
    )
)

echo Railway CLI 已安装: 
railway --version

echo.
echo ========================================
echo 开始Railway部署流程
echo ========================================

echo.
echo 1. 登录Railway...
echo 这将打开浏览器进行登录
railway login

echo.
echo 2. 初始化Railway项目...
railway init

echo.
echo 3. 设置环境变量...
echo.
echo 请在Railway控制台中设置以下环境变量:
echo ----------------------------------------
echo 必需的环境变量:
echo - ZHIPU_API_KEY: 您的智谱AI API密钥
echo - SECRET_KEY: JWT密钥（建议使用强随机字符串）
echo.
echo 可选的环境变量:
echo - TWITTERAPI_IO_KEY: 您的Twitter API密钥
echo - OPENAI_API_KEY: 您的OpenAI API密钥
echo - DATABASE_URL: 数据库连接URL（Railway可自动提供）
echo - REDIS_URL: Redis连接URL（Railway可自动提供）
echo ----------------------------------------
echo.
echo 您可以通过以下命令设置环境变量:
echo railway variables set ZHIPU_API_KEY=your_api_key
echo railway variables set SECRET_KEY=your_secret_key
echo.
echo 或者在Railway控制台网页中设置
echo.

echo 是否要添加PostgreSQL数据库服务? (y/n)
set /p add_db="请输入选择: "
if /i "%add_db%"=="y" (
    echo 添加PostgreSQL服务...
    railway add postgresql
)

echo.
echo 是否要添加Redis缓存服务? (y/n)
set /p add_redis="请输入选择: "
if /i "%add_redis%"=="y" (
    echo 添加Redis服务...
    railway add redis
)

echo.
echo 按任意键继续部署...
pause

echo.
echo 4. 开始部署到Railway...
railway up

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo 部署成功！
    echo ========================================
    echo.
    echo 有用的命令:
    echo - 查看部署状态: railway status
    echo - 查看日志: railway logs
    echo - 实时查看日志: railway logs --follow
    echo - 打开Railway控制台: railway open
    echo - 查看应用URL: railway domain
    echo.
    echo 获取应用URL...
    railway domain
    echo.
    echo 如果需要初始化数据库，请运行:
    echo railway run python railway_init.py
) else (
    echo.
    echo ========================================
    echo 部署失败！
    echo ========================================
    echo.
    echo 请检查:
    echo 1. 环境变量是否正确设置
    echo 2. railway.toml配置是否正确
    echo 3. Dockerfile是否有语法错误
    echo.
    echo 查看详细错误信息:
    echo railway logs
)

echo.
pause