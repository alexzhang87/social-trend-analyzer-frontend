@echo off
echo ========================================
echo 🚀 启动社交媒体趋势分析系统
echo ========================================

echo.
echo 📁 切换到backend目录...
cd /d "%~dp0backend"

echo.
echo 🔧 检查虚拟环境...
if not exist ".venv" (
    echo 🛠️ 创建虚拟环境...
    python -m venv .venv
)

echo.
echo 🔧 激活虚拟环境...
call .venv\Scripts\activate.bat

echo.
echo 📦 检查并安装依赖...
pip install -r requirements.txt > nul 2>&1

echo.
echo 📊 添加Vision Pro测试数据...
python add_vision_pro_data.py

echo.
echo 🔴 启动Redis服务 (端口6380)...
start "Redis Server" cmd /k "redis-server --port 6380"

echo.
echo ⏳ 等待Redis启动...
timeout /t 3 /nobreak > nul

echo.
echo 🌐 启动后端服务 (端口8001)...
start "Backend Server" cmd /k "python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload --log-level debug"

echo.
echo ⏳ 等待后端服务启动...
timeout /t 10 /nobreak > nul

echo.
echo 🧪 运行测试...
python quick_test_sync.py

echo.
echo ========================================
echo ✅ 系统启动完成！
echo 🌐 后端API: http://localhost:8001
echo 📚 API文档: http://localhost:8001/docs
echo ========================================
echo.
echo 如果仍然无法访问，请检查:
echo 1. 防火墙设置
echo 2. 端口是否被其他程序占用
echo 3. Windows Defender或其他安全软件是否阻止了连接
echo.
pause