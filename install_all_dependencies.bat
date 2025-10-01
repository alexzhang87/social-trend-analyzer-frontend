@echo off
echo ========================================
echo 社交媒体趋势分析工具 - 依赖安装脚本
echo ========================================
echo.

echo 🔍 检查Python环境...
python --version
if %errorlevel% neq 0 (
    echo ❌ Python未安装或未添加到PATH
    pause
    exit /b 1
)

echo.
echo 📦 开始安装后端依赖...
echo.

cd /d "%~dp0\backend"

echo 🔄 激活虚拟环境...
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    echo ✅ 虚拟环境已激活
) else (
    echo ⚠️  虚拟环境不存在，使用全局Python环境
)

echo.
echo 🔧 升级pip...
python -m pip install --upgrade pip

echo.
echo 📋 安装requirements.txt中的所有依赖...
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo.
    echo ❌ 依赖安装失败，尝试逐个安装...
    echo.
    
    echo 📦 安装核心依赖...
    pip install fastapi uvicorn[standard] sqlalchemy python-dotenv
    pip install zhipuai pydantic python-multipart pydantic-settings
    
    echo 📦 安装认证依赖...
    pip install "python-jose[cryptography]>=3.3.0" "passlib[bcrypt]>=1.7.4"
    pip install email-validator>=2.0.0
    
    echo 📦 安装任务队列依赖...
    pip install "celery[redis]>=5.3.0" redis requests
    
    echo 📦 安装文本分析依赖...
    pip install vaderSentiment==3.3.2 jieba==0.42.1 emoji==2.8.0
    pip install textblob>=0.17.1 nltk>=3.8.0
    
    echo 📦 安装数据处理依赖...
    pip install pandas>=1.5.0 numpy>=1.21.0 scikit-learn>=1.0.0
    
    echo 📦 安装网络爬虫依赖...
    pip install snscrape==0.7.0.20230622 "beautifulsoup4>=4.12.0"
    pip install "lxml>=4.9.0" "requests-html>=0.10.0"
    
    echo 📦 安装其他依赖...
    pip install "pytrends>=4.9.0" "retrying>=1.3.4"
    pip install "reportlab>=3.6.0,<4.0.0"
    pip install aiohttp>=3.8.0 feedparser>=6.0.0 stripe>=5.0.0
)

echo.
echo 🔍 验证关键依赖安装...
python -c "import fastapi; print('✅ FastAPI:', fastapi.__version__)"
python -c "import uvicorn; print('✅ Uvicorn:', uvicorn.__version__)"
python -c "import sqlalchemy; print('✅ SQLAlchemy:', sqlalchemy.__version__)"
python -c "import pydantic; print('✅ Pydantic:', pydantic.__version__)"
python -c "import jose; print('✅ Python-JOSE: OK')"
python -c "import passlib; print('✅ Passlib: OK')"
python -c "import email_validator; print('✅ Email-Validator: OK')"
python -c "import redis; print('✅ Redis:', redis.__version__)"
python -c "import celery; print('✅ Celery:', celery.__version__)"

echo.
echo 📦 检查前端依赖...
cd /d "%~dp0\social-trend-analyzer"

echo 🔍 检查Node.js环境...
node --version
if %errorlevel% neq 0 (
    echo ❌ Node.js未安装
    echo 请访问 https://nodejs.org 下载安装Node.js
) else (
    echo ✅ Node.js环境正常
    
    echo.
    echo 📋 安装前端依赖...
    npm install
    
    if %errorlevel% neq 0 (
        echo ❌ 前端依赖安装失败，尝试清理缓存重新安装...
        npm cache clean --force
        rmdir /s /q node_modules 2>nul
        del package-lock.json 2>nul
        npm install
    )
)

echo.
echo ========================================
echo 🎉 依赖安装完成！
echo ========================================
echo.
echo 📋 安装总结：
echo   ✅ 后端Python依赖
echo   ✅ 前端Node.js依赖
echo.
echo 🚀 现在可以启动服务：
echo   后端: start_backend_simple.bat
echo   前端: cd social-trend-analyzer && npm run dev
echo.
echo 🔧 如果遇到问题，请检查：
echo   1. Python和Node.js版本兼容性
echo   2. 网络连接是否正常
echo   3. 防火墙设置
echo.
pause