@echo off
chcp 65001 >nul
echo ========================================
echo 🔍 社交媒体趋势分析工具 - 综合依赖检查
echo ========================================
echo.

set "PROJECT_ROOT=%~dp0"
set "BACKEND_DIR=%PROJECT_ROOT%backend"
set "FRONTEND_DIR=%PROJECT_ROOT%social-trend-analyzer"
set "ERROR_COUNT=0"

echo 📋 项目目录:
echo    后端: %BACKEND_DIR%
echo    前端: %FRONTEND_DIR%
echo.

REM 检查Python环境
echo 🐍 检查Python环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python未安装或未添加到PATH
    set /a ERROR_COUNT+=1
    goto :check_node
) else (
    echo ✅ Python环境正常
)

REM 检查后端依赖
echo.
echo 🔍 检查后端Python依赖...
cd /d "%BACKEND_DIR%"

REM 激活虚拟环境（如果存在）
if exist "venv\Scripts\activate.bat" (
    echo 🔄 激活虚拟环境...
    call venv\Scripts\activate.bat
    echo ✅ 虚拟环境已激活
) else (
    echo ⚠️  虚拟环境不存在，使用全局Python环境
)

REM 运行后端依赖检查
if exist "quick_dependency_check.py" (
    echo 📊 运行后端依赖检查...
    python quick_dependency_check.py
    if %errorlevel% neq 0 (
        echo ❌ 后端依赖检查发现问题
        set /a ERROR_COUNT+=1
        
        echo.
        echo 🔧 尝试自动修复后端依赖...
        echo 📦 更新pip...
        python -m pip install --upgrade pip
        
        echo 📦 安装requirements.txt依赖...
        pip install -r requirements.txt
        
        if %errorlevel% neq 0 (
            echo ⚠️  requirements.txt安装失败，尝试逐个安装关键依赖...
            
            echo 📦 安装核心框架...
            pip install fastapi uvicorn[standard] pydantic sqlalchemy python-dotenv
            
            echo 📦 安装认证模块...
            pip install "python-jose[cryptography]" "passlib[bcrypt]" email-validator
            
            echo 📦 安装任务队列...
            pip install "celery[redis]" redis
            
            echo 📦 安装文本分析...
            pip install vaderSentiment jieba textblob nltk
            
            echo 📦 安装数据处理...
            pip install pandas numpy scikit-learn
            
            echo 📦 安装网络工具...
            pip install requests aiohttp beautifulsoup4 snscrape
            
            echo 📦 安装其他工具...
            pip install zhipuai reportlab stripe emoji pytrends retrying
        )
        
        echo.
        echo 🔍 重新检查后端依赖...
        python quick_dependency_check.py
        if %errorlevel% neq 0 (
            echo ❌ 后端依赖修复失败
        ) else (
            echo ✅ 后端依赖修复成功
            set /a ERROR_COUNT-=1
        )
    ) else (
        echo ✅ 后端依赖检查通过
    )
) else (
    echo ⚠️  后端依赖检查脚本不存在，跳过检查
)

:check_node
REM 检查Node.js环境
echo.
echo 🟢 检查Node.js环境...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js未安装
    echo 💡 请访问 https://nodejs.org 下载安装Node.js
    set /a ERROR_COUNT+=1
    goto :summary
) else (
    echo ✅ Node.js环境正常
)

REM 检查前端依赖
echo.
echo 🔍 检查前端依赖...
cd /d "%FRONTEND_DIR%"

REM 检查package.json
if not exist "package.json" (
    echo ❌ package.json文件不存在
    set /a ERROR_COUNT+=1
    goto :summary
)

REM 检查node_modules
if not exist "node_modules" (
    echo ⚠️  node_modules目录不存在，需要安装依赖
    set /a ERROR_COUNT+=1
    
    echo 📦 安装前端依赖...
    npm install
    
    if %errorlevel% neq 0 (
        echo ❌ 前端依赖安装失败，尝试清理重装...
        npm cache clean --force
        rmdir /s /q node_modules 2>nul
        del package-lock.json 2>nul
        npm install
        
        if %errorlevel% neq 0 (
            echo ❌ 前端依赖安装仍然失败
        ) else (
            echo ✅ 前端依赖安装成功
            set /a ERROR_COUNT-=1
        )
    ) else (
        echo ✅ 前端依赖安装成功
        set /a ERROR_COUNT-=1
    )
) else (
    echo ✅ node_modules目录存在
    
    REM 运行前端依赖检查（如果脚本存在）
    if exist "check_frontend_deps.js" (
        echo 📊 运行前端依赖检查...
        node check_frontend_deps.js
        if %errorlevel% neq 0 (
            echo ❌ 前端依赖检查发现问题
            set /a ERROR_COUNT+=1
            
            echo 🔧 尝试重新安装前端依赖...
            npm install
            if %errorlevel% equ 0 (
                echo ✅ 前端依赖重新安装成功
                set /a ERROR_COUNT-=1
            )
        ) else (
            echo ✅ 前端依赖检查通过
        )
    )
)

:summary
echo.
echo ========================================
echo 📊 综合检查结果
echo ========================================

if %ERROR_COUNT% equ 0 (
    echo ✅ 所有依赖检查通过！
    echo.
    echo 🚀 现在可以启动服务：
    echo    后端: start_backend_simple.bat
    echo    前端: cd social-trend-analyzer ^&^& npm run dev
    echo.
    echo 🌐 服务地址：
    echo    后端API: http://localhost:8001
    echo    前端界面: http://localhost:5173
) else (
    echo ❌ 发现 %ERROR_COUNT% 个问题需要手动解决
    echo.
    echo 🔧 建议操作：
    echo    1. 检查Python和Node.js是否正确安装
    echo    2. 确保网络连接正常
    echo    3. 检查防火墙设置
    echo    4. 手动运行 install_all_dependencies.bat
)

echo.
echo 📋 详细日志已保存到控制台输出
echo 如需帮助，请检查上述输出信息
echo.
pause
exit /b %ERROR_COUNT%